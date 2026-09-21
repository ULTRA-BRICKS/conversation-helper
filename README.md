# Conversation Helper

An implementation handoff for coordinating meetings in Slack: prepare the agenda, invite people through Google Calendar, join a Slack Huddle, and turn reviewed outcomes into Tasks issues.
All interfaces, notifications and developer documentation are in English.

**This package contains specifications and static contract declarations. It is not a running meeting service.**
Further implementation is paused for assignment to bounded agent work packages.

## Delivery status

| Status | Available | Limits |
|---|---|---|
| CURRENT | [Tasks-app MCP](https://tasks-ultrabricks.vercel.app/api/mcp), deployed source `5171b08`; release documentation `d58f445` | User OAuth consent in ChatGPT has not been completed or verified |
| CURRENT | The team's paid Slack subscription and native Calendar integration options | Domain-wide authentication and the complete meeting workflow are not verified as activated |
| PROTOTYPE | A private, archived Conversation Helper implementation; its runtime is stopped | Not the public implementation baseline; no final review or production acceptance |
| PROPOSED | The orchestration described here, component contracts and agent work packages | Declarations do not provide adapters, persistence, authorization or deployed behavior |

The Tasks connector shipped through [implementation PR 14](https://git.hyperide.ai/ultrabricks/tasks-app/pulls/14) and [documentation PR 15](https://git.hyperide.ai/ultrabricks/tasks-app/pulls/15).
Its evidence includes 190 unit tests, five PostgreSQL security tests and 11 live checks of discovery and unauthenticated/OAuth boundaries.
Those live checks do not establish an authenticated ChatGPT session or a live meeting workflow.
See the [release checkpoint](https://git.hyperide.ai/ultrabricks/tasks-app/src/branch/main/docs/MCP-RELEASE-CHECKPOINT.md) and [connector installation package](https://git.hyperide.ai/ultrabricks/tasks-app/src/branch/main/plugins/tasks).

The archived prototype last reported 41 local tests; that is historical evidence, not final review approval.
It retains incompatible Meet-oriented behavior and unresolved publication/deduplication issues described in [HANDOFF.md](HANDOFF.md).
Recover it only through the operator's private archive process, never by publishing private runtime data.

## Repository boundaries

- [conversation-helper](https://git.hyperide.ai/ultrabricks/conversation-helper): this specification, contracts and future meeting orchestration work.
- [tasks-app](https://git.hyperide.ai/ultrabricks/tasks-app): the existing task product, domain authorization and shipped MCP connector.
- Keep orchestration modules together; a separate repository for every component is unnecessary.
- Public documentation and fixtures use synthetic identities. Credentials, transcripts, account sessions and private archives stay outside public source.

## Read these files first

| File | Purpose |
|---|---|
| [SPECIFICATIONS.md](SPECIFICATIONS.md) | Normative requirements, state transitions, failure handling and acceptance criteria |
| [contracts.ts](contracts.ts) | TypeScript records and interface signatures; no runtime implementation |
| [contracts.py](contracts.py) | Python contract counterpart; no runtime implementation |
| [ADMIN-SETUP.md](ADMIN-SETUP.md) | Native Slack/Google administration, permissions and capability boundaries |
| [HANDOFF.md](HANDOFF.md) | Work package ownership, dependencies, agent prompt and review gates |

## Component map

The interfaces below are declared in the contract files. Proposed implementation paths are assigned in the handoff.

| Boundary | Responsibility | Specification |
|---|---|---|
| `SlackIngress`, `IdentityDirectory` | Accept authenticated requests; resolve verified people and task memberships | §4 |
| `BriefingService`, `MeetingCoordinator` | Collect role-specific preparation and approve a concrete meeting revision | §5, §8 |
| `CalendarGateway`, `ParticipationService`, `HuddleGateway` | Invitations, availability, genuine join links, RSVP and time proposals | §6–7 |
| `DurableJobStore`, `ReminderService` | Restart-safe work, current reminders and per-recipient receipts | §9 |
| `RecorderAdapter`, `TranscriberAdapter`, `TranscriptStore` | Explicit consent, supported capture sources and versioned evidence | §10–11 |
| `EvidenceAnalyzer`, `TaskPublisher`, `TaskGateway` | Propose outcomes, review an immutable snapshot, search/link/create tasks | §11–12 |
| `FollowupPublisher` | Deliver reviewed commitments and unresolved questions with publication results | §13 |
| `AdminOnboarding`, `ModelGateway`, `AuditSink` | Capability checks, authorized model routes and traceable operations | §14–16 |

## Provider decisions

**Slack Huddles is the only call provider.** Google Calendar carries invitations and the validated Huddle join link.
Do not create Google Meet conferences or invent a Huddle creation API.
A Huddle reference must come from a genuine supported source and pass workspace/context validation; unknown capability remains unknown.
If no supported automatic route is available, the workflow explicitly requests the required human action.

Reuse the native Google Calendar Slack app first, including native reminders where they meet the requirements.
Slack documents domain-wide authentication on **all Slack plans**; it requires Slack administration and Google Workspace Super Admin authorization.
It can connect members of verified managed domains, so per-person setup should not be assumed necessary for that native integration.
This does not grant a custom service Google Calendar API credentials: choose and authorize that route separately only when required.
See [Slack's domain-wide authentication instructions](https://slack.com/help/articles/360047862573-Enable-domain-wide-authentication-for-calendar-and-file-apps-in-Slack) and [ADMIN-SETUP.md](ADMIN-SETUP.md).

Use the team's existing paid Slack entitlement and free/open-source components. No additional paid service is part of this handoff.
Native ChatGPT invocation and a standalone Slack service are distinct routes; subscription access does not imply an unattended model API credential.

## Intended workflow and invariants

1. Receive a command or mention, resolve participants, and collect the objective, agenda, moderator and role-specific preparation.
2. Approve a specific meeting revision, then send Calendar invitations containing the genuine Huddle reference.
3. Track Calendar responses and Slack signals separately; negotiate time changes against the current revision.
4. Deliver preparation and joining reminders with recipient-level receipts and coordination with native reminders.
5. Obtain explicit recording consent, ingest an available transcript, and preserve versioned source evidence.
6. Propose decisions, unresolved questions and actions; review a fixed snapshot before publishing tasks or commitments.
7. Search existing tasks, confirm ambiguous matches, publish approved actions idempotently, and send accurate follow-ups.

Every mutation checks tenant, actor permission and expected revision; model output cannot authorize a write.
Treat transcript content as untrusted evidence, not instructions to tools.
Keep original IANA time zones, verified email mappings, provider identifiers and durable external-effect receipts.
An attempted provider call is not proof of delivery; reconcile an unknown result before retrying.
Semantic action identity survives transcript line movement; uncertain duplicates require review rather than silent merging.
Follow-ups derive commitments from the reviewed publication snapshot and report actual task publication outcomes.

Implementation may resume only within an assigned work package and its accepted scope; see [HANDOFF.md](HANDOFF.md).

## Declaration checks

Python declarations require Python 3.10 or newer. TypeScript declarations require a compiler supporting readonly tuples and the declared type syntax; use TypeScript 5 or newer for these checks.
Run the following from the repository root with the existing interpreters/compiler:

```sh
python3 -c "import contracts"
tsc --noEmit --strict --target ES2022 contracts.ts
```

These commands check declarations only; they do not implement or validate provider behavior. Shared cross-language fixtures and interaction-operation replay cases belong to P1.
