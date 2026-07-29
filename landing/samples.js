import { archetypes } from "./test-data.js";

const sampleBodies = {
  "el-oido-fractal": {
    title: "El patrón detrás del ruido",
    opening: "Tu escucha no se detiene en el objeto sonoro. Busca la relación que lo conecta con aquello que todavía no se ve.",
    practice: "Escucha durante tres minutos un espacio cotidiano. Anota cinco sonidos y dibuja las conexiones de distancia, repetición, causa y respuesta entre ellos.",
    question: "¿Qué estructura aparece cuando dejas de escuchar sonidos aislados?"
  },
  "el-colorista-armonico": {
    title: "La paleta sonora",
    opening: "Tu creatividad traduce tensión, timbre y movimiento en temperatura, color y textura emocional.",
    practice: "Elige una progresión breve. Asigna a cada acorde un color, una densidad y una dirección. Después cambia solo una cualidad y observa cómo cambia el sentido completo.",
    question: "¿Qué color todavía no has permitido entrar en tu obra?"
  },
  "el-arquitecto-de-la-disonancia": {
    title: "Construir con tensión",
    opening: "La disonancia es para ti una fuerza direccional: no un defecto, sino una estructura que exige movimiento.",
    practice: "Crea una tensión de cuatro compases y retrasa su resolución dos veces. Registra en qué punto deja de ser fértil y empieza a perder dirección.",
    question: "¿Qué tensión de tu obra necesita una puerta y no una eliminación?"
  },
  "el-juglar-transmedia": {
    title: "La idea que encuentra voz",
    opening: "Tu obra busca desplazarse: del sonido a la palabra, de la palabra al gesto y del gesto a la experiencia compartida.",
    practice: "Describe una idea musical en tres medios: una frase, una imagen y una acción escénica. Conserva el mismo núcleo en los tres.",
    question: "¿Cuál es el núcleo que debe sobrevivir cuando cambia el formato?"
  },
  "el-guardian-del-ritmo": {
    title: "El cuerpo sabe primero",
    opening: "Lees el mundo por pulsos, acentos y recurrencias. Tu pensamiento entra en movimiento antes de formularse.",
    practice: "Camina un pulso estable y desplaza un acento cada cuatro pasos. Observa cuándo el cuerpo comprende la nueva estructura sin contar.",
    question: "¿Qué parte de tu proceso necesita volver al cuerpo?"
  },
  "el-vegetal-antena": {
    title: "La memoria transmite",
    opening: "Tu raíz no es un archivo inmóvil. Es una antena que recibe voces, humor, calle, familia y paisaje.",
    practice: "Recupera un sonido de infancia y escríbelo sin nostalgia: como materia presente capaz de transformarse en ritmo, escena o personaje.",
    question: "¿Qué recuerdo pide convertirse en obra y dejar de ser únicamente recuerdo?"
  },
  "el-navegante-dodecasolido": {
    title: "Abrir el mapa",
    opening: "Tu mente organiza universos. Necesitas leyes, relaciones y recorridos que permitan comprender el conjunto.",
    practice: "Dibuja el mapa mínimo de una obra: origen, tres fuerzas, una transformación y una salida. Después elimina todo elemento que no cambie el recorrido.",
    question: "¿Dónde está la puerta de entrada de tu sistema?"
  },
  "el-alquimista-del-silencio": {
    title: "El peso de la pausa",
    opening: "Percibes el silencio como materia activa: marco, respiración, resonancia y condición de aparición.",
    practice: "Toma una frase de ocho compases y retira dos eventos esenciales. No rellenes el espacio. Escucha qué nueva fuerza adquiere lo que permanece.",
    question: "¿Qué necesita callar para que la estructura pueda hablar?"
  },
  "el-espejo-fractal": {
    title: "La totalidad en el fragmento",
    opening: "Reconoces cómo una pequeña forma puede contener la lógica del universo entero y cómo toda obra devuelve una imagen de quien la crea.",
    practice: "Elige un motivo de tres elementos. Reprodúcelo en ritmo, forma y narración sin copiar su superficie.",
    question: "¿Qué ley de tu universo ya está presente en su fragmento más pequeño?"
  },
  "el-crononauta-sonoro": {
    title: "Cruzar el tiempo sonoro",
    opening: "Tu creación conecta épocas. Tradición y tecnología no son extremos: son capas que pueden resonar simultáneamente.",
    practice: "Combina un gesto musical heredado con una herramienta actual. Conserva su memoria, pero cambia la dirección temporal de la experiencia.",
    question: "¿Qué pasado necesita futuro y qué futuro necesita memoria?"
  },
  "el-sintetizador-de-vacios": {
    title: "Dar forma a lo que falta",
    opening: "Detectas ausencias estructurales y conviertes la carencia en principio generador.",
    practice: "Define una obra por aquello que deliberadamente no tendrá. Construye tres decisiones positivas a partir de esa ausencia.",
    question: "¿Qué vacío ya está componiendo aunque todavía no lo nombres?"
  },
  "la-entropia-consciente": {
    title: "Dirigir la energía del caos",
    opening: "No necesitas extinguir el caos. Buscas el grado de organización suficiente para que libere potencia sin destruir la forma.",
    practice: "Genera diez materiales sin juzgarlos. Elige tres por contraste y establece una sola regla que permita su convivencia.",
    question: "¿Qué parte del caos necesita dirección y cuál debe conservar su libertad?"
  }
};

export const samples = Object.fromEntries(archetypes.map((archetype) => [archetype.id, {
  ...sampleBodies[archetype.id],
  archetype: archetype.name,
  group: archetype.group,
  zone: archetype.zone,
  diagnosis: archetype.diagnosis,
  blindSpot: archetype.blindSpot,
  identityPhrase: archetype.identityPhrase,
  affinity: archetype.suggestedAffinity,
  slug: archetype.id
}]));
