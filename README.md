# VMD Viewer for Mac（VvfM）

> 2026年11月8日更新：[v0.58.4／build569の変更概要](docs/updates/codex-motion-2026-11-08.md)。動画入りプロジェクトの保存、自動保存と回復、モーフ／カメラのダブルクリック登録、HQ設定の説明表示を更新しました。

[EULA 日本語原本](Licenses/VMDViewer-EULA-ja.md)｜[English](Licenses/VMDViewer-EULA-en.md)

PMXモデルとVMDモーションをMacで再生・編集し、音声付きの動画を書き出せるアプリです。ボーン・表情・カメラの調整から、見た目の仕上げ、作業の保存まで行えます。

このリポジトリには、配布案内・操作説明・スペックシートを掲載します。アプリ本体のソースコードは非公開とし、アプリはバイナリ形式で公開する予定です。

**詳しい操作は [一般ユーザーマニュアル（GUIDE.md）](GUIDE.md) を参照してください。**

操作説明はv0.56.49／build453を基に、v0.58.4／build569までの変更点を本文と更新補足へ追記しています。READMEと一般ユーザーマニュアルの画面例は、2026年11月8日に起動中のv0.58.4／build569から撮影しました。[スペックシート](docs/spec-sheet/VMDViewer_SpecSheet_ja.md)は2026年10月28日・保存済みv0.57.22／build495を基準とする別資料です。配布アプリの公開状況はReleasesで確認してください。

![VvfM v0.58.4／build569のメイン画面](images/v0.58.4-build569/01-overview.png)

## 主な機能

- 複数のPMXモデルとVMDモーションの読み込み・再生、編集を引き継ぐPMXの入れ替え
- ボーン・モーフ・カメラのタイムライン編集、補間曲線、指ポーズ、重み付きモーションレイヤー
- 独立したカメラ1／2、停止中の自由視点、左右反転・まばたき・目線キーの生成
- WAV／M4A音声の再生・波形表示、背景・スクリーンへの動画投影
- Metal／ToonShader LE／ToonShader HQ、DoFの設定キー・画面からの合焦、対応範囲内の`.fxdayo`
- 背景色・環境光・平行光源のキーフレーム編集
- 素材と設定をまとめた `.vmdviewer` 保存、VMD保存、H.264／HEVC／ProRes動画出力

## 動作環境と入手

macOS 14以降のMetal対応Macが必要です。配布アプリの対応チップ・環境・利用条件は、入手元の案内を確認してください。アプリの実行にXcodeは不要です。

配布情報は [Releases](https://github.com/opopoposiop/VvfM/releases)、導入・初回起動は [GUIDEの「導入と起動」](GUIDE.md#導入と起動) を参照してください。

モデル・モーション・音源は、利用許諾を確認したものを別途用意します。

## ライセンスと公開方針

公開文書とアプリのバイナリでは、ライセンスの適用対象を分けています。詳細は [ライセンス適用範囲（LICENSING.md）](LICENSING.md) を参照してください。

- **公開文書・MIT対象として提供するサンプル等**：[MIT License](LICENSE)を維持します。
- **今後EULAを明示して公開するアプリ独自バイナリ**：[補足EULA](Licenses/VMDViewer-EULA-ja.md)を適用し、逆コンパイル・逆アセンブル等のリバースエンジニアリングを禁止する条項を定めています。適用法令、第三者ライセンス、既に付与されたMIT等の許諾による例外を保持します。
- **第三者のライブラリ・SDK・エフェクト・素材**：各権利者の条件と通知を維持します。[第三者通知](THIRD_PARTY_NOTICES.md)と[ライセンス原文一覧](Licenses/README.md)を確認してください。

補足EULAは **2.0（2026年10月31日確定）** です。[日本語版](Licenses/VMDViewer-EULA-ja.md)を原本とし、[英語版](Licenses/VMDViewer-EULA-en.md)は参考訳です。内容に相違がある場合は、第9条に従い日本語原本が優先します。対象のversion/build、全文の提示・同意方法、配布物の条件は採用するReleaseで明示します。この案内と文書の追加によって、既存版のMIT許諾や保存済みbuild495のアプリ・ZIPの条件が変わることはありません。

## 使い始める

1. PMXと付属テクスチャのフォルダ構成を保ち、**⇧⌘O** でPMXを読み込みます。
2. 対象モデルを選び、0フレームへ戻って **⌥⌘O** でVMDを読み込みます。
3. **Space** で再生し、必要に応じて音声・カメラを追加します。
4. **⌘S** で作業を保存します。動画出力は **⇧⌘E** から、短い区間で試せます。

編集や物理演算、エフェクト、動画出力の設定は [GUIDE.md](GUIDE.md) にまとめています。

## 利用時の注意

MikuMikuDanceとの画像・物理・エフェクトの完全一致は保証していません。負荷は素材と設定によって変わるため、短い試行と別名保存で確認してください。素材入りのプロジェクトを共有する場合は、各素材の再配布条件とクレジットを確認してください。

## ドキュメント・問い合わせ

- [一般ユーザーマニュアル](GUIDE.md)：操作手順、ショートカット、対応範囲、困ったときの確認事項
- [技術ガイド](VvfM_Technical_Note.md)：編集・描画・保存の仕組み、形式互換、性能の検証範囲
- スペックシート：[PDF](docs/spec-sheet/VMDViewer_SpecSheet_ja.pdf)／[Markdown](docs/spec-sheet/VMDViewer_SpecSheet_ja.md)。2026年10月28日・v0.57.22／build495基準
- [.fxdayo資料の案内](docs/fxdayo/README.md)：開発者向け解説、教材、対応条件と現行版との差分
- [ライセンス適用範囲](LICENSING.md)／[MIT原文](LICENSE)／[EULA日本語原本](Licenses/VMDViewer-EULA-ja.md)・[英訳](Licenses/VMDViewer-EULA-en.md)／[第三者通知](THIRD_PARTY_NOTICES.md)
- [Issues](https://github.com/opopoposiop/VvfM/issues)：不具合報告。アプリの版、Macの環境、操作手順、エラーを添えてください

  ## 謝辞

VMD viewer for Macの開発にあたり技術的参考にさせていただきました お礼申し上げます

[MikuMikuDance](https://sites.google.com/view/vpvp/?pli=1&authuser=0) 樋口M 様
[MikuMikuDayo](https://github.com/pennennennennennenem/MikuMikuDayo) サンドマン 様
[MikuMikuMoving](https://sites.google.com/site/mikumikumoving/) Mogg 様
[PMXEditor](https://www.nicovideo.jp/watch/sm14024773) 極北P 様
[AutoLuminous](https://www.nicovideo.jp/watch/sm19843111) そぼろ 様
[msToonCoordinator](https://www.nicovideo.jp/watch/sm39850446) ましまし 様
[ikHolographic](https://seiga.nicovideo.jp/seiga/im8315687) ikeno 様
[浅草みどり](https://www.nicovideo.jp/watch/sm36384153) くれよん 様
[水崎ツバメ](https://www.nicovideo.jp/watch/sm36519353) くれよん 様
