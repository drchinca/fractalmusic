try {
  if (typeof process.loadEnvFile === "function") process.loadEnvFile();
} catch {}

import { createServer } from "node:http";
import { readFile, writeFile, mkdir, rename, stat } from "node:fs/promises";
import { basename, extname, join, normalize, resolve } from "node:path";
import { createHmac, randomUUID, timingSafeEqual } from "node:crypto";
import { mailchimpConfigured, markPurchaseInMailchimp, syncLeadToMailchimp } from "./integrations.js";
import { purchaseEmail, recoveryEmail, sendTransactionalEmail, transactionalEmailConfigured } from "./email.js";
import { log } from "./logger.js";

const ROOT = resolve(process.cwd());
const DATA_DIR = process.env.VERCEL ? "/tmp/fmw-data" : join(ROOT, "data");
const DATA_FILE = join(DATA_DIR, "store.json");
const PORT = Number(process.env.PORT || 3000);
const ADMIN_TOKEN = process.env.FMW_ADMIN_TOKEN || "";
const COMPRACLICK_CHECKOUT_URL = process.env.COMPRACLICK_CHECKOUT_URL || "";
const COMPRACLICK_WEBHOOK_SECRET = process.env.COMPRACLICK_WEBHOOK_SECRET || "";
const PUBLIC_BASE_URL = process.env.PUBLIC_BASE_URL || `http://localhost:${PORT}`;
const MAX_BODY_BYTES = 256_000;
const PRODUCT_FILE = process.env.FMW_PRODUCT_FILE ? resolve(process.env.FMW_PRODUCT_FILE) : "";
const DELIVERY_TOKEN_HOURS = Number(process.env.FMW_DELIVERY_TOKEN_HOURS || 72);
const RECOVERY_MAX_PER_HOUR = Number(process.env.FMW_RECOVERY_MAX_PER_HOUR || 5);
const TRUST_PROXY = process.env.FMW_TRUST_PROXY === "true";
const rateBuckets = new Map();

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
  ".svg": "image/svg+xml", ".pdf": "application/pdf"
};

const emptyStore = () => ({
  version: 5, leads: [], assessments: [], events: [], transactions: [], integrationOutbox: [], emailDeliveries: [],
  updatedAt: new Date().toISOString()
});

async function ensureStore() {
  await mkdir(DATA_DIR, { recursive: true });
  try { await stat(DATA_FILE); } catch { await atomicWrite(emptyStore()); }
}

async function readStore() {
  await ensureStore();
  const parsed = JSON.parse(await readFile(DATA_FILE, "utf8"));
  return { ...emptyStore(), ...parsed, assessments: Array.isArray(parsed.assessments) ? parsed.assessments : [], emailDeliveries: Array.isArray(parsed.emailDeliveries) ? parsed.emailDeliveries : [], version: 5 };
}

async function atomicWrite(store) {
  store.updatedAt = new Date().toISOString();
  const temporary = `${DATA_FILE}.${process.pid}.tmp`;
  await writeFile(temporary, JSON.stringify(store, null, 2), "utf8");
  await rename(temporary, DATA_FILE);
}

function securityHeaders() {
  return {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "DENY",
    "permissions-policy": "camera=(), microphone=(), geolocation=()",
    "content-security-policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data:; connect-src 'self'; font-src 'self' https://fonts.gstatic.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
  };
}

function json(response, status, payload) {
  response.writeHead(status, {
    "content-type": "application/json; charset=utf-8", "cache-control": "no-store",
    ...securityHeaders()
  });
  response.end(JSON.stringify(payload));
}

function secureEqual(left, right) {
  const a = Buffer.from(left || "");
  const b = Buffer.from(right || "");
  return a.length === b.length && timingSafeEqual(a, b);
}

function isAdmin(request) {
  if (!ADMIN_TOKEN) return false;
  return secureEqual(request.headers.authorization?.replace(/^Bearer\s+/i, "") || "", ADMIN_TOKEN);
}

async function readRawBody(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw Object.assign(new Error("Payload demasiado grande"), { status: 413 });
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}

function parseJsonBuffer(raw) {
  if (!raw.length) return {};
  try { return JSON.parse(raw.toString("utf8")); }
  catch { throw Object.assign(new Error("JSON inválido"), { status: 400 }); }
}

