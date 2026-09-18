# Beginner radar notebook story

This page follows the beginner notebook path and the helper reference that sits alongside it. It is intentionally small and teaching-focused. It is not a formal public API and it is not a broad production platform. It is a learning path: one radar, built step by step, with the math kept visible.

The beginner notebooks tell one continuous story: a radar is built layer by layer, from a simple pulse to a system that can detect a target, estimate its motion, sense its direction, and reject interference.

This is not a set of disconnected exercises. It is one narrative arc in which each chapter adds one missing piece of the radar system.

## The story begins with a pulse

The first idea is simple but important: radar does not transmit continuously. It sends a short burst and then listens for the echo. That gap between transmission and reception is the measurement of range.

The notebooks begin by making that idea concrete. In the early chapters, students work with the basic pulse and then move to the chirp, which carries the same energy but spreads it over time in a controlled way. The benefit is subtle but powerful: a long pulse gives more energy, and the chirp's frequency sweep gives the signal enough structure to resolve targets sharply.

By the time the learner reaches the range chapter, the point is clear: the echo is weak, delayed, and buried in noise, and the signal processing step is what makes the measurement possible.

## The echo comes back, but it is weak

The next part of the story introduces the channel model. The target reflection arrives later than the transmitted pulse, it is attenuated by path loss, and it is mixed with noise. This is where the physical reality of radar becomes visible: the strongest signal is not always the relevant one, and the signal you want may be tiny compared with the rest of the received waveform.

This is also where matched filtering enters the story. The radar knows the waveform it sent, and it uses that knowledge to slide the template across the signal and find where the echo aligns. The result is a strong, narrow peak at the target delay, and the range estimate becomes explicit.

## Velocity enters the story next

Once the learner understands how range is extracted from a single pulse, the next challenge is motion. A single measurement tells you where the target was at one instant, but not whether it is moving and how quickly.

The beginner track introduces Doppler processing by looking across many pulses. The target echo does not move in range from pulse to pulse, but its phase rotates. That phase evolution carries the velocity information. When the data are organized across pulses and transformed with an FFT, the result is a range-Doppler map: a picture that shows both range and radial velocity.

This is a major milestone in the story, because it turns the radar from a ranging instrument into a dynamic sensing system.

## The track becomes stable over time

The next layer is tracking. In real radar operation, detections are noisy and imperfect. A target can jump around from one estimate to the next, and the measurements are not always perfectly trustworthy.

The Kalman filter gives the learner a way to balance prediction and measurement. It smooths the noisy track and keeps the estimate coherent over time. At this point the story is no longer only about detecting a target; it is about maintaining a stable understanding of where that target is moving.

## The radar then learns direction

Once the radar knows how far away the target is and how fast it is moving, the next question is: where is it relative to the antenna? This is where the array story begins.

A single antenna gives a point measurement, but a line array adds phase differences between elements. Those phase differences encode the direction of arrival. In the beginner notebooks, the learner builds the array geometry, studies the beam pattern, and sees how the aperture focuses energy in certain directions while suppressing others.

This is the transition from range-Doppler sensing to spatial sensing. The radar starts to answer not only where the target is in time, but where it is in angle.

## Interference becomes part of the learning problem

The final chapters move from idealized target detection to a more realistic radar environment. A strong interferer can mask a weaker target, and naive spatial processing may not separate them. The beginner track introduces the idea of beam steering and adaptive nulling.

The learner sees how to form a beam toward the target while placing a null toward the jammer. This is where the full system becomes more like a real radar: it is not just detecting targets, it is managing competing sources and preserving the desired signal in a noisy environment.

## The full picture in one arc

The beginner narrative ends with a single integrated view: a chirp is transmitted, compressed into range, converted into Doppler across pulses, stabilized with a tracking filter, and then interpreted with array processing to determine direction. The result is a coherent radar story in which each layer builds on the previous one.

The arc is intentionally simple to follow:

Transmit a chirp → compress it into range → extract velocity from pulse-to-pulse phase → smooth the track → sense angle with an array → steer and null to survive interference.

This is the learning path the notebooks are designed to teach.

## Where to go next

Use the notebook story as the primary learning path, and use this site as the reference map.

- [Helper scripts](helper-api.md) — the beginner-friendly reference for the notebook support utilities
- Source narrative: beginner/00-intro-story.md — the full narrative draft for the course arc

The point of this page is not to be a broad public API or a product catalog. It is to help a learner understand the sequence of ideas, the chapter flow, and the purpose of the helper functions used throughout the beginner notebooks.
