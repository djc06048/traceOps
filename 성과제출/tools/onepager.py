# -*- coding: utf-8 -*-
"""성과 제출 원페이퍼(Word) 생성기. 사용: python3 성과제출/tools/onepager.py
기존 제출 Word 양식(제목 「」, 요약 한 줄, 참여자, 번호 장, ○ 가나다 개조식)을 따른다.
내용은 각 덱(build_*.py)의 최종 문구를 요약한 것이므로, 덱을 고치면 여기도 함께 갱신한다."""
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

FONT = '맑은 고딕'
MEMBERS = '황금빛, 홍건의, 박혜림, 서준혁'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {'prowin': os.path.join(HERE, '..', 'prowin', '원페이퍼_ProWin.docx'),
       'traceops': os.path.join(HERE, '..', 'traceOpsReqSync', '원페이퍼_TraceOps_ReqSync.docx')}


def run(p, text, size=10, bold=False, underline=False):
    r = p.add_run(text)
    r.font.size = Pt(size); r.bold = bold; r.underline = underline
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    return r


def border(p, where, sz=12):
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement('w:pBdr')
    e = OxmlElement(f'w:{where}')
    e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz)); e.set(qn('w:space'), '4'); e.set(qn('w:color'), '000000')
    b.append(e); pPr.append(b)


def para(doc, left=0.0, hang=0.0, before=0, after=2, align=None, line=1.25):
    p = doc.add_paragraph()
    f = p.paragraph_format
    f.left_indent = Cm(left + hang); f.first_line_indent = Cm(-hang) if hang else None
    f.space_before = Pt(before); f.space_after = Pt(after); f.line_spacing = line
    if align: p.alignment = align
    return p


def build(key, title, summary, sections):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.5)
    st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

    p = para(doc, before=0, after=6, align=WD_ALIGN_PARAGRAPH.CENTER, line=1.3)
    border(p, 'top', 18)
    run(p, f'「{title}」', 17, True)
    p = para(doc, after=3, line=1.3)
    run(p, '* ' + summary, 10.5)
    p = para(doc, after=6, align=WD_ALIGN_PARAGRAPH.RIGHT)
    run(p, '참여자 :', 10.5, underline=True); run(p, ' ' + MEMBERS, 10.5)
    border(p, 'bottom', 12)

    for no, head, lead, items in sections:
        p = para(doc, before=7, after=2)
        run(p, f'{no}. {head}', 11, True)
        if lead:
            p = para(doc, left=0.5, hang=0.5)
            run(p, '○ ' + lead, 10)
        for it in items:
            txt, subs = it if isinstance(it, tuple) else (it, [])
            p = para(doc, left=1.0 if lead else 0.5, hang=0.6)
            run(p, txt, 10)
            for sub in subs:
                p = para(doc, left=1.9 if lead else 1.4, hang=0.5, after=1)
                run(p, sub, 9.5)
    doc.save(OUT[key])
    return OUT[key]


PROWIN = ('ProWin 제안관리 시스템', '제안(Proposal)을 통해 수주(Win)를 이끌어낸다. 프로젝트(Project)를 수주(Win)한다.', [
    (1, '목 표', "제안을 '사람 수'가 아닌 '축적된 자산과 표준 절차'로 수행하는 체계로 전환", [
        '가. (효율화) 제안 전 과정을 표준 절차·템플릿으로 체계화하여 임시 TF 및 개인 역량 의존 구조에서 탈피',
        '나. (자산화) 과거 제안 산출물을 검색·재활용 가능한 자산 라이브러리로 축적하여 반복 재작성 제거',
        '다. (경쟁력) 소수 인력으로 제안 품질을 유지하고 제안 투입 인건비 절감']),
    (2, '추진 배경', '현행 제안 업무는 전담 조직·표준·시스템 없이 수작업과 개인 역량에 의존, 제안 확대 시 품질·생산성 저하 불가피', [
        '가. 전담 제안 조직 부재로 RFP마다 임시 TF 구성, 매 건 처음부터 반복되고 담당자 역량에 따라 품질이 좌우됨',
        '나. 조견표·합본·목차 등 핵심 산출물을 수작업으로 작성, 휴먼 에러가 상존하고 버전 꼬임·마감 리스크 발생',
        '다. 과거 제안 자산이 개인 단위로 분산·사장되어 재활용이 불가하고 매 제안마다 재작성 부담 반복',
        '라. 리뷰·의사결정이 구두 중심으로 이루어져 결정 근거가 기록되지 않아 추적·이관이 곤란']),
    (3, '성과', None, [
        ('가. 제안 업무 화면 구현과 표준 업무 흐름 정립', [
            '1) RFP·요구사항, 목차, 제안서 검토, 제안서 관리 등 핵심 기능이 데이터 저장과 함께 동작',
            '2) 제안 착수, 작성, 검토, 최종 확정의 4단계 표준 업무 흐름 정립']),
        ('나. 핵심 기능 기술 검증', [
            '1) PPT 업로드 시 제목 추출, 목차 연결, 미리보기, 이력 저장, 합본의 실현성 검증',
            '2) RFP 요구사항 후보 자동 추출(규칙 기반), 과거 제안서 슬라이드 적재와 키워드·메타 검색']),
        ('다. AI 활용 설계', [
            '1) 로컬 LLM(Ollama)이 요구사항·목차 초안을 생성하고 PM이 확정하는 구조 설계',
            '2) 요구사항 기준으로 과거 제안서의 유사 사례를 추천하는 RAG 저장소 설계'])]),
    (4, '핵심 설계 내용', None, [
        '가. 문서 작성은 기존 오피스(PPT·엑셀)를 활용하고 시스템은 업로드·처리·다운로드를 담당',
        '나. 제안서의 이력·확정본·변경점을 체계적으로 관리하는 버전관리 방식 도입',
        '다. 과거 제안을 재활용 자산으로 축적·검색하는 자산 라이브러리 구성',
        '라. 요구사항·목차·장표를 연결해 누락을 사전에 확인하고, 수주 후 확정 요구사항을 TraceOps로 연계하도록 설계']),
    (5, '개선사항', None, [
        '가. 로컬 LLM 기반 요구사항·목차 초안 보완, 의미 검색 기반 유사 사례 추천 구현',
        '나. 요구사항·목차·장표 연결(조견표 쪽수 자동 채움, 미답변 요구사항 알림) 구현',
        '다. 경비·공수 자동 합계, 데이터 연동·권한 정비, 상용화 기반 보완'])])

