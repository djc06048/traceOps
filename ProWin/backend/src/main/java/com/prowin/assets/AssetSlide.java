package com.prowin.assets;

import java.util.List;

public record AssetSlide(String id, String proposalName, String clientSector, String year, boolean won,
                          String author, String confidentiality, List<String> tags, int slideNumber,
                          String title, String body, String createdAt) {
}
