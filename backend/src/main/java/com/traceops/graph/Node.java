package com.traceops.graph;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "nodes")
public class Node {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "node_type", nullable = false)
    private String nodeType;

    @Column(name = "qualified_name", nullable = false)
    private String qualifiedName;

    @Column(name = "class_name")
    private String className;

    @Column(name = "method_name")
    private String methodName;

    @Column(name = "file_path")
    private String filePath;

    @Column(name = "edit_state", nullable = false)
    private String editState;

    public Long getId() { return id; }
    public String getNodeType() { return nodeType; }
    public String getQualifiedName() { return qualifiedName; }
    public String getClassName() { return className; }
    public String getMethodName() { return methodName; }
    public String getFilePath() { return filePath; }
    public String getEditState() { return editState; }
}
