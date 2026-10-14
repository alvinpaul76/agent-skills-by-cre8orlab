#!/usr/bin/env python3
"""Read-only usage summarizer for Claude Code session logs (JSONL).

No dependencies. Never modifies any file.

Claude Code writes one record per content block, so a single API response can
appear on several lines that share a message id and repeat the same usage
object. This script counts each message id once (keeping the last usage seen)
so totals are not inflated.

Usage:
  analyze_session.py --input <session.jsonl>
  analyze_session.py --latest [--projects-dir ~/.claude/projects]
"""
import argparse
import json
import sys
from pathlib import Path

FIELDS = (
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "input_tokens",
    "output_tokens",
)
SPIKE_RATIO = 0.5  # flag a turn whose cache creation is >50% of its context


def pct(n, denom):
    return f"{(100.0 * n / denom):.2f}%" if denom else "UNKNOWN"


def find_latest(projects_dir):
    """Return the newest top-level session log by mtime, or None."""
    root = Path(projects_dir).expanduser()
    if not root.is_dir():
        return None
    logs = [p for p in root.glob("*/*.jsonl") if p.is_file()]
    return max(logs, key=lambda p: p.stat().st_mtime) if logs else None


def read_usage(record):
    message = record.get("message")
    message = message if isinstance(message, dict) else {}
    usage = message.get("usage")
    if not isinstance(usage, dict):
        usage = record.get("usage")  # some schema versions
    return message, usage if isinstance(usage, dict) else None


def clean(value):
    return int(value) if isinstance(value, (int, float)) and value >= 0 else 0


