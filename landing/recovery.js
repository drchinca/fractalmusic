const form = document.querySelector("#recovery-form");
const status = document.querySelector("#recovery-status");

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  const data = new FormData(form);
  button.disabled = true;
  status.textContent = "Verificando la compra…";
  try {
    const response = await fetch("/api/delivery/recover", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email: String(data.get("email") || "").trim(), reference: String(data.get("reference") || "").trim() })
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || "No fue posible renovar el acceso");
    status.textContent = "Si los datos corresponden a una compra confirmada, recibirás un nuevo enlace por correo.";
    form.reset();
  } catch (error) {
    status.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
