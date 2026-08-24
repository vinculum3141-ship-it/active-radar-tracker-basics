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

#### 9. Close with the narrative Summary

The Summary should sound like a short explanation of the radar system, not a
list of formulas.

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
