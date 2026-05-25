export function sameOwner(recordOwner: string | number, currentUser: string | number): boolean {
  return String(recordOwner) === String(currentUser);
}

export function allowedCallback(target: string, allowedHosts: string[]): boolean {
  try {
    const parsed = new URL(target);
    return ["http:", "https:"].includes(parsed.protocol) && allowedHosts.includes(parsed.hostname);
  } catch {
    return false;
  }
}

export function normalizeIdentifier(value: unknown): string {
  return String(value ?? "").trim().toLowerCase();
}
