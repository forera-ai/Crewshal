"""Verify distinct retained lane files without a Linux mount or loop device."""

import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from crewshal import linux_production as production


class Phase2DLaneProduction(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.parent = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.parent)
        self.contexts = tuple(SimpleNamespace(lane_id=lane) for lane in production.LANE_IDS)
        self.owner = object.__new__(production.OwnedBackingProduction)
        self.owner.reservation = SimpleNamespace(_lane_contexts=self.contexts)
        self.owner._lane_contexts = self.contexts
        self.owner.root = str(self.root)
        self.owner.handles = {"directory": self.parent}
        self.pinned = {}

    def pin(self, name, descriptor):
        self.assertNotIn(name, self.pinned)
        self.assertEqual(os.fstat(descriptor).st_size, 0)
        self.pinned[name] = descriptor
        self.addCleanup(os.close, descriptor)

    def test_fifteen_exclusive_files_pin_before_growth_under_one_original_parent(self):
        channel = SimpleNamespace(transfer=self.pin)
        attached = []

        def attach(name, size, descriptor, actual_channel, control):
            self.assertIs(actual_channel, channel)
            self.assertEqual(control, 70000)
            self.assertIs(self.pinned[name], descriptor)
            self.assertEqual(os.fstat(descriptor).st_size, size)
            attached.append(name)

        with patch.object(self.owner, "_attach_created_loop", side_effect=attach):
            self.owner._create_images(self.owner._sizes(), channel, 70000)
        self.assertEqual(len(self.pinned), 15)
        self.assertEqual(len(attached), 15)
        self.assertEqual(sum(os.fstat(fd).st_size for fd in self.pinned.values()), 503316480)
        self.assertEqual(len({os.fstat(fd).st_ino for fd in self.pinned.values()}), 15)
        self.assertEqual(set(path.name for path in self.root.iterdir()), set(self.pinned))
        for lane in production.LANE_IDS:
            self.assertEqual(
                sum(
                    os.fstat(fd).st_size
                    for name, fd in self.pinned.items()
                    if name.startswith(lane + "--")
                ),
                167772160,
            )
        with self.assertRaises(FileExistsError):
            self.owner._create_images(self.owner._sizes(), channel, 70000)
        self.assertEqual(len(self.pinned), 15)

    def test_failed_growth_retains_both_acquired_files_and_does_not_continue(self):
        truncate = os.ftruncate
        calls = []

        def grow(descriptor, size):
            calls.append((descriptor, size))
            if len(calls) == 2:
                raise OSError("synthetic growth refusal")
            truncate(descriptor, size)

        with (
            patch.object(production.os, "ftruncate", side_effect=grow),
            patch.object(self.owner, "_attach_created_loop") as attach,
            self.assertRaisesRegex(OSError, "growth refusal"),
        ):
            self.owner._create_images(
                self.owner._sizes(), SimpleNamespace(transfer=self.pin), 70000
            )
        self.assertEqual(len(self.pinned), 2)
        attach.assert_called_once()
        self.assertEqual([os.fstat(fd).st_size for fd in self.pinned.values()], [33554432, 0])

    def test_layout_cannot_follow_a_replaced_lane_tuple(self):
        self.owner.reservation._lane_contexts = tuple(
            SimpleNamespace(lane_id=lane) for lane in production.LANE_IDS
        )
        with self.assertRaisesRegex(ValueError, "layout changed"):
            self.owner._sizes()
        self.assertFalse(list(self.root.iterdir()))

    def test_lane_paths_keep_shared_root_and_role_sizes_within_original_domain(self):
        self.assertEqual(production.ROOT_COPY_BYTES, 469762048)
        self.assertEqual(production.PHYSICAL_DOMAIN_BYTES, 1073741824)
        self.assertEqual(production.ROOT_COPY_BYTES + sum(self.owner._sizes().values()), 973078528)
        for lane in production.LANE_IDS:
            self.assertEqual(
                production._view_path("/owned", lane + "--native-auth", "-upper"),
                "/owned/lanes/" + lane + "/native-auth",
            )
            self.assertEqual(
                production._view_path("/owned", lane + "--candidate", "-upper"),
                "/owned/lanes/" + lane + "/candidate-upper",
            )
            self.assertEqual(production._role_uid(lane + "--validator-scratch"), 65531)
            self.assertEqual(
                production._image_geometry_name(lane + "--candidate.img"), "candidate.img"
            )
        for invalid in ("fourth--scratch", "live--../scratch", "live/--scratch", "scratch--live"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                production._view_path("/owned", invalid, "-upper")
