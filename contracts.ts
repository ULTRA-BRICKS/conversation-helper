/**
 * Conversation Helper implementation contracts. English interfaces; no implementation.
 * Huddles are the only call provider. Calendar events must never create Google Meet.
 * Validate these contracts at every trust boundary; types alone are not authorization.
 */
export type Id = string;
export type Instant = string; // ISO 8601 instant with an explicit UTC offset.
export type TimeZone = string; // Validated IANA identifier.
export type Email = string; // Verified directory email, never inferred from a name.
export type ETag = string;
export type Digest = string; // SHA-256 of canonical bytes.
export type IdempotencyKey = string;
export type SecretRef = string; // Opaque vault reference; never plaintext credentials.
export type Json = null | boolean | number | string | readonly Json[] | { readonly [key: string]: Json };

export interface ActorIdentity {
  readonly workspaceId: Id;
  readonly actorId: Id;
  readonly slackTeamId: Id;
  readonly slackUserId: Id;
  readonly requestId: Id;
}
export interface WorkerProvenance { readonly servicePrincipalId: Id; readonly approvalId: Id; readonly onBehalfOfId: Id; readonly approvedSnapshotId?: Id; readonly sourceEventId?: Id }
export type ActorContext = ActorIdentity & (
  { readonly authenticatedBy: "slack_socket" | "slack_signature" | "operator_session" | "oauth" } |
  { readonly authenticatedBy: "service_principal"; readonly provenance: WorkerProvenance }
);
export interface WriteGuard {
  readonly idempotencyKey: IdempotencyKey;
  readonly expectedRevision: number;
  readonly expectedETag?: ETag;
}
export interface TimeWindow {
  readonly start: Instant;
  readonly end: Instant;
  readonly displayTimeZone: TimeZone;
}
export type Role = "organizer" | "moderator" | "presenter" | "decision_maker" | "owner" | "participant";
export interface Member {
  readonly id: Id;
  readonly workspaceId: Id;
  readonly slackUserId: Id;
  readonly email: Email;
  readonly displayName: string;
  readonly active: boolean;
  readonly isBot: boolean;
}
export interface RoleAssignment {
  readonly memberId: Id;
  readonly roles: readonly Role[];
  readonly agendaItemIds: readonly Id[];
  readonly deliverable?: string;
  readonly preparationDue?: Instant;
}
export type IdentityResolution =
  | { readonly kind: "resolved"; readonly member: Member }
  | { readonly kind: "ambiguous"; readonly candidates: readonly Member[] }
  | { readonly kind: "unresolved"; readonly reason: string };
export interface Reachability {
  readonly memberId: Id;
  readonly channelId: Id;
  readonly channelAccess: "confirmed" | "denied" | "unknown";
  readonly directMessage: "confirmed" | "denied" | "unknown";
  readonly calendarInvitation: "verified_email" | "unavailable";
}
export interface TaskMemberMapping {
  readonly memberId: Id;
  readonly tasksWorkspaceId: Id;
  readonly tasksMemberId: Id;
  readonly verifiedEmail: Email;
  readonly verifiedAt: Instant;
}
export interface AgendaItem {
  readonly id: Id;
  readonly topic: string;
  readonly desiredOutcome: string;
  readonly ownerId?: Id;
  readonly presenterId?: Id;
  readonly materials: readonly string[];
  readonly preparationDue?: Instant;
  readonly durationMinutes: number;
}
export interface HuddleLink {
  readonly provider: "slack_huddle";
  readonly url: string;
  readonly slackTeamId: Id;
  readonly channelId: Id;
  readonly obtainedVia: "user_supplied" | "documented_slack_surface";
  readonly verification: "verified" | "unverified" | "rejected";
  readonly verificationReason?: string;
  readonly validatedAt?: Instant;
}
export interface HuddleObservation { readonly meetingId: Id; readonly state: "scheduled_reference" | "observed_active" | "observed_ended" | "unknown"; readonly source: string; readonly observedAt: Instant; readonly reason?: string }
export interface MeetingRevision {
  readonly meetingId: Id;
  readonly workspaceId: Id;
  readonly revision: number;
  readonly title: string;
  readonly outcome: string;
  readonly organizerId: Id;
  readonly moderatorId: Id; // Exactly one selected moderator, also a participant.
  readonly members: readonly Member[];
  readonly assignments: readonly RoleAssignment[];
  readonly agenda: readonly AgendaItem[];
  readonly window?: TimeWindow;
  readonly huddle?: HuddleLink;
  readonly channelId: Id;
  readonly threadId?: Id;
  readonly state: "draft" | "briefing" | "scheduling" | "scheduled" | "cancelling" | "cancelled" | "completed";
}
export interface PreparationReply {
  readonly meetingId: Id;
  readonly meetingRevision: number;
  readonly memberId: Id;
  readonly agendaItemIds: readonly Id[];
  readonly text: string;
  readonly sourceEventId: Id;
}
export interface Clarification {
  readonly id: Id;
  readonly recipientId: Id;
  readonly agendaItemIds: readonly Id[];
  readonly question: string;
  readonly due?: Instant;
}
export interface SlackInbound {
  readonly eventId: Id;
  readonly teamId: Id;
  readonly userId: Id;
  readonly channelId: Id;
  readonly threadId?: Id;
  readonly messageTs?: string; // Physical message identity shared by mention and message deliveries.
  readonly receivedAt: Instant;
  readonly kind: "slash_command" | "mention" | "thread_reply" | "interaction";
  readonly text: string;
  readonly interaction?: { readonly action: string; readonly meetingId: Id; readonly revision: number; readonly operationId: Id; readonly value: Json };
}
export interface InboundReceipt { readonly eventId: Id; readonly disposition: "accepted" | "duplicate" | "rejected"; readonly requestId: Id }

