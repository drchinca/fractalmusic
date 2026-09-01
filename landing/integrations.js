import { createHash } from "node:crypto";

const MAILCHIMP_API_KEY = process.env.MAILCHIMP_API_KEY || "";
const MAILCHIMP_SERVER_PREFIX = process.env.MAILCHIMP_SERVER_PREFIX || "";
const MAILCHIMP_AUDIENCE_ID = process.env.MAILCHIMP_AUDIENCE_ID || "";

export function mailchimpConfigured() {
  return Boolean(MAILCHIMP_API_KEY && MAILCHIMP_SERVER_PREFIX && MAILCHIMP_AUDIENCE_ID);
}

function subscriberHash(email) {
  return createHash("md5").update(email.trim().toLowerCase()).digest("hex");
}

function normalizeMergeFields(lead) {
  return {
    FNAME: lead.FNAME || "",
    ARQUETIPO: lead.ARQUETIPO || "",
    ARQSEC: lead.ARQSEC || "",
    SCORE1: String(lead.SCORE1 || ""),
    SCORE2: String(lead.SCORE2 || ""),
    MUESTRA: lead.MUESTRA || "",
    TESTDATE: lead.TESTDATE || "",
    COMPRA: lead.COMPRA || "NO",
    PRODUCTO: lead.PRODUCTO || "",
    FUENTE: lead.FUENTE || "THE_DISSONANCE_TEST",
    CONSENT: lead.CONSENT || ""
  };
}

async function mailchimpRequest(path, init = {}) {
  if (!mailchimpConfigured()) {
    throw Object.assign(new Error("Mailchimp no configurado"), { code: "MAILCHIMP_NOT_CONFIGURED" });
  }
  const response = await fetch(`https://${MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0${path}`, {
    ...init,
    headers: {
      authorization: `Basic ${Buffer.from(`fmw:${MAILCHIMP_API_KEY}`).toString("base64")}`,
      "content-type": "application/json",
      ...(init.headers || {})
    }
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.detail || payload.title || `Mailchimp respondió ${response.status}`);
    error.code = "MAILCHIMP_API_ERROR";
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

export async function syncLeadToMailchimp(lead) {
  const hash = subscriberHash(lead.EMAIL);
  const tags = [...new Set(Array.isArray(lead.tags) ? lead.tags.filter(Boolean) : [])];
  await mailchimpRequest(`/lists/${MAILCHIMP_AUDIENCE_ID}/members/${hash}`, {
    method: "PUT",
    body: JSON.stringify({
      email_address: lead.EMAIL,
      status_if_new: "subscribed",
      merge_fields: normalizeMergeFields(lead)
    })
  });
  if (tags.length) {
    await mailchimpRequest(`/lists/${MAILCHIMP_AUDIENCE_ID}/members/${hash}/tags`, {
      method: "POST",
      body: JSON.stringify({ tags: tags.map((name) => ({ name, status: "active" })) })
    });
  }
  return { synced: true, subscriberHash: hash, tags };
}

export async function markPurchaseInMailchimp(lead) {
  const purchaseTags = [...new Set([
    ...(Array.isArray(lead.tags) ? lead.tags : []),
    "COMPRADOR_FMW",
    "INICIADO_FMW"
  ].filter((tag) => tag !== "SECUENCIA_DISONANTE"))];
  return syncLeadToMailchimp({ ...lead, COMPRA: "SÍ", tags: purchaseTags });
}
