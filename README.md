# 令和8年8月千葉豪雨 — CTZC 復興支援ポータル（要件）

CivicTechZenChiba（CTZC）として、令和8年8月千葉豪雨の復興・災害対策のために検討しているポータルサイトの**要件定義**と、GitHub Pages 上の簡易公開サイトです。

**公開サイト:** https://civictechzenchiba.github.io/chibagouu/

検証・添削・協働編集を歓迎します。Issue や Pull Request で指摘してください。

## 更新を止めました（2026-10-25）

発災（2026-08-13）から 2 か月半がたち、公式ページの変化も落ち着いたので、2026-10-25 を最終更新日として自動処理を止めました。
全ページの先頭に「このサイトの更新は終了しました」の帯が出ます。公式ページへのリンクは切れていくことがあります。

残っているもの：

| もの | 場所 |
|---|---|
| サイト本体（帯つき） | GitHub Pages |
| 公式ページの更新検知の記録（2026-08-20〜10-25、1,204 件） | `site/data/watch-log/YYYY-MM.json`。記録の 1 件ごとの `archive_url` が、その版の Wayback の保存先（1,204 件中 683 件。残りは Wayback に保存が無く、埋められなかった） |
| 記録の要約（期間・件数・市町村別・種類別・日別） | `site/data/archive-summary.json` |
| 支援策の一覧と、その変化の履歴 | `data/supports.csv` と git の履歴 |
| 公式ページの当時の姿 | Wayback Machine（`site/data/archive-index.json`） |

再開するときは `site/data/site-status.json` の `archived` を `false` に戻し、`.github/workflows/` の 4 本の `schedule:` のコメントを外します。手順は [`docs/archive-runbook.md`](./docs/archive-runbook.md)。

## 似た仕組みを作るとき（経緯・構成・設定・罠）

次の災害で同じものを立ち上げる人のために、何をどう作ったかをここに残す。手順そのものは [`docs/replication-checklist.md`](./docs/replication-checklist.md)、止め方は [`docs/archive-runbook.md`](./docs/archive-runbook.md)。

### 経緯

