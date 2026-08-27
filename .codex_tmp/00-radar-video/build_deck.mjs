import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/ruby/Projects/active-radar-tracker-basics";
const TMP = `${ROOT}/.codex_tmp/00-radar-video`;
const OUT = `${ROOT}/beginner/ai_audio/00-radar-intuition-presentation.pptx`;
const W = 1280;
const H = 720;
const C = {
  white: "#FFFFFF",
  ink: "#0B0D10",
  muted: "#5B6470",
  panel: "#EDEDED",
  rule: "#B8BCC4",
  blue: "#3D8DFF",
  lightBlue: "#D0EDFA",
  green: "#1B9E77",
  orange: "#D95F02",
  pale: "#F7F8FA",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function box(slide, name, x, y, w, h, fill = C.panel, line = "none", radius = "none") {
  return slide.shapes.add({
    geometry: radius === "none" ? "rect" : "roundRect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 },
    ...(radius === "none" ? {} : { borderRadius: radius }),
  });
}

function text(slide, name, value, x, y, w, h, size = 24, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    fontSize: size,
    typeface: "Helvetica Neue",
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "top",
  };
  return shape;
}

function rule(slide, x, y, w, color = C.rule, height = 2) {
  box(slide, `rule-${x}-${y}`, x, y, w, height, color);
}

function chrome(slide, n, eyebrow = "ACTIVE RADAR · NOTEBOOK 00") {
  slide.background.fill = C.white;
  text(slide, `eyebrow-${n}`, eyebrow, 48, 28, 520, 28, 15, { bold: true, color: C.muted });
  text(slide, `page-${n}`, String(n).padStart(2, "0"), 1180, 670, 52, 24, 14, { align: "right", color: C.muted });
  rule(slide, 48, 654, 1184, C.rule, 1);
}

function title(slide, value, n) {
  text(slide, `title-${n}`, value, 48, 68, 1160, 80, 42, { bold: true });
}

function addMetric(slide, x, y, w, value, label, accent = C.blue) {
  rule(slide, x, y, w, accent, 5);
  text(slide, `metric-value-${value}`, value, x, y + 24, w, 68, 42, { bold: true });
  text(slide, `metric-label-${label}`, label, x, y + 92, w, 54, 18, { color: C.muted });
}

function addArrow(slide, x, y, w, h, fill = C.blue) {
  return slide.shapes.add({
    geometry: "rightArrow",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill, width: 0 },
  });
}

const p = Presentation.create({ slideSize: { width: W, height: H } });

// 1 — sparse opening, based on Codex Grid slide 01.
{
  const s = p.slides.add(); chrome(s, 1, "ACTIVE RADAR · BEGINNER SERIES");
  text(s, "cover-title", "Radar intuition\nand baseline parameters", 48, 164, 760, 220, 66, { bold: true, valign: "bottom" });
  text(s, "cover-subtitle", "Transmit briefly. Listen carefully. Turn echo delay into distance.", 48, 430, 720, 76, 25, { color: C.muted });
  box(s, "cover-pulse", 860, 225, 44, 190, C.orange);
  box(s, "cover-listen", 904, 225, 270, 190, C.green);
  text(s, "cover-tx-label", "TX", 860, 430, 44, 30, 16, { bold: true, align: "center", color: C.orange });
  text(s, "cover-rx-label", "LISTEN", 904, 430, 270, 30, 16, { bold: true, align: "center", color: C.green });
}

// 2 — four learning outcomes.
{
  const s = p.slides.add(); chrome(s, 2); title(s, "Four ideas anchor the lesson", 2);
  const items = [
    ["01", "Pulse radar", "Send a short burst, then stop transmitting."],
    ["02", "Listening window", "Give a distant echo time to return."],
    ["03", "Duty cycle", "Measure the fraction of time spent transmitting."],
    ["04", "Delay → range", "Convert round-trip travel time into distance."],
  ];
  items.forEach((it, i) => {
    const x = 48 + (i % 2) * 592;
    const y = 180 + Math.floor(i / 2) * 205;
    text(s, `goal-num-${i}`, it[0], x, y, 62, 42, 18, { bold: true, color: C.blue });
    text(s, `goal-title-${i}`, it[1], x + 72, y, 440, 44, 28, { bold: true });
    text(s, `goal-body-${i}`, it[2], x + 72, y + 56, 440, 74, 20, { color: C.muted });
    rule(s, x, y + 154, 520, C.rule, 1);
  });
}