export type Availability =
  | { readonly kind: "free"; readonly memberId: Id; readonly window: TimeWindow; readonly checkedAt: Instant }
  | { readonly kind: "busy"; readonly memberId: Id; readonly overlaps: readonly TimeWindow[]; readonly checkedAt: Instant }
  | { readonly kind: "unknown"; readonly memberId: Id; readonly reason: "no_access" | "provider_error" | "existing_event_overlap" | "unmapped_calendar"; readonly checkedAt: Instant };
export interface ScheduleApproval {
  readonly id: Id;
  readonly reviewerId: Id;
  readonly meetingRevision: number;
  readonly approvedAt: Instant;
  readonly briefingDigest: Digest;
  readonly acknowledgedUnknownMemberIds: readonly Id[];
  readonly idempotencyKey: IdempotencyKey;
}
export type CalendarCredentialMode =
  | { readonly kind: "per_user_oauth"; readonly subjectMemberId: Id; readonly credential: SecretRef; readonly grantedScopes: readonly string[] }
  | { readonly kind: "delegated_workspace"; readonly subjectEmail: Email; readonly credential: SecretRef; readonly grantedScopes: readonly string[]; readonly adminApprovalId: Id; readonly authorizedAdminRole: "super_admin" };
export interface NativeCalendarConnection {
  readonly application: "official_google_calendar_for_slack";
  readonly provisioning: "native_individual" | "native_domain_auth";
  readonly verifiedDomains: readonly string[];
  readonly unmatchedAccountFlow: "individual_oauth";
  readonly requiredRoles: readonly ("slack_owner_or_admin" | "google_workspace_super_admin")[];
  readonly customServiceCredentialAccess: "unavailable"; // Native app grants cannot be exported to this service.
}
export interface CalendarEventRef {
  readonly calendarId: Id;
  readonly eventId: Id;
  readonly url: string;
  readonly etag: ETag;
  readonly meetingId: Id;
  readonly meetingRevision: number;
}
export interface CalendarInvitation {
  readonly meeting: MeetingRevision;
  readonly huddle: HuddleLink;
  readonly recipientEmails: readonly Email[];
  readonly approval: ScheduleApproval;
  readonly conferenceCreation: "disabled";
}
export type Rsvp = "needs_action" | "accepted" | "tentative" | "declined";
export interface ParticipationResponse {
  readonly meetingId: Id;
  readonly meetingRevision: number;
  readonly memberId: Id;
  readonly response: Rsvp;
  readonly calendarWrite: "confirmed" | "pending" | "not_authorized";
  readonly source: "slack" | "google_calendar";
  readonly receiptId: Id;
}
export interface TimeProposal { readonly id: Id; readonly meetingId: Id; readonly meetingRevision: number; readonly memberId: Id; readonly preferred: TimeWindow; readonly reason?: string }

