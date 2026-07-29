import { sendEvent } from "./api-client.js";

const form = document.querySelector("#checkout-form");
const status = document.querySelector("#checkout-status");

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const data = new FormData(form);
    button.disabled = true;
    status.textContent = "Preparando pago seguro…";
    try {
      const response = await fetch("/api/checkout/start", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          email: String(data.get("email") || "").trim(),
          product: String(data.get("product") || "EL_LUJO_DE_LA_DISONANCIA_DIGITAL")
        })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.error || "No fue posible iniciar el pago");
      await sendEvent("checkout_started", { transaction_id: payload.transactionId });
      window.location.assign(payload.checkoutUrl);
    } catch (error) {
      status.textContent = error.message;
      button.disabled = false;
    }
  });
}
