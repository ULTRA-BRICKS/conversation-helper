# Agent implementation handoff

The current delivery is documentation and static types/signatures. No meeting runtime is being deployed by this package.
The private prototype is archived and stopped; do not restart it or treat its local tests as release approval.
The Tasks MCP connector is already shipped and remains a separate dependency.

## Assignment rules

Assign one bounded work package per agent, with a named reviewer and an exact base revision.
Paths below are **proposed implementation locations**, not claims that files already exist.
Select the primary runtime before implementation; TypeScript and Python declarations express the same boundaries and do not require two services.
Do not implement both languages merely because both contract files exist.
Changes to shared contracts need a reviewed contract change before dependent agents proceed.
Use existing repository instructions and normal commit/review gates; preserve unrelated work and credentials.

## Work packages

Each row lists the primary interfaces; detailed behavior and failure cases remain normative in SPECIFICATIONS.md.

| Package | Dependencies | Owned paths / interfaces | Acceptance boundary |
|---|---|---|---|
| P0 — capabilities and administration | None | `ADMIN-SETUP.md`, proposed `docs/capabilities.md`; `AdminOnboarding` | Record verified native Calendar/DWA, Huddle and model capabilities; identify exact admin actions and unknowns; do not claim custom API credentials from native app setup |
| P1 — contract fixtures and storage design | P0 | `contracts.ts`, `contracts.py`, proposed `fixtures/`, `docs/storage.md` | Agree primary runtime, stable IDs, tenant boundaries, state versions, immutable review snapshots and effect receipts; provide shared synthetic valid/invalid fixtures |
| P2 — Slack intake and identity | P1 | Proposed `src/slack/`, `src/identity/`; `SlackIngress`, `IdentityDirectory` | Authenticate input; deduplicate overlapping mention/message events; verify participant emails and memberships; preserve requests across retries; block bot loops |
| P3 — briefing and coordination | P2 | Proposed `src/briefing/`, `src/meetings/`; `BriefingService`, `MeetingCoordinator` | Show concrete agenda, attendees, time zones and moderator; collect relevant role questions; require revision-bound approval; reject stale interactions |
| P4 — Calendar, participation and Huddle references | P0, P3 | Proposed `src/calendar/`, `src/participation/`, `src/huddles/`; three provider interfaces | Use authorized Calendar access; validate real Huddle links; create/update invitations idempotently; distinguish native RSVP from local intent; reconcile uncertain provider outcomes; never create Meet |
| P5 — durable jobs and reminders | P1, P3, P4 | Proposed `src/jobs/`, `src/reminders/`; `DurableJobStore`, `ReminderService` | Fenced leases and restart-safe receipts; recheck current revision before delivery; send role-specific preparation; prevent duplicate native/custom reminders and cross-recipient suppression |
| P6 — consent and transcript evidence | P0, P3, P4 | Proposed `src/recording/`, `src/transcripts/`; recording/transcription/store interfaces | Verify a supported source before promising capture; record consent and withdrawal behavior; retain transcript versions and source anchors; report unavailable evidence explicitly |
| P7 — analysis and review | P1, P6 | Proposed `src/analysis/`, `src/review/`, `src/models/`; `EvidenceAnalyzer`, `ModelGateway` | Produce evidence-backed proposals and separate unresolved questions; no invented owner/deadline; defend tool boundaries against transcript instructions; approve immutable snapshots |
| P8 — Tasks adapter and publication | P1, P7 | Proposed `src/tasks/`; `TaskGateway`, `TaskPublisher` | Reuse shipped Tasks APIs: MCP for ChatGPT, REST for the standalone service where authorized; search before linking/creating; preserve semantic action IDs and source links; publish only approved actions; maintain receipts across refresh/retry; expose ambiguous matches for review |
| P9 — follow-up delivery | P5, P7, P8 | Proposed `src/followups/`; `FollowupPublisher` | Publish from reviewed snapshots and confirmed task results; unresolved questions remain questions; retry each recipient independently; never promote an unapproved action |
| P10 — integrated acceptance and operations | P2–P9 | Proposed `tests/integration/`, `docs/runbook.md`, deployment configuration; `AuditSink` | Demonstrate authorized end-to-end flow, restart/retry recovery and cross-tenant denial; document rollback and secret handling; deploy only within an explicitly assigned release scope |