export type CapabilityStatus = "available" | "unavailable" | "unknown";
export type IntegrationReadiness = "not_configured" | "consent_required" | "configured_unverified" | "verified" | "degraded" | "unsupported";
export interface IntegrationStatus { readonly integration: "slack" | "native_calendar_app" | "calendar_service" | "recorder" | "transcriber" | "tasks" | "model"; readonly readiness: IntegrationReadiness; readonly reason?: string; readonly checkedAt: Instant }
export interface WorkspaceCapabilities {
  readonly slackPlan: "free" | "paid" | "enterprise" | "unknown";
  readonly groupHuddles: CapabilityStatus;
  readonly huddleLinkDiscovery: CapabilityStatus;
  readonly nativeTranscriptRetrieval: CapabilityStatus;
  readonly externalRecording: CapabilityStatus;
  readonly calendarInvitations: CapabilityStatus;
  readonly calendarRsvp: CapabilityStatus;
  readonly tasksRead: CapabilityStatus;
  readonly tasksWrite: CapabilityStatus;
  readonly evidence: readonly { readonly capability: string; readonly source: string; readonly checkedAt: Instant }[];
}
export interface ConsentRecord {
  readonly meetingId: Id;
  readonly meetingRevision: number;
  readonly noticeId: Id;
  readonly noticeDigest: Digest;
  readonly participantSetDigest: Digest;
  readonly memberId: Id;
  readonly decision: "consented" | "declined" | "withdrawn";
  readonly sourceEventId: Id;
  readonly recordedAt: Instant;
}
export interface RecordingSession {
  readonly id: Id;
  readonly meetingId: Id;
  readonly meetingRevision: number;
  readonly noticeId: Id;
  readonly participantSetDigest: Digest;
  readonly adapter: "external_manual" | "supported_recorder" | "native_transcript_import";
  readonly state: "awaiting_consent" | "ready" | "start_requested" | "active" | "interrupted" | "stop_requested" | "stopped" | "consent_withdrawn";
  readonly artifactRef?: Id;
}
export interface TranscriptSegment { readonly id: Id; readonly line: number; readonly speakerId?: Id; readonly speakerLabel: string; readonly startMs?: number; readonly endMs?: number; readonly text: string; readonly contentDigest: Digest }
export interface TranscriptVersion {
  readonly transcriptId: Id;
  readonly meetingId: Id;
  readonly version: number;
  readonly source: string;
  readonly sourceKind: "full_transcript" | "ai_notes" | "human_notes";
  readonly coverage: "unknown" | "partial" | "complete";
  readonly originalBlobRef: Id;
  readonly contentDigest: Digest;
  readonly metadataDigest: Digest;
  readonly segments: readonly TranscriptSegment[];
  readonly gaps: readonly { readonly startMs?: number; readonly endMs?: number; readonly reason: string }[];
}
export interface EvidenceAnchor { readonly transcriptId: Id; readonly transcriptVersion: number; readonly segmentId: Id; readonly contentDigest: Digest; readonly line: number; readonly timestampMs?: number; readonly quote: string }
export interface AnalyzedStatement { readonly id: Id; readonly text: string; readonly evidence: readonly EvidenceAnchor[] }
export interface ActionProposal {
  readonly id: Id;
  readonly stableSemanticKey: string; // Reconcile evidence content, not title-only or line-number-only hashes.
  readonly title: string;
  readonly ownerId?: Id;
  readonly dueDate?: string; // Validated YYYY-MM-DD; absent when not explicitly agreed.
  readonly evidence: readonly EvidenceAnchor[];
  readonly uncertainty?: string;
}
export interface MeetingAnalysis { readonly id: Id; readonly transcript: TranscriptVersion; readonly decisions: readonly AnalyzedStatement[]; readonly unresolved: readonly AnalyzedStatement[]; readonly actions: readonly ActionProposal[]; readonly method: string }
export interface TaskRef { readonly workspaceId: Id; readonly id: Id; readonly key: string; readonly url: string; readonly version: number; readonly assigneeId?: Id }
export interface ApprovedAction {
  readonly action: ActionProposal;
  readonly owner: TaskMemberMapping;
  readonly target: { readonly kind: "create"; readonly duplicateSearchReceiptId: Id } | { readonly kind: "link"; readonly task: TaskRef };
}
export interface ReviewSnapshot {
  readonly snapshotId: Id;
  readonly meeting: MeetingRevision;
  readonly meetingRevision: number;
  readonly transcriptId: Id;
  readonly transcriptVersion: number;
  readonly approvedActionIds: readonly Id[];
  readonly actions: readonly ApprovedAction[];
  readonly decisions: readonly AnalyzedStatement[];
  readonly unresolved: readonly AnalyzedStatement[];
  readonly recipients: readonly Id[];
  readonly reviewerId: Id;
  readonly approvedAt: Instant;
  readonly contentDigest: Digest;
  readonly sendFollowups: boolean;
}
export interface EffectReceipt {
  readonly id: Id;
  readonly idempotencyKey: IdempotencyKey;
  readonly scopeId: Id;
  readonly actionId?: Id;
  readonly recipientId?: Id;
  readonly externalId?: Id;
  readonly status: "confirmed" | "unknown" | "failed";
  readonly attemptedAt: Instant;
}
export interface TaskPublication { readonly snapshotId: Id; readonly actionId: Id; readonly task: TaskRef; readonly receipt: EffectReceipt }
export interface Job {
  readonly id: Id;
  readonly kind: "inbound" | "briefing" | "clarification" | "calendar_upsert" | "calendar_cancel" | "reminder" | "recording_notice" | "transcript_request" | "analysis" | "task_publish" | "followup";
  readonly scope: { readonly kind: "calendar_revision"; readonly meetingId: Id; readonly revision: number } | { readonly kind: "review_snapshot"; readonly snapshotId: Id } | { readonly kind: "inbound"; readonly eventId: Id };
  readonly payloadRef: Id;
  readonly dueAt: Instant;
  readonly idempotencyKey: IdempotencyKey;
}
export interface JobLease { readonly job: Job; readonly workerId: Id; readonly fencingToken: number; readonly expiresAt: Instant; readonly attempt: number }
export interface RetryPolicy { readonly maxAttempts: number; readonly initialDelayMs: number; readonly maxDelayMs: number }
export interface Reminder { readonly id: Id; readonly meetingId: Id; readonly meetingRevision: number; readonly memberId: Id; readonly kind: "preparation" | "meeting" | "action_followup"; readonly dueAt: Instant; readonly agendaItemIds: readonly Id[]; readonly snapshotId?: Id }
export interface FollowupDelivery { readonly snapshotId: Id; readonly recipientId: Id; readonly destination: "meeting_thread" | "direct_message"; readonly publications: readonly TaskPublication[]; readonly idempotencyKey: IdempotencyKey }

