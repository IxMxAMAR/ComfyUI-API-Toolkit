"""Tests for shared.retry module."""

import pytest
from unittest.mock import patch, MagicMock

from shared.retry import api_request_with_retry
from shared.errors import APITransientError, APIPermanentError


def _make_response(status_code, text="", headers=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.headers = headers or {}
    return resp


class TestApiRequestWithRetry:
    @patch("shared.retry.requests")
    def test_success_on_first_try(self, mock_requests):
        mock_requests.request.return_value = _make_response(200, "ok")
        resp = api_request_with_retry("GET", "http://example.com", service_name="test")
        assert resp.status_code == 200
        assert mock_requests.request.call_count == 1

    @patch("shared.retry.time.sleep")
    @patch("shared.retry.requests")
    def test_retry_on_429(self, mock_requests, mock_sleep):
        mock_requests.request.side_effect = [
            _make_response(429, "rate limited"),
            _make_response(200, "ok"),
        ]
        resp = api_request_with_retry(
            "GET", "http://example.com", service_name="test", base_delay=0.01
        )
        assert resp.status_code == 200
        assert mock_requests.request.call_count == 2
        mock_sleep.assert_called_once()

    @patch("shared.retry.time.sleep")
    @patch("shared.retry.requests")
    def test_max_retries_exhaustion(self, mock_requests, mock_sleep):
        mock_requests.request.return_value = _make_response(500, "server error")
        with pytest.raises(APITransientError) as exc_info:
            api_request_with_retry(
                "GET",
                "http://example.com",
                service_name="test",
                max_retries=2,
                base_delay=0.01,
            )
        assert exc_info.value.status_code == 500
        assert mock_requests.request.call_count == 3  # initial + 2 retries

    @patch("shared.retry.requests")
    def test_no_retry_on_400(self, mock_requests):
        mock_requests.request.return_value = _make_response(400, "bad request")
        with pytest.raises(APIPermanentError) as exc_info:
            api_request_with_retry("GET", "http://example.com", service_name="test")
        assert exc_info.value.status_code == 400
        assert mock_requests.request.call_count == 1

    @patch("shared.retry.time.sleep")
    @patch("shared.retry.requests")
    def test_retry_after_header_honored(self, mock_requests, mock_sleep):
        mock_requests.request.side_effect = [
            _make_response(429, "rate limited", headers={"Retry-After": "5"}),
            _make_response(200, "ok"),
        ]
        resp = api_request_with_retry(
            "GET", "http://example.com", service_name="test", base_delay=1.0
        )
        assert resp.status_code == 200
        # Should sleep for 5 seconds (from Retry-After header), not base_delay
        mock_sleep.assert_called_once_with(5.0)

    @patch("shared.retry.time.sleep")
    @patch("shared.retry.requests")
    def test_uses_session_when_provided(self, mock_requests, mock_sleep):
        session = MagicMock()
        session.request.return_value = _make_response(200, "ok")
        resp = api_request_with_retry(
            "GET", "http://example.com", session=session, service_name="test"
        )
        assert resp.status_code == 200
        session.request.assert_called_once()
        mock_requests.request.assert_not_called()
