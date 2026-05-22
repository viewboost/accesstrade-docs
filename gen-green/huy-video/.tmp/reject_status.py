#!/usr/bin/env python3
"""Reject Gen Green contents whose status is not already 'rejected'."""
import json
import ssl
import time
import urllib.request
import urllib.error
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

HERE = Path(__file__).parent
IDS_FILE = HERE / "content_ids.txt"
LOG_FILE = HERE / "reject_status_log.csv"
DONE_FILE = HERE / "reject_processed_ids.txt"   # resume support


def http(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        return resp.status, json.loads(resp.read().decode())


def get_detail(cid):
    _, payload = http("GET", f"{BASE}/contents/{cid}")
    return payload["data"]["data"]


def reject(cid):
    status, _ = http("PATCH", f"{BASE}/contents/{cid}/status",
                      {"status": "rejected", "reason": REASON})
    return status


def main():
    ids = [l.strip() for l in IDS_FILE.read_text().splitlines() if l.strip()]
    done = set()
    if DONE_FILE.exists():
        done = {l.strip() for l in DONE_FILE.read_text().splitlines() if l.strip()}

    new_log = not LOG_FILE.exists()
    log = LOG_FILE.open("a", encoding="utf-8")
    done_f = DONE_FILE.open("a", encoding="utf-8")
    if new_log:
        log.write("id,action,old_status,note\n")

    total = len(ids)
    stats = {"rejected": 0, "skipped": 0, "error": 0}

    for i, cid in enumerate(ids, 1):
        if cid in done:
            continue
        try:
            detail = get_detail(cid)
            old_status = detail.get("status", "")

            if old_status == "rejected":
                stats["skipped"] += 1
                log.write(f'{cid},skip,{old_status},"already rejected"\n')
            else:
                code = reject(cid)
                stats["rejected"] += 1
                log.write(f'{cid},reject,{old_status},"http {code}"\n')
            done_f.write(cid + "\n")
        except urllib.error.HTTPError as e:
            stats["error"] += 1
            log.write(f'{cid},error,,"HTTP {e.code} {e.reason}"\n')
        except Exception as e:
            stats["error"] += 1
            log.write(f'{cid},error,,"{type(e).__name__}: {e}"\n')

        log.flush()
        done_f.flush()
        if i % 50 == 0:
            print(f"[{i}/{total}] rejected={stats['rejected']} "
                  f"skipped={stats['skipped']} error={stats['error']}", flush=True)
        time.sleep(0.15)

    log.close()
    done_f.close()
    print(f"DONE: total={total} rejected={stats['rejected']} "
          f"skipped={stats['skipped']} error={stats['error']}", flush=True)


if __name__ == "__main__":
    main()
