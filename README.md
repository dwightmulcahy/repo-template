# PROJECT_NAME

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
[![Release](https://github.com/OWNER/REPO/actions/workflows/release.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/release.yml)
[![GitHub release](https://img.shields.io/github/v/release/OWNER/REPO?sort=semver)](https://github.com/OWNER/REPO/releases/latest)
[![Docker Image Version](https://img.shields.io/docker/v/DOCKERHUB_USER/DOCKERHUB_REPO?sort=semver&label=docker)](https://hub.docker.com/r/DOCKERHUB_USER/DOCKERHUB_REPO)
[![Docker Pulls](https://img.shields.io/docker/pulls/DOCKERHUB_USER/DOCKERHUB_REPO)](https://hub.docker.com/r/DOCKERHUB_USER/DOCKERHUB_REPO)
[![Image Size](https://img.shields.io/docker/image-size/DOCKERHUB_USER/DOCKERHUB_REPO/latest)](https://hub.docker.com/r/DOCKERHUB_USER/DOCKERHUB_REPO)
[![Dependabot](https://img.shields.io/badge/dependabot-enabled-025e8c?logo=dependabot)](.github/dependabot.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Short description.

> [!IMPORTANT]
> ## Using this template — checklist (delete this section when done)
>
> **1. Create the repo**
> ```bash
> gh repo create myapp --public --template dwightmulcahy/repo-template --clone
> cd myapp
> ```
>
> **2. Replace placeholders** (search the repo for each token)
>
> | Placeholder | Replace with | Files |
> |---|---|---|
> | `PROJECT_NAME` / `Project Name` | Display name | `README.md`, `src/index.html` |
> | `project-name` | npm package name | `package.json` |
> | `OWNER/REPO` | `githubuser/myapp` | `README.md` (badges, links) |
> | `DOCKERHUB_USER/DOCKERHUB_REPO` | `dockeruser/myapp` | `README.md` (badges) |
> | `youruser/yourapp`, `yourapp` | Container image / app name | `.env.example` |
> | `/share/Container/app/data` | QNAP data path | `compose.qnap.yaml`, `.env.example` |
> | `OWNER/REPO` in the security URL | GitHub repository | `SECURITY.md` |
> | `Copyright (c) 2026 Dwight Mulcahy` | Year / owner if different | `LICENSE` |
> | `Short description.` | One-line description | `README.md` |
>
> ```bash
> grep -rnE 'PROJECT_NAME|Project Name|project-name|OWNER/REPO|DOCKERHUB_(USER|REPO)|youruser|yourapp' \
>   --exclude-dir={node_modules,.git} .
> ```
>
> **3. Image registry** (optional; not copied by templates — set per repo)
>
> With nothing set, releases publish to GitHub Container Registry as `ghcr.io/<owner>/<repo>` using the built-in `GITHUB_TOKEN`. To publish to Docker Hub instead, set both of these:
>
> | Name | Type | Value |
> |---|---|---|
> | `DOCKERHUB_USERNAME` | Variable | Docker Hub username |
> | `DOCKERHUB_REPO` | Variable | `dockeruser/myapp` (optional; defaults to `<username>/<repo-name>`) |
> | `DOCKERHUB_TOKEN` | Secret | Docker Hub access token (Read & Write) — hub.docker.com → Account settings → Personal access tokens |
>
> ```bash
> gh variable set DOCKERHUB_USERNAME --body dockeruser
> gh variable set DOCKERHUB_REPO     --body dockeruser/myapp
> gh secret   set DOCKERHUB_TOKEN    # prompts for value
> ```
>
> On GHCR, the first published image is a package you can find under your profile → Packages. Check its visibility there and make it public if hosts should pull it without logging in.
>
> **4. Repo settings** (not copied by templates)
> - [ ] Settings → Actions → General → Workflow permissions: *Read repository contents* (workflows request `contents: write` only where needed)
> - [ ] Settings → Rules → New branch ruleset on `main`: require PR, require status checks (`JS syntax check`, `Validate Compose files`, `Build web + offline`, `pytest`, `Docker image + Chromium smoke`), block force pushes
> - [ ] Settings → Rules → New tag ruleset on `v*`: restrict creation/deletion to admins
> - [ ] Settings → Code security → enable private vulnerability reporting, Dependabot alerts + security updates, secret scanning, push protection
> - [ ] About (gear icon) → description, topics
>
> **5. Replace the stub app**
> - [ ] `src/`, `server.mjs`, `scripts/build.mjs` — your app; keep `npm run build:web`, `npm run build:offline`, and a `GET /health` → 200
> - [ ] Keep the version label (`src/about.mjs`, the `build-info` script tag in `index.html`, `GET /api/about`) or delete all three
> - [ ] `Dockerfile`, `.dockerignore` — adjust `COPY` lines to your sources
> - [ ] `tests/` (pytest) and `tests/smoke/` (Playwright) — real tests
> - [ ] `package.json` `engines`, `NODE_VERSION` / `PYTHON_VERSION` in `.github/workflows/*.yml`
> - [ ] Remove `.github/dependabot.yml` entries for ecosystems you don't use
>
> **6. Verify**
> - [ ] Push to `main` → CI green
> - [ ] `git tag v0.1.0 && git push origin v0.1.0` → image on GHCR (or Docker Hub if configured), GitHub Release with ZIP + `.sha256`

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8080/health
```

QNAP: `docker compose -f compose.qnap.yaml pull && docker compose -f compose.qnap.yaml up -d`

Both Compose files run with a read-only root filesystem, dropped capabilities,
`no-new-privileges`, bounded memory/PIDs/shared memory, an init process, a
graceful shutdown window, and rotated JSON logs. Ensure `QNAP_DATA_DIR` is
writable by the container user before deployment.

Offline edition: download `*-offline.zip` from [Releases](https://github.com/OWNER/REPO/releases) and verify with `sha256sum -c *.sha256`.

## Version label and About dialog

The page header shows the build version (`v1.4.2` for releases, `dev <commit>` for local builds). Clicking it opens an About dialog with version, commit, edition, build time, server start time, links to the release notes and issue tracker, and **Copy details** for bug reports.

`scripts/build.mjs` writes this to `build.json` and embeds it in `index.html` (so it also works without a server):

| Field | Release build | Local `docker compose up --build` | `npm run build:*` |
|---|---|---|---|
| version | tag without `v` (`APP_VERSION`) | `dev` | `APP_VERSION` or `dev` |
| commit | `GIT_SHA` | read from `.git` (compose passes it as the `git` build context) | `GIT_SHA`, or `GIT_DIR=.git` |
| repository | `REPOSITORY` (`owner/repo`) | `.git` remote `origin` (GitHub only) | `GITHUB_REPOSITORY`, or `GIT_DIR=.git` |

The server adds its start time at `GET /api/about`. Nothing in either reveals dependency versions.

## Development

```bash
npm ci
npm run build:web        # -> dist/web
npm run build:offline    # -> dist/offline
pip install -r requirements-dev.txt && pytest
npx playwright install chromium && BASE_URL=http://localhost:8080 npm run test:smoke
```

CI pins every external GitHub Action to an immutable commit SHA, pins the
Docker base image by version and multi-architecture digest, and rejects fixable
high or critical image vulnerabilities with Trivy. Dependabot keeps those pins
reviewable and current.

## Releasing

1. Merge to `main`.
2. `git tag v1.2.3 && git push origin v1.2.3`
3. The Release workflow verifies the tag is on `main`, reruns CI, and publishes
   the multi-architecture image, offline ZIP, SHA-256 checksum, and grouped
   Conventional Commit release notes.

For the newest stable `v1.2.3` release, Docker receives `1.2.3`, `1.2`, `1`,
and `latest`. Older releases publish only their exact version, so rerunning or
backfilling an old tag cannot move a rolling tag backward. Tags containing `-`
(for example `v1.3.0-rc.1`) are prereleases and publish only the exact tag.

Registry: Docker Hub when the `DOCKERHUB_USERNAME` variable and `DOCKERHUB_TOKEN` secret are both set (optional `DOCKERHUB_REPO`, e.g. `user/app`); otherwise `ghcr.io/<owner>/<repo>`, with no setup. The release run shows a notice when it falls back to GHCR.

## License

[MIT](LICENSE)
