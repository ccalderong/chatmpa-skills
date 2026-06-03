# chatMPA Skills

Claude Code skills for marine science workflows developed by the [chatMPA](https://github.com/chatmpa-studio-lab) team. These skills extend Claude Code with domain-specific analytical capabilities for oceanography, conservation biology, and fisheries science.

## Available Skills

| Skill | Description |
|---|---|
| [`ltem-biomass-productivity`](./ltem-biomass-productivity/) | Fish biomass, productivity, and environmental drivers from the Baja California LTEM dataset |
| [`ltem-fish-community`](./ltem-fish-community/) | Fish community structure, diversity indices, and trophic metrics from LTEM surveys |
| [`ltem-mpa-effectiveness`](./ltem-mpa-effectiveness/) | MPA effectiveness assessment centered on Cabo Pulmo National Park |
| [`ltem-temporal-trends`](./ltem-temporal-trends/) | Long-term trend detection across 26 years of Baja California fish surveys (1998–2024) |
| [`marine-prosperity-brief`](./marine-prosperity-brief/) | Marine Prosperity Index policy briefs for coastal municipalities |
| [`marine-prosperity-publish`](./marine-prosperity-publish/) | Publishing and dissemination workflows for Marine Prosperity outputs |
| [`marine-species-analysis`](./marine-species-analysis/) | Species distribution modeling and OBIS biodiversity data workflows |
| [`mpa-effectiveness-assessment`](./mpa-effectiveness-assessment/) | General MPA effectiveness assessment framework |
| [`reef-ecology-report`](./reef-ecology-report/) | Coral reef monitoring data analysis and report generation |
| [`sea-surface-temperature`](./sea-surface-temperature/) | SST data retrieval and analysis via ERDDAP |

## Installation

Clone this repo into the `.claude/skills/` directory of your project:

```bash
git clone https://github.com/chatmpa-studio-lab/chatmpa-skills .claude/skills
```

Or add it as a git submodule to keep skills in sync:

```bash
git submodule add https://github.com/chatmpa-studio-lab/chatmpa-skills .claude/skills
```

To install only specific skills, use sparse checkout:

```bash
git clone --no-checkout https://github.com/chatmpa-studio-lab/chatmpa-skills .claude/skills
cd .claude/skills
git sparse-checkout init --cone
git sparse-checkout set ltem-mpa-effectiveness marine-prosperity-brief
git checkout main
```

## Updating

```bash
cd .claude/skills && git pull
```

## Skill Structure

Each skill follows the Claude Code skill format:

```
<skill-name>/
├── SKILL.md          # Skill definition, triggers, and workflow instructions
├── references/       # Domain reference documents (methodology, guides, context)
└── scripts/          # Helper scripts invoked by the skill
```

## Contributing

Skills are developed by the chatMPA team. To propose a new skill or update, open an issue or pull request.

## Related Repositories

- [chatmpa-studio](https://github.com/chatmpa-studio-lab/chatmpa-studio) — chatMPA Studio IDE
