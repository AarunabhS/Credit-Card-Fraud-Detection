"""Restore the documented public input, verifying both upstream and converted hashes."""
from __future__ import annotations
import hashlib
import io
import re
import urllib.request
import zipfile
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch():
    target = ROOT / "data" / TARGET
    if target.exists():
        if sha256(target.read_bytes()) != TARGET_SHA256:
            raise ValueError("Existing input differs from the documented sample. It was left untouched; use --data with analysis.py for custom inputs.")
        print(f"Verified existing input: {target.relative_to(ROOT)}")
        return
    request = urllib.request.Request(URL, headers={"User-Agent": "portfolio-reproducibility/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read()
    if sha256(content) != SOURCE_SHA256:
        raise ValueError("Upstream checksum mismatch; no input file was written. Review the publisher's version before updating the expected hash.")
    converted = convert(content)
    if sha256(converted) != TARGET_SHA256:
        raise ValueError("Converted checksum differs; no input file was written. Use the tested requirements.txt versions.")
    target.parent.mkdir(parents=True, exist_ok=True)
    # Never replace an existing file, even if it appeared during the download.
    with target.open("xb") as stream:
        stream.write(converted)
    print(f"Downloaded and verified: {target.relative_to(ROOT)}")


TARGET = 'transactions_full.csv'
URL = 'https://storage.googleapis.com/download.tensorflow.org/data/creditcard.csv'
SOURCE_SHA256 = '76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89'
TARGET_SHA256 = '61171795e96ec102e4876a6809da8181dffd6d0d80a3fcce14d86a75643698e5'

def convert(content):
    frame=pd.read_csv(io.BytesIO(content))
    if frame.shape!=(284807,31) or int(frame.Class.sum())!=492:
        raise ValueError('Unexpected full fraud dataset schema')
    return frame.to_csv(index=False).encode('utf-8')

if __name__ == "__main__":
    try:
        fetch()
    except (ValueError, OSError) as error:
        raise SystemExit(f"Download error: {error}")
