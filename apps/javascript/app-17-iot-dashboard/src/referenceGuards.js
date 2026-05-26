function sameOwner(recordOwner, currentUser) {
  return String(recordOwner) === String(currentUser);
}

function allowedCallback(target, allowedHosts) {
  try {
    const parsed = new URL(target);
    return ["http:", "https:"].includes(parsed.protocol) && allowedHosts.includes(parsed.hostname);
  } catch (_error) {
    return false;
  }
}

function normalizeIdentifier(value) {
  return String(value ?? "").trim().toLowerCase();
}

module.exports = { sameOwner, allowedCallback, normalizeIdentifier };
