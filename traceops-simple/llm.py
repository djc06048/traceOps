"""로컬 LLM 호출 (OpenAI 호환 API: Ollama, vLLM, llama.cpp 서버 등). 표준 라이브러리만 사용.

설정(환경변수):
  LLM_BASE_URL  기본 http://localhost:11434/v1  (Ollama)
  LLM_MODEL     기본 qwen3:4b
  LLM_API_KEY   필요한 서버만 (Ollama는 불필요)
  LLM_TIMEOUT   요청당 초, 기본 600 (CPU 추론은 느림)
  LLM_NO_THINK  기본 1 — 사고 과정 출력 끄기(reasoning_effort=none). 지원하지 않는 서버면 0
"""
import json, os, re, urllib.error, urllib.request

BASE_URL = os.environ.get('LLM_BASE_URL', 'http://localhost:11434/v1').rstrip('/')
MODEL = os.environ.get('LLM_MODEL', 'qwen3:4b')
API_KEY = os.environ.get('LLM_API_KEY', '')
TIMEOUT = float(os.environ.get('LLM_TIMEOUT', 600))
NO_THINK = os.environ.get('LLM_NO_THINK', '1') != '0'


class LLMError(Exception):
    pass


def _request(method, path, body=None, timeout=TIMEOUT):
    headers = {'Content-Type': 'application/json'}
    if API_KEY:
        headers['Authorization'] = 'Bearer ' + API_KEY
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise LLMError('LLM 서버 오류 %d: %s' % (e.code, e.read().decode('utf-8', 'replace')[:300]))
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise LLMError('LLM 서버에 연결하지 못했습니다 (%s). Ollama가 실행 중인지 확인하세요: %s' % (e, BASE_URL))


def status():
    """연결 여부와 설정한 모델이 서버에 있는지."""
    try:
        models = [m.get('id') for m in _request('GET', '/models', timeout=3).get('data', [])]
    except LLMError as e:
        return {'ok': False, 'baseUrl': BASE_URL, 'model': MODEL, 'error': str(e)}
    has = MODEL in models or (':' not in MODEL and MODEL + ':latest' in models)
    out = {'ok': has, 'baseUrl': BASE_URL, 'model': MODEL, 'models': models}
    if not has:
        out['error'] = '모델 %s 이(가) 없습니다. 설치: ollama pull %s' % (MODEL, MODEL)
    return out


def _parse_json(text):
    text = re.sub(r'<think>.*?</think>', '', text or '', flags=re.S).strip()  # Qwen3 사고 과정 제거
    m = re.search(r'```(?:json)?\s*(.*?)```', text, re.S)
    if m:
        text = m.group(1)
    return json.loads(text)


def chat_json(system, user, schema, validate=None, retries=1):
    """JSON 스키마를 강제해 호출하고 파싱·검증한 결과를 돌려준다. 실패하면 retries만큼 다시 요청한다."""
    body = {
        'model': MODEL,
        'temperature': 0,
        'messages': [{'role': 'system', 'content': system + '\n/no_think'}, {'role': 'user', 'content': user}],
        'response_format': {'type': 'json_schema', 'json_schema': {'name': 'result', 'schema': schema}},
    }
    if NO_THINK:  # 사고 과정 출력 끄기(Qwen3 등). CPU에서는 사고 과정 때문에 응답이 수 배 느려진다
        body['reasoning_effort'] = 'none'
    last = None
    for _ in range(retries + 1):
        r = _request('POST', '/chat/completions', body)
        try:
            out = _parse_json(r['choices'][0]['message']['content'])
            if validate:
                validate(out)
            return out
        except (KeyError, IndexError, TypeError, ValueError) as e:
            last = e
    raise LLMError('LLM 응답 형식이 올바르지 않습니다: %s' % last)
