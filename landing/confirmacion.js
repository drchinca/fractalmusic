const params = new URLSearchParams(location.search);
const reference = params.get("reference") || "";
const state = params.get("state") || "";
const title = document.querySelector("#confirmation-title");
const status = document.querySelector("#confirmation-status");
const detail = document.querySelector("#confirmation-detail");
const actions = document.querySelector("#delivery-actions");

async function verify() {
  if (!reference || !state) throw new Error("La referencia de pago está incompleta.");
  const response = await fetch("/api/checkout/status", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ reference, state })
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "No fue posible verificar la compra.");
  document.querySelector("#purchase-reference").textContent = data.transaction.reference;
  document.querySelector("#purchase-product").textContent = data.transaction.product;
  document.querySelector("#purchase-email").textContent = data.transaction.email;
  document.querySelector("#purchase-date").textContent = data.transaction.paidAt ? new Date(data.transaction.paidAt).toLocaleString("es-CR") : "Pendiente";
  detail.hidden = false;
  if (data.transaction.status === "paid") {
    title.textContent = "Compra confirmada";
    status.textContent = data.delivery.available
      ? "Tu pago fue aprobado. La descarga protegida ya está disponible."
      : "Tu pago fue aprobado. El archivo digital será habilitado por administración en cuanto el activo definitivo esté configurado.";
    if (data.delivery.available) {
      const link = document.createElement("a");
      link.className = "btn btn-primary";
      link.href = data.delivery.downloadUrl;
      link.textContent = "Descargar obra digital";
      actions.append(link);
    }
    const receipt = document.createElement("a");
    receipt.className = "btn btn-secondary";
    receipt.href = data.delivery.receiptUrl;
    receipt.textContent = "Descargar comprobante";
    actions.append(receipt);
  } else {
    title.textContent = "Pago en procesamiento";
    status.textContent = "CompraClick aún no ha confirmado el pago. Puedes actualizar esta página en unos minutos.";
  }
}

verify().catch((error) => {
  title.textContent = "No pudimos validar la compra";
  status.textContent = error.message;
});
