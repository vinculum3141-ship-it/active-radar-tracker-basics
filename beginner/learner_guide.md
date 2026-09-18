# Learner Guide

This document is for you. It walks through the radar concepts introduced in
Notebooks 00 through 10 at a slower pace, with more background and physical
intuition than the notebooks can fit between code cells.

Each chapter opens with the same learning objectives as its notebook, walks
through the ideas in narrative form, and closes with expanded answers to the
opening questions. Use it before a notebook to prime yourself, or after a
notebook to fill in the gaps.

For every chapter, the notebook is the place to run code and see output. This
guide is the place to understand why the code works.

This guide exists to carry the ideas that are hard to hold in one notebook cell:
why the assumptions are valid, what the signal is really doing, and how the
physics turns into the algebra and then into the plots. If a notebook answers
"what do I compute?", this guide answers "why is this the right computation?"
and "what would go wrong if I misunderstood the model?".

### How to read this guide

Think of the notebook and the guide as a pair of complementary tools.

- The notebook is the lab: you run the code, plot the outputs, and see the
  signals move.
- The guide is the explanation: it tells you what the waveforms mean, why the
  equations are the right ones, and where the assumptions matter.

The best way to use the material is to read the guide chapter before or just
after the matching notebook, then return to the code and explain the result in
plain language. A good student explanation sounds like this: "The chirp is long
for energy but wide in bandwidth for resolution, so the matched filter can
compress it without losing sensitivity." That is the kind of sentence this guide
is designed to help you build.

### The learning arc at a glance

The learner path is deliberately staged:

1. Start with timing and range.
2. Add waveform design and matched-filter gain.
3. Add attenuation, noise, and detection.
4. Add motion through Doppler and range-Doppler.
5. Add tracking and state estimation.
6. Add spatial direction using arrays and beamforming.
7. Add adaptive rejection of interference.
8. Join the whole chain into a complete radar narrative.

That arc is important. You are not learning isolated formulas. You are learning
one coherent story: transmit a pulse, recover the echo, estimate range and
velocity, locate direction, and reject interference while tracking the target.

---

## Chapter 0 — Radar Intuition and Baseline Parameters

### What you should be able to explain

- What pulse radar is.
- Why the radar listens after it transmits.
- How duty cycle is computed.
- How a range delay turns into a range estimate.

### The simplest radar system

A radar measures distance by timing its own energy. The system sends a short
burst of electromagnetic energy toward a scene, then stops transmitting and
waits. If the energy hits a target, some of it reflects back toward the radar as
an echo. Because the radar knows exactly when it transmitted and because
electromagnetic energy travels at a known speed — the speed of light — the
returning echo carries a distance measurement encoded as a time delay.

That is the whole idea. Transmit, listen, time the return. Every complication in
radar signal processing exists to make that basic measurement more reliable, more
precise, or useful at greater range. But the foundation is always the same:
turn a delay into a distance.

The important intuition is that radar is not measuring a target by looking at it
like a camera does. It is measuring a very precise timing problem. The radar
sends a pulse, waits for a reflection, and asks: how long did that echo take to
come back? Once you know the round-trip time, the target range is not an image
of the world — it is a computed consequence of the travel time and the speed of
light.

### Why the radar must listen

A radar cannot hear while it is speaking. The transmitted burst is enormously
powerful compared with the returning echo — often a billion times stronger. If
the radar tried to receive at the same time it was transmitting, its own
outgoing signal would swamp the receiver and the weak echo would be invisible.

The solution is to separate speaking and listening in time. The radar transmits
a short burst, then goes quiet. During that quiet interval the receiver is
sensitive enough to detect the faint echo arriving from a distant target. The
time the radar spends listening is not idle time; it is the measurement window.

The diagram in the notebook's timing figure shows this rhythm: a brief
transmit pulse (orange) followed by a long listening window (green) within each
pulse repetition interval. The transmit pulse occupies only a small fraction of
the cycle, and the rest is devoted to listening.

### The pulse repetition interval

One complete cycle of transmit-then-listen is called the pulse repetition
interval, or PRI. It has two parts: the pulse width (how long the transmitter
is on) and the listening window (how long the radar waits before the next
pulse).

With the baseline values used throughout this course, the pulse width is 20
microseconds and the PRI is 1 millisecond. That means the radar transmits for
20 microseconds and then listens for the remaining 980 microseconds. The
listening window is almost fifty times longer than the transmit burst.

### Duty cycle

Duty cycle answers a practical question: what fraction of the time is the radar
actually transmitting? It is computed by dividing the pulse width by the PRI:

    D = pulse width / PRI = 20 microseconds / 1 millisecond = 0.02

A duty cycle of 0.02 means the radar spends only 2 percent of its time
transmitting and 98 percent listening. This is typical for pulse radar: the
system is quiet for most of each cycle, which is exactly what allows it to hear
weak echoes.

A common mistake is to think that a longer PRI means the radar transmits more
often. The opposite is true. A longer PRI gives the radar more time to listen,
which means the duty cycle shrinks. The radar is active for a smaller fraction
of each cycle, but it can detect echoes from greater distances because the
listening window is longer.

### Baseline radar values

Every notebook in this course uses the same baseline radar specification. The
values are chosen to be plausible for a real radar while keeping the arithmetic
clean enough to follow by hand. The notebook's reference table lists each value
and explains what it controls.

The carrier frequency is 2.45 gigahertz. This sets the wavelength and later
connects to Doppler calculations. The bandwidth is 5 megahertz, which determines
the range resolution once the matched filter compresses the echo (Notebook 04). The pulse width is 20
microseconds. The PRI is 1 millisecond. The sampling rate is 20 megahertz, which
tells us how many samples the receiver records per second. The example target is
at 1000 metres.

These values are not arbitrary. A real radar designer starts with the mission
requirements and works backward: what range accuracy is needed (which drives the
bandwidth), what ranges must be covered (which affects the PRI), what velocity
behaviour must be measured (which influences the carrier frequency), and what
hardware is available (which constrains everything). The baseline values in this
course are a simplified outcome of that process — plausible enough to resemble a
real design, but chosen so the equations stay readable.

### From delay to range

The echo delay is the core measurement. When the radar transmits a pulse and
receives the echo, the time between transmission and reception is the round-trip
travel time. The pulse travels to the target and back, so the total path length
is twice the target range.

The round-trip delay is therefore:

    delay = 2 * range / speed of light

For the baseline 1000-metre target, the delay is about 6.67 microseconds. The
receiver records this delay as a number of samples: at a sampling rate of 20
megahertz, 6.67 microseconds spans approximately 133 samples.

To convert back from samples to range, you reverse the formula:

    range = (delay in samples / sampling rate) * speed of light / 2

The notebook's calculation cell runs this chain step by step: it computes the
delay from the range, converts to samples, and converts back. The result is
996.8 metres rather than exactly 1000, because the true delay falls between two
sample boundaries. This small gap is sample quantisation — a preview of the
resolution limits discussed later.

### Closing the loop

**What pulse radar is.** Pulse radar is a distance sensor built on timing. The
radar transmits a short burst, stops, and listens for the echo. The time
between transmission and reception encodes the target range. The timing diagram
in the notebook shows this cycle in one picture.

**Why the radar listens after it transmits.** The echo is billions of times
weaker than the transmitted pulse. If the radar kept transmitting, its own
signal would drown out the return. The quiet listening window is what makes the
measurement possible.

**How duty cycle is computed.** Duty cycle is the pulse width divided by the PRI.
With the baseline values it is 0.02 — the radar transmits for 2 percent of each
cycle and listens for the other 98 percent.

**How delay becomes range.** The echo delay in samples converts to seconds by
dividing by the sampling rate, then to range using R = c * delay / 2. The
notebook's calculation cell shows this chain with real numbers, and the helper
functions package it for reuse in later notebooks.

### Optional stretch challenge

Try the same calculation with a longer PRI and a shorter listening window. What
happens to the duty cycle? Does the radar spend more time transmitting or more
time listening? Explain the trade-off in plain language using the concepts of
pulse width, PRI, and range measurement.

### Answer

```python
pulse_width = 20e-6
pri_short = 1e-3
pri_long = 5e-3

for pri in [pri_short, pri_long]:
    duty_cycle = pulse_width / pri
    print(f"PRI={pri:.3e} s -> duty cycle={duty_cycle:.4f}")
```

This shows that increasing the PRI makes the duty cycle smaller, not larger. The
radar spends a smaller fraction of each cycle transmitting and a larger fraction
listening. That is why a longer PRI typically helps range measurement: it gives
the echo more time to return before the next pulse.

---

## Chapter 1 — Pulse Generation and Chirp Intuition

### What you should be able to explain

- What a rectangular pulse looks like in time.
- What an LFM chirp is and how its frequency sweeps.
- Why a chirp can resolve targets much closer together than its pulse length
  suggests.
- What the time-bandwidth product tells you about that gain.

### Inside the transmit burst

Notebook 00 treated the transmit burst as a time interval — the radar is on for
the pulse width and off after that. Now we look inside that interval and ask:
what waveform actually leaves the antenna?

