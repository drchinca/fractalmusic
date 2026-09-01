import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, cp, writeFile, readFile, mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { createHmac } from "node:crypto";
import { questions } from "../test-data.js";
import { scoreAnswers } from "../scoring-engine.js";

const source = resolve(process.cwd());
const port = 34187;
const base = `http://127.0.0.1:${port}`;
const adminToken = "qa-admin-token-012345678901234567890123";
const webhookSecret = "qa-webhook-secret-012345678901234567890";
let work;
let child;

async function waitForHealth() {
  for (let i = 0; i < 60; i += 1) {
    try {
      const response = await fetch(`${base}/api/health`);
      if (response.ok) return;
    } catch {}
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 100));
  }
  throw new Error("El servidor de pruebas no inició");
}

async function jsonRequest(path, options = {}) {
  const response = await fetch(`${base}${path}`, options);
  const body = await response.json();
  return { response, body };
}

test.before(async () => {
  work = await mkdtemp(join(tmpdir(), "fmw-e2e-"));
  await cp(source, work, { recursive: true, filter: (entry) => !entry.includes("node_modules") });
  await mkdir(join(work, "data"), { recursive: true });
  await writeFile(join(work, "data", "store.json"), JSON.stringify({ version: 5, leads: [], assessments: [], events: [], transactions: [], integrationOutbox: [], emailDeliveries: [] }));
  child = spawn(process.execPath, ["server.js"], {
    cwd: work,
    env: {
      ...process.env,
      PORT: String(port),
      PUBLIC_BASE_URL: base,
      FMW_ADMIN_TOKEN: adminToken,
      COMPRACLICK_CHECKOUT_URL: "https://checkout.example.test/pay",
      COMPRACLICK_WEBHOOK_SECRET: webhookSecret,
      EMAIL_PROVIDER: "",
      MAILCHIMP_API_KEY: ""
    },
    stdio: ["ignore", "pipe", "pipe"]
  });
  await waitForHealth();
});

test.after(() => {
  child?.kill("SIGTERM");
});

test("health, estáticos y cabeceras de seguridad", async () => {
  const health = await fetch(`${base}/api/health`);
  assert.equal(health.status, 200);
  assert.equal((await health.json()).version, "0.9.0");
  const home = await fetch(`${base}/`);
  assert.equal(home.status, 200);
  assert.equal(home.headers.get("x-frame-options"), "DENY");
  assert.match(home.headers.get("content-security-policy") || "", /default-src 'self'/);
});

test("flujo completo: lead, historial, checkout, webhook, confirmación y administración", async () => {
  const answers = Object.fromEntries(questions.map((question) => [question.id, question.options[0].technicalId]));
  const verified = scoreAnswers(answers);
  const leadPayload = {
    FNAME: "QA FMW", EMAIL: "qa@fractalmusicworld.test", ARQUETIPO: "RESULTADO ALTERADO", ARQSEC: "RESULTADO ALTERADO",
    SCORE1: "0.75", SCORE2: "0.66", MUESTRA: "/muestra.html?arquetipo=oido-fractal", TESTDATE: new Date().toISOString(),
    COMPRA: "NO", PRODUCTO: "", FUENTE: "QA", CONSENT: "SÍ", result_id: "qa-result-001",
    answers, raw_scores: { "Resultado alterado": 99 }, normalized_scores: { "Resultado alterado": 1 }
  };
  const lead = await jsonRequest("/api/leads", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(leadPayload) });
  assert.equal(lead.response.status, 201);
  assert.ok(lead.body.accessToken);

  const history = await jsonRequest("/api/history", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email: leadPayload.EMAIL, token: lead.body.accessToken }) });
  assert.equal(history.response.status, 200);
  assert.equal(history.body.assessments.length, 1);
  assert.equal(history.body.assessments[0].ARQUETIPO, verified.dominant.name);
  assert.notEqual(history.body.assessments[0].ARQUETIPO, "RESULTADO ALTERADO");

  const checkout = await jsonRequest("/api/checkout/start", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email: leadPayload.EMAIL, product: "EL_LUJO_ES" }) });
  assert.equal(checkout.response.status, 201);
  const checkoutUrl = new URL(checkout.body.checkoutUrl);
  const reference = checkout.body.transactionId;
  const state = checkoutUrl.searchParams.get("state");
  assert.ok(reference && state);

  const invalidWebhook = await jsonRequest("/api/webhooks/compraclick", { method: "POST", headers: { "content-type": "application/json", "x-fmw-signature": "invalid" }, body: JSON.stringify({ reference, status: "paid" }) });
  assert.equal(invalidWebhook.response.status, 401);

  const webhookPayload = JSON.stringify({ reference, status: "paid", provider_transaction_id: "QA-PAY-001" });
  const signature = createHmac("sha256", webhookSecret).update(webhookPayload).digest("hex");
  const webhook = await jsonRequest("/api/webhooks/compraclick", { method: "POST", headers: { "content-type": "application/json", "x-fmw-signature": signature }, body: webhookPayload });
  assert.equal(webhook.response.status, 200);

  const status = await jsonRequest("/api/checkout/status", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ reference, state }) });
  assert.equal(status.response.status, 200);
  assert.equal(status.body.transaction.status, "paid");
  assert.ok(status.body.delivery.receiptUrl);

  const unauthorized = await fetch(`${base}/api/admin/summary`);
  assert.equal(unauthorized.status, 401);
  const summary = await jsonRequest("/api/admin/summary", { headers: { authorization: `Bearer ${adminToken}` } });
  assert.equal(summary.response.status, 200);
  assert.equal(summary.body.totals.leads, 1);
  assert.equal(summary.body.totals.buyers, 1);
  assert.equal(summary.body.totals.paidTransactions, 1);

  const csv = await fetch(`${base}/api/admin/export.csv`, { headers: { authorization: `Bearer ${adminToken}` } });
  assert.equal(csv.status, 200);
  assert.match(await csv.text(), /qa@fractalmusicworld\.test/);

  const store = JSON.parse(await readFile(join(work, "data", "store.json"), "utf8"));
  assert.equal(store.transactions[0].status, "paid");
  assert.equal(store.leads[0].COMPRA, "SÍ");
  assert.ok(store.integrationOutbox.some((job) => job.type === "email.purchase_confirmation"));
});

test("recuperación responde neutralmente y limita abuso", async () => {
  for (let i = 0; i < 5; i += 1) {
    const result = await jsonRequest("/api/delivery/recover", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email: "nobody@example.test", reference: `missing-${i}` }) });
    assert.equal(result.response.status, 202);
  }
  const limited = await jsonRequest("/api/delivery/recover", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email: "nobody@example.test", reference: "missing-limit" }) });
  assert.equal(limited.response.status, 429);
});

test("eventos simultáneos se guardan sin colisiones ni pérdidas", async () => {
  const total = 40;
  const responses = await Promise.all(Array.from({ length: total }, (_, index) => jsonRequest("/api/events", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ name: "test_answer", detail: { audit_index: index } })
  })));
  assert.ok(responses.every(({ response }) => response.status === 202));
  const store = JSON.parse(await readFile(join(work, "data", "store.json"), "utf8"));
  const saved = store.events.filter((event) => Number.isInteger(event.detail?.audit_index));
  assert.equal(saved.length, total);
  assert.equal(new Set(saved.map((event) => event.detail.audit_index)).size, total);
});
