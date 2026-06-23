"""Certbot DNS authenticator for Arsys."""

from __future__ import annotations

import importlib.util
import ipaddress
import logging
import time
from typing import Any

from certbot import errors
from certbot.plugins import dns_common

from certbot_dns_arsys._internal.arsys_client import _DEFAULT_API_URL, _ArsysClient

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 15  # seconds between DNS propagation checks


def _authoritative_resolver(record_name: str) -> Any:
    """Return a dnspython resolver pointed at authoritative NS for the zone.

    Falls back to the system resolver when NS IPs are all private
    (Arsys internal infrastructure) or when NS lookup fails entirely.
    """
    import dns.resolver  # noqa: PLC0415

    resolver = dns.resolver.Resolver()
    resolver.timeout = 10
    resolver.lifetime = 10

    try:
        zone = ".".join(record_name.split(".")[-2:])
        public_ns_ips: list[str] = []
        for ns_rr in dns.resolver.resolve(zone, "NS"):
            try:
                for a_rr in dns.resolver.resolve(str(ns_rr), "A"):
                    addr = str(a_rr)
                    if not ipaddress.ip_address(addr).is_private:
                        public_ns_ips.append(addr)
            except Exception:
                pass
        if public_ns_ips:
            logger.info("Using authoritative nameservers: %s", public_ns_ips)
            resolver.nameservers = public_ns_ips
        else:
            logger.info(
                "Authoritative NS IPs are private/unreachable; falling back to system resolver: %s",
                resolver.nameservers,
            )
    except Exception as exc:
        logger.warning(
            "NS lookup failed (%s); using system resolver: %s",
            exc,
            resolver.nameservers,
        )

    return resolver


def _wait_for_propagation(record_name: str, value: str, timeout: int) -> None:
    """Poll DNS until the TXT record with the expected value is visible."""
    if importlib.util.find_spec("dns.resolver") is None:
        logger.warning(
            "dnspython is not installed; sleeping %ds. "
            "Install dnspython for smarter propagation polling.",
            timeout,
        )
        time.sleep(timeout)
        return

    resolver = _authoritative_resolver(record_name)
    deadline = time.time() + timeout
    start = time.time()
    logger.info("Polling DNS for %s (max %ds)...", record_name, timeout)

    while time.time() < deadline:
        try:
            answers = resolver.resolve(record_name, "TXT")
            found = [
                txt.decode("utf-8") if isinstance(txt, bytes) else txt
                for rdata in answers
                for txt in rdata.strings
            ]
            elapsed = int(time.time() - start)
            logger.info("DNS poll at ~%ds: found TXT values %s", elapsed, found)
            if value in found:
                logger.info("TXT record verified in DNS after ~%ds", elapsed)
                return
        except Exception as exc:
            elapsed = int(time.time() - start)
            logger.info("DNS poll at ~%ds: %s: %s", elapsed, type(exc).__name__, exc)

        time.sleep(_POLL_INTERVAL)

    logger.warning(
        "TXT record %s not confirmed in DNS after %ds "
        "(resolver may not be authoritative for this zone); proceeding.",
        record_name,
        timeout,
    )


class Authenticator(dns_common.DNSAuthenticator):
    """Certbot DNS authenticator for Arsys.

    Creates and removes _acme-challenge TXT records via the Arsys
    Hosting SOAP API to fulfil the DNS-01 challenge.
    """

    description = "Obtain certificates using a DNS TXT record (for Arsys domains)"
    ttl = 60

    @classmethod
    def add_parser_arguments(
        cls,
        add: Any,
        default_propagation_seconds: int = 30,
    ) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add(
            "credentials",
            help="Path to the Arsys credentials INI file.",
        )

    def more_info(self) -> str:
        return (
            "This plugin automates the DNS-01 challenge by creating and "
            "removing TXT records in Arsys DNS via the Arsys Hosting SOAP API."
        )

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "Arsys credentials INI file",
            {
                "api_login": "Arsys API login (your domain, e.g. example.com)",
                "api_key": "Arsys API key",
                "domain": "Base domain managed in your Arsys account",
            },
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        client = self._get_arsys_client()
        record_name = f"_acme-challenge.{domain}"
        client.create_txt_record(record_name, validation)
        propagation_seconds = self.conf("propagation-seconds")
        _wait_for_propagation(record_name, validation, propagation_seconds)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        client = self._get_arsys_client()
        record_name = f"_acme-challenge.{domain}"
        try:
            client.delete_txt_record(record_name, validation)
        except errors.PluginError as exc:
            logger.warning(
                "Failed to delete TXT record %s during cleanup: %s",
                record_name,
                exc,
            )

    def _get_arsys_client(self) -> _ArsysClient:
        api_url = self.credentials.conf("api_url") or _DEFAULT_API_URL
        return _ArsysClient(
            api_url=api_url,
            api_login=self.credentials.conf("api_login") or "",
            api_key=self.credentials.conf("api_key") or "",
            domain=self.credentials.conf("domain") or "",
        )
