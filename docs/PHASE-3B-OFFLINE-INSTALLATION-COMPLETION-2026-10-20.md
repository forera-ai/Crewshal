# Phase 3B offline package installation completion

Date: 2026-10-20. Entry revision: `95adfe4` on `codex/phase1-architecture`.
Status: The approved resume and one offline installation completed. This admission is closed.
Host environment: macOS 27.2 arm64, Python 3.12.15, RTK 0.51.0, and local VMware Fusion.

The owner approved the [exact resume proposal](PHASE-3B-OFFLINE-INSTALLATION-RESUME-PROPOSAL-2026-10-20.md).
The separate Ubuntu arm64 clone resumed at `2026-10-20T19:17:47Z`.
The clone had four CPUs, 17,408 MiB configured memory, and a disconnected network adapter.
VMware sharing, clipboard, and drag-and-drop remained disabled.
The guest reported `Linux 6.8.0-147-generic aarch64`, four CPUs, and 17,760,563,200 memory bytes.
The guest had 55,306,911,744 free `/var/tmp` bytes before installation.

## Exact commands and results

The agent used the VMware console for guest commands.
The owner signed in locally. Credentials did not enter commands or files.

```sh
uname -srm; getconf _NPROCESSORS_ONLN; free -b; df -B1 /var/tmp
cat /var/tmp/crewshal-phase3b-apt-nohooks.conf; ls -A /var/tmp/crewshal-phase3b-empty-aptconf.d
APT_CONFIG=/var/tmp/crewshal-phase3b-apt-nohooks.conf apt-config dump | grep -Ei 'invoke|hooks'; echo grep_exit=$?
sudo python3 -c 'import glob,os; f=glob.glob("/var/cache/apt/archives/*.deb"); print(len(f),sum(os.path.getsize(x) for x in f),len(os.listdir("/var/cache/apt/archives/partial")))'
```

The isolated APT configuration retained its two recorded lines and empty parts directory.
The hook search returned `grep_exit=1` and no effective hook.
The cache contained 101 packages, 111,245,650 bytes, and zero partial entries.
A read-only Python check compared every cached name, version, and SHA-256 with APT candidate metadata.
It returned `files 101 bad 0`.
The first unprivileged cache count hit `PermissionError` on the `partial` directory.
The privileged read-only count succeeded. No installation command had run at that point.

The agent set the thirty names from the [original installation proposal](PHASE-3B-OFFLINE-PACKAGE-INSTALLATION-PROPOSAL-2026-10-20.md).
The isolated `apt-get -s --no-download --no-install-recommends install "$@"` returned exit zero.
It selected 101 package objects: 100 new and one upgrade.
It selected zero removals and made no download request.
The agent then issued the approved command once:

```sh
sudo env APT_CONFIG=/var/tmp/crewshal-phase3b-apt-nohooks.conf apt-get -y --no-download -o Acquire::Retries=0 --no-install-recommends install "$@"
```

APT returned exit zero. Its terminal output ended after package setup and trigger processing.
`dpkg --audit` produced no output.
The guest record `/var/tmp/crewshal-phase3b-installed-package-versions-20261020.txt` contains all 101 names and installed versions.
It has 2,990 bytes. A comparison with the cached package metadata found zero version mismatches.
The guest had 54,882,734,080 free `/var/tmp` bytes after installation.
The guest file and APT logs remain in the retained clone.

## Closure and limits

The agent soft-stopped the clone. `vmrun list` then reported zero running guests.
The VMX retained four CPUs, 17,408 MiB, `ethernet0.startConnected = "FALSE"`, and disabled sharing controls.
The final clone allocation was 5,509,558,272 bytes, below its 34,359,738,368-byte cap.
The original guest, ISO, and clone together used 31,210,283,008 bytes, below 68,719,476,736.
The host had 833,549,340,672 free bytes, above its 68,719,476,736-byte floor.
All 31 original guest files matched the private custody manifest after shutdown.
The saved-state resume and installation finished within the two-hour active and four-hour elapsed limits.

The installation used zero new network transfer, paid-host cost, or metered API cost.
The historical archive charge remains 10,008,484,533 bytes.
The package retrieval charge remains 116,542,541 bytes.
The cumulative conservative charge remains 10,125,027,074 bytes.
Both receipt histories, all sixteen archives, both extraction images, the fixed image, and frozen Phase 3A bytes remain intact.

The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes this resume and installation.
Archived tool execution, Linux qualification, native turns, and evaluation remain closed.
Executable hashes, effective commands, providers, and B1 conformance remain unknown.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
