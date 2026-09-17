# Notebook narration and presentation-video workflow

This folder contains narration scripts, final audio recordings, editable presentations, and synchronized presentation videos for the beginner notebooks. Keep generated media here so it does not clutter the notebook directory.

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
- Editable presentation: `00-radar-intuition-presentation.pptx`
- Presentation timing: `00-radar-intuition-presentation-timing.tsv`
- Synchronized video: `00-radar-intuition-presentation-video.mp4`

Use descriptive versioned filenames only while comparing drafts. Remove superseded drafts after approving the final recording.

For every notebook that receives a presentation, keep this complete approved set:

1. Narration script (`*-audio-script.txt`)
2. Audio-only narration (`*-narration.mp4`)
3. Editable presentation (`*-presentation.pptx`)
4. Editable transition timing (`*-presentation-timing.tsv`)
5. Synchronized presentation video (`*-presentation-video.mp4`)
6. Shared source template (`Slide_template.pptx`, retained once for the whole folder)

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

## Creating a synchronized presentation video

The presentation video is a separate deliverable from the audio-only narration. It uses the same approved script and voice settings, but the narration is rendered in slide-sized segments so every visual transition has an exact audio boundary.

### Communication goal

Treat each deck as a beginner lesson, not as a notebook screenshot tour. By the end, the viewer should understand the notebook's physical story without needing to read code.

- Give each slide one teaching job and one main claim.
- Use takeaway-style slide titles rather than copying notebook section labels mechanically.
- Keep visible text concise; the narration carries the full explanation.
- Convert equations, tables, and plots into clear visual evidence.
- Preserve the notebook's causal sequence so each slide creates the need for the next.
- Omit code, setup instructions, Colab links, helper APIs, checkpoints, and production notes from audience-facing slides.

### Storyboarding

1. Divide the approved narration script into contiguous slide-sized blocks.
2. Keep every word and silence marker from the approved script; do not paraphrase during video assembly.
3. Aim for roughly 8–12 slides for a 6–10 minute beginner narration, adjusting for the lesson's natural structure.
4. Assign one visual purpose to each block—for example, establish the baseline, show a timing cycle, explain an equation, correct a misconception, or synthesize the lesson.
5. Keep closing-loop answers aligned with visuals that reinforce the relevant concept rather than repeating earlier slides unchanged.

### Approved hybrid visual system

Notebook 00 established the approved hybrid presentation style. It combines the supplied
`Slide_template.pptx` identity with a richer teaching layout:

- 16:9 canvas at 1280 × 720 pixels
- Authentic dark-navy technical artwork from the template on the cover
- Authentic template illustration strip across the top of teaching slides
- Authentic pi mark at the lower-left corner
- Arial typography, matching the template
- Very pale blue-gray teaching canvas with navy typography and fine blue-gray rules
- Template blue (`#4285F4`) for measurements and transformations
- Template orange (`#FFAB40`) for transmission
- Template teal (`#0097A7`) for listening and received information
- At least 50 pt for deck titles, 35 pt for slide titles, 24 pt for subheadings, and 16 pt for body text
- Low-density compositions with generous spacing

Keep the visual explanations from the approved notebook 00 deck: editable tables, timing
bars, equations, comparison arrows, process timelines, metric blocks, and calculation chains.
Do not reduce later lessons to plain title-and-body slides merely to follow the template.
The template provides the visual identity; the lesson content determines the explanatory layout.

### Exact audio synchronization

Do not estimate slide durations from word counts and do not place arbitrary timings on one long audio track.

For each slide:

1. Save its exact contiguous narration block as a temporary `.txt` file.
2. Render that block separately with Zoe Premium at 145 WPM.
3. Measure the resulting audio duration.
4. Keep the corresponding slide onscreen for exactly that duration.
5. Concatenate the audio segments without adding undocumented gaps.

Rendering each segment separately makes the slide boundary deterministic and keeps the approved silence markers inside the relevant section.

