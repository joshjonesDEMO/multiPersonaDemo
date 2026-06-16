# Project Apex — Stakeholder Kickoff
**Date:** 2024-01-08  
**Attendees:** Sarah (Eng Director), Marcus (VP Eng), Priya (PO), Dev (Staff Eng), Aisha (Data Lead)  
**Facilitator:** Priya

---

## Background

Engineering leadership asked for a way to measure developer velocity across teams after last quarter's missed deadlines. Currently we have no shared definition of "fast" or "slow" — every team uses different metrics in their own spreadsheets. Marcus wants one internal dashboard by end of quarter.

---

## What we talked about

### The problem everyone agreed on

- We don't know if cycle times are getting better or worse across teams
- Code review bottlenecks are invisible until a release slips
- No way to spot if a team is burning out from large PRs week over week
- Engineering Directors can't benchmark their teams against each other

### What the dashboard needs to show (direct quotes)

**Sarah:** "I need to see cycle time per developer so I know who's blocked, not just the team average. Team averages hide everything."

**Marcus:** "The executive view I want is: are our teams getting faster quarter over quarter? That's it. I don't want to drown in individual stats."

**Dev:** "Please don't make this a surveillance tool. The goal is to see patterns at the team level, not to rank individual engineers. I'd be more comfortable if individual stats were only visible to the individual and their direct manager."

**Aisha:** "We already have all the raw data in GitHub. The problem is nobody's built the pipeline to pull it into something queryable. The main ask from my team is: give us a clear spec for the event schema you need and we'll build the ingestion."

### Feature list from the whiteboard

Features the room wanted for MVP (week 4 launch):
1. Team cycle time — avg and p50/p90, 30-day rolling window
2. Individual developer velocity — for self-service and manager use only
3. Review latency — time from PR opened to first review received
4. PR throughput — merged PRs per week per team
5. Simple trend line — is cycle time going up or down week over week?

Explicitly deferred (not for MVP):
- Integration with Jira/Linear for story-point correlation
- Slack notifications ("too noisy, let's not do this yet" — Marcus)
- Benchmarking against industry data
- Mobile view

### Open questions from the room

1. **Who owns access controls?** Dev raised the individual visibility concern — do we restrict `/velocity/{userId}` to self + manager only, or is it open?
2. **How do we handle contractors?** Some repos have external contractors with GitHub access. Should they be included in team velocity stats?
3. **Team membership data?** There's no single source of truth for which developers are on which team. Aisha said the data team can maintain a CSV seed in dbt but someone needs to keep it updated.
4. **What counts as "merged"?** Some teams squash-merge everything. Does a squash-merge on a 3-week-old branch count the same as a regular merge?

### Agreed next steps

- Priya: Write up user stories and acceptance criteria, share by EOD Friday
- Aisha: Design event schema for GitHub webhook ingestion, coordinate with Dev
- Dev: Spike on the FastAPI service skeleton, estimate effort for cycle time endpoint
- Sarah: Get confirmation from Marcus on the access-control policy before we build

---

## Notes from the side conversation after the meeting

Marcus pulled Priya aside after and said: "The thing I'm really worried about is that we ship this and nobody uses it because it's just another dashboard. Make sure we have a plan for adoption — maybe the weekly team leads meeting is the right place to review it."

He also mentioned: "Don't over-engineer the first version. If it shows cycle time and review latency accurately I'll be happy. We can add trend lines in v2."
