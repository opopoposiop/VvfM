# .fxdayo教材

> VvfM収録注（2026-10-19）：開発版v0.56.49／build453（記録ID `3620662`）から取り込みました。教材の内容・検証条件は本文に記した導入時点のものです。現行版の対応範囲は[資料の案内](../README.md)を参照してください。本取り込みではビルド・実機試験を再実施していません。


このリポジトリで新しく作成した原文と、画像ファイルを使わないPMX三角形。第三者のモデル・textureは含まない。

| 原文 / 同名PMX | 動作 |
|---|---|
| [ExposureDemo.fxdayo](ExposureDemo.fxdayo) / [PMX](ExposureDemo.pmx) | HDRのRGBを2倍、alphaを保持 |
| [ExposureController.fxdayo](ExposureController.fxdayo) / [PMX](ExposureController.pmx) | 「明るさ」モーフから`exp2(2 * clamp(value, -1, 1))`倍 |
| [ExposureMultipass.fxdayo](ExposureMultipass.fxdayo) / [PMX](ExposureMultipass.pmx) | 中間textureへ2倍露出、その後RGBに`(1, 0.85, 0.7)`を乗算 |

操作は[開発者ガイド](../FXDAYO_DEVELOPER_GUIDE.md)。ToonShader HQ・FrameTime・透視投影、AA/DoF/Bloom/Diffusionなし、不透明出力で使用する。最初の2作例はcolor profile、2パス作例はscene profile。後者には不透明triangleのscene制約がある。

PMXには1本のセンターボーンと、形状を変えない「明るさ」モーフを含む。再生成は`python3 docs/fxdayo/examples/generate_pmx.py`。原文を編集してもモデルの名前・モーフ名は変更しない。

GPUテストは1920×1080の中間HDR値で確認する。controllerは-1 / 0 / 0.5 / 1 / 2を用い、UIから全値を入力できるとの保証とは分ける。これは教材の中間値の検証で、すべての原文や最終画像の検証ではない。Dayoアプリ側の実行・最終画像比較は未検証。
