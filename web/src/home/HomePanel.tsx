import { type JSX } from "react";
import "../landing.css";

interface HomePanelProps {
  readonly onNavigate: (view: "gatople" | "composer" | "strudel" | "chat") => void;
}

export function HomePanel({ onNavigate }: HomePanelProps): JSX.Element {
  return (
    <div className="home-panel-wrapper">
      <main className="landing-main">
        {/* Movimiento I — La Obertura */}
        <section aria-labelledby="home-002-title" className="hero score-movement" data-home="HOME-002" data-movement="La Obertura" id="inicio">
          <div className="hero-copy">
            <p className="eyebrow">Movimiento I · La Obertura</p>
            <h1 id="home-002-title">El sonido también piensa.</h1>
            <h2>Un universo donde la música aprende a tener cuerpo.</h2>
            <p className="hero-intro">
              Fractal Music World convierte la música en experiencia viva: una forma de aprender,
              crear y comprender el sonido desde la geometría, el cuerpo, la naturaleza,
              la memoria y la imaginación.
            </p>
            <p className="hero-statement">
              No enseñamos música como una fila de datos.<br/>
              La volvemos experiencia, arquitectura, juego y lenguaje vivo.
            </p>
            <div className="button-group">
              <button className="btn btn-primary" onClick={() => onNavigate("gatople")}>
                Abrir la rueda interactiva
              </button>
              <a className="btn btn-secondary" href="#sistema-fractal">Explorar FMW</a>
            </div>
          </div>
          <div aria-label="Gátople, emblema principal de Fractal Music World" className="hero-emblem">
            <span aria-hidden="true" className="orbit-note orbit-note-a"></span>
            <span aria-hidden="true" className="orbit-note orbit-note-b"></span>
            <span aria-hidden="true" className="orbit-note orbit-note-c"></span>
            <div className="emblem-halo"></div>
            <img alt="Gátople luminoso con orejas, ojo central y sistema cromático" src="/assets/gatople-luminoso.png"/>
          </div>
        </section>

        <div aria-hidden="true" className="movement-transition"><span></span></div>

        {/* Movimiento II — El Llamado */}
        <section aria-labelledby="home-003-title" className="portal-strip score-movement" data-home="HOME-003" data-movement="El Llamado">
          <div className="portal-conductor">
            <p className="eyebrow">Movimiento II · El llamado</p>
            <h2 id="home-003-title">El universo comienza a responder.</h2>
            <p>No entras a un catálogo. Entras a un biosistema donde cada ruta escucha, transforma y devuelve una posibilidad.</p>
          </div>
          <div aria-label="Áreas de Fractal Music World" className="portal-voices">
            <a href="#obras"><span className="portal-index">01</span><strong>Libros</strong><small>Historias que caminan</small></a>
            <a href="#experiencias"><span className="portal-index">02</span><strong>Música</strong><small>Imaginación que toma cuerpo</small></a>
            <button onClick={() => onNavigate("gatople")} className="portal-btn-link"><span className="portal-index">03</span><strong>Juegos</strong><small>Relaciones que responden</small></button>
            <a href="#personajes"><span className="portal-index">04</span><strong>Personajes</strong><small>Memoria convertida en símbolo</small></a>
            <button onClick={() => onNavigate("composer")} className="portal-btn-link"><span className="portal-index">05</span><strong>Geometría</strong><small>Forma, eje y equilibrio</small></button>
            <a href="#experiencias"><span className="portal-index">06</span><strong>Academia</strong><small>Proporción para aprender</small></a>
          </div>
        </section>

        <div aria-hidden="true" className="movement-transition"><span></span></div>

        {/* Movimiento III — El Descubrimiento */}
        <section aria-labelledby="home-004-title" className="section discovery score-movement" data-home="HOME-004" data-movement="El Descubrimiento" id="que-es">
          <div className="discovery-intro">
            <p className="eyebrow">Movimiento III · El Descubrimiento</p>
            <h2 id="home-004-title">El sonido también piensa.</h2>
            <p>Una nota no vive sola. Busca otra. Forma una relación. La relación crea tensión. La tensión crea movimiento. El movimiento crea música.</p>
          </div>
          <div aria-label="Nacimiento de una red musical" className="relation-field">
            <figure className="fauna-relation fauna-rel-a" data-fauna="Juglar">
              <img alt="Juglar, Inspiración" decoding="async" loading="lazy" src="/assets/fauna-juglar.jpeg"/>
              <figcaption><strong>Juglar</strong><span>Inspiración</span></figcaption>
            </figure>
            <figure className="fauna-relation fauna-rel-b" data-fauna="Vesica Piscis">
              <img alt="Vesica Piscis, Proporción" decoding="async" loading="lazy" src="/assets/fauna-vesica-piscis.jpeg"/>
              <figcaption><strong>Vesica Piscis</strong><span>Proporción</span></figcaption>
            </figure>
            <figure className="fauna-relation fauna-rel-c" data-fauna="Lute">
              <img alt="Lute, Geometría viva" decoding="async" loading="lazy" src="/assets/fauna-lute.jpeg"/>
              <figcaption><strong>Lute</strong><span>Geometría viva</span></figcaption>
            </figure>
            <figure className="fauna-relation fauna-rel-d" data-fauna="Trilobites">
              <img alt="Trilobites, Memoria geológica" decoding="async" loading="lazy" src="/assets/fauna-trilobites.jpeg"/>
              <figcaption><strong>Trilobites</strong><span>Memoria geológica</span></figcaption>
            </figure>
            <figure className="fauna-relation fauna-rel-e" data-fauna="Musicalia">
              <img alt="Musicalia, Imaginación encarnada" decoding="async" loading="lazy" src="/assets/fauna-musicalia.png"/>
              <figcaption><strong>Musicalia</strong><span>Imaginación encarnada</span></figcaption>
            </figure>
            <span aria-hidden="true" className="relation-bridge bridge-a"></span>
            <span aria-hidden="true" className="relation-bridge bridge-b"></span>
            <span aria-hidden="true" className="relation-bridge bridge-c"></span>
            <span aria-hidden="true" className="relation-bridge bridge-d"></span>
            <span aria-hidden="true" className="relation-bridge bridge-e"></span>
            <div className="relation-core">
              <img alt="Gátople articula las relaciones de la Fauna Fractal" src="/assets/gatople-luminoso.png"/>
              <strong>Gátople · Articulación</strong>
            </div>
          </div>
          <div className="discovery-coda">
            <p>Fractal Music World no sustituye la educación musical: la expande hacia la geometría, el cuerpo, el símbolo, el movimiento y la creación.</p>
            <strong>Si esto es posible… ¿qué puedes hacer dentro de este universo?</strong>
          </div>
        </section>

        <div aria-hidden="true" className="movement-transition"><span></span></div>

        {/* Movimiento IV — La Participación */}
        <section aria-labelledby="home-005-title" className="section participation score-movement" data-home="HOME-005" data-movement="La Participación" id="participacion">
          <div className="section-heading center participation-heading">
            <p className="eyebrow">Movimiento IV · La Participación</p>
            <h2 id="home-005-title">No existe una sola manera de entrar a la música.</h2>
            <p>Elige la puerta que corresponde a tu forma actual de escuchar.</p>
          </div>
          <div className="participation-orbit">
            <button className="entry-gate entry-primary" onClick={() => onNavigate("gatople")}>
              <span className="entry-index">01</span>
              <strong>El Gátople Interactivo</strong>
              <small>Interactúa con las 12 cartas, el piano y el diapasón constitucional.</small>
              <em>Explora tu forma de escuchar</em>
            </button>
            <button className="entry-gate" onClick={() => onNavigate("gatople")}>
              <span className="entry-index">02</span>
              <strong>Gátople</strong>
              <small>Explora relaciones sonoras en un organismo visual.</small>
            </button>
            <a className="entry-gate" href="#sistema-fractal">
              <span className="entry-index">03</span>
              <strong>Sistema Fractal</strong>
              <small>Comprende la arquitectura pedagógica.</small>
            </a>
            <button className="entry-gate" onClick={() => onNavigate("chat")}>
              <span className="entry-index">04</span>
              <strong>Preguntar a los libros</strong>
              <small>Somete tus dudas del Sistema Fractal al asistente de citas.</small>
            </button>
            <button className="entry-gate" onClick={() => onNavigate("composer")}>
              <span className="entry-index">05</span>
              <strong>Componer</strong>
              <small>Genera arreglos y melodías áureas con la rueda.</small>
            </button>
            <button className="entry-gate" onClick={() => onNavigate("strudel")}>
              <span className="entry-index">06</span>
              <strong>Patrón en vivo</strong>
              <small>Live-coding interactivo con Strudel REPL.</small>
            </button>
          </div>
        </section>

        <div aria-hidden="true" className="movement-transition"><span></span></div>

        {/* Movimiento V — La Dirección */}
        <section aria-labelledby="home-006-title" className="section direction score-movement" data-home="HOME-006" data-movement="La Dirección" id="sistema-fractal">
          <div className="direction-copy">
            <p className="eyebrow">Movimiento V · La Dirección</p>
            <h2 id="home-006-title">No todos comienzan en el mismo lugar.</h2>
            <p>Cada puerta abre una trayectoria distinta. FMW no entrega una ruta única: organiza caminos para escuchar, comprender, crear y compartir.</p>
          </div>
          <div className="route-score">
            <article className="route-card">
              <figure className="route-guide" data-fauna="Musicalia">
                <img alt="" decoding="async" loading="lazy" src="/assets/fauna-musicalia.png"/>
                <figcaption>Musicalia · Reconoce lo que todavía no tiene nombre.</figcaption>
              </figure>
              <span>Escuchar</span>
              <h3>Reconoce</h3>
              <p>Tensiones, pulsos, colores, silencios y direcciones.</p>
            </article>
            <article className="route-card">
              <figure className="route-guide" data-fauna="Trilobites">
                <img alt="" decoding="async" loading="lazy" src="/assets/fauna-trilobites.jpeg"/>
                <figcaption>Trilobites · Relaciona el presente con la memoria.</figcaption>
              </figure>
              <span>Comprender</span>
              <h3>Relaciona</h3>
              <p>Sonido, geometría, memoria, símbolo y movimiento.</p>
            </article>
            <article className="route-card">
              <figure className="route-guide" data-fauna="Juglar">
                <img alt="" decoding="async" loading="lazy" src="/assets/fauna-juglar.jpeg"/>
                <figcaption>Juglar · Convierte la comprensión en movimiento.</figcaption>
              </figure>
              <span>Crear</span>
              <h3>Transforma</h3>
              <p>Conocimiento en composición, improvisación y experiencia.</p>
            </article>
          </div>
          <div className="direction-gatople" id="gatople">
            <div className="gatople-stage">
              <img alt="Gátople luminoso oficial" src="/assets/gatople-luminoso.png"/>
            </div>
            <div>
              <p className="eyebrow">Guía del territorio</p>
              <h3>El Gátople orienta sin imponer.</h3>
              <p>Funciona como astrolabio musical para recorrer notas, funciones, intervalos, rutas armónicas, símbolos y relaciones.</p>
              <button className="btn btn-primary" onClick={() => onNavigate("gatople")}>
                Abrir el Gátople interactivo
              </button>
            </div>
          </div>
        </section>

        <div aria-hidden="true" className="movement-transition"><span></span></div>

        {/* Movimiento VI — La Acción */}
        <section aria-labelledby="home-007-title" className="action score-movement" data-home="HOME-007" data-movement="La Acción" id="accion">
          <div className="section action-inner">
            <div className="action-conductor">
              <p className="eyebrow">Movimiento VI · La Acción</p>
              <h2 id="home-007-title">Descubre tu próximo movimiento.</h2>
              <p>No hay urgencia artificial. Hay una decisión que nace de lo que acabas de comprender.</p>
              <button className="btn btn-primary btn-large" onClick={() => onNavigate("gatople")}>
                Comenzar con la Rueda
              </button>
            </div>
            <div className="action-voices">
              <section className="action-voice" id="obras">
                <span>Obras</span>
                <h3>Lee y escucha</h3>
                <p>El lujo de la disonancia y La antena vegetal abren el universo editorial de FMW.</p>
                <button onClick={() => onNavigate("chat")} className="btn-link-action">Consultar los libros →</button>
              </section>
              <section className="action-voice" id="experiencias">
                <span>Experiencias</span>
                <h3>Lleva la música al cuerpo</h3>
                <p>Talleres, Suite Fractal y programas para instituciones, festivales y comunidades.</p>
                <a href="mailto:fractalmusicworld@gmail.com">Solicitar una experiencia →</a>
              </section>
              <section className="action-voice" id="personajes">
                <span>Símbolos vivos</span>
                <h3>Explora los personajes</h3>
                <p>Criaturas que encarnan principios, emotions, aprendizajes y rutas de escucha.</p>
                <button onClick={() => onNavigate("gatople")} className="btn-link-action">Entrar por Gátople →</button>
              </section>
              <section className="action-voice" id="comprar">
                <span>Componer</span>
                <h3>Crea con algoritmos fractales</h3>
                <p>Genera partituras, audios, y código Strudel interactivo.</p>
                <button onClick={() => onNavigate("composer")} className="btn-link-action">Abrir compositor →</button>
              </section>
            </div>
          </div>
        </section>

        <div aria-hidden="true" className="movement-transition"><span></span></div>

        {/* Movimiento VII — La Resonancia */}
        <section aria-labelledby="home-008-title" className="resonance score-movement" data-home="HOME-008" data-movement="La Resonancia" id="contacto">
          <div aria-hidden="true" className="resonance-halo"></div>
          <div className="resonance-content">
            <p className="eyebrow">Movimiento VII · La Resonancia</p>
            <figure aria-label="La Fauna Fractal permanece viva después del último movimiento" className="fauna-ensemble">
              <img alt="Musicalia, Gátople, Trilobites, Juglar y Lute reunidos en Fractal Music World" decoding="async" loading="lazy" src="/assets/fauna-ensemble.png"/>
              <figcaption>La historia continúa entre quienes la habitan.</figcaption>
            </figure>
            <h2 id="home-008-title">La música nunca fue solamente sonido.</h2>
            <p className="resonance-thanks">Gracias por escuchar.</p>
            <div className="resonance-links">
              <a href="mailto:fractalmusicworld@gmail.com">fractalmusicworld@gmail.com</a>
              <a href="https://wa.me/50663058177">WhatsApp Patricio</a>
              <a href="https://wa.me/50689246856">WhatsApp Katherina</a>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer resonance-footer">
        <p>© 2026 Patricio Torres Rivera · Fractal Music World™</p>
        <p>fractalmusicworld.com</p>
      </footer>
    </div>
  );
}
