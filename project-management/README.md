# Project Management — Pac-Man

This directory holds the evidence of how the Pac-Man project was driven, as
required by the subject (chapter VIII, *Project management*).

## Contents

| Document | What it covers |
|---|---|
| [01-timeline.md](01-timeline.md) | Planned schedule, milestones, and the actual timeline rebuilt from the Git history |
| [02-team-organization.md](02-team-organization.md) | Who did what, module ownership, how decisions were made |
| [03-analysis-and-choices.md](03-analysis-and-choices.md) | Project analysis and the technical choices behind the architecture |
| [04-risk-analysis.md](04-risk-analysis.md) | Risk register, impact, and mitigations |
| [05-acceptance-test-plan.md](05-acceptance-test-plan.md) | Feature-by-feature acceptance tests mapped to the subject |
| [06-progress-tracking.md](06-progress-tracking.md) | Planned vs. actual progress, and the remaining backlog |

## A note on the commit history

The commit messages were normalised to `type(scope): description` near the end
of the project. Each message was rewritten from the diff of the commit it
describes; authors and author dates are untouched. The consequence is that
every commit carries the same *committer* date, the day of the rewrite. See the
retrospective in [02-team-organization.md](02-team-organization.md) for why we
consider this a poor substitute for having agreed a convention on day one.

## Sources of evidence

Everything marked as *measured* in these documents comes from the repository
itself and can be re-checked by the reviewer:

```bash
git log --format='%h|%an|%ad|%s' --date=short   # commit history
git shortlog -sne                               # commits per author
make lint                                       # code quality status
```

The timeline, the contribution figures, and the module ownership tables were
derived from the 51 commits between **2026-06-30** and **2026-09-01**.