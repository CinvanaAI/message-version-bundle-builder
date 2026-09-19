import pytest
from message_version_bundle import read_levels


@pytest.mark.parametrize('wrapper', [None, 'levels', 'versions'])
def test_duplicate_json_levels_are_rejected_before_replacement(tmp_path, wrapper):
    body='{"1":"first","1":"second",'+','.join('"'+str(i)+'":"text"' for i in range(2,10))+'}'
    if wrapper: body='{"'+wrapper+'":'+body+'}'
    path=tmp_path/'levels.json';path.write_text(body,encoding='utf-8')
    with pytest.raises(ValueError,match='duplicate JSON member'):
        read_levels(path)
