# Fractal Music World — optimización creativa final

**Versión:** COMMIT 019 — Optimización creativa final  
**Base preservada:** COMMIT 018 — Fauna Fractal / Reorquestación de personajes  
**Fecha de optimización:** 24 de agosto de 2026  
**Estado:** base técnica preservada y Home depurada para revisión creativa final.

## Qué cambió en COMMIT 019

- Hero concentrado en Gátople, el titular principal y dos acciones.
- Retiro de personajes pequeños en Hero, Participación y Acción.
- Reducción de ruido visual en El Llamado mediante rutas numeradas.
- Nombre y principio visibles para todos los personajes de El Descubrimiento.
- Numeración continua: Movimiento I a Movimiento VII; `HOME-001` permanece como Umbral.
- Jerarquía tipográfica más decidida y mayor espacio entre escenas.
- Transiciones visuales entre Movimientos.
- Botones normalizados en tamaño, forma, prioridad y respuesta de foco.
- Tratamiento visual común para las imágenes de la Fauna conservadas.
- Refinamiento mobile de navegación, titulares, áreas táctiles y composición relacional.
- Restauración Gátople A9: montaje centrado, estaciones constitucionales, piano de La a La y glifo oficial de dos puntos.

El detalle completo está en `docs/REVISION_COMMIT_019_OPTIMIZACION_CREATIVA.md`.

## Qué contiene

- Home completa organizada en ocho escenas (`HOME-001` a `HOME-008`): Umbral y siete Movimientos.
- Fauna Fractal integrada narrativamente: Musicalia, Juglar, Trilobites, Vesica Piscis, Lute y Gátople.
- The Dissonance Test: 12 preguntas, 48 opciones técnicas y 12 arquetipos.
- Resultado, recomendación, captura de datos, checkout, confirmación y recuperación.
- Integración preparada para CompraClick, Mailchimp y correo transaccional.
- Panel administrativo protegido por token.
- Gátople Core con orientación constitucional A9.
- Libreto integral revisado en `FMW_LIBRETO_COMPLETO_HOME_001_008_FAUNA_FRACTAL.docx`.
- Historial de commits en `docs/history/`.

## Requisitos

- Node.js 20 o superior.
- npm.

## Arranque local

```bash
cp .env.example .env
npm install
npm run qa
npm start
```

Abrir `http://localhost:3000`.

## Variables obligatorias antes de producción

Configurar en Vercel o en el servidor:

- `PUBLIC_BASE_URL`
- `FMW_ADMIN_TOKEN`
- `COMPRACLICK_CHECKOUT_URL`
- `COMPRACLICK_WEBHOOK_SECRET`
- `FMW_PRODUCT_FILE`
- `EMAIL_API_KEY`
- `EMAIL_FROM`

Mailchimp requiere además:

- `MAILCHIMP_API_KEY`
- `MAILCHIMP_SERVER_PREFIX`
- `MAILCHIMP_AUDIENCE_ID`

Nunca subir el archivo `.env` ni credenciales reales al repositorio.

## Verificación

```bash
npm run qa
npm run preflight
```

La consolidación original pasó **16/16 pruebas automatizadas**. En la revisión COMMIT 019.1 pasan las 16 pruebas que no requieren iniciar un servidor, incluidas las nuevas protecciones de orientación A9, piano de La a La y glifo de dos puntos, además de la simulación determinista de 250.000 respuestas. Las tres pruebas de flujo integral requieren un entorno que permita abrir un puerto local. El motor del test está técnicamente validado para beta controlada; la validación psicométrica con participantes reales sigue siendo una fase posterior.

## Despliegue en Vercel

1. Crear/importar el proyecto desde esta carpeta raíz.
2. Usar Node.js 20.
3. Registrar las variables de entorno.
4. Desplegar.
5. Configurar en CompraClick el webhook hacia la ruta API publicada.
6. Ejecutar una compra de prueba en entorno controlado.

## Archivos de entrada principales

- `index.html`: Home.
- `server.js`: servidor y API local.
- `api/index.js`: entrada serverless para Vercel.
- `test.html` / `test-app.js`: Test.
- `scoring-engine.js`: puntuación.
- `resultado.html` / `resultado.js`: resultado.
- `comprar.html` / `checkout.js`: compra.
- `admin.html` / `admin.js`: administración.
- `gatople.html` / `gatople-core.js`: Gátople.

## Límite de esta entrega

La estructura, el flujo y la narrativa están consolidados. Antes de publicar al público deben conectarse credenciales reales, archivo de producto, webhook de CompraClick y proveedor de correo, y ejecutarse una transacción real de prueba. La respuesta pendiente del BAC no bloquea la revisión creativa, pero sí debe resolverse antes del cierre comercial definitivo.
