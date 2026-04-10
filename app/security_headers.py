from typing import Callable
from starlette.types import ASGIApp, Receive, Scope, Send


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
    
                # Helper to check if we are serving a static file
                path = scope.get("path", "")
                is_static = path.startswith("/static")
    
                def set_header(name: str, value: str):
                    headers[name.lower().encode()] = value.encode()
    
                # (1-9) Keep your HSTS, CSP, etc.
                set_header("strict-transport-security", "max-age=63072000; includeSubDomains; preload")
                set_header("x-content-type-options", "nosniff")
                set_header("x-frame-options", "DENY")
                set_header("referrer-policy", "strict-origin-when-cross-origin")
                
                csp = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
                       "script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
                set_header("content-security-policy", csp)
    
                # (10) Cache-Control: ONLY for APIs, not for static images
                if not is_static:
                    set_header("cache-control", "no-store, max-age=0")
                
                # (11) Fix for the "Gibberish" / COEP issue
                # If it's an image, we need to allow it to be embedded
                if is_static:
                    set_header("cross-origin-resource-policy", "cross-origin")
                else:
                    set_header("cross-origin-resource-policy", "same-origin")
    
                message["headers"] = list(headers.items())
    
            await send(message)
    
        await self.app(scope, receive, send_wrapper)