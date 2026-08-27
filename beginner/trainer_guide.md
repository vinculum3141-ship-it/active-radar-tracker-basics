# Beginner Handbook

This handbook is the trainer-facing guide for the learner notebooks.
Each chapter corresponds to one notebook and gives the presentation flow,
background context, learner questions, and the story arc that ties the course
into a coherent whole.

The goal is not to repeat the notebook line by line. The goal is to make it easy
to present the notebook confidently, with enough background to explain the radar
choices and enough structure to keep the course story coherent from chapter to
chapter.

## How to use this handbook

- Read the chapter before you teach the notebook.
- Use the chapter as your talk track for the lesson.
- Use the background section to explain where the radar reference values come
  from in real engineering practice.
- Use the learner questions to check understanding before moving on.
- Add the next chapter when the next notebook is built.

---

## Chapter 00 — Radar Intuition and Baseline Parameters

### Chapter purpose

This chapter gives the learner the first mental model of pulse radar. It
establishes the idea that a radar transmits a short burst, listens in the quiet
interval, and uses echo delay to infer range. It also introduces the shared
baseline radar reference values used throughout the beginner track.

### Teaching goal in one sentence

Help the learner understand that pulse radar works by transmitting briefly,
waiting quietly, and using the return delay as the physical measurement of
range.

### What the trainer should emphasize

- Pulse radar is a timing system before it is a signal-processing system.
- The quiet listening window is essential, not optional.
- Range is inferred from delay, so the delay is the star of the lesson.
- The shared radar reference values are there to make every later notebook use
  the same physical situation.

### Suggested presentation flow

#### 1. Start with the radar story, not the math

Open by describing pulse radar in plain language.

The core idea is simple:

- the radar sends a short burst of energy,
- it stops transmitting,
- it listens for the echo,
- and the echo delay tells us how far away the target is.

Use the analogy already written in the notebook: the radar cannot listen while
it is speaking. That idea should sound obvious before any equations appear.

If the learner is brand new, keep the first explanation very concrete. Say that
a radar is measuring how long it takes for its own energy to leave, bounce off a
target, and come back.

#### 2. Introduce the baseline radar reference table

The table in the notebook is the first time the learner sees the numbers.
Do not rush this section. Walk through each value and connect it to the radar
story:

- Carrier frequency: sets the wavelength and later Doppler sensitivity.
- Bandwidth: sets the resolution potential once pulse compression appears.
- Pulse width: how long the transmitter is on.
- PRI: how long the radar waits before the next pulse.
- Sampling rate: how finely the received signal is recorded in time.
- Target range: the worked example used to turn delay into range.

Make it clear that this is a baseline teaching case, not a magical universal
radar configuration.

#### 3. Explain where these values come from in a real radar design

This is the background that helps the learner understand that engineering
values are usually derived, not guessed.

A real radar designer typically starts with requirements and works backward:

1. What is the mission?
   - Air surveillance, vehicle tracking, short-range sensing, drone detection,
     or something else.
2. What range accuracy is needed?
   - This drives the bandwidth choice because range resolution depends on it.
3. What target ranges must be covered?
   - This affects PRI and unambiguous range.
4. What velocity or Doppler behavior must be measured?
   - This influences carrier frequency, pulse repetition interval, and CPI
     length.
5. What hardware is available?
   - RF front-end limits, clock rate, ADC speed, antenna size, power budget,
     and legal band restrictions all matter.

So the reference values in this chapter are a simplified outcome of that
process. They are chosen so the learner can see the radar equations cleanly,
while still being plausible enough to resemble a real design.

A practical engineer would usually iterate:

- choose an operating band that is legal and suitable,
- choose a bandwidth that matches the range-resolution goal,
- choose a pulse width and PRI that balance energy, listening time, and
  unambiguous coverage,
- then check whether the hardware can sample the signal at the needed rate.

