# LMS API

## About the LMS API

## LMS API host port

The [port number](./computer-networks.md#port-number) (without `<` and `>`) which the [LMS API](#about-the-lms-api) is available at on the [host](./computer-networks.md#host).

The port number is the value of [`LMS_API_HOST_PORT`](./dotenv-docker-secret.md#lms_api_host_port) in [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret).

### `<lms-api-host-port>` placeholder

The [LMS API host port](#lms-api-host-port).

## LMS API URL

> [!NOTE]
>
> See [URL](./computer-networks.md#url).

LOCAL: `http://localhost:<lms-api-host-port>`

REMOTE: `http://<your-vm-ip-address>:<lms-api-host-port>`

Replace the placeholders:

- [`<your-vm-ip-address>`](./vm.md#your-vm-ip-address-placeholder)
- [`<lms-api-host-port>`](./lms-api.md#lms-api-host-port-placeholder)

### `<lms-api-url>` placeholder

[LMS API URL](#lms-api-url) (without `<` and `>`).

## `Caddy`

### `Caddyfile` in this project

In this project, the [`Caddyfile`](./caddy.md#caddyfile) is at [`caddy/Caddyfile`](../caddy/Caddyfile).

This configuration:

- Reads the value of [`CADDY_CONTAINER_PORT`](./dotenv-docker-secret.md#caddy_container_port) in [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret).
- Makes `Caddy` [listen on the port](./computer-networks.md#listen-on-a-port) listen on this port inside a [`Docker` container](./docker.md#container).
- [Serves frontend files](#caddy-serves-frontend-files)
- [Forwards requests to backend](#caddy-forwards-requests-to-backend)

### `Caddy` serves frontend files

`Caddy` serves static front-end files from `/srv` for all other paths.

The `try_files` directive falls back to `index.html` for client-side routing.

### `Caddy` forwards requests to backend

`Caddy` routes [API endpoints](./web-api.md#endpoint) (`/items*`, `/learners*`, `/interactions*`, `/docs*`, `/openapi.json`) to the [`app` service](./docker-compose-yml.md#app-service).
