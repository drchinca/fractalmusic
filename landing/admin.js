const form = document.querySelector("#admin-form");
const status = document.querySelector("#admin-status");
const dashboard = document.querySelector("#dashboard");
let activeToken = "";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  activeToken = document.querySelector("#admin-token").value;
  await loadDashboard();
});

document.querySelector("#retry-integrations").addEventListener("click", async () => {
  status.textContent = "Reprocesando integraciones…";
  try {
    const response = await fetch("/api/admin/retry-integrations", { method: "POST", headers: authHeaders() });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "No fue posible reprocesar");
    status.textContent = `${data.synced} integraciones sincronizadas; ${data.pending} pendientes.`;
    await loadDashboard(false);
  } catch (error) { status.textContent = error.message; }
});

document.querySelector("#export-csv").addEventListener("click", async () => {
  status.textContent = "Preparando CSV…";
  try {
    const response = await fetch("/api/admin/export.csv", { headers: authHeaders() });
    if (!response.ok) throw new Error("No fue posible exportar los leads");
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "FMW_leads.csv";
    link.click();
    URL.revokeObjectURL(url);
    status.textContent = "CSV exportado.";
  } catch (error) { status.textContent = error.message; }
});

function authHeaders() { return { authorization: `Bearer ${activeToken}` }; }

async function loadDashboard(showLoading = true) {
  if (showLoading) status.textContent = "Cargando…";
  try {
    const response = await fetch("/api/admin/summary", { headers: authHeaders() });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "No autorizado");
    render(data);
    if (showLoading) status.textContent = "";
    dashboard.hidden = false;
  } catch (error) {
    dashboard.hidden = true;
    status.textContent = error.message;
  }
}

function render(data) {
  document.querySelector("#lead-count").textContent = data.totals.leads;
  document.querySelector("#assessment-count").textContent = data.totals.assessments;
  document.querySelector("#buyer-count").textContent = data.totals.buyers;
  document.querySelector("#conversion-rate").textContent = `${data.totals.conversionRate}%`;
  document.querySelector("#paid-count").textContent = data.totals.paidTransactions;
  document.querySelector("#email-count").textContent = data.totals.emailsSent;
  document.querySelector("#pending-count").textContent = data.totals.pendingIntegrations;
  document.querySelector("#archetype-summary").replaceChildren(...Object.entries(data.archetypes)
    .sort((a, b) => b[1] - a[1]).map(([name, count]) => rowPair(name, count)));
  document.querySelector("#lead-rows").replaceChildren(...data.recentLeads.map((lead) => tableRow([
    formatDate(lead.updatedAt), lead.FNAME, lead.EMAIL, lead.ARQUETIPO, lead.ARQSEC, lead.COMPRA
  ])));
  document.querySelector("#transaction-rows").replaceChildren(...data.recentTransactions.map((transaction) => tableRow([
    formatDate(transaction.updatedAt), transaction.id, transaction.email, transaction.product,
    transaction.status, transaction.downloadedAt ? formatDate(transaction.downloadedAt) : "—"
  ])));
}

function rowPair(name, count) {
  const row = document.createElement("div");
  row.className = "admin-list-row";
  const label = document.createElement("span"); label.textContent = name;
  const value = document.createElement("strong"); value.textContent = count;
  row.append(label, value);
  return row;
}
function tableRow(values) {
  const row = document.createElement("tr");
  row.replaceChildren(...values.map((value) => { const cell = document.createElement("td"); cell.textContent = value || "—"; return cell; }));
  return row;
}
function formatDate(value) { return value ? new Date(value).toLocaleString("es-CR") : "—"; }
