---
description: Offload context compaction to Cerebras Qwen (qwen-3.8-27b) and prepare HANDOFF.md
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/qwen_compact.py:*)
---

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/qwen_compact.py`
2. Once it finishes, tell me the context is saved to HANDOFF.md and remind me to run /clear.