FROM node:18-alpine AS build
WORKDIR /web
COPY apps/web/package*.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web ./
RUN npm run build

FROM nginx:1.27-alpine
COPY infra/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /web/dist /usr/share/nginx/html
EXPOSE 80
