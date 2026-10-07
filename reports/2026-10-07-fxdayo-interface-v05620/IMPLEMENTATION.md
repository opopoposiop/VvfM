# v0.56.20 .fxdayo作者向けインターフェイス

> 開発元の2026-10-07時点の記録を転載しています。本文の実装・検証・Releaseは開発元での結果であり、VvfMへの文書取込時には再実施していません。生ログなどの`evidence/`資料は開発元ローカルにあり、本リポジトリには収録していません。[取込情報](../../docs/fxdayo/README.md#取込情報)

2026-10-07。`docs/fxdayo/INTERFACE_PLAN.md`のP0・P1を対象とする。P2・P3は今回の対象外。基準は`codex/pmxchange`、HEAD `16e20241e84755c78cb180b3e1f190dc7c73bfaa`。同じチャットのAstraで実装・自己レビューし、サブエージェントは使用しない。commit／pushは行っていない。

## 実装

- `FxDayoRuntimeService`に能力照会、immutableな検査結果、取消付きcompile、scene／寸法preflightをまとめた。専用native adapterのterminal拒否を先行させ、明示source指定の失敗をnativeへ退避しない。
- 条件配列をANDへ修正。全条件を解析し、空配列と式内ORを区別する。未供給OnLoadSkyboxを条件式と実参照から拒否する。
- 最後に確定したcontextからload、session開始、play/stop、resizeを判定。seekではframe差分とgeometryをリセットし、同一programの同じ寸法の資源内容を保持する。resizeでも絶対寸法buffer等の内容を引き継ぐ。
- 原文・include・Jsonnet import/importstr/importbinを型付きpackage2へ固定。明示root内の親参照と生成codeのincludeを捕捉し、絶対path・root脱出・衝突を拒否。旧package1の未認証メタデータで依存検査を迂回させない。
- 実compiler／dylib、SDK bytes、options、ABI、profileとpackageをcache identityへ含める。子processの取消・終了確認、1実行＋4待機、120秒の期限、子RSS監視1 GiB、workspace96 MiBを設ける。同期Metal APIは復帰後に取消・期限を再確認する。
- SPIR-Vのresource accessと定義順から未初期化read、RTV feedbackを検査。scene-v1の既存初期値として、後段の無条件writerへ循環する履歴資源は初回0で開始し診断へ明示する。resource単位の検査であり、全要素書込みや任意shaderの停止性の証明ではない。
- 全source attachmentの候補・確定履歴・GPU退役待ちを共通1 GiB予算で管理する。Viewer全体のHDR資源、pipeline、driverの総メモリ上限ではない。
- `dayo130.hdr-color.v1`では未使用のscene geometryを生成しない。self float controller、ScreenTextureと限定camera/frame入力を許可し、PMX alpha材質を受け入れる。AA/DoF/Bloom/Diffusionやnative混在、不透明出力など共通条件は保持する。
- 既存エフェクト読込状況へ方式選択、再検査、再読込・取消、原文／root選択、snapshot・診断書出しを追加。編集対象と採用版を分け、失敗後の再試行でも編集対象を保持する。
- reloadは既存モデル差替えtransactionへ接続し、現在frameの再評価、GPU成功、正のactual-present後に確定する。必要な物理は0起点で再評価する。編集中の未登録値を拒否し、失敗・取消では前回版へ戻す。
- resizeでzero-presentとなった原文候補は、renderer UUID・attempt一致を確認して退役し、新しいpreview proofで再試行する。未表示候補を履歴へcommitしない。
- project schema26へ実行選択・新profile・package2を保存。旧schema25/package1は読み続け、保存／exportは採用済みbytesを使用する。

## 検証記録

最終全テストは2,538件中、実通過2,489・条件付きskip49・失敗0（16 suite、170.344秒）。集計（開発元ローカル資料: `evidence/test-summary.json`）／ログ（開発元ローカル資料: `evidence/full-tests-gui.log`）。元MotionBlurとcompilerを指定し、通常GPU・原文変更・1080p作例・project・短尺exportに加え、`VMD_FXDAYO_GUI=1`で実表示・作者操作の2件も含む。素材未指定・性能・別機能のopt-in等の49 skipは成功に数えない。先行するGUI無効の標準実行は2,487通過／51skip／失敗0で、旧集計（開発元ローカル資料: `evidence/standard-test-summary.json`）とログ（開発元ローカル資料: `evidence/full-tests.log`）を保持する。

| 試験 | 結果 |
|---|---|
| 関連25件（phase10） | 25通過、skip0、失敗0。84.533秒 |
| ガイド3作例・1920×1080 | 原文からcompileしてHDR全画素を比較。単純2倍は最大差0、controller -1は0.00012207031、0/0.5/1/2は0、2パスは0.0009278059。許容0.006未満 |
| 配列ANDのGPU真偽表 | 4組の条件、実行pass列、bufferから得たR=1/3を確認。初期化pass欠落は拒否 |
| 依存・cache | importstr/importbin、明示root内の親参照、生成include、include変更でidentity/MSL変化、元folder削除後のuncached再compile |
| scene入力省略 | 1080pのcolor export、alpha=0.5材質、GBuffer読戻しなし・geometry=nil。透明出力は拒否 |
| live統合 | 実NSWindowとMetalRendererのactual-presentでplay/pause/seek/resize。関連8件の通過後、test hostと画面倍率を修正した最終全体実行でも通過。resize時のzero-present注入→候補退役→新寸法のpositive actual-presentを確認 |
| authoring | 最終全体実行で成功reload、別編集sourceのcompile失敗、変換／表示待ち取消、最新request優先、採用版保持、project移動・元folder削除、cacheを使わない再生成、採用版のexportを確認 |
| 旧project | schema25/package1とsource intentを実復元 |
| 動画 | 2個体の独立buffer、6frameのH.264、各PTS、失敗時の既存出力保持 |
| Release build409 | strict署名、817入力の指紋、実行物とdSYMのUUID、同梱schema一致。通常LaunchServices起動と同梱compilerの再検査・再読込を確認 |
| Release作者UI | 正常原文の採用完了、故障原文の45行目診断、前回採用版保持、診断JSON保存、project別名保存と格納sourceのSHA一致を確認。[GUI記録](GUI.md) |

追加GUIテストの経緯: 関連8件の成功後、全体GUI実行で初回actual-present待ちの2件失敗（196.466秒）、単独再試行でも2件失敗（35.788秒、観測1,909 callbackすべて時刻0）があった。test hostにregular activation policyと一度だけのfinishLaunchingを追加すると単独2件が9.742秒で通過した。次の全体実行で残った1テスト・2 issueは、画面倍率が変わって期待1024×512に対し実寸512×256だったため。現在のbacking scaleでfixture寸法を保ち、初回とresize後の幅・高さを厳密に待つよう修正した最終全体実行ではGUI2件を含め失敗0。製品側の正のactual-present要件とRelease本体は変更していない。最初の成功（開発元ローカル資料: `evidence/zero-present-recovery.log`）／初回表示timeout（開発元ローカル資料: `evidence/gui-harness-timeouts.txt`）／倍率不一致（開発元ローカル資料: `evidence/gui-harness-scale-failure.txt`）／AppKit初期化後（開発元ローカル資料: `evidence/gui-tests-launched.log`）。通常ReleaseのGUI操作は別途確認し、未実施の条件は[GUI記録](GUI.md)へ残す。

初回の資源検査はMotionBlurのPreVPを未初期化として拒否した。この開発中の失敗を、scene-v1の循環履歴の初期値とresize保持条件を明示して修正し、phase9・10で既存経路を再確認した。

ローカル検証成果物は`dist/fxdayo-interface-v05620-validation/`。`authoring-color.vmdviewer`、`release-controller.vmdviewer`、`two-models-two-programs.png`、`generic-source-two-instances.mp4`を保持する。`preserved-on-failure.mp4`はatomic失敗テスト用の文字列sentinelで、動画ではない。

## 制限と未検証

Windows版Dayo 1.30アプリの実行・同条件画像比較、全素材、全OS／複数画面、GPU faultの実機注入、正式性能matrix、600秒耐久は未検証。`performanceAccepted=false`。

computeは全passでthreadgroupの倍数を要求し、原文へguardを自動挿入しない。元MotionBlurの1080p／4K受入とは、color作例の1080p成功を区別する。任意HLSL、DXR、deform/render category、外部画像、copy/clear/mipmap pass、独立temporal profileは未対応。

[作者ガイド](../../docs/fxdayo/FXDAYO_DEVELOPER_GUIDE.md)／[計画と採用範囲](../../docs/fxdayo/INTERFACE_PLAN.md)／[レビュー](REVIEW.md)／[Release](RELEASE.md)／[GUI](GUI.md)
