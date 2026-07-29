# Entrega para Bado

Este ZIP es la única base activa. No trabajar sobre COMMIT 016, COMMIT 017 ni sobre `Archivo(17).zip`.

## Estado cerrado

- Arquitectura Home de ocho movimientos.
- Fauna Fractal reorquestada en los ocho movimientos.
- Libreto completo alineado con la implementación.
- The Dissonance Test y motor de puntuación.
- Resultado, lead, checkout, confirmación, recuperación y administración.
- Configuración para Vercel.
- Suite automatizada: 16/16 pruebas aprobadas.

## Trabajo de integración que requiere credenciales o decisiones externas

1. Introducir las credenciales reales en Vercel.
2. Confirmar URL y firma del webhook de CompraClick.
3. Definir y montar el PDF/archivo digital definitivo que se entregará.
4. Configurar Resend u otro proveedor transaccional.
5. Configurar Mailchimp si se activa la secuencia comercial.
6. Ejecutar compra real de monto mínimo y verificar correo, descarga y registro administrativo.
7. Revisar dominio, DNS, analítica, SEO final y consentimiento de datos.

## Regla de continuidad

Toda modificación debe partir de esta carpeta y conservar las pruebas existentes. Antes de entregar un cambio:

```bash
npm run qa
```
