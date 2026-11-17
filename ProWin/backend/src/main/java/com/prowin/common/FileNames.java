package com.prowin.common;

public final class FileNames {
    private FileNames() {
    }

    /** 경로 구분자를 제거해 파일명만 남긴다. DB 표시용으로만 쓰고, 저장 경로에는 쓰지 않는다. */
    public static String sanitize(String raw, String fallback) {
        if (raw == null || raw.isBlank()) return fallback;
        String name = raw.replace('\\', '/');
        int idx = name.lastIndexOf('/');
        if (idx >= 0) name = name.substring(idx + 1);
        name = name.strip();
        return name.isBlank() ? fallback : name;
    }
}
