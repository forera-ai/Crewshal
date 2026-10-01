# Decision 0001: Crewshal name and repository initialization

Date: 2026-10-01

Status: accepted by the owner, with bounded collision screening completed.

## Decision

Adopt **Crewshal**, pronounced like **crucial**. The sound deliberately evokes something vital or necessary; “crew” connects the name to coordinated agents. Use `Crewshal` for display and `crewshal` for future command/package identifiers. The single final “l” is intentional. Crewshall is an earlier spelling, not a second product.

Rename the existing empty GitHub repository from `prooshani/Foreman` to [prooshani/Crewshal](https://github.com/prooshani/Crewshal), and the local checkout directory from `Foreman` to `Crewshal`. Preserve the repository's identity and initialize its `main` branch with the independently authored research documents, README, this decision, ignore rules and license.

The owner selected **Apache-2.0** for permissive reuse with an explicit patent grant. The initial publication contains documentation only. Naming and repository initialization do not authorize Phase 1 architecture, runtime implementation or benchmark spend.

## Why retire Foreman?

Foreman has direct product and search collisions in infrastructure and AI coding supervision. Examples include [The Foreman](https://theforeman.org/), [ddollar/foreman](https://github.com/ddollar/foreman), [thruwire/foreman](https://github.com/thruwire/foreman) and the [eve software factory](https://github.com/vercel-labs/eve-software-factory-template). Their names and references remain intact in the competitive research. Earlier Runwarrant and Taskwarrant proposals are superseded by the owner's Crewshal decision.

## Collision screening

Screened on 2026-10-01 before renaming. Exact-name general web queries and combinations with AI, agent, software, developer, company and trademark terms were reviewed. Targeted indexed searches covered GitHub, Hugging Face, Go packages and editor extension marketplaces. Search results are incomplete observations, not proof of absence.

| Surface | Observed result | Recheck source |
|---|---|---|
| GitHub repository-name API search | One substring match: `knotman90/crewshal-compiler-C`, an older compiler-book translation/update project created in 2015. No exact bare `Crewshal` repository name in the returned result | [Search API](https://api.github.com/search/repositories?q=crewshal+in%3Aname&per_page=100), [existing repository](https://github.com/knotman90/crewshal-compiler-C) |
| Target owner/name | `prooshani/Crewshal` returned 404 before rename; existing `prooshani/Foreman` was public and empty | [Repository API](https://api.github.com/repos/prooshani/Crewshal) |
| npm | Exact unscoped package endpoint returned 404; search returned zero packages | [Exact endpoint](https://registry.npmjs.org/crewshal), [search endpoint](https://registry.npmjs.org/-/v1/search?text=crewshal&size=20) |
| PyPI | Exact package endpoint returned 404 | [Endpoint](https://pypi.org/pypi/crewshal/json) |
| crates.io | Exact crate endpoint returned 404 | [Endpoint](https://crates.io/api/v1/crates/crewshal) |
| RubyGems | Exact gem endpoint returned 404 | [Endpoint](https://rubygems.org/api/v1/gems/crewshal.json) |
| NuGet | Exact package endpoint returned 404 | [Endpoint](https://api.nuget.org/v3-flatcontainer/crewshal/index.json) |
| Homebrew core | Exact formula endpoint returned 404 | [Endpoint](https://formulae.brew.sh/api/formula/crewshal.json) |
| Packagist | `crewshal/crewshal` returned 404. Fuzzy search returned four differently named packages, including `crewstyle/*` and `crewcharge/core`; no Crewshal package in those results | [Exact endpoint](https://repo.packagist.org/p2/crewshal/crewshal.json), [search](https://packagist.org/search.json?q=crewshal) |
| Go, Hugging Face and editor extensions | No exact-name product surfaced in targeted indexed web searches; native catalog-wide absence was not established | [Go search](https://pkg.go.dev/search?q=crewshal), [Hugging Face](https://huggingface.co/) |
| General web | Personal gaming/forum handles and music references exist; no direct AI engineering competitor surfaced | [Forum handle example](https://mazdas247.com/forum/threads/hey-everyone-just-joined.123763426/) |
| `.com`, `.org`, `.dev` domains | All three exact domain RDAP endpoints returned 404; no domain purchased or reserved | [`.com` RDAP](https://rdap.verisign.com/com/v1/domain/crewshal.com), [`.org` RDAP](https://rdap.publicinterestregistry.org/rdap/domain/crewshal.org), [`.dev` RDAP](https://pubapi.registry.google/rdap/domain/crewshal.dev) |

HTTP 404 means the queried record was not returned at inspection time. It does not establish registrability, package-name reservation rights, availability under other namespaces or legal clearance. Go module identity will depend on a future module path; no language or manifest is chosen by this decision.

## Similarity and residual risks

- **Crucial:** the intentional pronunciation overlaps Micron's established technology brand. [Micron's consumer-brand page](https://www.micron.com/sales-support/sales-network/consumer-brand) establishes that use. This review does not decide trademark similarity or infer that a brand's commercial wind-down releases its name. Use the distinct Crewshal spelling, project descriptor and independent visual identity.
- **CrewAI and other “crew” products:** the root is crowded in AI. [CrewAI](https://docs.crewai.com/en/concepts/flows) is separate prior art; Crewshal has no affiliation with it. The proposed product is runtime-neutral and should not be presented as a CrewAI extension.
- **Crewshall:** the double-“l” variant has existing music and publication uses, including [CREWShall Connections and Conversations](https://miwc.org/who-we-are/the-miwc-team/jo-ann). It is not the canonical spelling.
- **Search and spelling:** users may type Crucial or Crewshall after hearing the name. Keep spelling and pronunciation consistent in documentation and metadata.

Web-indexed exact-name queries targeting USPTO, EUIPO and WIPO domains did not surface an exact Crewshal record. Native comprehensive official-register searches, phonetic/class-based trademark review and a legal assessment were not completed. Registrar availability is not confirmed by RDAP alone. Recheck relevant names and markets before commercial launch or substantial brand investment.

## Outcome

The bounded screen supports **initial open-source repository use**: no direct AI engineering name collision was found, and the known compiler project and personal/music uses are distinct in purpose. The owner authorized this rename conditional on an acceptable screen. Proceed with repository initialization under Crewshal; retain the screening limitations in the public record. No packages or domains are reserved by this decision.
