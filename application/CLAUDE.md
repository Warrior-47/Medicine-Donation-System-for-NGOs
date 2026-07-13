# Agent context — Medicine Donation System (microservices)

Read this first. It orients you in the codebase faster than exploring;
`README.md` (same directory) is the human-facing companion with the full
env-var table and deployment notes.

## What this is

"Reaching Doors" — a Django 4.2 server-rendered site (Bootstrap
templates, session auth, MySQL) where donors give leftover medicine to
NGOs. It was a monolith (see git history before the split); it is now
**four self-contained Django projects** under this directory, designed to
run behind one gateway host that routes by path prefix. Public URLs are
identical to the monolith's.

| Service | Public path prefixes | Data it owns | Calls |
|---|---|---|---|
| `user-service` | `/accounts/`, `/admin/` | `CustomUser` + auth tables | — |
| `medicine-service` | `/` (dashboard, medicine CRUD) | NGO/donor medicine lists, uploaded images | — |
| `search-service` | `/search/` | nothing — stateless, no real DB | user + medicine APIs |
| `donation-service` | `/donations/` | donation requests + line items | user + medicine APIs |

Dev ports: 8001/8002/8003/8004, gateway 8080 (`dev-gateway.py`).

## Cross-service contracts — keep these in sync or everything breaks

1. **Shared `SECRET_KEY`** (same default in every `config/settings.py`,
   env-overridable). Sessions are signed cookies
   (`SESSION_ENGINE=signed_cookies`); a per-service key change logs
   everyone out of that service and breaks auth.
2. **Session claims**: at login, user-service copies
   `{id, username, fullname, email, phone, is_ngo}` into
   `request.session['user_info']` (producer:
   `user-service/account/signals.py` + `common/session_claims.py`).
   The other three services rebuild `request.user` from it in
   `common/middleware.py` (`SessionUserMiddleware`). Key name and field
   set are a contract. Claims refresh only at login.
3. **Internal API** (JSON over HTTP, header `X-Internal-Token` must equal
   `INTERNAL_API_TOKEN`, same value on all services):
   - user-service: `/api/users/<id>/`, `/api/users/?ids=1,2`, `/api/ngos/?name=x`
     (views in `account/api.py`)
   - medicine-service: `/api/medicines/donor/<uid>/`, `/api/medicines/ngo/<uid>/`,
     `/api/medicines/ngo/` (views in `DonationSystem/api.py`)
   - consumers use `common/service_client.py` (`internal_get`; returns
     None on 404, raises `ServiceUnavailable` otherwise); base URLs from
     `USER_SERVICE_URL` / `MEDICINE_SERVICE_URL` env.
   - The gateway/ingress must **never** route `/api/*` publicly.
4. **Path contract**: cross-service links/redirects in templates and
   views are hardcoded absolute paths (`/`, `/accounts/login/`,
   `/search/...`, `/donations/...`) because `{% url %}` can't reverse
   another service's routes. Same-service links still use `{% url %}`.
   If you move a route, grep all services for its absolute path.
5. **No cross-service FKs**: ownership is plain `BigIntegerField` ids
   (`NGO_id`, `Donor_id`); donation-service denormalizes `Donor_name`,
   `Donor_phone`, `NGO_name` at request creation.

## Layout conventions

- Each service: `manage.py`, `config/` (settings/urls/wsgi/asgi),
  `common/` (shared plumbing), its domain app, `health/` app,
  `static/` (full copy of the shared theme assets — duplication is
  deliberate; services must stay self-contained), `requirements.txt`,
  `Dockerfile` (python3.12-alpine), `entrypoint.sh`, `.venv/` (gitignored).
- `common/` files are **duplicated by design** across services
  (middleware, context processor, decorators, service client, internal
  API guard). If you edit one, mirror the change into the sibling
  services that have the same file.
- `common/decorators.py: login_required` replaces Django's decorator on
  the three services without contrib.auth — Django's version crashes
  there (its anonymous-redirect path imports contrib.auth models).
  Similarly, never import `django.contrib.auth`/`admin` modules in those
  services, even "harmlessly" (e.g. in urls.py) — the app registry will
  raise at import time.
- donation/search services carry copies of the base templates they render
  under `common/templates/` (`DonationSystem/base.html`,
  `account/base.html`) plus needed static assets under `common/static/`.
- Code style intentionally matches the original monolith (naming,
  spacing, quirks). Don't reformat or "fix" behavior beyond your task;
  known preserved quirks: no ownership check on medicine update/delete,
  reject leaves the `donationRequest` row and deletes only its
  `donatedMedicines` (that's how donors see "Rejected").

## Databases

- Default: MySQL via env (`DB_*`), all services pointing at the single
  `medicine_donation` DB from the existing chart — tables are disjoint
  per service. Optional isolation: per-service `DB_NAME`.
- `DB_ENGINE=sqlite3` switches to a local sqlite file (used for all local
  dev/tests). search-service has no real DB (placeholder sqlite alias,
  never migrated; its entrypoint skips `migrate`).
- Schema differs from the monolith (id columns instead of FKs,
  denormalized fields, regenerated `0001_initial` per service) —
  **deploys need a fresh database**.

## Run / verify

```bash
./quick-check.sh              # boot everything + gateway on :8080 (venv bootstrap included)
./quick-check.sh stop|clean   # stop; clean also wipes DBs/uploads/logs

./e2e-test.sh                 # 18-step journey against the 4 dev ports
G=http://127.0.0.1:8080; USER_URL=$G MEDICINE_URL=$G SEARCH_URL=$G DONATION_URL=$G \
  ./e2e-test.sh               # same journey through the gateway (ingress simulation)
```

After changing anything touching the contracts above, run the e2e script
in **both** modes; it covers registration, cross-service login, medicine
CRUD + image upload, searches, the donation lifecycle, `/api` exposure
and logout.

## Boundaries and environment facts

- `infra/` (helmfile + charts) is **owned by the human** — do not modify
  it unless explicitly asked. The `django-app` chart is already generic
  over an `apps:` values map; deploying these services is a values-file
  exercise (see README.md).
- Images: one per service dir (`docker build` context = the service dir).
  Docker is not available inside this WSL distro; build/push is done by
  the human.
- Local venvs run Python 3.13, images use 3.12-alpine; Django is pinned
  `>=4.2.15,<4.3`. Never install packages globally — each service has its
  own `.venv`.
- `DEBUG` defaults to `True` and deployment uses `runserver` (parity with
  the original setup); static files and uploaded images are served by
  Django's static handling, with uploads living under
  `medicine-service/static/img/medicine_images/` (PVC-mounted in k8s).
- Historical fix to know about: the monolith referenced most assets as
  `{% static '/vendor/...' %}` — the leading slash bypassed `/static/`
  and 404'd. The split repo strips those slashes; don't reintroduce them.