Tell the learner that real systems rarely arrive at their final numbers in one
step. They are the result of trade-offs.

#### 4. Explain the equations in words before showing the cell output

The notebook already prints the math explicitly. When presenting it, say:

- Duty cycle is the fraction of time the radar is transmitting.
- Round-trip delay is the time for the pulse to travel to the target and back.
- Range is inferred from that delay because the radar knows the propagation
  speed.
- Wavelength connects carrier frequency to later Doppler and array topics.

The learner should hear the meaning first, then see the calculation.

#### 5. Walk through the explicit calculation cell slowly

When showing the handwritten-equation cell, read it as a story:

- compute duty cycle from pulse width and PRI,
- compute round-trip delay from range,
- convert delay into samples using the sample rate,
- convert those samples back into range,
- compute wavelength from carrier frequency.

Point out that this is the same physics the helpers will later package up.
The notebook is showing the equations once so the learner sees the chain.

#### 6. Transition to the helper-based version

Tell the learner why the helper functions exist:

- they keep the same formulas available later,
- they reduce repeated code,
- and they make later notebooks easier to read once the idea is already known.

This is the right place to say:

- first we learn it by hand,
- then we reuse it through helpers.

Make the helper cell feel like a second view of the same idea, not a new idea.

#### 7. Use the checkpoint to force verbal understanding

The checkpoint should be answered out loud or in writing before moving on.
The learner should be able to say:

- the radar must listen after it transmits because the echo needs time to come back,
- a longer PRI means more listening time and therefore a smaller duty cycle,
- the delay is not a side detail; it is the range measurement.

#### 8. Use the common-mistake note as a teaching moment

The common mistake is that learners may think a longer PRI means more
transmitting. It does not. It means less transmit time per unit time and more
listening time.

Also emphasize that beginners often treat delay as a mathematical nuisance.
You should correct that by saying delay is the core radar observable in this
lesson.

#### 9. Close with the answers section and the narrative Summary

The notebook now contains a "Closing the loop" section near the end that answers
the four opening questions directly. Use it as your recap device:

- ask the learner to answer each opening question themselves first,
- then read or paraphrase the matching narrative answer,
- point back at the timing diagram, the duty-cycle equation, and the
  delay-to-range steps in the calculation cell while you do.

Note that the answers section deliberately explains why the estimated range is
996.8 m instead of exactly 1000 m; that is sample quantization, and naming it
here prevents confusion later when resolution is discussed.

After closing the loop, deliver the narrative Summary. The Summary should sound
like a short explanation of the radar system, not a list of formulas.

Say that the learner has now seen the basic pulse-radar cycle:

- transmit a short burst,
- listen in the quiet interval,
- use the echo delay to estimate range,
- and use a shared radar reference case to keep the rest of the course aligned.

The point of the summary is to connect the lesson to real radar practice:
radar is an engineered timing problem that turns a returning echo into useful
information about the world.

### How to explain the reference values in real-world terms

Use this wording if the learner asks why the numbers look so specific:

- 2.45 GHz is a convenient example frequency because it has a meaningful
  wavelength and sits in a commonly recognized band.
- 5 MHz bandwidth is enough to demonstrate useful range resolution in a simple
  teaching setup.
- 20 microseconds pulse width gives a short burst that is easy to reason about.
- 1 millisecond PRI creates a clear listening window and a large unambiguous
  range for the teaching case.
- 20 MHz sample rate is comfortably above the signal bandwidth and makes the
  sample calculations easy.
- 1000 m target range is a round-number example that produces a visible delay.

Then add the engineering caveat:
real radar values are chosen by balancing mission goals, legal constraints,
hardware limits, and the physics of the waveform. The notebook uses fixed values
because it is a lesson, not a design report.

### Likely learner questions and answers

#### Why not transmit continuously?

Because the radar would be trying to hear while it is still speaking. The echo
would be hidden under the outgoing signal.

#### Why is the PRI longer than the pulse width?

