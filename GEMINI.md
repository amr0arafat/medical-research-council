# Medical Research Council (Gemini CLI)

This extension provides the `medical-research-council` skill in `skills/medical-research-council/`.

When the user asks to run the medical research council, pressure-test a research idea, protocol,
grant, manuscript, or MedTech project, or rank several research topics, activate the skill with
`activate_skill` and follow its SKILL.md exactly.

On Gemini CLI, spawn each council seat with `invoke_agent` and `agent_name: "generalist"`, all
seats in the same response so they run in parallel. Ask the user questions with `ask_user`. Run
the bundled scripts with `run_shell_command`.