### Editable slide-transition timing

For notebook 00, edit `00-radar-intuition-presentation-timing.tsv` when a visual transition
feels early or late. It contains one row per slide and is deliberately tab-separated so it can
be edited in a text editor or spreadsheet.

The currently approved notebook 00 timing uses `0` for every adjustment. The measured narration
boundaries already align correctly with the hybrid slides, so those zero values are intentional,
not unfinished placeholders. Preserve them as the baseline unless a later listening review finds
a specific transition that should move.

The `transition_adjust_ms` column moves the slide change relative to the measured start of its
narration block:

- `0`: use the measured narration boundary
- `-500`: show the new slide half a second earlier
- `350`: keep the previous slide visible for 350 milliseconds longer

Keep slide 1 at `0`. Use the `notes` column to record observations while watching the video.
Timing adjustments change only the visual transition; they do not alter the approved narration,
voice, pauses, or total audio duration. The timing-aware video builder is retained under
`.codex_tmp/00-radar-hybrid/make_timed_video.swift`.

### Video assembly

1. Create and visually verify the editable PowerPoint deck.
2. Render every slide to a 1280 × 720 PNG.
3. Build a still-frame video track whose slide boundaries use the measured segment durations.
4. Place the corresponding audio segments sequentially on one audio track.
5. Export an H.264 MP4 containing one video track and one audio track.

The macOS video encoder and decoder may require normal user access, just like Premium speech voices. If encoding or frame extraction fails inside the workspace sandbox, rerun that media step outside the sandbox when prompted.

### Presentation and video QA

Before approving a lesson video:

1. Render and inspect every slide individually at full size.
2. Check titles for wrapping, tables for legibility, and all shapes for clipping or overlap.
3. Run the presentation overflow test and fix every unintended warning.
4. Confirm that the MP4 duration equals the sum of the narration segments.
5. Confirm the MP4 contains exactly one video track and one audio track.
6. Extract and inspect a frame from every slide interval to confirm the assembled video follows the storyboard.
7. Listen across several slide boundaries to make sure visual changes occur at natural narration transitions.
8. Keep only the approved presentation and video in `beginner/ai_audio`; remove temporary drafts and inspection sidecars.

## Approved presentation reference

The canonical notebook 00 deck is `00-radar-intuition-presentation.pptx`. It uses 11 slides
and is the design reference for later beginner lessons.

The canonical synchronized output is `00-radar-intuition-presentation-video.mp4`. It uses Zoe
Premium at 145 WPM, the approved narration pauses, and the zero-adjustment timing recorded in
`00-radar-intuition-presentation-timing.tsv`. Its verified duration is 395.088 seconds, with one
video track and one audio track.

### Reproducing the hybrid deck

1. Inspect `Slide_template.pptx` and extract its authentic full-slide background, header strip,
   pi mark, Arial typography, and palette.
2. Divide the approved narration into the same 11 contiguous teaching scenes used by notebook 00.
3. Use the template artwork for the cover and slide chrome, but construct each teaching scene
   around the clearest explanatory form: table, timing bar, equation panel, comparison, process,
   metrics, or calculation chain.
4. Preserve the semantic colours consistently: orange means transmit, teal means listen/receive,
   and blue means measurement or transformation.
5. Keep every visible object editable in PowerPoint, except the authentic raster artwork inherited
   from the template.
6. Render and inspect every slide, then run the presentation overflow test before approval.
7. The exact notebook 00 builder and its source/design notes are retained under
   `.codex_tmp/00-radar-hybrid/` so the approved deck can be regenerated.

When a synchronized video is required, reuse the approved 11 Zoe Premium narration segments and
their measured durations. Do not reuse a video rendered from a superseded visual deck.

## Approved reference recording

The approved `00-radar-intuition` narration uses Zoe Premium at 145 WPM with all pause conventions described above. Its duration is approximately 6 minutes 39 seconds.
