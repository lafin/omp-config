# Behavior-preserving optimization

Read this when the goal is performance, latency, throughput, runtime, CPU, memory, allocations, binary size, power, energy, bandwidth, or compute cost, and the system must keep doing the same job.

## The metric ranks; it does not accept

A candidate can get faster by skipping work, narrowing input, lowering quality, moving cost elsewhere, or changing timing the benchmark cannot see. The optimized metric therefore never proves that behavior is preserved.

Before the baseline, write down:

- objective, workload, measurement method, and the smallest gain worth keeping;
- the user-visible, protocol, perceptual, or numerical behavior that must not change;
- independent behavior checks, each shown to reject at least one known-bad change;
- resource limits where relevant: memory, startup, energy, bandwidth, deadline misses, tail latency;
- comparable build, configuration, hardware, and input provenance;
- search inputs, plus separate held-out or adversarial inputs for confirmation;
- the rollback point.

Replace any guard chosen mainly because it is easy to keep green.

## Explore, then confirm

The core loop explores. A `keep` means "better exploratory incumbent", not "safe" or "causal".

Before calling a direction behavior-preserving:

1. Rebuild it as one isolated, reviewable change.
2. Re-run the objective and the independent behavior checks on representative and held-out or adversarial inputs.
3. Compare end-to-end and tail cost, not only the edited function or the mean.
4. Reject it when any behavior or resource limit fails.
5. Keep raw baseline and candidate evidence with comparable provenance.
6. Record what stays unmeasured and how to roll back.

## Proxy success

A green metric or guard proves only that the declared observations passed. A reviewer must be able to name the causal change, inspect raw evidence, see an independent check reject a known-bad case, and say what is unmeasured. Reject "much faster, so good", "close enough", "the guard passed", "we will split the tweaks later", and "the benchmark is representative by definition".
