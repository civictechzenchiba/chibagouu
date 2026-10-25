# -*- coding: utf-8 -*-
"""更新検知の記録（watch-log）の archive_url を、Wayback に既にある保存から埋め戻す。

watch_pages.py は変化を検知したときに Wayback へ保存を頼むが、1 回の検知で頼む数に
上限があり、保存できなかった event には archive_url が付かない。一方で archive.yml が
毎週すべての公式ページを保存しているので、「その event のあと、次の変化より前」に
撮られた capture が Wayback にあれば、それがその版の姿になる。

CDX API で、event の時刻から次の event の時刻までの間にある最初の 200 の capture を探し、
見つかれば archive_url に入れる。見つからなければそのまま（無いものは作れない）。

watch-log の月別ファイルが正本。同じ event が site/data/watch.json と
data/watch-state.json にも残っていれば、そちらにも同じ値を入れる。

使い方:
    python3 scripts/backfill_archive_urls.py --dry-run --limit 20   # 当たり具合を見る
    python3 scripts/backfill_archive_urls.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_config  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "site" / "data" / "watch-log"
PUBLIC = ROOT / "site" / "data" / "watch.json"
STATE = ROOT / "data" / "watch-state.json"
UA = site_config.user_agent("backfill")
CDX = "https://web.archive.org/cdx/search/cdx"
INTERVAL = 1.0


def to_cdx_stamp(iso: str) -> str:
    """JST の ISO 時刻を、CDX が使う UTC の YYYYmmddHHMMSS に直す。"""
    return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")


def first_capture(url: str, start: str, end: str) -> str | None:
    q = urllib.parse.urlencode({
        "url": url, "from": start, "to": end,
        "filter": "statuscode:200", "fl": "timestamp", "limit": "1",
    })
    req = urllib.request.Request(f"{CDX}?{q}", headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf-8", "replace").strip()
            return body.splitlines()[0].strip() if body else None
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) or e.code >= 500:
                time.sleep(30 * (attempt + 1))
                continue
            return None
        except Exception:
            time.sleep(10 * (attempt + 1))
    return None


def dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="探すだけで書き込まない")
    ap.add_argument("--limit", type=int, default=0, help="調べる event の数の上限（0 で全部）")
    args = ap.parse_args()

    logs: dict[Path, list[dict]] = {}
    events: list[dict] = []
    for path in sorted(LOG_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        logs[path] = data
        events.extend(data)

    by_url: dict[str, list[dict]] = {}
    for e in sorted(events, key=lambda e: e.get("at", "")):
        by_url.setdefault(e["url"], []).append(e)

    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    todo = []
    for url, evs in by_url.items():
        for i, e in enumerate(evs):
            if e.get("archive_url"):
                continue
            end = to_cdx_stamp(evs[i + 1]["at"]) if i + 1 < len(evs) else now_stamp
            todo.append((e, to_cdx_stamp(e["at"]), end))
    if args.limit:
        todo = todo[: args.limit]
    print(f"archive_url の無い event {sum(1 for e in events if not e.get('archive_url'))} 件のうち {len(todo)} 件を調べる")

    found: dict[tuple[str, str], str] = {}
    for n, (e, start, end) in enumerate(todo, 1):
        stamp = first_capture(e["url"], start, end)
        if stamp:
            found[(e["at"], e["url"])] = f"https://web.archive.org/web/{stamp}/{e['url']}"
        if n % 50 == 0 or n == len(todo):
            print(f"  {n}/{len(todo)} 調べて {len(found)} 件見つかった", flush=True)
        time.sleep(INTERVAL)

    print(f"見つかった {len(found)} / 調べた {len(todo)}")
    if args.dry_run or not found:
        return 0

    def apply(evs: list[dict]) -> int:
        c = 0
        for e in evs:
            k = (e.get("at"), e.get("url"))
            if k in found and not e.get("archive_url"):
                e["archive_url"] = found[k]
                c += 1
        return c

    for path, data in logs.items():
        c = apply(data)
        if c:
            dump(path, data)
            print(f"{path.relative_to(ROOT)}: {c} 件")
    for path in (PUBLIC, STATE):
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            c = apply(data.get("events") or [])
            if c:
                dump(path, data)
                print(f"{path.relative_to(ROOT)}: {c} 件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
