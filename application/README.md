# Medicine Donation System — Microservices

The former Django monolith is split into four independently deployable
services. Public URLs are unchanged: a gateway (Ingress on Kubernetes)
routes path prefixes to services, so the site behaves exactly as before
from the browser's point of view.

```
                        ┌──────────────────────┐
        browser ──────► │  gateway / ingress   │  (one hostname)
                        └──────────┬───────────┘
       /accounts/* /admin/*        │            /  /edit-list/ /add-medicine/ ...
             ┌─────────────────────┼──────────────────────┐
             ▼                     ▼                      ▼
      ┌─────────────┐      ┌──────────────────┐    ┌───────────────┐
      │ user-service │      │ medicine-service │    │ search-service │  /search/*
      │  (accounts,  │      │ (medicine lists, │    │  (stateless)   │
      │   auth, admin)│      │  image uploads)  │◄───┤                │
      └──────┬───────┘      └────────▲─────────┘    └──────┬────────┘
             │       internal APIs   │                     │
             └───────────────◄───────┼─────────◄───────────┘
                                     │
                          ┌──────────┴────────┐
                          │ donation-service  │  /donations/*
                          │ (request lifecycle)│
                          └───────────────────┘
```

| Service | Public path prefixes | Owns (tables) | Calls |
|---|---|---|---|
| `user-service` | `/accounts/`, `/admin/` | users (`account_customuser`, auth tables) | — |
| `medicine-service` | `/`, `/edit-list/`, `/add-medicine/`, `/update-medicine/`, `/delete-medicine/` | `DonationSystem_*` + uploaded images (PVC) | — |
| `search-service` | `/search/` | nothing (stateless) | user, medicine |
| `donation-service` | `/donations/` | `DonationRequestSystem_*` | user, medicine |

Every service also serves `GET /health/` for probes, and its own
`/static/*` assets.

## How the pieces fit together

### Authentication (no shared users table)

Sessions use Django's **signed-cookie backend** and all services share the
same `SECRET_KEY`, so every service can read the session cookie without a
session store. At login, user-service copies the user's claims
(`id`, `username`, `fullname`, `email`, `phone`, `is_ngo`) into the
session under the `user_info` key (`account/signals.py`). The other
services rebuild `request.user` from those claims in
`common/middleware.SessionUserMiddleware` — no database or network call.
Logout flushes the session, which logs the user out of every service at
once.

Consequences to be aware of:

- `SECRET_KEY` **must be identical** on all four services, or users will
  be logged out the moment they cross a path prefix.
- Claims refresh only at login. If an admin edits a user's name/role, the
  change shows up after the user's next login.

### Internal service-to-service API

Cross-service reads go over HTTP with a shared-token header
(`X-Internal-Token`; env `INTERNAL_API_TOKEN`, same value everywhere).
These paths must **not** be routed by the public gateway:

| Endpoint | Serves |
|---|---|
| `GET user-service /api/users/<id>/` | one user's details |
| `GET user-service /api/users/?ids=1,2` | bulk user details |
| `GET user-service /api/ngos/?name=x` | NGO search by name |
| `GET medicine-service /api/medicines/donor/<user_id>/` | a donor's medicines |
| `GET medicine-service /api/medicines/ngo/<user_id>/` | an NGO's needed medicines |
| `GET medicine-service /api/medicines/ngo/` | all NGO entries (priority search) |

### Data ownership

There are **no cross-service foreign keys**. Medicine and donation rows
store plain user ids (`NGO_id`, `Donor_id`); donation-service additionally
denormalizes `Donor_name`, `Donor_phone` and `NGO_name` at
request-creation time because its pages display them.

By default every service connects to the same MySQL database
(`medicine_donation`) — matching the existing MySQL chart — but each
service only touches its own tables, so you can later point each service
at its own database (`DB_NAME`) without code changes.

> **Fresh database required.** The schema differs from the monolith's
> (user FKs became plain id columns; donation rows gained denormalized
> name/phone columns) and each service now ships its own regenerated
> `0001_initial` migration. Deploy against a fresh/empty database.

## Configuration (env vars)

