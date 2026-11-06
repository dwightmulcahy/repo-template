# syntax=docker/dockerfile:1
# Empty unless compose.yaml supplies the checkout's .git as the "git" build context
FROM scratch AS git

FROM node:26.13.0-alpine3.24@sha256:c6ad9e9c1d80f6eb607c26b4b0a132ff7a2344fad1c78ea3baa2a7d4c8de6d94 AS build
# Set by the release workflow (tag without "v", commit, owner/repo); empty = "dev" build
ARG APP_VERSION=
ARG GIT_SHA=
ARG REPOSITORY=
WORKDIR /app
COPY scripts ./scripts
COPY src ./src
RUN --mount=type=bind,from=git,target=/git \
    APP_VERSION="${APP_VERSION}" GIT_SHA="${GIT_SHA}" REPOSITORY="${REPOSITORY}" GIT_DIR=/git \
    node scripts/build.mjs web

FROM node:26.13.0-alpine3.24@sha256:c6ad9e9c1d80f6eb607c26b4b0a132ff7a2344fad1c78ea3baa2a7d4c8de6d94
ENV NODE_ENV=production PORT=8080
WORKDIR /app
# Files owned by root, process runs as non-root: app cannot modify itself
COPY --from=build /app/dist/web ./public
COPY server.mjs ./
# Static runtime needs node, not npm/corepack or their vulnerable bundled packages.
# Keep package managers in the build stage only.
RUN rm -rf /usr/local/lib/node_modules /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack
USER node
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/health || exit 1
CMD ["node", "server.mjs"]
