import { access, stat } from "node:fs/promises";
import { resolve } from "node:path";

const required = [
  "FMW_ADMIN_TOKEN",
  "PUBLIC_BASE_URL",
  "COMPRACLICK_CHECKOUT_URL",
  "COMPRACLICK_WEBHOOK_SECRET",
  "MAILCHIMP_API_KEY",
  "MAILCHIMP_SERVER_PREFIX",
  "MAILCHIMP_AUDIENCE_ID",
  "EMAIL_API_KEY",
  "EMAIL_FROM",
  "FMW_PRODUCT_FILE"
];

const errors = [];
for (const name of required) {
  if (!String(process.env[name] || "").trim()) errors.push(`${name}: variable requerida ausente`);
}

const baseUrl = String(process.env.PUBLIC_BASE_URL || "");
if (baseUrl && !/^https:\/\//i.test(baseUrl)) errors.push("PUBLIC_BASE_URL: debe usar HTTPS en producción");
if ((process.env.FMW_ADMIN_TOKEN || "").length < 32) errors.push("FMW_ADMIN_TOKEN: debe tener al menos 32 caracteres");
if ((process.env.COMPRACLICK_WEBHOOK_SECRET || "").length < 32) errors.push("COMPRACLICK_WEBHOOK_SECRET: debe tener al menos 32 caracteres");

if (process.env.FMW_PRODUCT_FILE) {
  const product = resolve(process.env.FMW_PRODUCT_FILE);
  try {
    await access(product);
    const info = await stat(product);
    if (!info.isFile() || info.size === 0) errors.push("FMW_PRODUCT_FILE: debe apuntar a un archivo no vacío");
  } catch {
    errors.push("FMW_PRODUCT_FILE: el archivo no existe o no es accesible");
  }
}

if (errors.length) {
  console.error("PRE-FLIGHT BLOQUEADO");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}
console.log("PRE-FLIGHT OK");
