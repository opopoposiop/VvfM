# VvfM紹介動画 — PMX 2.1追加・3分25秒

QDEFのねじり比較とソフトボディの布・ロープ実演を、VMD Viewerのアプリ実画面で紹介する205秒の動画の編集用ソースです。日本語AIナレーションはHeyGen Jhennyを使用し、2026年10月23日版では場面11・12の2文に、保存済みJhenny音声を参照してローカルのQwen3-TTSで再合成した試聴済み音声を採用しています。BGMあり・なしの2版は同じ映像と字幕を使用します。

最新の2026年10月25日自然ナレーション版では、54秒付近の「腕」、1分45秒付近の「ToonShader HQ」、1分48秒付近の「リムライト」の3文を、元の同じ場面のJhenny音声を参照して読み直しました。前回のフラット化を外し、自然な抑揚を保った音声を、前後に合わせた音量で配置します。字幕の文字・時刻、映像、イラスト配置、BGM、全体205秒の時間割を維持しています。

- [3分25秒のシナリオ](../VvfM_紹介動画シナリオ_3分25秒_PMX21追加.md)
- [ナレーション全文と読みの指定](../VvfM_紹介動画_ナレーション全文_3分25秒.md)
- [日本語字幕・41件](captions-ja.srt)
- [場面と時間割](source/scenes.json)
- [映像のカット割り](source/edit-decision-list.json)
- [音声の配置](source/audio-alignment.json)
- [完成MP4の検証結果](checks/delivery-validation.json)
- [今回の音声差し替えと維持範囲](checks/natural-narration-validation.json)
- [今回の自然な抑揚と音量の計測](checks/natural-sentence-preparation.json)
- [今回の映像・字幕・イラストの維持検証](checks/natural-visual-preservation.json)
- [今回の23秒プレビュー検証](checks/natural-preview-validation.json)
- [完成音声の認識結果](checks/natural-final-transcripts.json)
- [ToonShader HQの字幕](images/toonshader-caption.png)
- [リムライトの字幕](images/rimlight-caption.png)
- [キャラクターイラストの配置](source/character-placement.json)
- [キャラクターイラストの生成原稿](source/imagegen-prompts.json)
- [締めイラスト追加の検証](checks/ending-illustration-validation.json)
- [締めイラストのプレビュー検証](checks/ending-preview-validation.json)
- [締めイラストの配置画像](images/ending-character-layout.png)
- [先行版・場面2のキャラクター追加の検証](checks/character-illustration-validation.json)
- [先行版・場面2のプレビュー検証](checks/character-preview-validation.json)
- [PMX 2.1のローカル再合成音声の採用・差し替え検証](checks/pmx21-local-voice-adoption-validation.json)
- [PMX 2.1修正箇所のプレビュー検証](checks/pmx21-preview-validation.json)
- [15〜20秒付近の一文読み直しの検証](checks/sentence-reread-validation.json)
- [fxdayoの発音・表記修正と差し替え範囲の検証](checks/fxdayo-correction-validation.json)
- [映像の変更箇所と音声・字幕の維持記録](source/video-reuse.json)
- [前段のアプリ実画面への変更検証](checks/appscreen-revision-validation.json)
- [全15場面の一覧](images/contact.jpg)
- [外部素材のハッシュ](media-manifest.json)

2026年10月22日の修正では、PMX 2.1の2場面をウインドウ全体の実画面に変更しました。さらに、場面10の字幕を「fxdayo」表記にし、「床の反射」を「ゆかのはんしゃ（yuka no hansha）」と発声するよう同じJhennyの音声で修正しました。

## 再構成の内容

| 時間 | 内容 |
|---|---|
| 02:40–02:48 | QDEF：BDEFと、ウェイト合計の異なるQDEFのねじり比較 |
| 02:48–02:58 | ソフトボディ：頂点固定の布、剛体アンカーの布、両端固定ロープ |

以前の `PMX21-App-Demo-Captions-23s.mp4` に使った元収録を再使用しました。QDEFは `shot-2.mov` の0–8秒、ソフトボディは `shot-1.mov` の0.15–10.15秒です。どちらもVMD Viewer v0.56.0 build376の実ウインドウ収録で、再生速度は1倍。タイトルバー・モデル一覧・再生操作部・タイムラインを含むウインドウ全体を表示します。説明は実画面の外に置き、アプリUIにはラベルを重ねません。

既存の場面04・05を各3秒、06を2秒、07・08・09を各1秒短縮しました。追加18秒と短縮11秒で、以前の198秒から205秒にしています。既存の台詞は保持しています。

