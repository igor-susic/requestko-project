from starlette.requests import Request
from starlette.responses import JSONResponse

from aiohttp import ClientResponse

SMART_ROUTE = "/api/smart"


def extract_timeout_parameter(request: Request) -> float:
    parameter_key = 'timeout'
    param: int = int(request.query_params[parameter_key])
    timeout: float = param / 1000.0

    return timeout


def does_route_matches(request: Request) -> bool:
    if request.scope["path"] == SMART_ROUTE:
        return True

    return False


def is_content_type_application_json(response: ClientResponse) -> bool:
    if response.headers.get('Content-Type') == JSONResponse.media_type:
        return True

    return False