// 3 — baseline reference table.
{
  const s = p.slides.add(); chrome(s, 3); title(s, "One baseline connects every lesson", 3);
  const rows = [
    ["Carrier frequency", "2.45 GHz", "Wavelength and later Doppler"],
    ["Bandwidth", "5 MHz", "Pulse-compressed range resolution"],
    ["Pulse width", "20 μs", "Duration of each transmitted burst"],
    ["PRI", "1 ms", "Time available before the next pulse"],
    ["Sampling rate", "20 MHz", "20 million recorded samples per second"],
    ["Target range", "1,000 m", "Concrete delay-to-range example"],
  ];
  const x = 48, y = 174, widths = [300, 210, 626], rh = 70;
  ["Quantity", "Value", "Physical role"].forEach((v, i) => {
    const xx = x + widths.slice(0, i).reduce((a,b)=>a+b,0);
    box(s, `head-${i}`, xx, y, widths[i], 50, C.ink);
    text(s, `head-text-${i}`, v, xx + 14, y + 12, widths[i] - 28, 28, 17, { bold: true, color: C.white });
  });
  rows.forEach((r, ri) => r.forEach((v, ci) => {
    const xx = x + widths.slice(0, ci).reduce((a,b)=>a+b,0);
    const yy = y + 50 + ri * rh;
    box(s, `cell-${ri}-${ci}`, xx, yy, widths[ci], rh, ri % 2 ? C.white : C.pale, C.rule);
    text(s, `cell-text-${ri}-${ci}`, v, xx + 14, yy + 18, widths[ci] - 28, 40, ci === 1 ? 22 : 18, { bold: ci === 1, color: ci === 2 ? C.muted : C.ink });
  }));
}

// 4 — timing diagram.
{
  const s = p.slides.add(); chrome(s, 4); title(s, "Pulse radar alternates speaking and listening", 4);
  text(s, "rhythm-copy", "The antenna sends power during a short burst, then becomes a receiver for the remainder of the cycle.", 48, 162, 1080, 58, 23, { color: C.muted });
  box(s, "tx-block", 48, 300, 42, 150, C.orange);
  box(s, "listen-block", 90, 300, 1090, 150, C.green);
  text(s, "listen-inner", "LISTEN FOR THE ECHO", 90, 350, 1090, 40, 28, { bold: true, align: "center", color: C.white });
  text(s, "tx-time", "TX · 20 μs", 48, 470, 130, 34, 18, { bold: true, color: C.orange });
  text(s, "listen-time", "980 μs", 1060, 470, 120, 34, 18, { bold: true, align: "right", color: C.green });
  text(s, "pri-time", "One pulse repetition interval = 1 ms", 390, 540, 450, 34, 22, { bold: true, align: "center" });
}

// 5 — listening rationale and equations.
{
  const s = p.slides.add(); chrome(s, 5); title(s, "The quiet interval makes range measurable", 5);
  text(s, "listen-claim", "A weak returning echo cannot compete with the outgoing transmit signal.", 48, 170, 520, 90, 28, { bold: true });
  text(s, "listen-detail", "The radar stops speaking so it can hear. The pulse width is the transmit interval; the rest of the PRI is the listening window.", 48, 284, 520, 120, 21, { color: C.muted });
  box(s, "formula-panel", 650, 170, 530, 340, C.pale, C.rule);
  text(s, "formula-duty-label", "DUTY CYCLE", 690, 210, 210, 24, 15, { bold: true, color: C.blue });
  text(s, "formula-duty", "D = pulse width / PRI", 690, 246, 430, 52, 30, { bold: true });
  rule(s, 690, 324, 440, C.rule, 1);
  text(s, "formula-range-label", "ROUND-TRIP RANGE", 690, 350, 220, 24, 15, { bold: true, color: C.blue });
  text(s, "formula-range", "R = c × echo delay / 2", 690, 386, 440, 52, 30, { bold: true });
  text(s, "formula-note", "Divide by two: the energy travels out and back.", 690, 458, 420, 34, 18, { color: C.muted });
}

// 6 — misconception correction.
{
  const s = p.slides.add(); chrome(s, 6); title(s, "Longer PRI means more listening—not more transmitting", 6);
  text(s, "mistake-label", "COMMON MISREAD", 48, 178, 240, 28, 16, { bold: true, color: C.orange });
  text(s, "mistake", "“A longer interval means the radar transmits more often.”", 48, 222, 500, 96, 28, { bold: true });
  text(s, "correction-label", "PHYSICAL RESULT", 676, 178, 220, 28, 16, { bold: true, color: C.green });
  text(s, "correction", "The pulse stays 20 μs. The listening window grows, so duty cycle falls.", 676, 222, 500, 96, 28, { bold: true });
  addArrow(s, 570, 250, 76, 42, C.blue);
  box(s, "delay-callout", 48, 398, 1128, 130, C.pale);
  text(s, "delay-big", "Delay is not a technical detail—it is the measurement.", 82, 432, 1060, 54, 32, { bold: true, align: "center" });
}