The simplest answer is a rectangular pulse: the transmitter is on at full
amplitude for the entire pulse width, then off. In sampled form this is a block
of ones, 400 samples long at 20 megahertz. There is no hidden structure — just a
flat burst of energy.

The rectangular pulse is the baseline waveform, and it is still used in some
radar systems. But it has a limitation that is worth understanding before we
move on.

When the radar receives an echo, it arrives as a pulse of energy spread over
time. The echo from a single target is as wide as the transmitted pulse — 400
samples, or 20 microseconds. During that entire window, the radar sees energy
arriving, but it cannot tell where within the window the energy came from. The
echo is a blurred copy of the transmitted shape.

Now imagine two targets at nearly the same range. Their echoes arrive almost at
the same time, overlapping each other. If the overlap is significant, the radar
sees one combined blob of energy instead of two distinct returns. The targets
blur together.

How far apart must the targets be to remain distinguishable? They need to be
separated by at least half the pulse length in time, which corresponds to a
range separation of c * tau / 2. For the baseline 20-microsecond pulse, that is
roughly 3000 metres. Two targets closer than 3000 metres apart will merge into
one echo.

A longer pulse makes this worse, not better. A 40-microsecond pulse would
require 6000 metres of separation. A shorter pulse improves resolution, but it
also contains less energy, so the echo from a distant target becomes weaker.
This is the fundamental trade: pulse length controls both the echo strength and
the resolution, and they pull in opposite directions.

The resolution formula is:

    delta_R = c * tau / 2

This is what limits the rectangular pulse. The chirp breaks the link between
pulse length and resolution, and the next section explains how.

### The LFM chirp

A linear-frequency-modulation (LFM) chirp keeps the same pulse length but adds
a frequency sweep. During the 20-microsecond pulse, the instantaneous frequency
rises linearly from zero to the bandwidth — 5 megahertz in the baseline case.

The complex baseband form of the chirp is:

    s(t) = exp(j * pi * (B / tau) * t^2)

where B is the bandwidth and tau is the pulse width. The ratio B / tau is the
chirp rate, which controls how fast the frequency climbs. With the baseline
values the chirp rate is 2.5 x 10^11 hertz per second.

The key point is that the frequency range covered — B — can be much larger than
the inverse of the pulse length (1 / tau). For the baseline values, B is 5
megahertz while 1 / tau is only 50 kilohertz. That extra bandwidth is what buys
resolution.

### Why the frequency sweep matters

Plotted in time, the rectangular pulse is a flat block of ones while the chirp
oscillates with a rising frequency. But their envelopes are the same shape —
both are constant-amplitude bursts. The difference is hidden in the phase. The
frequency sweep plot in the notebook makes this visible: the instantaneous
frequency ramps linearly from zero to the bandwidth across the pulse. The
rectangular pulse has no sweep at all.

This is why the frequency view matters. A chirp that looks like "just another
pulse" in the time domain is revealed as a wideband waveform in the frequency
domain. And it is that bandwidth — not the pulse length — that determines the
range resolution after the matched filter compresses the echo (introduced in
Notebook 04).

### Range resolution

The rectangular pulse resolution was delta_R = c * tau / 2 — roughly 3000
metres for the baseline pulse. That is the limitation described above.

For a chirp after the matched filter compresses the echo (Notebook 04), the
resolution is set by the bandwidth instead:

    delta_R = c / (2 * B)

With 5 megahertz of bandwidth that gives roughly 30 metres — a hundred times
better than the rectangular pulse of the same length.

The improvement factor is the ratio of these two numbers, which equals the
time-bandwidth product. The notebook's resolution comparison cell computes both
values and shows the factor explicitly.

### Why the chirp compresses: the mechanism

The width formula tells you *how* sharp the peak is, but not *why* correlation
squeezes a long chirp into a short spike. Here is that mechanism, because it is
the heart of pulse compression.

Cross-correlation slides a copy of the transmitted waveform across the received
signal and adds up the products at each lag. For a plain rectangular pulse there
is nothing to distinguish one lag from another — the block of ones overlaps a
block of ones over a wide span, so the output stays large for roughly the whole
pulse length. The result is a wide triangle, as wide as the pulse itself. There
is no way to localize it.

A chirp is different because it *labels each instant with its own frequency*.
The frequency sweeps from 0 to B across the pulse, so at any moment the chirp
has a unique, current frequency. When the sliding template lines up exactly with
the echo, those frequency labels match at every instant and the products add
constructively — the sum is large. Slide the template even slightly, and the
template's frequency at each instant no longer matches the echo's. Positive and
negative products start to cancel, and the sum collapses.

The wider the bandwidth B, the faster the frequency labels diverge as you slide,
so the faster the sum collapses and the narrower the peak. That is why the
compressed width is set by 1/B, not by the pulse length: the bandwidth is the
"clock" that tells the matched filter how precisely the chirp must line up. A
plain pulse has almost no bandwidth (only 1/tau), so it has no such clock and
cannot compress.

In short: the chirp compresses because its frequency sweep gives the matched
filter a precise way to tell when the template truly aligns with the echo, and
the bandwidth sets how sensitive that alignment is.

### The time-bandwidth product

The time-bandwidth product is:

    TBP = B * tau = 5 MHz * 20 microseconds = 100

This number is the compression ratio. The long chirp, squeezed by the matched
filter (introduced in Notebook 04), collapses into a peak roughly 100 times
narrower than the pulse itself. It captures the central trade of modern pulse
radar: the pulse can stay long for energy while the bandwidth provides the
resolution. The two properties are decoupled.

A large time-bandwidth product is what makes pulse radar practical. Without it,
you would have to choose between a short pulse (good resolution, weak echo) and
a long pulse (strong echo, poor resolution). The chirp lets you have both.

### Closing the loop

**What a rectangular pulse looks like in time.** A rectangular pulse is a block
of ones — the transmitter on at full amplitude for N = f_s * tau samples. With
the baseline values that is 400 samples. There is no frequency sweep; the energy
is concentrated near zero frequency.

**What an LFM chirp is and how its frequency sweeps.** An LFM chirp has the
same amplitude as the rectangular pulse, but its phase rises quadratically. The
instantaneous frequency ramps linearly from zero to the bandwidth across the
pulse. The sweep covers a band far wider than 1 / tau, which is the source of
the resolution improvement.

**Why a chirp resolves better than a same-length pulse.** Resolution for a plain
pulse is c * tau / 2; for a compressed chirp it is c / (2B). Because the
bandwidth can be made far larger than 1 / tau, the chirp resolves targets far
closer together. The matched-filter preview in the notebook shows this visually:
the chirp compresses to a narrow peak while the rectangular pulse stays wide.

**What the time-bandwidth product tells you.** TBP = B * tau = 100. This is the
compression factor — the long chirp is squeezed by roughly 100x into a sharp
peak. It measures how much work the chirp does compared to a plain pulse of the
same length.

### Optional stretch challenge

Compare the rectangular pulse and the chirp with the same pulse width and the
same target. Estimate the approximate resolution for each one and explain why the
chirp wins even though its pulse length stays the same. If you can, repeat the
same thought experiment with a longer chirp bandwidth and describe how the
resolution changes.

### Answer

```python
c = 299_792_458
pulse_width = 20e-6
bandwidth = 5e6

range_resolution_rect = c * pulse_width / 2
range_resolution_chirp = c / (2 * bandwidth)
print(f"Rectangular pulse: {range_resolution_rect/1000:.2f} km")
print(f"Chirp: {range_resolution_chirp/1000:.3f} km")

# Try a wider chirp: 10 MHz
bandwidth_wider = 10e6
range_resolution_chirp_wider = c / (2 * bandwidth_wider)
print(f"Wider chirp: {range_resolution_chirp_wider/1000:.3f} km")
```

The chirp wins because the key quantity is bandwidth, not pulse length alone. A
plain pulse has a resolution near c * tau / 2; a chirp has a resolution near c /
(2B), so increasing the bandwidth makes the range cell smaller even if the pulse
length stays constant.

---

## Chapter 2 — The Radar Equation

### What you should be able to explain

- Why radar echoes are billions of times weaker than the transmitted pulse.
- What the radar equation says and what each term means.
- Why received power falls as the fourth power of range.
- How the −40 dB attenuation used in later notebooks comes from the physics.

### Why the echo is so weak

When the radar transmits, the energy spreads outward in all directions like the
surface of an expanding sphere. Only a tiny fraction of that energy hits the
target. The target reflects some of it, again spreading in all directions. Only
a tiny fraction of the reflected energy heads back toward the radar. And by the
time it arrives, it has traveled twice the distance.

There are four separate losses at work:

1. **Outward spreading.** The transmitted power density at the target falls as
   1 / R², where R is the range.
2. **Target interception.** The target intercepts only the power that falls on
   its effective area, called the radar cross section (σ).
3. **Return spreading.** The reflected energy spreads outward again, and the
   power density at the radar falls as 1 / R² a second time.
4. **System losses.** The transmitter, antenna, receiver, and propagation medium
   all introduce losses.

