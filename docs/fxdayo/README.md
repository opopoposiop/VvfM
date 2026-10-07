# .fxdayo開発者向け資料

MikuMikuDayo 1.30の原文を記述し、VMD Viewer v0.56.20の限定profileで検査・再読込・保存・出力するための資料。

| 目的 | 入口 |
|---|---|
| 原文を書く、操作方法と制約を確認する | [開発者ガイド](FXDAYO_DEVELOPER_GUIDE.md) |
| 単純露出・モーフ制御・2パスの作例を使う | [教材](examples/README.md) |
| Jsonnet評価後の構造を検査する | [JSON Schema](definition.schema.json) |
| P0・P1の採用範囲と将来の拡張を確認する | [インターフェイス計画](INTERFACE_PLAN.md) |
| 実行した検証と未検証を確認する | [v0.56.20の実装記録](../../reports/2026-10-07-fxdayo-interface-v05620/IMPLEMENTATION.md) |
| 初稿の調査資料を特定する | [2026-10-06のsnapshot](SOURCE_SNAPSHOT.json) |

P0・P1を今回の実装範囲とし、P2以降、Windows版Dayoの実行・画像同等、正式性能受入は含めない。過去のbuild402の証拠と、今回の作例・reload経路の結果を区別する。

## 取込情報

2026-10-07、開発リポジトリの`docs/fxdayo/FXDAYO_DEVELOPER_GUIDE.md`と関連資料を取り込んだ。対象はv0.56.20の作業ツリーであり、未コミット変更を含む。配布アプリの最新版・GitHub Release公開を示すものではない。

- 開発元の基準HEAD: [`16e20241e84755c78cb180b3e1f190dc7c73bfaa`](https://github.com/opopoposiop/VMDviewer_for_Mac/commit/16e20241e84755c78cb180b3e1f190dc7c73bfaa)（`codex/pmxchange`）
- 取込元ガイドのSHA-256: `06a594f7e553f7be090b8d2254ccacac7e87a486c782601002673a126dcdb81b`
- 収録範囲: 開発者ガイド、計画、定義schema、初稿の参照snapshot、3組の教材とPMX再生成スクリプト、v0.56.20の実装・レビュー・Release・GUI記録
- 編集範囲: 公開用の参照リンクと転載注記。教材・schema・初稿snapshotは原本のbytesを保持した。

コード・過去の検証記録へのリンクは、存在を確認した開発元の上記公開コミットへ固定した。公開コミットには今回のv0.56.20の未コミット実装差分は含まれず、ガイドの説明とコードが一致しない箇所がある。開発元のソースツリーはVvfMには収録していない。

v0.56.20の実装記録に付随する生ログや`evidence/`資料は転載対象外とし、その参照は開発元ローカルのファイル名として残した。記録中の「commit／push／GitHub公開は行っていない」は開発元の実装・成果物についての記録であり、この文書の公開状態を指さない。検証件数・GUI結果は開発元の記録を転載したもので、本取込ではビルド・テスト・実機検証を再実施していない。
