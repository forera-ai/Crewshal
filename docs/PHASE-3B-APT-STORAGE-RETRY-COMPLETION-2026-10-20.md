# Phase 3B storage-gated APT retrieval completion

Date: 2026-10-20. Entry revision: `bb86c0ad5deca0c63d31fea3b8a9eb93a66a77a1` on `codex/phase1-architecture`.
The owner approved the [exact retry](PHASE-3B-APT-STORAGE-RETRY-PROPOSAL-2026-10-20.md) in this Codex chat.
The [single ledger](PHASE-3B-CAMPAIGN-ADMISSION-MANIFEST-2026-10-19.json) closes this one attempt.

## Environment and preflight

The separate VMware Ubuntu clone used Linux `6.8.0-147-generic aarch64`, four CPUs, and 17,760,563,200 guest memory bytes.
Guest `/var/tmp` had 55,443,779,584 free bytes before retrieval.
The host had 352,587,268 KiB free before network connection, above the 68,719,476,736-byte floor.
The clone used 4,792,052 KiB before retrieval. Its network and sharing were disconnected.
The isolated APT configuration had no effective executable hooks.
`apt-get --print-uris` returned 101 objects, 111,245,650 listed bytes, and an 18,708,214-byte largest object.
The `enp2s0` receive and transmit counters both started at zero.

## One admitted retrieval

The owner confirmed connection of only this clone's adapter at action time.
The one download-only command was:

```sh
sudo env APT_CONFIG=/var/tmp/crewshal-phase3b-apt-nohooks.conf apt-get -y -d -o Acquire::Retries=0 --no-install-recommends install "$@"
```

The command exited zero. APT reported `Fetched 111 MB in 2min 50s (654 kB/s)` and `Download complete and in download only mode`.
The adapter was disconnected immediately after the command. Guest sharing remained disabled.
The final receive counter was 115,742,341 bytes. The final transmit counter was 800,200 bytes.
The conservative new charge is their sum, 116,542,541 bytes, below the 167,772,160-byte cap.
The historical 10,008,484,533-byte charge remains intact. The new cumulative charge is 10,125,027,074 bytes.
This is below the approved 10,176,256,693-byte cumulative ceiling.

Exactly 101 `.deb` files occupy 111,245,650 bytes in the guest APT cache.
The largest file occupies 18,708,214 bytes. The partial cache directory is empty.
A read-only `python3-apt` check matched all 101 package names, versions, and SHA-256 hashes to guest candidate metadata.
It reported `files 101 bad 0`. No package was installed.

## Closure and custody

The clone had 55,382,311,040 free `/var/tmp` bytes after retrieval.
`vmrun -T fusion stop DESTINATION_VMX soft` exited zero. `vmrun list` reported zero running guests.
The clone VMX keeps its adapter disconnected and sharing, clipboard, and drag and drop disabled.
The source guest allocation was 21,875,204,096 bytes. The ISO directory allocation was 3,825,520,640 bytes.
The clone allocation was 5,012,570,112 bytes. Their combined allocation was 30,713,294,848 bytes.
The host had 353,388,589,056 free bytes after shutdown.
All 31 original guest files matched the private custody manifest.
Its SHA-256 is `a7b1408d10f50aaf44e00c28e8ef71953ae3dc7055e83d1f904d49efc6c89dcf`.
Known paid-host and metered API costs were zero.

Four read-only console commands needed correction. An uppercase `CAT` failed.
A `find` command lost its `-maxdepth` value during console entry.
One package check misread labeled `dpkg-deb` output and raised `KeyError`.
A malformed Python console entry ended at `PYTHON#`.
The corrected checks passed. The download command was not retried.

Installation, archived tool execution, Linux qualification, native turns, and evaluation remain closed.
Executable hashes, effective commands, providers, and B1 conformance remain unobserved.
All 192 development rows remain planned. All 576 sealed rows remain unexposed.
The sixteen retained archives, both receipts, both extraction images, the fixed image, and frozen Phase 3A bytes were not changed.
