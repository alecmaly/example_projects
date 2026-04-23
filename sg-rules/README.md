# sg-rules

Opt-in custom Semgrep rules for the example-projects scan pipeline.

`scan_all.sh` currently invokes `semgrep scan --config auto` and has
`--config ../sg-rules` commented out for speed. To exercise these rules,
uncomment that line in `scan_all.sh`.

One rules file per language, each with a couple of representative
patterns so the `semgrep-to-detector-results.py` stage is actually
producing output the extractor has to consume.
