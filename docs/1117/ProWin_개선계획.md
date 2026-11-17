# ProWin 개선 계획서

## 개요

ProWin 시스템에 다음 두 가지 주요 기능을 추가합니다:
1. **유사사례 검색 (RAG 기반)** - RFP 요구사항에 대한 과거 제안서 검색 및 추천
2. **제안서 미리보기 개선** - 슬라이드 확대/커밋 비교 기능

---

## 1. 유사사례 검색 (RAG 기반)

### 1.1 현재 상태

**위치**: `prowin-simple/js/app.js` - RFP 화면 (line 319-333)

**현재 구조**:
- `data/rfp.json`의 `similar` 필드에 요구사항별 유사 사례를 **정적 데이터**로 저장
- 예시:
  ```json
  "similar": {
    "R-01": [
      ["OO생명 언더라이팅 고도화", "기술 · 2026", "무중단 이관 아키텍처", "32p"],
      ["△△생명 계약관리", "기술 · 2025", "보상 트랜잭션 설계", "44p"]
    ]
  }
  ```
- UI에서 요구사항 클릭 시 미리 정의된 유사 사례 목록 표시

**문제점**:
- 수동으로 유사 사례를 매핑해야 함
- 새로운 제안서나 요구사항 추가 시 자동 추천 불가
- 의미 기반 검색 불가능 (키워드만 의존)

### 1.2 개선 목표

**RAG (Retrieval-Augmented Generation) 도입**으로 자동 유사사례 추천 시스템 구축

**핵심 기능**:
1. 과거 제안서 페이지를 벡터 임베딩으로 변환하여 저장
2. RFP 요구사항 입력 시 의미적으로 유사한 과거 제안서 페이지 자동 검색
3. 관련도 점수 기반 상위 N개 추천

### 1.3 아키텍처 설계

#### 1.3.1 전체 구조

```
┌─────────────────┐
│  ProWin Frontend│
│  (Vanilla JS)   │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────────────┐
│  RAG Backend (Python)   │
│  - FastAPI / Flask      │
│  - LangChain            │
└────────┬────────────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌────────┐ ┌──────────────┐
│Vector  │ │ LLM API      │
│DB      │ │ (OpenAI /    │
│(Chroma)│ │  Claude)     │
└────────┘ └──────────────┘
```

#### 1.3.2 데이터 흐름

**1단계: 임베딩 생성 및 저장 (오프라인)**
```
과거 제안서 PPT
  ↓ [슬라이드 추출]
슬라이드 텍스트 + 메타데이터
  ↓ [임베딩 모델]
벡터 임베딩
  ↓ [저장]
ChromaDB / FAISS
```

**2단계: 유사사례 검색 (런타임)**
```
RFP 요구사항 텍스트
  ↓ [임베딩]
쿼리 벡터
  ↓ [유사도 검색]
Vector DB → 상위 K개 슬라이드
  ↓ [재랭킹 (선택)]
LLM으로 관련도 평가
  ↓ [반환]
Frontend에 추천 목록 표시
```

### 1.4 구현 계획

#### Phase 1: 백엔드 구축

**1.1 Python 백엔드 서버 구축**
- 프레임워크: FastAPI (경량, 비동기 지원)
- 위치: `traceOps/prowin-rag-backend/`
- 포트: 8081 (ProWin과 분리)

**1.2 벡터 DB 선택 및 구축**
- **추천**: ChromaDB (로컬 설치, 경량, Python 친화적)
- 대안: FAISS (더 빠름, 메모리 기반)
- 위치: `traceOps/prowin-rag-backend/vectordb/`

**1.3 임베딩 모델**
- 옵션 1: OpenAI Embeddings API (`text-embedding-3-small`)
  - 장점: 성능 우수, 간편
  - 단점: API 비용 발생
- 옵션 2: 로컬 임베딩 모델 (HuggingFace Sentence Transformers)
  - 모델: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
  - 장점: 무료, 한국어 지원
  - 단점: 초기 다운로드 필요, 성능 약간 낮음

**1.4 데이터 전처리 파이프라인**
```python
# 예상 구조
class ProposalIndexer:
    def index_proposal(self, ppt_path, metadata):
        """PPT를 슬라이드 단위로 임베딩하여 저장"""
        slides = extract_slides(ppt_path)
        for idx, slide in enumerate(slides):
            text = slide.extract_text()
            embedding = embed_model.embed(text)
            vectordb.add(
                embedding=embedding,
                metadata={
                    "proposal_name": metadata["name"],
                    "year": metadata["year"],
                    "category": metadata["category"],
                    "slide_number": idx,
                    "text": text
                }
            )
```

#### Phase 2: API 엔드포인트

**2.1 유사사례 검색 API**
```
POST /api/rag/search-similar
Request:
{
  "requirement_text": "무중단 이관 방안",
  "top_k": 5,
  "filters": {
    "year_min": 2024,
    "category": "기술"  // optional
  }
}

Response:
{
  "results": [
    {
      "proposal_name": "OO생명 언더라이팅 고도화",
      "category": "기술",
      "year": 2026,
      "slide_title": "무중단 이관 아키텍처",
      "slide_number": 32,
      "relevance_score": 0.89,
      "preview_text": "서비스 중단 없이 기간계→차세대..."
    }
  ]
}
```

**2.2 제안서 인덱싱 API (관리자용)**
```
POST /api/rag/index-proposal
Request:
{
  "file_path": "/path/to/proposal.pptx",
  "metadata": {
    "name": "한화손해보험 차세대",
    "year": 2026,
    "category": "기술",
    "client": "한화손해보험"
  }
}

Response:
{
  "status": "success",
  "indexed_slides": 45
}
```