So the radar has time to listen after it transmits. The quiet part is the
measurement part.

#### Why does the notebook use a baseline spec object?

Because later notebooks need the same radar values. The object keeps those values
in one named place instead of scattering them through the code.

#### Why show the math once and then use helpers?

Because the learner should see the equation first, then see the reusable code
version. That teaches both understanding and clean reuse.

### Delivery notes

- Pause after each major explanation block.
- Do not rush the baseline table.
- Keep the tone concrete and physical.
- If the learner seems lost, return to the transmit/listen story before going
  back to equations.
- The goal is comprehension, not speed.

### One-sentence close

Pulse radar works because it sends a short burst, listens in the quiet window,
and measures the echo delay; this notebook gives the learner the first clear
picture of that cycle.

---

## Chapter 01 — Pulse Generation and Chirp Intuition

### Chapter purpose

This chapter takes the learner inside the transmit burst and builds the actual
waveform. It shows how a plain rectangular pulse becomes a frequency-swept LFM
chirp, and why that sweep gives the radar much finer range resolution than the
pulse length alone would allow. It is still about building the transmit signal,
not the full receive-and-track chain.

### Teaching goal in one sentence

Help the learner understand that a chirp keeps the pulse long and energetic while
its frequency sweep provides the bandwidth that sets range resolution.

### What the trainer should emphasize

- The rectangular pulse is just "transmitter on for the pulse width."
- The chirp's difference from the plain pulse is in frequency, not amplitude.
- Range resolution is a bandwidth story: chirp resolution is `c / (2B)`, not
  `c * tau / 2`.
- The time-bandwidth product `B * tau` is the compression gain that makes the
  long pulse useful.
- The matched filter is the mechanism that collapses the long chirp into a peak;
  Notebook 04 will convert that peak into range.

### Suggested presentation flow

#### 1. Start with the waveform, not the math

Open by reminding the learner that Notebook 00 treated the burst as a time
interval. Now we look inside that interval and ask what actually leaves the
antenna.

Say plainly:

- a rectangular pulse is the transmitter simply on at full amplitude,
- an LFM chirp is the same length but with frequency sliding during the pulse,
- the chirp looks similar in amplitude, so the difference hides in phase.

Keep this concrete: the learner should picture a block of energy before any
formula appears.

#### 2. Build the rectangular pulse cell

Show that the pulse is `N = fs * tau` samples of ones. Point out that the number
of samples is set entirely by the sampling rate and pulse width from the baseline
spec. This is the simplest possible waveform and the baseline for comparison.

Do not over-explain here. The pulse is the control case; the chirp is the star.

#### 3. Introduce the LFM chirp formula in words first

Before showing the cell, say the chirp has the same length but its frequency
rises from zero to the bandwidth `B` across the pulse. The complex baseband form
is

`exp(j * pi * (B / tau) * t^2)`

where `B / tau` is the chirp rate. Emphasize that the frequency covered, `B`, can
be far larger than `1 / tau` — that extra bandwidth is the resolution payoff.

#### 4. Walk through the chirp construction cell

Read the cell as a story:

- build the time vector,
- compute the chirp rate `B / tau`,
- form the quadratic phase,
- take the complex exponential,
- estimate the instantaneous frequency from the phase slope.

Point out that the stop frequency should equal the bandwidth. That check is the
learner's first confidence that the sweep is correct.

#### 5. Show the two waveforms in time

Use the time-domain plot to show that both waveforms look like constant-amplitude
bursts. Say clearly: the time plot alone does not reveal the chirp. This sets up
the frequency view as the revealing one.

#### 6. Show the frequency sweep

The frequency-ramp plot is the key visual. Walk the learner along the line: it
starts at zero and climbs steadily to `B`. Contrast with the plain pulse, which
has no sweep at all. This is the moment the chirp becomes distinct.

#### 7. Explain range resolution before the numbers

State the two formulas in words:

