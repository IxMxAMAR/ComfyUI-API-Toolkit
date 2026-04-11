"""Tests for shared.errors module."""

import json
import pytest

from shared.errors import (
    APIError,
    APITransientError,
    APIPermanentError,
    APIQuotaError,
    parse_error_response,
)


class TestErrorHierarchy:
    def test_api_error_is_runtime_error(self):
        assert issubclass(APIError, RuntimeError)

    def test_transient_is_api_error(self):
        assert issubclass(APITransientError, APIError)

    def test_permanent_is_api_error(self):
        assert issubclass(APIPermanentError, APIError)

    def test_quota_is_permanent(self):
        assert issubclass(APIQuotaError, APIPermanentError)

    def test_error_attributes(self):
        err = APIError("kling", 500, "server error")
        assert err.service == "kling"
        assert err.status_code == 500
        assert err.detail == "server error"
        assert "kling" in str(err)
        assert "500" in str(err)


class TestParseErrorResponse:
    def test_elevenlabs_json(self):
        body = json.dumps({"detail": {"status": "error", "message": "Invalid API key"}})
        err = parse_error_response("elevenlabs", 401, body)
        assert isinstance(err, APIPermanentError)
        assert err.detail == "Invalid API key"
        assert err.status_code == 401

    def test_kling_json(self):
        body = json.dumps({"code": 1001, "message": "Token expired"})
        err = parse_error_response("kling", 401, body)
        assert isinstance(err, APIPermanentError)
        assert err.detail == "Token expired"

    def test_plain_text(self):
        err = parse_error_response("gemini", 400, "Bad request body")
        assert isinstance(err, APIPermanentError)
        assert err.detail == "Bad request body"

    def test_truncation(self):
        long_body = "x" * 500
        err = parse_error_response("test", 400, long_body)
        assert len(err.detail) <= 304  # 300 + "..."
        assert err.detail.endswith("...")

    def test_transient_on_429(self):
        err = parse_error_response("test", 429, "rate limited")
        assert isinstance(err, APITransientError)

    def test_transient_on_500(self):
        err = parse_error_response("test", 500, "internal error")
        assert isinstance(err, APITransientError)

    def test_quota_error(self):
        body = json.dumps({"detail": {"status": "error", "message": "quota exhausted"}})
        err = parse_error_response("elevenlabs", 402, body)
        assert isinstance(err, APIQuotaError)

    def test_elevenlabs_detail_string(self):
        body = json.dumps({"detail": "Simple error message"})
        err = parse_error_response("elevenlabs", 400, body)
        assert err.detail == "Simple error message"