P0 and P1 establish the foundation. P2→P3→P4 establishes scheduling; P5 and P6 can then proceed independently with frozen contracts.
P7→P8→P9 establishes reviewed outcomes. P10 is a release gate, not permission to activate unfinished modules.
Provider-facing live tests require scoped credentials and authorized test destinations; fixtures must not send invitations or messages.

## Known prototype defects to close

These findings are open implementation requirements, not already-fixed behavior.

| Finding | Required correction | Regression evidence |
|---|---|---|
| Follow-up may promote unapproved actions into commitments | Build delivery from immutable review snapshots; only approved actions become commitments | A mixed approved/unapproved analysis never publishes the unapproved action as assigned work, including after an analysis edit |
| Deduplication keyed by `transcriptId:person` can suppress a later approved batch for the same participant | Include the immutable approved batch or snapshot in the recipient delivery key | Approve and deliver batch A, then approve batch B for the same person and transcript: B is delivered; retrying A produces no duplicate |
| Action identifiers depend on transcript lines | Persist semantic action identity separately from evidence locations and versions; review uncertain matches | Reflowed/reordered lines retain an approved action identity and task link; materially distinct actions stay distinct |
| Prototype retains Meet-oriented assumptions | Implement the Huddles-only provider boundary against verified capabilities | Calendar events contain only validated Huddle references; unavailable Huddle automation produces an explicit human step |

The historical 41-test prototype result does not prove these cases or final security review.
Use the archive as a reference only; each reused module still needs the assigned package's review and acceptance evidence.

## Agent prompt template

Copy this template for each assignment and fill every bracket before starting.

```text
Implement package [P-number and name] in [repository] at base [commit].
Primary runtime: [chosen runtime]. Reviewer: [reviewer].
Read repository instructions, README.md, SPECIFICATIONS.md sections [numbers],
ADMIN-SETUP.md where relevant, and the selected contract declarations.
Owned paths: [exact paths]. Dependencies accepted at: [commits/evidence].
Required behavior: [package-specific outcomes and negative cases].
Allowed external effects: [none, or exact authorized test actions/destinations].
Use synthetic fixtures and free components; do not introduce a paid dependency.
Keep interfaces and notifications in English. Huddles only; never create Meet.
Do not infer credentials, identities, provider capabilities or write approval.
If a required provider API is undocumented/unavailable, report the gap and
propose the smallest supported human step; do not invent an endpoint.
Do not change shared contracts or unrelated paths without a reviewed proposal.
Do not expose private archive contents, credentials, transcripts or account data.
Implement only this package. Test its acceptance boundary and concrete risks.
Return: exact commit/files; observed tests; external effects actually performed;
remaining blockers; contract changes requested; and review-ready diff summary.
Distinguish implemented, fixture-tested, live-tested and still-proposed behavior.
```

## Review and release evidence

- Contract acceptance: both declarations and shared fixtures agree; constraints requiring runtime checks are identified explicitly.
- Package acceptance: the assigned reviewer checks permissions, revision checks, retry behavior and the package's negative cases.
- Integration acceptance: one approved scheduling flow and one reviewed transcript-to-task flow pass with synthetic identities and controlled destinations.
- Recovery acceptance: duplicate events, provider timeouts, process restarts, stale approvals and partial recipient failures do not create duplicate effects or lose confirmed work.
- Production acceptance: separately record actual administrative configuration, OAuth grants, provider capabilities and observed results. A local mock is not live proof.
- Release evidence names the source revision, migration/rollback plan, test results and any remaining limitations; no claim that declarations alone deliver functionality.

Native Google Calendar domain-wide authentication may remove per-user native-app setup, but custom service credentials remain a separate decision.
Tasks connector installation still needs the intended user's OAuth consent; the existing endpoint does not establish that consent.
Do not restart the archived prototype, publish its source/data, change production configuration or send messages as part of this documentation handoff.
Resume those actions only when they belong to a newly assigned, authorized implementation or release scope.
