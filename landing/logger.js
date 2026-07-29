function scrub(value) {
  if (!value || typeof value !== "object") return value;
  const clone = Array.isArray(value) ? [...value] : { ...value };
  for (const key of Object.keys(clone)) {
    if (/token|secret|authorization|api[_-]?key|signature/i.test(key)) clone[key] = "[REDACTED]";
    else if (clone[key] && typeof clone[key] === "object") clone[key] = scrub(clone[key]);
  }
  return clone;
}

export function log(level, message, detail = {}) {
  const record = { timestamp: new Date().toISOString(), level, message, ...scrub(detail) };
  const output = JSON.stringify(record);
  if (level === "error") console.error(output);
  else if (level === "warn") console.warn(output);
  else console.log(output);
}
