import pytest
import fetch_full_data


def test_full_downloader_preserves_a_different_local_file(tmp_path,monkeypatch):
    monkeypatch.setattr(fetch_full_data,'ROOT',tmp_path)
    path=tmp_path/'data/transactions_full.csv'
    path.parent.mkdir()
    path.write_bytes(b'preserve my original data')
    with pytest.raises(ValueError,match='left untouched'):
        fetch_full_data.fetch()
    assert path.read_bytes()==b'preserve my original data'
