#!/usr/bin/env python3
"""Turn a Teams transcript (JSON/VTT) or an audio recording (M4A/WAV) into a compact text file.

Consecutive messages of the same speaker are merged into one 'Speaker: text' line. Audio is
transcribed locally: afconvert (16 kHz mono WAV) + mlx_whisper CLI (from PATH, else via uvx).
Stdlib only. Prints the output path and size, never the transcript itself.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

UNKNOWN_SPEAKER = 'Unknown Speaker'
AUDIO_EXTENSIONS = ('.m4a', '.wav')
WHISPER_MODEL = 'mlx-community/whisper-large-v3-turbo'
VOICE_PATTERN = re.compile(r'<v\s+([^>]+)>(.*?)(?:</v>|$)', re.DOTALL)


def parse_json(content):
    """Teams JSON: {"entries": [{"speakerDisplayName", "text"}, ...]}"""
    return [(entry.get('speakerDisplayName', UNKNOWN_SPEAKER), entry.get('text', ''))
            for entry in json.loads(content).get('entries', [])]


def parse_vtt(content):
    """Teams WebVTT with <v Speaker>text</v> voice tags."""
    entries = []
    # Cues are separated by blank lines
    for block in re.split(r'\n\s*\n', content.replace('\r\n', '\n')):
        lines = block.strip().split('\n')
        # Cue text is everything after the timing line
        timing_idx = next((i for i, line in enumerate(lines) if '-->' in line), None)
        if timing_idx is None:
            continue  # WEBVTT header, NOTE, STYLE blocks etc.
        cue_text = ' '.join(line.strip() for line in lines[timing_idx + 1:])
        match = VOICE_PATTERN.search(cue_text)
        entries.append((match.group(1).strip(), match.group(2)) if match else (UNKNOWN_SPEAKER, cue_text))
    return entries


PARSERS = {'.json': parse_json, '.vtt': parse_vtt}


def merge_turns(entries):
    """Join consecutive messages of the same speaker; unescape HTML entities (e.g. &#243;)."""
    turns = []
    for speaker, text in entries:
        speaker, text = html.unescape(speaker), html.unescape(text).strip()
        if not text:
            continue
        if turns and turns[-1][0] == speaker:
            turns[-1][1] += ' ' + text
        else:
            turns.append([speaker, text])
    return '\n'.join(f'{speaker}: {text}' for speaker, text in turns)


def transcribe_audio(path, language):
    """Transcript with one whisper segment per line (no speaker names)."""
    whisper = shutil.which('mlx_whisper')
    whisper_cmd = [whisper] if whisper else ['uvx', '--from', 'mlx-whisper', 'mlx_whisper']
    with tempfile.TemporaryDirectory() as tmp_dir:
        wav = Path(tmp_dir) / 'audio.wav'
        commands = [
            ['afconvert', '-f', 'WAVE', '-d', 'LEI16@16000', '-c', '1', str(path), str(wav)],
            [*whisper_cmd, str(wav), '--model', WHISPER_MODEL,
             '--output-format', 'txt', '--output-dir', tmp_dir, '--condition-on-previous-text', 'False'],
        ]
        if language:  # otherwise whisper detects it from the first 30 seconds
            commands[1] += ['--language', language]
        for cmd in commands:
            # Output is captured: whisper echoes every segment, which would flood the caller's context
            result = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
            if result.returncode:
                sys.exit(f"{' '.join(cmd[:3])} failed:\n{result.stderr[-2000:]}")
        return (Path(tmp_dir) / 'audio.txt').read_text(encoding='utf-8').strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('input', type=Path, help='.json, .vtt, .m4a or .wav file')
    parser.add_argument('--lang', help='Spoken language for audio transcription (default: auto-detect)')
    parser.add_argument('--output', type=Path, help='Output file (default: input with .md suffix)')
    args = parser.parse_args()

    suffix = args.input.suffix.lower()
    if suffix in AUDIO_EXTENSIONS:
        print(f'Transcribing {args.input} with {WHISPER_MODEL}...', flush=True)
        text = transcribe_audio(args.input, args.lang)
    elif suffix in PARSERS:
        text = merge_turns(PARSERS[suffix](args.input.read_text(encoding='utf-8-sig')))
    else:
        sys.exit(f"Unsupported file type '{suffix}'. Supported: {[*PARSERS, *AUDIO_EXTENSIONS]}")

    output = args.output or args.input.with_suffix('.md')
    output.write_text(text, encoding='utf-8')
    print(f'Transcript: {output.resolve()} ({text.count(chr(10)) + 1} lines, {len(text)} chars)')


if __name__ == '__main__':
    main()
