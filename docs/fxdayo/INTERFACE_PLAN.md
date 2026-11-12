# 未知の.fxdayoを受け入れるインターフェイス改修計画

> VvfM収録注（2026-10-19）：開発版v0.56.49／build453（記録ID `3620662`）から取り込みました。本文は初期P0〜P3案とv0.56.42の採用範囲を含む計画資料です。骨・別個体controllerの後続対応など、現在の採否は[資料の案内](README.md)を参照してください。本取り込みではビルド・実機試験を再実施していません。


VMD Viewerが、名前やSHAを事前登録していない`.fxdayo`を、宣言された機能と実際のscene条件から受け入れられるようにする。受入理由と拒否理由を作者へ返し、原文変更、再読み込み、project保存、live、動画出力まで同じ実行契約を保持する。

2026-10-06時点では`dayo130.hdr-scene.v1`のcompilerとexecutorが既に通常経路へ接続されている。本計画はそれを基礎とした仕様の明確化と拡張であり、汎用runtimeを一から作る計画ではない。初稿は文書化と静的照合のみだったが、その後の依頼によりv0.56.20ではP0・P1を実装対象とした。以下の詳細設計は初稿の検討経緯も含む。採用範囲は次節、当時の検証条件と未確認範囲は本書の検証概要に記す。

作者の記述手順と現行の制約は[技術解説書](FXDAYO_DEVELOPER_GUIDE.md)、参照ファイルのhashは[調査snapshot](SOURCE_SNAPSHOT.json)を正本とする。

## v0.56.42の追加範囲

限定原文runtimeの拡張として、R0の20原文診断、R1の共通定義・能力分析、R2の色契約と保存、R3のtexture資源操作を通常live/exportへ接続した。追加profileは`dayo130.postprocess.v2`／`dayo130.color.v2`。self bool/intとlocal 3D texture primitiveも含むが、骨・外部個体、共有simulation、端数dispatch、混在描画の契約は未成立のため拒否を維持する。これは限定profileでの対応であり、以下の旧P2/P3案全体の完成とは扱わない。

## v0.56.20の採用範囲

| 対象 | 実装と境界 |
|---|---|
| P0 | 条件配列AND、未供給OnLoadSkybox参照の拒否、[構造schema](definition.schema.json)と能力API、段階別診断、明示的な実行方式と単一owner |
| P1 API・作者UI | `FxDayoRuntimeService.inspect/compile/preflight`、取消job、既存読込状況UIの再検査・再読込・原文/root選択・snapshot書き出し・診断JSON |
| P1 原文と保存 | 型付き依存package2、root内正規化、生成codeのinclude捕捉、実compiler bytesとoptionsを含むcache identity、schema26の実行選択。旧schema25/package1を読む |
| P1 実行・資源 | load/start/resize/seekの区別、resourceアクセス計画、初期化とtexture feedback検査、source effect群1 GiBの資源予算。GPU/actual-present後の採用 |
| P1 color | `dayo130.hdr-color.v1`。履歴・scene資源を使わない画面加工ではGBufferを作らず、PMX alpha材質を許可。不透明出力など共通条件は保持 |
| 継続する制約 | computeは全passでthreadgroupの倍数を要求。shaderを書き換えず、端数dispatchは未採用。scene profileはv1の互換修正として記録 |
| 今回の対象外 | P2、P3、作者manifest、独立temporal profile、shader停止性の証明、Windows Dayo実行・画像完全一致、正式性能受入 |

擬似APIの`makeSession`は新たな並行ownerを作らず、既存`MetalFxDayoExecutor`とlive/export各自の`DayoFrameHistory`へ統合した。reloadは既存のモデル差し替えtransactionを利用し、未登録編集を拒否、現在frameの物理再評価、失敗時rollback、再生再開までつなぐ。コンパイル成功のみでは適用完了としない。

予算は1job 120秒、同時1・待機4、子process RSS監視1 GiB、入力込みworkspace96 MiB、source effect群のGPU資源1 GiB。Viewer全体のRSS・driverメモリや任意shaderの実行時間を保証する上限ではない。検証の通過数・条件・残る未確認は実装記録を正本とする。

## 受入の定義

「未知の汎用`.fxdayo`を受け入れる」は、対象profile内で次の条件をすべて満たすことと定義する。

