"""Unit tests for _ArsysClient."""

from __future__ import annotations

import base64
import urllib.error
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET

import pytest
from certbot.errors import PluginError

from certbot_dns_arsys._internal.arsys_client import _DEFAULT_API_URL, _ArsysClient


def _make_client(**kwargs: str) -> _ArsysClient:
    defaults = {
        "api_url": _DEFAULT_API_URL,
        "api_login": "example.com",
        "api_key": "secret123",
        "domain": "example.com",
    }
    defaults.update(kwargs)
    return _ArsysClient(**defaults)


def _soap_response(error_code: int = 0, error_msg: str = "") -> bytes:
    """Minimal valid XML SOAP-like response without namespace prefixes."""
    xml = (
        '<?xml version="1.0" encoding="ISO-8859-1"?>'
        "<Envelope>"
        "<Body>"
        "<Response>"
        f"<errorCode>{error_code}</errorCode>"
        f"<errorMsg>{error_msg}</errorMsg>"
        "</Response>"
        "</Body>"
        "</Envelope>"
    )
    return xml.encode("iso-8859-1")


def _urlopen_mock(response_bytes: bytes) -> MagicMock:
    """Return a mock that behaves as a context manager returning itself."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    mock.read = MagicMock(return_value=response_bytes)
    return mock


class TestClientInit:
    def test_valid_credentials_stored(self) -> None:
        client = _make_client()
        assert client.domain == "example.com"
        assert client.api_url == _DEFAULT_API_URL

    def test_empty_api_login_raises(self) -> None:
        with pytest.raises(ValueError, match="api_login"):
            _make_client(api_login="")

    def test_empty_api_key_raises(self) -> None:
        with pytest.raises(ValueError, match="api_key"):
            _make_client(api_key="")

    def test_auth_header_is_base64_basic(self) -> None:
        client = _make_client(api_login="example.com", api_key="secret123")
        expected = base64.b64encode(b"example.com:secret123").decode("ascii")
        assert client._auth_header == f"Basic {expected}"


class TestBuildEnvelope:
    def test_envelope_is_valid_xml(self) -> None:
        client = _make_client()
        payload = client._build_envelope("CreateDNSEntry", dns="_acme-challenge.example.com")
        root = ET.fromstring(payload.decode("iso-8859-1"))
        assert "Envelope" in root.tag

    def test_envelope_contains_operation(self) -> None:
        client = _make_client()
        payload = client._build_envelope("CreateDNSEntry", dns="test")
        assert b"CreateDNSEntry" in payload

    def test_xml_escaping_of_special_chars(self) -> None:
        client = _make_client()
        payload = client._build_envelope("Op", value='a<b>&c"d')
        xml_str = payload.decode("iso-8859-1")
        assert "&lt;" in xml_str
        assert "&gt;" in xml_str
        assert "&amp;" in xml_str

    def test_encoding_is_iso_8859_1(self) -> None:
        client = _make_client()
        payload = client._build_envelope("Op", value="test")
        assert isinstance(payload, bytes)
        assert b"ISO-8859-1" in payload


class TestParseResponse:
    def test_error_code_zero_is_success(self) -> None:
        client = _make_client()
        code = client._parse_response(_soap_response(0), "Op")
        assert code == 0

    def test_non_zero_error_code_raises_plugin_error(self) -> None:
        client = _make_client()
        with pytest.raises(PluginError, match="code 42"):
            client._parse_response(_soap_response(42, "Unauthorized"), "Op")

    def test_error_message_included_in_exception(self) -> None:
        client = _make_client()
        with pytest.raises(PluginError, match="Unauthorized"):
            client._parse_response(_soap_response(42, "Unauthorized"), "Op")

    def test_malformed_xml_raises_plugin_error(self) -> None:
        client = _make_client()
        with pytest.raises(PluginError, match="malformed XML"):
            client._parse_response(b"not xml at all!!!", "Op")


class TestCreateTxtRecord:
    def test_success(self) -> None:
        client = _make_client()
        mock_resp = _urlopen_mock(_soap_response(0))
        with patch("urllib.request.urlopen", return_value=mock_resp):
            client.create_txt_record("_acme-challenge.example.com", "token")

    def test_non_zero_error_code_raises(self) -> None:
        client = _make_client()
        mock_resp = _urlopen_mock(_soap_response(1, "Error"))
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(PluginError, match="code 1"):
                client.create_txt_record("_acme-challenge.example.com", "token")

    def test_http_error_raises_plugin_error(self) -> None:
        client = _make_client()
        http_err = urllib.error.HTTPError(
            url=_DEFAULT_API_URL, code=500, msg="Server Error", hdrs=MagicMock(), fp=None
        )
        with patch("urllib.request.urlopen", side_effect=http_err):
            with pytest.raises(PluginError, match="HTTP error"):
                client.create_txt_record("_acme-challenge.example.com", "token")

    def test_url_error_raises_plugin_error(self) -> None:
        client = _make_client()
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("timed out"),
        ):
            with pytest.raises(PluginError, match="connection error"):
                client.create_txt_record("_acme-challenge.example.com", "token")


class TestDeleteTxtRecord:
    def test_success(self) -> None:
        client = _make_client()
        mock_resp = _urlopen_mock(_soap_response(0))
        with patch("urllib.request.urlopen", return_value=mock_resp):
            client.delete_txt_record("_acme-challenge.example.com", "token")

    def test_not_found_error_code_is_idempotent(self) -> None:
        client = _make_client()
        # 404 is in _NOT_FOUND_CODES — should not raise
        mock_resp = _urlopen_mock(_soap_response(404, "Not Found"))
        with patch("urllib.request.urlopen", return_value=mock_resp):
            client.delete_txt_record("_acme-challenge.example.com", "token")

    def test_other_error_code_raises(self) -> None:
        client = _make_client()
        mock_resp = _urlopen_mock(_soap_response(500, "Internal Error"))
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(PluginError, match="code 500"):
                client.delete_txt_record("_acme-challenge.example.com", "token")

    def test_malformed_response_raises(self) -> None:
        client = _make_client()
        mock_resp = _urlopen_mock(b"bad xml")
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(PluginError, match="malformed XML"):
                client.delete_txt_record("_acme-challenge.example.com", "token")
