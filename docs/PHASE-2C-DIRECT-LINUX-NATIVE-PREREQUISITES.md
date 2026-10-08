# Direct Linux native and proxy prerequisites

Date: 2026-10-06. Status: **public metadata prepared; bounded deliberate fixture acquisition authorized by existing owner scope**. This is the next finite step of owner-approved ADR 0003 after the [kernel mechanism observations](PHASE-2C-DIRECT-LINUX-ASSESSMENT.md). It is not a native qualification manifest or permission for a provider call.

The current guest system paths have no observed Codex, Claude, nginx, mitmproxy, squid or haproxy executable. This is a bounded path lookup, not an exhaustive installation search. Existing curl, git, Node/npm and the kernel helpers are available. Do not search credentials or reuse ambient CLI configuration.

## Concrete acquisition decision

An acquisition question was initially sent but its interpretation was too broad. ADR 0003 forbids automatic downloads by the native runtime; deliberate, byte-pinned preparation of official test artifacts is within the owner-approved bounded feasibility work. The unanswered question is not treated as approval or as an additional binding gate. Supplied binaries remain an optional preference. Runtime downloads, installers, live provider calls and paid services remain prohibited.

The public host CLI path identifies version 0.160.1 without executing it. The official [release API](https://api.github.com/repos/openai/codex/releases/tags/rust-v0.160.1) reports a non-draft, non-prerelease tag. Relevant immutable artifact choices:

| Artifact | Compressed bytes | Publisher API SHA-256 |
|---|---:|---|
| `codex-aarch64-unknown-linux-musl.tar.gz` | 101633470 | `f54dc5852042445bf41da3aa31156f3cb02f52c5a1a04074de73dc5598f7e1f7` |
| `bwrap-aarch64-unknown-linux-musl.tar.gz` | 254885 | `5b2600ab05250bdf8b8b34f5dd8a8b543c941d2ad36a5213dfa93ad04d1a2bbd` |
| `codex-responses-api-proxy-aarch64-unknown-linux-musl.tar.gz` | 5023982 | `75bcef0603b51ffca62877cc9368cf1937b8d4799e1367c33dc6963633f0d431` |

The full `codex-package-aarch64-unknown-linux-musl.tar.gz` bundle (150931915 bytes, SHA-256 `dff0954438fa455c2197ddb1f421d8d68625d98de610f76bedb6e5bc837ea35b`) and the responses proxy archive were deliberately acquired and independently matched against publisher digests. Strict extraction accepted only regular files/directories, with no links or unsafe paths. The exact [acquisition inventory](qualification/phase-2c-direct-linux-native-artifacts-v1.json) binds all 412264787 extracted vendor bytes; that record describes the acquisition-time data-only state, before subsequent isolated discovery. No installer or runtime download ran. The smaller standalone choices above were not acquired separately.

The guest's existing apt metadata reports nginx arm64 candidate `1.24.0-2ubuntu7.18`, 521322 bytes, path `pool/main/n/nginx/nginx_1.24.0-2ubuntu7.18_arm64.deb`, SHA-256 `55af9202a0e3b12239f579d589f9dea9d899240efc6d9808cbbd500f53980a3d`. This is an observed cache entry, not a new authenticated archive verification. Dependencies include nginx-common, iproute2 and existing shared libraries. If chosen, bind authenticated Ubuntu metadata and every required package/library first. Extract into exclusively owned vendor preparation instead of starting a global nginx service or running package-maintainer scripts.

The official [responses proxy documentation at the same tag](https://raw.githubusercontent.com/openai/codex/rust-v0.160.1/codex-rs/responses-api-proxy/README.md) offers a smaller existing proxy alternative: fixed request path, token read from stdin, incoming Authorization replacement and configurable upstream URL. Any selected proxy remains outside native/tool mount and PID views under a distinct UID. A synthetic local upstream is mandatory. Neither this interface nor nginx alone establishes caller separation; untrusted tools must not reach its authenticated channel. No custom credential gateway is authorized.

Acquisition preparation must be capped prospectively: at most 512 MiB downloaded data, 1 GiB extracted vendor data, 120 seconds per transfer and 600 seconds total preparation, within the original 8 GiB logical/allocated fixture ceiling. Use exclusively new paths, refuse unsafe archive members/links/oversized expansion, check exact publisher hashes and inventory every representation. File transfer uses an existing artifact-copy interface with status output at most 65536 bytes per stream. These preparation ceilings bound deliberate fixture acquisition; they do not authorize native execution before its separate identity/control freeze. No paid host, account sign-in, real token, model call or global daemon is needed.

## Required feasibility result before full qualification

Freeze exact native, helper, library, kernel, configuration, credential-proxy and observer bytes before native/hostile execution. Trusted version/help discovery must use only a synthetic empty HOME and denied external network; admission flags must distinguish it from hostile native qualification. Demonstrate startup and intended tiny workflow under the original shared native/tool 128 MiB, one CPU, 32 tasks, zero swap and five-second envelope.

The [pinned sandbox documentation](https://raw.githubusercontent.com/openai/codex/rust-v0.160.1/codex-rs/linux-sandbox/README.md) describes nested user/PID/network namespace setup. The successful v5 credential-free payload filter denies that setup, so it cannot be copied blindly onto the native parent. Find a supported existing native/tool boundary that permits trusted sandbox setup while keeping tool namespace/storage/proxy escalation unavailable. Preserve any incompatibility as a concrete NO-GO; do not weaken grants, add allowances or build another executor.

Then prove one permitted synthetic authenticated request and all original worker/child/grandchild/validator negatives at two independent sinks. Freeze the complete profile before replaying fixed provider-shaped responses through the existing native CLI. All twenty original cases must pass twice on that same profile. Complementary mechanism, network or old SBX subsets do not qualify it. If any supported interface or resource limit fails, report the precise missing resolver to the owner and stop that route. No Phase 2D or live spending follows from successful synthetic tests.


## Actual native feasibility observations

Four version/help discovery profiles are retained separately. Profile v1 refused an observer sample taken before process placement. Profile v2 used `sandbox linux --help`, which this CLI treated as payload arguments; v3 confirmed `linux` is not a subcommand. Profile v4 uses the actual `codex sandbox --help` interface: all four commands pass in each of two fresh isolated services, with independently sampled 134217728-byte/zero-swap/one-CPU/32-task controls. The run coordinator exits zero in 0.458 seconds. Help success is not native agent startup or qualification.

The [first tiny native sandbox capability probe](qualification/phase-2c-direct-linux-native-compatibility-profile-v1.json) preserves unchanged limits and runs only a literal tiny-file/one-byte memfd diagnostic. It fails before payload execution: `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`. Scoped kernel audit independently reports AppArmor `unprivileged_userns` denying `net_admin` and `setpcap`. The host's `apparmor_restrict_unprivileged_userns` reads `1`. No native payload result or storage compatibility is claimed.

A fixture-only temporary AppArmor exception was presented to the owner; it has not been applied. Global protection changes are excluded. The next experiment must bind the exact exception and cleanup before running and must still prove that code tools cannot create namespaces, remount writable storage or regain native/proxy authority. A startup exception cannot substitute for that boundary or qualify the complete twenty-case profile.
