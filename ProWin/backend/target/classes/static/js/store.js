/* RFP·목차·제안서 검토·제안서 관리 4개 화면용 API 헬퍼. traceops-simple/js/store.js와 동일 호출 규약. */
(function () {
  window.api = async function (method, path, body) {
    var r = await fetch(path, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: body == null ? undefined : JSON.stringify(body),
      cache: 'no-store'
    });
    var j = null;
    try { j = await r.json(); } catch (e) { /* 204 등 본문 없음 */ }
    if (!r.ok) throw new Error((j && j.error) || (path + ' (' + r.status + ')'));
    return j;
  };
  window.apiUpload = async function (path, formData) {
    var r = await fetch(path, { method: 'POST', body: formData, cache: 'no-store' });
    var j = null;
    try { j = await r.json(); } catch (e) { /* 본문 없음 */ }
    if (!r.ok) throw new Error((j && j.error) || (path + ' (' + r.status + ')'));
    return j;
  };
})();
