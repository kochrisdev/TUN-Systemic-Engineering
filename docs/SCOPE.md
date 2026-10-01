# TUN Systemic Engineering — Scope and Non-Claims

Updated: 1 October 2026.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Status](STATUS-AND-ROADMAP.md)

## What this repository provides

The repository contains a draft specification, a component catalog, architectural and workflow guidance, a proposed record model, a design-integration map, an adoption worksheet, planned validation procedures, and a requirement traceability matrix. It also provides a standard-library documentation checker and an [experimental local publication and recovery pilot](PILOT.md).

The specification remains a draft. A specialized JSON Schema profile and Python/SQLite host/provider implement one local workflow. A local React interface uses two pinned design components. Focused pilot tests and checker regression tests are executable; general record shapes remain proposed.

## Initial engineering boundary

The initial scope is the contract around consequential AI actions: proposal binding, human decisions, host authorization, execution identity, observations, verification, intervention, and recovery.

Data access and information disclosure still need authorization and privacy controls when the user-facing result is informational. Applicability follows actual effects and enabled capabilities rather than an interface label.

The architecture is technology-neutral. The reference implementation direction is one local publication provider and host. Additional providers require separate evidence for their semantics.

## What remains planned

No production runtime, stable schema package, model integration, remote provider adapter, general-purpose presentation SDK, or complete runtime conformance suite is supplied. The local pilot's fixture identity, limited host, and SQLite provider are not substitutes for those features.

The companion design repository's broader UI library and local host example are separate implementations. This repository vendors only ApprovalGate, ActionReceipt, and their supporting files at a pinned revision. Their existence or test results cannot be transferred automatically to this engineering specification.

## Limits of the model

The documents do not establish universal exactly-once remote effects, immediate cancellation of accepted work, reversible external communication, or certainty from model confidence.

A verified action claim has a scope and observation time. It may establish publication or acceptance without establishing delivery, enduring state, factual truth, or benefit to the user.

Schemas can validate structure; they cannot authenticate identity, enforce host policy, or prove an outcome by themselves. An append-only journal also needs actual integrity and access controls.

## Other product responsibilities

Adopting teams still own model and retrieval evaluation, content quality, domain-specific safety, application security, accessibility, reliability, cost, data governance, and operating practice.

TUN can structure evidence and obligations for those teams. It does not replace their domain judgment or a product-specific release decision.

## Version and assessment terminology

A document version, source commit, package release, deployment, and assessment are different identifiers. Cite a source commit when reviewing an evolving v0.1 document.

Draft-specified means behavior is written down. Implemented means code exists. Validated means a named check passed in a stated environment. Published means an artifact is available through a stated channel.

There is no independent TUN certification program. The [assessment rule](SPECIFICATION-v0.1.md#tse-032) defines the evidence required for a future scoped engineering claim. Complete requirements remain marked not assessed; selected pilot tests provide narrower evidence.

## Website boundary

The documentation structure is informed by the design site. This repository update does not create or deploy an engineering website. The Markdown index is the current navigation entry point.
