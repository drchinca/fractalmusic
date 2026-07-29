FMW WEB COMMIT 012 — VERCEL LISTO

Este paquete sí está preparado para importarse directamente en Vercel.

PUBLICACIÓN:
1. En Vercel: Add New > Project.
2. Importar esta carpeta o subirla a un repositorio Git.
3. Framework Preset: Other.
4. Build Command: dejar vacío.
5. Output Directory: dejar vacío.
6. Deploy.
7. En Project > Settings > Domains, asignar fractalmusicworld.com y www.fractalmusicworld.com.

VARIABLES DISPONIBLES:
PUBLIC_BASE_URL=https://fractalmusicworld.com
FMW_ADMIN_TOKEN=<token nuevo y privado>
MAILCHIMP_API_KEY=<cuando BAC/Mailchimp lo entreguen>
MAILCHIMP_SERVER_PREFIX=<ejemplo us21>
MAILCHIMP_AUDIENCE_ID=<audience id>
COMPRACLICK_CHECKOUT_URL=<checkout BAC>
COMPRACLICK_WEBHOOK_SECRET=<secreto webhook>

NOTA TÉCNICA:
La interfaz, el test, la puntuación, los resultados y las rutas quedan desplegables ya.
Mientras no exista una base de datos externa, Vercel usa /tmp para el almacenamiento del proceso; Mailchimp y CompraClick se conectan mediante variables de entorno cuando estén disponibles.
