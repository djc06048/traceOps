package com.prowin.rfp;

import java.util.List;

public record RfpResponse(RfpDocument document, List<RfpRequirement> requirements) {
}