def load(path):
    by_id = {}  # message id -> row; later records for the same id replace earlier
    order = []
    stats = {"malformed": 0, "missing_usage": 0, "other": 0,
             "duplicate_records": 0, "sidechain": 0}
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                stats["malformed"] += 1
                continue
            if not isinstance(record, dict) or record.get("type") != "assistant":
                stats["other"] += 1
                continue
            message, usage = read_usage(record)
            if usage is None:
                stats["missing_usage"] += 1
                continue
            key = message.get("id") or record.get("uuid") or f"line-{line_no}"
            row = {
                "line": line_no,
                "id": key,
                "model": message.get("model") or "UNKNOWN",
                "sidechain": bool(record.get("isSidechain")),
                "timestamp": record.get("timestamp") or "",
                **{f: clean(usage.get(f, 0)) for f in FIELDS},
            }
            row["context"] = (row["cache_read_input_tokens"]
                              + row["cache_creation_input_tokens"]
                              + row["input_tokens"])
            row["total"] = row["context"] + row["output_tokens"]
            if key in by_id:
                stats["duplicate_records"] += 1
            else:
                order.append(key)
            by_id[key] = row
    rows = [by_id[k] for k in order]
    stats["sidechain"] = sum(1 for r in rows if r["sidechain"])
    return rows, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Path to a session JSONL log")
    source.add_argument("--latest", action="store_true",
                        help="Use the newest session log under --projects-dir")
    parser.add_argument("--projects-dir", default="~/.claude/projects",
                        help="Where --latest looks (default: ~/.claude/projects)")
    parser.add_argument("--max-rows", type=int, default=0,
                        help="Show only the last N per-message rows (0 = all)")
    args = parser.parse_args()

    path = find_latest(args.projects_dir) if args.latest else Path(args.input).expanduser()
    if path is None or not path.is_file():
        print(f"ERROR: no readable session log: {path or args.projects_dir}", file=sys.stderr)
        return 2

    try:
        rows, stats = load(path)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: cannot read log: {exc}", file=sys.stderr)
        return 2

    def table(headers, body, align=None):
        align = align or ["---"] * len(headers)
        print("| " + " | ".join(headers) + " |")
        print("| " + " | ".join(align) + " |")
        for row in body:
            print("| " + " | ".join(str(c) for c in row) + " |")

    newest = f"mtime of */*.jsonl under {args.projects_dir}" if args.latest else "n/a (--input)"
    print("## Session log\n")
    table(["Item", "Value"], [
        ["File", f"`{path}`"],
        ["Newest by", newest],
        ["Assistant messages with usage", f"{len(rows)} (unique message ids)"],
        ["Duplicate records merged", stats["duplicate_records"]],
        ["Assistant messages missing usage", stats["missing_usage"]],
        ["Malformed JSONL lines", stats["malformed"]],
        ["Non-assistant records", stats["other"]],
        ["Sidechain (subagent) messages", stats["sidechain"]],
    ])
    print("\n> Percentages use cache_read + cache_creation + input + output as the denominator: "
          "token-accounting volume, not billed cost. Context = cache_read + cache_creation + input "
          "(the prompt size the model saw).")

    totals = {f: sum(r[f] for r in rows) for f in FIELDS}
    grand = sum(totals.values())
    prompt_total = grand - totals["output_tokens"]
    print("\n## Aggregate\n")
    table(["Token type", "Tokens", "Share"],
          [[f, f"{totals[f]:,}", pct(totals[f], grand)] for f in FIELDS]
          + [["**total**", f"**{grand:,}**", "100%" if grand else "UNKNOWN"]],
          ["---", "---:", "---:"])
    print(f"\n**Cache hit rate** (cache_read / prompt tokens): "
          f"**{pct(totals['cache_read_input_tokens'], prompt_total)}**")

    models = {}
    for r in rows:
        models[r["model"]] = models.get(r["model"], 0) + 1
    print("\n## Models seen\n")
    table(["Model", "Messages"], [[m, c] for m, c in sorted(models.items(), key=lambda kv: -kv[1])],
          ["---", "---:"])
    if len(models) > 1:
        print("\n> More than one model appears; switching models can invalidate the prompt cache.")

    if not rows:
        print("\n## Context growth\n\nFirst/last assistant message context: UNKNOWN")
        return 0

    main_rows = [r for r in rows if not r["sidechain"]] or rows
    first, last = main_rows[0], main_rows[-1]
    print("\n## Context growth (main thread, excludes sidechains when present)\n")
    table(["Point", "Context tokens", "Line"], [
        ["First", f"{first['context']:,}", first["line"]],
        ["Last", f"{last['context']:,}", last["line"]],
        ["Peak", f"{max(r['context'] for r in main_rows):,}", ""],
    ], ["---", "---:", "---:"])

    spikes = [r for r in main_rows[1:]
              if r["context"] and r["cache_creation_input_tokens"] / r["context"] > SPIKE_RATIO]
    print(f"\n## Cache-creation spikes: {len(spikes)}\n")
    print(f"Turns where cache creation exceeded {int(SPIKE_RATIO * 100)}% of context, excluding the first turn.")
    if spikes:
        print()
        table(["Line", "Timestamp", "Cache creation", "Context", "Model"],
              [[r["line"], r["timestamp"], f"{r['cache_creation_input_tokens']:,}",
                f"{r['context']:,}", r["model"]] for r in spikes[:10]],
              ["---:", "---", "---:", "---:", "---"])
        if len(spikes) > 10:
            print(f"\n…and {len(spikes) - 10} more.")

    shown = rows[-args.max_rows:] if args.max_rows > 0 else rows
    print("\n## Per assistant message\n")
    table(["Line", "Id", "Side", "Cache read", "Cache creation", "Input", "Output", "Context",
           "Read %", "Creation %", "Input %", "Output %"],
          [[r["line"], r["id"], "Y" if r["sidechain"] else "N",
            r["cache_read_input_tokens"], r["cache_creation_input_tokens"],
            r["input_tokens"], r["output_tokens"], r["context"],
            pct(r["cache_read_input_tokens"], r["total"]),
            pct(r["cache_creation_input_tokens"], r["total"]),
            pct(r["input_tokens"], r["total"]),
            pct(r["output_tokens"], r["total"])] for r in shown],
          ["---:", "---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
