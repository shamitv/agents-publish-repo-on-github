package com.hr.model;

import java.util.Arrays;
import java.util.List;

public enum OnboardingState {
    DRAFT,
    VERIFIED,
    BACKGROUND_CHECKED,
    ACTIVE,
    REJECTED;

    public List<OnboardingState> nextValidStates() {
        return switch (this) {
            case DRAFT -> List.of(VERIFIED, REJECTED);
            case VERIFIED -> List.of(BACKGROUND_CHECKED, REJECTED);
            case BACKGROUND_CHECKED -> List.of(ACTIVE, REJECTED);
            case ACTIVE -> List.of();
            case REJECTED -> List.of();
        };
    }

    public static OnboardingState fromString(String s) {
        return Arrays.stream(values())
                .filter(v -> v.name().equalsIgnoreCase(s))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Unknown state: " + s));
    }
}
