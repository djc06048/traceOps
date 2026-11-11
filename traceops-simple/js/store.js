/* localStorage 대체: 서버(SQLite)에 저장. getItem/setItem/removeItem 동일 시그니처.
 * ponytail: 시작 시 동기 XHR로 전체를 한 번 읽음(데이터 ~130KB). 커지면 async 로드로 전환. */
(function () {
  var cache = {};
  try {
    var x = new XMLHttpRequest();
    x.open('GET', '/api/store', false);
    x.send();
    if (x.status === 200) cache = JSON.parse(x.responseText);
  } catch (e) { /* 서버 없이 열면 빈 상태 → 원본 JSON 사용 */ }
  function send(method, key, body) {
    var r = new XMLHttpRequest();
    r.open(method, '/api/store/' + encodeURIComponent(key), false);
    r.setRequestHeader('Content-Type', 'application/json');
    r.send(body);
    if (r.status >= 300) throw new Error('store ' + r.status); // 호출부 try/catch가 토스트 처리
  }
  // 관계형 API 호출(요구사항 관리용): 실패 시 서버가 준 메시지로 Error
  window.api = async function (method, path, body) {
    var r = await fetch(path, { method: method, headers: { 'Content-Type': 'application/json' }, body: body == null ? undefined : JSON.stringify(body), cache: 'no-store' });
    var j = null;
    try { j = await r.json(); } catch (e) { /* 204 등 본문 없음 */ }
    if (!r.ok) throw new Error((j && j.error) || (path + ' (' + r.status + ')'));
    return j;
  };
  window.DB = {
    getItem: function (k) { return k in cache ? cache[k] : null; },
    setItem: function (k, v) { send('PUT', k, v); cache[k] = v; },
    removeItem: function (k) { send('DELETE', k); delete cache[k]; }
  };
})();