1. 新しいファイル名、SHA、pass/resource名に対し、Viewerの再buildや個別adapter追加なしで判定・コンパイル・実行できる。
2. 許可範囲内のHLSLの式変更が出力へ反映される。似たnative effectへの置換を原文実行と表示しない。
3. 必要なpass、controller、入力、資源、時刻の意味をすべて満たすか、不足を理由付きで拒否する。対応するパスだけを抜き出して成功扱いにしない。
4. liveとexportを独立に判定し、同じ原文packageと確定した入力契約を使う。
5. 保存・移動・再起動後も実行方式とsource bytesを保持し、旧版readerで機能を黙って落とさない。

任意のHLSL、Dayo renderer全体、DXR、任意の計算時間、画像完全一致はこの定義に含めない。対応範囲を名前のallow-listから版付きの機能契約へ移すことが目的である。

## 初稿時点の実装と不足（2026-10-06）

| 層 | 現行コードで確認できる到達点 | 次に整備する境界 |
|---|---|---|
| 取り込み | `FxDayoLoader.loadAdjacent`、未登録sourceのbackground compile | 読み込み前の要求照会、明示的な実行方式、PMXとsourceの再関連付け |
| 原文固定 | `FxDayoSourcePackage`、依存bytes・SDK/profile・intent保存 | root内の正規化path、import種別、生成include、virtual pathの一般化 |
| 定義 | Jsonnet→厳密な`FxDayoProgramIR`、未知field拒否 | 機械可読schema、metadataと実行fieldの区別、Dayoのdefaultと条件式の正確な再現 |
| compiler | DXC→SPIR-V→SPIRV-Cross→MSL、reflection検査、8-entry cache | job取消、source位置付き診断、総時間・メモリ制限、artifact identityの強化 |
| owner | nativeと`.sourceProgram`を分離、terminal拒否を先行 | 選択理由の公開、native近似による原文変更の吸収を防ぐ明示モード |
| GPU | ordered compute/postprocess/index-only rasterizer | 条件の互換修正、資源read/write計画、必要入力だけを供給するprofile |
| scene | ToonShader HQ HDR、不透明triangle、camera/GBuffer/前回頂点 | 単純画面加工の軽量化、透過・AA・他effect混在の段階的受入 |
| 履歴 | 候補状態と確定状態の分離、actual-present連動 | reset原因別event、reload世代、積分型effectの再実行方針 |
| 保存 | schema25、原文package、source intent、元folderなしの復元 | 実行選択と新profileの移行規則、将来SDK解決の固定 |
| export | 共通executorと独立history、失敗時の停止 | sample契約の明文化、機能別preflight、liveとの対照試験 |

処理は読み込み、構造検査、コンパイル、GPU実行、シーン条件の検査へ分かれる。構造検査の成功だけで実行可能とは判定しない。

build402の記録には元MotionBlurの7pass、原文の改名・式変更、限定sceneのlive、保存往復、短尺動画がある。これを全素材・任意解像度・Dayo画像互換の合格とは扱わない。

## 最優先で固定する互換契約（初稿の課題と方針）

### 条件配列のAND評価

静的照合ではDayo 1.30の`YRZFx.ixx:3833`付近の`PassCond`が全条件のAND、初稿時のViewerは配列を`contains(where:)`でOR評価していた。v0.56.20ではANDへ修正した。

例として`conditions: ["OnLoad", "OnResize"]`は、OnLoadだけが真の候補でDayoは実行せず、初稿時のViewerは実行していた。初期化・履歴更新パスが意図より多く動く不一致を、P0で修正した。単にドキュメントをORへ合わせる対応は採らない。

空配列、1要素、2要素の真偽4通り、否定・括弧、式内ORと配列ANDの違いを試験する。parser単体だけでなく、executorの実行pass列とbuffer結果を確認する。元MotionBlurは1要素の式を使用するため、その成功は複数要素の互換性の証明にならない。

### eventと式言語

初稿時のlive経路は前回履歴がないと`OnStart/OnLoad/OnResize`をまとめて立てる。profileの受入式はboolと一部eventに限られ、Dayo側の数値controller条件などとは範囲が違う。