収録時は4秒のVMD範囲をループ再生しています。これは選んだテストモデルの機能実演であり、MMDとの画像一致や再生性能の合格を示すものではありません。

## キャラクターイラストの追加（2026年10月24日）

場面2のアプリ画面を挟む左右の余白に、Codexの画像生成で制作した透過PNGのちびキャラクター2体を配置しました。左は赤茶色の片側に流した前髪・紫の制服・緑のネクタイ・紺のハイソックス、右は茶色の短髪・迷彩帽子・紫の制服など、本編に登場するPMXモデルの特徴を取り入れています。[完成動画の配置画像](images/character-layout.png)で確認できます。生成時の指定は [画像の生成原稿](source/imagegen-prompts.json) に記録しています。

場面2では、アプリ枠の横幅を1040pxへ調整し、左のノートPCの飾りを外しました。1920×1080の画面上で、キャラクターの表示枠は左が x=450・y=670、右が x=1730・y=670、いずれも160×260pxです。この配置は10月25日版でも維持します。透過PNG自体は加工せず、アルファ値8以上の領域を基準にCSSで表示位置と大きさを決めています。詳細は [配置記録](source/character-placement.json) を参照してください。

10月24日の追加は場面15（03:16〜03:25）です。同じPNG2体を再使用し、2体とも197〜197.5秒で表示します。表示枠は左が x=490・y=670、右が x=1730・y=670、いずれも160×260px。アプリ枠は x=664・横幅1040pxとし、実画面の縦横比を維持します。左のノートPCの飾りを外し、URL・字幕・アプリUIを避けて配置します。最後は場面全体の204.35〜205秒のフェードとともに消えます。画像の再生成やPNG自体の加工は行いません。

10月24日のイラスト追加版では前版のAAC音声をコピーし、音声ストリームの一致を確認しました。最新の10月25日版は3文の音声を変更するため、変更範囲外のPCMとBGM成分を維持したWAVからAACを再出力します。先行する発音修正は保持します。

## 発音と表記の修正

### 腕・ToonShader HQ・リムライト（2026年10月25日）

最新の自然ナレーション版は、次の3文を一文ずつ連続して再合成した音声です。同じ場面の元のJhenny音声を参照するローカルQwen3-TTSを使用し、音声の外部送信は行っていません。

- 腕の角度を少し変えて、お気に入りのポーズに。
- ToonShader HQでは、輪郭線や光を調整できます。
- リムライトで輪郭に光を、ブルームで輝きを。

前回の音高変動を35%に圧縮する処理は使わず、合成音声の自然な抑揚を保ちます。ピッチ変更や一文中の単語の切り貼りはありません。ToonShader HQの文は「トゥーンシェーダーエイチキューでは、りんかくせんやひかりをちょうせいできます。」という読みで再合成し、前後を含む音声認識でも「光」を確認しました。

音量は、完成動画と同じステレオ配置にしてから測定し、各文に一定のゲインを適用しています。腕は直後の文、ToonShader HQは元の同じ文、リムライトは前後の説明文に合わせています。ダイナミクスを圧縮する処理は加えていません。

| 対象 | 調整後WAVの配置 | 差し替え領域 | 音量（ステレオ） | 速度 |
|---|---|---|---|---|
| 腕の一文 | 54.56〜57.816333秒 | 54.18〜57.925秒 | -15.99 LUFS | 1倍 |
| ToonShader HQの一文 | 102.18〜105.7645秒 | 102.12〜105.90秒 | -16.87 LUFS | 1.08倍 |
| リムライトの一文 | 106.12〜109.467958秒 | 105.90〜109.55秒 | -16.81 LUFS | 1.10倍 |

速度調整は音高を保つ処理です。境界は無音に近い位置に置き、4msの短い接続処理を施しています。字幕全41件の文字と表示時刻は維持しています。差し替え領域外のナレーションとBGMあり音声はPCM単位で一致し、BGM成分は全区間で一致します。元の声との完全な同一性や、人が聴いた自然さの合格を断定するものではありません。完成動画から作る23秒プレビューで3文と前後のつながりを確認できます。

先行するフラット版の2文と字幕変更は、元の制作フォルダに保持しています。[先行版の変更記録](checks/flat-narration-validation.json)と[先行版の音高比較](checks/flat-pitch-comparison.json)は過去版の記録であり、最新の自然ナレーション版の処理ではありません。

### PMX 2.1の読み（2026年10月23日）

2分34秒・2分43秒付近の2文は、「PMX 2.1」を「ぴーえむえっくす　にーてん　いち」と発声する一文全体の再合成音声に差し替えています。保存済みJhenny音声を参照したローカルQwen3-TTSの候補を試聴後に採用したもので、元の声との同一性を断定するものではありません。

