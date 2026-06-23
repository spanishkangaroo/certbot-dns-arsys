"""Unit tests for _authoritative_resolver."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from certbot_dns_arsys._internal.dns_arsys import _authoritative_resolver


def _ns_rr(name: str) -> MagicMock:
    rr = MagicMock()
    rr.__str__ = lambda s: name
    return rr


def _a_rr(ip: str) -> MagicMock:
    rr = MagicMock()
    rr.__str__ = lambda s: ip
    return rr


class TestAuthoritativeResolver:
    def test_public_ns_ips_used_as_nameservers(self) -> None:
        with (
            patch("dns.resolver.resolve") as mock_resolve,
            patch("dns.resolver.Resolver") as mock_cls,
        ):
            mock_resolve.side_effect = [
                [_ns_rr("ns1.example.com")],  # NS lookup
                [_a_rr("8.8.8.8")],  # A lookup for ns1
            ]
            resolver_inst = MagicMock()
            resolver_inst.nameservers = ["127.0.0.1"]
            mock_cls.return_value = resolver_inst

            _authoritative_resolver("_acme-challenge.example.com")
            assert resolver_inst.nameservers == ["8.8.8.8"]

    def test_private_ns_ips_fall_back_to_system_resolver(self) -> None:
        with (
            patch("dns.resolver.resolve") as mock_resolve,
            patch("dns.resolver.Resolver") as mock_cls,
        ):
            mock_resolve.side_effect = [
                [_ns_rr("ns1.example.com")],
                [_a_rr("192.168.1.1")],  # private — filtered out
            ]
            resolver_inst = MagicMock()
            original_ns = ["10.0.0.1"]
            resolver_inst.nameservers = list(original_ns)
            mock_cls.return_value = resolver_inst

            _authoritative_resolver("_acme-challenge.example.com")
            # nameservers should remain the original system resolver list
            assert resolver_inst.nameservers == original_ns

    def test_ns_resolution_failure_falls_back_to_system_resolver(self) -> None:
        with (
            patch("dns.resolver.resolve", side_effect=Exception("SERVFAIL")),
            patch("dns.resolver.Resolver") as mock_cls,
        ):
            resolver_inst = MagicMock()
            original_ns = ["10.0.0.1"]
            resolver_inst.nameservers = list(original_ns)
            mock_cls.return_value = resolver_inst

            _authoritative_resolver("_acme-challenge.example.com")
            assert resolver_inst.nameservers == original_ns

    def test_mixed_public_and_private_ips(self) -> None:
        """Only public IPs are kept when both private and public NS IPs exist."""
        with (
            patch("dns.resolver.resolve") as mock_resolve,
            patch("dns.resolver.Resolver") as mock_cls,
        ):
            mock_resolve.side_effect = [
                [_ns_rr("ns1.example.com"), _ns_rr("ns2.example.com")],
                [_a_rr("192.168.1.1")],  # private for ns1
                [_a_rr("1.2.3.4")],  # public for ns2
            ]
            resolver_inst = MagicMock()
            resolver_inst.nameservers = ["127.0.0.1"]
            mock_cls.return_value = resolver_inst

            _authoritative_resolver("_acme-challenge.example.com")
            assert resolver_inst.nameservers == ["1.2.3.4"]