P0では現行eventの意味を公開する。P1では`load`、`start`、`resize`、`seek`、`program replacement`を内部のreset原因として分離し、Dayoへ渡すeventを対象版の実行コードで固定する。`OnLoadSkybox`のように名前を受け付けてもproducerがない入力は、能力表で「供給なし」とし、false固定を完全対応として扱わない。

### 互換性の表示

次の軸を独立させる。単一の`supportLevel`だけから「対応済み」を判断しない。

| 軸 | 状態例 | 何を保証するか |
|---|---|---|
| 解析 | captured、evaluated、rejected | 原文と定義を取得した |
| 変換 | compiling、compiled、failed | shader生成とABI検査が終わった |
| 実行能力 | live eligible、export eligible、scene blocked | 指定条件で準備できる |
| runtime | inactive、active、failed、previous revision active | 今回のscene・frameで使っている状態 |
| 画像検証 | unverified、verified for recorded cases | 特定条件のDayo比較がある |

英語状態名はAPI案の識別子で、UIでは「原文の変換完了」「現在の設定では実行不可」など利用者が次の操作を判断できる表示にする。

## 公開するインターフェイス

### 作者とViewerの境界

既存Dayo原文を標準入力とし、新しい必須fieldを`.fxdayo`へ挿入しない。作者向けには次の三つを用意する。

| 入口 | 入力 | 結果 |
|---|---|---|
| 対応条件の照会 | runtime版、device、描画構成 | 対応profile、SDK、機能、制限、診断schema |
| effect検査 | PMX、source package、希望する実行方式 | 定義・依存・必要能力・不足・候補方式 |
| コンパイルと適用 | 検査済みpackage、scene context | 取消可能job、prepared program、適用結果 |

`.fxdayo`単独ではPMX controllerやsceneの供給能力が決まらない。検査結果は「sourceだけの判定」と「このsceneでの判定」を分ける。

### 内部API案

次は責務と入出力を示すSwift風の擬似コードであり、現行型の宣言ではない。実装時に既存型へ統合し、不必要な二重管理を作らない。

```swift
protocol FxDayoRuntimeService {
    func capabilities(for context: HostContext) -> RuntimeCapabilities
    func inspect(_ request: InspectionRequest) async -> InspectionReport
    func compile(_ request: CompilationRequest) async throws -> PreparedProgram
    func preflight(_ program: PreparedProgram,
                   in context: ExecutionContext) -> ExecutionReport
    func makeSession(_ program: PreparedProgram,
                     for context: ExecutionContext) throws -> ExecutionSession
}
```

| データ | 必須内容 |
|---|---|
| `HostContext` | runtime/SDK/toolchain版、device能力、描画style、色・alpha・AA、サイズ |
| `InspectionRequest` | 読取許可root、元bytes、PMX能力、execution intent、要求profile |
| `InspectionReport` | package fingerprint、評価済み定義、必要capability、依存graph、候補と拒否理由 |
| `CompilationRequest` | immutable package、選択profile、compiler options、request generation、取消token |
| `PreparedProgram` | IR、reflection、生成shader、device別pipeline、source map、identity |
| `ExecutionReport` | live/export別判定、不足入力、寸法制約、資源見積り、診断 |
| `ExecutionSession` | attachment/scene/run固有の可変資源、pending/committed history、failure latch |

`inspect`はsceneを書き換えない。Jsonnet評価等の外部処理を必要とする場合もjob管理下で行う。`compile`成功後にも`preflight`を必須とし、resizeや設定変更時に再判定する。`makeSession`だけでliveの表示済み状態へcommitしない。

### capabilityの粒度

`supportsHLSL=true`のような一つのboolを設けず、少なくとも次の単位で公開する。

- 言語: 対象Dayo/Jsonnet契約、HLSL target、include/import方式、条件式の文法。
- パス: category、pass種別、shader stages、render target数、blend/depth/rasterizer状態。
- 資源: texture次元・format・view、buffer型・stride、sampler、配列とregister space。
- scene入力: 色の挿入位置、深度の定義、GBuffer各成分、頂点member、camera ABI。
- 動的入力: controller型と参照先、clock、event、履歴、seek policy。
- 実行条件: live/export、alpha、AA、描画style、寸法、deviceと資源予算。

