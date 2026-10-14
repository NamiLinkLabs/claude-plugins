---
name: meeting-summary
description: Summarize a meeting from a Teams transcript (.vtt/.json) or an audio recording (.m4a/.wav, transcribed locally with mlx-whisper). Writes <name>.md (transcript) and <name>_ai_summary.md next to the input file.
argument-hint: <file> [hu|en, default: transcript language]
context: fork
allowed-tools:
  - Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/prepare_transcript.py *)
  - Read
  - Write
---

Summarize the meeting in: $ARGUMENTS
The first argument is the input file. The optional second argument is the summary language: `hu` or `en`. Without it, use the transcript's language: `hu` for a Hungarian transcript, `en` for anything else.

1. Prepare the transcript. Audio is transcribed locally (spoken language detected automatically) and can take several minutes, so run this with a 600000 ms Bash timeout:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/prepare_transcript.py "<file>"`
   It prints the transcript path, never the transcript itself. If it fails, stop and report the error.
2. Read the whole transcript file. If it is too large for one Read, read consecutive chunks with offset/limit until every line is covered.
3. Follow the prompt for the summary language below, and write only the summary to `<input file stem>_ai_summary.md` in the input file's directory.
4. Reply with only the transcript and summary file paths and a 3-line gist. The full summary lives in the file.

## Prompt: hu

Kérlek, elemezd a 2. lépésben beolvasott megbeszélés-átiratot, és készíts átfogó összefoglalót, amely tartalmazza:

1. A megbeszélt fő témákat, minden részlettel
2. A meghozott kulcsfontosságú döntéseket
3. A felvetett fontos szempontokat vagy aggályokat
4. A teendőket és azok felelőseit (ha elhangzott)

Az átirat automatikus beszédfelismeréssel készült, ezért tartalmazhat félrehallott szavakat; ahol egyértelmű, értelmezd a szövegkörnyezet alapján.

Kérlek, adj világos, strukturált összefoglalót magyar nyelven.

NE készíts külön szekciót az érthetetlen, nem egyértelmű vagy félrehallott szövegrészekről.

## Prompt: en

Please analyze the meeting transcript you read in step 2 and provide a comprehensive summary that includes:

1. Main topics discussed with all details
2. Key decisions made
3. Important points or concerns raised
4. Action items and their owners (if mentioned)

Please provide a clear, structured summary.

DO NOT include a separate section about unclear, unintelligible or misheard parts of the transcript.
