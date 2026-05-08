# sg-rules

Opt-in custom Semgrep rules for the example-projects scan pipeline.

`scan_all.sh` invokes `semgrep scan --config /app/sg-rules --config auto`
(the bundled local rule pack inside the Docker image, plus registry
auto-detect). To exercise these example-project rules instead, swap
`/app/sg-rules` for the path to this directory.

One rules file per language, each with a couple of representative
patterns so the `detectors_to_results.py -s semgrep` converter stage
is actually producing output the VS Code extension has to consume.
