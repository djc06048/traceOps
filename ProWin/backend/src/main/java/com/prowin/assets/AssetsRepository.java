package com.prowin.assets;

import java.util.List;

public interface AssetsRepository {

    record NewSlide(String title, String body, int slideNumber) {
    }

    record SearchFilter(String keyword, String clientSector, String year, Boolean won) {
    }

    List<AssetSlide> ingest(String proposalName, String clientSector, String year, boolean won,
                             String author, String confidentiality, List<String> tags,
                             String sourceFile, List<NewSlide> slides);

    List<AssetSlide> search(SearchFilter filter, int limit);

    List<AssetSlide> findAll();
}
