from __future__ import annotations

import logging

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.schemas import SchemaGenerator
from starlette.middleware import Middleware
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST

from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from requestko.middleware import PrometheusMiddleware, TimeoutMiddleware
from requestko.requestor import Requestor
from requestko.utils import SMART_ROUTE, extract_timeout_parameter

middleware = [Middleware(PrometheusMiddleware), Middleware(TimeoutMiddleware)]

app = Starlette(debug=True, middleware=middleware)

logger = logging.getLogger("requestko.app")

schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "API documentation for this simple server", "version": "0.1"}}
)

requestor: Requestor


@app.on_event("startup")
def startup():
    global requestor
    logger.info("Application is starting")
    requestor = Requestor()


@app.on_event("shutdown")
def shutdown():
    global requestor
    logger.info("Application is shutting down")
    requestor.close()


@app.route(path=SMART_ROUTE, methods=["GET"])
async def smart_endpoint(request: Request) -> JSONResponse:
    """
    responses:
      200:
        description: Forwards info from Exponea server.
        examples:
          {"time": "124"}
      504:
        description: Terminates if timeout is reached
        examples:
            {"detail": "Error define timeout reached", "timeout": 2, "time_spent": 1.9996373653411865}
      500:
        description: Internal server error happened
      400:
        description: Bad request, client sent request with either invalid or missing query parameter: timeout
    """
    try:
        timeout: float = extract_timeout_parameter(request=request)
    except Exception as e:
        return JSONResponse({'detail': 'You should send integer as query parameter: ?timeout=100'},
                            status_code=HTTP_400_BAD_REQUEST)

    response: dict = await requestor.request_work(timeout=timeout)
    return JSONResponse(content=response)


@app.route(path="/schema", include_in_schema=False)
async def openapi_schema(request: Request) -> Response:
    return schemas.OpenAPIResponse(request=request)


@app.route(path="/metrics", include_in_schema=False)
async def metrics(request: Request) -> Response:
    return Response(generate_latest(REGISTRY), headers={"Content-Type": CONTENT_TYPE_LATEST})


@app.exception_handler(HTTP_404_NOT_FOUND)
async def not_found(request: Request, exc: Exception) -> Response:
    return Response(content="Ooops, not found.", status_code=HTTP_404_NOT_FOUND)


@app.exception_handler(HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_server_error(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(content={'Message': 'Internal server error'}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
