try {
  if (typeof process.loadEnvFile === "function") process.loadEnvFile();
} catch {}

const EMAIL_API_KEY = process.env.EMAIL_API_KEY || "";
const EMAIL_FROM = process.env.EMAIL_FROM || "Fractal Music World <noreply@fractalmusicworld.com>";
const EMAIL_REPLY_TO = process.env.EMAIL_REPLY_TO || "";
const EMAIL_PROVIDER = (process.env.EMAIL_PROVIDER || "resend").toLowerCase();

export function transactionalEmailConfigured() {
  return Boolean(EMAIL_API_KEY && EMAIL_FROM && EMAIL_PROVIDER === "resend");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function shell({ eyebrow, title, intro, buttonLabel, buttonUrl, footer }) {
  const safeUrl = escapeHtml(buttonUrl);
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
  <body style="margin:0;background:#030303;color:#f6f0df;font-family:Inter,Arial,sans-serif">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#030303;padding:32px 16px"><tr><td align="center">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;border:1px solid #493a1b;border-radius:18px;background:#0b0a08;overflow:hidden">
        <tr><td style="padding:34px">
          <div style="font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#ffda68">${escapeHtml(eyebrow)}</div>
          <h1 style="font-family:Georgia,serif;font-size:34px;line-height:1.15;margin:14px 0;color:#ffda68">${escapeHtml(title)}</h1>
          <p style="font-size:17px;line-height:1.7;color:#ede5d1">${escapeHtml(intro)}</p>
          <p style="margin:30px 0"><a href="${safeUrl}" style="display:inline-block;background:#e4aa24;color:#080704;text-decoration:none;font-weight:700;padding:14px 22px;border-radius:999px">${escapeHtml(buttonLabel)}</a></p>
          <p style="font-size:13px;line-height:1.6;color:#a99d85">${escapeHtml(footer)}</p>
        </td></tr>
      </table>
    </td></tr></table>
  </body></html>`;
}

export function purchaseEmail({ name, product, downloadUrl, receiptUrl, expiresAt }) {
  const displayName = name || "Disonante";
  const expiry = new Date(expiresAt).toLocaleString("es-CR", { dateStyle: "long", timeStyle: "short" });
  return {
    subject: "Tu compra en Fractal Music World está confirmada",
    text: [
      `Hola ${displayName}.`, "", `Tu compra de ${product} fue confirmada.`,
      `Descarga segura: ${downloadUrl}`, `Comprobante: ${receiptUrl}`,
      `El enlace vence el ${expiry}.`, "", "Fractal Music World"
    ].join("\n"),
    html: shell({
      eyebrow: "Compra confirmada", title: `Gracias, ${displayName}`,
      intro: `Tu acceso a ${product} ya está disponible. El enlace privado vence el ${expiry}.`,
      buttonLabel: "Descargar obra", buttonUrl: downloadUrl,
      footer: `Conserva este correo. Tu comprobante está disponible en ${receiptUrl}`
    })
  };
}

export function recoveryEmail({ name, product, downloadUrl, expiresAt }) {
  const displayName = name || "Disonante";
  const expiry = new Date(expiresAt).toLocaleString("es-CR", { dateStyle: "long", timeStyle: "short" });
  return {
    subject: "Nuevo enlace de descarga — Fractal Music World",
    text: [`Hola ${displayName}.`, "", `Se generó un nuevo enlace para ${product}.`, downloadUrl, `Vence el ${expiry}.`, "", "Fractal Music World"].join("\n"),
    html: shell({
      eyebrow: "Acceso renovado", title: "Tu nuevo enlace está listo",
      intro: `Renovamos el acceso privado a ${product}. Este enlace vence el ${expiry}.`,
      buttonLabel: "Abrir descarga", buttonUrl: downloadUrl,
      footer: "La renovación invalida automáticamente el enlace anterior."
    })
  };
}

export async function sendTransactionalEmail({ to, subject, text, html }) {
  if (!transactionalEmailConfigured()) {
    throw Object.assign(new Error("Correo transaccional no configurado"), { code: "EMAIL_NOT_CONFIGURED" });
  }
  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { authorization: `Bearer ${EMAIL_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({ from: EMAIL_FROM, to: [to], subject, text, html, ...(EMAIL_REPLY_TO ? { reply_to: EMAIL_REPLY_TO } : {}) })
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.message || `Proveedor de correo respondió ${response.status}`);
    error.code = "EMAIL_API_ERROR";
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return { sent: true, provider: "resend", messageId: payload.id || "" };
}
