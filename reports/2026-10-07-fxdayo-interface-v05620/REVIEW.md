# v0.56.20 Astraレビュー

> 開発元の2026-10-07時点の記録を転載しています。本文の実装・検証・Releaseは開発元での結果であり、VvfMへの文書取込時には再実施していません。生ログなどの`evidence/`資料は開発元ローカルにあり、本リポジトリには収録していません。[取込情報](../../docs/fxdayo/README.md#取込情報)

2026-10-07。同じチャットのAstraが実装と自己レビューを行った。独立した第二者レビューではなく、サブエージェントは使用していない。対象はインターフェイス計画のP0・P1と、それに接続する通常load、live、保存復元、export。

## 修正した指摘

| 指摘 | 対応・根拠 |
|---|---|
| 相対path中の`..`を文字列APIだけでは正規化できず、root内の正当な依存も拒否 | namespace内のsegment stackで正規化。root内親参照、脱出拒否、生成codeのincludeを試験 |
| CRLF原文と抽出HLSLの位置がずれる | 改行正規化とsource map、原文と生成codeの位置を分離 |
| 条件付き初期化のないreadと、旧scene-v1の循環履歴を同一視 | SPIR-Vの実resource accessをordered planで追跡。初回0の循環履歴は限定条件と診断を設け、欠けた条件付きinitializerは拒否。元MotionBlurのPreVPをGPUで再確認 |
| resizeで絶対寸法の履歴bufferまで失う | geometry/frameの前回値とresource内容の継承条件を分離。同じshapeのみ保持 |
| 別の編集sourceが失敗すると再試行が採用版を向く | 編集source/root/intentをsession状態として保持。保存/exportは採用版を使う |
| package1のhash対象外のfile kindが検査条件を変更し得る | package1の未認証kindを拒否し、package2で型とbytesを認証。旧schema25/package1復元も試験 |
| Metal pipeline準備がcompiler同時実行枠から外れる | 同じ枠へ接続。同期Metal API内部を強制中断できない点は能力APIとガイドへ明記 |
| 表示適用待ちの取消がrollback後に「失敗」と記録される | 先に取消状態を確定し、rollbackの障害診断を追加しない。表示前取消、旧identity復元、rollback表示後の状態を試験 |
| 新requestより古いcompletionが遅れて到着する | request ID照合とjob取消を保持。旧失敗requestを新しい再検査が追い越すケースを試験 |
| resizeのzero-present後にsource programのpreview proofを再利用して待機が解消しない | 実表示診断でresize段階・positive actual-present欠落を再現。正しいDayo leaseの候補を退役させ、既存の世代／owner検査を保った新しいpreview proofの再取得へ接続 |
| live試験が旧寸法の遅着表示を拾い得る | 可視のresizable windowとCore Animation反映を固定。zero-present注入後の退役数と新寸法のcommitted frameの両方を待ち、古いactual-presentを成功へ数えない |
| GUI test hostが通常AppKitの起動処理を完了していない | opt-inのGUI試験に限りregular activation policyと一度だけのfinishLaunchingを追加。単独2件は正の実表示・reloadを含め9.742秒で通過。製品側の表示成功条件は変えない |
| ウインドウ配置後の画面倍率が取得済み倍率と異なり、fixtureが1024×512の代わりに512×256になる | 中央配置後に寸法を設定し、draw時の実際のbacking scaleで所定pixel寸法を維持。初回も新しい表示journalの幅・高さ両方を要求。画面倍率の差をshader失敗と混同しない |
| 全体テスト2件が旧minimum reader値17/19を要求 | nativeを含む実行選択保存はschema26を要するため期待値を更新。reader floorを下げて黙って選択を失う対応はしない |

## 残る境界

resource検査はresource単位であり、全要素の書込みやデータ競合、任意shaderの終了を証明しない。1 GiB予算はsource effectが保持するtracked GPU資源に適用し、Viewer全体やdriverの総メモリ上限ではない。Metal同期APIの内部待機中にjobの期限で強制中断することはできない。これらを万能なsandboxとして表示しない。

新profileの不透明出力、HQ Toon・FrameTime、AA/DoF/Bloom/Diffusionなし、native混在不可、scene-v1のcompute倍数条件を維持した。P2/P3、独立temporal profile、端数dispatchを実装済みへ変更しない。

## 検証に残る指摘

zero-present注入を含む関連8件が通過した後に生じたGUI2件の初回表示timeoutは、test hostのAppKit初期化を追加して再検証した。単独2件が通過し、全体実行で残った画面倍率由来の寸法不一致も上表の修正後にGUI2件が通過した。最終全体件数と過去の失敗証拠は実装記録へ分ける。Release本体はその前後で同一の817入力・実行物であり、通常GUIの採用・失敗保持・保存も確認済み。

ReleaseのUI非表示全画面ではメニュー項目の操作が無効になり、画像も取得できなかった。メニューのCancel actionで観測は回復し、設定復元と通常終了まで実施した。本体クラッシュの証拠ではなく、この条件でのエフェクトwindowの前面・同一画面・focusは未検証。VoiceOverについても、画面更新後に取得AXテキストの一部が古い値を含んだため受入しない。

[実装・検証](IMPLEMENTATION.md)／[Release](RELEASE.md)／[GUI](GUI.md)
