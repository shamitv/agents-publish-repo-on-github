package com.energy.billing.support;

import java.net.URI;
import java.util.Locale;
import java.util.Set;

public final class ReferenceGuards {
    private ReferenceGuards() {
    }

    public static boolean sameOwner(Object recordOwner, Object currentUser) {
        return String.valueOf(recordOwner).equals(String.valueOf(currentUser));
    }

    public static boolean allowedCallback(String target, Set<String> allowedHosts) {
        try {
            URI parsed = URI.create(target == null ? "" : target);
            String scheme = parsed.getScheme();
            return ("http".equals(scheme) || "https".equals(scheme)) && allowedHosts.contains(parsed.getHost());
        } catch (IllegalArgumentException ex) {
            return false;
        }
    }

    public static String normalizeIdentifier(Object value) {
        return String.valueOf(value == null ? "" : value).trim().toLowerCase(Locale.ROOT);
    }
}