未使用のSDK宣言とshaderが実際に参照する能力は分ける。評価済み定義とreflectionから要求を導出し、条件付きパスも含めたprogram全体で判定する。実行時に使わなかったことを理由に未対応機能を見逃さない。

## profileの整理案

既存`dayo130.hdr-scene.v1`を互換性の基準として残し、次の段階へ分ける。追加IDは仮称。

| profile案 | 目的と主な入力 | 受入の境界 |
|---|---|---|
| `dayo130.hdr-color.v1` | 履歴なしの画面加工、ScreenTexture、必要なcamera/frame値、self float controller | scene geometryを要求しない。shaderが要求しない不透明triangle制約を機械的に継承しない |
| `dayo130.hdr-scene.v2` | 複数pass、compute、限定rasterizer、GBuffer、前回geometry | v1から条件・event・資源状態・寸法を厳密化。初期の可視性範囲を明示 |
| `dayo130.temporal.v1` | 永続texture/buffer、状態を持つ効果 | step、commit、reset、seek復元、export sample列を定義してから公開 |
| 将来のdeform profile | custom deformとcurrent/previous完成頂点 | 既定skinを置換し、二重スキニングを防ぐ。別の実証を要求 |
| 将来のrender/DXR profile | renderer全体やraytracing | 本計画の初期完了条件には含めない。別途成立性を評価 |

軽量color profileも、tone mapping前後・linear/sRGB・alphaの責任を固定するまで公開しない。GPU負荷の削減は目標であり、現段階の性能結果ではない。profileを増やす目的は、作者が必要とする機能だけを契約化し、単純なshaderにMotionBlur用の全scene資源を要求しないことにある。

SDK版、profile版、保存schema版、toolchain版は独立に管理する。`v1`文字列を保ったままdefaultや意味を拡張しない。バグ修正で旧projectの結果が変わるときは変更理由と対象条件を診断へ出す。条件配列のORに依存した旧projectを再現するために、正しいDayo互換としてORを温存しない。移行対象として検出し、再検証を要求する。

## 実行方式と単一owner

### 選択規則

`executionIntent`を、native adapter指定、source program指定、未選択に分ける。UIで変更した意図をprojectへ保存する。

| 入力の状態 | 選択 |
|---|---|
| 既知source/PMX/sidecar/vertex ABIのterminal不一致 | 拒否。source compilerで迂回しない |
| source programを明示 | profileとsceneが成立すれば原文を実行。native近似への自動退避なし |
| native adapterを明示 | 指定adapterの契約を検査。失敗時に別ownerへ変更しない |
| 既存projectに実行方式がある | 保存した方式・profileを維持 |
| 新規で未選択、既知native候補あり | 従来選択を初期候補とし、方式と近似範囲を表示。作者は原文実行を選べる |
| 新規で未選択、native候補なし | profileの能力判定からsource programを試す |

native内のexact-source、capability-matched、registered providerの優先順位は既存契約を保持する。`restricted generic + registered native provider`をsource compilerの別名にしない。同一優先tierの複数native候補はambiguousとして拒否する。

attachmentの実行ownerは0または1。source compilerが成功してもnative ownerを同時に残さない。解析・失敗したattachmentもauthoring/status順に保持し、実行可能なものの相対順をlive/exportごとに解決する。

### 原文reload

1. 現在のpackage/programを確定したまま、新bytesを新しいrequest generationとして捕捉する。
2. 依存、定義、compiler、pipeline、scene preflightをbackgroundで完了させる。
3. job完了時にrequest generation、PMX/scene世代、希望する方式がまだ一致するか確認する。古い完了は適用しない。
4. frame境界で全ownerの実行計画を交換し、変更されたprogramと入力に依存する履歴を初期化する。
5. GPU使用中の旧program/resourceは完了まで保持して退役する。

失敗時に旧programを保持する場合は「編集版は適用失敗、前回版を表示中」と示す。保存とexportは現在採用中のsnapshotを使い、失敗した編集版を成功版として保存しない。sceneが変更され旧programも成立しなくなった場合は、旧版維持ではなく明示的な停止状態にする。

## 原文packageと依存解決

### 読取境界

