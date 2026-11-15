package com.prowin.toc;

import java.util.List;
import java.util.Map;

public record TocResponse(List<TocRow> rows, Map<String, String> statusLabel) {
    public static final Map<String, String> STATUS_LABEL = Map.of(
            "todo", "미착수", "doing", "진행중", "fix", "보완", "done", "완료");
}
