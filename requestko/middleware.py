import time
import asyncio
import logging

from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_504_GATEWAY_TIMEOUT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from prometheus_client import Histogram, Counter, Gauge

from requestko.utils import does_route_matches, extract_timeout_parameter

logger = logging.getLogger("requestko.middleware")
logger.setLevel(logging.DEBUG)

TOTAL_REQUESTS = Counter(
    "custom_requests_total", "Total count of requests"
)

REQUESTS_PROCESSING_TIME = Histogram(
    "custom_requests_processing_time_seconds",
    "Histogram of requests processing time (in seconds)"
)

FAILED_REQUESTS = Counter(
    "custom_exceptions_total",
    "Total count of exceptions raised with exception type",
    ["exception_type"],
)

REQUESTS_IN_PROGRESS = Gauge(
    "custom_requests_in_progress",
    "Gauge of requests in execution for our smart endpoint"
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if does_route_matches(request=request):

            REQUESTS_IN_PROGRESS.inc()
            TOTAL_REQUESTS.inc()

            try:
                with REQUESTS_PROCESSING_TIME.time():
                    return await call_next(request)
            except Exception as e:
                FAILED_REQUESTS.labels(exception_type=type(e)).inc()
                return JSONResponse(
                    {'detail': 'Internal server error'},
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                REQUESTS_IN_PROGRESS.dec()
        else:
            return await call_next(request)


class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        timeout = None
        start_time = None

        if does_route_matches(request=request):
            try:
                timeout = extract_timeout_parameter(request=request)
            except Exception as e:
                return JSONResponse(
                    {'detail': 'You should send integer as query parameter: ?timeout=100'}, status_code=HTTP_400_BAD_REQUEST)
        try:
            start_time = time.time()
            return await asyncio.wait_for(call_next(request), timeout=timeout)
        except asyncio.TimeoutError:
            spent = time.time() - start_time
            return JSONResponse(
                {'detail': 'Error defined timeout reached', 'timeout': timeout, 'time_spent': spent},
                status_code=HTTP_504_GATEWAY_TIMEOUT)