原文、Jsonnet import、HLSL include、外部画像、SDKをvirtual filesystemの名前空間へ収録する。取り込み以降は収録bytesだけをコンパイラと保存処理へ渡す。

初稿時は`..`を一律拒否していた。v0.56.20では、明示したpackage rootの内側へ正規化される参照なら、`../../hlsl`のような配置を扱えるようにする。ただし任意の親ディレクトリを自動でrootへ拡大しない。最初のPMX folderで足りない場合に、作者がpackage rootを指定するUIを設ける。

絶対path、root外へ出るsymlink、NFC・大小文字の衝突、重複pathを拒否する。system SDK aliasと作者ファイルの大小文字規則は分離する。SDKを最新へ自動置換しない。

### 評価器による依存捕捉

literal探索は事前検査として残し、最終的にはJsonnetのimport解決とHLSLのinclude解決で実際に使った依存を記録する。`import`はJsonnet、`importstr`は文字列、`importbin`はbinaryとして別の型を持たせる。現在の`File.isJsonnet`だけにすべての依存意味を押し込めない。

Jsonnetが生成したHLSLやincludeも同じ境界を通す。実際に採用された依存だけでなく、対応profileの別pass macro・設定で必要な依存も検査する。未収録の依存が後から有効になった場合は再検査する。shader原文やinclude行を書き換えて成立したことにしない。

### 任意manifest案

作者向け補助情報が必要なら、Dayoが読まない別ファイル`vvfm.fxdayo-manifest.json`を任意で認める。これは新規提案であり、現行の保存内部形式`.vvfm-fxdayo.json`とは別物である。

```json
{
  "schemaVersion": 1,
  "entry": "ExposureDemo.fxdayo",
  "targetDayo": "1.30",
  "preferredExecution": "sourceProgram",
  "requestedProfile": "dayo130.hdr-color.v1"
}
```

manifestがなくても、必要能力の導出から対応profileを選べる設計にする。manifestの自己申告でshader検査、terminal拒否、予算、PMX能力検査を省略しない。未確認の性能や互換性をmanifestで「合格」にするfieldは設けない。

## コンパイルと診断

### job管理

既存のbackground compileと一時workspaceを基礎に、job単位の総時間、入力bytes、生成物bytes、子processメモリ、同時job数、queue長、取消を管理する。個々の子process timeoutだけでは32 pass全体の待ち時間は制御できない。P0で現行値を可視化し、総予算は実装時の測定に基づいて決定する。

取消では子processの終了を確認し、一時資源を掃除する。取消後のcompletionはsceneへ適用しない。将来helperを分離する場合も、ネットワーク不要、native callback非公開、許可したworkspace以外を読まない境界を設ける。任意shaderのGPU上の停止性はこの仕組みでは保証できないため、「安全なshader sandbox」という表示はしない。

### cache identity

原文と推移的依存のdigest、SDKの実bytes、profile、compiler実体/version、compiler options、ABI版をcode cache keyへ含める。deviceごとのpipeline cacheにはdevice能力とOS/Metal条件も含める。現行のtoolchain manifest digestを、そのまま署名後実行物の真正性検証とみなさない。

原文を変更した場合だけでなく、include、SDK、compile optionを変更した場合にも正しく失効することを確認する。キャッシュ削除や新しいMacでの読み込みでも、保存packageから再生成できることを条件とする。

### 診断schema案

```json
{
  "code": "FXD-PROFILE-UNSUPPORTED-RESOURCE",
  "severity": "error",
  "stage": "reflection",
  "source": { "path": "source/MyEffect.fxdayo", "line": 87, "column": 9 },
  "pass": "Trace",
  "resource": "TLAS",
  "profile": "dayo130.hdr-scene.v2",
  "message": "このprofileはTLAS入力を供給しません",
  "capabilities": { "live": false, "export": false }
}
```

codeは安定した機械識別子、messageは翻訳可能な説明とする。source mapで元のinclude、Jsonnet生成code、pass生成宣言を区別する。位置を復元できない場合はline/columnを省略し、仮の元行番号を出さない。

診断stageはcapture、definition、profile、compile、reflection、pipeline、scene、resource、encode、GPU、presentation、exportに分ける。source hash、request generation、program identity、attachment IDは詳細情報へ含める。同じ失敗をframeごとに出し続けず、構造的なreset境界を持つfailure latchで抑える。