- plain pulse: resolution scales with pulse length,
- chirp: resolution scales with bandwidth after compression.

Then show the cell so the learner sees the arithmetic and the improvement factor.

Make the teaching point explicit: the chirp is long for energy but sharp for
resolution, and bandwidth is what decouples the two.

#### 8. Explain the time-bandwidth product

Introduce `TBP = B * tau` as the compression factor. With the baseline values it
is a round 100, so the long pulse compresses by about 100x. Tell the learner
this is the central trade that makes modern pulse radar practical: stay loud, get
sharp.

#### 9. Use the checkpoint to force verbal understanding

The checkpoint should be answered out loud or in writing. The learner should be
able to say:

- a chirp resolves better than a same-length pulse because bandwidth, not length,
  sets the resolution,
- increasing `B` at fixed `tau` raises the time-bandwidth product and improves
  (shrinks) the range resolution.

#### 10. Use the common-mistake note as a teaching moment

The common mistake is to think pulse length alone sets resolution. Correct it by
restating that for a chirp, bandwidth sets the resolution while the pulse length
stays free for energy.

Also warn that the chirp's time plot looks like "just a weird pulse." Resolution
lives in the frequency sweep, so always check the frequency view.

#### 11. Transition to the helper-based version

Tell the learner why the helper functions exist:

- they keep one correct waveform definition for every later notebook,
- they reduce repeated code,
- and they make later cells shorter once the idea is known.

Make the helper cell feel like a second view of the same idea, not a new idea.

#### 12. Close with the matched-filter preview

The compression plot is the payoff visual. Show that the plain-pulse filter
output stays wide while the chirp collapses to a narrow peak. Say that this sharp
peak is the object Notebook 04 will turn into a range estimate.

Keep the preview forward-looking: the learner has now built the transmit
waveform; the matched-filter output is the bridge to the next notebooks where
the echo is received and turned into a measurement.

#### 13. Close the loop on the opening questions and the narrative Summary

The notebook now contains a "Closing the loop" section that answers the four
opening questions directly. Use it as your recap device:

- ask the learner to answer each opening question themselves first,
- then read or paraphrase the matching narrative answer,
- point back at the resolution comparison cell, the matched-filter plot, and the
  time-bandwidth product while you do.

After closing the loop, deliver the narrative Summary. The Summary should sound
like a short explanation of the chirp, not a list of formulas.

Say that the learner has now built two waveforms and understood the core trade:

- the plain pulse is short and limited in resolution by its length,
- the chirp sweeps frequency across a wide bandwidth,
- that bandwidth, not the pulse length, sets the range resolution after
  compression,
- and the time-bandwidth product captures the compression gain.

The point of the summary is to connect the waveform lesson to the next step:
Notebook 04 will take the compressed peak and turn it into a range estimate.

### How to explain the waveform choices in real-world terms

Use this wording if the learner asks why the numbers look specific:

- The baseline pulse width of 20 microseconds is long enough to carry useful
  energy but short enough to reason about directly.
- The 5 MHz bandwidth is the sweep range that gives a clean, visible compression
  gain over the pulse length.
- Staying at baseband (frequency sweep from 0 to `B`) keeps the math simple while
  still showing the real LFM idea used in radio-frequency radars.

Then add the engineering caveat: real waveforms are chosen by trading energy,
resolution, hardware bandwidth, and legal spectral limits. The notebook uses
fixed values because it is a lesson, not a waveform design report.

### Likely learner questions and answers

#### Why not just use a short pulse for good resolution?

Because a very short pulse has little energy, so the echo is weak. The chirp keeps
the pulse long for energy and uses bandwidth for resolution instead.

#### Why does the chirp look like a normal pulse in the time plot?

Because the sweep changes the phase, not the amplitude. The resolution lives in
the frequency view, which is why the frequency-ramp plot matters.

#### Why show the math once and then use helpers?

