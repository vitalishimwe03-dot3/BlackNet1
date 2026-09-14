"""Consistent error responses: {status, code, detail, errors}."""

from rest_framework.views import exception_handler
from rest_framework import status as http_status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(response.data, dict):
        detail = response.data.get("detail", "")

        # SimpleJWT raises 401 with "Given token not valid..." or "No active account" style messages.
        # Normalize into compact codes without leaking internals.
        if response.status_code == http_status.HTTP_401_UNAUTHORIZED:
            detail = detail or "AUTHENTICATION_REQUIRED"

        message_map = {
            "No active account found with the given credentials": "INVALID_CREDENTIALS",
            "Given token not valid for any token type": "INVALID_TOKEN",
            "Token is invalid or expired": "INVALID_TOKEN",
            "User is inactive": "ACCOUNT_SUSPENDED",
            "AUTHENTICATION_REQUIRED": "AUTHENTICATION_REQUIRED",
            "You do not have permission to perform this action.": "PERMISSION_DENIED",
            "NotFound": "NOT_FOUND",
        }
        code = message_map.get(detail, str(response.status_code))

        return_response = {
            "status": response.status_code,
            "code": code,
            "detail": detail,
            "errors": {k: v for k, v in response.data.items() if k != "detail"},
        }
        response.data = return_response
    return response