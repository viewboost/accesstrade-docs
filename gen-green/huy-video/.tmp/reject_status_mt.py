#!/usr/bin/env python3
"""Reject Gen Green contents (multi-threaded) whose status is not 'rejected'.

Shares resume files with reject_status.py:
  reject_processed_ids.txt / reject_status_log.csv
"""
import json
import ssl
import sys
import threading
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

BASE = "https://vcreator-admin-api.koc.com.vn"
REASON = ("Video của bạn không đạt tỷ lệ bình luận tối thiểu và tỷ lệ tương tác "
          "tối thiểu theo quy định. BTC sẽ không đồng ý kháng cáo với video này.")
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NjE4NDA4NTcyZDExZDQyZDc1MzFlZDEiLCJlbWFpbCI6ImRpZW1uZ3V5ZW4yQGludGVyc3BhY2Uudm4iLCJleHAiOjE3NzkyMTAxNjAsImlzUm9vdCI6dHJ1ZSwibmFtZSI6IkRp4buFbSIsInBhcnRuZXIiOiIwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAiLCJwaG9uZSI6IiJ9.MJgQxeRLFWHM-yGXIR-WcH9X4FT85vzU8m_6H1-F4DI"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Referer": "https://admin.gen-green.global/",
    "Origin": "https://admin.gen-green.global",
    "Accept-Language": "vi",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
}

WORKERS = 10
MAX_RETRY = 3          # retry transient errors (502/timeout) within a run
RETRY_BACKOFF = 2.0    # seconds, multiplied per attempt

HERE = Path(__file__).parent
IDS_FILE = HERE / "content_ids.txt"
LOG_FILE = HERE / "reject_status_log.csv"
DONE_FILE = HERE / "reject_processed_ids.txt"

_lock = threading.Lock()
_counter = {"n": 0, "rejected": 0, "skipped": 0, "error": 0}


def http(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        return resp.status, json.loads(resp.read().decode())


def is_transient(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in (429, 500, 502, 503, 504)
    return True  # timeouts, conn reset, etc.


def with_retry(fn):
    last = None
    for attempt in range(1, MAX_RETRY + 1):
        try:
            return fn()
        except Exception as e:
            last = e
            if attempt < MAX_RETRY and is_transient(e):
                time.sleep(RETRY_BACKOFF * attempt)
                continue
            raise
    raise last


def get_status(cid):
    _, payload = with_retry(lambda: http("GET", f"{BASE}/contents/{cid}"))
    return payload["data"]["data"].get("status", "")


def reject(cid):
    status, _ = with_retry(lambda: http(
        "PATCH", f"{BASE}/contents/{cid}/status",
        {"status": "rejected", "reason": REASON}))
    return status


def csv_field(s):
    return '"' + str(s).replace('"', '""') + '"'


def worker(cid, total, log_f, done_f):
    try:
        old_status = get_status(cid)
        if old_status == "rejected":
            row = f'{cid},skip,{old_status},"already rejected"\n'
            kind = "skipped"
        else:
            code = reject(cid)
            row = f'{cid},reject,{old_status},"http {code}"\n'
            kind = "rejected"
        with _lock:
            log_f.write(row)
            done_f.write(cid + "\n")
            log_f.flush()
            done_f.flush()
            _counter[kind] += 1
    except urllib.error.HTTPError as e:
        with _lock:
            log_f.write(f'{cid},error,,{csv_field(f"HTTP {e.code} {e.reason}")}\n')
            log_f.flush()
            _counter["error"] += 1
    except Exception as e:
        with _lock:
            log_f.write(f'{cid},error,,{csv_field(f"{type(e).__name__}: {e}")}\n')
            log_f.flush()
            _counter["error"] += 1
    finally:
        with _lock:
            _counter["n"] += 1
            n = _counter["n"]
        if n % 100 == 0:
            print(f"[{n}/{total}] rejected={_counter['rejected']} "
                  f"skipped={_counter['skipped']} error={_counter['error']}",
                  flush=True)


def main():
    all_ids = [l.strip() for l in IDS_FILE.read_text().splitlines() if l.strip()]
    done = set()
    if DONE_FILE.exists():
        done = {l.strip() for l in DONE_FILE.read_text().splitlines() if l.strip()}
    todo = [c for c in all_ids if c not in done]
    total = len(todo)
    print(f"all={len(all_ids)} done={len(done)} todo={total} workers={WORKERS}",
          flush=True)
    if not total:
        print("nothing to do")
        return

    new_log = not LOG_FILE.exists()
    log_f = LOG_FILE.open("a", encoding="utf-8")
    done_f = DONE_FILE.open("a", encoding="utf-8")
    if new_log:
        log_f.write("id,action,old_status,note\n")

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for cid in todo:
            ex.submit(worker, cid, total, log_f, done_f)

    log_f.close()
    done_f.close()
    print(f"DONE: todo={total} rejected={_counter['rejected']} "
          f"skipped={_counter['skipped']} error={_counter['error']}", flush=True)


if __name__ == "__main__":
    main()
