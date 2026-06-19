FROM node:20-slim AS deps
WORKDIR /workspace
COPY package.json package-lock.json* ./
COPY apps/web/package.json apps/web/package.json
COPY packages/api-client/package.json packages/api-client/package.json
RUN npm install --workspaces

FROM deps AS build
COPY apps/web apps/web
COPY packages/api-client packages/api-client
RUN npm run build --workspace @openvend/web

FROM nginx:1.27-alpine AS runtime
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/apps/web/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