| 場面 | 採用した発声原稿 | WAV全長の配置 | 差し替え領域 |
|---|---|---|---|
| 11 | ぴーえむえっくす　にーてん　いちのモデルにも対応しています。 | 152.5925〜156.4325秒 | 152.55〜156.60秒 |
| 12 | ぴーえむえっくす　にーてん　いちのキューデフは、ねじったときの形を保つための変形方式です。 | 160.36〜167.24秒 | 160.35〜167.45秒 |

試聴済みWAVをそのまま使用し、再生速度は1倍、ピッチ変更は0です。字幕の文字・表示時刻と映像は変更せず、「あぷりじょう」と「ゆかのはんしゃ」の先行修正も維持します。適用処理は [apply_pmx21_pronunciation.py](source/apply_pmx21_pronunciation.py)、音声の採用・配置の検証記録は [pmx21-local-voice-adoption-validation.json](checks/pmx21-local-voice-adoption-validation.json) を参照してください。

### アプリ上・床の反射の読み（2026年10月22日）

15〜20秒付近の「PMXモデルとVMDモーションを読み込んで、アプリ上でリアルタイム再生。」を、同じHeyGen Jhennyで一文まとめて読み直しました。音声合成用の原稿は「ピーエムエックスモデルとブイエムディーモーションを読み込んで、あぷりじょうでリアルタイム再生。」です。字幕は従来の漢字・英字表記を維持しています。

新しい音声は約6.03秒。14.85〜20.98秒の範囲を差し替え、既存字幕の表示時間内に配置しています。再生速度はピッチを維持した1.04倍で、一文の途中の音声接合やピッチ補正はありません。以前の「あぷりじょう」だけの差し替え・音高調整は、この連続した一文の音声で置き換えています。範囲外のナレーション・BGMあり音声はPCM単位で一致し、BGM成分も全区間で維持しています。

[読み直し音声の認識結果](checks/sentence-reread-transcript.json)と[前後を含む14秒区間の認識結果](checks/sentence-reread-preview-transcript.json)で、台詞と時刻を照合しています。

場面10の字幕は「対応するfxdayoで、ステージの演出も。」です。[該当フレーム](images/fxdayo-caption.jpg)で確認できます。「床の反射」は漢字表記を維持し、発声用の原稿は「ゆかのはんしゃ」です。この先行修正は今回も維持しています。

## 完成品と素材の扱い

完成MP4、元収録、ナレーションWAVはGitに含めていません。最新のローカル制作フォルダは、リポジトリからの相対パスで `output/video/vvfm-introduction-natural-narration-20261025/` です。先行するフラット版 `output/video/vvfm-introduction-flat-narration-20261025/` も保持しています。直前の締めイラスト版 `output/video/vvfm-introduction-character-ending-20261024/` も保持しています。先行する場面2のイラスト版 `output/video/vvfm-introduction-character-illustrations-20261024/`、発音修正版 `output/video/vvfm-introduction-pmx21-pronunciation-final-20261023/`、一文読み直し版 `output/video/vvfm-introduction-sentence-reread-jhenny-20261022/` も保持しています。

完成ファイル名：

- `VvfM_紹介動画_自然ナレーション版_3分25秒_BGMあり_1080p.mp4`
- `VvfM_紹介動画_自然ナレーション版_3分25秒_BGMなし_1080p.mp4`
- 修正箇所の23秒プレビュー：`VvfM_腕とToonShader_自然ナレーション_23秒プレビュー.mp4`

ここにあるソースの再生成には、`media-manifest.json` に記録したローカル素材が必要です。最新の素材には、既存のキャラクターPNGと音声に加え、調整済みの3文、同じ場面の参照音声、変更前のWAV、差し替え済みのBGMあり・なしWAVを含みます。APIキー、認証情報、音声生成サービスの応答URLは保存していません。保存済み画像・音声を使用するため、再生成で画像・音声生成APIを呼ぶ必要はありません。

## ローカルでの再生成

macOS、Python 3.12＋NumPy・Pillow、HomebrewのFFmpeg／FFprobe、Node.jsを使用します。HyperFramesは0.7.71に固定しています。このディレクトリで実行してください。

