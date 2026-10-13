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


# ---------------------------------------------------------------- PlaceReasoner-Bench (end-to-end) ----
# data/placereasoner_bench.csv: paper Tables 6 (1:1) and 7 (2:1), ablation rows (CWI, CWS) removed.
PR_METHODS = [
    # csv name, display name, kind, backbone
    ("PlaceReasoner-Beta", "PlaceReasoner-Beta", "agent", "Claude Opus 4.8"),
    ("Qwen3-VL-30B", "PlaceReasoner-Beta", "agent", "Qwen3-VL-30B"),
    ("Qwen3-VL-8B", "PlaceReasoner-Beta", "agent", "Qwen3-VL-8B"),
    ("RTL-MP", "RTL-MP", "classical", None),
    ("ChiPFormer", "ChiPFormer", "classical", None),
    ("DREAMPlace", "DREAMPlace", "classical", None),
    ("SA", "SA", "classical", None),
]
DRC_BUDGET = 1000  # runs with >= this many DRC violations are not comparable (paper convention)


def placereasoner():
    rows = []
    for r in csv.DictReader(open(ROOT / "data" / "placereasoner_bench.csv")):
        out = {"aspect": r["aspect"], "design": r["design"], "method": r["method"], "status": r["status"]}
        for k in ("wns", "tns", "power_w", "runtime_s", "tokens_k"):
            out[k] = float(r[k]) if r[k] else None
        for k in ("drc", "wl_um", "area_um2"):
            out[k] = int(r[k]) if r[k] else None
        out["valid"] = out["status"] == "routed" and out["tns"] is not None and out["drc"] is not None and out["drc"] < DRC_BUDGET
        rows.append(out)
    summary = {m: {"routed": 0, "clean": 0, "best_tns": 0} for m, *_ in PR_METHODS}
    for key in {(r["aspect"], r["design"]) for r in rows}:
        task = [r for r in rows if (r["aspect"], r["design"]) == key]
        valid = [r for r in task if r["valid"]]
        best = max((r["tns"] for r in valid), default=None)
        for r in task:
            r["best_tns"] = r["valid"] and r["tns"] == best
            r["best_wns"] = r["valid"] and r["wns"] == max(x["wns"] for x in valid)
            summary[r["method"]]["routed"] += r["valid"]
            summary[r["method"]]["clean"] += r["valid"] and r["drc"] == 0
            summary[r["method"]]["best_tns"] += r["best_tns"]
    return {
        "benchmark": "PlaceReasoner-Bench",
        "tasks": len({(r["aspect"], r["design"]) for r in rows}),
        "designs": sorted({r["design"] for r in rows}, key=str.lower),
        "drc_budget": DRC_BUDGET,
        "methods": [{"key": k, "name": n, "kind": kd, "backbone": b, **summary[k]} for k, n, kd, b in PR_METHODS],
        "rows": rows,
    }


def readme_pr_table(pr):
    T = pr["tasks"]
    ms = sorted(pr["methods"], key=lambda m: (-m["best_tns"], -m["routed"], -m["clean"]))
    L = [f"| Method | Type | Routed (< {pr['drc_budget']:,} DRC) | DRC-clean | Best TNS |", "|---|---|---|---|---|"]
    for m in ms:
        name = f"{m['name']} ({m['backbone']})" if m["backbone"] else m["name"]
        if m["key"] == "PlaceReasoner-Beta":
            name = f"**{name}**"
        L.append(f"| {name} | {'LLM agent' if m['kind'] == 'agent' else 'classical'} | {m['routed']}/{T} | {m['clean']}/{T} | {m['best_tns']}/{T} |")
    return "\n".join(L)


def fill(txt, tag, body):
    a, b = f"<!-- {tag}:START -->", f"<!-- {tag}:END -->"
    if a not in txt or b not in txt:
        return txt
    pre, rest = txt.split(a, 1)
    return pre + a + "\n" + body + "\n" + b + rest.split(b, 1)[1]


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

    prd = placereasoner()
    pr = json.dumps(prd, indent=1, ensure_ascii=False)
    (ROOT / "data" / "placereasoner.json").write_text(pr + "\n")
    (ROOT / "data" / "placereasoner.js").write_text("window.PLACEREASONER = " + pr + ";\n")

    readme = ROOT / "README.md"
    if readme.exists():
        txt = fill(readme.read_text(), "LEADERBOARD", readme_table(models))
        readme.write_text(fill(txt, "PLACEREASONER", readme_pr_table(prd)))
    print(f"wrote data/leaderboard.json ({len(models)} models)")


if __name__ == "__main__":
    main()
