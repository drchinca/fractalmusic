// Pseudo "under construction" gate — keeps casual visitors out while the site
// is in development. This is NOT real security: it runs entirely client-side on
// a static site, so anyone who reads the source can bypass it. It only stops
// the page from being browsable by the public during the build phase.
//
// To remove the gate entirely: delete this file and the <script src="gate.js">
// line from index.html, gatople.html, and compose.html.
(function () {
  "use strict";

  const UNLOCK_KEY = "fmw_gate_ok";
  const PASSWORD = "fractalworldlove";

  // Already unlocked this browser — let the page through untouched.
  try {
    if (localStorage.getItem(UNLOCK_KEY) === "1") return;
  } catch (_) {
    // localStorage blocked (private mode / cookies off) — gate still works,
    // it just won't persist across reloads.
  }

  // Lock scrolling on the document while the gate is up.
  document.documentElement.style.overflow = "hidden";

  const style = document.createElement("style");
  style.textContent = `
    #fmw-gate {
      position: fixed;
      inset: 0;
      z-index: 99999;
      display: grid;
      place-items: center;
      padding: 24px;
      color: #f4efe4;
      font-family: "Montserrat", system-ui, sans-serif;
      background:
        radial-gradient(circle at 82% 14%, rgba(111,24,56,.42), transparent 30%),
        radial-gradient(circle at 14% 30%, rgba(217,180,91,.14), transparent 32%),
        linear-gradient(180deg, #080a10 0%, #0b0d15 52%, #090b12 100%);
    }
    #fmw-gate .fmw-box {
      width: min(440px, 100%);
      text-align: center;
    }
    #fmw-gate .fmw-mark {
      width: 64px;
      height: 64px;
      margin: 0 auto 26px;
      border-radius: 50%;
      border: 1px solid #d9b45b;
      position: relative;
      box-shadow: inset 0 0 28px rgba(217,180,91,.16);
    }
    #fmw-gate .fmw-mark::before,
    #fmw-gate .fmw-mark::after {
      content: "";
      position: absolute;
      top: 50%;
      left: 50%;
      background: #d9b45b;
      opacity: .85;
    }
    #fmw-gate .fmw-mark::before {
      width: 30px; height: 1px;
      transform: translate(-50%, -50%) rotate(30deg);
    }
    #fmw-gate .fmw-mark::after {
      width: 1px; height: 30px;
      transform: translate(-50%, -50%) rotate(30deg);
    }
    #fmw-gate .fmw-eyebrow {
      color: #f1d891;
      font-size: .72rem;
      letter-spacing: .26em;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 16px;
    }
    #fmw-gate h1 {
      margin: 0 0 12px;
      font-size: clamp(1.5rem, 5vw, 2.1rem);
      line-height: 1.12;
      letter-spacing: -.02em;
      font-weight: 800;
    }
    #fmw-gate p {
      margin: 0 0 28px;
      color: #aaa9b3;
      font-size: .92rem;
      line-height: 1.5;
    }
    #fmw-gate form {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    #fmw-gate input {
      width: 100%;
      min-height: 52px;
      padding: 0 18px;
      border-radius: 999px;
      border: 1px solid rgba(217,180,91,.4);
      background: rgba(255,255,255,.05);
      color: #f4efe4;
      font: inherit;
      font-size: .95rem;
      text-align: center;
      letter-spacing: .04em;
      outline: none;
      transition: border-color .2s ease, background .2s ease;
    }
    #fmw-gate input:focus {
      border-color: #d9b45b;
      background: rgba(217,180,91,.08);
    }
    #fmw-gate input::placeholder { color: rgba(170,169,179,.7); }
    #fmw-gate button {
      min-height: 52px;
      border: 0;
      border-radius: 999px;
      cursor: pointer;
      font: inherit;
      font-weight: 700;
      font-size: .92rem;
      color: #17120a;
      background: linear-gradient(135deg, #f1d891, #d9b45b);
      box-shadow: 0 14px 32px rgba(217,180,91,.18);
      transition: transform .2s ease;
    }
    #fmw-gate button:hover { transform: translateY(-2px); }
    #fmw-gate .fmw-error {
      min-height: 18px;
      margin: 4px 0 0;
      color: #e8a0a0;
      font-size: .82rem;
      letter-spacing: .02em;
    }
    @media (prefers-reduced-motion: reduce) {
      #fmw-gate * { transition: none !important; }
    }
  `;
  document.documentElement.appendChild(style);

  const overlay = document.createElement("div");
  overlay.id = "fmw-gate";
  overlay.innerHTML = `
    <div class="fmw-box">
      <div class="fmw-mark" aria-hidden="true"></div>
      <div class="fmw-eyebrow">Fractal Music World</div>
      <h1>Construyendo tu músico ancestral</h1>
      <p>Este universo está en construcción. Ingresa la clave para continuar.</p>
      <form id="fmw-gate-form" autocomplete="off">
        <input
          id="fmw-gate-pass"
          type="password"
          name="adminpass"
          placeholder="adminpass"
          aria-label="Clave de acceso"
          autocomplete="off"
          autofocus
        />
        <button type="submit">Entrar</button>
        <p class="fmw-error" id="fmw-gate-error" role="alert"></p>
      </form>
    </div>
  `;
  // Append to <html> so the gate exists even before <body> is parsed.
  document.documentElement.appendChild(overlay);

  const form = overlay.querySelector("#fmw-gate-form");
  const input = overlay.querySelector("#fmw-gate-pass");
  const error = overlay.querySelector("#fmw-gate-error");

  input.focus();

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (input.value === PASSWORD) {
      try {
        localStorage.setItem(UNLOCK_KEY, "1");
      } catch (_) {
        // Persistence unavailable — unlock for this view only.
      }
      document.documentElement.style.overflow = "";
      overlay.remove();
      style.remove();
    } else {
      error.textContent = "Clave incorrecta. Intenta de nuevo.";
      input.value = "";
      input.focus();
    }
  });
})();
