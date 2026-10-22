from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError, PermissionDenied, NotAuthenticated, NotFound, APIException,
)

def custom_exception_handler(exc, context):
    # Validation error - field errors
    if isinstance(exc, ValidationError):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "invalid",
                    "message": "Validation failed.",
                    "details": exc.detail,
                },
            },
            status=400,
        )
    
    # Permission denied - 403
    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "error": {"code": "permission_denied", "message": str(exc.detail)},
            },
            status=403,
        )
    
    # Not authenticated - 401
    if isinstance(exc, NotAuthenticated):
        return Response(
            {
                "success": False,
                "error": {"code": "not_authenticated", "message": str(exc.detail)},
            },
            status=401,
        )
    
    # Not found - 404
    if isinstance(exc, NotFound):
        return Response(
            {
                "success": False,
                "error": {"code": "not_found", "message": str(exc.detail)},
            },
            status=404,
        )
    
    # Any other APIException - use its status + code
    if isinstance(exc, APIException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": getattr(exc, "default_code", "error"),
                    "message": str(exc.detail),
                },
            },
            status=exc.status_code,
        )
    
    # Unknown  let Django return 500
    return None