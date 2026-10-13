# PDAGENT-BENCH Leaderboard

**PDAGENT-BENCH** measures how well large language models handle VLSI **physical design** (backend) work. It has 343 tasks in eight categories: foundational knowledge, root-cause analysis and tool-report reading, through to writing exact place-and-route, formal-verification and ECO commands.

**Interactive leaderboard: https://fenggev56.github.io/PDAGENT-BENCH/**  ·  **Paper: [arXiv:2606.17253](https://arxiv.org/abs/2606.17253)**  ·  **Open-source version: [Hugging Face](https://huggingface.co/datasets/fenggev566/PDAgent-Bench_open)**

[![PDAGENT-BENCH leaderboard](assets/leaderboard.png)](https://fenggev56.github.io/PDAGENT-BENCH/)

## Leaderboard (pass@1, %)

Overall is the unweighted mean of the category scores. † = text-only model, averaged over the 6 categories that need no image input.

<!-- LEADERBOARD:START -->
| # | Model | Round | Overall | Foundational | Root-Cause | Report | STA | FM | ECO | P&R Vendor 1 | P&R Vendor 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GPT-5.5 | R1 | **65.1** | 80.4 | 73.3 | 74.6 | 72.7 | 81.8 | 50.0 | 45.5 | 42.2 |
| 2 | GPT-5.6 Sol | R2 | **63.4** | 85.7 | 65.7 | 68.2 | 72.7 | 81.8 | 40.0 | 52.3 | 41.1 |
| 3 | Claude Opus 5 | R2 | **60.5** | 90.0 | 74.8 | 53.6 | 63.6 | 81.8 | 40.0 | 39.8 | 40.0 |
| 4 | Claude Opus 4.7 | R1 | **59.9** | 82.4 | 76.2 | 64.1 | 72.7 | 72.7 | 40.0 | 34.1 | 36.7 |
| 5 | DeepSeek-V4.1-Flash | R2 | **57.6** | 84.8 | 66.9 | 50.4 | 72.7 | 77.3 | 40.0 | 36.4 | 32.2 |
| 6 | Claude Sonnet 4.6 | R1 | **57.3** | 82.6 | 68.8 | 66.8 | 63.6 | 63.6 | 50.0 | 34.1 | 28.9 |
| 7 | GPT-5.6 Luna | R2 | **55.3** | 84.8 | 57.6 | 60.0 | 45.5 | 59.1 | 60.0 | 38.6 | 36.7 |
| 8 | Claude Sonnet 5 | R2 | **51.5** | 82.9 | 57.4 | 62.3 | 54.5 | 54.5 | 40.0 | 27.3 | 33.3 |
| 9 | GPT-5.4-mini | R1 | **50.2** | 72.3 | 54.5 | 46.1 | 63.6 | 59.1 | 50.0 | 29.5 | 26.7 |
| 10 | GPT-5.1 | R1 | **50.2** | 82.0 | 65.5 | 65.5 | 54.5 | 54.5 | 20.0 | 31.8 | 27.8 |
| 11 | DeepSeek-Reasoner | R1 | **42.5**† | 73.7 | 61.2 | N/A | N/A | 45.5 | 30.0 | 21.6 | 23.3 |
| 12 | DeepSeek-Chat | R1 | **41.9**† | 72.6 | 48.6 | N/A | N/A | 40.9 | 30.0 | 34.0 | 25.6 |
| 13 | GPT-5-mini | R1 | **41.0** | 80.0 | 56.0 | 65.5 | 54.5 | 22.7 | 30.0 | 5.7 | 13.3 |
| 14 | Qwen-VL-30B | R1 | **31.4** | 69.2 | 37.9 | 32.3 | 54.5 | 27.3 | 10.0 | 9.1 | 11.1 |
| 15 | Qwen-VL-8B | R1 | **27.7** | 53.3 | 24.5 | 32.7 | 54.5 | 27.3 | 10.0 | 6.8 | 12.2 |
| 16 | Qwen3-8B | R1 | **21.2**† | 54.3 | 25.5 | N/A | N/A | 27.3 | 0.0 | 8.0 | 12.2 |
<!-- LEADERBOARD:END -->

**R2** = latest evaluation (2026-09-23). **R1** = earlier evaluation reported in the paper. Rule-checked categories (STA, FM, ECO, P&R Vendor 1, P&R Vendor 2) use identical checkers in both rounds. The three judged categories (Foundational, Root-Cause, Report) were scored by different judges in the two rounds, so compare those columns within a round only.

## PlaceReasoner-Bench: end-to-end macro placement

16 tasks: 8 open-source designs (ariane133, ariane81, bp_be, bp_fe, ethernet, swerv_wrapper, VeriGPU, vga_lcd), each at a square (1:1) and an elongated (2:1) die. A method outputs every macro's position and orientation; the full open flow (Yosys, OpenROAD, Nangate45, FakeRAM 2.0) then places, routes and signs off the design, and it is scored on post-route PPA. Our agent **PlaceReasoner-Beta** runs on **Claude Opus 4.8**; the same agent on open-weight Qwen3-VL backbones is shown for comparison.

<!-- PLACEREASONER:START -->
| Method | Type | Routed (< 1,000 DRC) | DRC-clean | Best TNS |
|---|---|---|---|---|
| **PlaceReasoner-Beta (Claude Opus 4.8)** | LLM agent | 16/16 | 13/16 | 11/16 |
| PlaceReasoner-Beta (Qwen3-VL-30B) | LLM agent | 13/16 | 10/16 | 3/16 |
| RTL-MP | classical | 15/16 | 10/16 | 1/16 |
| ChiPFormer | classical | 14/16 | 12/16 | 1/16 |
| PlaceReasoner-Beta (Qwen3-VL-8B) | LLM agent | 14/16 | 12/16 | 0/16 |
| SA | classical | 1/16 | 1/16 | 0/16 |
| DREAMPlace | classical | 0/16 | 0/16 | 0/16 |
<!-- PLACEREASONER:END -->

A run counts as routed when detailed routing completes with fewer than 1,000 DRC violations. Best TNS = best post-route total negative slack on the task among routed runs. Per-task WNS, TNS, DRC, wirelength, power, area, runtime and tokens (paper Tables 6 and 7, without the CWI / CWS ablations) are in [`data/placereasoner_bench.csv`](data/placereasoner_bench.csv) and on the [interactive page](https://fenggev56.github.io/PDAGENT-BENCH/#placereasoner).

![Macro placements produced by PlaceReasoner-Beta](assets/placereasoner_fig9.png)

*Macro placements produced by PlaceReasoner-Beta (Claude Opus 4.8) on 15 PlaceReasoner-Bench tasks, with each macro's pin side marked: (a)–(h) the eight designs at 1:1 and (i)–(o) seven of them at 2:1. Macros are grouped against the periphery, and each group's pin side faces the standard-cell region it serves.*

## Open-source version

[**PDAgent-Bench_open**](https://huggingface.co/datasets/fenggev566/PDAgent-Bench_open) on Hugging Face is the open release of the benchmark. It runs on open tools only (Yosys, OpenROAD, Nangate45, FakeRAM 2.0) and contains:

- 133 QA tasks: Foundational Knowledge (90), Root-Cause Analysis (21), Report Comprehension (11) and Static Timing Analysis (11)
- PlaceReasoner-Bench: the 16 end-to-end macro-placement tasks above, with netlists, SDC, LEF, LIB, DEF and cluster files

## Categories

| Category | Group | Tasks | Grading | What it tests |
|---|---|---|---|---|
| Foundational Knowledge | Understanding | 90 | LLM judge (0–10 rubric) | Floorplanning, CTS, STA, DFT, extraction, device physics, flow inputs/outputs |
| Root-Cause Analysis | Understanding | 21 | LLM judge (0–10 rubric) | Diagnosing real backend failures (hold, IR drop, congestion, SDC, multi-voltage) and proposing fixes |
| Report Comprehension | Understanding | 11 | LLM judge (0–10 rubric) | Reading P&R and timing sign-off tool reports and screenshots (multimodal) |
| Static Timing Analysis | Understanding | 11 | Rule checker | Timing calculations and multiple-choice STA, some from circuit diagrams (multimodal) |
| Formal Verification | Script Generation | 22 | Rule checker | Exact Formality commands |
| ECO | Script Generation | 10 | Rule checker | PrimeTime ECO commands |
| P&R Vendor 1 | Script Generation | 88 | Rule checker | Exact Tcl for a commercial place-and-route tool across the full flow |
| P&R Vendor 2 | Script Generation | 90 | Rule checker | Exact Tcl for a second commercial place-and-route tool across the full flow |

## Protocol

- Plain base-model API calls: no tools, retrieval or agent loop, and one stateless turn per task.
- **pass@1**: one sample. **pass@5**: five separate samples. For rule-checked tasks a task counts as passed if any sample is correct; for judged tasks the score is the mean over the 5 samples.
- Latest round (R2): reasoning effort *medium*, no temperature, 32K output-token cap, and a blind GPT-5.4-mini judge (model identity scrubbed, jobs shuffled across candidates).
- STA, ECO and Report have only 10–11 tasks, so one task moves the score by about 9–10 points.

## Repository layout

```
index.html                 the leaderboard site (static, served by GitHub Pages)
data/leaderboard.json      all scores (pass@1 / pass@5 per model per category)
data/leaderboard.js        same data, loaded by index.html
data/round1_earlier.csv    earlier-round scores, as reported in the paper
data/placereasoner_bench.csv  PlaceReasoner-Bench per-task post-route results
data/placereasoner.json    the same, with per-method summary (also .js for the page)
scripts/build_data.py      rebuilds data/ and the table above from evaluation outputs
```

## Adding a model

1. Run the evaluation harness for the new model. It writes `results/<subset>/<model>/summary.json`. The eval path and subset folder names go in `scripts/local_config.json` (not tracked).
2. Add the model to `LATER_MODELS` in `scripts/build_data.py`.
3. Run `python3 scripts/build_data.py`. This regenerates `data/` and the README table.
4. Commit and push. GitHub Pages redeploys automatically.

## Citation

```bibtex
@article{li2026pdagentbench,
  title   = {PDAGENT-BENCH: Characterizing, Grounding, and Architecting LLM/VLM Agents for VLSI Physical Design},
  author  = {Li, Qiufeng and Chen, Rongqian and Cheng, Quan and Wang, Chengxuan and Tang, Sizhe and Ho, Chia-Tung and Pan, David Z. and Lan, Tian and Cao, Weidong},
  journal = {arXiv preprint arXiv:2606.17253},
  year    = {2026}
}
```
