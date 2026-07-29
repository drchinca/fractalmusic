# Fractal Music World — entrega canónica para Bado

**Versión:** COMMIT 018 — Fauna Fractal / Reorquestación de personajes  
**Fecha de consolidación:** 28 de julio de 2026  
**Estado:** base técnica y narrativa consolidada para integración y despliegue controlado.

## Qué contiene

- Home completa organizada en ocho movimientos (`HOME-001` a `HOME-008`).
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

La consolidación pasó **16/16 pruebas automatizadas**. El motor del test está técnicamente validado para beta controlada; la validación psicométrica con participantes reales sigue siendo una fase posterior.

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

La estructura, el flujo y la narrativa están consolidados. Antes de publicar al público deben conectarse credenciales reales, archivo de producto, webhook de CompraClick y proveedor de correo, y ejecutarse una transacción real de prueba.
