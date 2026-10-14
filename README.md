# namilink-plugins

Claude Code plugins by NamiLink.

| Plugin | What it does |
| --- | --- |
| [`meeting-summary`](plugins/meeting-summary) | Summarizes a meeting from a Teams transcript (`.vtt`/`.json`) or an audio recording (`.m4a`/`.wav`, transcribed locally with mlx-whisper) |
| [`fc`](plugins/fc) | Offloads context compaction to Cerebras Qwen and writes `HANDOFF.md` |

## Install

1. Add the marketplace once. Run this in a Claude Code session:

   ```text
   /plugin marketplace add NamiLinkLabs/claude-plugins
   ```

2. Install the plugins you want:

   ```text
   /plugin install meeting-summary@namilink-plugins
   /plugin install fc@namilink-plugins
   ```

   Choose **Install for you (user scope)** to get the plugin in every project.

3. Type `/` and check that the commands are listed: `/meeting-summary:meeting-summary`, `/fc:fc`.

From your shell, without a session:

```bash
claude plugin marketplace add NamiLinkLabs/claude-plugins
claude plugin install meeting-summary@namilink-plugins
claude plugin install fc@namilink-plugins
```

## Update

Auto-update is off for this marketplace by default. To pull new versions, run `/plugin`, open the **Marketplaces** tab, select `namilink-plugins` and choose **Update marketplace**. You can turn on **Enable auto-update** there too.

From your shell: `claude plugin update meeting-summary@namilink-plugins`.

## meeting-summary

```text
/meeting-summary:meeting-summary <file> [hu|en]
```

You can also just ask Claude to summarize a meeting file.

- Writes `<name>.md` (transcript) and `<name>_ai_summary.md` (summary) next to the input file.
- The summary language is the transcript's language (`hu` for Hungarian, `en` for anything else) unless you pass `hu` or `en`.
- Runs in a background subagent, so your session stays free and its context stays clean. The result arrives in the chat when it's done.
- Claude writes the summary itself: no API key needed.

Requirements:

- **Transcripts (`.vtt`/`.json`)**: `python3`.
- **Audio (`.m4a`/`.wav`)**: a Mac with Apple Silicon, `ffmpeg` (`brew install ffmpeg`), and either `mlx_whisper` on your `PATH` or [`uv`](https://docs.astral.sh/uv/) (`brew install uv`). The first run downloads the whisper model (about 1.5 GB). The spoken language is detected from the first 30 seconds.

## fc

```text
/fc:fc
```

Sends the current session's transcript to Cerebras Qwen, writes the compacted context to `HANDOFF.md`, then tells you to run `/clear`.

Requirements: `python3` and a `CEREBRAS_API_KEY` environment variable. Set it in your shell profile before starting Claude Code, or in `~/.claude/settings.json`:

```json
{
  "env": {
    "CEREBRAS_API_KEY": "your-key"
  }
}
```

## Developing

- Test a plugin without installing it: `claude --plugin-dir ./plugins/<name>`.
- Validate: `claude plugin validate ./plugins/<name>` and `claude plugin validate .` for the marketplace.
- Bump `version` in the plugin's `.claude-plugin/plugin.json` on every change, or installed copies won't update.
