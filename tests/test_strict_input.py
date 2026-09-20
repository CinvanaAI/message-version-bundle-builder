import pytest
from message_version_bundle.builder import build_versions, normalize_levels, read_message


@pytest.mark.parametrize("key", ["01", "10", "-1", "typo", "١"])
def test_invalid_level_is_never_silently_discarded(key):
    with pytest.raises(ValueError, match="invalid level key"):
        build_versions("canonical", {key: "text"}, "repeat-last")


@pytest.mark.parametrize("value", [None, 23, [], {}, {"message": None}])
def test_non_text_level_is_rejected(value):
    with pytest.raises(ValueError):
        normalize_levels({"1": value})


def test_canonical_null_is_not_coerced_to_empty(tmp_path):
    path = tmp_path / "canonical.json"
    path.write_text('{"message": null}', encoding="utf-8")
    with pytest.raises(ValueError, match="must be a string"):
        read_message(path)


def test_invalid_fill_policy_fails_even_when_complete():
    with pytest.raises(ValueError, match="fill_missing"):
        build_versions("canonical", {str(i): "text" for i in range(1,10)}, "guess")
