# Calendar administration and Slack Huddles: implementation handoff

Research checked 2026-09-21 against current official documentation. This is a specification and capability assessment, not evidence that the integrations have been activated. Paid Slack is an existing dependency; no additional paid service, plan upgrade, or Google Meet is proposed. Public examples must use fictional identities.

## Decision

Use Slack's existing Google Calendar app, its native domain-wide authentication where applicable, copied Slack Huddle links, and native Huddle notes. Build only the coordination layer: briefing, moderator and role preparation, time-change requests, reminder reconciliation, transcript ingestion, and Tasks integration. Keep a manual transcript handoff until a supported full-transcript retrieval path is demonstrated.

## Centralized setup matrix

| Route | Administrator action | Individual connection | Recommendation |
| --- | --- | --- | --- |
| Native Calendar app, ordinary installation | Install/approve Slack app once | Each member connects Google account | Fallback for personal Gmail or unmanaged domains |
| Native Calendar domain-wide authentication | Slack owner/admin initiates; Google Workspace Super Admin authorizes and verifies domain | Matching corporate accounts connect automatically | Preferred when company uses Google Workspace |
| Slack Enterprise org installation | Org Owner/Admin/Integrations Admin distributes supported apps to workspaces | Distribution alone does not authorize Google accounts | Relevant only if actual plan is Enterprise |
| Custom organizer Calendar API integration | Authorize a distinct application or existing connector as organizer | Attendees need not authorize our app to receive email invitations | Optional implementation boundary |
| Custom domain-wide Calendar API service | Google Super Admin grants application's own narrowly scoped delegation | Domain users need no individual OAuth consent | Only if proven native gaps justify added privilege/maintenance |

Native domain-wide authentication is documented on **all Slack plans**. In Google Calendar's Slack Home → Settings → Domain-wide Authentication, add each company domain, follow the supplied Marketplace domain-install and ownership-verification links as Google Workspace Super Admin, then verify in Slack. Enterprise administrators additionally select workspaces. Matching members cannot disconnect their Google account while this mode applies; reminders are automatically subscribed but notification preferences remain adjustable. This cannot centrally authorize unrelated personal or external domains. Source: [Slack domain-wide authentication](https://slack.com/help/articles/360047862573-Enable-domain-wide-authentication-for-calendar-and-file-apps-in-Slack).

