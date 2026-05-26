#!/usr/bin/env python3
"""Append warningTag 6a0c25d17c5842dcc6ff5a6c to Gen Green content list."""
import json
import ssl
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

BASE = "https://vcreator-admin-api.koc.com.vn"
NEW_TAG = "6a0c25d17c5842dcc6ff5a6c"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NjE4NDA4NTcyZDExZDQyZDc1MzFlZDEiLCJlbWFpbCI6ImRpZW1uZ3V5ZW4yQGludGVyc3BhY2Uudm4iLCJleHAiOjE3NzkyMTAxNjAsImlzUm9vdCI6dHJ1ZSwibmFtZSI6IkRp4buFbSIsInBhcnRuZXIiOiIwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAiLCJwaG9uZSI6IiJ9.MJgQxeRLFWHM-yGXIR-WcH9X4FT85vzU8m_6H1-F4DI"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Referer": "https://admin.gen-green.global/",
    "Accept-Language": "vi",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
}

HERE = Path(__file__).parent
IDS_FILE = HERE / "content_ids.txt"
LOG_FILE = HERE / "append_tag_log.csv"
DONE_FILE = HERE / "processed_ids.txt"   # resume support


def http(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        return resp.status, json.loads(resp.read().decode())


def get_detail(cid):
    _, payload = http("GET", f"{BASE}/contents/{cid}")
    return payload["data"]["data"]


def patch_tags(cid, tags):
    status, _ = http("PATCH", f"{BASE}/contents/tag",
                      {"contentIds": [cid], "warningTags": tags})
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
        log.write("id,action,status,old_tags,new_tags,note\n")

    total = len(ids)
    stats = {"patched": 0, "skipped": 0, "error": 0}

    for i, cid in enumerate(ids, 1):
        if cid in done:
            continue
        try:
            detail = get_detail(cid)
            old_tags = detail.get("warningTags") or []
            old_ids = [t.get("_id", t) if isinstance(t, dict) else t for t in old_tags]
            content_status = detail.get("status", "")

            if NEW_TAG in old_ids:
                stats["skipped"] += 1
                log.write(f'{cid},skip,{content_status},"{";".join(map(str,old_ids))}",,"tag already present"\n')
            else:
                new_tags = old_ids + [NEW_TAG]
                code = patch_tags(cid, new_tags)
                stats["patched"] += 1
                log.write(f'{cid},patch,{content_status},"{";".join(map(str,old_ids))}","{";".join(map(str,new_tags))}","http {code}"\n')
            done_f.write(cid + "\n")
        except urllib.error.HTTPError as e:
            stats["error"] += 1
            log.write(f'{cid},error,,,,"HTTP {e.code} {e.reason}"\n')
        except Exception as e:
            stats["error"] += 1
            log.write(f'{cid},error,,,,"{type(e).__name__}: {e}"\n')

        log.flush()
        done_f.flush()
        if i % 50 == 0:
            print(f"[{i}/{total}] patched={stats['patched']} skipped={stats['skipped']} error={stats['error']}",
                  flush=True)
        time.sleep(0.15)

    log.close()
    done_f.close()
    print(f"DONE: total={total} patched={stats['patched']} "
          f"skipped={stats['skipped']} error={stats['error']}", flush=True)


if __name__ == "__main__":
    main()
