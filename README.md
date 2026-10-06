# VMD Viewer for Mac（VvfM）

PMXモデルとVMDモーションをMacで再生・編集し、音声付きの動画を書き出せるアプリです。ボーン・表情・カメラの調整から、見た目の仕上げ、作業の保存まで行えます。

**詳しい操作は [一般ユーザーマニュアル（GUIDE.md）](GUIDE.md) を参照してください。**

![VvfMのメイン画面](images/01-scene3-overview.jpg)

## 主な機能

- 複数のPMXモデルとVMDモーションの読み込み・再生
- ボーン・モーフ・カメラのタイムライン編集、補間曲線、指ポーズ、モーションレイヤー
- WAV／M4A音声の再生・波形表示、背景・スクリーンへの動画投影
- Metal／ToonShader LE／ToonShader HQ、DoF、材質・エフェクトの調整
- 素材と設定をまとめた `.vmdviewer` 保存、VMD保存、H.264／HEVC／ProRes動画出力

## 動作環境と入手

macOS 14以降のMetal対応Macが必要です。配布アプリの対応チップ・環境・利用条件は、入手元の案内を確認してください。アプリの実行にXcodeは不要です。

配布情報は [Releases](https://github.com/opopoposiop/VvfM/releases)、導入・初回起動は [GUIDEの「導入と起動」](GUIDE.md#導入と起動) を参照してください。

モデル・モーション・音源は、利用許諾を確認したものを別途用意します。

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
- [LICENSE](LICENSE)／[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)：本体と同梱ライブラリ・画像・エフェクトの利用条件
- [Issues](https://github.com/opopoposiop/VvfM/issues)：不具合報告。アプリの版、Macの環境、操作手順、エラーを添えてください
- [開発リポジトリ](https://github.com/opopoposiop/VMDviewer_for_Mac)：実装と変更履歴