Enterprise org installation can distribute eligible apps and make them defaults for future workspaces. It is distinct from Google authorization and does not replace it. Do not infer Enterprise from the fact that Slack is paid. Source: [Slack Enterprise app administration](https://slack.com/help/articles/360000281563-Manage-apps-in-an-Enterprise-organization).

Native Calendar supports invitation responses in Slack, invitation/update/cancellation notifications, configurable reminders, and meeting Join options for events containing Huddle links. Ordinary account connection remains the fallback. Source: [Google Calendar for Slack](https://slack.com/help/articles/206329808-Google-Calendar-for-Slack).

## Huddle scheduling and transcript boundary

A channel/DM's **Copy huddle link** action is available before the Huddle begins. The first person joining through it starts the Huddle. Store that actual copied link in the calendar description/location and reminder messages; do not synthesize a URL or describe a calendar event as an API-created Huddle. Paid Slack permits 50 Huddle participants, up to 25 with video. Private-channel/DM access may require admission. Source: [Slack Huddles](https://slack.com/help/articles/4402059015315-Use-huddles-in-Slack).

Current Slack documentation lists AI Huddle notes on paid plans for members, excluding guests. Huddles containing external people or guests cannot use them. Notes can start automatically per channel, subject to administrator restrictions. Participants are notified and can stop, resume, or cancel capture. The resulting canvas includes notes and an embedded transcript; the transcript is not searchable. Source: [AI Huddle notes](https://slack.com/help/articles/31377193680019-Use-AI-to-take-huddle-notes-in-Slack).

No supported public Huddle creation, recording-start, or full-transcript export endpoint was established in this research. This is an evidence limit, not a claim that no internal Slack interface exists. Slack's [Calls API](https://docs.slack.dev/apis/web-api/using-the-calls-api/) integrates calling applications with Slack; it does not establish Huddle control. [canvases.sections.lookup](https://docs.slack.dev/reference/methods/canvases.sections.lookup/) returns matching section identifiers, not full canvas/transcript text. A notes summary must never be labeled a full transcript.

Required ingestion contract: `source_kind = full_transcript | ai_notes | human_notes`, source permalink, capture consent/status, meeting identifier, and coverage information. Until authorized retrieval of the actual transcript is proven, the moderator supplies accessible text/file content; a missing transcript becomes `awaiting_transcript`, not a fabricated completed analysis. This contract is a proposed design.

## Optional custom API design

Native Slack-managed Google credentials are not credentials for our application. Keep ChatGPT's authorized Calendar connector, or provision a separately authorized organizer integration. Do not extract or reuse another app's tokens.

Google domain-wide delegation permits an application to act for Workspace users without their individual consent. It requires a Google Super Admin, explicit client ID and scopes, and potentially another superadmin's approval where multi-party approval is enabled. Google warns that the grant covers domain users; an application-side subject allowlist is not a Google-enforced user restriction. Source: [Google domain-wide delegation](https://knowledge.workspace.google.com/admin/apps/control-api-access-with-domain-wide-delegation).

Prefer organizer-only authorization when it satisfies the workflow. Scope candidates: `calendar.events.owned` for owned calendars and `calendar.events.freebusy` for availability on accessible calendars; verify each chosen endpoint and target calendar. Avoid blanket calendar/ACL access by default. Source: [Calendar scope definitions](https://developers.google.com/workspace/calendar/api/auth).

Send actual invitations with `sendUpdates=all` and new attendee state `needsAction`. Service accounts require domain-wide delegation to populate attendees; sharing a calendar with a bare service account is not a complete invitation solution. Use the Calendar API's supported client event ID plus reconciliation for retries where implementing directly. Source: [Events insert](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert).

Custom RSVP buttons must authenticate the clicking Slack user, bind to the verified calendar identity, and update only that person's response through authorized access. Otherwise route to native Calendar RSVP and label any local acknowledgment separately. A proposed new time is a request; the organizer resolves availability and revises the canonical event. These are design requirements, not claims of a ready custom integration.

## Acceptance criteria for the next implementer

1. Record actual Slack plan, an available Slack administrator, Google Workspace domain ownership, and Super Admin availability. Company email addresses do not prove Google Workspace hosting. An ordinary Slack account or personal Google Calendar does not prove managed-domain eligibility. Verify Slack admin and Google Workspace Super Admin separately.
2. Pilot native domain-wide authentication for the intended corporate domain, or document per-user fallback. Verify a real invitation, RSVP propagation, reminder, and Huddle Join link for each participant type.
3. Every event is Huddles-only: no Meet conference creation or Meet link. Use IANA time zones and test Belgrade daylight-saving transitions against Tbilisi.
4. Resolve identities, agenda and expected decisions before scheduling; assign a moderator, role questions, and preparation owners/deadlines. Conflicting or missing availability stays explicit.
5. Implement replay protection and meeting revisions. Rescheduling/cancellation invalidates stale preparation and join reminders; native and custom reminders must not duplicate each other unnecessarily.
6. Verify AI-note eligibility and channel settings using actual workspace UI. Retain consent and visibility boundaries. Prove complete transcript ingestion separately from receiving the notes-canvas link.
7. Action items and unresolved questions carry source evidence, owner, due date or explicit unknown, and stable deduplication keys. Reuse existing Tasks issues before creating new ones; send follow-ups only to authorized participants/channels.
8. The native ChatGPT route discovered in this environment supports channel messages and thread replies, after ChatGPT joins the channel and required connectors are authorized. It is separate from the custom server. Do not promise slash-command, DM, edit, reaction triggers or direct server invocation without a separately implemented adapter.
9. No new paid dependency is required by the proposed native setup. Existing Slack/ChatGPT/Google account quotas, policies, and available entitlements still apply; do not promise unlimited execution.

## Minimal activation handoff

The Slack administrator and Google Workspace Super Admin complete native domain authentication if applicable. A channel member copies and verifies the actual Huddle link and checks AI-note eligibility. Add ChatGPT to the selected channel, connect Tasks MCP, then activate and pilot the message/thread workflow with existing authorized Calendar and Slack connectors. Credentials stay in their respective authorization flows. No additional implementation or external messages were performed by this research task.
