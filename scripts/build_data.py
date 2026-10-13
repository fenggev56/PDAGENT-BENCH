"""Build data/leaderboard.json (and the README table) from the evaluation outputs.

Sources
  data/round1_earlier.csv          earlier evaluation, as reported in the paper table
  <later-eval>/results/<subset>/<model>/summary.json
                                   later evaluation (pdagent-bench_9.23eval harness)

Usage
  python3 scripts/build_data.py [--later-eval /path/to/eval]   (defaults from scripts/local_config.json)

To add a new model: run the harness for it, add an entry to LATER_MODELS below,
then re-run this script.
"""

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Local settings, kept out of git: {"later_eval": "/path/to/eval", "subset_dirs": {category key: results dir}}
LOCAL = ROOT / "scripts" / "local_config.json"

# key, display name, short label, N items, grader, group, description
CATEGORIES = [
    ("foundational", "Foundational Knowledge", "Foundational", 90, "judge", "Understanding",
     "Open-ended physical-design concepts: floorplanning, CTS, STA, DFT, extraction, device physics, flow I/O."),
    ("root_cause", "Root-Cause Analysis", "Root-Cause", 21, "judge", "Understanding",
     "Diagnose real backend failures (hold fixing, IR drop, congestion, SDC, multi-voltage) and propose fixes."),
    ("report", "Report Comprehension", "Report", 11, "judge", "Understanding",
     "Read EDA tool reports and screenshots (P&R and timing sign-off tools) and explain what they show. Multimodal."),
    ("sta", "Static Timing Analysis", "STA", 11, "rule", "Understanding",
     "Timing calculations and multiple-choice STA questions, several from circuit diagrams. Multimodal."),
    ("fm", "Formal Verification", "FM", 22, "rule", "Script Generation",
     "Exact Formality commands for library setup, read, match/verify and reporting."),
    ("eco", "ECO", "ECO", 10, "rule", "Script Generation",
     "PrimeTime ECO commands: timing fixes, false paths, change lists, violation reports."),
    ("pr_vendor1", "P&R Vendor 1", "P&R Vendor 1", 88, "rule", "Script Generation",
     "Exact Tcl for a commercial place-and-route tool: setup, floorplan, power, placement, CTS, routing, EM and antenna."),
    ("pr_vendor2", "P&R Vendor 2", "P&R Vendor 2", 90, "rule", "Script Generation",
     "Exact Tcl for a second commercial place-and-route tool: initialization and MMMC through floorplan, CTS, ECO and sign-off export."),
]

# model name in round1 csv -> (provider, open weights, multimodal)
EARLIER_MODELS = {
    "Qwen-VL-8B": ("Alibaba", True, True),
    "Qwen-VL-30B": ("Alibaba", True, True),
    "Qwen3-8B": ("Alibaba", True, False),
    "DeepSeek-Chat": ("DeepSeek", True, False),
    "DeepSeek-Reasoner": ("DeepSeek", True, False),
    "GPT-5-mini": ("OpenAI", False, True),
    "GPT-5.1": ("OpenAI", False, True),
    "Claude Sonnet 4.6": ("Anthropic", False, True),
    "Claude Opus 4.7": ("Anthropic", False, True),
    "GPT-5.5": ("OpenAI", False, True),
    "GPT-5.4-mini": ("OpenAI", False, True),
}
# results dir -> (display name, provider, open weights, api model)
LATER_MODELS = {
    "DeepSeek-V4.1-Flash": ("DeepSeek-V4.1-Flash", "DeepSeek", True, "deepseek-flash"),
    "GPT-5.6-luna": ("GPT-5.6 Luna", "OpenAI", False, "gpt-5.6-luna"),
    "GPT-5.6-sol": ("GPT-5.6 Sol", "OpenAI", False, "gpt-5.6-sol"),
    "Claude-sonnet5": ("Claude Sonnet 5", "Anthropic", False, "claude-sonnet-5"),
    "Claude-opus5": ("Claude Opus 5", "Anthropic", False, "claude-opus-5"),
}

ROUNDS = {
    "r1": {"label": "Earlier evaluation", "date": None,
           "judge": "LLM judge + human evaluation (paper Table 1)",
           "settings": "temperature 0 (pass@1) / 0.8 (pass@5), provider default output caps"},
    "r2": {"label": "2026-09-23 evaluation", "date": "2026-09-23",
           "judge": "GPT-5.4-mini rubric judge (blind)",
           "settings": "reasoning effort medium, no temperature, 32K output cap"},
}


