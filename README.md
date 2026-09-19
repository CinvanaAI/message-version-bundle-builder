# Message Version Bundle Builder

Package a canonical message and nine reviewed context versions into a strict, verifiable bundle.

## Try it

Python 3.11+. Run from this checkout:

```sh
python -m pip install -e .
message-version-bundle-builder --message-file examples/canonical_message.json --levels-file examples/levels.txt --output output/versions.json
```

**Input:** One canonical message and nine explicitly authored context versions.

**Result:** One JSON bundle contains levels 0–9 and freshly calculated character counts. Level 0 is required to match the canonical message exactly.

See [the captured example](examples/RESULT.md) for the observed output and reproduction command.

## How it works

Strict level parsing and canonical identity checks make the bundle independently verifiable; explicit fill-forward is available when a reviewed semantic floor is reached.

Source: [message_version_bundle/builder.py](message_version_bundle/builder.py), [examples/levels.txt](examples/levels.txt).

## Use it for your work

Replace the two sample input files with your reviewed message and versions. Existing output is refused unless `--force` is explicit; inspect the CLI help for accepted text markers and JSON forms.

## Scope

This tool packages versions; it does not generate summaries or prove semantic equivalence. Missing/duplicate levels fail unless the documented repeat-last policy is chosen.

Owned code is available under the [MIT license](LICENSE.md).