Because the learner should see the quadratic phase first, then see the reusable
code version. That teaches both understanding and clean reuse.

#### What is the matched filter doing in the preview?

It correlates the received waveform with a reversed, conjugated copy of the
transmit waveform. For the chirp this collapses a long pulse into a sharp peak,
which is the start of range measurement.

### Delivery notes

- Pause after the frequency-sweep plot; it is the conceptual turning point.
- Do not rush the resolution comparison; the numbers are the lesson.
- Keep the tone physical: loud versus sharp, long versus narrow.
- If the learner seems lost, return to "the chirp is a long pulse that sweeps
  frequency" before going back to formulas.
- The goal is comprehension, not speed.

### One-sentence close

A chirp keeps the transmit pulse long and energetic while its frequency sweep
provides the bandwidth that sets range resolution; this notebook gives the
learner the first clear picture of pulse compression.

---

## Chapter 02 — The Radar Equation

### Chapter purpose

This chapter explains why radar echoes are so weak and introduces the radar
equation as the physics foundation for everything on the receive side. It gives
the learner the quantitative understanding for why attenuation is so large and
why signal processing is essential.

### Teaching goal in one sentence

Help the learner understand that the radar equation connects transmitted power,
range, and target properties to the received signal level, and that the 1 / R⁴
dependence is why echoes are so weak.

### What the trainer should emphasize

- The signal spreads twice (out and back), giving 1 / R⁴, not 1 / R².
- The radar cross section is a target property, not a system parameter.
- The −40 dB used in later notebooks comes from this equation, not from
  arbitrary choice.
- This is the physics that motivates the matched filter.

### Suggested presentation flow

#### 1. Bridge from the transmit side

Open by reminding the learner that Notebooks 00 and 01 built the transmit
waveform. Now we ask: once the pulse leaves the antenna, how much comes back?

#### 2. Build the intuition before the equation

Explain the four losses in plain language:

- outward spreading (1 / R²),
- target interception (radar cross section),
- return spreading (another 1 / R²),
- system losses.

The two spreading losses combine to give 1 / R⁴. Make sure the learner
understands this is a round-trip effect.

#### 3. Introduce the radar equation

Show the equation and walk through each term. Do not rush — the learner should
understand what each symbol means before moving on.

#### 4. Show the 1 / R⁴ curve

The log–log plot is the key visual. Walk the learner along the curve: a factor
of 10 in range gives a factor of 10,000 in received power. Mark the baseline
target on the curve.

#### 5. Compute the round-trip loss

Show the loss factor computation by hand. The learner should see the number
and understand it is tiny.

#### 6. Connect to the −40 dB

This is the bridge to the next notebook. Explain that the −40 dB attenuation
comes from the radar equation with plausible parameters. The learner should
understand it is physics, not a magic number.

### Likely learner questions and answers

#### Why is it R⁴ and not R²?

Because the signal makes a round trip. It loses as 1 / R² on the way out and
1 / R² on the way back. Multiplying gives 1 / R⁴.

#### What is radar cross section?

It measures how much energy the target reflects back toward the radar, expressed
as an equivalent area. A large aircraft might be 100 m²; a small drone might be
0.01 m².

### Delivery notes

- Pause after the 1 / R⁴ plot; it is the conceptual turning point.
- Make sure the learner understands −40 dB is not arbitrary before moving on.
- Keep the tone physical: spread, reflect, spread again.

### One-sentence close

The radar equation shows that received power falls as 1 / R⁴ because the
signal spreads on both legs of the round trip; this notebook gives the learner
the physics foundation for why attenuation is so large and matched filtering
is essential.

---

## Chapter 03 — Channel Model and Echoes

### Chapter purpose

This chapter takes the learner across to the receive side for the first time.
It builds the channel model step by step — delay, attenuation, noise — and
shows why the echo is hard to see without processing. It also gives the learner
the physical intuition for why the matched filter exists.

