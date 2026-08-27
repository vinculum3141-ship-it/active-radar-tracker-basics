# Learner Guide

This document is for you. It walks through the radar concepts introduced in
Notebooks 00 through 03 at a slower pace, with more background and physical
intuition than the notebooks can fit between code cells.

Each chapter opens with the same learning objectives as its notebook, walks
through the ideas in narrative form, and closes with expanded answers to the
opening questions. Use it before a notebook to prime yourself, or after a
notebook to fill in the gaps.

For every chapter, the notebook is the place to run code and see output. This
guide is the place to understand why the code works.

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

The two clocks turn the received data into a grid. One axis is fast time
(range), the other is slow time (pulse number / velocity). Any single pulse
answers "how far?"; the sequence of pulses answers "how fast?". This notebook
shows you how to read the second answer.

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

Now that you have one complex number per pulse at the target's range bin, the
tool from Notebook 01 reappears: an FFT. You take the fast Fourier transform of
the slow-time samples and look for the peak. It sits at the Doppler frequency.
This is exactly the frequency analysis you did on the transmit waveform, but
now the "signal" is sampled once per PRI rather than at 20 MHz.

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

You do not have to pick a single range bin by eye. Repeat the slow-time FFT at
*every* fast-time position and you get a two-dimensional array: one dimension
is range, the other is velocity, and the value at each cell is the echo power
for that combination. Plot it as a heatmap and you can read a whole scene at a
glance.

A single target shows up as one bright blob at its range and velocity. Two
targets that share a range but move at different speeds — invisible overlap in
fast time — split into two blobs along the velocity axis. This is why the
range-Doppler map is the standard radar display: it separates targets that
collapse into one peak in a single matched filter.

### Velocity resolution and ambiguity

Doppler has limits, and they mirror the range limits you met in Notebook 00.

**Resolution.** The slow-time observation is one CPI: 64 pulses at 1 ms, so
64 ms. The FFT over that window can distinguish frequencies separated by about
one bin, which translates to a velocity resolution of

    delta_v = lambda / (2 N PRI) = 0.1224 / (2 * 64 * 0.001) = 0.96 m/s

Two targets whose speeds differ by less than that appear as one blob.

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