async function parseBody(request) { return parseJsonBuffer(await readRawBody(request)); }


function clientIp(request) {
  if (TRUST_PROXY) return String(request.headers["x-forwarded-for"] || "").split(",")[0].trim() || request.socket.remoteAddress || "unknown";
  return request.socket.remoteAddress || "unknown";
}

function enforceRateLimit(request, scope, limit, windowMs = 3600_000) {
  const key = `${scope}:${clientIp(request)}`;
  const now = Date.now();
  const bucket = rateBuckets.get(key);
  if (!bucket || bucket.resetAt <= now) {
    rateBuckets.set(key, { count: 1, resetAt: now + windowMs });
    return;
  }
  bucket.count += 1;
  if (bucket.count > limit) {
    const error = new Error("Demasiadas solicitudes. Intenta nuevamente más tarde.");
    error.status = 429;
    throw error;
  }
}

function publicDeliveryUrls(transaction) {
  return {
    downloadUrl: `${PUBLIC_BASE_URL}/api/download/${transaction.deliveryToken}`,
    receiptUrl: `${PUBLIC_BASE_URL}/api/receipt/${transaction.deliveryToken}`
  };
}

function queueEmail(store, type, transaction, error) {
  addOutbox(store, type, { transactionId: transaction.id }, error);
}

async function sendPurchaseDelivery(store, transaction, lead) {
  const urls = publicDeliveryUrls(transaction);
  const content = purchaseEmail({ name: lead?.FNAME, product: transaction.product, ...urls, expiresAt: transaction.deliveryExpiresAt });
  const result = await sendTransactionalEmail({ to: transaction.email, ...content });
  store.emailDeliveries.push({ id: randomUUID(), type: "purchase", transactionId: transaction.id, email: transaction.email, providerMessageId: result.messageId, sentAt: new Date().toISOString() });
  transaction.deliveryEmailSentAt = new Date().toISOString();
  return result;
}

async function sendRecoveryDelivery(store, transaction, lead) {
  const { downloadUrl } = publicDeliveryUrls(transaction);
  const content = recoveryEmail({ name: lead?.FNAME, product: transaction.product, downloadUrl, expiresAt: transaction.deliveryExpiresAt });
  const result = await sendTransactionalEmail({ to: transaction.email, ...content });
  store.emailDeliveries.push({ id: randomUUID(), type: "recovery", transactionId: transaction.id, email: transaction.email, providerMessageId: result.messageId, sentAt: new Date().toISOString() });
  transaction.recoveryEmailSentAt = new Date().toISOString();
  return result;
}

function validateLead(input) {
  const email = String(input.EMAIL || "").trim().toLowerCase();
  const name = String(input.FNAME || "").trim();
  if (!name || name.length > 120) throw Object.assign(new Error("Nombre inválido"), { status: 422 });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
    throw Object.assign(new Error("Correo inválido"), { status: 422 });
  }
  if (!input.CONSENT) throw Object.assign(new Error("Consentimiento obligatorio"), { status: 422 });
  if (!input.ARQUETIPO || !input.ARQSEC) throw Object.assign(new Error("Resultado incompleto"), { status: 422 });
  return {
    ...input, EMAIL: email, FNAME: name, COMPRA: input.COMPRA === "SÍ" ? "SÍ" : "NO",
    FUENTE: String(input.FUENTE || "THE_DISSONANCE_TEST"),
    tags: [...new Set(Array.isArray(input.tags) ? input.tags.map(String) : [])],
    updatedAt: new Date().toISOString()
  };
}

function sanitizeEvent(input) {
  const allowed = ["test_started", "test_answer", "test_completed", "scores_calculated", "result_generated",
    "result_viewed", "lead_captured", "sample_sent", "sample_downloaded", "email_clicked",
    "checkout_started", "purchase_completed", "postpurchase_started", "history_viewed"];
  const name = String(input.name || "");
  if (!allowed.includes(name)) throw Object.assign(new Error("Evento no permitido"), { status: 422 });
  return { id: randomUUID(), name, detail: typeof input.detail === "object" && input.detail ? input.detail : {}, createdAt: new Date().toISOString() };
}

function addOutbox(store, type, payload, error) {
  store.integrationOutbox.push({
    id: randomUUID(), type, payload, attempts: 1, status: "pending",
    lastError: error?.message || "Error desconocido", createdAt: new Date().toISOString(), updatedAt: new Date().toISOString()
  });
}

