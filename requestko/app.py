from __future__ import annotations

import os
import logging

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.schemas import SchemaGenerator
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from requestko.middleware import PrometheusMiddleware
from requestko.requestor import Requestor

os.environ.setdefault("PYTHONASYNCIODEBUG", "1")

app = Starlette(debug=True)
app.add_middleware(middleware_class=PrometheusMiddleware)


logger = logging.getLogger("requestko.app")
logger.setLevel(logging.DEBUG)

schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "API documentation for this simple server", "version": "0.1"}}
)

SMART_ROUTE = "/api/smart"
requestor: Requestor


@app.on_event("startup")
def startup():
    global requestor
    logger.info("Application is starting")
    requestor = Requestor()


@app.route(path=SMART_ROUTE, methods=["GET"])
async def smart_endpoint(request: Request) -> JSONResponse:
    """
    responses:
      200:
        description: A list of users.
        examples:
          [{"username": "tom"}, {"username": "lucy"}]
    """
    response: dict = await requestor.request_work()
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