Combining the two spreading losses gives the characteristic 1 / R⁴ dependence.
That is why radar echoes are so much weaker than the transmitted pulse.

### The radar equation

The monostatic radar equation relates the received power to the transmitted
power and the system parameters:

    P_r = (P_t * G² * λ² * σ) / ((4π)³ * R⁴ * L)

where:

- P_r is the received power (what the radar detects),
- P_t is the transmitted power (what the radar puts out),
- G is the antenna gain (how much the antenna concentrates the beam),
- λ is the wavelength of the carrier frequency,
- σ is the target radar cross section (effective reflecting area),
- R is the range to the target,
- L is the combined system losses.

The R⁴ in the denominator is the key. Doubling the range does not halve the
received power — it reduces it by a factor of 16.

This is the single most important reason radar is difficult. The range loss is
not linear, it is geometric and round-trip. The signal leaves the radar,
spreads over a sphere, bounces off a target, and spreads again on the way back.
The system therefore loses power in a way that is brutal at long range, and the
signal processing methods that follow in the notebooks are designed directly to
recover information from that weak return.

### The 1 / R⁴ dependence

The fourth-power law comes from the signal making a round trip: the power falls
as 1 / R² on the way out and 1 / R² on the way back. Multiplying the two gives
1 / R⁴.

On a log–log scale, the curve is steep. The notebook's plot shows this with
the baseline target marked: at 1000 m — five times further than the 200 m
reference — the received power is 1/5⁴ = 1/625 of the reference. A fivefold
increase in range costs a factor of 625 in received power.

### What each term controls

The radar designer can control the transmitted power, the antenna gain, and (to
some extent) the operating wavelength. The target's radar cross section is not
under the designer's control — it depends on the target's size, shape, and
materials. The range is the variable the radar is trying to measure, not
something the designer chooses.

**Transmitted power.** More power means a stronger echo, but higher power costs
more electricity and requires heavier hardware.

**Antenna gain.** A high-gain antenna sends more energy toward the target and
collects more on the return, but it covers a smaller patch of sky.

**Radar cross section.** A large aircraft might have a radar cross section of
100 m²; a small drone might be 0.01 m². Stealth shapes and materials can reduce
the cross section by orders of magnitude.

### Connecting to the channel model

The next notebook (Chapter 3) uses an attenuation of −40 dB for the baseline
1000-metre target. That value comes from the radar equation with plausible
transmitter power, antenna gain, and target cross section. It is not arbitrary —
it is the physical consequence of the signal path. When you see −40 dB in
Chapter 3, you will know it encodes the range, the target, and the geometry.

### Closing the loop

**Why radar echoes are so weak.** The energy spreads on the way out (1 / R²),
only a fraction hits the target (radar cross section), and the reflected energy
spreads again on the way back (another 1 / R²). The two spreading losses
combine to give 1 / R⁴.

**What the radar equation says.** It connects received power to transmitted
power, antenna gain, wavelength, target cross section, range, and losses. The
R⁴ denominator is the dominant term — it is why range is the hardest challenge
in radar.

**Why received power falls as the fourth power of range.** The signal makes a
round trip, losing power as 1 / R² on each leg. Doubling the range reduces
received power by a factor of 16, which is 10 * log10(16) ≈ 12 dB.

**How the −40 dB attenuation comes from the physics.** It is the combined
effect of the radar equation with plausible system parameters. The exact value
depends on the specific radar and target, but −40 dB is a realistic ballpark
for a 1000-metre target.

### Optional stretch challenge

Pick one range value such as 200 m, 1000 m, and 5000 m and compute the
received-power ratio relative to a reference target. When you compare the
results, explain why the 1 / R⁴ law matters so much more at longer ranges than
at short ranges.

### Answer

```python
reference_range = 200
ranges = [200, 1000, 5000]

for R in ranges:
    ratio = (reference_range / R) ** 4
    print(f"Range={R} m -> received power ratio relative to 200 m = {ratio:.3e}")
```

This makes the effect very clear: the received power falls with the fourth power
of range, so moving from 200 m to 1000 m is a huge loss even before you count
other system terms. That is why range is the hardest challenge in radar design.

---

## Chapter 3 — Channel Model and Echoes

### What you should be able to explain

- How range turns into a sample delay in the received signal.
- What an echo looks like relative to the transmitted pulse.
- Why attenuation makes the echo weaker than the original.
- How noise hides the echo and motivates the matched filter.

### Crossing from transmit to receive

Notebooks 00 and 01 built the transmit side: the waveform, its timing, and its
resolution properties. Now we cross the gap between the antenna and the target
and ask a simple physical question: once the pulse leaves the antenna, what
comes back?

The answer is the channel model. The channel is the path between the radar and
the target, and it does three things to the transmitted pulse: it delays it, it
weakens it, and it corrupts it with noise. Understanding these three effects is
the foundation for everything on the receive side.

### Delay: the echo arrives later

The pulse travels to the target at the speed of light, reflects, and travels
back. The total travel time is the round-trip delay:

    delay = 2 * range / c

For the baseline 1000-metre target this is about 6.67 microseconds. At a
sampling rate of 20 megahertz, the delay spans 133 samples.

The radar receiver digitises the incoming signal — it samples the voltage
coming from the antenna 20 million times per second and stores the samples in a
digital array. This array is the received signal buffer. Think of it like
recording audio, but for radar echoes.

In this buffer, the echo begins at sample 133 and extends for the length of the
pulse (400 samples). The buffer must be at least 533 samples long to hold the
entire echo. The notebook builds this step by step: first the empty buffer, then
the pulse written at the correct offset.

The critical point is that the echo is a copy of the transmitted pulse — same
shape, same length. Only its position has changed. The delay is the range
measurement in disguise.

### Attenuation: the echo is weaker

Only a tiny fraction of the transmitted energy returns to the radar. The signal
spreads as it travels outward, reflects imperfectly from the target, and spreads
again on the return journey. The radar hardware also introduces losses. All of
these effects combine into a single attenuation factor.

The notebook uses -40 decibels, which corresponds to an amplitude factor of
0.01. The echo amplitude is one hundredth of the transmitted amplitude, and
because power scales with amplitude squared, the echo power is only
one ten-thousandth of the transmitted power.

Why -40 dB specifically? In a real radar, the attenuation depends on the
transmitted power, antenna gains, target radar cross section, and range —
combined through the radar equation. For a 1000-metre target with typical
parameters, -40 dB is a plausible ballpark. The exact value is not the point;
the point is to see what a weak echo looks like when it arrives at the receiver.
You will use a different attenuation value in later notebooks when the scenario
calls for it.

Attenuation is deterministic: it scales the echo down but does not change its
shape. The middle panel of the notebook's three-part plot shows this clearly —
the echo is recognisable as the same waveform, just much smaller.

### Noise: the echo is buried

Every radar receiver has a thermal noise floor — random fluctuations caused by
the motion of electrons in the electronics. We model this as additive white
Gaussian noise (AWGN), meaning the noise is spread uniformly across the
frequency band and added on top of the signal.

The amount of noise is described by the signal-to-noise ratio (SNR). At 20
decibels the signal power is 100 times the noise power. That sounds high, but
because the noise is spread across the entire received buffer while the echo is
concentrated in a short slot, the echo can still be hard to spot by eye.

The bottom panel of the notebook's three-part plot shows the result: the
attenuated echo is still there, but receiver noise has been added on top. Your
eye can still pick out the general shape if you know where to look — the signal
is no longer a flat burst, it fluctuates across the buffer. But a detector
cannot rely on visual inspection. The radar needs a systematic way to pull the
echo out of the noise, which is what the matched filter does in Notebook 04.

### Attenuation and noise are different

A common mistake is to treat attenuation and noise as the same effect. They are
not.

Attenuation is a predictable scaling. The echo is smaller but still clean. If
you could remove the noise, you would see the attenuated echo as an exact,
scaled copy of the transmitted pulse.

Noise is random. It adds fluctuations that corrupt the signal. Even if there
were no attenuation, noise would still make the echo hard to detect.

Keeping these two effects separate makes the received signal much easier to
understand. The channel applies them in sequence: first delay, then attenuation,
then noise.

### Closing the loop

**How range turns into a sample delay.** The round-trip delay equals twice the
target range divided by the speed of light. Multiplying by the sampling rate
gives the delay in samples. For a 1000-metre target at 20 megahertz, the echo
begins at approximately sample 133.

**What an echo looks like.** The echo is a replica of the transmitted waveform.
Its shape and duration are the same; only its position is shifted by the travel
delay and its amplitude is reduced by attenuation. The notebook's middle panel
shows it as a small, recognisable copy of the transmitted pulse.

**Why the echo is weak.** Energy spreads on the outward journey, only part of it
reflects from the target, and the reflected energy spreads again on the return.
At -40 decibels of attenuation, the echo amplitude is one hundredth of the
transmitted amplitude.

**How noise hides the echo and why the matched filter is needed.** Receiver noise
adds random fluctuations across the entire buffer. A weak echo can disappear
visually among those fluctuations even though it is physically present. The
matched filter in Notebook 04 exploits the fact that the echo is a known shape
to concentrate its energy into a detectable peak.