```sh
python3 stage_media.py --from-directory ../../../output/video/vvfm-introduction-natural-narration-20261025 --check-only
python3 stage_media.py --from-directory ../../../output/video/vvfm-introduction-natural-narration-20261025
python3 source/build_composition.py
npx --yes hyperframes@0.7.71 check composition --at 55.5,104,108,18,201 --snapshots
npx --yes hyperframes@0.7.71 render composition --output final-render.mp4 --fps 24 --quality high --workers 4 --video-frame-format png --experimental-fast-capture=false --strict
python3 source/finalize_delivery.py
```

`stage_media.py` は素材のSHA-256を照合してからコピーします。最新の `finalize_delivery.py` は差し替え済みWAVをAAC 192 kbpsへ変換して完成MP4へ格納します。既存の完成MP4は上書きしません。過去の発音修正と今回の3文は保存済み音声へ反映済みのため、上記の再生成で音声生成や差し替え処理を再実行する必要はありません。`apply_natural_narration.py` は保存済みの変更前WAVと調整済み3文から差し替えを再現するための記録です。

## 検証範囲

最新の10月25日自然ナレーション版の完成音声：BGMあり -16.82 LUFS・-4.40 dBTP / BGMなし -16.06 LUFS・-4.69 dBTP。

今回の変更は3文の音声です。既存の映像をそのまま使用し、前版との映像ストリーム一致、字幕・全タイムライン・イラストの同一性を確認しています。3文の前後を含む音声認識、音高、ステレオ音量、接合境界を計測しました。両版とも205秒・1920×1080・24fps・4,920フレーム・AAC 48kHzステレオで、全編デコードを通過しています。完成MP4から53〜62秒・99〜113秒を続けた23秒プレビューも全編デコード済みです。AAC音声から切り出した2区間を自動音声認識で再確認しています。

先行する10月25日フラット版の表示検査は、レイアウト・ランタイム・モーションのエラー0、コントラスト44/44件でした。今回は映像を再描画せず、その同じ映像を使用しています。

先行する2026年10月24日締めイラスト追加版は、場面15への追加と配置調整です。BGMあり・なしの再出力と検証を完了しました。確認時刻は18秒（場面2の維持）、196.9秒（登場前）、197秒（登場開始）、197.5秒（登場完了）、201秒（アプリ映像への切替後）、204.6秒（最後のフェード中）です。最新の配置と維持範囲は [締めイラスト追加の検証](checks/ending-illustration-validation.json)、8秒区間は [プレビュー検証](checks/ending-preview-validation.json)、配置画像は [ending-character-layout.png](images/ending-character-layout.png) に記録しています。当時の完成MP4は元の制作フォルダに保持しています。レイアウト・ランタイム・モーションのエラーは0、文字コントラスト43件はすべて通過しました。同じPNG2点を2場面で使う重複素材の警告1件は、時刻を持たない装飾画像の意図した再利用と確認しています。

先行する10月24日の場面2イラスト版では、18秒・24秒の静止画で2体の全身が見え、説明文・アプリUI・字幕を隠していないことを確認済みです。この先行版の記録は [キャラクター追加の検証](checks/character-illustration-validation.json) と [プレビュー検証](checks/character-preview-validation.json) を参照してください。これらは場面15の追加後の合格記録ではありません。

2026年10月23日の変更は2文の音声のみでした。映像・字幕を再描画せず、既存の `final-render.mp4` と修正音声から完成MP4を再出力しています。この先行版の音声配置・差し替え領域外の維持は [採用音声の検証記録](checks/pmx21-local-voice-adoption-validation.json)、修正箇所の確認は [発音修正のプレビュー検証記録](checks/pmx21-preview-validation.json) を参照してください。

先行する2026年10月24日締めイラスト追加版は205秒、1920×1080、24fps、4,920フレーム、AAC 48kHzステレオです。BGMあり・なしの2版それぞれを全編デコードし、映像ストリーム一致、字幕41件の原文一致・時刻・非重複、音声と映像の長さを確認しました。両方の音声ストリームは前の場面2イラスト版と圧縮データのSHA-256が一致し、10月23日の発音修正済み音声を保持しています。

この10月24日版の音声ラウドネスはBGMあり −16.80 LUFS、BGMなし −16.02 LUFS、トゥルーピークはそれぞれ −5.15 dBTP、−5.54 dBTPです。場面15の追加後も、完成音声は先行版と全区間で一致しています。

先行版の修正字幕とPMX 2.1部分の5時刻の表示検査では、レイアウト・ランタイム・モーションのエラーは0、文字コントラスト46件はすべて検査を通過しました。fxdayo字幕の画像を確認し、差し替え後の13秒区間は自動音声認識でも台詞を照合しています。10月23日に差し替えた2文の候補音声は試聴後に採用されていますが、人が全編を実聴・実視聴したという確認は含みません。