## 資源とパスの実行契約

### IRからの実行計画

IRへresourceごとのread/write、view、format、サイズ式、初期値、寿命、persistent/transient、共有元を持たせる。sourceのpass順を正本にし、依存graphは不正な循環・未初期化read・hazard・barrier・寿命の検査へ使う。勝手な並べ替えは行わない。

条件付きproducerが動かない候補では、後段が初期値または確定済み履歴を読めるかを検査する。資源がゼロ初期化されていることと、原文が要求する有効な履歴であることは別である。外部共有resourceのproducerがないときは代用textureで対応済みにしない。

### 端数dispatch

P0では現行の倍数条件と拒否理由を維持して能力表へ載せる。P1で一般解像度対応を扱う際には、次の二案を分けて実証する。

| 案 | 必要な根拠 | 初期判断 |
|---|---|---|
| 正確なlogical thread数を処理するdispatch | 対象GPUの非一様threadgroupとshader内group共有・barrierの意味が整合する | 成立する限定profileで検討 |
| ceil groupと作者のbounds guard | 全read/writeが論理範囲内、barrierに全threadが参加するなどの契約を満たす | shader解析とnegative試験が必要 |

shaderがguardを持つという文字列検査だけで許可しない。dispatch切捨て、原文への自動return挿入、余分な要素を黙って増やす方式は、同値性の証拠なしに採用しない。未成立ならそのprofileは正確な倍数のみを受け入れる。

### scene入力と予算

必要capabilityから色だけ、深度、GBuffer、前回geometryを選び、不要な入力の生成・保持を省く。複数source attachmentはimmutable scene入力を共有できるが、書込み先や履歴はattachment/live/exportごとに分離する。

program単位に加え、scene全体、pending候補、committed履歴、GPU使用中の旧世代を含むbyte ledgerを設ける。たとえば4KのRGBA16F一枚は画素部分だけで約63.3 MiBとなるため、現行の候補内上限だけでは複数effectの総容量を説明できない。この値は容量計算であり実機測定ではない。

資源不足時は、適用前の拒否とactive後の失敗を分ける。liveで効果を抑制するpolicyを導入するなら状態を明示し、exportではactive effectを省いた成功frameへ置換しない。保持中の旧世代はGPU fence後に退役させる。

## 履歴と時刻のAPI

frame packetには少なくとも、scene/PMX/resource世代、program identity、controller revision、VMD sample、camera、event、前回commit identityを含める。値とその世代を別々のmutable場所から読む構成を避ける。

| 状態の種類 | stepとseek方針 |
|---|---|
| stateless | 指定VMD時刻から直接評価。重複描画しても状態が進まない |
| previous sample依存 | 前回確定sampleとの組を保持。不連続時の初期値を明示 |
| 積分・蓄積 | 固定stepまたは作者契約のsample列を保存。reset、始点再実行、checkpointのどれを採るかprofileで定義 |

liveは全ownerの同一transactionとGPU成功・positive actual-present後にcommitする。attemptはretryで変わり得るが、意味上のsampleは勝手に進めない。present欠落、late callback、旧resource completionは新世代を更新しない。

exportはimmutable snapshotと独立sessionを作り、rational PTSから入力sampleを求める。GPU成功後の完成frameだけwriterへ渡す。履歴effectのlive/export同値を試験する場合は入力sample列も揃える。物理の全fixed-stepを飛ばす方法でeffectの遅延を隠さない。

既存のフレーム履歴と表示の確定処理を拡張し、第二の独立した履歴commit機構を作らない。

## UIと開発者の操作

最初は既存のエフェクト読込状況へ機能を追加し、新しい補助windowを必須にしない。

| 操作 | 表示と結果 |
|---|---|
| 対応条件を見る | 対象profile、必要な描画設定、対応しない機能を表示 |
| 実行方式を選ぶ | 原文実行／選択済みnative adapterと差の説明 |
| 原文を再検査する | dependency、definition、compile、scene判定の進行と取消 |
| 再読込する | 新版の準備完了後に適用。失敗時は旧版表示を明記 |
| 元sourceへ移動する | 読み込んだ元fileとproject内snapshotを区別 |
| 診断を保存する | source hash・profile・環境・失敗stageをまとめ、機密pathは任意で伏せる |