export interface SlackIngress {
  verify(envelope: Json, transport: "socket_mode" | "signed_http"): Promise<SlackInbound>;
  accept(event: SlackInbound): Promise<InboundReceipt>; // Persist before acknowledging success.
}
export interface IdentityDirectory {
  resolve(context: ActorContext, slackUserId: Id): Promise<IdentityResolution>;
  checkReachability(context: ActorContext, member: Member, channelId: Id): Promise<Reachability>;
  mapTaskMember(context: ActorContext, member: Member, tasksWorkspaceId: Id): Promise<TaskMemberMapping>;
}
export interface BriefingService {
  draft(context: ActorContext, request: string, guard: WriteGuard): Promise<MeetingRevision>;
  revise(context: ActorContext, meetingId: Id, request: string, guard: WriteGuard): Promise<MeetingRevision>;
  questions(context: ActorContext, meeting: MeetingRevision): Promise<readonly Clarification[]>;
  reply(context: ActorContext, reply: PreparationReply, guard: WriteGuard): Promise<void>;
}
export interface MeetingCoordinator {
  get(context: ActorContext, meetingId: Id): Promise<MeetingRevision>;
  confirm(context: ActorContext, meetingId: Id, approval: ScheduleApproval, guard: WriteGuard): Promise<Job>;
  cancel(context: ActorContext, meetingId: Id, guard: WriteGuard): Promise<Job>; // Never cancels an approved publication snapshot.
  review(context: ActorContext, snapshot: ReviewSnapshot, guard: WriteGuard): Promise<ReviewSnapshot>;
  publish(context: ActorContext, snapshotId: Id, idempotencyKey: IdempotencyKey): Promise<readonly Job[]>;
}
export interface CalendarGateway {
  availability(context: ActorContext, credentials: CalendarCredentialMode, members: readonly Member[], window: TimeWindow, previous?: CalendarEventRef): Promise<readonly Availability[]>;
  upsert(context: ActorContext, credentials: CalendarCredentialMode, invitation: CalendarInvitation, guard: WriteGuard, previous?: CalendarEventRef): Promise<CalendarEventRef>;
  cancel(context: ActorContext, credentials: CalendarCredentialMode, event: CalendarEventRef, guard: WriteGuard): Promise<EffectReceipt>;
  respond(context: ActorContext, credentials: CalendarCredentialMode, event: CalendarEventRef, response: Rsvp, guard: WriteGuard): Promise<ParticipationResponse>;
  readResponses(context: ActorContext, credentials: CalendarCredentialMode, event: CalendarEventRef): Promise<readonly ParticipationResponse[]>;
}
export interface ParticipationService {
  respond(context: ActorContext, meetingId: Id, response: Rsvp, guard: WriteGuard): Promise<ParticipationResponse>;
  proposeTime(context: ActorContext, proposal: TimeProposal, guard: WriteGuard): Promise<void>;
  reconcile(context: ActorContext, event: CalendarEventRef): Promise<readonly ParticipationResponse[]>;
}
export interface HuddleGateway {
  capabilities(context: ActorContext): Promise<WorkspaceCapabilities>;
  resolveLink(context: ActorContext, channelId: Id, suppliedUrl?: string): Promise<HuddleLink>; // No invented createHuddle API.
  validateAccess(context: ActorContext, link: HuddleLink, members: readonly Member[]): Promise<readonly Reachability[]>;
  observe(context: ActorContext, meetingId: Id, link: HuddleLink): Promise<HuddleObservation>;
}
export interface DurableJobStore {
  enqueue(jobs: readonly Job[], audit: AuditEvent): Promise<void>; // Atomic with the related domain transition.
  claim(workerId: Id, now: Instant, leaseMs: number): Promise<JobLease | null>;
  renew(lease: JobLease, expiresAt: Instant): Promise<JobLease>;
  complete(lease: JobLease, receipts: readonly EffectReceipt[]): Promise<void>;
  fail(lease: JobLease, errorCode: string, policy: RetryPolicy): Promise<void>;
  cancelCalendarRevision(meetingId: Id, revision: number): Promise<void>;
  reconcileUnknown(jobId: Id): Promise<readonly EffectReceipt[]>;
}
export interface ReminderService {
  plan(meeting: MeetingRevision, replies: readonly PreparationReply[]): Promise<readonly Reminder[]>;
  deliver(context: ActorContext, reminder: Reminder, idempotencyKey: IdempotencyKey): Promise<EffectReceipt>;
}
export interface RecorderAdapter {
  requestConsent(context: ActorContext, meeting: MeetingRevision, notice: string, guard: WriteGuard): Promise<RecordingSession>;
  recordConsent(context: ActorContext, consent: ConsentRecord, guard: WriteGuard): Promise<void>;
  start(context: ActorContext, session: RecordingSession, guard: WriteGuard): Promise<RecordingSession>;
  stop(context: ActorContext, session: RecordingSession, reason: "completed" | "withdrawn" | "interrupted", guard: WriteGuard): Promise<RecordingSession>;
  status(context: ActorContext, sessionId: Id): Promise<RecordingSession>;
}
export interface TranscriberAdapter {
  transcribe(context: ActorContext, session: RecordingSession, artifactRef: Id, idempotencyKey: IdempotencyKey): Promise<TranscriptVersion>;
  retrieveNative(context: ActorContext, meetingId: Id, sourceRef: Id): Promise<TranscriptVersion>; // Requires verified capability and permission, not merely Slack paid.
}
export interface TranscriptStore {
  importTranscript(context: ActorContext, transcript: TranscriptVersion, guard: WriteGuard): Promise<TranscriptVersion>;
  get(context: ActorContext, transcriptId: Id, version: number): Promise<TranscriptVersion>;
  exportOriginal(context: ActorContext, transcriptId: Id, version: number): Promise<Id>;
}
export interface EvidenceAnalyzer {
  analyze(context: ActorContext, meeting: MeetingRevision, transcript: TranscriptVersion): Promise<MeetingAnalysis>;
  reconcileActions(previous: readonly ActionProposal[], next: readonly ActionProposal[]): Promise<readonly ActionProposal[]>;
}
export interface DuplicateSearch { readonly receiptId: Id; readonly query: string; readonly tasks: readonly TaskRef[]; readonly checkedAt: Instant }
export interface TaskPublisher {
  search(context: ActorContext, action: ActionProposal): Promise<DuplicateSearch>;
  publish(context: ActorContext, snapshot: ReviewSnapshot, actionId: Id, idempotencyKey: IdempotencyKey): Promise<TaskPublication>;
  reconcile(context: ActorContext, idempotencyKey: IdempotencyKey): Promise<TaskPublication | null>;
}
export interface TaskGateway {
  readonly transport: "rest" | "mcp";
  capabilities(context: ActorContext): Promise<{ readonly read: boolean; readonly write: boolean; readonly idempotentCreate: boolean; readonly optimisticUpdate: boolean }>;
  search(context: ActorContext, query: string): Promise<readonly TaskRef[]>;
  fetch(context: ActorContext, taskId: Id): Promise<TaskRef>;
  create(context: ActorContext, action: ApprovedAction, description: string, idempotencyKey: IdempotencyKey): Promise<TaskRef>;
  addComment(context: ActorContext, task: TaskRef, body: string, idempotencyKey: IdempotencyKey): Promise<EffectReceipt>;
  update(context: ActorContext, task: TaskRef, patch: { readonly title?: string; readonly assigneeId?: Id; readonly dueDate?: string }, guard: WriteGuard): Promise<TaskRef>;
}
export interface FollowupPublisher {
  plan(snapshot: ReviewSnapshot, publications: readonly TaskPublication[]): Promise<readonly FollowupDelivery[]>;
  publish(context: ActorContext, snapshot: ReviewSnapshot, delivery: FollowupDelivery): Promise<EffectReceipt>;
}
export interface ProvisioningPlan {
  readonly id: Id;
  readonly workspaceId: Id;
  readonly mode: "guided_existing_apps" | "self_hosted";
  readonly capabilities: WorkspaceCapabilities;
  readonly calendarMode?: CalendarCredentialMode["kind"]; // Native app-only setup grants no service credentials.
  readonly calendarStrategy: "native_domain_auth" | "native_individual" | "custom_organizer_oauth" | "custom_domain_delegation";
  readonly nativeCalendarConnection?: NativeCalendarConnection;
  readonly requiredScopes: readonly string[];
  readonly requiredAdminRoles: readonly string[];
  readonly operatorSteps: readonly string[];
  readonly blockers: readonly string[];
  readonly recurringCost: "free" | "uses_existing_paid_workspace" | "requires_new_payment";
  readonly readiness: readonly IntegrationStatus[];
}
export interface AdminOnboarding {
  inspect(context: ActorContext): Promise<WorkspaceCapabilities>;
  plan(context: ActorContext, mode: ProvisioningPlan["mode"], calendarStrategy: ProvisioningPlan["calendarStrategy"]): Promise<ProvisioningPlan>;
  apply(context: ActorContext, approvedPlanId: Id, credentialRefs: readonly SecretRef[], guard: WriteGuard): Promise<WorkspaceCapabilities>; // Explicit grants only; never bypass admin consent.
}
export interface ModelRequest { readonly purpose: "briefing" | "clarification" | "analysis"; readonly instructionVersion: string; readonly untrustedInput: Json; readonly responseSchema: Json; readonly maxOutputTokens: number }
export interface ModelResponse { readonly value: Json; readonly provider: "chatgpt_authorized_bridge" | "local_model" | "configured_api" | "deterministic"; readonly model: string; readonly requestId: Id; readonly inputTokens?: number; readonly outputTokens?: number }
export interface ModelGateway { complete(context: ActorContext, request: ModelRequest, idempotencyKey: IdempotencyKey): Promise<ModelResponse> }
export interface AuditEvent { readonly id: Id; readonly workspaceId: Id; readonly actorId: Id; readonly performedById: Id; readonly approvedById?: Id; readonly approvalId?: Id; readonly operation: string; readonly resourceId: Id; readonly revision?: number; readonly snapshotId?: Id; readonly receiptId?: Id; readonly at: Instant; readonly outcome: "allowed" | "denied" | "confirmed" | "unknown" | "failed" }
export interface AuditSink { append(event: AuditEvent): Promise<void> }
