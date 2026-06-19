# Fidelity Threshold Calibration

- Pairs: 40 (20 supporting, 20 non-supporting)
- Embedder: Ollama nomic-embed-text, cosine similarity

## Score distribution

- Supporting pairs:    min=0.748  median=0.871  max=0.980
- Non-supporting:      min=0.526  median=0.726  max=0.873

## Sweep

| threshold | TP | FP | TN | FN | precision | recall | F1 | accuracy |
|---|---|---|---|---|---|---|---|---|
| 0.30 | 20 | 20 | 0 | 0 | 0.500 | 1.000 | 0.667 | 0.500 |
| 0.35 | 20 | 20 | 0 | 0 | 0.500 | 1.000 | 0.667 | 0.500 |
| 0.40 | 20 | 20 | 0 | 0 | 0.500 | 1.000 | 0.667 | 0.500 |
| 0.45 | 20 | 20 | 0 | 0 | 0.500 | 1.000 | 0.667 | 0.500 |
| 0.50 | 20 | 20 | 0 | 0 | 0.500 | 1.000 | 0.667 | 0.500 |
| 0.55 | 20 | 18 | 2 | 0 | 0.526 | 1.000 | 0.690 | 0.550 |
| 0.60 | 20 | 15 | 5 | 0 | 0.571 | 1.000 | 0.727 | 0.625 |
| 0.65 | 20 | 14 | 6 | 0 | 0.588 | 1.000 | 0.741 | 0.650 |
| 0.70 | 20 | 11 | 9 | 0 | 0.645 | 1.000 | 0.784 | 0.725 |
| 0.75 | 19 | 8 | 12 | 1 | 0.704 | 0.950 | 0.809 | 0.775 |
| 0.80 | 17 | 4 | 16 | 3 | 0.810 | 0.850 | 0.829 | 0.825 |
| 0.85 | 13 | 2 | 18 | 7 | 0.867 | 0.650 | 0.743 | 0.775 |
| 0.90 | 7 | 0 | 20 | 13 | 1.000 | 0.350 | 0.519 | 0.675 |

## Chosen threshold: **0.79**

- F1: 0.857  (P=0.818, R=0.900)
- TP=18, FP=4, TN=16, FN=2

## All pairs, sorted by score

| score | supports | claim |
|---|---|---|
| 0.526 | ✗ | La función de Bessel modifica las series de Fourier en guías de onda. |
| 0.528 | ✗ | Las mesas consagradas a Júpiter eran de oro mientras que las de Diana eran de... |
| 0.553 | ✗ | Los chacras se despiertan mediante prácticas de tantra y kundalini. |
| 0.558 | ✗ | Bach inventó el contrapunto en el siglo XVIII basándose en estos principios. |
| 0.592 | ✗ | La luna en Capricornio favorece el control y la disciplina personal. |
| 0.608 | ✗ | El swing y el bebop dependen de subdivisiones rítmicas extremas. |
| 0.661 | ✗ | La pentatónica es exclusivamente una construcción del barroco europeo. |
| 0.682 | ✗ | El sistema parte desde la nota Do mayor como tonalidad matriarcal universal. |
| 0.698 | ✗ | El Frigio es un modo mayor luminoso que se usa principalmente en el jazz bebop. |
| 0.725 | ✗ | El Cero Pitágoras requiere ocho notas en orden cromático ascendente. |
| 0.726 | ✗ | Los semitonos del sistema son el Do y el Sol. |
| 0.738 | ✗ | El Dodecamundo está formado por 7 notas heptatónicas y nada más. |
| 0.748 | ✓ | El sistema utiliza simbología ancestral basada en ejes transversales. |
| 0.758 | ✓ | La pentatónica fue usada por tribus de todo el planeta, ancestralmente. |
| 0.765 | ✗ | El Frigio nunca se relaciona con el Lidio en ningún contexto musical. |
| 0.784 | ✗ | El sistema desaconseja explícitamente el uso de simbología ancestral. |
| 0.788 | ✗ | El Mixolidio cierra el mundo hepta menor con tensión disminuida. |
| 0.788 | ✗ | El sistema solo enseña ritmo y deja de lado la armonía y la melodía. |
| 0.797 | ✓ | El Frigio funciona como dominante del Eólico. |
| 0.805 | ✗ | El sistema rechaza explícitamente el uso de matrices y figuras geométricas en... |
| 0.826 | ✓ | Los semitonos en el sistema son el Si y el Fa. |
| 0.836 | ✓ | La escala pentatónica no tiene semitonos. |
| 0.841 | ✓ | El Dodecamundo es un conjunto de doce mundos sonoros donde ninguno es igual a... |
| 0.844 | ✗ | La Función Cíclica añade siete alteraciones cromáticas a la escala original. |
| 0.846 | ✓ | El libro propone descubrir la música mediante matrices, figuras geométricas y... |
| 0.864 | ✓ | El Frigio es la base sonora del flamenco árabe-español, partiendo en semitono... |
| 0.865 | ✓ | El Sistema Fractal incluye habilidades de autoconocimiento, empatía y pensami... |
| 0.866 | ✓ | El Locrio es la sensible que siempre aparece junto al Jónico. |
| 0.867 | ✗ | El Locrio es siempre tónico estable, nunca aparece junto al Jónico. |
| 0.871 | ✓ | Cada elemento del Dodecamundo tiene un peso molecular único. |
| 0.873 | ✗ | La pentatónica contiene semitonos como cualquier otra escala diatónica. |
| 0.873 | ✓ | El Dodecamundo funciona como un ecosistema: si algo falta, todo lo demás se d... |
| 0.899 | ✓ | El Cero Pitágoras genera una semilla pentatónica de cinco notas sin semitonos. |
| 0.909 | ✓ | La pentatónica ha sido la base de la música folclórica durante miles de años. |
| 0.910 | ✓ | La pentatónica está libre de semitonos, lo que la hace resistente a errores. |
| 0.924 | ✓ | El Sistema Fractal explora la música desde la armonía, la melodía y el ritmo. |
| 0.929 | ✓ | La Función Cíclica nos hace volver a la tonalidad de origen con cero alteraci... |
| 0.932 | ✓ | Aplicando el teorema de Pitágoras y la serie Fibonacci se experimentan los pr... |
| 0.937 | ✓ | La revisión del sistema parte desde la nota La menor, que produce la tonalida... |
| 0.980 | ✓ | El Mixolidio es el dominante 7 del Jónico, el punto antes del cierre del mund... |
