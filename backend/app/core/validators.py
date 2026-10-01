from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow requests with no Content-Length (but upload endpoint still validates chunk size)
        content_length_str = request.headers.get("content-length")
        
        if content_length_str:
            try:
                content_length = int(content_length_str)
                max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
                
                if content_length > max_bytes:
                    logger.warning(f"Request rejected due to size: {content_length} bytes > {max_bytes} bytes")
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "code": "FILE_TOO_LARGE",
                                "message": "Maximum upload size exceeded"
                            }
                        }
                    )
            except ValueError:
                # If content-length is completely malformed, we can either ignore it or reject it.
                # The prompt states: "Handle malformed Content-Length safely. Never crash because of an invalid header."
                pass
                
        return await call_next(request)
