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

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8080/health
```

QNAP: `docker compose -f compose.qnap.yaml up -d`

Offline edition: download `*-offline.zip` from [Releases](https://github.com/OWNER/REPO/releases) and verify with `sha256sum -c *.sha256`.

## Development

```bash
npm ci
npm run build:web        # -> dist/web
npm run build:offline    # -> dist/offline
pip install -r requirements-dev.txt && pytest
npx playwright install chromium && BASE_URL=http://localhost:8080 npm run test:smoke
```

## Releasing

1. Merge to `main`.
2. `git tag v1.2.3 && git push origin v1.2.3`
3. The Release workflow verifies the tag is on `main`, reruns CI, pushes `1.2.3` + `latest` (amd64/arm64) to Docker Hub, and publishes the offline ZIP + SHA-256 to a GitHub Release. Tags with `-` (e.g. `v1.3.0-rc.1`) are prereleases and skip `latest`.

Required settings: repo variables `DOCKERHUB_USERNAME`, `DOCKERHUB_REPO` (e.g. `user/app`); secret `DOCKERHUB_TOKEN`.

## License

[MIT](LICENSE)
