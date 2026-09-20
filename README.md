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

Read the [complete generated bundle](examples/expected/versions.json) alongside the [canonical message](examples/canonical_message.json) and [authored levels](examples/levels.txt). [The recorded run](examples/RESULT.md) gives the command and counts.

## How it works

Strict level parsing and canonical identity checks make the bundle independently verifiable; explicit fill-forward is available when a reviewed semantic floor is reached.

Source: [message_version_bundle/builder.py](message_version_bundle/builder.py), [examples/levels.txt](examples/levels.txt).

## Use it for your work

Replace the two sample input files with your reviewed message and versions. Existing output is refused unless `--force` is explicit; inspect the CLI help for accepted text markers and JSON forms.

## Scope

This tool packages versions; it does not generate summaries or prove semantic equivalence. Missing levels fail by default. `--fill-missing repeat-last` explicitly fills gaps with the preceding text; duplicate or invalid keys always fail.

Owned code is available under the [MIT license](LICENSE.md).

## The format and its meaning

Level `0` is copied exactly from the canonical JSON `message` string. Levels `1`–`9` come from the supplied file; this tool does not assign a meaning or compression ratio to a level. The example deliberately repeats its final text: a shorter lens has reached its authored floor. Character counts measure Python string characters, not tokens, bytes, or semantic fidelity.

Levels may use `--- 1 ---` text markers, a JSON object keyed by `"1"` through `"9"`, or that object under `levels` or `versions`. JSON values are strings or objects containing a string `message`; any supplied `char_count` is recalculated. JSON preserves exact whitespace; marker bodies trim surrounding whitespace. An optional supplied level `0` must equal the canonical string. Ambiguous keys such as `"01"`, unknown keys, duplicate members and non-text messages fail instead of disappearing silently.

The writer stages UTF-8 JSON without a BOM beside the destination, then replaces it. An existing file requires `--force`; that option is a deliberate overwrite, not a merge. The bundler is a [historical workbench extraction](ORIGIN.md); the stricter parser and complete worked output are public continuation work. It can feed a context consumer such as [Agent Chatroom Ledger](https://github.com/CinvanaAI/agent-chatroom-ledger), but has no runtime dependency on that project. Automatic semantic review is an optional future integration, not implemented here.
