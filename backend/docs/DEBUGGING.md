# Debugging the Academic Research Agent

## 1. `KeyError: 'Context variable not found: seminal_paper'`

### Cause

Sub-agents (`academic_websearch`, `academic_newresearch`) use **instruction templates** with `{seminal_paper}` and `{recent_citing_papers}`. ADK substitutes these from **session state**. If the coordinator has not yet written to those keys when a sub-agent runs, substitution raises `KeyError`.

- The coordinator has `output_key="seminal_paper"` (it writes to session state when it *produces* output).
- When the coordinator *invokes* a sub-agent (e.g. right after the user says "find citing papers"), it may not have produced output yet, so `seminal_paper` (and possibly `recent_citing_papers`) can be missing.

### Fix (applied in this repo)

Sub-agent prompts were updated to **not** depend on session state for `seminal_paper` / `recent_citing_papers`. They now instruct the sub-agent to use the **content of the parent’s message** (the coordinator’s tool-invocation message). The coordinator should include the seminal paper info (and, for newresearch, the citing papers) in that message when calling the tool.

### Alternative fixes (if you prefer session state)

- **Initial session state**: If your AG-UI/ADK stack supports it, create sessions with `initial_state={"seminal_paper": "", "recent_citing_papers": ""}` so substitution never fails. You would need to pass this through wherever sessions are created (e.g. `ag_ui_adk`’s session manager / `ADKAgent` if it exposes an `initial_state` or similar).
- **Flow order**: Ensure the coordinator always produces an output that gets stored in `seminal_paper` (and, for newresearch, that something has written `recent_citing_papers`) *before* invoking the sub-agents. That depends on your coordinator prompt and tool-calling logic.

### How to verify

1. Run the backend from `backend/`: `uv run python main.py`.
2. Send a message that triggers a sub-agent (e.g. “Find papers citing Attention is All You Need”).
3. Confirm there is no `KeyError` and that the sub-agent’s reply uses the paper/citing info from the coordinator’s tool message.

---

## 2. `App name mismatch detected ... implies app name "agents"`

### Cause

AG-UI ADK infers an “app name” from the **module path** of the root agent. Your root agent is `academic_research.agent.root_agent`, but the stack trace shows a path under `.venv\...\google\adk\agents`, so the middleware may be resolving the wrong module and reporting an app name like `"agents"` instead of `"academic_research"`.

### Fix (applied in this repo)

The root coordinator is defined as a **subclass of `LlmAgent` in this package** (`AcademicCoordinatorAgent` in `academic_research/agent.py`). Then `inspect.getmodule(academic_coordinator.__class__)` is `academic_research.agent`, so the inferred path is under your project and the mismatch warning no longer appears.

### If the warning reappears

1. **Root agent class must be defined in your code** — use a thin subclass (e.g. `class MyRootAgent(LlmAgent): pass`) as the root agent instead of `LlmAgent(...)` directly.
2. **Confirm app_name** in `backend/main.py`: `ADKAgent(..., app_name="academic_research", ...)`.
3. **Run from backend**: `cd backend && uv run python main.py`.

---

## 3. `Warning: non-text parts in the response: ['function_call', 'thought_signature']`

### Cause

The model sometimes returns parts that are not plain text (e.g. `function_call`, `thought_signature`). The code that builds the string for the client only uses text parts and warns about the rest.

### Impact

Usually **informational only**. The concatenated text is still returned. You can log or ignore this unless you need to handle function calls or other part types explicitly.

---

## 4. General debugging tips

- **Logging**: Increase log level to see ADK/AG-UI flow:
  ```bash
  cd backend
  set LOG_LEVEL=DEBUG
  uv run python main.py
  ```
  (Or set `LOG_LEVEL` in `backend/.env`.)

- **Minimal repro**: Reproduce with a single user message (e.g. “Who are you?” or “Find papers citing Attention is All You Need”) to see whether the error is in the coordinator or in a specific sub-agent.

- **Session state**: If you add custom state keys, ensure they are set (e.g. by the coordinator or by initial state) before any sub-agent instruction uses them in `{variable}` templates.
