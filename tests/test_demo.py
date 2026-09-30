from contextlib import contextmanager
from http.server import ThreadingHTTPServer
import json
import threading
import urllib.request
import urllib.error
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier
from demo import handler, score_rows
from analysis import FEATURES


@contextmanager
def server():
    model=DummyClassifier(strategy='prior').fit(pd.DataFrame({name:[0,1] for name in FEATURES}),[0,1])
    http=ThreadingHTTPServer(('127.0.0.1',0),handler({'model':model,'threshold':.5}))
    thread=threading.Thread(target=http.serve_forever,daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{http.server_address[1]}'
    finally:
        http.shutdown()
        http.server_close()
        thread.join()


def test_demo_disallows_arbitrary_file_routes_and_foreign_origin():
    with server() as url:
        for suffix in ['/../analysis.py','/data/transactions_full.csv']:
            with pytest.raises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(url+suffix)
            assert error.value.code==404
        request=urllib.request.Request(url+'/api/predict',data=b'[]',headers={'Content-Type':'application/json','Origin':'https://example.com'})
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        assert error.value.code==403


def test_demo_rejects_bad_schema_and_large_payload():
    with server() as url:
        for data in [b'[{"path":"/etc/passwd"}]',b' '*25001]:
            request=urllib.request.Request(url+'/api/predict',data=data,headers={'Content-Type':'application/json'})
            with pytest.raises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            assert error.value.code==400


def test_demo_scores_numeric_rows_without_uploading_a_file():
    with server() as url:
        request=urllib.request.Request(url+'/api/predict',data=json.dumps([{name:0 for name in FEATURES}]).encode(),headers={'Content-Type':'application/json'})
        result=json.loads(urllib.request.urlopen(request).read())
        assert result==[{'score':.5,'flagged':True}]
