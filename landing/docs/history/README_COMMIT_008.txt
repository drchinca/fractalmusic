FMW WEB — COMMIT 008 — QA INTEGRAL Y DESPLIEGUE

TERMINADO
- Pruebas E2E automatizadas con node:test, sin dependencias externas.
- Cobertura del flujo lead → historial → checkout → webhook firmado → pago → confirmación → administración → CSV.
- Pruebas de cabeceras de seguridad, autorización administrativa, firma inválida y rate limiting.
- Preflight de producción que bloquea despliegues sin secretos, HTTPS o producto digital válido.
- Dockerfile con usuario no privilegiado y healthcheck.
- Compose con volumen persistente, activo digital montado en solo lectura y filesystem de aplicación read-only.
- Configuración Nginx de referencia para HTTPS y proxy inverso.
- Cierre ordenado SIGTERM/SIGINT y timeouts HTTP.

EJECUTAR QA
npm run qa

VALIDAR PRODUCCIÓN
set -a; . ./.env; set +a; npm run preflight

DESPLEGAR
cp .env.example .env
# completar valores reales
docker compose up -d --build

NO PUBLICAR
- .env
- data/store.json real
- archivo maestro del producto
- secretos de Mailchimp, Resend o CompraClick
