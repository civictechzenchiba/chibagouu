# -*- coding: utf-8 -*-
"""更新検知の記録（site/data/watch-log）を、あとから読める要約にまとめる。

- 出力: site/data/archive-summary.json
- 何市町村の公式ページを、いつからいつまで、何回の変化として記録したかを残す。
- 更新を止めるときに1回動かす想定。途中で動かしても害はない。
  手動: python scripts/build_archive_summary.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "site" / "data" / "watch-log"
CSV_PATH = ROOT / "data" / "supports.csv"
OUT = ROOT / "site" / "data" / "archive-summary.json"
JST = timezone(timedelta(hours=9))


def main() -> int:
    events: list[dict] = []
    for path in sorted(LOG_DIR.glob("*.json")):
        events.extend(json.loads(path.read_text(encoding="utf-8")))
    if not events:
        print("watch-log が空です")
        return 0

    events.sort(key=lambda e: e.get("at", ""))
    by_muni = Counter(e.get("name") or e.get("slug", "") for e in events)
    by_kind = Counter(e.get("kind", "") for e in events)
    by_day = Counter((e.get("at") or "")[:10] for e in events)
    urls = {e.get("url") for e in events if e.get("url")}
    with_archive = sum(1 for e in events if e.get("archive_url"))

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    watched = [r for r in rows if (r.get("url") or "").startswith("http")]
    by_status = Counter((r.get("status") or "unknown").strip() or "unknown" for r in watched)

    summary = {
        "generated_at": datetime.now(JST).isoformat(timespec="seconds"),
        "note": (
            "令和8年8月千葉豪雨で、千葉県内の市町村・県・国の公式ページの本文が変わったことを"
            "数時間おきに自動で見た記録の要約。検知した時刻であり、実際の更新はそれより前のことがある。"
        ),
        "period": {"first": events[0].get("at", ""), "last": events[-1].get("at", "")},
        "events_total": len(events),
        "events_with_archive_url": with_archive,
        "pages_changed": len(urls),
        "pages_watched": len(watched),
        "municipalities": len(by_muni),
        "by_municipality": by_muni.most_common(),
        "by_kind": by_kind.most_common(),
        "by_day": sorted(by_day.items()),
        "supports_by_status": by_status.most_common(),
    }
    OUT.write_text(json.dumps(summary, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  期間 {summary['period']['first'][:16]} 〜 {summary['period']['last'][:16]}")
    print(f"  検知 {summary['events_total']} 件（Wayback の保存先あり {with_archive} 件） / "
          f"変化のあったページ {summary['pages_changed']} / "
          f"監視 {summary['pages_watched']} / {summary['municipalities']} 市町村等")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
