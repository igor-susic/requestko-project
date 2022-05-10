import time
import asyncio
import logging

from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_504_GATEWAY_TIMEOUT
from prometheus_client import Histogram, Counter, Gauge

from requestko.utils import does_route_matches, extract_timeout_parameter

logger = logging.getLogger("requestko.middleware")
logger.setLevel(logging.DEBUG)

TOTAL_REQUESTS = Counter(
    "custom_requests_total", "Total count of requests."
)

REQUESTS_PROCESSING_TIME = Histogram(
    "custom_requests_processing_time_seconds",
    "Histogram of requests processing time by path (in seconds)"
)
FAILED_REQUESTS = Counter(
    "custom_exceptions_total",
    "Total count of exceptions raised by path and exception type",
    ["exception_type"],
)
REQUESTS_IN_PROGRESS = Gauge(
    "custom_requests_in_progress",
    "Gauge of requests in exection for our smart endpoint"
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if does_route_matches(request=request):

            REQUESTS_IN_PROGRESS.inc()
            TOTAL_REQUESTS.inc()

            try:
                with REQUESTS_PROCESSING_TIME.time():
                    response = await call_next(request)
                return response
            except Exception as e:
                FAILED_REQUESTS.labels(exception_type=type(e)).inc()
                raise HTTPException(500, str(e))
            finally:
                REQUESTS_IN_PROGRESS.dec()
        else:
            response = await call_next(request)
            return response


class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        timeout = None
        start_time = None

        if does_route_matches(request=request):
            timeout = extract_timeout_parameter(request=request)
        try:
            start_time = time.time()
            return await asyncio.wait_for(call_next(request), timeout=timeout)
        except asyncio.TimeoutError:
            spent = time.time() - start_time
            return JSONResponse(
                {'detail': 'Error define timeout reached', 'timeout': timeout, 'time_spent': spent},
                status_code=HTTP_504_GATEWAY_TIMEOUT)
