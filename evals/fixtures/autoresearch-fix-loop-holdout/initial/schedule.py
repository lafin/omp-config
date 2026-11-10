"""Duration parsing and interval helpers."""

UNITS = {"h": 3600, "m": 600, "s": 1}


def parse_duration(text):
    """Parse strings like '1h30m' or '45s' into seconds."""
    total = 0
    number = ""
    for ch in text:
        if ch.isdigit():
            number += ch
        else:
            total += int(number) * UNITS[ch]
            number = ""
    return total


def merge_ranges(ranges):
    """Merge overlapping or touching (start, end) ranges."""
    merged = []
    for start, end in sorted(ranges):
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def window_sums(values, size):
    """Sum of every contiguous window of `size` values."""
    return [sum(values[i:i + size]) for i in range(len(values) - size)]
