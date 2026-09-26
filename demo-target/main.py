"""SIH26163 Controlled Security Demo Target Application.

IMPORTANT NOTICE:
This is an independent, intentionally vulnerable LOCAL test application
used solely to demonstrate the SIH26163 security-assessment platform workflow.
It is NOT World Monitor and has no connection to production infrastructure.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(
    title="SIH26163 Controlled Security Demo Target",
    description="Intentionally vulnerable local testbed for defensive security assessment validation.",
    version="1.0.0-demo",
)


@app.middleware("http")
async def demo_custom_headers_middleware(request: Request, call_next):
    """Middleware exposing debug metadata and intentionally omitting standard security headers."""
    response = await call_next(request)

    # Controlled Information Disclosure: Expose X-Powered-By header
    response.headers["X-Powered-By"] = "FastAPI-Controlled-Demo-Server/1.0"

    # NOTE: Standard security headers (Content-Security-Policy, X-Content-Type-Options,
    # Referrer-Policy, Permissions-Policy) are INTENTIONALLY OMITTED here for demonstration.
    return response


@app.get("/")
async def root_banner(response: Response):
    """Root banner endpoint identifying the application as a controlled demo target."""
    # Insecure Cookie Configuration: Missing HttpOnly, Missing Secure, Missing SameSite
    # Value is a fake, synthetic demonstration string.
    response.set_cookie(
        key="demo_session",
        value="controlled-demo-value",
        httponly=False,
        secure=False,
        samesite=None,
    )
    return {
        "application": "SIH26163 Controlled Security Demo Target",
        "warning": "INTENTIONALLY VULNERABLE LOCAL TEST APPLICATION",
        "environment": "LOCAL DEMO ONLY",
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Harmless health probe endpoint."""
    return {
        "status": "ok",
        "environment": "demo",
        "message": "SIH26163 Demo Target is operational",
    }


@app.options("/api/demo-data")
@app.get("/api/demo-data")
async def demo_data_endpoint(request: Request):
    """Permissive CORS demonstration endpoint.

    Contains only non-sensitive synthetic dummy data.
    Intentionally returns permissive CORS headers (wildcard / reflected origin with credentials).
    """
    origin = request.headers.get("origin", "*")
    headers = {
        "Access-Control-Allow-Origin": origin if origin != "*" else "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS, HEAD",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
    }

    body = {
        "message": "Controlled demonstration data",
        "environment": "demo",
    }
    return JSONResponse(content=body, headers=headers)


@app.options("/api/health")
async def health_cors_options(request: Request):
    """Permissive preflight options for health endpoint."""
    origin = request.headers.get("origin", "*")
    headers = {
        "Access-Control-Allow-Origin": origin if origin != "*" else "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
    }
    return Response(status_code=200, headers=headers)


@app.get("/api/demo-error")
async def demo_error_endpoint():
    """Controlled information disclosure endpoint.

    Returns a synthetic development-style exception trace with a fake Windows internal path.
    Does NOT expose real system paths, environment variables, or secrets.
    """
    error_payload = {
        "error": "UnhandledDemoException",
        "message": "Simulated debug error in demo environment",
        "file": "C:\\demo\\application\\example.py",
        "line": 42,
        "stack_trace": (
            "Traceback (most recent call last):\n"
            "  File \"C:\\demo\\application\\example.py\", line 42, in handle_demo_request\n"
            "    raise ValueError(\"Synthetic demo disclosure\")"
        ),
    }
    return JSONResponse(status_code=500, content=error_payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9000)
