# ¿Qué es Fractal Music World?

> *"Aprende música desde un idioma que no es la música: la etno-matemática."*
> — Patricio Torres Rivera, *El Sistema Fractal: Música Viva y en Reproducción* (2024)

**Fractal Music World** es un emprendimiento educativo artístico-científico
fundado en 2019 por el compositor ecuatoriano-costarricense **Patricio Torres
("Pattorres")** y **Katherina Castro**. Su núcleo es el **Sistema Fractal**, un
método que enseña música a través de la geometría, el número, el color y el
símbolo — recuperando el conocimiento musical ancestral que la educación tonal
moderna dejó de lado.

Este documento explica las ideas del sistema. El paquete `fractalmusic`
(ver [README](./README.md)) las implementa en código sobre
[pytheory](https://pytheory.org).

---

## Tabla de contenidos

- [La idea central](#la-idea-central)
- [El Dodecamundo (5 + 7 = 12)](#el-dodecamundo-5--7--12)
- [El Gátople, el astrolabio musical](#el-gátople-el-astrolabio-musical)
- [Los 12 modos y sus símbolos](#los-12-modos-y-sus-símbolos)
- [Origen en La menor, no en Do mayor](#origen-en-la-menor-no-en-do-mayor)
- [Las pentatónicas primero](#las-pentatónicas-primero)
- [La etno-matemática: Pitágoras, Fibonacci, potenciación](#la-etno-matemática-pitágoras-fibonacci-potenciación)
- [Glosario](#glosario)

---

## La idea central

La música es una **función fractal**: estructuras simples que se auto-replican a
cualquier escala — igual que las ramas de un árbol, una espiral de nautilo o una
red neuronal. *"Como es arriba es abajo"* (Kybalión). Si aprendes la arquitectura
mínima, puedes generar todo el universo musical desde ella.

El método convierte las notas en **mundos con color, forma, número y función
algebraica**. Las notas dejan de ser teclas blancas y negras y se vuelven cartas
de un juego — un "tarot musical" de 12 cartas — que se manipulan sobre un reloj
trigonométrico, el **Gátople**.

## El Dodecamundo (5 + 7 = 12)

Las 12 notas cromáticas forman el **Dodecamundo**: dos sistemas simbióticos.

```
5 (pentatónico, teclas negras)  +  7 (diatónico, teclas blancas)  =  12
```

- **7 naturales** (A B C D E F G) → los 7 modos griegos diatónicos.
- **5 negras** (A♯ C♯ D♯ F♯ G♯) → los 5 Penta-modos pentatónicos, las "estrellas".

El número 12 es estructural en la naturaleza: 12 horas, 12 meses, 12
constelaciones, ciclos de 12 años de Júpiter. El Dodecamundo es el *códex* del
sistema.

## El Gátople, el astrolabio musical

El **Gátople** ("gato cíclope") es un reloj de 12 segmentos con un ojo central —
el logo del sistema. Es un **instrumento trigonométrico**: cada nota ocupa una
hora, los intervalos se vuelven ángulos, y los acordes y escalas se vuelven
**polígonos inscritos** en el círculo. Mide y ubica la música — *"ubicación y
medida musical"*.

La fórmula que lo mueve es el **Cero Pitágoras**: poner los cinco dedos sobre las
cinco teclas negras y componer desde ahí. Es la semilla pentatónica ancestral.

## Los 12 modos y sus símbolos

Cada mundo lleva el glifo de su modo (cap. 8, "Música de Colores"):

| Nota | Modo | Glifo | Calidad | Hora | Color |
|------|------|:-----:|---------|:----:|-------|
| A | Eólico | `⋮` | menor | 9 | verde |
| A♯ | Penta 5 | `★ V` | menor | 1 | magenta |
| B | Locrio | `△` | disminuido | 7 | verde-amarillo |
| C | Jónico | `□` | mayor | 12 | amarillo |
| C♯ | Penta 1 | `★ I` | menor | 5 | turquesa |
| D | Dórico | `+` | menor | 2 | azul |
| D♯ | Penta 2 | `★ II` | menor | 9 | azul profundo |
| E | Frigio | `♀` | menor | 8 | violeta |
| F | Lidio | `↑` | mayor | 1 | índigo |
| F♯ | Penta 3 | `★ III` | mayor | 6 | púrpura |
| G | Mixolidio | `↓` | mayor | 11 | naranja |
| G♯ | Penta 4 | `★ IV` | menor | 3 | rojo |

- `⋮` Eólico — los dos puntos de la división; descanso, el horizonte estable.
- `△` Locrio — el triángulo; puerta entre los mundos penta y hepta.
- `□` Jónico — el cuadrado; verticalidad, la escala mayor.
- `+` Dórico — la cruz; primer Cero Pitágoras, inestabilidad que abre.
- `♀` Frigio — la llave (koppa ϙ) que cierra el círculo; sabor flamenco.
- `↑` Lidio — flecha exclusiva hacia arriba; híbrido penta-hepta.
- `↓` Mixolidio — flecha inclusiva hacia abajo; compresión, dominante 7.
- `★` Penta — las cinco estrellas pentatónicas (teclas negras).

## Origen en La menor, no en Do mayor

El sistema mide desde **La (A) menor**, no desde **Do (C) mayor**. Razones del
libro:

- Ontológicamente, **A está antes que C** en el alfabeto primigenio A B C D E F G.
- El acorde de A menor (La-Do-Mi) y el de C mayor (Do-Mi-Sol) comparten Do y Mi;
  partir de C deja a La en un "sexto grado lejano".
- A Eólico es el **horizonte** — la escala más estable, femenina, matriarcal.

`fractalmusic` hereda esto gratis: pytheory ya indexa su sistema occidental
**desde A** (índice 0 = A, índice 3 = C).

## Las pentatónicas primero

Las 5 escalas pentatónicas son **ontológicamente anteriores** a las 7
heptatónicas (el 5 viene antes que el 7). Son el "sistema óseo" de la música:

- No tienen semitonos → son "a prueba de errores", resistentes.
- Son la base de la música folclórica ancestral de todas las tribus.
- 5 Penta-modos × 12 tonalidades = **60 microestructuras** que sustentan todo.
- Generan las heptatónicas: penta → hepta.

## La etno-matemática: Pitágoras, Fibonacci, potenciación

- **Teorema de Pitágoras** → análisis armónico e identificación sonora; los
  intervalos como razones de frecuencia (la quinta justa = 3:2).
- **Serie Fibonacci / Phi (φ ≈ 1.618)** → construcción de acordes.
- **Potenciación** (cuento del tablero de ajedrez) → 1, 2, 4, 16, 256… el
  crecimiento geométrico, el infinito (8 = ∞) accesible desde un grano de trigo.
- **La tabla periódica de sonidos** → el brazo de la guitarra (o el teclado) como
  una matriz química donde cada sonido es un elemento que combina en "compuestos"
  (acordes), produciendo bioquímica en el cerebro.

## Glosario

- **Dodecamundo** — el conjunto de las 12 notas cromáticas como "mundos".
- **Gátople** — el reloj/astrolabio trigonométrico de 12 notas (gato cíclope).
- **Cero Pitágoras** — componer desde las 5 teclas negras (semilla pentatónica).
- **Carta** — una nota-mundo como naipe ilustrado (color + glifo + número).
- **Penta-modo** — uno de los 5 modos pentatónicos (estrellas I–V).
- **Microestructura** — una de las 60 escalas penta (5 modos × 12 raíces).
- **Etno-matemática** — el lenguaje numérico-natural-filosófico de la música.
- **VDMG** — "Virus del Mal Gusto", el antagonista pedagógico del libro.

---

*Todos los derechos del Sistema Fractal y el Gátople pertenecen a Patricio
Torres Rivera / Fractal Music World. Este repositorio es una implementación de
estudio basada en el libro y los materiales públicos.*