---

## Chapter 4 — Matched Filtering and Range Estimation

### What you should be able to explain

- What correlation means in the matched-filter context.
- Why the compressed peak is sharper than the raw echo.
- How peak location converts to a range estimate.
- Why matched filtering beats simple thresholding.

### The problem this notebook solves

You have built the transmit waveform (Notebook 01) and seen what the channel
does to it (Notebook 03). The echo is in the received buffer, but it is buried
in noise. You cannot see it by eye, and a simple threshold on the raw signal
would trigger on noise as often as on the echo.

The matched filter solves this problem. It is the standard tool for pulling a
known waveform out of noise, and it is the foundation of range measurement in
every pulse radar.

### What the matched filter does

The radar already knows the shape of the waveform it transmitted. The matched
filter exploits that knowledge by sliding a copy of the transmitted shape across
the received signal and measuring how well they line up at every position.

Formally, the matched filter computes the cross-correlation between the received
signal and the transmitted template. At each lag position it multiplies
overlapping samples and sums the products. Where the transmitted shape lines up
with an echo, every sample contributes positively and the sum is large. Where
they do not line up, the contributions cancel and the sum stays small.

The result is a new signal — the matched-filter output — that peaks wherever an
echo is present. The peak location corresponds to the echo delay, and the peak
height reflects the total energy accumulated across the pulse length.

This is the most important conceptual step in the beginner track: the radar does
not simply measure the strongest sample, it measures the strongest match between
a known transmit waveform and a received signal. That is why the matched filter
is the natural tool for weak echoes buried in noise. The code is not doing a
mysterious trick; it is measuring alignment between a template and the signal,
which is exactly what a radar should do when it knows the pulse it transmitted.

### Correlation by hand

The notebook walks through this step by step before calling any helper function.
It slides the rectangular pulse across the noisy received signal, multiplies
overlapping samples, and sums at each position. The output is a vector one
sample longer than the received buffer.

The peak appears at a specific index in the output vector. Because of the
`full`-mode correlation convention used by numpy, the echo delay is the peak
index minus (pulse length - 1). For the baseline 1000-metre target the peak
lands at sample 532, giving an echo delay of 133 samples — exactly the delay
expected from the range.

### Why the compressed peak is sharper than the raw echo

The raw echo is as wide as the transmitted pulse — 400 samples. The matched
filter concentrates that energy into a peak whose width is set by the waveform
bandwidth, not the pulse length.

For the rectangular pulse the bandwidth is only 1 / tau (50 kilohertz), so the
compressed peak is still relatively wide. For the chirp the bandwidth is much
larger (5 megahertz), so the compressed peak is far narrower. The notebook's
overlay plot shows both on the same axes: the chirp peak is visibly sharper.

The matched filter does not add energy to the signal. It coherently adds across
the pulse length, compressing the energy that was already there into a narrower
time slot. The peak is higher because the energy is concentrated, not because
energy was created.

### Converting peak location to range

The peak gives you a sample delay, and the round-trip range equation converts
that delay to a distance. The notebook's calculation cell does this explicitly:

1. Find the peak index in the matched-filter output.
2. Subtract (pulse length - 1) to get the echo delay in samples.
3. Divide by the sampling rate to get seconds.
4. Apply R = c * delay / 2.

For the baseline target the result is 996.8 metres, matching the true range to
within a fraction of a metre. The small discrepancy is sample quantisation —
the same effect seen in Notebook 00.

### Why thresholding the raw echo fails

A natural first thought is to look for the largest sample in the received
signal. The problem is visible in the notebook's raw-signal panel: noise can
produce samples as large as the echo. The raw peak may not be at the echo
location at all, and many samples may exceed any reasonable threshold.

The matched filter avoids this because it accumulates energy across the entire
pulse length. The echo contributes consistently at the correct lag, so the peak
grows proportionally to the pulse length, while the noise adds incoherently and
averages out. This is why the matched-filter output shows a clear peak even
though the echo is invisible in the raw signal.

### Closing the loop

**What correlation means in the matched-filter context.** Correlation is a
sliding dot product. The matched filter multiplies the received signal by the
transmitted waveform and sums at every lag. When the shapes line up, the sum is
large. When they do not, it stays small. The output peaks at the echo delay.

**Why the compressed peak is sharper than the raw echo.** The matched filter
concentrates the echo energy into a narrow time slot whose width is set by the
bandwidth, not the pulse length. For the chirp the bandwidth is much larger than
1 / tau, so the compressed peak is proportionally narrower.

**How peak location converts to a range estimate.** The peak index gives the
echo delay in samples (after subtracting the correlation offset). Dividing by
the sampling rate converts to seconds, and R = c * delay / 2 gives the range.
The notebook's calculation cell shows this chain with real numbers.

**Why matched filtering beats simple thresholding.** A threshold on the raw
signal triggers on the single largest sample, which may be noise. The matched
filter accumulates energy across the entire pulse, so the echo grows while the
noise averages out. The result is a clear peak even when the echo is invisible
in the raw received data.

---

## Chapter 5 — Doppler and the Range-Doppler Map

### What you should be able to explain

- The difference between fast time and slow time, and which carries range versus velocity.
- Why a moving target's echo phase advances from pulse to pulse.
- How an FFT across pulses turns that phase advance into a Doppler frequency.
- How the Doppler frequency maps to a radial velocity.
- Why the baseline 40 m/s target wraps to a wrong speed.

### The problem this notebook solves

By the end of Notebook 04 you could measure *where* a target is. The matched
filter turned a weak, noisy echo into a sharp peak, and reading the peak's
position gave you the range. But a single peak says nothing about motion. Two
targets at the same range are indistinguishable in fast time, and a stationary
target looks the same as a receding one to a detector that only measures
arrival time.

Doppler fixes this. When a target moves toward or away from you, the round-trip
changes each pulse, and that change carries a velocity signal. This notebook
makes you measure that signal. It is the first major milestone in the course:
you will leave it able to build a two-dimensional picture that locates targets
in *both* range and velocity at once.

### Fast time versus slow time

A pulse radar has two clocks running at very different speeds, and keeping them
apart is the key to this notebook.

**Fast time** is the clock you already know. Inside a single PRI you sample the
receive window at 20 MHz, so each fast-time sample is a tiny fraction of a
microsecond later than the last. Because radio waves travel at the speed of
light, a fast-time sample index maps directly to a time-of-arrival, and
therefore to a range. Fast time is where range lives.

**Slow time** is a much slower clock. The radar sends one pulse per PRI, so the
number of the pulse itself is a second kind of time: pulse 0, pulse 1, pulse 2,
and so on. Each slow-time tick is one whole PRI, here 1 ms. You do not sample
at 20 MHz along slow time; you sample at the pulse repetition frequency, once
per pulse.

The two clocks turn the received data into a grid: a two-dimensional array. It
is worth being precise about its two axes.

- **Rows are slow time.** Each row is one pulse, indexed by pulse number. Slow
  time advances once per PRI, once per pulse, at the 1000 Hz pulse repetition
  frequency. The row index is what you will FFT across to get Doppler.
- **Columns are fast time.** Each column is one *range bin* — a particular
  fast-time sample inside the receive window, mapped to a distance. The column
  index carries range.

So a **range bin** is a fast-time column (a range cell), while **once per PRI**
is how the slow-time rows are sampled. They are two different axes, not two
names for the same thing. One cell of the grid, at pulse k, range bin r, holds
one sampled value of the echo at that range, on that pulse. Any single pulse
answers "how far?"; the sequence of pulses answers "how fast?". This notebook
shows you how to read the second answer.

One more thing about that cell value: it is now a **complex number**. In earlier
notebooks you worked with the real waveform as it might appear on a single wire.
To see Doppler you must track the carrier's *phase*, which requires both the
in-phase and quadrature parts — the real and imaginary components. The chirp you
built in Notebook 01 is already complex, so each cell carries a real part and an
imaginary part. The phase, the thing that actually moves, only exists if you
keep both parts, which is why the pulse stack is built with a complex dtype.

### Why the echo phase advances

Imagine a target at 1000 m, stationary. Every pulse you send travels the same
round trip, so the echo comes back with the same phase, pulse after pulse. The
echo sits at the same fast-time delay and its shape does not change. A
stationary target is boring in slow time.

Now let the target move toward you at 20 m/s. Between one pulse and the next
(1 ms later) it closes a little ground, so the round trip is a little shorter.
That tiny change in path length is tiny compared with a range bin, so the echo
still lands at the same fast-time delay — you cannot see the motion by watching
delay. But the *phase* of the carrier is sensitive to changes far smaller than
a whole wavelength. Over that 1 ms the target moves 2 cm, which is a noticeable
fraction of the 12 cm carrier wavelength. The echo phase rotates by that
fraction each pulse.

The result is a steady phase advance across slow time. Extract the complex echo
at the target's range bin from every pulse and the real and imaginary parts
draw out a sinusoid whose frequency is the Doppler shift. Magnitude stays flat;
phase is where the motion lives.

