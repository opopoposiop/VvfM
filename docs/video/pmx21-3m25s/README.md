# VvfM紹介動画 — PMX 2.1追加・3分25秒

QDEFのねじり比較とソフトボディの布・ロープ実演を加えた、205秒の紹介動画の編集用ソースです。日本語AIナレーションはHeyGen Jhenny。BGMあり・なしの2版は同じ映像と字幕を使用します。

- [3分25秒のシナリオ](../VvfM_紹介動画シナリオ_3分25秒_PMX21追加.md)
- [日本語字幕・41件](captions-ja.srt)
- [場面と時間割](source/scenes.json)
- [映像のカット割り](source/edit-decision-list.json)
- [音声の配置](source/audio-alignment.json)
- [完成MP4の検証結果](checks/delivery-validation.json)
- [全15場面の一覧](images/contact.jpg)
- [外部素材のハッシュ](media-manifest.json)

## 再構成の内容

| 時間 | 内容 |
|---|---|
| 02:40–02:48 | QDEF：BDEFと、ウェイト合計の異なるQDEFのねじり比較 |
| 02:48–02:58 | ソフトボディ：頂点固定の布、剛体アンカーの布、両端固定ロープ |

以前の `PMX21-App-Demo-Captions-23s.mp4` に使った元収録を再使用しました。QDEFは `shot-2.mov` の0–8秒、ソフトボディは `shot-1.mov` の0.15–10.15秒です。どちらもVMD Viewer v0.56.0 build376の実ウインドウ収録で、再生速度は1倍。表示範囲をトリミングし、今回の画面デザインに合わせたラベルを重ねています。

既存の場面04・05を各3秒、06を2秒、07・08・09を各1秒短縮しました。追加18秒と短縮11秒で、以前の198秒から205秒にしています。既存の台詞は保持しています。

収録時は4秒のVMD範囲をループ再生しています。これは選んだテストモデルの機能実演であり、MMDとの画像一致や再生性能の合格を示すものではありません。

## 完成品と素材の扱い

完成MP4、元収録、ナレーションWAVはGitに含めていません。ローカルの制作フォルダは、リポジトリからの相対パスで `output/video/vvfm-introduction-pmx21-jhenny-20261022/` です。

完成ファイル名：

- `VvfM_紹介動画_PMX21追加_3分25秒_BGMあり_1080p.mp4`
- `VvfM_紹介動画_PMX21追加_3分25秒_BGMなし_1080p.mp4`

ここにあるソースの再生成には、`media-manifest.json` に記録したローカル素材が必要です。APIキー、認証情報、音声生成サービスの応答URLは保存していません。保存済み音声を使用するため、再編集で音声APIを呼ぶ必要はありません。

## ローカルでの再生成

macOS、Python 3＋NumPy・Pillow、HomebrewのFFmpeg／FFprobe、Node.jsを使用します。HyperFramesは0.7.71に固定しています。このディレクトリで実行してください。

```sh
python3 stage_media.py --from-directory ../../../output/video/vvfm-introduction-pmx21-jhenny-20261022 --check-only
python3 stage_media.py --from-directory ../../../output/video/vvfm-introduction-pmx21-jhenny-20261022
python3 source/prepare_reconstruction_audio.py
python3 source/create_bgm.py
python3 source/mix_audio.py
python3 source/build_composition.py
npx --yes hyperframes@0.7.71 check composition --at 52,83,165,174,201
npx --yes hyperframes@0.7.71 render composition --output final-render.mp4 --fps 24 --quality high --workers 4 --video-frame-format png --experimental-fast-capture=false --strict
python3 source/finalize_delivery.py
```

`stage_media.py` は素材のSHA-256を照合してからコピーします。`finalize_delivery.py` は既存の完成MP4を上書きしません。

## 検証範囲

完成品は205秒、1920×1080、24fps、4,920フレーム、AAC 48kHzステレオです。2版それぞれを全編デコードし、映像ストリームの一致、字幕41件の原文一致・時刻・非重複、音声と映像の長さを確認しました。検査の数値は上記の検証JSONに記録しています。

音声の実測値は、BGMあり版が −16.78 LUFS／−5.16 dBTP、BGMなし版が −16.01 LUFS／−5.54 dBTPでした。

代表時刻の表示検査では、レイアウト・ランタイム・モーションのエラーは0、最終5時刻の文字コントラスト54件はすべて検査を通過しました。自動音声認識による台詞の照合も行っています。人が全編を実聴・実視聴したという確認は含みません。
