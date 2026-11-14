package com.prowin.toc;

public record TocRow(String id, int level, String title, String owner, String pages, String status,
                      int orderIndex, boolean presentationAssigned) {
}