This is a critical point that students often miss: a moving target does not
necessarily change the *power* of the echo much, but it changes the phase from
pulse to pulse. If you look only at magnitude, you miss the motion. Radar
velocity is therefore not a magnitude problem; it is a phase problem. Once you
understand that, the whole Doppler story becomes much easier to follow.

### From phase advance to Doppler frequency

The phase advance has a rate: it completes `fd` cycles per second, where `fd`
is the Doppler frequency. For a monostatic radar the Doppler shift is

    fd = 2 v / lambda

The factor of two comes from the round trip: the wave travels out and back, so
a target moving at speed `v` produces a shift equal to two radial velocities.
Here `lambda` is the carrier wavelength you met in Notebook 00/02, c / fc, which
is 12.2 cm at the 2.45 GHz baseline — the distance the carrier wave travels in
one cycle. For the 20 m/s target at 2.45 GHz, that is

    fd = 2 * 20 / 0.1224 = 327 Hz

which is well within the unambiguous band, so it appears cleanly. The band is
plus or minus half the PRF (plus or minus 500 Hz here); the next section gives
the numbers.

### Finding the Doppler frequency with an FFT

Now take a single column of the grid: slice the complex values at the target's
range bin out of *every* pulse. That slice is a row of slow-time samples — one
complex number per pulse, sampled once per PRI. The tool from Notebook 01 now
reappears: an FFT. You take the fast Fourier transform of those slow-time
samples and look for the peak. It sits at the Doppler frequency. This is
exactly the frequency analysis you did on the transmit waveform, but now the
"signal" is sampled once per PRI rather than at 20 MHz.

The slow-time sampling rate is the PRF, or pulse repetition frequency — the
number of pulses the radar sends per second. It is simply the inverse of the
PRI: PRF = 1 / PRI = 1 / 0.001 = 1000 pulses per second. The radar transmits
one pulse every 1 ms, so it fires 1000 times a second, and that is how often it
samples each slow-time location.

Just as fast-time sampling at `fs` limits the frequencies you can name, sampling
slow time at the PRF of 1000 Hz limits the Doppler frequencies you can name to
plus or minus half the PRF — the slow-time Nyquist rate — which is plus or minus
500 Hz. The 327 Hz peak from a 20 m/s target is comfortably inside that range.

### From Doppler frequency to velocity

To recover the speed, invert the Doppler relation:

    v = fd * lambda / 2

This is the same formula with the two unknowns swapped. Feed the FFT's peak
frequency into it and you get the radial velocity — positive for approaching,
negative for receding. For the 327 Hz peak you get about 20 m/s, matching the
target. The scale factor `lambda / 2` is small, which is why radar can resolve
fine velocities: even a large Doppler frequency compresses to a modest speed.
The relation is linear, so doubling the Doppler frequency exactly doubles the
reported velocity.

### The range-Doppler map

So far you picked a single range bin and found its Doppler. But which range bin
is the right one? A *range bin* is one fast-time sample of the receive window —
after matched filtering, each one corresponds to a specific distance. Range bin
133, for example, is the 1000 m cell. It is purely a range concept; it has
nothing to do with velocity. The 20 m/s you fed in was the target's speed,
which lives in slow time, not in the choice of range bin.

A real radar does not know where the targets are. Rather than guess a single
range bin, it repeats the slow-time FFT at *every* range bin, building a
two-dimensional array: one axis is range (the range bins), the other is
velocity (the Doppler frequency at each bin), and the value in each cell is the
echo power for that range-and-velocity combination. You build the 2D map
precisely so the data can tell you which range bins hold moving targets and how
fast each one is going — you do not need to know where to look in advance.
Plot it as a heatmap and you can read a whole scene at a glance.

A single target shows up as one bright blob at its range and velocity. Two
targets that share a range but move at different speeds — invisible overlap in
fast time — split into two blobs along the velocity axis. This is why the
range-Doppler map is the standard radar display: it separates targets that
collapse into one peak in a single matched filter.

### Velocity resolution and ambiguity

Doppler has limits, and they mirror the range limits you met in Notebook 00.

**Resolution.** To measure velocity you collect a batch of pulses and process
them together. That batch is the **CPI**, or coherent processing interval — the
total time over which the radar gathers pulses that it will look at as one
coherent group. The size of the batch, N = 64 pulses, is a baseline choice (the
`n_pulses = 64` setting in the helpers); it is not forced by the physics, it is
a knob the radar uses, alongside PRI, to shape how long and how fine the
velocity measurement will be. Each CPI lasts

    CPI = N * PRI = 64 * 1 ms = 64 ms

During that window the FFT has N slow-time samples (one per pulse) per range
bin, so it can tell apart frequencies up to one bin apart. That frequency
spacing becomes a velocity resolution of

    delta_v = lambda / (2 N PRI) = 0.1224 / (2 * 64 * 0.001) = 0.96 m/s

The longer the CPI (more pulses, or a longer PRI), the finer the velocity
resolution; a shorter CPI gives coarser resolution but a faster update. Two
targets whose speeds differ by less than delta_v appear as one blob.

**Ambiguity.** Because slow time samples once per PRI, the unambiguous Doppler
band is plus or minus half the PRF, plus or minus 500 Hz. To find the fastest
speed that band can name, feed the edge frequency into the velocity formula
`v = fd * lambda / 2`:

    v_max = (500 Hz) * (0.1224 m) / 2 = 30.6 m/s

So the highest velocity measured uniquely is plus or minus 30.6 m/s
(equivalently lambda * PRF / 4). A target faster than that has a Doppler beyond
the band and *aliases*: it folds over and appears at a lower, wrong frequency,
often with the wrong sign of velocity.

### The 40 m/s ambiguity case

The baseline target moves at 40 m/s, which is beyond the 30.6 m/s limit. Its
true Doppler would be

    fd = 2 * 40 / 0.1224 = 654 Hz

but the system can only name frequencies up to 500 Hz. The 654 Hz tone aliases:
because 654 lies between 500 Hz and 1000 Hz (twice the Nyquist edge), it wraps
around the band by subtracting one PRF, so it is measured as

    654 - 1000 = -346 Hz

The minus sign means it appears on the receding side. Reading that back through
the velocity formula,

    v = (-346 Hz) * (0.1224 m) / 2 = -21.2 m/s

A target really moving toward you at 40 m/s is reported as receding at about
21 m/s.

This is not a bug in the FFT; it is a consequence of sampling slow time too
coarsely. Reducing the PRF raises the unambiguous velocity but reduces the
unambiguous range, and vice versa — the classic trade-off real radars resolve
with staggering or multiple PRFs. For now, the point is to see the aliasing
deliberately and understand where it comes from.

### Closing the loop

**Fast time versus slow time.** Fast time is the 20 MHz sampling within a PRI
that resolves range; slow time is the once-per-pulse sampling at the PRF that
resolves velocity. Range lives in fast time, velocity in slow time.

**Why the echo phase advances.** A moving target changes the round-trip
distance slightly each pulse, so although the echo stays at the same fast-time
delay, its carrier phase rotates steadily at the Doppler frequency
`fd = 2 v / lambda`. The magnitude stays flat; the phase carries the motion.

**How the FFT turns that into Doppler.** Sampling the complex echo once per
pulse and taking an FFT across pulses produces a peak at `fd`. For the 20 m/s
target that peak sat at about 327 Hz.

**How Doppler maps to velocity.** Inverting the relation gives
`v = fd * lambda / 2`. The 327 Hz peak became about 20 m/s, matching the truth.

**Why the 40 m/s target wraps.** Slow time samples at the 1000 Hz PRF, so the
unambiguous velocity is plus or minus 30.6 m/s. The 40 m/s target's 654 Hz
Doppler folds over and was reported at about minus 21 m/s — the wrong speed and
the wrong direction.

If you can retell these five answers, you can measure velocity as well as
range, and you are ready to combine both into a trajectory.

---

## Chapter 6 — Kalman Tracking

### What you should be able to explain

- Why a single noisy detection is not enough to know where a target is.
- What the predict step does and why its guess is uncertain.
- What the update step does with each new measurement.
- How the filter decides how much to trust the model versus the sensor.
- Why the filtered track is smoother than the raw measurements.

### The problem: one noisy measurement is not enough

A range-Doppler map gives you one (range, velocity) reading per CPI. Reading it
again every 64 ms produces a stream of detections, but each one is the true
value plus noise. Your detector's peak wobbles around the truth, so a single
reading can be off by several metres or m/s. If you steered the radar by one
reading you would chase noise. You need to combine many readings and use the
knowledge that targets move smoothly - that combination is a Kalman filter.

### What the filter keeps: state and uncertainty

The filter's belief is two objects.

- The **state vector** `x = [range, velocity]` — its best guess of where the
  target is and how fast it is moving right now.
- The **covariance matrix** `P` — how unsure the filter is about that guess.
  Big diagonal entries mean big uncertainty.

Two settings you choose ahead of time describe how much to trust the inputs:

- `Q`, the **process noise** — how much the model is trusted (how strongly the
  target really obeys constant velocity).
- `R`, the **measurement noise** — how much the sensor is trusted (how noisy
  the detections are).