async function syncLeadOrQueue(store, lead) {
  if (!mailchimpConfigured()) {
    addOutbox(store, "mailchimp.lead_upsert", { leadId: lead.id }, new Error("Mailchimp no configurado"));
    return { status: "queued" };
  }
  try {
    await syncLeadToMailchimp(lead);
    return { status: "synced" };
  } catch (error) {
    addOutbox(store, "mailchimp.lead_upsert", { leadId: lead.id }, error);
    return { status: "queued" };
  }
}

function validateCheckout(input) {
  const email = String(input.email || "").trim().toLowerCase();
  const product = String(input.product || "EL_LUJO_DE_LA_DISONANCIA_DIGITAL").trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw Object.assign(new Error("Correo inválido"), { status: 422 });
  if (!/^[A-Z0-9_-]{3,80}$/.test(product)) throw Object.assign(new Error("Producto inválido"), { status: 422 });
  return { email, product };
}

function checkoutState(transaction) {
  if (!COMPRACLICK_WEBHOOK_SECRET) return "";
  return createHmac("sha256", COMPRACLICK_WEBHOOK_SECRET)
    .update(`${transaction.id}:${transaction.email}:${transaction.product}`)
    .digest("hex");
}

function verifyWebhook(raw, signature) {
  if (!COMPRACLICK_WEBHOOK_SECRET || !signature) return false;
  const expected = createHmac("sha256", COMPRACLICK_WEBHOOK_SECRET).update(raw).digest("hex");
  return secureEqual(expected, signature.replace(/^sha256=/i, ""));
}

