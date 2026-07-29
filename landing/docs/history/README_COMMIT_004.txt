COMMIT 004 — MAILCHIMP + PREPARACIÓN SEGURA COMPRACLICK

Terminado:
- Upsert seguro de contactos en una audiencia Mailchimp.
- Merge fields y etiquetas oficiales del Test.
- Cola persistente de reintentos si Mailchimp falla o no está configurado.
- Endpoint administrativo de reintento.
- Inicio de checkout desde servidor.
- Transacciones pendientes persistidas e idempotencia por referencia.
- Webhook firmado por HMAC para confirmar compra.
- Actualización de COMPRA, PRODUCTO, COMPRADOR_FMW e INICIADO_FMW.
- Eventos purchase_completed y postpurchase_started.
- Formulario de CompraClick agregado a comprar.html.

Configuración pendiente de producción:
- Credenciales Mailchimp.
- URL real de checkout CompraClick.
- Secreto y contrato exacto de firma entregado por BAC.
