package com.traceops.graph;

import java.util.List;
import java.util.Map;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@CrossOrigin(origins = "http://localhost:5173")
public class GraphController {

    private final NodeRepository nodeRepository;
    private final EdgeRepository edgeRepository;

    public GraphController(NodeRepository nodeRepository, EdgeRepository edgeRepository) {
        this.nodeRepository = nodeRepository;
        this.edgeRepository = edgeRepository;
    }

    @GetMapping("/api/graph")
    public Map<String, List<?>> getGraph() {
        return Map.of(
                "nodes", nodeRepository.findAll(),
                "edges", edgeRepository.findAll());
    }
}
