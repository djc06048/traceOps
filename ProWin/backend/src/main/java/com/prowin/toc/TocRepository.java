package com.prowin.toc;

import java.util.List;

public interface TocRepository {
    List<TocRow> findAll(String projectId);

    TocRow create(String projectId, int level, String title, String owner, String pages, String status, String who);

    TocRow update(String projectId, String id, int level, String title, String owner, String pages, String status, String who);

    void delete(String projectId, String id, String who, String reason);

    void updatePages(String projectId, String id, String pages);
}
