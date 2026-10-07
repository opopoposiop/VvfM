# v0.56.20 / build409

> 開発元の2026-10-07時点の記録を転載しています。本文の実装・検証・Releaseは開発元での結果であり、VvfMへの文書取込時には再実施していません。生ログなどの`evidence/`資料は開発元ローカルにあり、本リポジトリには収録していません。[取込情報](../../docs/fxdayo/README.md#取込情報)

2026-10-07。インターフェイス計画のP0・P1を収録したローカルRelease。旧build408以前を保持し、commit／push／GitHub公開は行っていない。

## 成果物と照合

- app: `dist/release-v0.56.20-build409/VMD Viewer.app`
- dSYM: `dist/release-v0.56.20-build409/VMDViewer.dSYM`
- version / build: `0.56.20` / `409`
- 基準HEAD: `16e20241e84755c78cb180b3e1f190dc7c73bfaa`、dirty=true
- Release build date: `2026-10-07T06:23:14Z`、SDK `27.0`、arm64
- ソース入力817件のSHA-256: `e9ab09cb66bc142e659541e3ef012057a8d104ab9c6a3bc11b3174233cf55fb6`
- 実行ファイルSHA-256: `50933ced9889170e565115837f2c8d6c995f3effdb74d59fcbe85d842114ee39`
- Mach-OとdSYMのUUID: `4D9874AF-1B6F-3D63-A0F2-2124433B1EB1`

`BUILD_NUMBER=409 VMD_VIEWER_OUTPUT_ROOT=dist/release-v0.56.20-build409 ./scripts/build-app.sh release`で生成。`dsymutil`でdSYMを保存し、`codesign --verify --deep --strict`、build scriptと同じ入力集合の指紋、同梱schemaのbyte一致を確認した。署名検証はDeveloper ID／notarizationの確認を意味しない。照合JSON（開発元ローカル資料: `evidence/release-verification.json`）／入力一覧（開発元ローカル資料: `evidence/release-inputs.tsv`）／buildログ（開発元ローカル資料: `evidence/release-build.log`）。

## 検証範囲

GUIを有効にした最終全テストは実通過2,489、条件付きskip49、失敗0（170.344秒）。ガイド3作例の1080p HDR値、AND条件のGPU動作、依存・cache更新、元MotionBlurの7pass／12stage、schema25復元、独立した2個体と6frame動画のPTSを確認した。GUI test hostの起動初期化と画面倍率によるfixture寸法を修正した後、実表示／作者操作の2件も最終全体実行で通過。先行するtimeoutと寸法不一致の証拠も保持する。[全体記録](IMPLEMENTATION.md)。

このRelease本体をLaunchServicesで起動し、同梱compilerによる再検査、正常版の表示後採用、故障版の元行診断と旧版保持、診断JSON・project保存を確認した。[GUI記録](GUI.md)。

`performanceAccepted=false`。Windows Dayoとの画像比較、正式性能matrix、600秒耐久、任意GPU fault、全OS／複数画面、UI非表示全画面の作者UIは未受入。P2・P3、独立temporal profile、端数compute dispatchは未実装。

教材と再生成手順は[examples](../../docs/fxdayo/examples/)、操作と対応条件は[開発者ガイド](../../docs/fxdayo/FXDAYO_DEVELOPER_GUIDE.md)を参照する。
