# .fxdayo教材

このリポジトリで新しく作成した原文と、画像ファイルを使わないPMX三角形。第三者のモデル・textureは含まない。

| 原文 / 同名PMX | 動作 |
|---|---|
| [ExposureDemo.fxdayo](ExposureDemo.fxdayo) / [PMX](ExposureDemo.pmx) | HDRのRGBを2倍、alphaを保持 |
| [ExposureController.fxdayo](ExposureController.fxdayo) / [PMX](ExposureController.pmx) | 「明るさ」モーフから`exp2(2 * clamp(value, -1, 1))`倍 |
| [ExposureMultipass.fxdayo](ExposureMultipass.fxdayo) / [PMX](ExposureMultipass.pmx) | 中間textureへ2倍露出、その後RGBに`(1, 0.85, 0.7)`を乗算 |

操作は[開発者ガイド](../FXDAYO_DEVELOPER_GUIDE.md)。HQ Toon・FrameTime・透視投影、AA/DoF/Bloom/Diffusionなし、不透明出力で使用する。最初の2作例はcolor profile、2パス作例はscene profile。後者には不透明triangleのscene制約がある。

PMXには1本のセンターボーンと、形状を変えない「明るさ」モーフを含む。再生成は`python3 docs/fxdayo/examples/generate_pmx.py`。原文を編集してもモデルの名前・モーフ名は変更しない。

GPUテストは1920×1080の中間HDR値で確認する。controllerは-1 / 0 / 0.5 / 1 / 2を用い、UIから全値を入力できるとの保証とは分ける。結果は[実装記録](../../../reports/2026-10-07-fxdayo-interface-v05620/IMPLEMENTATION.md)。Dayoアプリ側の実行・最終画像比較は未検証。