任意のfile watcherを後から導入する場合はdebounce、編集中の一時構文エラー、保存連打、取消、PMX削除を扱う。取り込み時に失敗するたび既存sceneを消さない。新しい別windowを作る場合は共通ウインドウ仕様の前面表示、最大化・全画面、focusと再生保持を完了条件へ追加する。

## 保存と移行

schema25のsource packageを読み続け、原文bytes、依存、SDK/profile、source intentを保持する。実装時にschema一覧を確認し、新しい実行選択とpackage2にschema26／minimum reader26を割り当てた。

| ケース | 移行規則 |
|---|---|
| 既存native project | 選択済みadapterと既存契約を保持 |
| schema25 source project | source programとして復元。profileの意味差があれば診断 |
| 新しいprofileを旧readerで開く | minimum readerまたは必要featureで拒否。effectを落として開かない |
| SDKやcompilerを変更する | 変更したidentityで再compile。結果差の可能性を表示 |
| 元folderがない | 保存packageだけで復元できることを確認 |
| キャッシュがない | 保存原文から再生成する。cacheをprojectの正本にしない |

GPU履歴をprojectへ保存することと、effectの再現に必要なseed・初期条件・step policyを保存することは分ける。永続GPU状態の直接serializeは初期範囲に含めない。

## 実装順序と完了条件

### P0 現行profileを正確に公開する

| 作業 | 主な変更先 | 完了条件 |
|---|---|---|
| 条件配列AND修正とevent差の明示 | IR、executor、program tests | 真偽表と実行pass列がDayo 1.30契約に一致。旧複数条件sourceの影響を診断 |
| 現行capability/schema一覧 | IR、SceneProfile、SDK/ABI定義 | 現行受入/拒否と一覧が一致し、未知fieldと供給しない入力を説明できる |
| 段階別診断 | ProgramError、compiler、attachment/status UI | compile成功とscene実行可を分離、pass/resource/可能な元位置を返す |
| 明示execution intent | loader、registry、project | source指定の数式変更がnative近似に吸収されず、単一ownerとterminal拒否を維持 |
| 状態文書整合 | STATUS、旧adapter資料、READMEの対象節 | 全面未実装という古い記述を限定対応へ更新し、未受入範囲を保持 |

P0は機能を拡張する前の契約修正である。追加pass対応や1080pを同時に成功条件へ詰め込まない。

### P1 作者が反復開発できる入口

P0を基礎に、inspect/compile/preflight API、job取消、再読み込みtransaction、source map、package root選択、依存型の分離、cache identity、scene総予算を実装する。並行compileの積極導入より、旧jobの誤適用とUI停止を防ぐことを先に成立させる。

color profileを追加し、scene geometryを参照しない新作を使って、PMX alpha等の制約をどこまで外せるか契約ごとに検証する。端数dispatchは独立の変更として取り組み、対応可否を解像度別に公開する。

完了条件は、原文変更→診断→適用→取消／失敗→旧版保持→保存→移動復元の一連の操作が、通常UIと通常load/render/export経路で成立すること。parserと設定の追加だけでは完了にしない。

### P2 対応する効果の範囲を広げる

外部texture、copy/clear/mipmap、永続texture、controller型・参照先、共有scene入力、AA/DoF/Bloom等との混在、透明出力を、それぞれのprofile改版として追加する。

各機能は、言語→IR→compiler→入力供給→GPU実行→live/export→保存→診断を縦に通す。一覧に機能名を追加しただけで対応と表示しない。特定effectの式をhard-codeする実装は、この汎用受入の成果へ数えない。

### P3 別categoryと互換性受入

deform、renderer、DXRは独立した成立性調査から始める。deformでは完成頂点の所有権と二重skin回避、rendererではPMX材質順・alpha・depth・scene全体の所有、DXRではMetal側の機能と意味を個別に実証する。初期計画の完了をこれらすべての無条件互換まで拡張しない。

## 受入試験

以下は受入matrixであり、各行をすべて通過済みとする一覧ではない。v0.56.20での教材確認と、全素材・Dayo画像同値・正式性能の未確認範囲は分けて扱う。

