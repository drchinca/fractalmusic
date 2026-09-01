# FMW · COMMIT 019 · Optimización creativa final

Fecha: 24 de agosto de 2026  
Base: COMMIT 018 — Fauna Fractal / Reorquestación de personajes

## Principio de la revisión

La web no se reconstruye. Se preservan la arquitectura, el Test, el Gátople, los flujos comerciales y el libreto consolidado. COMMIT 019 aplica una poda visual para que cada personaje aparezca solamente cuando cumple una función narrativa legible.

## Decisiones implementadas

### Hero · Movimiento I

- Gátople queda como único protagonista visual.
- Se retiran la constelación de cinco personajes pequeños y los indicadores de fauna del encabezado.
- Se conservan dos acciones: `Descubrir mi arquetipo` y `Explorar FMW`.
- Se amplían escala tipográfica, respiración y presencia del emblema.

### El Llamado · Movimiento II

- Las seis entradas permanecen, pero ya no compiten seis retratos y seis nombres.
- Las rutas se ordenan mediante una numeración sobria de `01` a `06`.

### El Descubrimiento · Movimiento III

- Se conserva la red de personajes porque aquí sí constituye el argumento central.
- Cada aparición muestra nombre y principio: Juglar / Inspiración, Vesica Piscis / Proporción, Lute / Geometría viva, Trilobites / Memoria geológica y Musicalia / Imaginación encarnada.
- Gátople queda identificado como Articulación.
- Los retratos reciben un tratamiento común de encuadre, borde, contraste y color.

### La Participación · Movimiento IV

- Se retiran miniaturas y nombres de personajes de las seis puertas.
- El contenido, la numeración y el destino vuelven a ser la jerarquía principal.
- The Dissonance Test conserva la puerta dominante.

### La Dirección · Movimiento V

- Se conservan Musicalia, Trilobites y Juglar porque acompañan una secuencia concreta: reconocer, relacionar y transformar.
- Sus imágenes reciben el mismo tratamiento visual.
- Gátople conserva su escena protagónica propia.

### La Acción · Movimiento VI

- Se retiran cuatro miniaturas laterales.
- Obras, Experiencias, Símbolos vivos y Adquirir quedan como acciones claras y no como un segundo catálogo de personajes.

### La Resonancia · Movimiento VII

- Se conserva la imagen coral como cierre narrativo.
- La fauna aparece reunida una sola vez, no fragmentada en pequeñas voces competitivas.

## Sistema visual

- Numeración continua de Movimiento I a Movimiento VII. `HOME-001` funciona como Umbral.
- Pausas gráficas entre escenas para reforzar el ritmo cinematográfico.
- Botones con altura mínima consistente, radio común, foco visible y prioridad primaria/secundaria.
- Mayor espacio vertical y titulares con contraste de escala más agresivo.
- Navegación mobile con áreas táctiles de al menos 44 px y desplazamiento interno seguro.
- Hero mobile ordenado como mensaje → acciones → Gátople.
- Composición relacional reajustada para pantallas estrechas.
- Preferencia de movimiento reducido preservada.

## Verificación

- Sintaxis JavaScript: aprobada.
- Pruebas independientes del servidor: 16/16 aprobadas.
- Matriz del Test: 12 preguntas, 48 opciones técnicas y 12 arquetipos.
- Simulación determinista: 250.000 respuestas.
- Estado del motor: técnicamente válido para beta controlada.
- Las tres pruebas E2E no pudieron repetirse en el entorno de revisión porque este no permite abrir el puerto del servidor. La entrega COMMIT 018 conserva el registro archivado de 16/16 pruebas.

## Dependencias externas pendientes

- Respuesta del BAC.
- Credenciales y definición final de la ruta comercial.
- Webhook de CompraClick y firma.
- Proveedor de correo y Mailchimp.
- Archivo digital definitivo.
- Compra real de monto mínimo.
- Dominio, DNS, analítica, SEO y consentimiento de datos.

Estas dependencias no bloquean el cierre creativo, pero sí el cierre público y comercial.

## Corrección COMMIT 019.1 · Gátople A9

La comparación con la versión publicada permitió identificar una regresión de la entrega local:

- Se perdió la compensación geométrica entre el centro real del rostro/sigil y el centro matemático de la rueda.
- La rueda local volvió a distribuir las funciones consecutivamente, en lugar de usar las estaciones constitucionales del sigil.
- El piano local volvió a comenzar en Do.
- La referencia publicada recuperaba el piano en La, pero mostraba tres puntos para Memoria.

La versión corregida combina únicamente las decisiones válidas:

- Centro del rostro alineado proporcionalmente con el centro de la rueda en cualquier tamaño.
- Estaciones constitucionales: `12, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7`.
- Do permanece a las 12 h y La permanece a las 9 h.
- Piano de La a La: `A B C D E F G A`, con octavas correctas.
- Memoria/A usa el glifo oficial de dos puntos `∶`, no el glifo de tres puntos.
- Se añadieron pruebas automáticas específicas para impedir que estas decisiones vuelvan a perderse.