| Variable | Used by | Default |
|---|---|---|
| `SECRET_KEY` | all | insecure dev key (set one value for all services) |
| `DEBUG` | all | `True` (`runserver` also serves static files only when `True`) |
| `DB_ENGINE` | user, medicine, donation | `mysql` (`sqlite3` for local dev) |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | user, medicine, donation | `medicine_donation` / `admin` / — / `localhost` / `3306` |
| `USER_SERVICE_URL` | search, donation | `http://user-service` |
| `MEDICINE_SERVICE_URL` | search, donation | `http://medicine-service` |
| `INTERNAL_API_TOKEN` | all | insecure dev token (set one value for all services) |
| `EMAIL_USER` / `EMAIL_PASS` | user | — (password-reset emails) |

search-service needs no database configuration at all.

## Local development

Each service has its own virtual environment — nothing is installed
globally:

```bash
cd application/<service>            # user-service, medicine-service, ...
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Run all four (each in its own terminal, from the service directory):

```bash
# user-service
DB_ENGINE=sqlite3 .venv/bin/python manage.py migrate
DB_ENGINE=sqlite3 .venv/bin/python manage.py runserver 127.0.0.1:8001

# medicine-service
DB_ENGINE=sqlite3 .venv/bin/python manage.py migrate
DB_ENGINE=sqlite3 .venv/bin/python manage.py runserver 127.0.0.1:8002

# search-service (no database)
USER_SERVICE_URL=http://127.0.0.1:8001 MEDICINE_SERVICE_URL=http://127.0.0.1:8002 \
    .venv/bin/python manage.py runserver 127.0.0.1:8003

# donation-service
DB_ENGINE=sqlite3 .venv/bin/python manage.py migrate
DB_ENGINE=sqlite3 USER_SERVICE_URL=http://127.0.0.1:8001 MEDICINE_SERVICE_URL=http://127.0.0.1:8002 \
    .venv/bin/python manage.py runserver 127.0.0.1:8004
```

Cookies are host-scoped (ports don't matter), so login on `:8001` carries
over to the other ports. Links that cross services point at absolute
paths (`/search/...`), which only resolve behind a single gateway host —
when clicking around locally, adjust the port by hand or just run the
automated journey:

```bash
./application/e2e-test.sh     # drives registration → donation lifecycle end to end
```

### Browser access: quick check & dev gateway

For a one-command browser check (bootstraps venvs, migrates, starts the
four services plus the gateway on **http://localhost:8080**):

```bash
./application/quick-check.sh          # start everything
./application/quick-check.sh stop     # stop, keep local data
./application/quick-check.sh clean    # stop + wipe DBs, uploads, logs
```

Under the hood it uses the bundled gateway — a dependency-free reverse
proxy that plays the ingress role locally, serving the whole app on one
host with the same path-prefix routing the cluster will use (and, like
the ingress, it does not expose `/api/*`):

```bash
python3 application/dev-gateway.py
```

The end-to-end script can exercise the gateway too, proving the routing
contract itself:

```bash
G=http://127.0.0.1:8080
USER_URL=$G MEDICINE_URL=$G SEARCH_URL=$G DONATION_URL=$G ./application/e2e-test.sh
```

## Container images

Each service directory is a self-contained build context:

```bash
docker build -t <docker_user>/user-service:latest     application/user-service
docker build -t <docker_user>/medicine-service:latest application/medicine-service
docker build -t <docker_user>/search-service:latest   application/search-service
docker build -t <docker_user>/donation-service:latest application/donation-service
```

Deployment notes for the (unchanged) infra:

- The existing `django-app` chart is already generic over an `apps:` map —
  one entry per service gives each its own Deployment, ConfigMap
  (`<name>-config`), Secret (`<name>-secrets`), Service and probes.
  Point each service's config at the env vars above.
- Only medicine-service needs the image PVC
  (mount `/app/static/img/medicine_images`, same path as before).
- search-service is the only service whose entrypoint skips
  `manage.py migrate` (it owns no data).
- The gateway/Ingress must route the path prefixes from the table above to
  the matching Service, and must **not** expose `/api/*`.
- `/health/` redirects `/health` → `/health/` (HTTP 301); Kubernetes
  httpGet probes treat 3xx as success, same as with the monolith.
