import json
from urllib.parse import parse_qs, urlparse

class HTTPException(Exception):
    def __init__(self, status_code=500, detail="Error"):
        self.status_code = status_code
        self.detail = detail

class Request:
    def __init__(self):
        self.headers = {}
        self.url = type("Url", (), {"path": ""})()

class Response:
    def __init__(self, status_code=200, content=None):
        self.status_code = status_code
        self._content = content
        self.headers = {}
    def json(self):
        return self._content

class FastAPI:
    def __init__(self, title=None, version=None):
        self.title = title
        self.version = version
        self.routes = []
    def add_middleware(self, *args, **kwargs):
        return None
    def middleware(self, kind):
        def decorator(func):
            return func
        return decorator
    def get(self, path):
        return self._route("GET", path)
    def post(self, path):
        return self._route("POST", path)
    def _route(self, method, path):
        def decorator(func):
            self.routes.append((method, path, func))
            return func
        return decorator
    def _match(self, method, path):
        for m, template, func in self.routes:
            if m != method:
                continue
            tparts = template.strip('/').split('/') if template != '/' else []
            pparts = path.strip('/').split('/') if path != '/' else []
            if len(tparts) != len(pparts):
                continue
            params = {}
            ok = True
            for tp, pp in zip(tparts, pparts):
                if tp.startswith('{') and tp.endswith('}'):
                    params[tp[1:-1]] = pp
                elif tp != pp:
                    ok = False
                    break
            if ok:
                return func, params
        return None, {}
    async def __call__(self, scope, receive, send):
        await send({"type": "http.response.start", "status": 404, "headers": []})
        await send({"type": "http.response.body", "body": b'{"detail":"Not implemented in lightweight test shim"}'})