### Teaching goal in one sentence

Help the learner understand that the received signal is a known transmitted
waveform, shifted and scaled, buried in noise — and that the matched filter is
the tool that pulls it out.

### What the trainer should emphasize

- The echo is a copy of the transmitted pulse, not a different waveform.
- Delay is deterministic (set by range), while noise is random.
- Attenuation and noise are different things and must not be confused.
- The three-panel plot is the key visual: clean pulse, weak echo, noisy mess.
- The matched filter in Notebook 03 solves the problem this chapter introduces.

### Suggested presentation flow

#### 1. Bridge from Notebooks 00, 01, and 02

Open by reminding the learner that the transmit side is done. The pulse and
chirp are built, duty cycle and resolution are understood. Now the pulse
travels to the target and comes back. Say simply: we are crossing the gap
between the antenna and the receiver.

#### 2. Present the channel model as three things

Before any code, describe what the channel does in plain language:

- it delays the pulse (range turns into time),
- it weakens the echo (path and target losses),
- it adds noise (receiver electronics).

Keep the picture concrete: a pulse leaves, bounces, comes back smaller, and
lands in a noisy buffer.

#### 3. Build the delay cell

Show the delay arithmetic — the same `delay_samples_for_range` calculation
from Notebook 00, now used to know where in the received buffer the echo
should land. Point out that the buffer must be at least `n_delay + pulse_length`
samples long.

#### 4. Build the echo by shifting

Show the copy operation: write the pulse into the buffer at the right slot.
This is the "delay" part of the channel. Say that the echo shape is identical
to the transmitted pulse — only its position changes.

#### 5. Add attenuation

Explain the dB-to-linear conversion and why we use -40 dB. Point out that the
echo amplitude is now 0.01 — a hundred times weaker in amplitude, ten thousand
times weaker in power. This is realistic for a radar at moderate range.

#### 6. Add noise

Explain the SNR and how noise power is derived from the echo power. At 20 dB
the echo is still 100 times stronger than the noise in power, but because the
noise is spread across the whole buffer while the echo is concentrated, it can
still be hard to spot by eye.

#### 7. Walk through the three-panel plot slowly

This is the key visual. Read it as a story:

- top: the clean transmitted pulse,
- middle: the attenuated echo — recognisable, just much smaller,
- bottom: the noisy received signal — the echo disappears into the fluctuations.

Ask the learner: can you see the echo in the bottom panel? The answer is usually
no, or only barely. That is the moment to say: this is why the matched filter
exists.

#### 8. Use the stretch exercise for advanced learners

The second-target cell is optional. If time allows, show what two echoes look
like in the same buffer. This sets up the multi-target problem that later
notebooks address.

#### 9. Use the checkpoint to force verbal understanding

The checkpoint should be answered out loud or in writing. The learner should be
able to say:

- the channel delays, attenuates, and adds noise,
- doubling the range doubles the delay but does not change the pulse shape,
- attenuation and noise are different things.

#### 10. Use the common-mistake note as a teaching moment

The common mistake is confusing attenuation with noise. Attenuation scales the
echo down deterministically; noise adds random fluctuations. Correct it by
pointing back at the middle panel (attenuation only) versus the bottom panel
(attenuation plus noise).

Also correct the idea that the echo is a different waveform. It is a copy — same
shape, shifted and scaled.

#### 11. Transition to the helper-based version

Tell the learner why the helper functions exist:

- `add_echo` places a delayed, attenuated copy in one call,
- `awgn` adds noise to a target SNR,
- `single_target_channel` runs the full pipeline.

Make the helper cell feel like a second view of the same idea, not a new idea.

#### 12. Close with the answers section and the narrative Summary

Use the "Closing the loop" section as your recap device:

- ask the learner to answer each opening question themselves first,
- then read or paraphrase the matching narrative answer,
- point back at the three-panel plot and the delay calculation while you do.

