"""Local-only fraud demo: public examples, validation policies, no file uploads."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'results/phase2/local/mpl-cache'))
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import json
import joblib
import pandas as pd
from analysis import prepare_features

ROOT=Path(__file__).resolve().parent


def score_rows(rows, bundle):
    if not isinstance(rows,list) or not 1 <= len(rows) <= 20 or not all(isinstance(row,dict) for row in rows):
        raise ValueError('Provide a list of one to twenty transaction objects')
    scores=bundle['model'].predict_proba(prepare_features(pd.DataFrame(rows)))[:,1]
    return [{'score':float(score),'flagged':bool(score>=bundle['threshold'])} for score in scores]


def handler(bundle):
    class Handler(BaseHTTPRequestHandler):
        def valid_host(self):
            port=self.server.server_address[1]
            return self.headers.get('Host') in [f'127.0.0.1:{port}',f'localhost:{port}']

        def reply(self,status,content,kind='application/json'):
            if isinstance(content,(dict,list)):
                content=json.dumps(content,allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type',kind)
            self.send_header('Content-Length',str(len(content)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            if not self.valid_host():
                self.reply(403,{'error':'Local host required'})
                return
            routes={'/':('demo/index.html','text/html; charset=utf-8'),
                    '/api/context':('demo/context.json','application/json'),
                    '/reliability.png':('results/phase2/reliability.png','image/png')}
            if self.path not in routes:
                self.reply(404,{'error':'Unknown route'})
                return
            file,kind=routes[self.path]
            self.reply(200,(ROOT/file).read_bytes(),kind)

        def do_POST(self):
            if not self.valid_host():
                self.reply(403,{'error':'Local host required'})
                return
            # Same-origin browser requests only; never accept filesystem paths or serialized models.
            if self.path!='/api/predict':
                self.reply(404,{'error':'Unknown route'})
                return
            if self.headers.get('Origin') not in [None,f'http://{self.headers.get("Host")}']:
                self.reply(403,{'error':'Cross-origin requests are disabled'})
                return
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0 < size <= 25000:
                    raise ValueError('JSON request must be at most 25 KB')
                if self.headers.get_content_type()!='application/json':
                    raise ValueError('Use application/json')
                payload=json.loads(self.rfile.read(size))
                self.reply(200,score_rows(payload,bundle))
            except (ValueError,TypeError,KeyError,OverflowError):
                self.reply(400,{'error':'Invalid transaction input; use the documented V1–V28 and non-negative Amount fields'})

        def log_message(self,*args):
            # The demo does not persist transactions, requests, or visitor data.
            pass
    return Handler


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=0,help='Use an available local port by default')
    args=parser.parse_args()
    bundle=joblib.load(ROOT/'results/phase2/model.joblib')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler(bundle))
    print(f'Fraud demo: http://127.0.0.1:{server.server_address[1]} — press Ctrl+C to stop',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__=='__main__':
    main()