### Step 1: predict from the model

The first half of each timestep uses only the model, no new measurement. If the
current estimate is range `r` and velocity `v`, then after a time `dt` the best
guess is:

    new range = r + v*dt
    new velocity = v

That is the transition matrix `F = [[1, dt], [0, 1]]` applied to the state. The
covariance grows by adding `Q`, because the model is not perfect. Predict
answers "where do I expect the target to be now?" before you look at the
measurement.

### Step 2: update with the measurement

The second half fuses the prediction with the newest detection. You look at the
difference between what the model predicted and what the sensor measured — the
innovation `z - x_pred` — and decide how much of it to accept. The weight is
the **Kalman gain** `K`, derived from the two uncertainties:

- if the measurement is very trustworthy relative to the prediction (R small, P
  large), `K` is close to 1 and you mostly follow the measurement;
- if the prediction is very trustworthy (P small, R large), `K` is close to 0
  and you mostly keep the prediction.

The update is `new_state = prediction + K * (measurement - prediction)`, and the
covariance shrinks because the measurement reduced the uncertainty. The gain is
recomputed every step as the uncertainties change.

### The recursive loop and the gain over time

One step is predict then update. Repeating it over every CPI yields the whole
track. The filter keeps only the state and covariance and carries them forward,
so each new measurement is folded in with the latest belief rather than the full
history — that is what makes it *recursive*.

The gain is not a fixed constant. Early on the filter is very unsure (P is
large), so it leans on each measurement and the gain is high. As measurements
arrive and P shrinks, it trusts its own estimate more and the gain settles to a
lower, steady value. That adaptation is the balance between model and sensor.

### Why the filtered track is smoother

The filter combines information across many detections while still tracking
motion. Measurement noise tends to cancel out when combined, so the filtered
range and velocity wobble far less than any single measurement, while the
predict step keeps the track from lagging a moving target. In the notebook the
filtered range RMS error (about 1.8 m) was far below the single-measurement
error (about 4.8 m).

### A common mistake

The filter does not simply average the measurements. If the target is moving, a
plain average of past positions lags behind the truth. The predict step —
using velocity to guess where the target is now — is what lets the track keep
up with a moving target instead of trailing it.

Do not tune the Kalman gain by hand. The gain is *derived* from P, Q, and R at
each step. You tune the covariances (how much you trust model and sensor), and
the gain follows. Set R too small and the filter chases every bit of measurement
noise; set R too large and it ignores the sensor and drifts.

### Checkpoint answers

**What does the predict step do?** It advances the state using only the model —
range grows by `v*dt`, velocity is unchanged — and grows the covariance by the
process noise `Q`, because the model is not perfect. It is the filter's guess of
where the target is *before* it looks at the new measurement.

**What does the update step do?** It fuses the prediction with a new measurement.
It forms the innovation (measurement minus prediction), weights it by the
Kalman gain `K`, and adds that weighted correction to the prediction. Then it
shrinks the covariance because the measurement reduced the uncertainty.

**If measurement noise were larger (bigger R), would the filter trust the
measurements more or less?** Less. Larger `R` makes the gain `K` smaller, so the
filter leans more on its prediction and does not chase the noisier measurements.
That is the correct instinct, though it costs the filter some ability to respond
to genuinely new information — which is why `R` should reflect the real noise.

### Closing the loop

**Why a single noisy detection is not enough.** Each detection is the true
range and velocity plus noise, so one reading can be off by several metres or
m/s. Steering by a single reading would chase noise; the track must combine
many readings and use the fact that targets move smoothly.

**What the predict step does.** Predict uses only the model: it advances the
state by `dt` (range grows by `v*dt`, velocity unchanged) and grows the
covariance by `Q`. It answers "where do I expect the target to be now?" before
looking at the new measurement.

**What the update step does.** Update forms the innovation, weights it by the
Kalman gain, and adds the weighted correction to the prediction, then shrinks
the covariance.

**How the filter balances model and sensor.** The gain is derived from the two
uncertainties. When the sensor is trustworthy (R small, P large), K is near 1
and the filter follows the measurement. When the prediction is trustworthy
(P small, R large), K is near 0 and the filter keeps its prediction. Larger R
means less trust in the sensor, a smaller gain, and a more model-driven
estimate.

**Why the filtered track is smoother.** Combining many measurements cancels the
noise that jitters each single detection, while the predict step keeps the track
from lagging a moving target. The filtered error against truth drops well below
the single-measurement error.

If you can retell these five answers, you have turned a stream of noisy
detections into a stable estimate of where a target is and where it is going.

---

## Chapter 7 — Array Geometry and Beam Patterns

### What you should be able to explain

- How a line of antennas turns a time difference between elements into an angle.
- What the element spacing is and why half a wavelength is the usual choice.
- How the phase stepping between elements forms the steering vector.
- Why the array factor (beam pattern) has a main lobe and sidelobes.
- When and why grating lobes appear.

### The missing coordinate: direction

You can already measure range and velocity. A single antenna cannot tell you
direction — the echo only says the target lies somewhere on a circle of constant
range, not where on that circle. An array of antennas changes this. If the same
echo reaches several elements, it travels a slightly different distance to each
one, so it arrives at a slightly different time and phase. That difference is
the seed of an angle measurement.

### Array geometry

A uniform linear array (ULA) places N identical elements along a line spaced d
apart, with the first at the origin. The target's direction is the angle theta
measured from broadside (theta = 0 is perpendicular to the line of elements).
A wave from direction theta travels an extra path

    d * sin(theta)

from one element to the next. That is the whole geometry: the angle is buried
in how much farther each element is from the target.

This is the point where radar becomes spatial rather than temporal. A single
antenna gives you a distance measurement; a line of antennas lets you compare
phase across positions and recover direction. The radar is no longer asking only
"how long did the echo take?" It is now asking "from which angle did that echo
arrive?" That is the leap from a scalar measurement to a directional estimate.

### Why element spacing is half a wavelength

The spacing d is a trade-off. Wider spacing makes the phase difference grow
faster with angle, so the beam is narrower and resolves angles better — but the
phase wraps every full wavelength, and past d = lambda/2 the array cannot tell
one direction from another: it grows spurious **grating lobes**, whole extra
copies of the main beam. Narrower spacing is unambiguous but gives a wider beam.

The standard compromise is d = lambda/2. Then the phase step per element is

    Delta_phi = (2 pi d / lambda) * sin(theta) = pi * sin(theta)

which stays within plus or minus pi over the whole visible range (plus or minus
90 degrees), so there is exactly one main lobe and no grating lobes.

### The steering vector

The phase step builds up along the array. Element 0 has phase 0, element 1 has
the step, element 2 twice the step, and so on. The complex values at each
element form the steering vector

    a(theta) = [1, e^{j Delta_phi}, e^{j 2 Delta_phi}, ..., e^{j (N-1) Delta_phi}]

It is one complex number per element — the pattern of echo phases the array
records for a wave from theta. For the baseline 20-degree target at half-
wavelength spacing, Delta_phi came to about 61.6 degrees and the extra path per
gap was about 2.1 cm (0.17 wavelengths).

The steering vector is the key turning point in array processing. It is not just a
mathematical convenience; it is the exact phase template that the radar uses to
ask: "how much does this incoming angle resemble the direction I am steering
toward?" The radar does not guess the angle from a single element. It compares the
whole array pattern to a candidate direction and finds the best match.

### The array factor and the beam pattern

Summing the elements coherently gives the array factor

    AF(theta) = sum over n of w_n e^{j n k d sin(theta)},  k = 2 pi / lambda

At broadside every term is +1 and they add to N: a strong main lobe. Away from
broadside the phases spread out and partly cancel, forming sidelobes. With 8
elements the first null falls at about 14.5 degrees, so the beam is about 29
degrees wide, and the first sidelobe sits about 13 dB below the main lobe.

### Reading the pattern: nulls, beamwidth, and steering

The first null of a uniform array falls at

    sin(theta_null) = lambda / (N d)

so more elements, or wider spacing, both narrow the beam. To listen at a chosen
angle you phase-shift each element to undo the delay the wave picked up crossing
the array — the weights become a steering vector and the main lobe follows. That
is how the radar scans angles to find a target.

### Common mistake

Wider spacing is not always better. It narrows the main lobe but risks grating
lobes that look exactly like the real lobe, so the array cannot trust where it
points. Half-wavelength spacing is the sweet spot.

Also, only the *relative* phase between neighbouring elements carries direction;
the absolute phase at any one element depends on the total path and tells you
nothing about angle.

### Checkpoint answers

**Why does an off-broadside wave reach the elements at different times, and how
does that become an angle?** The wave travels an extra d*sin(theta) to each
successive element, so it arrives later and with a phase shift between
neighbouring elements. Because that shift depends on sin(theta), it encodes the
angle. Summing the elements coherently peaks where they line up, revealing the
direction.

**What happens if you double the spacing to lambda?** The inter-element phase
step doubles, the main lobe narrows, and the pattern begins to fold over — the
phase reaches a whole cycle inside the visible range, so grating lobes appear
and an incoming direction is no longer unambiguous. The extra lobes come from
the phase wrapping exactly a full turn at other angles, making those directions
look identical to the true main lobe.

