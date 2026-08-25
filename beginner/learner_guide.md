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
the range resolution once pulse compression appears. The pulse width is 20
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
radar systems. But it has a limitation: its range resolution is tied directly to
its length. A long pulse has poor resolution. That limitation is what motivates
the chirp.

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

Plotted in time, both the rectangular pulse and the chirp look like
constant-amplitude bursts. The difference hides in the phase. The frequency
sweep plot in the notebook makes this visible: the instantaneous frequency ramps
linearly from zero to the bandwidth across the pulse. The rectangular pulse has
no sweep at all.

This is why the frequency view matters. A chirp that looks like "just another
pulse" in the time domain is revealed as a wideband waveform in the frequency
domain. And it is that bandwidth — not the pulse length — that determines the
range resolution after compression.

### Range resolution

Range resolution is the smallest separation between two targets that the radar
can tell apart. For a plain rectangular pulse it is set by the pulse length:

    delta_R = c * tau / 2

With the baseline values that gives roughly 3000 metres — very coarse.

For a chirp after pulse compression it is set by the bandwidth:

    delta_R = c / (2 * B)

With 5 megahertz of bandwidth that gives roughly 30 metres — a hundred times
better.

The improvement factor is the ratio of these two numbers, which equals the
time-bandwidth product. The notebook's resolution comparison cell computes both
values and shows the factor explicitly.

### The time-bandwidth product

The time-bandwidth product is:

    TBP = B * tau = 5 MHz * 20 microseconds = 100

This number is the compression ratio. The long chirp, squeezed by the matched
filter (introduced in Notebook 03), collapses into a peak roughly 100 times
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

## Chapter 2 — Channel Model and Echoes

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

In the received signal buffer, the echo begins at sample 133 and extends for
the length of the pulse (400 samples). The buffer must be at least 533 samples
long to hold the entire echo. The notebook builds this step by step: first the
empty buffer, then the pulse written at the correct offset.

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

The bottom panel of the notebook's three-part plot shows the problem: the small,
delayed echo disappears into the noise fluctuations. Without signal processing,
you cannot reliably tell whether the echo is present at all. This is what
motivates the matched filter in Notebook 03.

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
matched filter in Notebook 03 exploits the fact that the echo is a known shape
to concentrate its energy into a detectable peak.

---

## Chapter 3 — Matched Filtering and Range Estimation

### What you should be able to explain

- What correlation means in the matched-filter context.
- Why the compressed peak is sharper than the raw echo.
- How peak location converts to a range estimate.
- Why matched filtering beats simple thresholding.

### The problem this notebook solves

You have built the transmit waveform (Notebook 01) and seen what the channel
does to it (Notebook 02). The echo is in the received buffer, but it is buried
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
