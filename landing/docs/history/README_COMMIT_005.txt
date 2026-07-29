FMW WEB — COMMIT 005
Entrega personalizada y memoria evolutiva

AGREGADO
- muestra.html / muestra.js / samples.js: doce muestras personalizadas, una por arquetipo.
- resultado.html / resultado.js: informe registrado e historial evolutivo del usuario.
- API POST /api/history protegida por token de acceso por contacto.
- Persistencia de cada ejecución del test en assessments, sin sobrescribir ciclos anteriores.
- Comparación automática entre la medición actual y la anterior: inicial, estable, cambio secundario o cambio dominante.
- Descarga local de la muestra personalizada.

MODIFICADO
- test-app.js: URL real de muestra, result_id, acceso al informe después de guardar.
- api-client.js: lectura segura del historial.
- server.js: store v3, assessments, token de acceso, historial y versión 0.5.0.
- styles.css: vistas de informe, muestra e historial.
- test.html: botón de acceso al informe completo.

EJECUCIÓN
npm start
http://localhost:3000/test.html
