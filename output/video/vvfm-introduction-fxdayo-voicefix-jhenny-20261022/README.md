# VvfM紹介動画 — fxdayo表記・発音修正版

PMX 2.1のアプリ実画面版をもとに、字幕の「エフエックスダヨー」を「fxdayo」へ変更し、2分17秒付近の「床の反射」を「ゆかのはんしゃ（yuka no hansha）」と発声するよう修正しました。

- [修正箇所・13秒プレビュー（ナレーションのみ）](VvfM_fxdayo修正箇所_13秒プレビュー.mp4)
- [BGMあり・3分25秒・1080p MP4](VvfM_紹介動画_fxdayo修正版_3分25秒_BGMあり_1080p.mp4)（145.9 MB）
- [BGMなし・3分25秒・1080p MP4](VvfM_紹介動画_fxdayo修正版_3分25秒_BGMなし_1080p.mp4)（144.8 MB）
- [日本語字幕・41件](VvfM_紹介動画_fxdayo修正_日本語字幕.srt)
- [修正後の字幕画像](checks/final-frames/scene-10-at-134.png)
- [シナリオ](../../../docs/video/VvfM_紹介動画シナリオ_3分25秒_PMX21追加.md)
- [編集ソースと再生成手順](../../../docs/video/pmx21-3m25s/README.md)
- [完成MP4の検証結果](checks/delivery-validation.json)
- [音声差し替え範囲の検証](checks/fxdayo-correction-validation.json)

全編は205.000秒、1920×1080、24fps、4,920フレーム、AAC 48kHzステレオ、15チャプターです。両版の全編映像・音声デコード、字幕の原稿一致・非重複を確認しました。両版の映像ストリームは同一です。

差し替えは136.20–143.10秒。前後のナレーションとBGMあり音声はPCM単位で前版と一致し、BGM成分は全区間で保持しています。音声は同じHeyGen Jhennyです。元音声・前版の完成動画はそれぞれの制作フォルダに残しています。