// 7 — three-step process based on Codex Grid timeline.
{
  const s = p.slides.add(); chrome(s, 7); title(s, "Pulse radar is a timing instrument", 7);
  const xs = [80, 470, 860];
  const labels = ["TRANSMIT", "LISTEN", "TIME THE RETURN"];
  const bodies = ["Create a precisely timed event.", "Wait for reflected energy.", "Use the delay as a distance measurement."];
  rule(s, 100, 330, 1000, C.ink, 2);
  xs.forEach((x, i) => {
    const dot = s.shapes.add({ geometry: "ellipse", position: { left: x, top: 318, width: 26, height: 26 }, fill: i===0?C.orange:(i===1?C.green:C.blue), line: { style:"solid", fill:"none", width:0 } });
    text(s, `process-label-${i}`, labels[i], x, 258, 280, 34, 18, { bold: true, color: i===0?C.orange:(i===1?C.green:C.blue) });
    text(s, `process-body-${i}`, bodies[i], x, 380, 280, 86, 24, { bold: true });
  });
}

// 8 — baseline timing metrics.
{
  const s = p.slides.add(); chrome(s, 8); title(s, "The measurement happens while the radar listens", 8);
  addMetric(s, 48, 188, 330, "20 μs", "Transmit: the radar speaks", C.orange);
  addMetric(s, 474, 188, 330, "980 μs", "Listen: the echo can return", C.green);
  addMetric(s, 900, 188, 280, "1 ms", "One complete PRI", C.blue);
  box(s, "listening-message", 48, 430, 1132, 130, C.pale);
  text(s, "listening-message-text", "The listening window is not idle time. It is where the measurement actually happens.", 88, 466, 1052, 56, 30, { bold: true, align: "center" });
}

// 9 — duty cycle split.
{
  const s = p.slides.add(); chrome(s, 9); title(s, "The radar transmits only two percent of the time", 9);
  text(s, "duty-equation", "20 μs ÷ 1 ms = 0.02", 48, 170, 520, 62, 34, { bold: true });
  text(s, "duty-copy", "Duty cycle asks what fraction of each interval is spent transmitting.", 48, 246, 520, 76, 22, { color: C.muted });
  box(s, "duty-tx", 48, 404, 23, 112, C.orange);
  box(s, "duty-listen", 71, 404, 1109, 112, C.green);
  text(s, "duty-2", "2% TX", 48, 536, 160, 40, 22, { bold: true, color: C.orange });
  text(s, "duty-98", "98% LISTEN", 950, 536, 230, 40, 22, { bold: true, align: "right", color: C.green });
}

// 10 — delay/range chain and quantization.
{
  const s = p.slides.add(); chrome(s, 10); title(s, "Delay becomes range through a round trip", 10);
  const steps = [
    ["1,000 m", "Target range"],
    ["6.67 μs", "Round-trip delay"],
    ["133", "Recorded samples"],
    ["996.8 m", "Quantized estimate"],
  ];
  steps.forEach((st, i) => {
    const x = 48 + i * 292;
    box(s, `range-step-${i}`, x, 210, 236, 176, i===3?C.lightBlue:C.pale, C.rule);
    text(s, `range-value-${i}`, st[0], x + 18, 248, 200, 58, 34, { bold: true, align: "center" });
    text(s, `range-label-${i}`, st[1], x + 18, 320, 200, 38, 17, { align: "center", color: C.muted });
    if (i < 3) addArrow(s, x + 246, 274, 36, 34, C.blue);
  });
  text(s, "range-formula", "R = c × delay / 2", 48, 440, 420, 54, 30, { bold: true });
  text(s, "quantization", "The 3.2 m gap is sample quantization: the true delay falls between two recorded sample boundaries.", 520, 432, 660, 92, 22, { color: C.muted });
}

// 11 — deliberate synthesis close.
{
  const s = p.slides.add(); chrome(s, 11, "ACTIVE RADAR · FOUNDATION COMPLETE");
  text(s, "close-title", "Transmit. Listen.\nTime the return.", 48, 152, 760, 180, 62, { bold: true, valign: "bottom" });
  text(s, "close-copy", "Careful timing turns an echo delay into a physical measurement with meaning.", 48, 378, 700, 82, 25, { color: C.muted });
  const vals = [["2%", "transmit", C.orange], ["98%", "listen", C.green], ["133", "samples", C.blue]];
  vals.forEach((v,i)=>{
    const x=850;
    const y=150+i*130;
    text(s, `close-value-${i}`, v[0], x, y, 160, 60, 38, { bold:true, color:v[2] });
    text(s, `close-label-${i}`, v[1].toUpperCase(), x+170, y+13, 230, 36, 17, { bold:true, color:C.muted });
  });
}

await fs.mkdir(`${TMP}/rendered`, { recursive: true });
for (const [index, slide] of p.slides.items.entries()) {
  const id = String(index + 1).padStart(2, "0");
  await writeBlob(`${TMP}/rendered/slide-${id}.png`, await p.export({ slide, format: "png", scale: 1 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(`${TMP}/rendered/slide-${id}.layout.json`, await layout.text());
}
await writeBlob(`${TMP}/deck-montage.webp`, await p.export({ format: "webp", montage: true, scale: 1 }));
const pptx = await PresentationFile.exportPptx(p);
await pptx.save(OUT);
