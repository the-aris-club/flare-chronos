# Continuous Deployment

CD runs on a tag push matching `v*.*.*` (`.github/workflows/cd.yml`). It builds two images (`flare-chronos-api`, `flare-chronos-workbench`), pushes them to GHCR, then deploys to the VPS over SSH.

## Required GitHub secrets (environment: `production`)

- `VPS_HOST` — VPS hostname or IP.
- `VPS_USER` — SSH user with docker access.
- `VPS_SSH_KEY` — private key for that user (paste the whole key, including newlines).
- `GITHUB_TOKEN` is provided automatically and is used to push to GHCR.

## Required on the VPS

- Docker + Docker Compose installed.
- Deploy directory: `/opt/flare-chronos/` (owned by the deploy user), containing `docker-compose.yml` and `.env`.
- `/opt/flare-chronos/.env` with the runtime configuration:
  - `AI_SERVICE_JWT_KEY` (required; auth is enabled in production)
  - `AI_SERVICE_CORS_ORIGINS` (Workbench origin, e.g. `http://<host>:3000`)
  - `NEXT_PUBLIC_API_URL` is a build-time value (see GitHub variable below)
  - `TAG` (image tag to run, e.g. `v1.0.0` or `latest`)
- The deploy user must be in the `docker` group.
- The VPS must be able to pull from GHCR: either make the packages public, or run
  `docker login ghcr.io` on the VPS with a token that has `read:packages`.

## GitHub repository variable

- `NEXT_PUBLIC_AI_SERVICE_URL` — public URL the Workbench calls (e.g.
  `http://<host>:8765`). Used as a build arg when building the Workbench image.

## Current production host

- Host alias: `sang` (`node.sang0023.io.vn`), user `sang`.
- Public IP: `163.227.231.153`. API on `:5901`, Workbench on `:5900`.
- Other services on this host (Pterodactyl, Portainer, beszel) are untouched; the two
  new containers use only ports `8765` and `3000`, which were verified free.

## Release procedure

1. Merge to `main`.
2. Create a tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. The CD workflow builds, pushes, and deploys. Smoke tests hit `/health` on the API and `/` on the Workbench.

## Reverse proxy (nginx)

`/etc/nginx/sites-available/flare-chronos.resonance.io.vn` proxies `/` to the Workbench
(`127.0.0.1:5900`) and `/api/` to the API (`127.0.0.1:5901`). DNS for the domain must
point at the VPS IP before running Certbot:

```
sudo certbot --nginx -d flare-chronos.resonance.io.vn
```

The Workbench calls the API through the relative `/api` path, so it works on any host
behind this proxy.

## Rollback

Edit `/opt/flare-chronos/docker-compose.yml` (or set `TAG=vX.Y.Z-1` in `.env`) and run `docker compose up -d`.

## Notes

- Vercel Remote Cache (Turborepo) is **not** used yet. Adopting Turborepo is tracked as a separate decision; when adopted, authenticate via OIDC (recommended) with team `team_n32FmJjpnddxMjQryhJz36wy`.
- The API persists runs in a SQLite file under the `api-data` volume; do not delete that volume without a backup.