| ID | 試験 | 合格条件 |
|---|---|---|
| A01 | 未登録名/SHA、pass/resource改名、式変更 | 登録不要、意味を保つ改名は同結果、係数変更は期待した画素・数値変化 |
| A02 | 条件配列・event | AND真偽表、空配列、式内OR、load/start/resize/resetの契約に一致 |
| A03 | 依存 | root内の依存が保存後も同じbytesへ解決され、root外・衝突・欠落を理由付き拒否 |
| A04 | ABIと資源 | offset/stride/major、register space衝突、未対応member、未初期化readを正しく受入/拒否 |
| A05 | controller | 0/既定/負値/範囲外、group/flip、重複名、二個体、VMDなしで仕様どおり |
| A06 | live | play/pause/seek/loop/resize、model差し替え、effect順、late completionで世代混在なし |
| A07 | reload | 保存連打、旧job完了、取消、compile失敗、PMX削除で誤適用なし |
| A08 | 履歴失敗 | GPU failure、positive present欠落、retryで未表示候補をcommitせず二重stepなし |
| A09 | 保存 | 元folder移動、cache削除、新SDK/旧reader、方式保持、改ざん検出 |
| A10 | export | 適用能力判定、rational PTS、透明可否、liveと別history、active失敗時停止、atomic commit |
| A11 | 汎用素材 | 単純色、複数pass、compute、scene入力、履歴の別々の未知sourceで実行 |
| A12 | Dayo比較 | 同じ入力textureとsample列の中間結果、最終scene画像を別々に比較 |
| A13 | 性能と資源 | Releaseでactual-present、VMD進行、pose age、入力遅延、MainActor、pass GPU時間、RSS/GPU byte、10分 |

A03は入れ子import/include、importstr、生成code、大小文字、symlinkを含める。A11は「何本読み込めたか」だけでなく、各sourceの必要能力・実行pass・未対応を残す。

単体・GPU fixture・通常統合・Release GUI・Dayo画像比較・正式性能は別のgateとする。素材不足やGPU不足によるskipは成功へ数えない。GPU fault等をpure state testだけで代替した場合は、実機障害注入が未検証であることを記録する。

実装変更時は関連テスト、全`swift test`、`git diff --check`を行い、描画・資源・配布物に関係する段階ではRelease buildと対象実機検証を追加する。性能の許容差は計測前にsceneごとに決め、FPSだけで採用しない。実表示FPS、CPU／GPU時間、姿勢鮮度、資源量を分けて評価する。

## 採用時に残す証拠

機能追加ごとに、source/PMX/依存のhash、Dayo版とSDK由来、profile/toolchain、必要capability、実行方式、実行pass、scene条件、試験ログ、画像・動画、未対応・未検証を保存する。作品の利用許諾と検証データの公開条件を確認し、作者素材を無条件にrepoへ同梱しない。

最初の採用単位はP0、次にP1とする。P2以降は機能別に受入を進める。リリース記録の更新、ローカルbuildの完成、Git統合、外部公開、Dayo互換、性能受入を別々に記録する。

## 根拠と保留事項

初稿の調査対象HEADは`6c83be79a10eda0a15a2da6e5fda103d2b49e274`、未コミット実装を含むv0.56.16作業ツリー。設計の前提は現行コードで再確認した。[参照snapshot](SOURCE_SNAPSHOT.json)

- 先行の汎用runtime研究とMotionBlur実装記録を引き継ぐ。実装済みのcompiler、scene入力、保存、exportを新規成果として数え直さない。
- adapter契約のterminal拒否、単一owner、native優先順位を維持する。原文経路は独立した契約として扱う。
- 再生復旧、動画書き出し、Metal資源の既存境界を保持する。
- DXC/SPIRV-Cross経路を現行基盤として継続する。変換器の全面置換は本計画の前提にしない。[DXC](https://github.com/microsoft/DirectXShaderCompiler/blob/main/docs/SPIR-V.rst)、[SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross)

能力表・構造schema・jobとGPU予算はv0.56.20実装に合わせて公開した。端数dispatchとDayo比較の許容誤差は未採用・未確定。Dayo 1.30配布物の対応upstream commit、全素材の画像互換、build402の正式性能と600秒耐久は引き続き未確認・未受入である。
