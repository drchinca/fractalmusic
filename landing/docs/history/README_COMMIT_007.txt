FRACTAL MUSIC WORLD — COMMIT 007
Correo transaccional y endurecimiento para producción

VERSIÓN
0.7.0

ARCHIVOS NUEVOS
- email.js
- logger.js
- recuperar.html
- recovery.js

ARCHIVOS MODIFICADOS
- server.js
- admin.html
- admin.js
- confirmacion.html
- package.json
- .env.example
- data/store.json

IMPLEMENTACIÓN CERRADA
1. Correo automático al confirmarse una compra.
2. Plantillas HTML y texto para confirmación y recuperación.
3. Enlace privado de descarga y comprobante incluidos en el correo.
4. Recuperación de acceso mediante correo + referencia de compra.
5. Renovación invalida el token anterior y genera una expiración nueva.
6. Respuesta neutra para impedir enumeración de compradores.
7. Límite configurable de solicitudes de recuperación por IP.
8. Cola persistente para reintentar correos fallidos o no configurados.
9. Reprocesamiento administrativo de Mailchimp y correo.
10. Registro persistente de entregas transaccionales.
11. Cabeceras CSP, X-Frame-Options, Permissions-Policy y nosniff.
12. Errores 5xx sin exposición de detalles internos.
13. Logs estructurados JSON con secretos redactados.
14. Estado del proveedor de correo visible en /api/health.
15. Métrica de correos enviados en el panel administrativo.

PROVEEDOR IMPLEMENTADO
Resend mediante API HTTP. No se agregaron dependencias npm.

VARIABLES NUEVAS
EMAIL_PROVIDER=resend
EMAIL_API_KEY=
EMAIL_FROM=Fractal Music World <noreply@fractalmusicworld.com>
EMAIL_REPLY_TO=
FMW_RECOVERY_MAX_PER_HOUR=5
FMW_TRUST_PROXY=false
NODE_ENV=production

VALIDACIÓN
npm run check

CONTINÚA
Commit 008: QA integral, pruebas automatizadas del flujo completo y paquete de despliegue.
