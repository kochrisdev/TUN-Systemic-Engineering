# TUN Systemic Engineering — Glossary

Status: shared vocabulary for the v0.1 draft.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Contracts](CONTRACTS-v0.1.md)

## People, purpose, and permission

| Term | Meaning |
|---|---|
| Intent | Desired outcome, constraints, and scope; it does not authorize every means of achieving the goal |
| Principal | Authenticated person or service whose access rights are evaluated |
| Actor | Person, agent, or system attributed with performing an action |
| Host | Application and trusted services that enforce policy, canonical state, and execution |
| Capability | What an actor or tool can technically perform |
| Authority | What current permissions and policy allow within a defined scope |
| Delegation | An authorized assignment of bounded work and rights to another actor |
| Autonomy | Arrangement for who chooses and performs work; separate from permission |
| Consequence | Material effect on resources or people, including disclosure and downstream changes |
| Security scope | Tenant, account, project, or other enforced isolation boundary |

## Review and authorization

| Term | Meaning |
|---|---|
| Plan | Reviewable approach and dependencies; accepting it does not approve every resulting action |
| Proposal | Canonical description of a particular action revision and its material effects |
| Material field | A field whose change alters the approved meaning, consequences, or relevant conditions |
| Fingerprint/material binding | A reproducible binding to the selected canonical fields and referenced content |
| Approval | A person's affirmative decision about a particular proposal |
| Authorization | Host evaluation of whether an operation is permitted now |
| Execution grant | Bounded permission for an executor to act on a specific operation |
| Precondition | A condition, such as the target's current revision, checked before applying an effect |
| Revocation | Removal of further authority at a defined boundary; not automatic reversal of earlier effects |

A fingerprint helps detect changed material content. It does not authenticate the approver, prove truth, or grant permission.

## Execution and evidence

| Term | Meaning |
|---|---|
| Operation | One intended logical action with stable identity |
| Attempt | One bounded invocation for an operation |
| Effect | A change, disclosure, communication, or other consequence of work |
| Idempotency | A declared guarantee that repeated requests for the same operation do not add effects within the supported scope |
| Reservation | Durable claim recording the intention and ownership of a dispatch |
| Acknowledgement | Confirmation of a particular request-processing step; its meaning depends on the source |
| Observation | Report or measurement of an event or state |
| Verification | Assessment of whether evidence supports a defined claim within a stated scope and time |
| Reconciliation | Evidence gathering to establish the outcome of an unresolved operation |
| Unknown outcome | Available evidence does not establish which relevant effects occurred |
| Partial outcome | Some relevant effects are established while others did not occur or remain unresolved |
| Action record | Versioned host aggregate of effects, evidence, uncertainty, and next actions |
| Receipt | Authorized user-facing projection of an action record |
| Provenance | Source and production history used to judge relevance and authenticity |
| Causality | Relationship between an operation and its observations/effects; not merely timestamp ordering |

## Control and recovery

| Term | Meaning |
|---|---|
| Run | A bounded execution context that may contain multiple operations |
| Intervention | Request to pause, stop, cancel, revoke, transfer control, or escalate |
| Control outcome | Evidence of the actual effect of an intervention request |
| Retry | A further attempt at the same logical operation |
| Restoration | Return of relevant state to a defined earlier condition, subject to current preconditions |
| Correction | A new effect that fixes an identified problem |
| Compensation | A new effect intended to offset another; it may not restore the original state |
| Escalation | Transfer of an unresolved decision to an authorized person or process |
| Recovery | Umbrella term for supported responses to failure or unwanted effects |

## Documentation status

**Draft-specified:** proposed behavior is documented. **Implemented:** source code supplies the stated behavior. **Validated:** named checks passed for an identified revision and environment. **Published:** an artifact is available through a stated distribution channel.

Publishing this draft does not make its runtime implemented or validated. The [status page](STATUS-AND-ROADMAP.md) separates those claims.
