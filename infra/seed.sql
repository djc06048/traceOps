-- DB 적재 흐름 검증용 샘플 데이터 (실제 분석기 구현 전 파이프라인 확인용)
INSERT INTO nodes (node_type, qualified_name, class_name, method_name, file_path, edit_state) VALUES
    ('ENTRY',   'hwgi.ltr.UdrtkGu.bc.FcdLtrFacvrBscrlAcmrkInq', 'FcdLtrFacvrBscrlAcmrkInq', 'inquireFacvrBscrlAcmrk',
     'hwgi-ltr-UdrtkGu/src/main/java/hwgi/ltr/UdrtkGu/bc/FcdLtrFacvrBscrlAcmrkInq.java', 'AUTO'),
    ('PROGRAM', 'hwgi.ltr.UdrtkGu.bc.LtrFacvrBscrlAcmrkInq', 'LtrFacvrBscrlAcmrkInq', 'inquireFacvrBscrlAcmrkNew',
     'hwgi-ltr-UdrtkGu/src/main/java/hwgi/ltr/UdrtkGu/bc/LtrFacvrBscrlAcmrkInq.java', 'AUTO'),
    ('EXTERNAL', 'hwgi.ltr.UdrtkGu.bc.InfLtrInsCrdif', 'InfLtrInsCrdif', NULL, NULL, 'AUTO');

INSERT INTO edges (caller_node_id, callee_node_id, call_site_line, edit_state)
SELECT c.id, e.id, 45, 'AUTO'
FROM nodes c, nodes e
WHERE c.qualified_name = 'hwgi.ltr.UdrtkGu.bc.FcdLtrFacvrBscrlAcmrkInq'
  AND e.qualified_name = 'hwgi.ltr.UdrtkGu.bc.LtrFacvrBscrlAcmrkInq';

INSERT INTO edges (caller_node_id, callee_node_id, edit_state)
SELECT c.id, e.id, 'AUTO'
FROM nodes c, nodes e
WHERE c.qualified_name = 'hwgi.ltr.UdrtkGu.bc.LtrFacvrBscrlAcmrkInq'
  AND e.qualified_name = 'hwgi.ltr.UdrtkGu.bc.InfLtrInsCrdif';

INSERT INTO requirements (title, description, status) VALUES
    ('정액담보업계누적위험조회 연계 확인', 'FcdLtrFacvrBscrlAcmrkInq 호출체인이 캔버스에 정상 반영되는지 확인', 'CONFIRMED');
