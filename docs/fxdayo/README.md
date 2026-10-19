# .fxdayo開発者向け資料

MikuMikuDayo 1.30の原文と、VMD Viewerの専用adapter・限定原文runtimeを理解するための資料です。2026年10月19日に確認した[公開main `3620662`](https://github.com/opopoposiop/VMDviewer_for_Mac/tree/36206626a7214ad8b8de5bba362189a38c285529)（v0.56.49／build453）を参照しています。VvfMでの配布公開や、Dayoとの画像一致を示すものではありません。

| 目的 | 入口 |
|---|---|
| 原文を書く、操作方法と制約を確認する | [開発者ガイド](FXDAYO_DEVELOPER_GUIDE.md) |
| 単純露出・モーフ制御・2パスの作例を使う | [教材](examples/README.md) |
| Jsonnet評価後の構造を検査する | [JSON Schema 2](definition.schema.json) |
| 採用範囲と将来の拡張を区別する | [インターフェイス計画](INTERFACE_PLAN.md) |
| 失敗・再試行・保存の設計を読む | [フェイルセーフ設計](FAILSAFE_DESIGN.md) |
| Blue Palaceの限定SSRと検証範囲を確認する | [SSR profile](BLUE_PALACE_SSR.md) |
| 初稿の調査資料を特定する | [2026-10-06のsnapshot](SOURCE_SNAPSHOT.json) |

## 現行版と資料の時点の違い

開発者ガイド本文の「現行」は主にv0.56.37の研究時点を指し、v0.56.42の追記を含みます。計画の旧P2／P3や研究のR0〜R7を、現行機能の一覧や全項目完成の宣言として読まないでください。

- **v0.56.42**：v2 profileへ共通定義、pass macro、対応するBORDER／UNORM、self bool／int、2D／3D texture、mip・clear／copy等を追加。不透明8bit PNG／BMPの依存保存と、HDR／tone mapper／表示linearの担当・順序を検査します。[実装と未完了項目](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-runtime-v05642/IMPLEMENTATION.md)。
- **v0.56.46**：色処理専用原文とFXAAの明示profile併用、骨controller、UUIDで指定する別個体controllerを追加しました。資料中の「骨・外部個体は未対応」は、この後続対応と分けて読んでください。[採用範囲](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-17-research-implementation-v05646/CONTROLLERS.md)／[全体の実装・検証](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-17-research-implementation-v05646/IMPLEMENTATION.md)。
- **v0.56.47以降**：通常のeffect候補失敗とGPU device障害を区別します。device障害では描画・背景GPU処理・MetalFX生成・動画出力を再起動まで止め、保存は維持します。「効果を除外すれば常に描画継続できる」という保証ではありません。[GPU障害時の停止](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-18-gpu-failure-stop/README.md)。

任意の端数dispatch、共有Fog／Fluid simulation、すべての描画方式の混在への一般化はできません。構造schemaの通過、解析、compile、GPU実行、実表示、原版との画像同値、正式性能・600秒耐久は別の確認です。JSON Schema 2は旧v1と拡張v2の構造上の上位集合であり、実行の許可や全機能対応を示すものではありません。

## 取込情報

今回の取込元は上記の公開mainに固定し、開発ブランチの未公開差分は含めていません。開発者ガイド、計画、フェイルセーフ、SSR、教材説明、定義schemaを同期しました。文書へ収録注を追加し、収録外のコード・仕様・検証記録へのリンクは同じ公開コミットへ固定しています。開発元のソースツリーや生ログはVvfMへコピーしていません。

3組の教材の `.fxdayo`／PMXと再生成スクリプト、初稿 `SOURCE_SNAPSHOT.json` は、公開mainと同一のbytesを保持しています。snapshotは2026-10-06の初稿の調査対象を示す履歴で、今回の取込コミットへ書き換えていません。

従来収録した[v0.56.20の実装・レビュー記録](../../reports/2026-10-07-fxdayo-interface-v05620/IMPLEMENTATION.md)と、そのRelease・GUI記録は当時の資料として残しています。初回取込は2026-10-07、基準HEAD `16e20241e84755c78cb180b3e1f190dc7c73bfaa` の未コミット変更を含む作業ツリー由来でした。記録中の未公開・未検証という説明や、転載していない `evidence/` の名前を、現行版の結果へ読み替えないでください。

検証件数・GUI・性能の結果は開発元の記録を参照したもので、今回の文書更新ではアプリのビルド・テスト・実機試験を再実施していません。ライセンスと同梱toolchainの通知は[第三者ライセンス](../../THIRD_PARTY_NOTICES.md)を確認してください。