**2.3 헬스 체크**
```
GET /api/rag/health
Response:
{
  "status": "ok",
  "indexed_proposals": 15,
  "total_slides": 678
}
```

#### Phase 3: 프론트엔드 통합

**3.1 RFP 화면 수정** (`js/app.js`)

현재 코드 (line 328-331):
```javascript
h += '<div class="card"><h3>유사 사례 추천 <span class="chip">Step 2</span></h3>';
var sims = r.similar[sel] || [];
h += sims.length ? sims.map(function (x) {
  return '<div class="act">...</div>';
}).join('') : '<div class="empty">추천 사례가 없습니다.</div>';
```

개선:
```javascript
// RAG API 호출 추가
function fetchSimilarCases(reqId) {
  var req = S.data.rfp.reqs.find(r => r.id === reqId);
  if (!req) return Promise.resolve([]);

  return fetch('http://localhost:8081/api/rag/search-similar', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      requirement_text: req.t + ' ' + req.d,
      top_k: 5
    })
  })
  .then(r => r.json())
  .then(data => data.results);
}

// viewRfp 함수 수정
function viewRfp() {
  // ... 기존 코드 ...

  // 유사사례를 비동기로 로드
  h += '<div class="card"><h3>유사 사례 추천 <span class="chip">RAG</span></h3>';
  h += '<div id="similar-cases"><div class="empty">검색 중...</div></div>';
  h += '</div></div></div>';

  // 렌더링 후 비동기 로드
  setTimeout(() => {
    fetchSimilarCases(S.rfpReq).then(cases => {
      var container = document.getElementById('similar-cases');
      if (!cases.length) {
        container.innerHTML = '<div class="empty">추천 사례가 없습니다.</div>';
        return;
      }
      container.innerHTML = cases.map(c =>
        `<div class="act">
          <div>
            <b>${esc(c.proposal_name)}</b>
            <div class="muted">${esc(c.category)} · ${c.year} · 슬라이드 ${c.slide_number}</div>
            <div style="font-size:13px;color:var(--ink2);margin-top:4px">${esc(c.preview_text)}</div>
          </div>
          <span class="d">관련도 ${Math.round(c.relevance_score * 100)}%</span>
        </div>`
      ).join('');
    });
  }, 100);

  return h;
}
```

**3.2 로딩 상태 및 에러 처리**
```javascript
function fetchSimilarCases(reqId) {
  return fetch('http://localhost:8081/api/rag/search-similar', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      requirement_text: req.t + ' ' + req.d,
      top_k: 5
    })
  })
  .then(r => {
    if (!r.ok) throw new Error('RAG 서버 오류');
    return r.json();
  })
  .then(data => data.results)
  .catch(err => {
    console.error('RAG 검색 실패:', err);
    // Fallback: 정적 데이터 사용
    return S.data.rfp.similar[reqId] || [];
  });
}
```

#### Phase 4: 초기 데이터 준비

**4.1 과거 제안서 수집**
- 위치: `traceOps/prowin-rag-backend/proposals/`
- 필요 항목: PPT 파일 + 메타데이터 (이름, 연도, 카테고리, 발주처)

**4.2 메타데이터 정의** (`proposals_metadata.json`)
```json
{
  "proposals": [
    {
      "id": "P001",
      "name": "OO생명 언더라이팅 고도화",
      "file": "proposals/P001_OO생명_언더라이팅.pptx",
      "year": 2026,
      "category": "기술",
      "client": "OO생명",
      "tags": ["MSA", "무중단 이관", "성능 최적화"]
    }
  ]
}
```

**4.3 인덱싱 스크립트**
```bash
# 초기 인덱싱 실행
cd traceOps/prowin-rag-backend
python scripts/index_all_proposals.py
```

### 1.5 기술 스택

| 항목 | 기술 | 비고 |
|------|------|------|
| 백엔드 프레임워크 | FastAPI | 비동기, 자동 API 문서 |
| 벡터 DB | ChromaDB | 로컬, 경량, 영구 저장 |
| 임베딩 모델 | OpenAI API 또는 Sentence Transformers | API vs 로컬 선택 |
| PPT 파싱 | python-pptx | 슬라이드 텍스트 추출 |
| RAG 프레임워크 | LangChain (선택) | 고급 RAG 패턴 구현 시 |

### 1.6 디렉토리 구조

```
traceOps/
├── prowin-simple/           # 기존 프론트엔드
├── prowin-rag-backend/      # 새로운 RAG 백엔드
│   ├── main.py             # FastAPI 엔트리포인트
│   ├── requirements.txt    # Python 의존성
│   ├── config.py           # 설정 (임베딩 모델, DB 경로)
│   ├── api/
│   │   ├── search.py       # 검색 엔드포인트
│   │   └── index.py        # 인덱싱 엔드포인트
│   ├── core/
│   │   ├── embedder.py     # 임베딩 생성
│   │   ├── vectordb.py     # ChromaDB 래퍼
│   │   └── ppt_parser.py   # PPT 파싱
│   ├── scripts/
│   │   └── index_all_proposals.py  # 초기 인덱싱
│   ├── proposals/          # PPT 파일 저장소
│   │   └── metadata.json
│   └── vectordb/           # ChromaDB 영구 저장소
└── docs/
    └── ProWin_개선계획.md  # 이 문서
```