### Closing the loop

**How a line of antennas turns a time difference into an angle.** A wave from
theta travels d*sin(theta) farther to each successive element, arriving at a
different time and phase. The angle is recovered from the phase difference
between elements, and the array factor peaks where the elements line up.

**What the spacing is and why half a wavelength.** Elements are d apart; the
standard is lambda/2, where the phase step pi*sin(theta) stays within plus or
minus pi over the visible range, giving one unambiguous main lobe. Wider spacing
narrows the beam but risks grating lobes.

**How the phase step forms the steering vector.** The step is
(2 pi d/lambda) sin(theta), and the steering vector stacks one phase per
element: a(theta) = [1, e^{j Delta_phi}, ..., e^{j (N-1) Delta_phi}]. For the
baseline target the step was 61.6 degrees.

**Why the array factor has a main lobe and sidelobes.** Summing the elements
grows to N at broadside and falls where phases spread and cancel; the central
hump is the main lobe and the smaller humps are the sidelobes. With 8 elements
the first null is at 14.5 degrees.

**When and why grating lobes appear.** Past half-wavelength spacing the phase
step can reach a full 2 pi inside the visible range, adding false main lobes at
other angles. For d = 1.5 lambda they sat at plus or minus 41.8 degrees. The
array cannot tell these from the true lobe, which is why half-wavelength spacing
is standard.

If you can retell these five answers, you know how an array measures direction —
the coordinate that lets a radar point at a target in angle as well as range and
velocity.

## Chapter 8 — Direction of Arrival and Interference

### What you should be able to explain

- How a set of snapshots becomes a covariance matrix R.
- How scanning a spatial spectrum turns R into an angle estimate.
- Why the Bartlett scan cannot separate targets that are close in angle.
- How the Capon (MVDR) scan resolves them, and the price it pays.
- Why a strong interferer masks a weak target in a conventional scan, and how an adaptive scan recovers it.

### The missing measurement: where sideways

Notebook 7 gave you a beam you can point. A real radar does more than draw a
pattern — it *scans* that beam over every angle and reads where the power peaks.
That is direction of arrival (DOA): sweeping a spatial spectrum over candidate
angles and treating the peaks as target directions. It is the natural completion
of range and velocity, except that the conventional scan has two weaknesses you
must understand: it blurs close targets, and it can be drowned out by a loud
interferer.

### From snapshots to a covariance

At each moment the array records a snapshot: a vector x of N complex values, one
per element. Each snapshot is the sum of the targets' steering vectors (scaled
by their amplitudes) plus noise. Over many moments you collect many snapshots
and average their outer products into the sample covariance

    R = (1/K) * sum over snapshots of x x^H

R is the object both scans read from. Its diagonal entries hold the per-element
power, and its off-diagonal entries hold the correlations between elements —
which is exactly where the phase differences that carry the angle live. For the
baseline 8-element array the diagonal came out near 2 (target power plus noise),
and R is Hermitian: R equals its own conjugate transpose, as it must for any
real covariance.

### Scanning a spatial spectrum: Bartlett

Imagine a plane wave arriving from each candidate angle theta and ask how
strongly the array's data agree with it. The Bartlett beamformer simply weights
the array with the steering vector a(theta) and reads the power:

    P_Bartlett(theta) = a(theta)^H R a(theta)

Sweeping theta, the power peaks where a(theta) matches the actual direction of a
source. For a single target at 20 degrees the scan peaks cleanly at 20 — the
simplest possible angle estimate.

### The limit: close targets blur together

Bartlett's beam is as wide as the array's main lobe, about 14 degrees for our 8
elements. Two targets closer together than that produce peaks that merge into
one. Adding a second target at 30 degrees — only 10 away — the Bartlett scan
reports a single wide bump somewhere between them (at about 25 degrees) instead
of two. The beam is simply too fat to see the separation.

### The fix: Capon / MVDR

Capon's insight is to make the weights *adaptive*. Instead of fixed
steering-vector weights, it chooses weights that pass the look direction with
unit gain while minimising power from every other direction. That constraint
forces sharp notches at the other sources, so the response is far narrower than
Bartlett's fixed beam:

    P_Capon(theta) = 1 / ( a(theta)^H R^-1 a(theta) )

For the two-target scene Capon resolves both: sharp peaks at about 22.4 and 27.7
degrees. It sees what Bartlett cannot. The price is that Capon needs a reliable
estimate of R and its inverse — with too few snapshots that inverse is unstable
and Capon invents spurious peaks.

The conceptual difference is important: Bartlett answers "how much total energy
is in this look direction?" Capon answers "what weights let me pass the signal
from this direction while suppressing everything else?" That is a different and
stronger question, and it is exactly why Capon can resolve close targets while a
simple beam scan cannot.

### A strong interferer can mask the target

Now the problem is not two weak targets but one weak target and one very loud
interferer: our target at 20 degrees and a strong interferer at -30 degrees, 20
dB stronger. In the Bartlett scan the interferer's broad response through the
beam's sidelobes swamps everything. The target's feature is buried more than 15
dB below the interferer peak and drifts off its true angle. To a conventional
radar the scene looks like *only* the interferer: the weak target is masked.

### Capon confines the interferer and recovers the target

Capon combines the elements so that a strong source at one angle cannot speak
loudly at the target's angle. The interferer's energy is *confined* to its own
direction instead of leaking through sidelobes, so the weak target's peak
reappears at its true 20-degree angle, exactly on target. Looking at the
before-and-after numbers: Bartlett's target feature collapses from 0 dB (target
alone) to about -16 dB and drifts to 21.6 degrees, while Capon's stays at 20.0
degrees throughout. That contrast — a conventional scan at the mercy of a loud
neighbour, an adaptive scan not — is the heart of the notebook.

### Common mistake

Bartlett's resolution is not something you can tweak away. It is the best
*non-adaptive* scan, and its width is fixed by the array aperture (N d). You
cannot beat it with weights; you must go adaptive, and adaptivity needs an
estimated covariance and its inverse.

Equally, do not trust Capon on too few snapshots. R is estimated from snapshots,
and with too few the inverse is unreliable and Capon shows spurious peaks. With
8 snapshots the two-target scene produced 3 peaks; with 2000 it cleanly found 2.

### Checkpoint answers

**Why can Bartlett not separate two close targets, and how does Capon?**
Bartlett's fixed beam has a finite width (about 14 degrees here), so targets
closer than that blend into one broad bump. Capon is adaptive: it passes the
look angle and minimises power from everywhere else, which forces sharp notches
at the other sources and lets it resolve peaks the fixed beam cannot.

**How does the target's fate differ between the scans when a loud interferer
sits nearby?** In Bartlett the interferer leaks power through the sidelobes and
buried the weak target (its feature fell to about -16 dB and drifted off angle),
so the target disappeared. In Capon the interferer is confined to its own angle
and the target stayed as a sharp peak at exactly 20 degrees — recovered.

### Closing the loop

**How snapshots become an angle.** Averaging many snapshots x x^H builds the
covariance R, whose cross-element entries carry the phase differences that
encode direction. Scanning a power measure built from R and the steering vector
a(theta) peaks at a source's angle.

**Why Bartlett cannot separate close targets.** Its resolution is fixed by the
array main-lobe width, about 14 degrees, so targets 10 degrees apart merged into
one bump near 25 degrees.

**How Capon resolves them.** It chooses adaptive weights that pass the look
direction and minimise all other power, forcing sharp notches at other sources —
giving two resolved peaks at 22.4 and 27.7 degrees.

**The price Capon pays.** It needs a trustworthy estimate of R and its inverse.
With too few snapshots the inverse is unstable and Capon produces spurious
peaks; with enough snapshots it is clean.

**How a loud interferer masks the target, and how adaptivity saves it.** In
Bartlett, sidelobe leakage from a 20 dB-stronger interferer buried the target
feature. In Capon, the interferer is confined to its own angle and the target
reappeared at exactly 20 degrees, so the radar is not fooled into thinking the
scene holds only the interferer.

If you can retell these five answers, you understand how a radar turns its array
into a direction-finder that stays trustworthy even with loud neighbours.

## Chapter 9 — Beam Steering and Adaptive Nulling

### What you should be able to explain

- What the array weights do, and how steering points the main lobe at the target.
- How an LCMV constraint forces a null at the interferer's angle.
- How deep that null is, and why steering alone cannot provide it.
- Why the null is applied before the matched filter.
- How an adaptive null removes the interferer from the range-Doppler map while preserving the target.

### Combining the array is choosing weights

Every way of using the array reduces to one weight vector w, one complex gain
per element. The combined output is

    y = w^H x

where x is the snapshot at one moment. The beam pattern you drew in Notebook 07
is just |w^H a(theta)|^2 — how strongly this weighting responds to a wave from
each angle. So pointing the array and nulling an interferer are the same act:
choosing w.

### Steering the beam at the target

