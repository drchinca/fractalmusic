# Entrega técnica para Bado — Fractal Music World

Fecha: 26 de agosto de 2026  
Base: COMMIT 019 — Optimización creativa final  
Versión del servidor: 0.9.0

## Incluye

- Web completa de Fractal Music World.
- Gátople público V0.46 integrado en `gatople.html`.
- The Dissonance Test optimizado y validado.
- Configuración de Vercel en `vercel.json`.
- Flujo preparado para CompraClick, confirmación, correo y entrega digital.
- Panel administrativo y recuperación de compras.
- Manifiesto SHA-256 de integridad.
- Página `COMPRAR` configurada en modo asistido: solicita el enlace manual de CompraClick por WhatsApp o correo y no promete confirmación automática.

## Verificación realizada

- 21 de 21 pruebas automatizadas aprobadas.
- Simulación de 250.000 recorridos del Test Disonante.
- Prueba de 40 eventos simultáneos sin pérdidas.
- El paquete no contiene credenciales reales ni datos de compradores.

## Obligatorio antes de publicar sobre producción

1. Importar/desplegar esta carpeta raíz con Node.js 20.
2. Configurar las variables descritas en `.env.example`.
3. Mantener el flujo asistido de CompraClick hasta que BAC habilite E-Commerce o Simple Pay. CompraClick no ofrece API, webhook ni automatización.
4. Configurar almacenamiento persistente externo para leads, transacciones y eventos. `/tmp` de Vercel no es una base de datos durable.
5. Configurar el proveedor de correo transaccional.
6. Configurar el archivo digital definitivo o almacenamiento privado desde el que se entregará.
7. Ejecutar `npm run qa` y `npm run preflight`.
8. Realizar una compra controlada completa antes de activar ventas públicas.

## Variables principales

- `PUBLIC_BASE_URL=https://fractalmusicworld.com`
- `FMW_ADMIN_TOKEN`
- `COMPRACLICK_CHECKOUT_URL`
- `COMPRACLICK_WEBHOOK_SECRET` solamente si BAC confirma ese contrato
- `EMAIL_API_KEY`
- `EMAIL_FROM`
- `FMW_PRODUCT_FILE` o sustitución por almacenamiento privado persistente
- Credenciales de Mailchimp, si se utilizará

## Advertencia comercial

CompraClick está activo para Fractal Music World en modalidad manual. El comprador solicita el enlace, el comercio lo genera desde MiPOS, verifica el pago y entrega el producto manualmente. El código automático se conserva únicamente para una futura migración a E-Commerce o Simple Pay; no debe activarse como si CompraClick ofreciera webhook o API.
