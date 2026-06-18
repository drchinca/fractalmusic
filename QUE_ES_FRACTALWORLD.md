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
| A | Eólico | `⋮` Dos Puntos | menor | 9 | rojo |
| A♯ | Penta 5 | `★ V` Estrella V | menor | 2 | azul profundo |
| B | Locrio | `△` Triángulo | disminuido | 7 | verde |
| C | Jónico | `■` Casita | mayor | 12 | rojo (techo) |
| C♯ | Penta 1 | `★ I` Estrella I | menor | 5 | azul agua + naranja |
| D | Dórico | `+` Más / Cruz | menor | 10 | verde |
| D♯ | Penta 2 | `★ II` Estrella II | menor | 3 | azul + sol naranja |
| E | Frigio | `♀` Llave (koppa) | menor | 8 | rojo |
| F | Lidio | `↑` Flecha arriba | mayor | 1 | azul cielo |
| F♯ | Penta 3 | `★ III` Estrella III | mayor | 6 | rojo (casa de Gátople) |
| G | Mixolidio | `↓` Flecha abajo | mayor | 11 | verde |
| G♯ | Penta 4 | `★ IV` Estrella IV | menor | 4 | azul + reflejos naranja |

> Los nombres y colores de la tabla son los canónicos de las 12 cartas pintadas
> a mano por Patricio Torres (digitalizadas 2026-06). Las notas listadas son
> las del **default A-tonic**: rotan cuando giras el disco interior.

> Las horas siguen el **círculo de cuartas** (Función Cuartal, cap. 4): cada hora
> avanza una cuarta justa (+5 semitonos) desde A Eólico = 9. Es una biyección:
> las 12 notas ocupan las 12 horas sin repetición.

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
- **Función Cuartal** — el orden por cuartas justas (+5 semitonos) que rige el reloj
  del Gátople; ubica cada nota en su hora desde A Eólico = 9.
- **Potenciación** — el crecimiento geométrico (cuento del tablero de ajedrez): un
  número se multiplica por sí mismo hasta el infinito (8 = ∞).
- **VDMG** — "Virus del Mal Gusto", el antagonista pedagógico del libro.

### Las 12 cartas, por nombre

- **Dos Puntos** (`⋮`) — carta 1, A, Eólico. Los dos puntos de la división.
- **Estrella V** (`★ V`) — carta 2, A♯/B♭, Penta 5.
- **Triángulo** (`△`) — carta 3, B, Locrio. La primera figura geométrica natural.
- **Casita** (`■`) — carta 4, C, Jónico. Casa con techo rojo y puerta amarilla.
- **Estrella I** (`★ I`) — carta 5, C♯/D♭, Penta 1.
- **Más** (`+`) — carta 6, D, Dórico. La cruz, primer Cero Pitágoras.
- **Estrella II** (`★ II`) — carta 7, D♯/E♭, Penta 2.
- **Llave** (`♀`) — carta 8, E, Frigio. La koppa (ϙ) que cierra el círculo.
- **Flecha arriba** (`↑`) — carta 9, F, Lidio.
- **Estrella III** (`★ III`) — carta 10, F♯/G♭, Penta 3. La casa de Gátople.
- **Flecha abajo** (`↓`) — carta 11, G, Mixolidio. Compresión hacia el dominante.
- **Estrella IV** (`★ IV`) — carta 12, G♯/A♭, Penta 4.

---

*Todos los derechos del Sistema Fractal y el Gátople pertenecen a Patricio
Torres Rivera / Fractal Music World. Este repositorio es una implementación de
estudio basada en el libro y los materiales públicos.*