def num(s):
    return round(float(s), 4) if s not in ("", None) else None


def earlier():
    out = []
    for r in csv.DictReader(open(ROOT / "data" / "round1_earlier.csv")):
        prov, open_w, mm = EARLIER_MODELS[r["model"]]
        scores = {}
        for k, *_ in CATEGORIES:
            p1, p5 = num(r[f"{k}_p1"]), num(r[f"{k}_p5"])
            if p1 is None:
                continue
            scores[k] = {"p1": p1, "p5": p5}
            if r.get(f"{k}_p1_human"):
                scores[k]["p1_human"] = num(r[f"{k}_p1_human"])
                scores[k]["p5_human"] = num(r[f"{k}_p5_human"])
        out.append({"name": r["model"], "provider": prov, "open_weights": open_w,
                    "multimodal": mm, "round": "r1", "scores": scores})
    return out


def later(root, subset):
    out = []
    for d, (name, prov, open_w, api) in LATER_MODELS.items():
        scores = {}
        for k, *_ in CATEGORIES:
            f = root / "results" / subset.get(k, k) / d / "summary.json"
            if not f.exists():
                continue
            s = json.load(open(f))
            if "mean_of_5" in s["pass@5"]:  # judged, 0-10 scale; pass@5 = mean of 5 samples (paper convention)
                scores[k] = {"p1": round(s["pass@1"]["mean"] / 10, 4),
                             "p5": round(s["pass@5"]["mean_of_5"] / 10, 4),
                             "p5_best": round(s["pass@5"]["best_of_5"] / 10, 4)}
            else:
                scores[k] = {"p1": round(s["pass@1"]["rate_pct"] / 100, 4),
                             "p5": round(s["pass@5"]["rate_pct"] / 100, 4)}
        out.append({"name": name, "provider": prov, "open_weights": open_w, "multimodal": True,
                    "api_model": api, "round": "r2", "scores": scores})
    return out


def overall(m, key):
    v = [m["scores"][k][key] for k, *_ in CATEGORIES if k in m["scores"]]
    return round(sum(v) / len(v), 4) if v else None


def readme_table(models):
    hdr = ["#", "Model", "Round", "Overall"] + [c[2] for c in CATEGORIES]
    L = ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    for i, m in enumerate(sorted(models, key=lambda m: -m["overall"]["p1"]), 1):
        cells = [str(i), m["name"], "R2" if m["round"] == "r2" else "R1",
                 f"**{m['overall']['p1'] * 100:.1f}**" + ("†" if m["n_categories"] < len(CATEGORIES) else "")]
        for k, *_ in CATEGORIES:
            s = m["scores"].get(k)
            cells.append(f"{s['p1'] * 100:.1f}" if s else "N/A")
        L.append("| " + " | ".join(cells) + " |")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--later-eval", type=Path)
    a = ap.parse_args()
    local = json.load(open(LOCAL)) if LOCAL.exists() else {}
    root = a.later_eval or Path(local["later_eval"])
    models = earlier() + later(root, local.get("subset_dirs", {}))
    for m in models:
        m["overall"] = {"p1": overall(m, "p1"), "p5": overall(m, "p5")}
        m["n_categories"] = len(m["scores"])
    data = {
        "benchmark": "PDAGENT-BENCH",
        "categories": [{"key": k, "name": n, "short": sh, "n": N, "grader": g, "group": grp, "desc": de}
                       for k, n, sh, N, g, grp, de in CATEGORIES],
        "rounds": ROUNDS,
        "models": models,
    }
    js = json.dumps(data, indent=1, ensure_ascii=False)
    (ROOT / "data" / "leaderboard.json").write_text(js + "\n")
    # same data as a script, so index.html also works when opened from disk
    (ROOT / "data" / "leaderboard.js").write_text("window.LEADERBOARD = " + js + ";\n")

    readme = ROOT / "README.md"
    if readme.exists():
        txt = readme.read_text()
        a_, b_ = "<!-- LEADERBOARD:START -->", "<!-- LEADERBOARD:END -->"
        if a_ in txt and b_ in txt:
            pre, rest = txt.split(a_, 1)
            post = rest.split(b_, 1)[1]
            readme.write_text(pre + a_ + "\n" + readme_table(models) + "\n" + b_ + post)
    print(f"wrote data/leaderboard.json ({len(models)} models)")


if __name__ == "__main__":
    main()
