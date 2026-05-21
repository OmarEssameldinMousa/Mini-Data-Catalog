import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


correlation_id_var: ContextVar[str] = ContextVar(
    "correlation_id",
    default="no-correlation-id",
)


def get_correlation_id() -> str:
    """
    Return the current request correlation ID.
    """
    return correlation_id_var.get()


class CorrelationIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        x_correlation_id = request.headers.get(
            "x-correlation-id"
        )

        if not x_correlation_id:
            x_correlation_id = str(uuid.uuid4())

        token = correlation_id_var.set(x_correlation_id)

        try:

            response = await call_next(request)

            response.headers[
                "x-correlation-id"
            ] = x_correlation_id

            return response

        finally:
            correlation_id_var.reset(token)