After closing the loop, deliver the narrative Summary. The Summary should sound
like a short explanation of the receive side, not a list of formulas.

Say that the learner has now built the full channel:

- the pulse is delayed by the round-trip travel time,
- attenuated by path and target losses,
- and corrupted by receiver noise.

The point of the summary is to connect the channel to the next step: the
matched filter in Notebook 03 is the tool that pulls the echo out of the noise.

### How to explain attenuation in real-world terms

Use this wording if the learner asks why we use -40 dB:

- the echo power depends on the target radar cross section, the range to the
  fourth power, and the system losses,
- -40 dB amplitude is a convenient teaching value that produces a visible but
  clearly weakened echo,
- real attenuation varies with target type, range, and frequency, and is one of
  the main reasons radar design involves careful link-budget analysis.

### Likely learner questions and answers

#### Why not just make the transmitted pulse stronger?

Because legal limits, hardware constraints, and power consumption bound the
transmit power. The radar must work with the echo it gets, which is why
processing matters.

#### Is the noise always Gaussian?

Not always, but Gaussian thermal noise is a good first model and the standard
assumption for matched-filter theory. Non-Gaussian clutter is addressed in
more advanced courses.

#### Why does the matched filter work?

Because it correlates the received signal with the known transmitted shape.
The echo is a match; the noise is not. The filter output peaks at the echo
delay and stays low elsewhere.

### Delivery notes

- Pause after the three-panel plot; it is the conceptual turning point.
- Do not rush the attenuation and noise cells; the numbers are the lesson.
- Keep the tone physical: shift, weaken, corrupt.
- If the learner seems lost, return to "the echo is a copy of the transmitted
  pulse" before going back to the math.
- The goal is comprehension, not speed.

### One-sentence close

The channel shifts the transmitted pulse by the round-trip delay, weakens it
by the path losses, and adds receiver noise; this notebook gives the learner the
first clear picture of why the matched filter is needed.

---

## Chapter 04 — Matched Filtering and Range Estimation

### Chapter purpose

This chapter is the payoff for everything built so far. It takes the transmit
waveform from Notebook 01, the channel model from Notebook 03, and produces a
range estimate — the first complete radar measurement in the course. It also
explains why matched filtering is superior to thresholding the raw received
signal.

### Teaching goal in one sentence

Help the learner understand that correlation with the known transmitted shape
concentrates the echo into a sharp peak whose location gives the range
estimate.

### What the trainer should emphasize

- The matched filter exploits knowledge the radar already has: the transmitted
  waveform.
- The output peaks at the echo delay, not at the echo amplitude.
- The chirp peak is sharper because bandwidth sets the compressed width, not
  pulse length.
- Thresholding fails because noise can exceed the echo on individual samples.
- This notebook is the first complete radar measurement in the course.

### Suggested presentation flow

#### 1. Bridge from Notebooks 00 through 02

Open by reminding the learner of the story so far:

- Notebook 00 introduced range, delay, and duty cycle.
- Notebook 01 built the transmit waveform and showed why chirps buy resolution.
- Notebook 03 showed the channel — delay, attenuation, noise — and ended with
  the echo buried in the received signal.

Say simply: the echo is there, but you cannot see it. The matched filter is the
tool that pulls it out.

#### 2. Explain the matched filter in words before the equation

Say the radar already knows the shape it transmitted. The matched filter slides
a copy of that shape across the received signal and measures how well they line
up at each position. Where the shapes match, the output is large. Where they
do not, the output stays low.

Only after that intuition should you show the correlation equation. The learner
should hear "slide, multiply, sum, look for the peak" before seeing the math.

#### 3. Build the received signal

Use the channel from Notebook 03: one rectangular pulse, one echo at the
baseline range, -40 dB attenuation, 20 dB SNR. The learner should recognise
this as the same received signal they saw in the previous notebook.

#### 4. Walk through the correlation-by-hand cell

Read the cell as a story:

