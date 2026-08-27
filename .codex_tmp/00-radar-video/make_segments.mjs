import fs from "node:fs/promises";
import path from "node:path";

const root = "/Users/ruby/Projects/active-radar-tracker-basics";
const sourcePath = path.join(root, "beginner/ai_audio/00-radar-intuition-audio-script.txt");
const outDir = path.join(root, ".codex_tmp/00-radar-video/audio-segments");
const source = await fs.readFile(sourcePath, "utf8");
const lines = source.split(/\r?\n/);

const segments = [
  { id: "01", title: "Radar intuition", start: 1, end: 3 },
  { id: "02", title: "Four ideas anchor the lesson", start: 5, end: 9 },
  { id: "03", title: "One baseline connects every lesson", start: 11, end: 25 },
  { id: "04", title: "Pulse radar alternates speaking and listening", start: 27, end: 33 },
  { id: "05", title: "The quiet interval makes range measurable", start: 35, end: 41 },
  { id: "06", title: "Longer PRI means more listening, not more transmitting", start: 43, end: 47 },
  { id: "07", title: "Pulse radar is a timing instrument", start: 49, end: 53 },
  { id: "08", title: "The measurement happens while the radar listens", start: 55, end: 57 },
  { id: "09", title: "The radar transmits only two percent of the time", start: 59, end: 61 },
  { id: "10", title: "Delay becomes range through a round trip", start: 63, end: 67 },
  { id: "11", title: "Transmit. Listen. Time the return.", start: 69, end: 75 },
];

await fs.mkdir(outDir, { recursive: true });
for (const segment of segments) {
  const text = lines.slice(segment.start - 1, segment.end).join("\n").trim() + "\n";
  const textPath = path.join(outDir, `slide-${segment.id}.txt`);
  await fs.writeFile(textPath, text);
  segment.textPath = textPath;
  segment.audioPath = path.join(outDir, `slide-${segment.id}.aiff`);
  segment.imagePath = path.join(root, `.codex_tmp/00-radar-video/rendered/slide-${segment.id}.png`);
}

await fs.writeFile(
  path.join(root, ".codex_tmp/00-radar-video/segments.json"),
  JSON.stringify(segments, null, 2),
);

