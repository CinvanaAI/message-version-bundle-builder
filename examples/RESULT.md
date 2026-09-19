# Recorded first use

This output was produced by the included example with network connections disabled. Synthetic provider or worker replies are identified by the example; no real model quality or billing is implied.

From the installed checkout:

```sh
python -m message_version_bundle.cli --message-file examples/canonical_message.json --levels-file examples/levels.txt --output output/versions.json
```

[Complete recorded output](result.json)

```text
{
  "output": "output\\versions.json",
  "level_count": 10,
  "level_0_char_count": 100,
  "counts": {
    "0": 100,
    "1": 56,
    "2": 37,
    "3": 18,
    "4": 13,
    "5": 13,
    "6": 14,
    "7": 5,
    "8": 8,
    "9": 8
  },
  "bom": false
}
```

Generated timestamps and synthetic identifiers can change between runs. The demonstrated behavior and input fixture remain inspectable in the adjacent example files.
