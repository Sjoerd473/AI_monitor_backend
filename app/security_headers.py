from typing import Callable
from starlette.types import ASGIApp, Receive, Scope, Send


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))

                def set_header(name: str, value: str):
                    headers[name.lower().encode()] = value.encode()

                # (1) HSTS
                set_header(
                    "strict-transport-security",
                    "max-age=63072000; includeSubDomains; preload",
                )

                # (2) X-Content-Type-Options
                set_header("x-content-type-options", "nosniff")

                # (3) X-Frame-Options
                set_header("x-frame-options", "DENY")

                # (4) Referrer-Policy
                set_header("referrer-policy", "strict-origin-when-cross-origin")

                # (5) Permissions-Policy
                set_header(
                    "permissions-policy",
                    "geolocation=(), camera=(), microphone=()",
                )

                # (6) Content-Security-Policy (CSP)
                csp = (
                    "default-src 'self'; "
                    "img-src 'self' data:; "
                    "style-src 'self' 'unsafe-inline'; "
                    "script-src 'self'; "
                    "object-src 'none'; "
                    "base-uri 'self'; "
                    "frame-ancestors 'none'"
                )
                set_header("content-security-policy", csp)

                # (7) Cross-Origin-Opener-Policy
                set_header("cross-origin-opener-policy", "same-origin")

                # (8) Cross-Origin-Resource-Policy
                set_header("cross-origin-resource-policy", "same-origin")

                # (9) Cross-Origin-Embedder-Policy
                set_header("cross-origin-embedder-policy", "require-corp")

                # (10) Cache-Control (for APIs)
                set_header(
                    "cache-control",
                    "no-store, max-age=0",
                )

                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_wrapper)