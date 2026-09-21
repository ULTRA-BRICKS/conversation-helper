"""Conversation Helper contracts, aligned with contracts.ts; no implementations.

Huddles are the only call provider. Calendar writes never create Google Meet.
Field names preserve the shared wire vocabulary. Frozen records use tuples for
collections. Implementations must validate/authorize every boundary, deep-freeze
review snapshots, and serialize tagged unions without losing their ``kind``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping, Protocol, TypeAlias

Id: TypeAlias = str
Instant: TypeAlias = str  # ISO 8601 with explicit UTC offset.
TimeZone: TypeAlias = str  # Validated IANA identifier.
Email: TypeAlias = str  # Verified directory email, never inferred from a name.
ETag: TypeAlias = str
Digest: TypeAlias = str
IdempotencyKey: TypeAlias = str
SecretRef: TypeAlias = str  # Opaque vault reference, never a credential value.
Json: TypeAlias = None | bool | int | float | str | tuple["Json", ...] | Mapping[str, "Json"]
Role: TypeAlias = Literal["organizer", "moderator", "presenter", "decision_maker", "owner", "participant"]
Rsvp: TypeAlias = Literal["needs_action", "accepted", "tentative", "declined"]
CapabilityStatus: TypeAlias = Literal["available", "unavailable", "unknown"]


@dataclass(frozen=True, kw_only=True)
class ActorIdentity:
    workspaceId: Id
    actorId: Id
    slackTeamId: Id
    slackUserId: Id
    requestId: Id


@dataclass(frozen=True, kw_only=True)
class WorkerProvenance:
    servicePrincipalId: Id
    approvalId: Id
    onBehalfOfId: Id
    approvedSnapshotId: Id | None = None
    sourceEventId: Id | None = None


@dataclass(frozen=True, kw_only=True)
class InteractiveActorContext(ActorIdentity):
    authenticatedBy: Literal["slack_socket", "slack_signature", "operator_session", "oauth"]


@dataclass(frozen=True, kw_only=True)
class WorkerActorContext(ActorIdentity):
    authenticatedBy: Literal["service_principal"] = "service_principal"
    provenance: WorkerProvenance


ActorContext: TypeAlias = InteractiveActorContext | WorkerActorContext


@dataclass(frozen=True, kw_only=True)
class WriteGuard:
    idempotencyKey: IdempotencyKey
    expectedRevision: int
    expectedETag: ETag | None = None


@dataclass(frozen=True, kw_only=True)
class TimeWindow:
    start: Instant
    end: Instant
    displayTimeZone: TimeZone


@dataclass(frozen=True, kw_only=True)
class Member:
    id: Id
    workspaceId: Id
    slackUserId: Id
    email: Email
    displayName: str
    active: bool
    isBot: bool


@dataclass(frozen=True, kw_only=True)
class RoleAssignment:
    memberId: Id
    roles: tuple[Role, ...]
    agendaItemIds: tuple[Id, ...]
    deliverable: str | None = None
    preparationDue: Instant | None = None


@dataclass(frozen=True, kw_only=True)
class ResolvedIdentity:
    kind: Literal["resolved"] = "resolved"
    member: Member


@dataclass(frozen=True, kw_only=True)
class AmbiguousIdentity:
    kind: Literal["ambiguous"] = "ambiguous"
    candidates: tuple[Member, ...]


@dataclass(frozen=True, kw_only=True)
class UnresolvedIdentity:
    kind: Literal["unresolved"] = "unresolved"
    reason: str


IdentityResolution: TypeAlias = ResolvedIdentity | AmbiguousIdentity | UnresolvedIdentity


@dataclass(frozen=True, kw_only=True)
class Reachability:
    memberId: Id
    channelId: Id
    channelAccess: Literal["confirmed", "denied", "unknown"]
    directMessage: Literal["confirmed", "denied", "unknown"]
    calendarInvitation: Literal["verified_email", "unavailable"]


@dataclass(frozen=True, kw_only=True)
class TaskMemberMapping:
    memberId: Id
    tasksWorkspaceId: Id
    tasksMemberId: Id
    verifiedEmail: Email
    verifiedAt: Instant


@dataclass(frozen=True, kw_only=True)
class AgendaItem:
    id: Id
    topic: str
    desiredOutcome: str
    materials: tuple[str, ...]
    durationMinutes: int
    ownerId: Id | None = None
    presenterId: Id | None = None
    preparationDue: Instant | None = None


@dataclass(frozen=True, kw_only=True)
class HuddleLink:
    provider: Literal["slack_huddle"] = "slack_huddle"
    url: str
    slackTeamId: Id
    channelId: Id
    obtainedVia: Literal["user_supplied", "documented_slack_surface"]
    verification: Literal["verified", "unverified", "rejected"]
    verificationReason: str | None = None
    validatedAt: Instant | None = None


@dataclass(frozen=True, kw_only=True)
class HuddleObservation:
    meetingId: Id
    state: Literal["scheduled_reference", "observed_active", "observed_ended", "unknown"]
    source: str
    observedAt: Instant
    reason: str | None = None


@dataclass(frozen=True, kw_only=True)
class MeetingRevision:
    meetingId: Id
    workspaceId: Id
    revision: int
    title: str
    outcome: str
    organizerId: Id
    moderatorId: Id  # Exactly one moderator, also a participant.
    members: tuple[Member, ...]
    assignments: tuple[RoleAssignment, ...]
    agenda: tuple[AgendaItem, ...]
    channelId: Id
    state: Literal["draft", "briefing", "scheduling", "scheduled", "cancelling", "cancelled", "completed"]
    window: TimeWindow | None = None
    huddle: HuddleLink | None = None
    threadId: Id | None = None


@dataclass(frozen=True, kw_only=True)
class PreparationReply:
    meetingId: Id
    meetingRevision: int
    memberId: Id
    agendaItemIds: tuple[Id, ...]
    text: str
    sourceEventId: Id


@dataclass(frozen=True, kw_only=True)
class Clarification:
    id: Id
    recipientId: Id
    agendaItemIds: tuple[Id, ...]
    question: str
    due: Instant | None = None


@dataclass(frozen=True, kw_only=True)
class SlackInteraction:
    action: str
    meetingId: Id
    revision: int
    operationId: Id
    value: Json


@dataclass(frozen=True, kw_only=True)
class SlackInbound:
    eventId: Id
    teamId: Id
    userId: Id
    channelId: Id
    receivedAt: Instant
    kind: Literal["slash_command", "mention", "thread_reply", "interaction"]
    text: str
    threadId: Id | None = None
    messageTs: str | None = None
    interaction: SlackInteraction | None = None


@dataclass(frozen=True, kw_only=True)
class InboundReceipt:
    eventId: Id
    disposition: Literal["accepted", "duplicate", "rejected"]
    requestId: Id


@dataclass(frozen=True, kw_only=True)
class FreeAvailability:
    kind: Literal["free"] = "free"
    memberId: Id
    window: TimeWindow
    checkedAt: Instant


@dataclass(frozen=True, kw_only=True)
class BusyAvailability:
    kind: Literal["busy"] = "busy"
    memberId: Id
    overlaps: tuple[TimeWindow, ...]
    checkedAt: Instant


@dataclass(frozen=True, kw_only=True)
class UnknownAvailability:
    kind: Literal["unknown"] = "unknown"
    memberId: Id
    reason: Literal["no_access", "provider_error", "existing_event_overlap", "unmapped_calendar"]
    checkedAt: Instant


Availability: TypeAlias = FreeAvailability | BusyAvailability | UnknownAvailability


@dataclass(frozen=True, kw_only=True)
class ScheduleApproval:
    id: Id
    reviewerId: Id
    meetingRevision: int
    approvedAt: Instant
    briefingDigest: Digest
    acknowledgedUnknownMemberIds: tuple[Id, ...]
    idempotencyKey: IdempotencyKey


@dataclass(frozen=True, kw_only=True)
class PerUserCalendarCredentials:
    kind: Literal["per_user_oauth"] = "per_user_oauth"
    subjectMemberId: Id
    credential: SecretRef
    grantedScopes: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class DelegatedCalendarCredentials:
    kind: Literal["delegated_workspace"] = "delegated_workspace"
    subjectEmail: Email
    credential: SecretRef
    grantedScopes: tuple[str, ...]
    adminApprovalId: Id
    authorizedAdminRole: Literal["super_admin"]


CalendarCredentialMode: TypeAlias = PerUserCalendarCredentials | DelegatedCalendarCredentials
CalendarModeName: TypeAlias = Literal["per_user_oauth", "delegated_workspace"]


@dataclass(frozen=True, kw_only=True)
class NativeCalendarConnection:
    application: Literal["official_google_calendar_for_slack"] = "official_google_calendar_for_slack"
    provisioning: Literal["native_individual", "native_domain_auth"]
    verifiedDomains: tuple[str, ...]
    unmatchedAccountFlow: Literal["individual_oauth"] = "individual_oauth"
    requiredRoles: tuple[Literal["slack_owner_or_admin", "google_workspace_super_admin"], ...]
    customServiceCredentialAccess: Literal["unavailable"] = "unavailable"


@dataclass(frozen=True, kw_only=True)
class CalendarEventRef:
    calendarId: Id
    eventId: Id
    url: str
    etag: ETag
    meetingId: Id
    meetingRevision: int


@dataclass(frozen=True, kw_only=True)
class CalendarInvitation:
    meeting: MeetingRevision
    huddle: HuddleLink
    recipientEmails: tuple[Email, ...]
    approval: ScheduleApproval
    conferenceCreation: Literal["disabled"] = "disabled"


@dataclass(frozen=True, kw_only=True)
class ParticipationResponse:
    meetingId: Id
    meetingRevision: int
    memberId: Id
    response: Rsvp
    calendarWrite: Literal["confirmed", "pending", "not_authorized"]
    source: Literal["slack", "google_calendar"]
    receiptId: Id


@dataclass(frozen=True, kw_only=True)
class TimeProposal:
    id: Id
    meetingId: Id
    meetingRevision: int
    memberId: Id
    preferred: TimeWindow
    reason: str | None = None


@dataclass(frozen=True, kw_only=True)
class CapabilityEvidence:
    capability: str
    source: str
    checkedAt: Instant


IntegrationReadiness: TypeAlias = Literal["not_configured", "consent_required", "configured_unverified", "verified", "degraded", "unsupported"]


@dataclass(frozen=True, kw_only=True)
class IntegrationStatus:
    integration: Literal["slack", "native_calendar_app", "calendar_service", "recorder", "transcriber", "tasks", "model"]
    readiness: IntegrationReadiness
    checkedAt: Instant
    reason: str | None = None


@dataclass(frozen=True, kw_only=True)
class WorkspaceCapabilities:
    slackPlan: Literal["free", "paid", "enterprise", "unknown"]
    groupHuddles: CapabilityStatus
    huddleLinkDiscovery: CapabilityStatus
    nativeTranscriptRetrieval: CapabilityStatus
    externalRecording: CapabilityStatus
    calendarInvitations: CapabilityStatus
    calendarRsvp: CapabilityStatus
    tasksRead: CapabilityStatus
    tasksWrite: CapabilityStatus
    evidence: tuple[CapabilityEvidence, ...]


@dataclass(frozen=True, kw_only=True)
class ConsentRecord:
    meetingId: Id
    meetingRevision: int
    noticeId: Id
    noticeDigest: Digest
    participantSetDigest: Digest
    memberId: Id
    decision: Literal["consented", "declined", "withdrawn"]
    sourceEventId: Id
    recordedAt: Instant


@dataclass(frozen=True, kw_only=True)
class RecordingSession:
    id: Id
    meetingId: Id
    meetingRevision: int
    noticeId: Id
    participantSetDigest: Digest
    adapter: Literal["external_manual", "supported_recorder", "native_transcript_import"]
    state: Literal["awaiting_consent", "ready", "start_requested", "active", "interrupted", "stop_requested", "stopped", "consent_withdrawn"]
    artifactRef: Id | None = None


@dataclass(frozen=True, kw_only=True)
class TranscriptSegment:
    id: Id
    line: int
    speakerLabel: str
    text: str
    contentDigest: Digest
    speakerId: Id | None = None
    startMs: int | None = None
    endMs: int | None = None


@dataclass(frozen=True, kw_only=True)
class RecordingGap:
    reason: str
    startMs: int | None = None
    endMs: int | None = None


@dataclass(frozen=True, kw_only=True)
class TranscriptVersion:
    transcriptId: Id
    meetingId: Id
    version: int
    source: str
    sourceKind: Literal["full_transcript", "ai_notes", "human_notes"]
    coverage: Literal["unknown", "partial", "complete"]
    originalBlobRef: Id
    contentDigest: Digest
    metadataDigest: Digest
    segments: tuple[TranscriptSegment, ...]
    gaps: tuple[RecordingGap, ...]


@dataclass(frozen=True, kw_only=True)
class EvidenceAnchor:
    transcriptId: Id
    transcriptVersion: int
    segmentId: Id
    contentDigest: Digest
    line: int
    quote: str
    timestampMs: int | None = None


@dataclass(frozen=True, kw_only=True)
class AnalyzedStatement:
    id: Id
    text: str
    evidence: tuple[EvidenceAnchor, ...]


@dataclass(frozen=True, kw_only=True)
class ActionProposal:
    id: Id
    stableSemanticKey: str  # Reconcile evidence content, not title-only or line-number-only hashes.
    title: str
    evidence: tuple[EvidenceAnchor, ...]
    ownerId: Id | None = None
    dueDate: str | None = None
    uncertainty: str | None = None


@dataclass(frozen=True, kw_only=True)
class MeetingAnalysis:
    id: Id
    transcript: TranscriptVersion
    decisions: tuple[AnalyzedStatement, ...]
    unresolved: tuple[AnalyzedStatement, ...]
    actions: tuple[ActionProposal, ...]
    method: str


@dataclass(frozen=True, kw_only=True)
class TaskRef:
    workspaceId: Id
    id: Id
    key: str
    url: str
    version: int
    assigneeId: Id | None = None


@dataclass(frozen=True, kw_only=True)
class CreateTaskTarget:
    kind: Literal["create"] = "create"
    duplicateSearchReceiptId: Id


@dataclass(frozen=True, kw_only=True)
class LinkTaskTarget:
    kind: Literal["link"] = "link"
    task: TaskRef


@dataclass(frozen=True, kw_only=True)
class ApprovedAction:
    action: ActionProposal
    owner: TaskMemberMapping
    target: CreateTaskTarget | LinkTaskTarget


@dataclass(frozen=True, kw_only=True)
class ReviewSnapshot:
    snapshotId: Id
    meeting: MeetingRevision
    meetingRevision: int
    transcriptId: Id
    transcriptVersion: int
    approvedActionIds: tuple[Id, ...]
    actions: tuple[ApprovedAction, ...]
    decisions: tuple[AnalyzedStatement, ...]
    unresolved: tuple[AnalyzedStatement, ...]
    recipients: tuple[Id, ...]
    reviewerId: Id
    approvedAt: Instant
    contentDigest: Digest
    sendFollowups: bool


@dataclass(frozen=True, kw_only=True)
class EffectReceipt:
    id: Id
    idempotencyKey: IdempotencyKey
    scopeId: Id
    status: Literal["confirmed", "unknown", "failed"]
    attemptedAt: Instant
    actionId: Id | None = None
    recipientId: Id | None = None
    externalId: Id | None = None


@dataclass(frozen=True, kw_only=True)
class TaskPublication:
    snapshotId: Id
    actionId: Id
    task: TaskRef
    receipt: EffectReceipt


@dataclass(frozen=True, kw_only=True)
class CalendarRevisionScope:
    kind: Literal["calendar_revision"] = "calendar_revision"
    meetingId: Id
    revision: int


@dataclass(frozen=True, kw_only=True)
class ReviewSnapshotScope:
    kind: Literal["review_snapshot"] = "review_snapshot"
    snapshotId: Id


@dataclass(frozen=True, kw_only=True)
class InboundScope:
    kind: Literal["inbound"] = "inbound"
    eventId: Id


@dataclass(frozen=True, kw_only=True)
class Job:
    id: Id
    kind: Literal["inbound", "briefing", "clarification", "calendar_upsert", "calendar_cancel", "reminder", "recording_notice", "transcript_request", "analysis", "task_publish", "followup"]
    scope: CalendarRevisionScope | ReviewSnapshotScope | InboundScope
    payloadRef: Id
    dueAt: Instant
    idempotencyKey: IdempotencyKey


@dataclass(frozen=True, kw_only=True)
class JobLease:
    job: Job
    workerId: Id
    fencingToken: int
    expiresAt: Instant
    attempt: int


@dataclass(frozen=True, kw_only=True)
class RetryPolicy:
    maxAttempts: int
    initialDelayMs: int
    maxDelayMs: int


@dataclass(frozen=True, kw_only=True)
class Reminder:
    id: Id
    meetingId: Id
    meetingRevision: int
    memberId: Id
    kind: Literal["preparation", "meeting", "action_followup"]
    dueAt: Instant
    agendaItemIds: tuple[Id, ...]
    snapshotId: Id | None = None


@dataclass(frozen=True, kw_only=True)
class FollowupDelivery:
    snapshotId: Id
    recipientId: Id
    destination: Literal["meeting_thread", "direct_message"]
    publications: tuple[TaskPublication, ...]
    idempotencyKey: IdempotencyKey


@dataclass(frozen=True, kw_only=True)
class DuplicateSearch:
    receiptId: Id
    query: str
    tasks: tuple[TaskRef, ...]
    checkedAt: Instant


@dataclass(frozen=True, kw_only=True)
class TaskCapabilities:
    read: bool
    write: bool
    idempotentCreate: bool
    optimisticUpdate: bool


@dataclass(frozen=True, kw_only=True)
class TaskPatch:
    title: str | None = None
    assigneeId: Id | None = None
    dueDate: str | None = None


@dataclass(frozen=True, kw_only=True)
class ProvisioningPlan:
    id: Id
    workspaceId: Id
    mode: Literal["guided_existing_apps", "self_hosted"]
    capabilities: WorkspaceCapabilities
    calendarMode: CalendarModeName | None = None
    calendarStrategy: Literal["native_domain_auth", "native_individual", "custom_organizer_oauth", "custom_domain_delegation"]
    requiredScopes: tuple[str, ...]
    requiredAdminRoles: tuple[str, ...]
    operatorSteps: tuple[str, ...]
    blockers: tuple[str, ...]
    recurringCost: Literal["free", "uses_existing_paid_workspace", "requires_new_payment"]
    readiness: tuple[IntegrationStatus, ...]
    nativeCalendarConnection: NativeCalendarConnection | None = None


@dataclass(frozen=True, kw_only=True)
class ModelRequest:
    purpose: Literal["briefing", "clarification", "analysis"]
    instructionVersion: str
    untrustedInput: Json
    responseSchema: Json
    maxOutputTokens: int


@dataclass(frozen=True, kw_only=True)
class ModelResponse:
    value: Json
    provider: Literal["chatgpt_authorized_bridge", "local_model", "configured_api", "deterministic"]
    model: str
    requestId: Id
    inputTokens: int | None = None
    outputTokens: int | None = None


@dataclass(frozen=True, kw_only=True)
class AuditEvent:
    id: Id
    workspaceId: Id
    actorId: Id
    performedById: Id
    approvedById: Id | None = None
    approvalId: Id | None = None
    operation: str
    resourceId: Id
    at: Instant
    outcome: Literal["allowed", "denied", "confirmed", "unknown", "failed"]
    revision: int | None = None
    snapshotId: Id | None = None
    receiptId: Id | None = None


class SlackIngress(Protocol):
    async def verify(self, envelope: Json, transport: Literal["socket_mode", "signed_http"]) -> SlackInbound: ...
    async def accept(self, event: SlackInbound) -> InboundReceipt: ...  # Persist before acknowledging success.


class IdentityDirectory(Protocol):
    async def resolve(self, context: ActorContext, slackUserId: Id) -> IdentityResolution: ...
    async def checkReachability(self, context: ActorContext, member: Member, channelId: Id) -> Reachability: ...
    async def mapTaskMember(self, context: ActorContext, member: Member, tasksWorkspaceId: Id) -> TaskMemberMapping: ...


class BriefingService(Protocol):
    async def draft(self, context: ActorContext, request: str, guard: WriteGuard) -> MeetingRevision: ...
    async def revise(self, context: ActorContext, meetingId: Id, request: str, guard: WriteGuard) -> MeetingRevision: ...
    async def questions(self, context: ActorContext, meeting: MeetingRevision) -> tuple[Clarification, ...]: ...
    async def reply(self, context: ActorContext, reply: PreparationReply, guard: WriteGuard) -> None: ...


class MeetingCoordinator(Protocol):
    async def get(self, context: ActorContext, meetingId: Id) -> MeetingRevision: ...
    async def confirm(self, context: ActorContext, meetingId: Id, approval: ScheduleApproval, guard: WriteGuard) -> Job: ...
    async def cancel(self, context: ActorContext, meetingId: Id, guard: WriteGuard) -> Job: ...  # Approved publications are separate.
    async def review(self, context: ActorContext, snapshot: ReviewSnapshot, guard: WriteGuard) -> ReviewSnapshot: ...
    async def publish(self, context: ActorContext, snapshotId: Id, idempotencyKey: IdempotencyKey) -> tuple[Job, ...]: ...


class CalendarGateway(Protocol):
    async def availability(self, context: ActorContext, credentials: CalendarCredentialMode, members: tuple[Member, ...], window: TimeWindow, previous: CalendarEventRef | None = None) -> tuple[Availability, ...]: ...
    async def upsert(self, context: ActorContext, credentials: CalendarCredentialMode, invitation: CalendarInvitation, guard: WriteGuard, previous: CalendarEventRef | None = None) -> CalendarEventRef: ...
    async def cancel(self, context: ActorContext, credentials: CalendarCredentialMode, event: CalendarEventRef, guard: WriteGuard) -> EffectReceipt: ...
    async def respond(self, context: ActorContext, credentials: CalendarCredentialMode, event: CalendarEventRef, response: Rsvp, guard: WriteGuard) -> ParticipationResponse: ...
    async def readResponses(self, context: ActorContext, credentials: CalendarCredentialMode, event: CalendarEventRef) -> tuple[ParticipationResponse, ...]: ...


class ParticipationService(Protocol):
    async def respond(self, context: ActorContext, meetingId: Id, response: Rsvp, guard: WriteGuard) -> ParticipationResponse: ...
    async def proposeTime(self, context: ActorContext, proposal: TimeProposal, guard: WriteGuard) -> None: ...
    async def reconcile(self, context: ActorContext, event: CalendarEventRef) -> tuple[ParticipationResponse, ...]: ...


class HuddleGateway(Protocol):
    async def capabilities(self, context: ActorContext) -> WorkspaceCapabilities: ...
    async def resolveLink(self, context: ActorContext, channelId: Id, suppliedUrl: str | None = None) -> HuddleLink: ...
    async def validateAccess(self, context: ActorContext, link: HuddleLink, members: tuple[Member, ...]) -> tuple[Reachability, ...]: ...
    async def observe(self, context: ActorContext, meetingId: Id, link: HuddleLink) -> HuddleObservation: ...


class DurableJobStore(Protocol):
    async def enqueue(self, jobs: tuple[Job, ...], audit: AuditEvent) -> None: ...  # Atomic with domain transition.
    async def claim(self, workerId: Id, now: Instant, leaseMs: int) -> JobLease | None: ...
    async def renew(self, lease: JobLease, expiresAt: Instant) -> JobLease: ...
    async def complete(self, lease: JobLease, receipts: tuple[EffectReceipt, ...]) -> None: ...
    async def fail(self, lease: JobLease, errorCode: str, policy: RetryPolicy) -> None: ...
    async def cancelCalendarRevision(self, meetingId: Id, revision: int) -> None: ...
    async def reconcileUnknown(self, jobId: Id) -> tuple[EffectReceipt, ...]: ...


class ReminderService(Protocol):
    async def plan(self, meeting: MeetingRevision, replies: tuple[PreparationReply, ...]) -> tuple[Reminder, ...]: ...
    async def deliver(self, context: ActorContext, reminder: Reminder, idempotencyKey: IdempotencyKey) -> EffectReceipt: ...


class RecorderAdapter(Protocol):
    async def requestConsent(self, context: ActorContext, meeting: MeetingRevision, notice: str, guard: WriteGuard) -> RecordingSession: ...
    async def recordConsent(self, context: ActorContext, consent: ConsentRecord, guard: WriteGuard) -> None: ...
    async def start(self, context: ActorContext, session: RecordingSession, guard: WriteGuard) -> RecordingSession: ...
    async def stop(self, context: ActorContext, session: RecordingSession, reason: Literal["completed", "withdrawn", "interrupted"], guard: WriteGuard) -> RecordingSession: ...
    async def status(self, context: ActorContext, sessionId: Id) -> RecordingSession: ...


class TranscriberAdapter(Protocol):
    async def transcribe(self, context: ActorContext, session: RecordingSession, artifactRef: Id, idempotencyKey: IdempotencyKey) -> TranscriptVersion: ...
    async def retrieveNative(self, context: ActorContext, meetingId: Id, sourceRef: Id) -> TranscriptVersion: ...  # Verified capability/permission required.


class TranscriptStore(Protocol):
    async def importTranscript(self, context: ActorContext, transcript: TranscriptVersion, guard: WriteGuard) -> TranscriptVersion: ...
    async def get(self, context: ActorContext, transcriptId: Id, version: int) -> TranscriptVersion: ...
    async def exportOriginal(self, context: ActorContext, transcriptId: Id, version: int) -> Id: ...


class EvidenceAnalyzer(Protocol):
    async def analyze(self, context: ActorContext, meeting: MeetingRevision, transcript: TranscriptVersion) -> MeetingAnalysis: ...
    async def reconcileActions(self, previous: tuple[ActionProposal, ...], next: tuple[ActionProposal, ...]) -> tuple[ActionProposal, ...]: ...


class TaskPublisher(Protocol):
    async def search(self, context: ActorContext, action: ActionProposal) -> DuplicateSearch: ...
    async def publish(self, context: ActorContext, snapshot: ReviewSnapshot, actionId: Id, idempotencyKey: IdempotencyKey) -> TaskPublication: ...
    async def reconcile(self, context: ActorContext, idempotencyKey: IdempotencyKey) -> TaskPublication | None: ...


class TaskGateway(Protocol):
    transport: Literal["rest", "mcp"]
    async def capabilities(self, context: ActorContext) -> TaskCapabilities: ...
    async def search(self, context: ActorContext, query: str) -> tuple[TaskRef, ...]: ...
    async def fetch(self, context: ActorContext, taskId: Id) -> TaskRef: ...
    async def create(self, context: ActorContext, action: ApprovedAction, description: str, idempotencyKey: IdempotencyKey) -> TaskRef: ...
    async def addComment(self, context: ActorContext, task: TaskRef, body: str, idempotencyKey: IdempotencyKey) -> EffectReceipt: ...
    async def update(self, context: ActorContext, task: TaskRef, patch: TaskPatch, guard: WriteGuard) -> TaskRef: ...


class FollowupPublisher(Protocol):
    async def plan(self, snapshot: ReviewSnapshot, publications: tuple[TaskPublication, ...]) -> tuple[FollowupDelivery, ...]: ...
    async def publish(self, context: ActorContext, snapshot: ReviewSnapshot, delivery: FollowupDelivery) -> EffectReceipt: ...


class AdminOnboarding(Protocol):
    async def inspect(self, context: ActorContext) -> WorkspaceCapabilities: ...
    async def plan(self, context: ActorContext, mode: Literal["guided_existing_apps", "self_hosted"], calendarStrategy: Literal["native_domain_auth", "native_individual", "custom_organizer_oauth", "custom_domain_delegation"]) -> ProvisioningPlan: ...
    async def apply(self, context: ActorContext, approvedPlanId: Id, credentialRefs: tuple[SecretRef, ...], guard: WriteGuard) -> WorkspaceCapabilities: ...


class ModelGateway(Protocol):
    async def complete(self, context: ActorContext, request: ModelRequest, idempotencyKey: IdempotencyKey) -> ModelResponse: ...


class AuditSink(Protocol):
    async def append(self, event: AuditEvent) -> None: ...
