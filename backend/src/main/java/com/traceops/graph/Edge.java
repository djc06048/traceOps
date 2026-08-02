package com.traceops.graph;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "edges")
public class Edge {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "caller_node_id", nullable = false)
    private Long callerNodeId;

    @Column(name = "callee_node_id", nullable = false)
    private Long calleeNodeId;

    @Column(name = "call_site_line")
    private Integer callSiteLine;

    @Column(name = "edit_state", nullable = false)
    private String editState;

    public Long getId() { return id; }
    public Long getCallerNodeId() { return callerNodeId; }
    public Long getCalleeNodeId() { return calleeNodeId; }
    public Integer getCallSiteLine() { return callSiteLine; }
    public String getEditState() { return editState; }
}