| 日 | できごと |
|---|---|
| 2026-08-13〜14 | 令和8年8月千葉豪雨。県内で死者 13 人・床上浸水約 2,000 棟（当時の報道） |
| 08-14 | CTZC の有志で着手。要件定義（[`docs/input/`](./docs/input/)）を GitHub に公開し、同日に GitHub Pages の簡易サイトを出す。先行事例は [シビックテック袖ケ浦の災害支援ナビゲーター](https://civictechsodegaura.org/) |
| 08-15 | CTZC 公式サイトで告知。54 市町村の公式リンクをそろえ、日次収集を回し始める |
| 08-16 | 市町村検索（読みがな）・時期別ページ・「困りごとから探す」と自己チェックを足す（PR #1〜#8） |
| 08-18 | 市町村の公式リンクを `data/supports.csv` に集め、受付状態と確認日つきで市町村ページの最上部に出す（#7） |
| 08-19〜20 | 「この情報は違う」の報告フォーム（#11）、公式ページの更新検知（#12）、Slack の朝のまとめ（#15）、更新履歴ページ（#16）、月別ログと Wayback への保存で、履歴が消えないようにする（#17〜#19） |
| 08-23〜27 | 県・国のページも監視に加える（#22）。リンクの鮮度を見て張り替え 11・追加 14（#21）。候補の自動発見（#24）。本文からサイドバーなどを外して誤検知を減らす（#25） |
| 08-25 | トップを「困っている人ファースト」に変える（#26。要件の変更を伴う判断） |
| 08-31 | サイト固有の値を `config.json` に集める（#33）。止めたあとの見え方と記録の残し方を先に用意（#30）。Wayback の依頼間隔を 20 秒に戻す（#34） |
| 09-01〜02 | 候補から 43 件を採用（#35）。北陸豪雨向けに複製して `hokurikugouu` を立ち上げる |
| 09-05〜06 | supports.csv の見直し。機械で材料を集め、人が読んで判断する道具（#38） |
| 10-25 | 個人アカウント（office626）から CTZC の organization へ移す（#39・#40）。同日、更新を止めて記録として残す |

関わった人：CTZC（CivicTechZenChiba）の有志。リポジトリの作成とオーナーは office626、開発の大半は jollyjoester（Code for INZAI）。開発は Claude Code を相棒にして進め、コミットの本文に「なぜそうしたか」を残すようにした。supports.csv の受付状態のような「読んで決める」ことは人がやり、機械は材料集めまでに留めた。

### 動いている仕組み

| 何 | いつ | 中身 |
|---|---|---|
| `daily.yml` 日次収集 | 6:00 JST | 市町村・県・国の公式ページと報道の見出しを集め、`site/data/collection.json` などを作って Pages を公開する |
| `watch.yml` 更新検知 | 約 3 時間おき（実際は 4〜8 時間おき） | `supports.csv` の全ページの本文のハッシュを比べ、変わった行を `watch.json` と月別ログに記録し、Wayback に保存を頼む |
| `archive.yml` Wayback 保存 | 日曜 3:10 JST | 全公式ページを Wayback に保存し、`archive-index.json` に記録する。1 件 45 秒・間隔 20 秒で 200 件に 2 時間半 |
| `notify.yml` Slack 通知 | 7:00 JST | 直近 24 時間の更新検知を Slack にまとめて投稿する。`SLACK_WEBHOOK_URL` が無ければ何もしない |
| `pages.yml` 公開 | push のたび | 日英の検査（`check_bilingual.py`）と sitemap の生成をしてから Pages を公開する |

人のデータは 2 つ。`site/data/municipalities.json`（市町村の一覧と公式トップ・防災ページ）と `data/supports.csv`（種類ごとの公式ページ、受付状態、確認日、期限、メモ）。ほかは全部、スクリプトが作る。

### 設定の一覧（複製するとき差し替えるもの）

| 置き場 | 何を決めるか |
|---|---|
| `site/data/config.json` | `repo`・`base_url`・`ua_prefix`（外部サイトへ名乗る UA）・災害名（日英）・発災日・県と国の `regions` |
| `scripts/apply_site_urls.py` | `config.json` を書き換えたあとに流す。HTML の canonical・og:url・hreflang・GitHub へのリンクを一括で置き換える |
| `site/data/report-config.json` | 「この情報は違う」の送り先 Google フォームと entry ID。空なら GitHub Issue へ落ちる |
| `site/data/vote-config.json`・`site/supporters/index.html` | 運用スプレッドシートの URL（HTML に直書きの箇所がある） |
| リポジトリの Secrets `SLACK_WEBHOOK_URL` | 通知先の Slack チャンネル。災害ごとに別にする |
| GitHub Pages | Settings → Pages を「GitHub Actions」にする。API なら `POST /repos/<owner>/<repo>/pages` に `build_type=workflow` |
| workflow の有効化 | 複製直後は 4 本とも止めておき、`daily` と `watch` を手で 1 回ずつ流してから schedule を有効にする |
| インフォグラフィック | `scripts/build_infographics.py`・`build_infographics_en.py`（Pillow と日本語フォントが要る） |
| 日英の同期記録 | `python scripts/check_bilingual.py --update-manifest`。これを忘れると Pages の公開が落ちる |

### 踏んだ罠

- **自動で「受付終了」を付けない。** 本文にある別の災害の話や過去の期限を拾って誤って閉じる（我孫子市の東日本大震災の記述、匝瑳市の 2019 年の期限）。機械は材料集めまで、判断は人
- **Wayback は間隔 20 秒を下げない。** 5 秒にしたら 159 件中 124 件が失敗した。保存は 1 件 45 秒前後かかる
- **更新検知が 1 回の実行で Wayback に保存を頼める件数には上限がある。** 残りの更新には保存リンクが付かない。あとから `scripts/backfill_archive_urls.py` で、Wayback に保存済みのものから埋められる
- **行政ページは数日で 404 になる。** 8/16→8/20 で 8 件、8/20→8/23 で 11 件。だから監視と保存が要る
- **GitHub の schedule は 3 時間おきと書いても 4〜8 時間おきになる。** 表示は「数時間おき」にしてある
- **`daily.yml` と `watch.yml` が重なると push が拒否される。** push の前に `git pull --rebase origin main` を入れる
- **fork で複製すると PR の base が元の repo に向く。** 新しい repo を作って履歴ごと push するほうが安全。fork は push で `pages.yml` が起動しないこともある
- **config.json だけ変えても URL は変わらない。** HTML・README・インフォグラフィックの脚注は静的なので、`apply_site_urls.py` と描き直しが要る

## このリポジトリで見ること

要件の本体は [`docs/input/`](./docs/input/) です。

| ファイル | 内容 |
|----------|------|
| [docs/input/README.md](./docs/input/README.md) | プロジェクト概要 |
| [docs/input/business-requirements.md](./docs/input/business-requirements.md) | ビジネス要件 |
| [docs/input/user-personas.md](./docs/input/user-personas.md) | ターゲットユーザー |
| [docs/input/product-requirements.md](./docs/input/product-requirements.md) | プロダクト要件 |
| [docs/input/user-flows.md](./docs/input/user-flows.md) | ユーザーフロー |
| [docs/input/feature-list.md](./docs/input/feature-list.md) | 機能一覧 |
| [docs/input/mvp-scope.md](./docs/input/mvp-scope.md) | MVP範囲 |
| [docs/input/ui-ux-direction.md](./docs/input/ui-ux-direction.md) | UI/UX方針 |
| [docs/input/source-allowlist.md](./docs/input/source-allowlist.md) | 行政・報道の収集許可リスト（毎日 6:00 JST） |
| [docs/output/system_requirements.md](./docs/output/system_requirements.md) | システム要件 |
| [docs/output/detailed_requirements_specification.md](./docs/output/detailed_requirements_specification.md) | 詳細要件（実装向け） |
| [運用スプレッドシート](https://docs.google.com/spreadsheets/d/1_dHZHMLvTx6iTCzwvbw6U9cTHjTIH_6RlEob81Ng7KM/edit?usp=sharing) | 許可リスト・やること・訂正。リンクを知っている人は閲覧可 |

`docs/prompts/` と `docs/template/` は、要件を引き出すためのプロンプトとテンプレートです。

## 日本語版・英語版の更新

- 日本語版は `site/`、英語版は同じ構成の `site/en/` にあります。
- 表示文言、リンク、メタデータ、動的UI、インフォグラフィックを変更するときは、日英を同じ変更で更新します。
- `python scripts/sync_language_chrome.py` で全ページの言語切替と `hreflang` を補完します。
- 日英双方を確認後、`python scripts/check_bilingual.py --update-manifest` で同期記録を更新します。
- 通常の確認は `python scripts/check_bilingual.py` です。GitHub Pages の公開前にも同じ検査が動きます。

## プロダクトの骨格（要約）

一つのサイトに二つの入口を持つ。

1. **県民向け** — 市町村ごとの被害状況ログ（過去〜現在）と、いま受けられる支援策
2. **支援者向け** — 有志が集まり、行政情報の収集と伝達拡散を分担する場

先行事例として [シビックテック袖ケ浦の災害支援ナビゲーター](https://civictechsodegaura.org/) を県全域・市町村別に広げる（ソース再利用は作成後に確認）。現地の行政プロセスは「とある行政」の知見として一般化しており、個人名・特定の内部情報は出さない。

初日に被害ログを出す対象は、警戒レベル5（大雨特別警報）が出た自治体および流山市。県民向け情報は行政機関と報道機関から収集し、1日1回自動更新する。

## 検証してほしいこと

- 県民入口と支援者入口の切り分けは分かりそうか
- 市町村ページのテンプレート（ログ／いまの支援策／生活再建の段取り）に足りない欄はないか
- MVP の切り方（枠は全市町村、初日ログはレベル5対象＋流山市）は現場で回るか
- 公式情報の扱いに危うい断定がないか（金額・日数は裏取り前に断定しない方針）
- 既存の行政・社協・他団体の取り組みと重複していないか

## 注意

- 本資料は有志の検討用であり、行政の公式発表ではない
- 制度の金額・所要日数・適用可否は各実施機関の判断。公開前に公式で確認する
- `[仮]` や `[要公式確認]` が付いた項目は未確定

## 連絡

- CTZC ウェブサイト: https://sites.google.com/view/civictechzenchiba/
- Facebook グループ: https://www.facebook.com/groups/civictechzenchiba/
- Facebook ページ: https://www.facebook.com/p/Civic-Tech-Zen-Chiba-100064346395345/
- CTZC Slack: https://civictechzenchiba.slack.com/archives/C0BPSMN4L5D
