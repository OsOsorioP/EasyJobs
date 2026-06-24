import httpx
from fastapi import Request, Response

EXCLUDED_HEADERS = {"host", "content-length", "connection"}

async def forward_request(request: Request, target_base_url: str, target_path: str) -> Response:
    headers = {k: v for k, v in request.headers.items() if k.lower() not in EXCLUDED_HEADERS}

    correlation_id = getattr(request.state, "correlation_id", None)
    if correlation_id:
        headers["x-correlation-id"] = correlation_id

    body = await request.body()
    
    client: httpx.AsyncClient = request.app.state.http_client

    upstream_response = await client.request(
        method=request.method,
        url=f"{target_base_url}{target_path}",
        headers=headers,
        params=request.query_params,
        content=body,
    )

    response_headers = {
        k: v for k, v in upstream_response.headers.items() if k.lower() not in EXCLUDED_HEADERS
    }

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )