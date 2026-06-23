"""Arsys SOAP DNS API client."""

from __future__ import annotations

import base64
import logging
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html import escape as xml_escape

from certbot.errors import PluginError

logger = logging.getLogger(__name__)

_DEFAULT_API_URL = "https://api.servidoresdns.net:54321/hosting/api/soap/index.php"

_SOAP_ENVELOPE = (
    '<?xml version="1.0" encoding="ISO-8859-1"?>'
    '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"'
    ' xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"'
    ' xmlns:xsd="http://www.w3.org/1999/XMLSchema">'
    "<soap:Body>"
    '<{op} xmlns="{op}"><input>{params}</input></{op}>'
    "</soap:Body></soap:Envelope>"
)

# Error codes returned by the Arsys API that indicate "record not found"
# during a delete — treated as success for idempotency.
_NOT_FOUND_CODES = {404, 1002, 1004}

_TIMEOUT_SECONDS = 30


class _ArsysClient:
    """Lightweight SOAP client for the Arsys Hosting DNS API."""

    def __init__(
        self,
        api_url: str,
        api_login: str,
        api_key: str,
        domain: str,
    ) -> None:
        if not api_login:
            raise ValueError("api_login must not be empty")
        if not api_key:
            raise ValueError("api_key must not be empty")

        self.api_url = api_url or _DEFAULT_API_URL
        self.domain = domain
        creds = f"{api_login}:{api_key}".encode()
        self._auth_header = f"Basic {base64.b64encode(creds).decode('ascii')}"

    def _build_envelope(self, operation: str, **params: str) -> bytes:
        param_xml = "".join(
            f'<{k} xsi:type="xsd:string">{xml_escape(v)}</{k}>' for k, v in params.items()
        )
        body = _SOAP_ENVELOPE.format(op=operation, params=param_xml)
        return body.encode("iso-8859-1")

    def _call(self, operation: str, **params: str) -> bytes:
        payload = self._build_envelope(operation, **params)
        req = urllib.request.Request(
            self.api_url,
            data=payload,
            headers={
                "Content-Type": "text/xml; charset=ISO-8859-1",
                "SOAPAction": operation,
                "Authorization": self._auth_header,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
                return bytes(resp.read())
        except urllib.error.HTTPError as exc:
            raise PluginError(
                f"Arsys API HTTP error during {operation}: {exc.code} {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise PluginError(
                f"Arsys API connection error during {operation}: {exc.reason}"
            ) from exc

    def _parse_response(self, xml_bytes: bytes, operation: str) -> int:
        try:
            root = ET.fromstring(xml_bytes.decode("iso-8859-1"))
        except ET.ParseError as exc:
            raise PluginError(
                f"Arsys API returned malformed XML during {operation}: {exc}"
            ) from exc

        code_el = root.find(".//{*}errorCode")
        msg_el = root.find(".//{*}errorMsg")
        code = int(code_el.text or "0") if code_el is not None else 0
        msg = (msg_el.text or "") if msg_el is not None else ""

        if code != 0:
            raise PluginError(f"Arsys API error during {operation} (code {code}): {msg}")
        return code

    def create_txt_record(self, name: str, value: str) -> None:
        logger.debug("Creating TXT record: %s = %r", name, value)
        xml_bytes = self._call(
            "CreateDNSEntry",
            dns=name,
            domain=self.domain,
            type="TXT",
            value=value,
        )
        self._parse_response(xml_bytes, "CreateDNSEntry")
        logger.info("Created TXT record %s", name)

    def delete_txt_record(self, name: str, value: str) -> None:
        logger.debug("Deleting TXT record: %s", name)
        try:
            xml_bytes = self._call(
                "DeleteDNSEntry",
                dns=name,
                domain=self.domain,
                type="TXT",
                value=value,
            )
            self._parse_response(xml_bytes, "DeleteDNSEntry")
        except PluginError as exc:
            msg = str(exc)
            for code in _NOT_FOUND_CODES:
                if f"code {code}" in msg:
                    logger.warning(
                        "TXT record %s not found during cleanup (idempotent): %s",
                        name,
                        msg,
                    )
                    return
            raise
        logger.info("Deleted TXT record %s", name)
