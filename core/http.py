"""Stdlib-only HTTP client that mimics the requests API.

Why this exists: `requests` depends on `urllib3`, which can break on
some Python installs (notably Python 3.14) with import errors like:

    ImportError: cannot import name 'SSLTransport' from 'urllib3.util.ssltransport'

By using only the Python standard library (urllib.request), we sidestep
that entirely. Drop-in replacement for the subset of `requests` that
MrRobotTools uses:

    from core import http as requests
    r = requests.get(url, headers=..., timeout=..., allow_redirects=..., verify=False)
    r.status_code / r.text / r.content / r.url / r.headers / r.cookies
    r.json() / r.raise_for_status() / r.is_redirect / r.ok
    except requests.RequestException as e: ...
"""

import json as _json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import http.cookiejar


# Exceptions (mirror requests.exceptions)
class RequestException(Exception):
    pass


class Timeout(RequestException):
    pass


class ConnectionError(RequestException):
    pass


class HTTPError(RequestException):
    def __init__(self, response):
        self.response = response
        super().__init__(f"HTTP {response.status_code}: {response.url}")


class Response:
    """Simple response object matching the requests.Response API."""

    def __init__(self, status_code, body, url, headers, cookies):
        self.status_code = status_code
        self._body = body  # bytes
        self.url = url
        self.headers = headers
        self.cookies = cookies  # list of http.cookiejar.Cookie

    @property
    def text(self):
        content_type = ""
        if self.headers:
            content_type = self.headers.get("Content-Type", "") or ""
        encoding = "utf-8"
        if "charset=" in content_type.lower():
            encoding = content_type.split("charset=")[-1].split(";")[0].strip()
        try:
            return self._body.decode(encoding, errors="replace")
        except (LookupError, TypeError):
            return self._body.decode("utf-8", errors="replace")

    @property
    def content(self):
        return self._body

    def json(self):
        return _json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPError(self)

    @property
    def is_redirect(self):
        return self.status_code in (301, 302, 303, 307, 308)

    @property
    def ok(self):
        return self.status_code < 400


def get(url, headers=None, timeout=10, allow_redirects=True, verify=True, params=None):
    """HTTP GET using only the Python standard library."""
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"

    headers = dict(headers or {})
    if "User-Agent" not in headers:
        headers["User-Agent"] = "MrRobotTools/1.0 (stdlib-urllib)"

    # SSL context
    ctx = None
    if url.lower().startswith("https://"):
        ctx = ssl.create_default_context()
        if not verify:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

    cookie_jar = http.cookiejar.CookieJar()
    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)

    handlers = [cookie_processor]
    if ctx is not None:
        handlers.append(urllib.request.HTTPSHandler(context=ctx))

    if not allow_redirects:
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        handlers.append(_NoRedirect())

    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers=headers)

    try:
        resp = opener.open(req, timeout=timeout)
        body = resp.read()
        final_url = resp.geturl()
        status = resp.getcode()
        resp_headers = resp.headers
        cookies = list(cookie_jar)
        return Response(status, body, final_url, resp_headers, cookies)

    except urllib.error.HTTPError as e:
        # 4xx/5xx or 3xx (when allow_redirects=False) -> return Response
        try:
            body = e.read()
        except Exception:
            body = b""
        return Response(
            e.code,
            body,
            getattr(e, "url", None) or url,
            e.headers or {},
            list(cookie_jar),
        )

    except urllib.error.URLError as e:
        msg = str(getattr(e, "reason", e))
        if "timed out" in msg.lower() or "timeout" in msg.lower():
            raise Timeout(msg)
        raise ConnectionError(msg)

    except ssl.SSLError as e:
        raise ConnectionError(f"SSL Error: {e}")

    except Exception as e:
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            raise Timeout(str(e))
        raise ConnectionError(str(e))