- slide the transmitted pulse across the received signal,
- multiply overlapping samples,
- sum at each position,
- the result is a vector with a peak at the echo delay.

Point out that the peak index must be converted to a lag by subtracting
`len(pulse) - 1` because of the `full`-mode correlation convention.

#### 5. Show the two-panel comparison plot slowly

This is the key visual. Read it as a story:

- top: the raw received signal — echo invisible in noise,
- bottom: the matched-filter output — echo as a clear peak.

Ask the learner: can you see the echo in the top panel? The answer is usually
no. Then ask: can you see it in the bottom panel? The answer is yes. That is
the matched-filter gain.

#### 6. Explain why thresholding fails

Use the threshold cell to show that the raw signal peak is not at the echo
location, and that multiple samples exceed the threshold. The matched filter
avoids this because it accumulates energy across the entire pulse length, not
just one sample.

#### 7. Repeat with the chirp

Show the chirp overlay plot. The chirp peak is sharper because its bandwidth is
larger. Point back to Notebook 01's resolution formulas: the compressed width
is set by 1/B, not by tau.

#### 8. Use the checkpoint to force verbal understanding

The checkpoint should be answered out loud or in writing. The learner should be
able to say:

- the matched filter slides a copy of the transmitted shape and looks for the
  peak,
- the chirp peak is narrower because bandwidth, not pulse length, sets the
  compressed width,
- the peak gives a sample delay, which converts to range with the round-trip
  formula.

#### 9. Use the common-mistake note as a teaching moment

The common mistake is thinking the matched filter amplifies the signal. It does
not; it concentrates energy into a narrow peak by coherently adding across the
pulse length. The peak is higher because energy is compressed in time.

Also correct the idea that the peak index is directly a range. It is a sample
delay, and the range equation converts it.

#### 10. Transition to the helper-based version

Tell the learner why the helper functions exist:

- `matched_filter` runs the correlation in one call,
- `range_from_delay_samples` converts the delay to range.

Make the helper cell feel like a second view of the same idea, not a new idea.

#### 11. Close with the answers section and the narrative Summary

Use the "Closing the loop" section as your recap device:

- ask the learner to answer each opening question themselves first,
- then read or paraphrase the matching narrative answer,
- point back at the two-panel plot, the threshold cell, and the chirp overlay
  while you do.

After closing the loop, deliver the narrative Summary. The Summary should sound
like a short explanation of the matched filter, not a list of formulas.

Say that the learner has now completed the first full radar measurement:

- the transmit waveform was built in Notebook 01,
- the channel placed an echo in Notebook 02,
- and the matched filter pulled it out and converted it to a range estimate here.

The point of the summary is to connect the matched filter to the rest of the
course: every range measurement in a pulse radar starts with this operation.

### Likely learner questions and answers

#### Why not just look for the loudest sample?

Because noise can be louder than the echo on any single sample. The matched
filter accumulates energy across the entire pulse, so the echo contribution
grows while the noise averages out.

#### Why is the chirp peak narrower?

Because the compressed width is set by the bandwidth, not the pulse length.
The chirp has a much larger bandwidth than the rectangular pulse, so its
compressed peak is proportionally narrower.

#### Does the matched filter work for any waveform?

Yes. The matched filter is optimal for any known waveform in white noise. The
choice of waveform determines the peak shape and width, but the detection
principle is the same.

### Delivery notes

- Pause after the two-panel comparison; it is the conceptual turning point.
- Do not rush the threshold cell; it is the strongest argument for the matched
  filter.
- Keep the tone physical: slide, multiply, sum, peak.
- If the learner seems lost, return to "the radar knows what it transmitted"
  before going back to the math.
- The goal is comprehension, not speed.

### One-sentence close

The matched filter correlates the received signal with the known transmitted
shape to concentrate a weak echo into a sharp peak whose location gives the
range estimate; this notebook is the first complete radar measurement in the
course.
