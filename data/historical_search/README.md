# Historical search artifacts

These files are preserved verbatim from the original ChatGPT response:

- `high_precision_base.py`: original high-precision constructor with its broken
  `/mnt/data/...` import preserved for provenance.
- `layer1_vertices.json`: 78 first-layer summaries; its `path` fields point to
  temporary `/mnt/data/.../*.npz` files that were never attached.
- `classify_final.txt`: historical classification output.
- `multi_trace.log`: 312 completed second-layer transitions (`4×78`).
- `trace_graph_direct.py`: original continuation program with its broken
  `/mnt/data/...` import preserved for provenance.
- `layer3_trace.log`: the final attachment contains all 468 planned third-layer
  transitions, although the prose was written when 264 had completed.

Together with `data/exact/strict_high_precision.csv` and
`data/exact/high_precision_report.json`, these are the eight strict-result
attachments from the final response. The certificate and report live under
`data/exact/` because they are primary results rather than historical logs.

They are evidence about the historical run, not inputs to the new search.
`scripts/contact_graph.py`, `scripts/trace_graph.py`, and
`scripts/run_search.py` reconstruct the missing geometry module and regenerate
new seeds under `results/search_reproduction/`. The published reconstruction
includes the root, all 78 first-layer seeds and traces, and their summary.

The phrase “390 additional second-level transitions” in the preserved model
output is not supported literally by `multi_trace.log`. The consistent count is
78 first-layer traces plus 312 second-layer traces, or 390 cumulatively.
