#!/usr/bin/env python3
"""Claude Code token tracker: input/output tokens + API-equivalent dollars.

Reads ~/.claude/projects/**/*.jsonl (Claude Code transcripts, incl. subagents).
Stdlib only.

  python3 tools/token_tracker.py                 # totals by model
  python3 tools/token_tracker.py --by day        # per day
  python3 tools/token_tracker.py --by project    # per project
  python3 tools/token_tracker.py --by session    # per session
  python3 tools/token_tracker.py --days 7        # last 7 days only
  python3 tools/token_tracker.py --project AIWorkshop

Dollars = what the same tokens would cost on the Claude API. On a Pro/Max
subscription you pay the flat fee, not this.
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# $ per 1M tokens: input, output, cache write 5m, cache write 1h, cache read.
# Source: Anthropic pricing (cached 2026-10-06). Update if prices change.
PRICES = {
    "claude-fable-5-1":  (10.00, 50.00, 12.50, 20.00, 0.25),
    "claude-mythos-5-1": (10.00, 50.00, 12.50, 20.00, 0.25),
    "claude-fable-5":    (10.00, 50.00, 12.50, 20.00, 1.00),
    "claude-opus-5-5":   (4.00, 20.00, 5.00, 8.00, 0.20),
    "claude-opus-5":     (5.00, 25.00, 6.25, 10.00, 0.50),
    "claude-opus-4-8":   (5.00, 25.00, 6.25, 10.00, 0.50),
    "claude-opus-4-7":   (5.00, 25.00, 6.25, 10.00, 0.50),
    "claude-opus-4-6":   (5.00, 25.00, 6.25, 10.00, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00, 2.50, 4.00, 0.20),
    "claude-sonnet-5":   (2.00, 10.00, 2.50, 4.00, 0.20),
    "claude-sonnet-4-6": (3.00, 15.00, 3.75, 6.00, 0.30),
    "claude-sonnet-4-5": (3.00, 15.00, 3.75, 6.00, 0.30),
    "claude-haiku-5-5":  (0.10, 0.50, 0.125, 0.20, 0.01),
    "claude-haiku-4-5":  (1.00, 5.00, 1.25, 2.00, 0.10),
}
# Haiku 5.5: prompts over 100K tokens use a 5x rate card.
HAIKU_55_LONG = (0.50, 2.50, 0.625, 1.00, 0.05)
FAST_MULTIPLIER = 2.0  # fast mode (speed == "fast") is 2x standard

FIELDS = ["input", "output", "cache_write", "cache_read", "cost"]


def price_for(model, prompt_tokens):
    for name, rates in PRICES.items():
        if model == name or model.startswith(name + "-"):  # tolerate date suffixes
            if name == "claude-haiku-5-5" and prompt_tokens > 100_000:
                return HAIKU_55_LONG
            return rates
    return None


def cost_of(usage, model):
    inp = usage.get("input_tokens", 0) or 0
    out = usage.get("output_tokens", 0) or 0
    read = usage.get("cache_read_input_tokens", 0) or 0
    write = usage.get("cache_creation_input_tokens", 0) or 0
    split = usage.get("cache_creation") or {}
    w1h = split.get("ephemeral_1h_input_tokens", 0) or 0
    w5m = split.get("ephemeral_5m_input_tokens", write - w1h) or 0

    rates = price_for(model, inp + read + write)
    if rates is None:
        return None
    p_in, p_out, p_w5, p_w1h, p_read = rates
    dollars = (inp * p_in + out * p_out + w5m * p_w5 + w1h * p_w1h + read * p_read) / 1e6
    if usage.get("speed") == "fast":
        dollars *= FAST_MULTIPLIER
    return dollars


def project_name(path, root):
    folder = path.relative_to(root).parts[0]
    home = str(Path.home()).replace("/", "-")  # e.g. "-home-alex"
    return folder.replace(home + "-", "").replace(home, "~") or "~"


def load(root, since, project_filter):
    seen = set()
    for path in root.rglob("*.jsonl"):
        project = project_name(path, root)
        if project_filter and project_filter.lower() not in project.lower():
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"usage"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = entry.get("message") or {}
                usage = msg.get("usage")
                model = msg.get("model", "")
                if not usage or not model or model.startswith("<"):
                    continue
                # One API response is logged once per content block: count it once.
                key = (msg.get("id"), entry.get("requestId"))
                if key in seen:
                    continue
                seen.add(key)
                stamp = entry.get("timestamp", "")
                try:
                    when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if since and when < since:
                    continue
                yield {
                    "model": model,
                    "project": project,
                    "session": entry.get("sessionId", path.stem)[:8],
                    "day": when.astimezone().strftime("%Y-%m-%d"),
                    "usage": usage,
                }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--by", choices=["model", "day", "project", "session"], default="model")
    ap.add_argument("--days", type=int, help="only the last N days")
    ap.add_argument("--project", help="only projects whose name contains this")
    ap.add_argument("--root", default=str(Path.home() / ".claude" / "projects"))
    args = ap.parse_args()

    since = datetime.now(timezone.utc) - timedelta(days=args.days) if args.days else None
    groups: defaultdict[str, dict[str, float]] = defaultdict(lambda: dict.fromkeys(FIELDS, 0))
    unpriced = set()

    for row in load(Path(args.root), since, args.project):
        u = row["usage"]
        g = groups[row[args.by]]
        g["input"] += u.get("input_tokens", 0) or 0
        g["output"] += u.get("output_tokens", 0) or 0
        g["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
        g["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
        c = cost_of(u, row["model"])
        if c is None:
            unpriced.add(row["model"])
        else:
            g["cost"] += c

    if not groups:
        print("No usage found.")
        return

    head = f"{args.by:<32} {'input':>12} {'output':>12} {'cache write':>13} {'cache read':>14} {'$ API-equiv':>12}"
    print(head)
    print("-" * len(head))
    total: dict[str, float] = dict.fromkeys(FIELDS, 0)
    order = sorted(groups) if args.by == "day" else sorted(groups, key=lambda k: -groups[k]["cost"])
    for name in order:
        g = groups[name]
        for k in FIELDS:
            total[k] += g[k]
        print(f"{name[:32]:<32} {g['input']:>12,} {g['output']:>12,} {g['cache_write']:>13,} {g['cache_read']:>14,} {g['cost']:>12,.2f}")
    print("-" * len(head))
    t = total
    print(f"{'TOTAL':<32} {t['input']:>12,} {t['output']:>12,} {t['cache_write']:>13,} {t['cache_read']:>14,} {t['cost']:>12,.2f}")
    if unpriced:
        print("\nNo price for (excluded from $):", ", ".join(sorted(unpriced)))


if __name__ == "__main__":
    main()
