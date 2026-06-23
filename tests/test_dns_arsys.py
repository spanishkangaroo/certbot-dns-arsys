"""Unit tests for the Authenticator and propagation poller."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from certbot.errors import PluginError

from certbot_dns_arsys._internal.dns_arsys import Authenticator, _wait_for_propagation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_authenticator(
    api_login: str = "example.com",
    api_key: str = "secret123",
    domain: str = "example.com",
    api_url: str = "",
) -> Authenticator:
    creds: dict[str, str] = {
        "api_login": api_login,
        "api_key": api_key,
        "domain": domain,
        "api_url": api_url,
    }
    auth = Authenticator(config=MagicMock(), name="dns-arsys")
    mock_creds = MagicMock()
    mock_creds.conf.side_effect = lambda key: creds.get(key, "")
    auth.credentials = mock_creds
    return auth


# ---------------------------------------------------------------------------
# Authenticator — credential loading / client factory
# ---------------------------------------------------------------------------


class TestAuthenticatorCredentials:
    def test_get_arsys_client_uses_credentials(self) -> None:
        auth = _make_authenticator()
        with patch("certbot_dns_arsys._internal.dns_arsys._ArsysClient") as mock_cls:
            auth._get_arsys_client()
            mock_cls.assert_called_once()
            kwargs = mock_cls.call_args[1]
            assert kwargs["api_login"] == "example.com"
            assert kwargs["api_key"] == "secret123"
            assert kwargs["domain"] == "example.com"

    def test_default_api_url_applied_when_absent(self) -> None:
        from certbot_dns_arsys._internal.arsys_client import _DEFAULT_API_URL

        auth = _make_authenticator(api_url="")
        with patch("certbot_dns_arsys._internal.dns_arsys._ArsysClient") as mock_cls:
            auth._get_arsys_client()
            kwargs = mock_cls.call_args[1]
            assert kwargs["api_url"] == _DEFAULT_API_URL

    def test_custom_api_url_used_when_provided(self) -> None:
        custom_url = "https://custom.example.com/soap"
        auth = _make_authenticator(api_url=custom_url)
        with patch("certbot_dns_arsys._internal.dns_arsys._ArsysClient") as mock_cls:
            auth._get_arsys_client()
            kwargs = mock_cls.call_args[1]
            assert kwargs["api_url"] == custom_url


# ---------------------------------------------------------------------------
# _perform
# ---------------------------------------------------------------------------


class TestPerform:
    def test_perform_standard_domain(self) -> None:
        auth = _make_authenticator()
        with (
            patch.object(auth, "_get_arsys_client") as mock_get,
            patch("certbot_dns_arsys._internal.dns_arsys._wait_for_propagation"),
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            auth._perform("example.com", "_acme-challenge.example.com", "tok")
            mock_client.create_txt_record.assert_called_once_with(
                "_acme-challenge.example.com", "tok"
            )

    def test_perform_subdomain(self) -> None:
        auth = _make_authenticator()
        with (
            patch.object(auth, "_get_arsys_client") as mock_get,
            patch("certbot_dns_arsys._internal.dns_arsys._wait_for_propagation"),
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            auth._perform("sub.example.com", "_acme-challenge.sub.example.com", "tok")
            mock_client.create_txt_record.assert_called_once_with(
                "_acme-challenge.sub.example.com", "tok"
            )

    def test_perform_calls_wait_for_propagation(self) -> None:
        auth = _make_authenticator()
        auth.conf = MagicMock(return_value=180)
        with (
            patch.object(auth, "_get_arsys_client") as mock_get,
            patch("certbot_dns_arsys._internal.dns_arsys._wait_for_propagation") as mock_wait,
        ):
            mock_get.return_value = MagicMock()
            auth._perform("example.com", "_acme-challenge.example.com", "tok")
            mock_wait.assert_called_once()
            _, _, timeout = mock_wait.call_args[0]
            assert timeout == 180


# ---------------------------------------------------------------------------
# _cleanup
# ---------------------------------------------------------------------------


class TestCleanup:
    def test_cleanup_calls_delete(self) -> None:
        auth = _make_authenticator()
        with patch.object(auth, "_get_arsys_client") as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            auth._cleanup("example.com", "_acme-challenge.example.com", "tok")
            mock_client.delete_txt_record.assert_called_once_with(
                "_acme-challenge.example.com", "tok"
            )

    def test_cleanup_suppresses_plugin_error(self) -> None:
        auth = _make_authenticator()
        with patch.object(auth, "_get_arsys_client") as mock_get:
            mock_client = MagicMock()
            mock_client.delete_txt_record.side_effect = PluginError("oops")
            mock_get.return_value = mock_client
            # Must not raise
            auth._cleanup("example.com", "_acme-challenge.example.com", "tok")


# ---------------------------------------------------------------------------
# _wait_for_propagation
# ---------------------------------------------------------------------------


class TestWaitForPropagation:
    def test_returns_immediately_when_value_found(self) -> None:
        mock_rdata = MagicMock()
        mock_rdata.strings = [b"expected_token"]

        with patch("certbot_dns_arsys._internal.dns_arsys._authoritative_resolver") as mock_res:
            resolver = MagicMock()
            resolver.resolve.return_value = [mock_rdata]
            mock_res.return_value = resolver
            with patch("certbot_dns_arsys._internal.dns_arsys.time") as mock_time:
                mock_time.time.return_value = 0.0
                mock_time.sleep = MagicMock()
                _wait_for_propagation("_acme-challenge.example.com", "expected_token", 120)
            resolver.resolve.assert_called_once()

    def test_multiple_txt_values_matches_correctly(self) -> None:
        mock_rdata = MagicMock()
        mock_rdata.strings = [b"other_token", b"expected_token"]

        with patch("certbot_dns_arsys._internal.dns_arsys._authoritative_resolver") as mock_res:
            resolver = MagicMock()
            resolver.resolve.return_value = [mock_rdata]
            mock_res.return_value = resolver
            with patch("certbot_dns_arsys._internal.dns_arsys.time") as mock_time:
                mock_time.time.return_value = 0.0
                mock_time.sleep = MagicMock()
                _wait_for_propagation("_acme-challenge.example.com", "expected_token", 120)

    def test_logs_warning_on_timeout(self) -> None:
        with patch("certbot_dns_arsys._internal.dns_arsys._authoritative_resolver") as mock_res:
            resolver = MagicMock()
            resolver.resolve.side_effect = Exception("NXDOMAIN")
            mock_res.return_value = resolver
            with (
                patch("certbot_dns_arsys._internal.dns_arsys.time") as mock_time,
                patch("certbot_dns_arsys._internal.dns_arsys.logger") as mock_logger,
            ):
                # deadline = 0 + 0 = 0, while time.time() < 0 is immediately False
                mock_time.time.return_value = 0.0
                mock_time.sleep = MagicMock()
                _wait_for_propagation("_acme-challenge.example.com", "tok", 0)
                mock_logger.warning.assert_called()

    def test_falls_back_to_sleep_when_dnspython_missing(self) -> None:
        """When dns.resolver is not found, fall back to a plain sleep."""
        with (
            patch(
                "certbot_dns_arsys._internal.dns_arsys.importlib.util.find_spec",
                return_value=None,
            ),
            patch("certbot_dns_arsys._internal.dns_arsys.time") as mock_time,
        ):
            mock_time.sleep = MagicMock()
            _wait_for_propagation("_acme-challenge.example.com", "tok", 30)
            mock_time.sleep.assert_called_once_with(30)