async function handleApi(request, response, url) {
  if (request.method === "GET" && url.pathname === "/api/health") {
    return json(response, 200, { ok: true, service: "fmw-web", version: "0.8.0", integrations: {
      mailchimp: mailchimpConfigured(), transactionalEmail: transactionalEmailConfigured(), compraClickCheckout: Boolean(COMPRACLICK_CHECKOUT_URL), compraClickWebhook: Boolean(COMPRACLICK_WEBHOOK_SECRET)
    }});
  }

  if (request.method === "POST" && url.pathname === "/api/leads") {
    const lead = validateLead(await parseBody(request));
    const store = await readStore();
    const index = store.leads.findIndex((item) => item.EMAIL === lead.EMAIL);
    const accessToken = index >= 0 && store.leads[index].accessToken ? store.leads[index].accessToken : randomUUID();
    const stored = index >= 0
      ? { ...store.leads[index], ...lead, id: store.leads[index].id, accessToken }
      : { ...lead, id: randomUUID(), accessToken, createdAt: new Date().toISOString() };
    if (index >= 0) store.leads[index] = stored; else store.leads.push(stored);

    const assessmentId = String(lead.result_id || randomUUID());
    const existingAssessment = store.assessments.findIndex((item) => item.id === assessmentId);
    const assessment = {
      id: assessmentId, leadId: stored.id, EMAIL: stored.EMAIL, FNAME: stored.FNAME,
      ARQUETIPO: stored.ARQUETIPO, ARQSEC: stored.ARQSEC, SCORE1: stored.SCORE1, SCORE2: stored.SCORE2,
      TESTDATE: stored.TESTDATE, MUESTRA: stored.MUESTRA, answers: stored.answers || {},
      raw_scores: stored.raw_scores || {}, normalized_scores: stored.normalized_scores || {},
      result_type: stored.result_type || "ranked", createdAt: new Date().toISOString()
    };
    if (existingAssessment >= 0) store.assessments[existingAssessment] = assessment;
    else store.assessments.push(assessment);

    const mailchimp = await syncLeadOrQueue(store, stored);
    await atomicWrite(store);
    return json(response, index >= 0 ? 200 : 201, {
      ok: true, leadId: stored.id, assessmentId, accessToken, updated: index >= 0, mailchimp: mailchimp.status
    });
  }


  if (request.method === "POST" && url.pathname === "/api/history") {
    const input = await parseBody(request);
    const email = String(input.email || "").trim().toLowerCase();
    const token = String(input.token || "");
    const store = await readStore();
    const lead = store.leads.find((item) => item.EMAIL === email);
    if (!lead || !secureEqual(lead.accessToken || "", token)) {
      return json(response, 401, { ok: false, error: "Acceso al historial no autorizado" });
    }
    const assessments = store.assessments
      .filter((item) => item.leadId === lead.id)
      .sort((a, b) => String(b.TESTDATE).localeCompare(String(a.TESTDATE)));
    const latest = assessments[0];
    const previous = assessments[1];
    let evolution = { type: "initial", summary: "Este es tu primer registro cognitivo. La próxima medición permitirá observar estabilidad, desplazamiento o transformación." };
    if (latest && previous) {
      if (latest.ARQUETIPO === previous.ARQUETIPO && latest.ARQSEC === previous.ARQSEC) {
        evolution = { type: "stable", summary: `Tu configuración permanece estable en ${latest.ARQUETIPO}, con ${latest.ARQSEC} como fuerza secundaria.` };
      } else if (latest.ARQUETIPO === previous.ARQUETIPO) {
        evolution = { type: "secondary_shift", summary: `Tu núcleo dominante permanece en ${latest.ARQUETIPO}, pero la fuerza secundaria cambió de ${previous.ARQSEC} a ${latest.ARQSEC}.` };
      } else {
        evolution = { type: "dominant_shift", summary: `Tu perfil dominante se desplazó de ${previous.ARQUETIPO} a ${latest.ARQUETIPO}. El sistema registra una transformación de estado, no una identidad fija.` };
      }
    }
    return json(response, 200, { ok: true, lead: { FNAME: lead.FNAME, EMAIL: lead.EMAIL }, assessments, evolution });
  }

  if (request.method === "POST" && url.pathname === "/api/events") {
    const event = sanitizeEvent(await parseBody(request));
    const store = await readStore();
    store.events.push(event);
    if (store.events.length > 20_000) store.events.splice(0, store.events.length - 20_000);
    await atomicWrite(store);
    return json(response, 202, { ok: true, eventId: event.id });
  }

  if (request.method === "POST" && url.pathname === "/api/checkout/start") {
    if (!COMPRACLICK_CHECKOUT_URL) return json(response, 503, { ok: false, error: "CompraClick aún no está configurado" });
    const input = validateCheckout(await parseBody(request));
    const store = await readStore();
    const transaction = { id: randomUUID(), provider: "BAC_COMPRACLICK", status: "pending", ...input, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
    transaction.state = checkoutState(transaction);
    transaction.deliveryToken = randomUUID();
    transaction.deliveryExpiresAt = new Date(Date.now() + DELIVERY_TOKEN_HOURS * 3600_000).toISOString();
    store.transactions.push(transaction);
    store.events.push({ id: randomUUID(), name: "checkout_started", detail: { transaction_id: transaction.id, product: transaction.product }, createdAt: new Date().toISOString() });
    await atomicWrite(store);
    const checkout = new URL(COMPRACLICK_CHECKOUT_URL);
    checkout.searchParams.set("reference", transaction.id);
    checkout.searchParams.set("state", transaction.state);
    checkout.searchParams.set("email", transaction.email);
    checkout.searchParams.set("product", transaction.product);
    checkout.searchParams.set("return_url", `${PUBLIC_BASE_URL}/confirmacion.html?reference=${transaction.id}&state=${transaction.state}`);
    return json(response, 201, { ok: true, transactionId: transaction.id, checkoutUrl: checkout.toString() });
  }

  if (request.method === "POST" && url.pathname === "/api/checkout/status") {
    const input = await parseBody(request);
    const reference = String(input.reference || "");
    const state = String(input.state || "");
    const store = await readStore();
    const transaction = store.transactions.find((item) => item.id === reference);
    if (!transaction || !secureEqual(transaction.state || "", state)) {
      return json(response, 401, { ok: false, error: "Referencia de compra inválida" });
    }
    const paid = transaction.status === "paid";
    const deliveryAvailable = paid && Boolean(PRODUCT_FILE);
    return json(response, 200, {
      ok: true,
      transaction: {
        reference: transaction.id, product: transaction.product, email: transaction.email,
        status: transaction.status, paidAt: transaction.paidAt || null
      },
      delivery: {
        available: deliveryAvailable,
        downloadUrl: deliveryAvailable ? `/api/download/${transaction.deliveryToken}` : null,
        receiptUrl: paid ? `/api/receipt/${transaction.deliveryToken}` : null,
        expiresAt: transaction.deliveryExpiresAt
      }
    });
  }

  if (request.method === "GET" && url.pathname.startsWith("/api/download/")) {
    const token = decodeURIComponent(url.pathname.slice("/api/download/".length));
    const store = await readStore();
    const transaction = store.transactions.find((item) => item.deliveryToken === token && item.status === "paid");
    if (!transaction) return json(response, 404, { ok: false, error: "Entrega no encontrada" });
    if (Date.parse(transaction.deliveryExpiresAt || 0) < Date.now()) return json(response, 410, { ok: false, error: "El enlace de entrega expiró" });
    if (!PRODUCT_FILE) return json(response, 503, { ok: false, error: "El activo digital definitivo aún no está configurado" });
    try {
      const content = await readFile(PRODUCT_FILE);
      response.writeHead(200, {
        "content-type": MIME_TYPES[extname(PRODUCT_FILE).toLowerCase()] || "application/octet-stream",
        "content-disposition": `attachment; filename="${basename(PRODUCT_FILE).replace(/["\r\n]/g, "_")}"`,
        "cache-control": "private, no-store", "x-content-type-options": "nosniff"
      });
      response.end(content);
    } catch (error) {
      if (error.code === "ENOENT") return json(response, 503, { ok: false, error: "El archivo digital configurado no existe" });
      throw error;
    }
    transaction.downloadedAt = new Date().toISOString();
    transaction.updatedAt = transaction.downloadedAt;
    store.events.push({ id: randomUUID(), name: "sample_downloaded", detail: { transaction_id: transaction.id, kind: "paid_product" }, createdAt: transaction.downloadedAt });
    await atomicWrite(store);
    return;
  }

  if (request.method === "GET" && url.pathname.startsWith("/api/receipt/")) {
    const token = decodeURIComponent(url.pathname.slice("/api/receipt/".length));
    const store = await readStore();
    const transaction = store.transactions.find((item) => item.deliveryToken === token && item.status === "paid");
    if (!transaction) return json(response, 404, { ok: false, error: "Comprobante no encontrado" });
    const receipt = [
      "FRACTAL MUSIC WORLD", "Comprobante digital de compra", "",
      `Referencia: ${transaction.id}`, `Producto: ${transaction.product}`,
      `Correo: ${transaction.email}`, `Estado: PAGADO`, `Fecha: ${transaction.paidAt || ""}`,
      `Proveedor: ${transaction.provider}`, `ID proveedor: ${transaction.providerTransactionId || "No informado"}`
    ].join("\n");
    response.writeHead(200, { "content-type": "text/plain; charset=utf-8", "content-disposition": `attachment; filename="FMW-${transaction.id}.txt"`, "cache-control": "private, no-store" });
    response.end(receipt);
    return;
  }

  if (request.method === "POST" && url.pathname === "/api/delivery/recover") {
    enforceRateLimit(request, "delivery-recovery", RECOVERY_MAX_PER_HOUR);
    const input = await parseBody(request);
    const email = String(input.email || "").trim().toLowerCase();
    const reference = String(input.reference || "").trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !reference) {
      return json(response, 202, { ok: true });
    }
    const store = await readStore();
    const transaction = store.transactions.find((item) => item.id === reference && item.email === email && item.status === "paid");
    if (transaction) {
      transaction.deliveryToken = randomUUID();
      transaction.deliveryExpiresAt = new Date(Date.now() + DELIVERY_TOKEN_HOURS * 3600_000).toISOString();
      transaction.updatedAt = new Date().toISOString();
      transaction.recoveryCount = Number(transaction.recoveryCount || 0) + 1;
      const lead = store.leads.find((item) => item.EMAIL === transaction.email);
      try { await sendRecoveryDelivery(store, transaction, lead); }
      catch (error) { queueEmail(store, "email.delivery_recovery", transaction, error); }
      await atomicWrite(store);
    }
    return json(response, 202, { ok: true });
  }

  if (request.method === "POST" && url.pathname === "/api/webhooks/compraclick") {
    const raw = await readRawBody(request);
    const signature = String(request.headers["x-fmw-signature"] || request.headers["x-compraclick-signature"] || "");
    if (!verifyWebhook(raw, signature)) return json(response, 401, { ok: false, error: "Firma de webhook inválida" });
    const payload = parseJsonBuffer(raw);
    const reference = String(payload.reference || payload.transaction_id || "");
    const paid = ["paid", "approved", "completed", "success"].includes(String(payload.status || "").toLowerCase());
    if (!reference || !paid) return json(response, 202, { ok: true, ignored: true });
    const store = await readStore();
    const transaction = store.transactions.find((item) => item.id === reference);
    if (!transaction) return json(response, 404, { ok: false, error: "Transacción desconocida" });
    if (transaction.status === "paid") return json(response, 200, { ok: true, duplicate: true });
    transaction.status = "paid";
    transaction.providerTransactionId = String(payload.provider_transaction_id || payload.id || "");
    transaction.paidAt = new Date().toISOString();
    transaction.updatedAt = transaction.paidAt;
    const lead = store.leads.find((item) => item.EMAIL === transaction.email);
    if (lead) {
      lead.COMPRA = "SÍ";
      lead.PRODUCTO = transaction.product;
      lead.tags = [...new Set([...(lead.tags || []).filter((tag) => tag !== "SECUENCIA_DISONANTE"), "COMPRADOR_FMW", "INICIADO_FMW"])];
      lead.updatedAt = transaction.paidAt;
      try { await markPurchaseInMailchimp(lead); }
      catch (error) { addOutbox(store, "mailchimp.purchase_update", { leadId: lead.id, transactionId: transaction.id }, error); }
    }
    try { await sendPurchaseDelivery(store, transaction, lead); }
    catch (error) { queueEmail(store, "email.purchase_confirmation", transaction, error); }
    store.events.push({ id: randomUUID(), name: "purchase_completed", detail: { transaction_id: transaction.id, product: transaction.product }, createdAt: transaction.paidAt });
    store.events.push({ id: randomUUID(), name: "postpurchase_started", detail: { transaction_id: transaction.id }, createdAt: transaction.paidAt });
    await atomicWrite(store);
    return json(response, 200, { ok: true });
  }

  if (request.method === "POST" && url.pathname === "/api/admin/retry-integrations") {
    if (!isAdmin(request)) return json(response, 401, { ok: false, error: "No autorizado" });
    const store = await readStore();
    let synced = 0;
    for (const job of store.integrationOutbox.filter((item) => item.status === "pending")) {
      const transaction = job.payload.transactionId ? store.transactions.find((item) => item.id === job.payload.transactionId) : null;
      const lead = job.payload.leadId
        ? store.leads.find((item) => item.id === job.payload.leadId)
        : (transaction ? store.leads.find((item) => item.EMAIL === transaction.email) : null);
      if (job.payload.leadId && !lead) { job.status = "failed"; job.lastError = "Lead no encontrado"; continue; }
      try {
        if (job.type === "mailchimp.purchase_update") await markPurchaseInMailchimp(lead);
        else if (job.type === "mailchimp.lead_upsert") await syncLeadToMailchimp(lead);
        else {
          if (!transaction) throw new Error("Transacción no encontrada");
          if (job.type === "email.purchase_confirmation") await sendPurchaseDelivery(store, transaction, lead);
          else if (job.type === "email.delivery_recovery") await sendRecoveryDelivery(store, transaction, lead);
          else throw new Error("Tipo de integración desconocido");
        }
        job.status = "completed"; job.completedAt = new Date().toISOString(); synced += 1;
      } catch (error) {
        job.attempts += 1; job.lastError = error.message; job.updatedAt = new Date().toISOString();
      }
    }
    await atomicWrite(store);
    return json(response, 200, { ok: true, synced, pending: store.integrationOutbox.filter((item) => item.status === "pending").length });
  }

  if (request.method === "GET" && url.pathname === "/api/admin/export.csv") {
    if (!isAdmin(request)) return json(response, 401, { ok: false, error: "No autorizado" });
    const store = await readStore();
    const columns = ["updatedAt", "FNAME", "EMAIL", "ARQUETIPO", "ARQSEC", "SCORE1", "SCORE2", "COMPRA", "PRODUCTO", "FUENTE"];
    const quote = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;
    const csv = [columns.map(quote).join(","), ...store.leads.map((lead) => columns.map((column) => quote(lead[column])).join(","))].join("\r\n");
    response.writeHead(200, { "content-type": "text/csv; charset=utf-8", "content-disposition": "attachment; filename=FMW_leads.csv", "cache-control": "no-store" });
    response.end(`\uFEFF${csv}`);
    return;
  }

  if (request.method === "GET" && url.pathname === "/api/admin/summary") {
    if (!isAdmin(request)) return json(response, 401, { ok: false, error: "No autorizado" });
    const store = await readStore();
    const archetypes = {};
    for (const lead of store.leads) archetypes[lead.ARQUETIPO] = (archetypes[lead.ARQUETIPO] || 0) + 1;
    const buyers = store.leads.filter((lead) => lead.COMPRA === "SÍ").length;
    const paidTransactions = store.transactions.filter((item) => item.status === "paid").length;
    const conversionRate = store.leads.length ? Number(((buyers / store.leads.length) * 100).toFixed(2)) : 0;
    const recentTransactions = [...store.transactions].sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt))).slice(0, 100);
    return json(response, 200, { ok: true, totals: {
      leads: store.leads.length, buyers, conversionRate,
      events: store.events.length, assessments: store.assessments.length, transactions: store.transactions.length,
      paidTransactions, emailsSent: store.emailDeliveries.length, pendingIntegrations: store.integrationOutbox.filter((item) => item.status === "pending").length
    }, archetypes, recentLeads: [...store.leads].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).slice(0, 100), recentTransactions, updatedAt: store.updatedAt });
  }

  return json(response, 404, { ok: false, error: "Ruta API no encontrada" });
}

