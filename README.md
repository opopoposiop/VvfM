![MacでMMD — VMD Viewer for Mac](images/vvfm-eyecatch.jpg)

# VMD Viewer for Mac（VvfM）

[アプリをダウンロード（ZIP）](https://github.com/opopoposiop/VvfM/releases/download/v0.58.18/VMD.Viewer.app.zip)｜[リリース詳細](https://github.com/opopoposiop/VvfM/releases/tag/v0.58.18)｜[導入・初回起動](GUIDE.md#導入と起動)｜[スペックシート](docs/spec-sheet/VMDViewer_SpecSheet_ja.md)

[EULA 日本語原本](Licenses/VMDViewer-EULA-ja.md)｜[English](Licenses/VMDViewer-EULA-en.md)

PMXモデルとVMDモーションをMacで再生・編集し、音声付きの動画を書き出せるアプリです。ボーン・表情・カメラの調整から、見た目の仕上げ、作業の保存まで行えます。

　[作例/紹介動画](https://www.nicovideo.jp/watch/sm47023510)

このリポジトリには、配布案内・操作説明・スペックシートを掲載します。アプリ本体のソースコードは非公開とし、アプリは[Releases](https://github.com/opopoposiop/VvfM/releases)でバイナリ形式で配布しています。

**詳しい操作は [一般ユーザーマニュアル（GUIDE.md）](GUIDE.md) を参照してください。**

![VvfM v0.58.4／build569のメイン画面](images/v0.58.4-build569/01-overview.png)

## v0.58.18の更新内容

**再生・編集**

- **物理ループ再生の停止を修正**:「物理優先・再生時のみ」で、ループ先頭の姿勢を準備したまま再生が止まる不具合を修正しました
- **指ポーズの適用率を追加**:左手・右手・両手・選択ボーンを対象に、現在の姿勢とVPDポーズを0〜100%で混ぜられます。登録前に割合を変えて試せるほか、取消で元の未登録姿勢に戻せます。
- **多層ボーンタイムラインの編集待ちを短縮**:レイヤーをボーン別にまとめて表示行を作るようにしました。
- **再生時の描画待ちを追跡できるよう改善**:姿勢や動画の準備完了から、メインスレッドでの受付、対応する描画までを結び付けて記録できるようにしました。

**描画・画質**

- **ToonShader HQの光・影・材質調整を拡充**:材質ごとに局所光を当てても影を残す量を調整でき、リムライトは主光源の方向と色に追従できます。髪の帯状ハイライトの強さ・幅・毛流れ、遠景で密集する内側線の濃さも調整可能になりました。幾何AOには地平線方式を追加し、床と箱の接地付近で陰影の計算誤差を減らしました。
- **HQの新機能をOFFにしたときのGPU負荷増を抑制**:リムライトの方向追従がOFFなら専用の軽い描画処理を使います。
- **カメラの被写界深度に新方式を追加**:新方式`type1`は背景の大小のボケを分けて八角形に、手前の大きなボケを円形に描きます。既存プロジェクトは従来方式の`type2`で開きます。どちらも同じ焦点・F値・ボケ量のキーを使い、再生と動画書き出しに反映します。

**読み込み・書き出し**

- **大型VMDの読み込み時のメモリ使用量を削減**:連続するボーンキーの補間データが同じ場合にメモリを共有します。
- **動画書き出しの頂点モーフをGPU化**:対応するMacでは、通常PMXの表情などによる頂点変形をGPUで計算し、MOV完成までの時間を短縮しました。CPU互換設定、ソフトボディや`.fxdayo`付きのモデルにはCPU処理を使います。

## 主な機能

- 複数のPMXモデルとVMDモーションの読み込み・再生、編集を引き継ぐPMXの入れ替え
- ボーン・モーフ・カメラのタイムライン編集、補間曲線、指ポーズ、重み付きモーションレイヤー
- 独立したカメラ1／2、停止中の自由視点、左右反転・まばたき・目線キーの生成
- WAV／M4A音声の再生・波形表示、背景・スクリーンへの動画投影
- Metal／ToonShader LE／ToonShader HQ、DoFの設定キー・画面からの合焦、対応範囲内の`.fxdayo`
- 背景色・環境光・平行光源のキーフレーム編集
- 素材と設定をまとめた `.vmdviewer` 保存、VMD保存、H.264／HEVC／ProRes動画出力

## 動作環境と入手

macOS 14以降のMetal対応Mac(M2以降)が必要です。Intel CPU搭載のMacでは動作しません。

配布アプリは [ZIP](https://github.com/opopoposiop/VvfM/releases/download/v0.58.18/VMD.Viewer.app.zip) からダウンロードできます。ZIPを展開してアプリを取り出し、[GUIDEの「導入と起動」](GUIDE.md#導入と起動) に従って起動してください。配布ファイル名は `VMD.Viewer.app.zip` です。過去の版やリリース情報は [Releases](https://github.com/opopoposiop/VvfM/releases) を参照してください。

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

- [一般ユーザーマニュアル](GUIDE.md)：操作手順、ショートカット、対応範囲,確認事項
- [FAQ](FAQ.md):困ったときに確認
- [更新履歴](CHANGELOG.md):アプリリリースバージョンの更新履歴
- [技術ガイド](VvfM_Technical_Note.md)：編集・描画・保存の仕組み、形式互換、性能の検証範囲
- スペックシート：[PDF](docs/spec-sheet/VMDViewer_SpecSheet_ja.pdf)／[Markdown](docs/spec-sheet/VMDViewer_SpecSheet_ja.md)。2026年10月28日・v0.57.22／build495基準
- [.fxdayo資料の案内](docs/fxdayo/README.md)：開発者向け解説、教材、対応条件と現行版との差分
- [ライセンス適用範囲](LICENSING.md)／[MIT原文](LICENSE)／[EULA日本語原本](Licenses/VMDViewer-EULA-ja.md)・[英訳](Licenses/VMDViewer-EULA-en.md)／[第三者通知](THIRD_PARTY_NOTICES.md)
- [Issues](https://github.com/opopoposiop/VvfM/issues)：不具合報告。アプリの版、Macの環境、操作手順、エラーを添えてください

## 謝辞

VMD Viewer for Macの開発にあたり技術的参考にさせていただきました お礼申し上げます

- [MikuMikuDance](https://sites.google.com/view/vpvp/?pli=1&authuser=0) 樋口M 様
- [MikuMikuDayo](https://github.com/pennennennennennenem/MikuMikuDayo) サンドマン 様
- [MikuMikuMoving](https://sites.google.com/site/mikumikumoving/) Mogg 様
- [PMXEditor](https://www.nicovideo.jp/watch/sm14024773) 極北P 様
- [AutoLuminous](https://www.nicovideo.jp/watch/sm19843111) そぼろ 様
- [msToonCoordinator](https://www.nicovideo.jp/watch/sm39850446) ましまし 様
- [ikHolographic](https://seiga.nicovideo.jp/seiga/im8315687) ikeno 様
- [LiteDOF HC](https://seiga.nicovideo.jp/seiga/im10818176) akeru 様
- [浅草みどり](https://www.nicovideo.jp/watch/sm36384153) / [水崎ツバメ](https://www.nicovideo.jp/watch/sm36519353) くれよん 様
