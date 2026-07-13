# Medicine Donation System for NGOs

A website to easily donate medicine to underprivileged people through
NGOs, built with Django as four microservices:

| Service | Responsibility |
|---|---|
| `application/user-service` | accounts, login, admin |
| `application/medicine-service` | dashboard, medicine lists, image uploads |
| `application/search-service` | NGO search & priority matching (stateless) |
| `application/donation-service` | donation request lifecycle |

See [`application/README.md`](application/README.md) for the
architecture, cross-service contracts, configuration, local development
and image builds. Deployment lives under [`infra/`](infra/) (helmfile).