async function serveStatic(request, response, url) {
  const requested = url.pathname === "/" ? "/index.html" : url.pathname;
  const safe = normalize(decodeURIComponent(requested)).replace(/^(\.\.[/\\])+/, "");
  const filePath = resolve(ROOT, `.${safe}`);
  if (!filePath.startsWith(ROOT)) return json(response, 403, { ok: false, error: "Acceso denegado" });
  try {
    const content = await readFile(filePath);
    response.writeHead(200, { "content-type": MIME_TYPES[extname(filePath).toLowerCase()] || "application/octet-stream",
      "cache-control": extname(filePath) === ".html" ? "no-cache" : "public, max-age=3600", ...securityHeaders() });
    response.end(content);
  } catch (error) {
    if (error.code === "ENOENT") return json(response, 404, { ok: false, error: "Archivo no encontrado" });
    throw error;
  }
}

export async function handler(request, response) {
  try {
    await ensureStore();
    const url = new URL(request.url || "/", `http://${request.headers.host || "localhost"}`);
    if (url.pathname.startsWith("/api/")) return await handleApi(request, response, url);
    return await serveStatic(request, response, url);
  } catch (error) {
    const requestId = randomUUID();
    log("error", "request_failed", { requestId, method: request.method, url: request.url, status: error.status || 500, error: error.message, stack: process.env.NODE_ENV === "production" ? undefined : error.stack });
    return json(response, error.status || 500, { ok: false, error: error.status && error.status < 500 ? error.message : "Error interno", requestId });
  }
}

export default handler;

if (!process.env.VERCEL) {
  await ensureStore();
  const server = createServer(handler);
  server.keepAliveTimeout = 65_000;
  server.headersTimeout = 66_000;
  server.requestTimeout = 30_000;
  server.listen(PORT, () => {
    log("info", "server_started", { port: PORT, publicBaseUrl: PUBLIC_BASE_URL, nodeEnv: process.env.NODE_ENV || "development" });
    if (!ADMIN_TOKEN) log("warn", "admin_token_missing");
  });

  let shuttingDown = false;
  async function shutdown(signal) {
    if (shuttingDown) return;
    shuttingDown = true;
    log("info", "server_shutdown_started", { signal });
    const forceExit = setTimeout(() => process.exit(1), 10_000);
    forceExit.unref();
    server.close((error) => {
      clearTimeout(forceExit);
      if (error) {
        log("error", "server_shutdown_failed", { error: error.message });
        process.exit(1);
      }
      log("info", "server_shutdown_completed", { signal });
      process.exit(0);
    });
  }
  process.on("SIGTERM", () => shutdown("SIGTERM"));
  process.on("SIGINT", () => shutdown("SIGINT"));
}