To listen to the target at 20 degrees, choose weights w = a(20)/N — the target's
own steering vector, scaled to unit response. A wave from 20 degrees then adds
coherently across the elements (the main lobe points there), while a wave from
another angle falls into the sidelobes. The main lobe peaks exactly at 20
degrees, but the response at the interferer's -30 degrees is only about -18.6 dB
down: it still leaks through a sidelobe.

This is the cleanest way to frame the next idea: steering is a pointing action,
not a rejection action. It tells the array to listen in one direction, but it
does not tell it to suppress the other direction. The beam can still leak power
through sidelobes, and that is exactly why a strong interferer can survive a
beam that is otherwise aimed correctly.

### Why steering alone cannot reject the interferer

Steering points the beam but imposes no constraint to reject other directions.
At -30 degrees the response is only -18.6 dB below the main lobe, so an
interferer 30 dB stronger than the target arrives about 30 - 18.6 = 11 dB above
the target even though you aimed straight at the target. Pointing is not
rejection.

### Forcing a null: the LCMV constraint

Collect the steering vectors of the target and interferer into a constraint
matrix C = [a(20), a(-30)] and demand

    C^H w = [1, 0]

meaning "respond with gain 1 to the target and gain 0 to the interferer". The
linear-constrained minimum-variance (LCMV) choice satisfies this while also
minimising output power:

    w = C (C^H C)^{-1} f,   f = [1, 0]

This is constraint-driven nulling: you state the null angle directly instead of
scanning for it, as with Capon. The constraint check came out exactly [1, 0], the
response at the target was 0 dB, and the response at -30 degrees fell to about
-319 dB — a null limited only by numerical precision, versus the -18.6 dB that
steering alone left.

### Why the null happens before the matched filter

The null is a *spatial* operation (which direction a wave came from), while the
matched filter is a *temporal* one (how far away it is). Apply the spatial
weights to the raw array snapshot first, cancelling the interference in angle;
then range-compress and Doppler-process the clean signal that remains. Nulling
after pulse compression would try to cancel a mixed signal and would not be clean.

### The payoff in the range-Doppler map

With steering-only weights, the 30 dB-stronger interferer leaked through the
sidelobe and inflated both Doppler bins at the target's range, muddling the map.
After the LCMV null, the interferer's own bin fell back to the noise floor (1471
down to about 376, the same as the interferer-free reference) while the target's
bin matched its clean, no-interference level (422 against 429). The interferer is
gone and the target is preserved at exactly its true strength.

### Common mistake

A common mistake is to think steering toward the target should be enough. It is
not: steering has no constraint to reject other directions, so it leaves
sidelobes a strong interferer punches through. Rejection requires an explicit
null, which is exactly what the LCMV constraint adds.

Another is to apply the null after pulse compression. The null is a spatial
operation on the array snapshot; the matched filter is a temporal one. Cancel in
space first, then range- and Doppler-process what remains.

### Checkpoint answers

**Why does steering toward the target not remove a strong interferer that sits
off to the side?** Steering sets unit response at the target but puts no
constraint on other directions. The beam keeps sidelobes, and at -30 degrees the
response is only -18.6 dB below the main lobe, so an interferer 30 dB stronger
still arrives roughly 11 dB above the target.

**What does the LCMV constraint C^H w = [1, 0] demand, and what does it do to the
beam at -30 degrees?** It demands the weights respond with gain 1 to the target's
steering vector and gain 0 to the interferer's. At -30 degrees the beam response
collapses to about -319 dB, a deep null, while staying at 0 dB at the target.

### Closing the loop

**What the weights do and how steering points the lobe.** Every use of the array
is a weight vector w. Steering picks w = a(target)/N so a wave from the target
adds coherently and the main lobe points there.

**How an LCMV constraint forces a null.** You put the target and interferer
steering vectors into C and demand C^H w = [1, 0]. Solving w = C (C^H C)^{-1} f
picks the weights that keep the target at full gain and set the interferer to zero.

**How deep the null is and why steering cannot give it.** The LCMV null sat at
about -319 dB versus the -18.6 dB sidelobe steering left. Steering only points;
it has no constraint to reject other directions.

**Why the null happens before the matched filter.** The null is spatial (angle),
the matched filter is temporal (range). Cancel the interference in angle first,
then range- and Doppler-process the clean signal.

**How the null removes the interferer from the range-Doppler map.** Before, the
interferer inflated both Doppler bins at the target's range. After the null, its
bin fell to the noise floor while the target's matched its interferer-free level.
The interferer is gone; the target is preserved.

If you can retell these five answers, you can point an array and deliberately
silence a jammer while keeping the target — the sharpest tool in the beamforming
kit.

## Chapter 10 — Integration and Portfolio Artifacts

### What you should be able to explain

- How the whole chain fits together, from waveform to range, velocity, angle, and null.
- Where each earlier notebook contributes to the final system.
- How the stages share one scene and one set of helpers, so their numbers agree.
- How the final artifacts are produced and exported, including saving the portfolio figure.
- How to tell the entire radar story end to end in your own words.

### The whole chain in one scene

Notebook 10 does not add new physics - it joins the pieces you built one at a
time into one coherent pipeline and gathers the results into a single portfolio
artifact. A shared scene (target at 1000 m moving at 20 m/s, with an interferer
at -30 degrees) flows through every stage, so the numbers all stay consistent.

### Restoring delay, Doppler, and angle

The snag in earlier notebooks - that the matched filter, the range-Doppler map,
and the beam all plain-normalize their own strongest peak - is resolved here by
reusing the packaged helpers on one scene. Each stage is a short cell that calls
the helper its own notebook built, so the range read by the matched filter, the
velocity read by the range-Doppler map, and the angle read by the DOA scan all
agree without hand-tuning the normalisation.

### The range measurement (Notebook 4)

Feed the echo to the matched filter. The chirp compresses into a sharp peak whose
position is the two-way delay, converted to range. With a 5 MHz bandwidth the
range resolution is about 30 m, and the baseline target at 1000 m reads back at
997 m.

### The range-Doppler map (Notebook 5)

Repeat over the 64 pulses with the target moving. The slow-time FFT turns the
echo's phase drift into a velocity axis, producing a range-Doppler map with
range on one axis and velocity on the other; the target stands out at
(1000 m, 20 m/s).

### The beam, the DOA scan, and the null (Notebooks 7-9)

The same array that compressed the echo in range is now used in angle. The array
factor shows the main lobe and sidelobes of the 8-element half-wavelength beam;
the Bartlett scan of the covariance finds the target's direction at 20 degrees;
and steering plus LCMV weights drive the interferer down from -18.6 dB (steer
only) to about -319 dB, while the target is held at 0 dB.

### The portfolio figure and the export

The final cell gathers four panels - waveform, range-Doppler map, beam-null
overlay, and DOA scan - onto one figure, then saves it to a PNG on disk. That one
figure is the beginner-track portfolio artifact: range, velocity, direction, and
interference rejection all on one page.

### Common mistake

Treating the stages as independent boxes that happen to share a plot. They are
not independent - they share one scene and one set of helpers, and the numbers
must stay consistent: the same delay gives the same range whether read by the
matched filter or the map, and the same 20-degree angle appears in the beam, the
DOA scan, and the null. Also remember the null is only as good as the constraint:
you must know the interferer's direction (via a DOA scan) before you can null it.

### Checkpoint answers

**How a transmitted chirp becomes range, velocity, and direction.** The chirp is
compressed by the matched filter into a peak whose delay gives range (Notebook 4).
The phase drift across the slow-time pulses gives the Doppler velocity (Notebook
5). The delay differences across the array give the angle, found by scanning the
array factor or a spatial spectrum (Notebooks 7-8), and the same angle is used to
steer and null (Notebook 9).

**Which notebook introduced each piece.** The chirp came from Notebook 1, the
matched filter from Notebook 4, the range-Doppler map from Notebook 5, the Kalman
track from Notebook 6, the steering vector from Notebook 7, the Capon scan from
Notebook 8, and the LCMV null from Notebook 9.

### Closing the loop

The five answers from the opening now line up: a single scene flows through the
stages, each stage reuses the helper its own notebook built, the numbers agree
across range, velocity, and angle, the artifacts are gathered and exported, and
you can retell the story in one breath - transmit, echo, compress for range, FFT
for velocity, scan for direction, steer and null to hide a jammer. If you can
defend that sentence, you command the whole chain.

---

## Final learner summary

If you step back from the equations, the whole course has one simple plot:
radar starts with a pulse, measures a delay, extracts a Doppler phase, measures
angle from spatial differences, and then makes decisions under uncertainty.

That is why the sequence matters. You first learn to hear a target in one
dimension, then in two dimensions, then in three dimensions of information.
Range is time-of-flight. Velocity is phase drift across pulses. Angle is phase
spread across the array. Filtering, tracking, and adaptive nulling are what make
those measurements usable when the world is noisy, moving, and cluttered.

The notebooks give you the direct implementation; this guide gives you the
mental model. If you can explain the chain in one paragraph, you are ready to
build from it rather than only copy it. That is the real goal of the beginner
track: not memorising formulas, but understanding the sequence of ideas so you
can reason from first principles whenever the radar scenario changes.
