# PMX 2.1の読み直し — 再開準備

状態：音声生成枠の不足により未完了。新しい音声・完成動画は作成していません。

同じHeyGen Jhennyで、以下の2文を全文読み直す依頼です。

1. 2分34秒付近：ぴーえむえっくす　にーてん　いちのモデルにも対応しています。
2. 2分43秒付近：ぴーえむえっくす　にーてん　いちのキューデフは、ねじったときの形を保つための変形方式です。

2026年10月23日、1文目の生成が `insufficient_credit`（HTTP 402）で失敗しました。応答は残り4秒・必要5秒で、音声は作成されていません。2文目は送信していません。自動再試行は行っていません。

入力には前回の一文読み直し版 `../vvfm-introduction-sentence-reread-jhenny-20261022/` を使用します。現在の完成MP4・音声・公開用編集ソースは変更していません。利用枠の解消後、ユーザーの再開指示を受けて生成と差し替えを行います。

- [1文目の生成依頼](source/heygen-scene11-request.json)
- [サービスの失敗応答](source/heygen-scene11-result.json)
- [2文目の原稿・未送信](source/heygen-scene12-request-not-submitted.json)
- [再開条件と対象位置](source/pending-edit.json)
