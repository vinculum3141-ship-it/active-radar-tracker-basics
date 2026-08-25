# Notebook narration workflow

This folder contains the narration script and final audio recording for each notebook. Keep audio work here so generated files do not clutter the notebook directory.

## Approved narration settings

- Voice: `Zoe (Premium)`
- Language/accent: US English
- Reading rate: 145 words per minute (`-r 145`)
- Output: audio-only MP4
- Goal: calm, concrete technical narration optimized for comprehension

## Pause conventions

The macOS `say` command recognizes explicit silence markers in the form `[[slnc milliseconds]]`.

- Before each main heading: `[[slnc 800]]`
- After each main heading: `[[slnc 600]]`
- Between ordinary prose paragraphs: `[[slnc 350]]`
- Between individual baseline/table values: `[[slnc 700]]`
- After the final baseline/table value: `[[slnc 1000]]`
- The numbered subheadings such as “First,” “Second,” “Third,” and “Fourth” use only `[[slnc 600]]` afterward.

Do not rely on blank lines to create audible pauses. Zoe does not always preserve them consistently.

## Preparing a narration script

1. Extract the notebook's explanatory Markdown.
2. Omit executable code, cell output, badges, URLs, and notebook-operation instructions.
3. Omit checkpoint or self-test sections unless they are essential to the explanation.
4. Rewrite tables as spoken prose. Introduce each value separately and do not rush the list.
5. Rewrite notation for speech—for example, use `P R I`, `2.45 gigahertz`, and `20 microseconds`.
6. Prefer concrete physical language over abstract or code-oriented wording.
7. Add the pause markers above.
8. Listen to a draft and revise pronunciation, pacing, and paragraph boundaries before designating the final file.

## File naming

For a notebook named `00-radar-intuition.ipynb`, use:

- Script: `00-radar-intuition-audio-script.txt`
- Final recording: `00-radar-intuition-narration.mp4`

Use descriptive versioned filenames only while comparing drafts. Remove superseded drafts after approving the final recording.

## Rendering

Jamie and Zoe Enhanced/Premium voices require normal macOS user access. Inside the Codex workspace sandbox they may create an empty 0.01-second audio file. Run the `say` step outside the sandbox when prompted for permission.

Render to a temporary AIFF file:

```sh
say -v 'Zoe (Premium)' -r 145 \
  -f beginner/ai_audio/00-radar-intuition-audio-script.txt \
  -o /tmp/00-radar-intuition-narration.aiff
```

Convert it to an audio-only MP4:

```sh
afconvert /tmp/00-radar-intuition-narration.aiff \
  -o beginner/ai_audio/00-radar-intuition-narration.mp4 \
  -f mp4f -d LEI16
```

Verify that the output contains real audio:

```sh
afinfo beginner/ai_audio/00-radar-intuition-narration.mp4
```

Check that `estimated duration` is plausible and not approximately `0.011610 sec`.

## Approved reference recording

The approved `00-radar-intuition` narration uses Zoe Premium at 145 WPM with all pause conventions described above. Its duration is approximately 6 minutes 39 seconds.
