# build409 通常GUI検証

> 開発元の2026-10-07時点の記録を転載しています。本文の実装・検証・Releaseは開発元での結果であり、VvfMへの文書取込時には再実施していません。生ログなどの`evidence/`資料は開発元ローカルにあり、本リポジトリには収録していません。[取込情報](../../docs/fxdayo/README.md#取込情報)

2026-10-07、macOS 27.0.1。署名・UUIDを照合したRelease本体をLaunchServicesの`open -na`で起動。PID 69124の実行パスを確認し、アプリ自身の診断はこのプロセスにだけ環境変数で指定した。既存Viewerは起動していなかった。制限付きshellの最初の`open`は`kLSNoExecutableErr`、許可済みLaunchServices呼出しで起動できた。本体実行ファイルの欠損とは判断しない。

生成教材だけを使った`dist/fxdayo-interface-v05620-validation/authoring-color.vmdviewer`を開き、既存「エフェクト → 読込状況」を操作した。

| 操作 | 確認結果 |
|---|---|
| project読込と動作モード | 原文・6依存ファイル・color profileを復元。既存アプリ設定はRealTimeだったため理由付きfailedを表示。設定→再生でFrameTimeへ変更するとactiveへ移行 |
| 再検査 | 「検査完了。採用中の版は変更していません」を実画面で確認 |
| 別の原文選択 | 生成した2倍露出版を指定。「新版の表示を確認し、適用しました」と新source SHAを確認。compilerだけの成功表示とは区別 |
| 不正な原文 | `Broken.fxdayo`を指定。`FXD-COMPILER-FAILED [compile] Exposure/vert`、`source/Broken.fxdayo:45:19`と未定義識別子を表示 |
| 失敗後の保持 | 編集対象はBroken、runtimeは採用済みExposureDemo。画面と保存診断の採用SHAは`282bacf1bbe7f43d111adc1961ebb37d730915a24b91979fb56aa83474013505` |
| 診断を保存 | GUIの保存panelからJSONを保存。source位置、編集原文SHA、request／attachment、採用program identityを含む。実ファイル（開発元ローカル資料: `evidence/gui-compile-failure.json`） |
| projectを別名保存 | `gui-editable/gui-authoring.vmdviewer`を保存。ZIPを読み、manifest schema26／minimumReader26、package2／color profile、採用sourceのSHA一致を確認。Brokenは保存されていない |
| 最大化 | 再生中にnative zoomを実行。エフェクトwindowを開閉し、一時停止ボタンとframe 19→36の進行を確認 |
| native全画面 | 全画面に移行してエフェクトwindowを開閉。復帰後のSpaceで一時停止できることを確認 |
| UI非表示全画面 | 表示切替まで確認したが、Windowメニューのエフェクト項目で操作ツールが無効elementを報告し、画像取得も不可。この条件の作者UI受入は未確認 |
| 終了 | メニューのCancel actionで設定画面の観測が回復。変更した動作モードを元のRealTimeへ戻して選択状態を確認し、⌘Qで通常終了。PID消滅を照合 |

保存・診断panelはViewerを所有元とするsheetとして操作できた。通常／最大化／native全画面の対象window開閉と入力復帰を確認したが、常時のwindow重なり順・screen ID・全Space組合せ・複数画面を計測したものではない。人による実マウスdragとVoiceOverも未検証。取得AXテキストの一部が更新前の値を含んだため、採用結果は実画面と書き出したJSON／ZIPでも照合した。

compiler失敗の診断内profileは新規原文の初期compile契約`scene.v1`、採用program identityは前回版の`color.v1`。新規原文はcompileとreflectionが成功してからcolorへ選択されるため、失敗した編集版と採用中programの情報を混同しない。

## 実表示に関する留保

Release起動時にはRealTimeの不足理由とzero-present退役の記録が出た。FrameTimeへ変更後、表示完了を条件とする原文採用と通常再生を確認した。実表示診断は失敗・復旧を中心に出力するもので、全frameのpositive timestamp集計ではない。

別のSwiftテスト実行ではresize zero-present注入試験が通過した一方、その後はGUI2件の初回actual-presentがtimeoutし、単独再試行でも全1,909 callbackの時刻が0だった。test hostのregular activation policyとfinishLaunchingを追加した後は、単独2件が9.742秒で通過。全体実行で残った寸法不一致は、取得済みの画面倍率2に対して描画時は1となり、期待1024×512に対し512×256だった。現在のbacking scaleでfixture寸法を保つよう修正し、全体実行中のGUI2件も再通過した。いずれもテスト側の修正で、Release本体や正のactual-present条件は変えていない。

過去の失敗は削除せず、初回表示timeout（開発元ローカル資料: `evidence/gui-harness-timeouts.txt`）、倍率による寸法不一致（開発元ローカル資料: `evidence/gui-harness-scale-failure.txt`）、AppKit初期化後の単独通過（開発元ローカル資料: `evidence/gui-tests-launched.log`）を保持する。最終全体件数は[実装記録](IMPLEMENTATION.md)を参照する。

全画面メニュー操作時のPIDは生存し、短いstack sampleではmain threadはAppKitのevent待ちだった。メニューCancelで観測を回復し通常終了できた。観測ツールの失敗だけから本体クラッシュ・deadlockとは判断しない。

機械記録はGUI要約（開発元ローカル資料: `evidence/gui-summary.json`）、window通知（開発元ローカル資料: `evidence/gui-window.jsonl`）、実表示診断抜粋（開発元ローカル資料: `evidence/gui-presentation-excerpts.txt`）。大きいrawログとstack sampleはローカル`dist/fxdayo-interface-v05620-validation/gui-evidence/`に保持する。projectを移動し元原文をなくした復元、snapshot書出し、取消の詳細は関連API／統合テストの証拠であり、今回の通常Release GUI操作では再実施していない。
