"""Source checks preserve unknown login results and retained failure custody."""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from crewshal.linux_auth import (
    AuthenticationRefusal,
    FrozenAuthenticationPlan,
    OriginalAuthenticationOwner,
    OriginalAuthenticationProc,
)


class AuthenticationCustodyTests(unittest.TestCase):
    def test_credentials_and_routes_cannot_enter_the_metadata_plan(self) -> None:
        original = {"configuration_source": "a" * 64, "account_reference": "b" * 64}
        plan = FrozenAuthenticationPlan.model_validate(original)
        self.assertEqual(plan.native_interface, "stock_device_login_v1")
        for field in ("token", "password", "home", "provider_url", "argv", "environment"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                FrozenAuthenticationPlan.model_validate({**original, field: "extra"})

    def test_reconstructed_process_and_owner_refuse(self) -> None:
        for target in (OriginalAuthenticationOwner, OriginalAuthenticationProc):
            with self.subTest(target=target), self.assertRaises(ValueError):
                target()
            with self.assertRaises(TypeError):
                object.__new__(target).__reduce__()

    def test_stop_failure_preserves_original_unknown_and_child_handle(self) -> None:
        owner = object.__new__(OriginalAuthenticationOwner)
        owner.failed = False
        owner.child = SimpleNamespace(poll=lambda: None)
        owner.group = SimpleNamespace(stop=Mock(side_effect=OSError("stop refused")))
        owner.reservation = SimpleNamespace(_retain_installation_refusal=Mock())
        owner.handles = {"pidfd": 987}
        error = ValueError("original login result unknown")
        with patch(
            "crewshal.linux_auth.signal.pidfd_send_signal",
            create=True,
            side_effect=OSError("signal refused"),
        ) as send:
            with self.assertRaises(AuthenticationRefusal) as refusal:
                owner._refuse(error)
        self.assertIs(refusal.exception.owner, owner)
        self.assertIs(refusal.exception.__cause__, error)
        self.assertTrue(owner.failed)
        owner.reservation._retain_installation_refusal.assert_called_once_with(error)
        send.assert_called_once()
        self.assertEqual(owner.handles, {"pidfd": 987})
        self.assertEqual(len(error.__notes__), 2)

    def test_partial_capture_and_charge_remain_after_refusal(self) -> None:
        owner = object.__new__(OriginalAuthenticationOwner)
        owner.failed = False
        owner.child = None
        owner.handles = {"root": 123}
        owner._buffers = {1: bytearray(b"partial private output")}
        owner.reservation = SimpleNamespace(_retain_installation_refusal=Mock())
        with self.assertRaises(AuthenticationRefusal):
            owner._refuse(ValueError("incomplete"))
        self.assertEqual(owner._buffers[1], b"partial private output")
        self.assertEqual(owner.handles, {"root": 123})
        owner.reservation._retain_installation_refusal.assert_called_once()
