import inspect
from fastapi import HTTPException, Response

class TestClient:
    def __init__(self, app):
        self.app = app
    def get(self, path):
        return self._request("GET", path, None)
    def post(self, path, json=None):
        return self._request("POST", path, json)
    def _request(self, method, path, body):
        url_path, _, query = path.partition('?')
        func, params = self.app._match(method, url_path)
        if not func:
            return Response(404, {"detail": "Not found"})
        sig = inspect.signature(func)
        kwargs = dict(params)
        for name, p in sig.parameters.items():
            if name in kwargs:
                continue
            ann = p.annotation
            if body is not None and hasattr(ann, "__annotations__"):
                kwargs[name] = ann(**body)
            elif p.default is not inspect._empty:
                kwargs[name] = p.default
        try:
            result = func(**kwargs)
        except HTTPException as exc:
            return Response(exc.status_code, {"detail": exc.detail})
        return Response(200, _dump(result))

def _dump(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, list):
        return [_dump(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _dump(v) for k, v in obj.items()}
    return obj
