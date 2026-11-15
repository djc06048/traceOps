package com.prowin.common;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public final class Clock {
    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

    private Clock() {
    }

    public static String nowText() {
        return LocalDateTime.now().format(FMT);
    }
}
