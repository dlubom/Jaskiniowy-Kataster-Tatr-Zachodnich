#!/usr/bin/env python3
"""
Average multiple survey shots for the same leg in a Walls .SRV file.

Usage:
    python average_shots.py <path/to/FILE_S.SRV>

For each group of consecutive shots measuring the same station pair (A->B and
B->A), replaces them with a single averaged shot in the forward direction.

Algorithm:
  - Distance    : arithmetic mean of all measurements
  - Azimuth     : circular mean (handles 0/360 wrap correctly)
                  backward shots: az = (az_back + 180) % 360 before averaging
  - Inclination : arithmetic mean
                  backward shots: inc = -inc_back before averaging
"""

import math
import re
import sys
from datetime import date


def circular_mean_degrees(angles):
    """Circular mean for angles in degrees (handles 0/360 boundary)."""
    sin_sum = sum(math.sin(math.radians(a)) for a in angles)
    cos_sum = sum(math.cos(math.radians(a)) for a in angles)
    return (math.degrees(math.atan2(sin_sum, cos_sum)) + 360) % 360


def is_shot_line(line):
    """Return True if line is a survey shot: FROM TO DIST AZ INC."""
    stripped = line.strip()
    if not stripped or stripped[0] in (';', '#'):
        return False
    parts = stripped.split()
    if len(parts) != 5:
        return False
    try:
        float(parts[2])
        float(parts[3])
        float(parts[4])
        return True
    except ValueError:
        return False


def parse_shot(line):
    parts = line.strip().split()
    return parts[0], parts[1], float(parts[2]), float(parts[3]), float(parts[4])


def format_shot(frm, to, dist, az, inc, indent=""):
    return f"{indent}{frm}\t{to}\t{dist:.3f}\t{az:.2f}\t{inc:.2f}\n"


def get_indent(line):
    m = re.match(r'^(\s*)', line)
    return m.group(1) if m else ""


def average_shots(srv_file):
    with open(srv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    result = []
    i = 0
    stats = {"groups": 0, "shots_before": 0, "shots_after": 0}

    while i < len(lines):
        line = lines[i]

        if not is_shot_line(line):
            result.append(line)
            i += 1
            continue

        frm, to, dist, az, inc = parse_shot(line)
        fwd_from, fwd_to = frm, to
        pair = frozenset([frm, to])
        indent = get_indent(line)

        # Collect all consecutive shots with the same station pair
        group = [(frm, to, dist, az, inc)]
        i += 1

        while i < len(lines) and is_shot_line(lines[i]):
            n_frm, n_to, n_dist, n_az, n_inc = parse_shot(lines[i])
            if frozenset([n_frm, n_to]) == pair:
                group.append((n_frm, n_to, n_dist, n_az, n_inc))
                i += 1
            else:
                break

        stats["shots_before"] += len(group)

        if len(group) == 1:
            result.append(line)
            stats["shots_after"] += 1
        else:
            all_dist, all_az, all_inc = [], [], []
            fwd_count = bwd_count = 0

            for (s_frm, s_to, s_dist, s_az, s_inc) in group:
                all_dist.append(s_dist)
                if s_frm == fwd_from and s_to == fwd_to:
                    all_az.append(s_az)
                    all_inc.append(s_inc)
                    fwd_count += 1
                else:
                    all_az.append((s_az + 180) % 360)
                    all_inc.append(-s_inc)
                    bwd_count += 1

            avg_dist = sum(all_dist) / len(all_dist)
            avg_az = circular_mean_degrees(all_az)
            avg_inc = sum(all_inc) / len(all_inc)

            result.append(format_shot(fwd_from, fwd_to, avg_dist, avg_az, avg_inc, indent))
            stats["groups"] += 1
            stats["shots_after"] += 1

            print(
                f"  {fwd_from}->{fwd_to}: {len(group)} shots "
                f"({fwd_count} fwd + {bwd_count} bwd) "
                f"-> dist={avg_dist:.3f}  az={avg_az:.2f}  inc={avg_inc:.2f}"
            )

    with open(srv_file, 'w', encoding='utf-8') as f:
        f.writelines(result)

    removed = stats["shots_before"] - stats["shots_after"]
    print(
        f"\nDone: {stats['groups']} legs averaged, "
        f"{stats['shots_before']} -> {stats['shots_after']} shots "
        f"({removed} removed)."
    )
    print(f"File: {len(result)} lines (was {len(lines)}).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path/to/FILE_S.SRV>")
        sys.exit(1)
    average_shots(sys.argv[1])