TRACEOPS = ('TraceOps · ReqSync 요구사항 추적·연계관리 플랫폼', '요구사항을 AI가 빠짐없이 보완하고, 요구사항부터 연계까지 하나의 흐름으로 추적한다.', [
    (1, '목 표', '개발자 개인의 경험과 기억에 의존하는 방식에서, 프로젝트 전체가 공유하는 표준 절차와 공용 자산 기반 체계로 전환', [
        '가. (자산화) 요구사항·프로세스·화면·테이블·대내외 연계의 연결고리를 프로젝트 공용 자산으로 관리',
        '나. (AI 활용 자동화) AI·연계 분석·수행 관리의 자동화로 요구사항 반영 정확도를 높이고 변경 영향 분석·범위 관리 효율화',
        '다. (추적성) 요구사항부터 테스트까지 단계 간 정합성을 갖춘 추적성을 확보하여 누락 리스크 최소화']),
    (2, '추진 배경', '현행 요구사항 확정·연계관리 업무는 회의록과 엑셀·PMS 중심의 수작업에 의존, 프로젝트 확대 시 누락·재작업 불가피', [
        '가. 요구사항이 상세화되어 있지 않아 기술협상·분석 단계에서 고객사와 협의하며 보완, 근거는 회의록에만 남고 반영은 수작업',
        '나. 한 프로세스에 여러 메서드와 담당 개발자가 있어, 메서드 하나가 개발 대상에서 빠지면 프로세스 전체가 동작하지 않음',
        '다. 요구사항·분석·설계·개발·테스트를 엑셀·PMS로 수작업 관리, 개발 목록 삭제 시 요구사항 매핑 누락 가능']),
    (3, '성과', None, [
        ('가. ReqSync 요구사항 개정 (AI)', [
            '1) 로컬 LLM이 회의록에서 결정사항을 추출하고 요구사항 매칭과 개정안 제시까지 수행',
            '2) AI 추출 결과와 PL 편집을 나란히 비교해 확정하는 검토 화면 구현']),
        ('나. 추적 관리', [
            '1) ProWin 확정 RFP 요구사항을 가져와 분석·설계·개발·단위·통합 테스트까지 연결, 삭제·변경 시 영향 안내',
            '2) 상위 항목이 바뀌면 하위에 재검증 표시, 요구사항 변경 이력과 근거 회의 자동 기록']),
        ('다. 연계관리', [
            '1) 프로세스 단위로 메서드 누락을 확인하고, 연계 캔버스에서 호출 관계를 설계',
            '2) 호출구조 정적분석으로 AS-IS 콜트리를 반영하고, 연계 테스트케이스로 프로세스 검증'])]),
    (4, '핵심 설계 내용', None, [
        '가. (AI) 회의록 결정사항을 AI가 추출해 요구사항 개정안에 반영하고, 확정 권한은 PL에게 두어 AI 오판 리스크 통제 (ReqSync)',
        '나. (연계관리) 캔버스 기반 호출체인 등록으로 연계 관계를 공용 자산화하고, 메서드 누락을 사전에 차단',
        '다. (추적 관리) 요구사항ID·물리ID를 단계 간 자동 상속하고, 삭제·변경 시 영향 범위를 안내한 뒤 검토 후 진행',
        '라. 로컬 LLM 서버(Ollama)와 Python 서버·SQLite로 가볍게 구성하여 사내 환경에서 활용']),
    (5, '개선사항', None, [
        '가. GPU 서버와 더 큰 모델 적용, 실회의록 검증으로 AI 정확도와 활용 범위 확대',
        '나. 채널(CM, TM, 콜센터)과 AI Agent를 노드로 구분한 연계 범위와 변경 영향 추적 확대'])])

if __name__ == '__main__':
    print(build('prowin', *PROWIN))
    print(build('traceops', *TRACEOPS))
