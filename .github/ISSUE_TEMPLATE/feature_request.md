---
name: Feature request
about: Propose a change to a skill, an agent, a hook, the lab scaffold or the migration
labels: enhancement
---

- [ ] I searched open and closed issues and this is not a duplicate
- [ ] I removed every secret, lab record and piece of personal data from this request

Never paste API keys, tokens, passwords, lab records, unpublished data or personal data here. This issue is public.

## Environment (required)

| Field | Value |
|-------|-------|
| science-ultrapowers version (`.claude-plugin/plugin.json`) | |
| Claude Code version (`claude --version`) | |
| Operating system and shell | |
| Skill or agent involved | |

## The situation
<!-- What were you trying to do in your lab, and what got in the way? A concrete session beats a general idea. -->

## The proposal
<!-- What should change: which skill, agent, hook or template, and how it would behave. -->

## How would we know it worked?
<!-- The session you would run before and after, and the difference you expect in the agent's behaviour. Skill bodies are tuned with pressure tests, so a change there needs that kind of evidence. -->

## Boundaries check
- [ ] This does not add a runtime dependency beyond bash, node 22+ and the Python 3.11+ standard library
- [ ] This does not add telemetry or any remote call at runtime
