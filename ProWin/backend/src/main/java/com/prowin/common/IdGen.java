package com.prowin.common;

import java.util.List;
import java.util.function.Function;

public final class IdGen {
    private IdGen() {
    }

    /** Mirrors prowin-simple's nextNum(): prefix-001, prefix-002, ... based on the max existing suffix. */
    public static <T> String next(String prefix, List<T> existing, Function<T, String> idOf) {
        int max = 0;
        for (T item : existing) {
            String id = idOf.apply(item);
            int dash = id.lastIndexOf('-');
            if (dash < 0) continue;
            try {
                int n = Integer.parseInt(id.substring(dash + 1));
                if (n > max) max = n;
            } catch (NumberFormatException ignored) {
            }
        }
        return prefix + "-" + String.format("%02d", max + 1);
    }
}
