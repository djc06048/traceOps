package com.prowin.rfp;

import java.util.List;

public interface RfpRepository {
    RfpDocument findDocument(String projectId);

    List<RfpRequirement> findRequirements(String projectId);

    RfpRequirement create(String projectId, String code, String title, String description, String who);

    RfpRequirement update(String projectId, String id, String title, String description, String who);

    void delete(String projectId, String id, String who, String reason);
}
