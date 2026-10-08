# Fixture-only compatible root-directory read correction to owner-approved v4.
# Exact new vendor attachment only. No global userns setting changes.
abi <abi/4.0>,

profile crewshal-native-bwrap-v1 /{opt/codex/codex-resources/bwrap,var/tmp/crewshal-native-discovery-v1/root/opt/codex/codex-resources/bwrap} flags=(chroot_relative,attach_disconnected) {
  userns,
  capability,
  network,
  mount,
  umount,
  pivot_root,
  signal,
  ptrace,
  / r,
  /** rwklm,
  /** Px -> "crewshal-native-bwrap-v1//&crewshal-native-tool-v1",
}

# Only the trusted new bubblewrap profile enters this payload domain.
# Every subsequent exec inherits it; calling bubblewrap cannot regain setup rights.
profile crewshal-native-tool-v1 flags=(chroot_relative) {
  deny userns,
  deny capability,
  deny mount,
  deny umount,
  deny pivot_root,
  / r,
  /** rm,
  /candidate/owned/ rwkm,
  /candidate/owned/** rwkm,
  /scratch/ rwkm,
  /scratch/** rwkm,
  /dev/null rw,
  /** ix,
  network unix,
  signal (send, receive) peer=crewshal-native-tool-v1,
  signal (receive) peer=unconfined,
  signal (receive) peer=crewshal-native-bwrap-v1,
  ptrace (readby) peer=unconfined,
}
