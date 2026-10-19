# MikuMikuDayoとVMD Viewerの.fxdayo開発者向け技術解説書

> VvfM収録注（2026-10-19）：[公開main `3620662`](https://github.com/opopoposiop/VMDviewer_for_Mac/tree/36206626a7214ad8b8de5bba362189a38c285529)から取り込みました。本文の「現行」は主に2026-10-14のv0.56.37研究時点を指し、v0.56.42の追記を含みます。v0.56.46のcontroller等、後続の採用範囲と未完了項目は[資料の案内](README.md)を参照してください。本取込ではビルド・実機試験を再実施していません。


`.fxdayo`は、GPUで実行するHLSLに加え、入力資源、出力資源、パスの順序、PMXから受け取る操作値を定義するエフェクト形式である。両アプリで同じ原文を動かすには、HLSLの構文だけでなく、ホストが供給するデータの意味と実行条件を合わせる必要がある。

VMD Viewerの現行作業ツリーには、既知エフェクトをMetalへ移植した専用adapterと、未知の原文をコンパイルする限定汎用runtimeがある。新作はまず、後者の対応範囲に収まる単純な画面加工から始める。**`.fxdayo`という拡張子、解析成功、コンパイル成功のいずれも、すべての機能やDayoとの画像一致を保証しない。**

**2026-10-14更新。** 対象はMikuMikuDayo 1.30配布物と、ViewerのVERSION `0.56.37`の作業ツリー（HEAD `6328f50376fe9217de76dc82401c97e80360a0eb`、未コミット変更を含む）。以下の「現行Viewer」は、この時点のコードで確認した契約を指す。今回の更新は、同梱postprocessの20本を未知原文として調べた[互換性研究](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/COMPATIBILITY.md)と[テスト環境研究](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/TEST_ENVIRONMENT.md)を反映した文書更新であり、新しい対応機能の実装や動作試験は行っていない。

既存の作者インターフェイスP0・P1は[v0.56.20の実装記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-07-fxdayo-interface-v05620/IMPLEMENTATION.md)、フェイルセーフは[v0.56.21の実装記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-07-fxdayo-failsafe-v05621/IMPLEMENTATION.md)を参照する。[インターフェイス計画](INTERFACE_PLAN.md)のP2以降や、本書の拡張案は現行機能と区別する。過去buildの検証結果をv0.56.37や20本全体の合格には繰り越さない。

## 読み方と到達点

HLSLの基本的な型と関数、PMXの材質とモーフを理解した開発者を想定する。最初に最小例を作り、モーフ制御、複数パス、時刻と履歴の順に進める。GPU経験が浅い場合は、次の用語を押さえる。

| 用語 | この解説での意味 |
|---|---|
| パス | 入力を読み、shaderやコピー処理などで出力を作る一回の処理 |
| resource | texture、bufferなどGPUが読み書きするデータ |
| controller | PMXモーフ等をHLSL変数へ結び付ける定義 |
| ABI | CPUとGPUが共有する型、配置、offset、stride、bindingの約束 |
| profile | Viewerが受け入れる言語・資源・描画条件を版付きで定めた契約 |
| attachment | PMX個体に結び付いたエフェクト。原文が同じでも個体の状態は別 |
| native adapter | 特定の契約をViewer内の既存Metal実装へ接続する方式 |
| source program | 読み込んだ原文から生成したGPUプログラムを実行する方式 |

教材の原文と再生成可能なPMXは[examples](examples/)へ収録した。単純露出、モーフ制御、2パス色調整を個別に検証する。Viewerの結果とDayoアプリでの実行・画像比較は別の証拠であり、Windows版Dayoの実行結果は未取得。

## エフェクトが動く仕組み

### 定義とshaderの役割

Jsonnetはパスや資源の定義を生成する。HLSLは各パス内のGPU処理を記述する。Jsonnetの`local`や配列生成は読み込み時の定義構築に使い、フレームごとのモーフ値や時刻をJsonnetへ戻して評価するものではない。[Jsonnet言語仕様](https://jsonnet.org/ref/language.html)

```text
PMXと同名の.fxdayo
  ├─ prefix               include、macro、共通宣言
  ├─ [YRZFX]〜[HLSL]     Jsonnetによる定義
  └─ [HLSL]以降          shader本体

定義の評価 → controllerとresourceの宣言生成 → パスごとのshader生成
```

prefixは単なる注釈欄ではない。ここにあるincludeやmacroを捨てると、shaderの意味が変わる。現行Viewerの生成順はprefix、controller宣言、sampler/resource宣言、`fx.code`、shader本文。パス名から`YRZ_PASS_<name>`が定義される。[コンパイラ実装](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoCompilerService.swift)

### categoryとパス種別

categoryはエフェクトを差し込む段階、パス種別は一回の処理方法である。`category: postprocess`でもcomputeやrasterizerを使える。Dayoの公式解説では、deformとpostprocessは同名PMXの読み込みで起動し、renderはrendererフォルダから選択する。[Dayo公式解説](https://github.com/pennennennennennenem/MikuMikuDayo/blob/main/tutorial/fxdayo.md)

| category | 担当する処理 | 現行Viewerの未知原文 |
|---|---|---|
| `deform` | 頂点の変形やスキニング | 対象外。既知native adapterは別契約 |
| `render` | 変形済みモデルを使うシーン描画 | 対象外 |
| `postprocess` | 描画結果を使った画面加工 | 限定profileで対象 |

現行profileのパスは`postprocess`、`compute`、index bufferを使う限定`rasterizer`。`copy`、`clearUAV`、`clearRTV`、`mipmapgen`、`raytracing`という独立したパス種別は受け入れない。RTVの`clear`指定と、独立したclearパスは区別する。[IRの受入検査](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoProgramIR.swift)

### Viewerの二つの実行経路

```text
同名sourceの取得
  → native契約の検査
      → terminalな契約不一致なら拒否
      → native指定ならnativeへ
      → 自動選択でnative候補があり、保存source archiveがなければnativeへ
      → 保存source archiveがある自動選択は原文packageの復元へ
      → 原文実行指定ならsourceへ（nativeへの失敗時退避なし）
      → その他は原文packageを取得してコンパイル
          Jsonnet → 厳密IR → DXCのSPIR-V → SPIRV-CrossのMSL → Metal
```

現行loaderは、未知の名前やSHAを理由に一律拒否する方式ではない。ただし構造が既知adapterに合う原文は、先にnative経路へ接続され得る。HLSLの式を書き換えたのに見た目が変わらない場合は、最初に選択された実行方式を確認する。エフェクト読込状況の「方式」で「原文を実行」を選べる。「自動選択」「Native adapter」と区別し、選択をprojectへ保存する。既知契約のterminal拒否は原文指定でも迂回しない。[loader](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoEffects.swift)、[registry](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoAdapterRegistry.swift)

DXCによる言語変換とSPIRV-CrossによるMSL生成は、Dayoのシーン入力や履歴を作らない。それらはViewerのrendererが供給する。変換器の導入だけでは互換runtimeは完成しない。[DXC SPIR-V仕様](https://github.com/microsoft/DirectXShaderCompiler/blob/main/docs/SPIR-V.rst)、[SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross)

## 最小の画面加工を記述する

### ファイルを用意する

自作または利用条件を確認した有効なPMXを教材用にコピーし、次のように配置する。PMXの構造自体は通常のPMXでよい。最初は不透明な三角形材質のみとし、shaderの効果を確認できる被写体を置く。

```text
ExposureDemo/
  ExposureDemo.pmx
  ExposureDemo.fxdayo
  PMXが参照する画像など
```

拡張子より前の名前と配置先を一致させる。`.fxdayo`はUTF-8で保存する。Dayo用の共通headerは対象版のものを使い、異なる版のheaderを混在させない。次の`<resources_pp.hlsli>`はDayoのsystem include形式で、Viewerでは同梱SDKへ解決される。この教材のinclude形式を、移植のために`../../hlsl/...`へ書き換える必要はない。

既存原文がquoted `../../hlsl/...`を使っている場合は相対参照として扱う。既定のpackage rootは原文の親フォルダなので、必要に応じて「依存ファイルのrootを指定」で配布rootを明示する。system SDKとsource相対参照を暗黙に置換しない。原文のpath自体が誤っている場合は、root指定だけでは解決しない。

### 最小例

次の全文を`ExposureDemo.fxdayo`へ記述する。同じ原文を[ExposureDemo.fxdayo](examples/ExposureDemo.fxdayo)、対応する教材モデルを[ExposureDemo.pmx](examples/ExposureDemo.pmx)として収録している。画面のRGBを線形空間で2倍にし、alphaは保持する。

```hlsl
#include <resources_pp.hlsli>

[YRZFX]
{
  "fx": {
    "category": "postprocess",
    "cereal_class_version": 0,
    "samplers": [
      {
        "name": "ImageSampler",
        "filter": "LINEAR",
        "addressU": "CLAMP",
        "addressV": "CLAMP"
      }
    ],
    "passes": [
      {
        "name": "Exposure",
        "type": "postprocess",
        "vertexShader": "FullscreenVS",
        "pixelShader": "ExposurePS",
        "rasterizerDesc": { "cullMode": "none" }
      }
    ]
  }
}
[HLSL]

struct ScreenVertex {
    float4 position : SV_POSITION;
    float2 uv : TEXCOORD0;
};

ScreenVertex FullscreenVS(float4 position : POSITION, float2 uv : TEXCOORD0)
{
    ScreenVertex result;
    result.position = position;
    result.uv = uv;
    return result;
}

float4 ExposurePS(ScreenVertex input) : SV_TARGET
{
    float4 color = Dayo::ScreenTexture.Sample(ImageSampler, input.uv);
    return float4(color.rgb * 2.0, color.a);
}
```

`samplers`の定義から`ImageSampler`の宣言が生成されるため、同名の`SamplerState`をHLSLへ重複宣言しない。`RTV`を省略したパスは既定出力へ書く。postprocessのvertex入力は`float4 POSITION`と`float2 TEXCOORD`で、最初の例ではこの二つをそのまま渡す。`SV_VertexID`だけで三角形を生成する別形式は、現行Viewerのpostprocess入力契約に合わない。

Viewerの原文実行位置はHQ ToonのHDRトーンマップ前なので、RGBを2倍にしても最終表示の各画素値が2倍になるとは限らない。中間HDR値は1を超えてよい。ここで`saturate(color.rgb)`や独自のガンマ変換を入れると、後段のトーンマップへ渡す情報を変える。[実行器](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Renderer/MetalFxDayoExecutor.swift)、[通常renderer](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Renderer/MetalModelView.swift)

### MikuMikuDayoで確認する

1. 対象をDayo 1.30に固定し、被写体と`ExposureDemo.pmx`を読み込む。
2. effectの読み込み・コンパイルエラーが出ていないことを確認する。includeが見つからなければ、対象配布物のheader配置と検索規則を確認する。
3. 基準画像を保存し、倍率を`1.0`にした版と`2.0`にした版で結果を比較する。読み直したsourceであることを確認する。
4. 解像度、使用renderer、カメラ、照明、後処理の順序を記録する。原文が同じでもシーン描画やトーンマップが異なれば最終画像は異なる。

### VMD Viewerで確認する

1. compiler同梱版を使用し、実際の版／buildを記録する。作者インターフェイスとフェイルセーフの導入はv0.56.20／v0.56.21で、当時の実機結果は各実装記録を参照する。本書の更新でv0.56.37を実行検証したという意味ではない。
2. HQ Toon、透視投影にし、「設定 → 再生 → .fxdayo 動作」でFrameTimeを選ぶ。この動作モードはアプリ設定なので、教材projectを開くだけでは切り替わらない。AA・DoF・Bloom・DiffusionをOFFにし、native effectとの混在を避ける。
3. `ExposureDemo.pmx`を通常のモデル読込から追加する。別名の原文は「原文を選択」で関連付けられる。
4. エフェクト読込状況の方式を「原文を実行」にする。単純な画面加工は`dayo130.hdr-color.v1`になり、GBuffer・前回頂点を作らない。「変換完了」とruntimeの実行状態をそれぞれ確認する。
5. 原文を保存し、「再検査」で確認、「再読込」で候補を準備する。初回や内容を変更した未知原文は「この原文を試す」で実行する。自動ファイル監視はない。同じPMXのpostprocess差替えはモデル個体・物理・未登録編集を保持し、GPU成功とactual-present後に確定する。準備中や失敗時の保存は採用済み原文を使う。native描画ownerまで変わる変更は既存のモデル差替え検査を使う。
6. 変換中は「取消」、適用の表示待ち中はViewer側の進捗の取消を使用する。失敗・取消では前回採用版を保持し、その版を保存・exportの入力にする。編集版のエラーと現在の実行状態を別に確認する。
7. 停止、再生、seek、resizeを確認し、短い不透明動画を書き出す。color profileにはcomputeがないため、MotionBlur固有のthreadgroup倍数条件は適用されない。共通の描画・寸法・資源条件は残る。


## PMXモーフを操作値へ結び付ける

### 定義と式を変更する

教材PMXに一意な名前のモーフ`明るさ`を用意する。形状を動かす必要がなければ、通常の有効なPMXとして保存できる操作専用モーフを使用する。Viewer内でPMXモーフ定義そのものを新規作成・書出しできるという意味ではない。

`fx`内へ次の`controllers`配列を加える。

```json
"controllers": [
  {
    "name": "C_Exposure",
    "controllerName": "(self)",
    "item": "明るさ",
    "type": "float"
  }
]
```

最小例のreturn文を次の2行へ置き換える。

```hlsl
float exposureEV = 2.0 * clamp(C_Exposure, -1.0, 1.0);
return float4(color.rgb * exp2(exposureEV), color.a);
```

`name`はHLSLの変数名、`item`はPMXモーフ名、`(self)`はエフェクトを起動したPMX個体を指す。controllerの変数宣言もホストが生成する。

| モーフ値 | 露出補正 | 線形RGB倍率 |
|---:|---:|---:|
| 0 | 0 EV | 1 |
| 0.5 | 1 EV | 2 |
| 1 | 2 EV | 4 |
| -1 | -2 EV | 0.25 |

このclampは教材shaderが選んだ仕様である。現行Viewerはcontrollerの有限raw値を一律に0〜1へ丸めない。負値をUIから入力できるかとは分けて、作者は範囲外入力に対する式の振る舞いを定義する。

### 評価の流れ

```text
VMDモーフと手動値
  → group/flipを含む評価済みPMXモーフ配列
  → 同じ評価世代のcontroller値
  → controller用constant buffer
  → 全パス
```

現行source programは`(self)`の`float`だけに対応し、モーフ名がない、重複する、値が非有限なら拒否する。別PMXの名前指定、ボーン位置、行列、controller配列を使うDayo effectは、そのままでは対象外。[controller検査](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoSceneProfile.swift)

controller内の`desc`と`slider`も現行の厳密IRでは受け入れない。Dayoの`desc`は説明文だが、`slider`には範囲・既定値・対数／整数入力の指定があり、配布実装は既定値をmorphへ接続する。これらを削って定義を通すだけでは、元の操作値を再現したことにならない。ColorGradingSDRのように既定値やVMDが見た目へ影響する素材では、初期値、既存キー、手動値、resetの優先関係まで確認する。[1.30のcontrollerと既定値の調査](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/COMPATIBILITY.md)

手動スライダーだけでなく、VMDの0・中間・最大値、group/flip経由、同じPMXの二個体で異なる値、seek後と動画出力の値を確認する。二個体は同じ原文を共有していても、controllerと履歴の可変状態を共有してはならない。

## 複数パスと資源を設計する

### 中間textureを明示する

「画面を明るくした後、その結果を色調整する」例では、中間texture`ExposureBuffer`を定義する。次のJSON断片は、最小例の`fx`へ`textures`を追加し、`passes`を置き換えるためのもの。

```json
"textures": [
  { "name": "ExposureBuffer", "format": "R16G16B16A16_FLOAT", "view": "RTV" }
],
"passes": [
  {
    "name": "Exposure", "type": "postprocess",
    "vertexShader": "FullscreenVS", "pixelShader": "ExposurePS",
    "rasterizerDesc": { "cullMode": "none" },
    "RTV": [{ "name": "ExposureBuffer", "clear": true }]
  },
  {
    "name": "Tint", "type": "postprocess",
    "vertexShader": "FullscreenVS", "pixelShader": "TintPS",
    "rasterizerDesc": { "cullMode": "none" }
  }
]
```

HLSLへ次を追加する。

```hlsl
float4 TintPS(ScreenVertex input) : SV_TARGET
{
    float4 color = ExposureBuffer.Sample(ImageSampler, input.uv);
    return float4(color.rgb * float3(1.0, 0.85, 0.7), color.a);
}
```

```text
attachment開始時のScreenTexture → Exposure → ExposureBuffer → Tint → 既定出力
```

現行Viewerの`ScreenTexture`はattachmentの開始時点の画面であり、同じattachment内でパスを実行するたびに直前の出力へ置き換わるものではない。後続パスは前段が書いたtexture名を明示して読む。別attachmentへ進む際には前attachmentの出力が次の入力になる。

この境界は、Dayo 1.30がeffectごとに出力を入力へcopyする構造と一致する。汎用互換性を広げる際も、ScreenTextureをpassごとに自動更新する変更は行わない。[Dayo／Viewerの接続比較](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/COMPATIBILITY.md)

同じパスで同じtextureを読みながらRTVへ書かない。二枚を交互に使うか、別の出力資源を設ける。`clear:false`はその資源の内容が既に有効であるときに使う。特に条件付きパスの後段では、producerがスキップされた場合の内容を設計する。現行版が未書込み資源の意味まで全て静的保証するとは扱わない。

### 型とformat

| 現行profileの資源 | 対応する代表的な型・形式 |
|---|---|
| 2D RTV texture | `R16G16B16A16_FLOAT`、`R32G32B32A32_FLOAT`、`R32G32_FLOAT`、`R32G32_UINT`、`R32_FLOAT` |
| SRV/UAV buffer | `uint`、`int`、`float`、`float2`、`float4`、`float4x4` |
| sampler | point/linearの対応filter、WRAP/CLAMP/MIRROR |
| 出力 | 既定はRGBA16FのHDR中間画像 |

`type`、`format`、`view`は互換な組み合わせが必要である。たとえばtexture UAV、DSV、3D texture、任意の画像ファイル入力、BORDER samplerはこのprofileの対象外。`float3` bufferも上表の受入型に含まれない。Dayoの全機能一覧とViewerの受入一覧を混同しない。

copy／clear／mipmapやtexture UAVを拡張する場合は、IRにfieldを足すだけでは足りない。生成HLSL、reflection、Metalのusage／view、subresourceごとのread/write、初期化、資源寿命、容量計算を一緒に定義する。BORDERをCLAMPへ置換したり、mipを作らずLODを無視したりする近似は、原文実行の成功とは分ける。

### 色処理とtone mappingの順序

同じHLSLを変換できても、挿入位置が違えば見た目は変わる。Dayo 1.30の同梱説明では、DoF／Glare／MotionBlur／Fogはtone-map前、FXAA／ColorGradingはtone-map後に置く。ACES系の原文自体がtone mapperを担う。一方、Viewerの原文はHQのHDR処理に挿入され、その後にViewerのACES曲線等が適用される。

```text
Dayoの指定順序の例:
  scene-linear HDR → DoF・Glare等 → 原文tone mapper → FXAA・ColorGrading等 → 表示色変換

Viewerの現行接続:
  HQのHDR画像 → 原文postprocess chain → Viewerのtone mapper → 出力
```

このため原文ACESの後に再びACESを掛ける、SDR向けの処理へHDRを渡す、といった意味の違いが起こり得る。Dayoの`renDayo.h`末尾にはtone mappingというコメントがあるが、対応する`background.hlsl`はgamma変換とclamp／出力色空間を扱う。コメントだけからACES二重適用が両アプリ共通と判断しない。Viewer側の実処理は[MetalEffectStack.swift](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Renderer/MetalEffectStack.swift)の`applyTonemapper`を参照する。

未知HLSLの色域やtone mapperをファイル名だけで判定しない。将来の拡張では、scene-linear／display-linear／最終encodeの境界とtone mappingのownerを明示する必要がある。作者の宣言やproject側のchain設定で原文を保持する案は**研究段階**であり、現行UIに任意の挿入位置を選ぶ機能があるわけではない。

DayoのppIn／ppOutはRGBA32F、Viewerの標準原文入出力はRGBA16Fである。色変換順序に加え、精度・HDR値域・alphaも別々に比較する。具体的なsource位置・hashは[互換性研究と環境記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/README.md)に保存した。今回、この構造差を画像差として測定してはいない。

### computeの寸法

`outputSize`は処理する要素領域、`numthreads`は一つのthreadgroupに属するスレッド数である。現行Viewerは全computeパスで、各軸の処理領域がthreadgroupの整数倍になることを要求する。条件が偽で今は実行しない初期化パスも検査される。

将来の端数対応を見据えた作者側の基本形は、論理要素数を取得して境界外を処理しないこと。ただし次は考え方の例であり、現行Viewerの倍数制限を解除するコードではない。

```hlsl
// NumElementsは作者が定義する論理要素数。
// group barrierを使わない独立要素処理の例。
[numthreads(64, 1, 1)]
void CS(uint3 tid : SV_DispatchThreadID)
{
    if (tid.x >= NumElements) return;
    // 有効要素だけを読み書きする。
}
```

group barrierがあるshaderで一部スレッドだけ早期returnする設計は別途検討が必要である。ホストが自動でguardを差し込む、dispatchを切り捨てる、余剰bufferを作る方法を、原文と同じ意味とみなしてはならない。

元MotionBlurの初期化は、標準定数で概ね`幅×高さ/16`要素を1024スレッド単位で処理する。1024×576なら36,864要素で36 groupとなるが、1920×1080は129,600要素で1024の倍数にならない。build402では後者と3840×2160を拒否する。この制約は「全`.fxdayo`が1080p非対応」という意味ではない。[既存の実装・検証記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-06-motionblur-generic-proof-plan/IMPLEMENTATION.md)

2026-10-14のコード確認でも[FxDayoResourceBudget](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoResourceBudget.swift)の倍数検査は残っている。Dayo 1.30は切上げdispatchを使うため、今後は元shaderの越境アクセスとbarrierを調べたうえで意味の一致を検証する。通常解像度と端数解像度は個別の試験caseにし、教材の1080p成功をMotionBlurの1080p成功へ読み替えない。

## 条件式と互換性上の注意

現行Viewerの条件式は、`OnStart`、`OnLoad`、`OnResize`、`Playing`、`true`、`false`、`!`、`&&`、`||`、括弧の範囲。controllerの数値比較は対象外。`OnLoadSkybox`は入力producerがないため、条件式と実際のViewCB member参照を拒否する。SDK内の未使用宣言は許可する。

v0.56.20はDayo 1.30の`PassCond`と同じく、条件配列の全要素をANDで評価する。v0.56.19以前のOR評価は修正した。複数要素のsourceには移行診断を表示するため、旧版の結果に依存していないか確認する。

| 記述 | Dayo 1.30 / Viewer v0.56.20 |
|---|---|
| `[]`または省略 | 常時 |
| `["OnLoad \|\| OnResize"]` | loadまたはresize |
| `["OnLoad", "OnResize"]` | loadかつresize |

イベントは最後に表示確定したcontextから求める。初回はOnStart・OnLoad・OnResize。Viewerの新規session（program・モデル世代・可視性・effect順の変更）はOnStartとOnLoad、寸法変更はOnResize、再生／停止の切替はOnStart。これはDayoのイベント名に対応させたViewerのsession初期化方針であり、Dayoアプリ全体の通知順を完全再現するとの主張ではない。seekだけではこれらを再発行せず、frame差分と前回geometryをリセットする。program・モデル構成が同じなら、寸法が変わっていない資源の内容を保持する。resize時もサイズが同じ絶対寸法bufferなどは保持し、サイズが変わった資源は再生成する。これは積分型effectの過去再現を保証するものではない。[履歴とイベント](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Renderer/DayoFrameHistory.swift)

scene-v1では、最初の読取りより後に無条件writerがある循環履歴資源を初回0で開始する。このViewer固有の既存初期値を`FXD-RESOURCE-ZERO-HISTORY`で明示する。一般の初期化passが実行されず後段がresourceを読むと、`FXD-RESOURCE-UNINITIALIZED`で停止する。同じpassのtexture読取り・出力は`FXD-RESOURCE-FEEDBACK`で拒否する。検査はresource単位であり、shaderがbufferの全要素を書いたことやGPU上の停止性までは証明しない。

## 時刻と前回frameを扱う

### 秒とVMD frame

Dayo 1.30の`FrameTime`はVMD frame番号を30で割った秒である。描画が60 HzでもVMD時計は30 frame/秒のまま。現行原文profileはFrameTimeを要求し、RealTimeを使うeffectはそのまま受け入れない。[同梱cb.hlsli](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Resources/Dayo130SDK/cb.hlsli)、[入力ABI](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Renderer/DayoSceneInputs.swift)

時刻だけから明るさを求めるなら、たとえば`0.75 + 0.25 * sin(6.2831853 * Dayo::FrameTime)`という式にできる。前回出力へ加算するfeedbackでは、同じframeでもそれまでのsample列で結果が変わる。両者を同じ「時間依存」として扱わない。

実例として、Dayo同梱DoFのfocus追従は`RealTime`／`DRealTime`を使用し、fluid3Dは固定`FluidDT=1/30`で状態を更新する。前者を機械的にFrameTimeへ置換したり、後者をseek先の時刻だけで再現したりしても原文互換にはならない。live／録画の時刻規則とreset条件を版付きで確認し、Viewer固有の決定的モードを提案する場合は原文同等の保証と分ける。

### 履歴の確定

現行Viewerは、候補のGPU処理が完了しただけではlive履歴を更新しない。同じ表示transaction、全ownerの表示確定、正のactual-present時刻が成立した候補を次の基準にする。表示されなかった候補や失敗した候補の状態を次へ混ぜない。[DayoFrameHistory](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Renderer/DayoFrameHistory.swift)

seekと再生状態の切替では、前回geometryとframe差分を再初期化する。program・モデル世代・可視性・effect順の変更では資源候補を再生成し、resizeでは寸法が一致する資源だけ前回内容を引き継ぐ。過去を積分する任意effectをseek先で再現する保証はない。積分型effectには始点からの再実行やcheckpointなど別の契約が必要になる。

### 動画出力

動画はliveの可変履歴から独立して評価する。出力rateを`num/den` fpsとすると、出力frame `n`のPTSは`n×den/num`秒、対応するVMD frameは`開始frame+n×30×den/num`で求める。履歴effectのsample列がliveと異なれば、同じframe番号でも画素一致は自動では成立しない。

現行source programは不透明出力を対象とする。実行中effectのresource・encoder・GPU失敗を、effectを省いた成功動画へ置き換えない。既存ファイルの置換は全処理の成功後に行う。[MovieExportSession](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Export/MovieExportSession.swift)、[書出し契約](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/skills/mmd-deterministic-movie-export-qa/references/movie-export-rules.md)

## シーン入力とMetal変換の境界

| 入力 | 現行profileでの扱い | 作者が注意すること |
|---|---|---|
| `ScreenTexture` | attachment開始時のRGBA16F HDR画像 | 前パス出力と混同しない |
| `NormalDepth` | 法線と線形深度を持つRGBA32F | Viewer内部のReverse-Z depthを直接代入した値ではない |
| `GBuffer1` | RG32UIntのmodel IDとface ID | 背景の無効IDを検査してから配列を読む |
| `GBuffer2` | RG32Fの透視補正された重心座標 | 成分から三角形の三つの重みを復元する |
| `PreVB` | 112-byte Vertex配置の前回world position | 受入memberは`position`のみ。normal等まで対応したと解釈しない |
| `IB` | モデル別のindex buffer配列 | IDとモデルtableの同じ世代を使う |
| `ViewCB` | camera、model数、FrameTime系、解像度、sample、一部event等 | headerに宣言があってもすべて参照可能ではない |

ViewCBの`RealTime`、mouse、照明等、TLAS、任意bindless texture、汎用material tableは初期profileの対応範囲外。型付きSPIR-Vのmemberアクセスも検査されるため、別名の変数を経由して参照すれば対応になるわけではない。[reflection](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoCompiledProgram.swift)、[member契約](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoVertexAccessContract.swift)

HLSLの`register(tN, spaceM)`はMetalのtexture番号と同義ではない。現行compilerはregister種別とspaceを分離して変換し、reflectionで衝突や型を照合する。作者は同梱system resourceを自己流のregisterで再宣言せず、Dayo headerと定義から生成される宣言を使う。

同様に`float3`、行列、配列、boolのCPU配置を推測してbufferへ書かない。Viewerを拡張する際はoffset・stride・行列のmajor方向をreflectionと数値fixtureで確認する。座標の左右、画面Y、行列の積順、線形深度、色空間、alphaは言語変換とは別の互換契約である。

## 現行profileの受入条件

次表は`dayo130.hdr-scene.v1`の制限であり、Dayo形式そのものの上限ではない。

| 項目 | 現行作業ツリーの条件 |
|---|---|
| scene | HQ Toon、透視投影、不透明triangle、1 sample、AA/DoF/Bloom/Diffusionなし |
| 混在 | native effectと材質effect graphとの混在を拒否 |
| device | Metal argument buffer tier 2、各compute pipelineのthreadgroup上限を満たす |
| 定義 | `fx.category=postprocess`、`cereal_class_version=0`、未知fieldを拒否 |
| 数 | 1〜32 pass、最大32 resource、64 controller、16 sampler |
| 入力file | 一つ8 MiB以下、総bytes 32 MiB以下、最大64 file、依存深さ32以下 |
| 依存 | literal include/import/importstr/importbinとsystem SDK。明示root内の`..`を正規化。絶対path、root脱出、macro includeは拒否 |
| sceneサイズ | 画面各辺4096以下、model table最大256 |
| GPU容量 | resource 256 MiB、program候補512 MiB、scene入力候補512 MiB。source effect群の確定・候補・GPU退役待ちを含む共通予算1 GiB |
| compute | 定義とreflectionのthreadgroup一致、全出力軸がその整数倍 |
| 保存 | 実行選択／package schema 2の導入条件はproject schema・minimum reader 26。native payloadを持たない原文attachmentの現行保存は、実行ON／OFF・承認fingerprintを含むschema27以上を要求。旧schema25・package1の読込を保持 |

共通GPU予算はsource effect用のGBuffer、program資源、定数・argument bufferとGPU使用中の旧資源を数える。Viewer全体のHDR、pipeline、driver、RSSを含む上限ではない。compilerは同時1・待機4job、総時間120秒、子process RSS監視1 GiB、入力を含むworkspace96 MiB。取消は外部compiler子processの終了まで確認する。同期Metal pipeline APIは呼出しを強制終了できないため、復帰後に取消・期限を再確認し結果を採用しない。shaderのGPU計算量を制限するsandboxではない。

`dayo130.hdr-color.v1`は資源・条件・履歴・scene geometryを参照しないpostprocessをreflectionから自動選択する。ScreenTexture、self float、許可されたcamera/frame値だけを使い、PMXのalpha材質をscene profileの理由で拒否しない。HQ Toon・透視・FrameTime・AA/DoF/Bloom/Diffusionなし・native混在なし・不透明出力という共通条件は残る。透明な動画出力の対応とは別である。

### v0.56.42の追加profileと色設定

`dayo130.postprocess.v2`は共通2D機能と資源操作を追加した契約で、scene geometryが不要とreflectionで確認できる場合は`dayo130.color.v2`を選ぶ。新規原文でもv1へ適合する場合は従来のv1を選び、保存packageのprofileは保持する。20原文の段階別結果と検証範囲は[実装記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-runtime-v05642/IMPLEMENTATION.md)に分ける。

| v2追加項目 | 意味と制約 |
|---|---|
| controller | `desc`、`slider`の範囲・既定値・log/intを保持。現在のPMX/VMD・手動値を優先し、load時に既存値をdefaultで上書きしない。selfのfloatモーフ値、boolの名前存在、intの名前indexを供給。骨位置・matrix・外部個体は入力不足として拒否 |
| shader/sampler | pass別macro、BORDERの透明黒・不透明黒・不透明白、基本UNORM。任意border色の近似はしない |
| texture | 2D SRV/RTV/UAV、mipSlice、明示mipmapgen、個体内3D SRV/UAV。3D RTV・array・共有textureは未対応 |
| functional pass | shape/formatが同じ資源間copy、2D clearRTV、float/UNORM textureのclearUAV、2D mip生成。buffer/integer clearは未対応 |
| 初期化 | mip単位で追跡。部分shader writeは全域初期化に昇格せず、先行clear/copy・採用済み履歴が必要。base変更後の下位mipは明示mipmapgenまで従前のbytesを保持 |
| 外部image | 不透明8bit PNG/BMPをsRGBとして解釈しbytesをpackageへ保存。各辺4096・入力8 MiBの制限と共有CPU展開予算128 MiBを検査。HDR/DDS、ICC変換、透明画像は未対応 |

既存のエフェクト読込状況で、原文の「色段階」を選べる。通常は「HDR → HDR（従来）」を使う。原文がtone mappingを行う場合はその原文を担当に指定し、後続を「表示linear → 表示linear」として担当を指定する。Viewerにtone mappingを任せる表示用原文では担当をViewerにする。表示linearはRec.709 primariesの線形値、不透明alphaを意味し、ガンマ符号化済み値をそのまま指定する契約ではない。

効果順は変更されない。表示段からHDRへの逆行、担当の重複、停止・削除・順序変更された担当への参照を拒否する。色設定の変更後は「この原文を試す」で再試行する。liveでは成立しないchain全体を破棄して通常描画へ戻り、exportでは失敗として停止する。明示した色chainでは共通条件に加えAOと輪郭線をOFFにする。色の宣言だけではDayoとの画像同値を保証しない。

機械可読の[定義schema](definition.schema.json)はJsonnet評価後の構造を表す。名前参照、resource型の組合せ、寸法、条件文法、reflection、scene条件はIRとruntimeが追加検査する。categoryとpass.typeはDayoの省略既定値へ依存せず明示する。

SDKはDayo 1.30配布物のheaderに基づく。headerが存在することは機能対応の証拠ではない。`desc`などの追加fieldも、選択profileの許可位置以外では拒否される。未知fieldを勝手に消して元effectを対応済みと扱わない。能力分析のsupportedは実行許可ではなく、未評価のshader・scene・容量・表示条件を追加確認する。

## 依存ファイルとproject保存

ユーザーincludeは、たとえば`#include "lib/color.hlsli"`のようにsourceの下へ配置する。ファイル名の大小文字を正確に合わせることを推奨する。v0.56.42ではroot内の一意な大小文字違いを同じ依存へ解決し、大小文字だけで衝突する別ファイルを拒否する。保存したpath・bytesは保持し、compile用workspace内だけに相対aliasを作る。root外への探索は許可しない。

現DXCでは、同じheaderを異なるcase表記で複数includeした場合、`#pragma once`だけでは再定義を防げない場合がある。表記を統一するか明示include guardを作者側で用意する。Viewerは原文へguardを自動注入せず、再定義をcompileエラーとして返す。`#pragma once`以外のconsole専用pragmaも現行profile外である。

```text
MyEffect/
  MyEffect.pmx
  MyEffect.fxdayo
  lib/color.hlsli
  definitions/settings.jsonnet
  README.md
```

現行runtimeは取り込み時の原文と対応する推移的依存を固定し、保存projectへ含める。保存用の`.vvfm-fxdayo.json`は内部packageであり、作者用の新しいDayo文法や手編集用のmanifestではない。Jsonnetが生成する`fx.code`のincludeも同じrootから捕捉する。取り込み後、compilerが未収録のファイルを参照することは拒否する。[SourcePackage](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Effects/FxDayoSourcePackage.swift)

依存が親フォルダにある場合は「依存ファイルのrootを指定」で範囲を明示する。自動的に親へ探索範囲を広げない。`importstr`はUTF-8の文字列、`importbin`は生bytesとして扱い、その中身を別のimportとして解析しない。

今回の20本には、原文より上の`hlsl/`、FXAAの`.fxsub`、FogのDDS・補助PMX、GlareのHDR画像等がある。includeを捕捉できることと、画像resourceや外部controllerを実行器が扱えることは別である。AbbeFeedbackのquoted include 2本は配布配置と合わず、root指定では直らない。大文字小文字だけが違うpathは、case-insensitiveな環境で見つかっても、case-sensitiveなpackage保存・復元で再確認する。[依存台帳](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/CORPUS.json)

元フォルダを失ったprojectでは「採用済み原文と依存を書き出す」で新しいフォルダへ展開できる。`source/`内のentryを編集元に選び、必要なら展開先の`source/`を依存rootへ指定する。既存フォルダは上書きしない。保存projectを編集元sourceの自動更新先として使わない。原文を更新した版と、既存project内の取り込み済み版は別のsnapshotである。復元では原文実行の意図を保持し、再コンパイル失敗をnative近似へ無言で変更しない。[project保存](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Project/ProjectPayloadArchiveIO.swift)

## 失敗を切り分ける

| 症状や診断 | 最初に確認すること |
|---|---|
| effectが検出されない | PMXと同じディレクトリ・同じbasenameか |
| 未対応field | field名と階層、対象profileのschema。例としてcontroller内`desc`は現行対象外 |
| package外の参照 | 明示root内か、絶対path、symlinkでの脱出、macro includeの有無 |
| controllerを一意に解決できない | `(self)`のPMXに同名モーフが一つあるか、評価値がfiniteか |
| 未対応shader resource/member | TLAS、追加ViewCB値、PreVBのposition以外などを読んでいないか |
| vertex入力がprofile外 | postprocessに所定のPOSITIONとTEXCOORDがあるか |
| threadgroupの倍数ではない | 各computeのoutputSizeを解決し、各軸で割り切れるか |
| compile済みなのに実行拒否 | scene設定、alpha材質、混在effect、実際の描画pixel寸法 |
| 原文変更が結果へ反映されない | native/sourceの実行方式、読み込んだ元path、保存snapshot、再読込の有無 |
| 色が白飛びする／暗くなる | HDR／SDRの挿入位置、トーンマップ重複、範囲clamp、alphaの扱い |
| 初期状態で黒い | controllerの既定値・既存VMD・必要資源を確認。ColorGradingの黒出力だけでGPU失敗と断定しない |
| 複数条件で実行頻度が違う | v0.56.20は配列AND。旧版のOR依存と、load/start/resizeの発火条件を確認 |

「原文・診断 → 診断を保存」で版、能力表、実行方式、hash、runtime状態、段階別診断をJSONに保存できる。原文とincludeの位置はvirtual pathで示し、Jsonnet生成HLSLは`generated/definition-code.hlsl`として元行と区別する。ローカル絶対pathは既定で伏せる。

診断を依頼するときは、Viewerの版/build、Dayo版、sourceとPMXのSHA、依存一覧、scene設定、pass名、失敗stage、再現操作を添える。単に「読み込めた」だけでGPU実行や画像互換の報告をしない。

## 両アプリでの検証と配布

### 検証の順序

1. 原文と依存を固定し、Dayo上で定義・shader・controllerが成立することを確認する。
2. Viewerの原文経路で受け入れられ、対象passが実行されることを確認する。
3. ファイル名やpass/resource名を変えても同じ処理になり、HLSLの係数変更が出力へ反映されることを確認する。これが名前登録依存でないことの試験になる。
4. controller値、初回、停止・再生・後方seek・loop・resize、二個体、保存後の元folder移動を確認する。
5. 同一入力の中間textureを比較する。DayoとViewerのベース描画が異なる場合は、共通の入力textureを使った比較と最終画像の比較を分ける。
6. 動画のsample列、PTS、失敗時の既存ファイル保持を確認する。履歴を使うならliveとexportの前提を記録する。
7. その後でRelease実機のpass時間、actual-present、VMD時計、pose age、入力応答、CPU/GPU、メモリ、10分耐久を評価する。

基準画像にはOS/GPU、Dayo renderer、SDK、解像度、カメラ、モーフ、時刻、前回sample列、色変換条件を付ける。画素誤差の許容値は対象効果ごとに比較前に決める。目視確認、数値fixture、画像差分、性能は別の結果として残す。

### 配布用READMEに書くこと

| 項目 | 記載例 |
|---|---|
| 対象 | Dayo 1.30、Viewerの確認版/buildとprofile |
| 内容 | PMX、原文、include/import、texture、VMD、各ファイルの利用条件 |
| 操作 | モーフ名、既定値、範囲、VMD使用時の動作 |
| 描画条件 | HDR挿入位置、対応renderer、透過、AA、解像度 |
| 状態 | 解析／compile／live／export／Dayo比較／性能を個別記載 |
| 制約 | 対象外のresourceやpass、履歴reset、既知の差 |

既知adapterの「exact source」はsource契約が一致したことを表し、Dayo画像の完全一致ではない。`compiledSource`も原文実行経路へ接続したことを表し、画像互換の認証ではない。

### Viewer側のテスト環境を構築する

既存のSwiftテストとproduction compiler／executorを土台にする。常設の自己完結fixtureと外部素材corpusを分け、Windows版Dayoの基準画像は独立した比較段階として取得する。Dayo本体の実行環境がなくても、Viewerの受入・変換・GPU数値試験は設計できるが、Dayo画像互換の証明にはならない。

| 層 | 検査する内容 | 成功から言えること |
|---|---|---|
| 台帳 | 再帰列挙、原文／PMX／依存hash、controller対象、SDK・toolchain | 同じ入力を特定できる |
| 受入 | production capture、Jsonnet、strict IR、能力・数量・容量制限 | 契約に従う受理／拒否。GPU実行ではない |
| compile | uncached変換、pass／stage数、reflection、binding／stride／offset | 対象pipelineを作れる |
| GPU数値 | HDR ramp、sampler境界、typed resource、条件、端数、履歴、pass別readback | 共通入力で処理と数値が成立する |
| 通常live | PMX load、source owner、同一世代GPU成功＋positive actual-present、操作、保存復元 | 通常経路で原文が採用された |
| export | immutable入力、PTS、liveとの中間HDR、途中失敗、atomic commit | 指定した出力条件で成立する |
| Dayo比較 | 同一scene／時刻／controller／色条件の基準画像 | 対象caseでの画像互換 |
| 性能・耐久 | 同一ReleaseのA/B、tail、VMD時計、pose age、CPU/GPU・資源、10分 | 測定条件内での性能・安定性 |

現存する[ProgramTests](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Tests/VMDViewerTests/FxDayoProgramTests.swift)は依存・IR・ABI等、[ProgramGPUTests](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Tests/VMDViewerTests/FxDayoProgramGPUTests.swift)は合成GPUと教材、[SceneIntegrationTests](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Tests/VMDViewerTests/FxDayoSceneIntegrationTests.swift)はPMX・live・export、[FailsafeTests](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Tests/VMDViewerTests/FxDayoFailsafeTests.swift)は故障・隔離を扱う。ただし外部原文の7 pass／12 stage試験はMotionBlur向けで、任意の20本へそのまま差し替えるrunnerではない。

GPU／統合群の既存opt-inは`VMD_FXDAYO_SOURCE`と`VMD_FXDAYO_TOOLCHAIN`、GUIは追加の`VMD_FXDAYO_GUI=1`である。toolchain環境変数を明示rootとして使う試験と、bundle／DEBUGの既定toolchainを探すproduction経路は異なる。実際に使ったbinaryとSDKのhashを記録する。2026-10-14にはローカルtoolchain 16ファイルとSDK 6 headerのmanifest一致を読取確認したが、再実行してはいない。[環境記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/ENVIRONMENT.json)

未知原文の証明には、整合した改名で出力が変わらないこと、簡単な式変更で対象画素が変わること、include変更でcacheが更新されることを使う。source owner・program identity・実行pass・採用出力を記録し、nativeやbaselineへの退避を原文成功へ数えない。既知adapterのterminal拒否を回避する目的の改名とは区別する。

集計は段階別に、検出件数、実行件数、受入、期待した拒否、予期しない失敗、skip、未実施を残す。外部rootを指定しない試験はskipにできるが、指定したrootがない／0件の場合は失敗とする。拒否試験のpassを素材の実行成功数へ加えない。

exportは開始時の拒否と、1 frame以上をappendした後のactive resource／encoder／GPU失敗を分ける。後者でもrun失敗、progress 1.0未通知、既存finalのhash保持、temporary cleanupを確認する。GPU比較の浮動小数点許容差はformatと値域からcaseごとに定め、既存教材の閾値を全素材へ流用しない。

20件corpus runner、汎用case manifest、Dayo基準画像の比較環境は**構築案**であり、今回追加した機能ではない。最初に台帳とproduction受入診断、次に小さなGPU fixture、その後に通常経路・Dayo比較・性能へ進む。[具体的な構築案と受入条件](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/TEST_ENVIRONMENT.md)

## 既存effectを両環境へ持ち込む

### そのまま実行できる部分を見極める

既存effectは、まず定義を評価した後のpassと依存を一覧にする。ファイルの見た目が短くても、Jsonnet importからcompute、別controller、履歴resourceが追加されることがある。`.fx`を`.fxdayo`へ改名しても、MMEの意味や実行APIは変換されない。

| 元effectの構成 | 選ぶ経路 |
|---|---|
| 現行profile内のpostprocess | 原文実行を確認し、式変更の反映と両環境の結果を試験する |
| include配置や説明fieldだけがprofile外 | 原版を保管し、作者が管理する移植版へ変更点を明示。依存やmetadataの修正も両環境で再確認する |
| 追加scene入力、履歴、copy等を必要とする | 汎用runtimeの不足capabilityとして報告し、対応profileの追加を待つか別途実装する |
| deformやrenderer、強い固有ABIを必要とする | native adapterによる移植か、新categoryのruntime開発を選ぶ |

機能を削除してViewerで読めるようにした版は、元effectそのものの互換対応とは区別する。元source、移植版、変更理由、対応条件、比較結果を別々に保持する。

### native adapterを追加する場合

native adapterはViewer本体の開発を伴う。作者が`.fxdayo`だけを書き換えて任意のMetal実装を登録する仕組みではない。追加する場合は次の順で契約を固定する。

1. 元sourceとPMX、sidecar、controller、resource、pass順、頂点ABI、対象Dayo版を特定する。
2. sourceそのものの一致を要求する範囲と、構造から近似できる範囲を分ける。SHAは作者識別や画像品質認証に使わない。
3. typed providerと実行ownerを登録し、通常load・live・exportへ接続する。descriptorの登録だけでは描画対応にならない。
4. deformでは出力がどの段階の頂点かを固定する。完成したskin済み頂点なら既定skinを重ねず、current/previousを別々に供給する。
5. controllerとposeの世代、GPU失敗、保存復元、画像と数値を確認する。

sourceのbyte一致が必要な既知adapterでは、コメントや空白の編集でもhashが変わる。動作例に合わせるための安易な整形や改名判定を入れず、元契約と選択されたownerを確認する。[adapter設計契約](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/skills/mmd-fxdayo-adapter-engineering/references/adapter-resolution-contract.md)、[登録時の確認事項](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/skills/mmd-fxdayo-adapter-engineering/references/native-profile-checklist.md)

## 同梱postprocess 20本から見える拡張課題

2026-10-14にDayo 1.30の`postprocess/`以下を`Test/`も含めて再帰列挙した。全20本に同名PMXが存在する。単純JSONとして読めたのは7本、コメント・末尾commaを読取時だけ除いた構造整理では17本、Jsonnetの式等が残るものは3本だった。これは構文・実行の合否や「17本対応」を意味しない。今回Jsonnet評価、compile、GPU実行、PMX内部のcontroller解決は行っていない。

次表は名前別adapterを追加する分類ではなく、共通能力を検証するための素材群である。完全なhash、20行の個別制約、依存とsource位置は[互換性研究](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/COMPATIBILITY.md)と[素材台帳](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/CORPUS.json)を参照する。

| 素材群 | 件数 | 共通の研究課題 |
|---|---:|---|
| CompositionLines、NTSC、ACESCg、ACESTonemap | 4 | headerの主要構造に明白な阻害がない静的候補。依存・shader・controller・色処理の実行確認は必要 |
| Panini、AddNoise、FXAA、ColorGradingSDR、diffusion | 5 | BORDER、metadata／slider、UNORM、pass macro、色処理の順序。全て同じ追加だけで動くとは限らない |
| ExpensiveLens、streak | 2 | mip生成、LOD、sampler、controller情報 |
| cross、AbbeFeedback | 2 | 外部image、texture UAV、clear／copy、feedback。AbbeFeedbackは依存配置も要確認 |
| DoF、DoFStochastic、MotionBlur | 3 | bone位置、時計、深度・scene入力、履歴、端数dispatch。MotionBlurの既存証拠を他素材へ広げない |
| OverDrawn、Skywalker | 2 | scene再描画・DSV、skybox／sampling table等のhost producer |
| fog、fluid3D | 2 | 外部／配列controller、3D・共有資源、材質・光源、状態更新とseek／export |

Fog／Fluidは単純な画面加工と分けて設計する。共有resourceは名前を一致させるだけでは足りず、producer／consumer、shape・format、世代、実行順、失敗の伝播、GPU完了までの寿命が必要。現行のownerごとのnamed resourceへ、無条件で別attachmentのtextureを結び付けない。

実装の研究順序は、20件の段階別試験を先に用意し、共通2Dと色の順序、functional pass／mip、typed controller／scene入力、3D・共有simulationへ進む。各段階でschema・IR・reflection・executor・保存・live／exportを一緒に扱う。取り込めるfieldを増やしただけでは対応完了にしない。原本、修復fixture、作者が管理する移植版を別々に評価し、原文が変わったことを隠さない。

## 参照資料と調査基準

初稿の調査日は2026-10-06。Viewerの当時のHEADは`6c83be79a10eda0a15a2da6e5fda103d2b49e274`で、未コミット変更を含む。当時読んだファイルのSHAは[初稿の参照snapshot](SOURCE_SNAPSHOT.json)へ保持する。2026-10-14の研究は別の[基準](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/BASELINE.json)・[素材台帳](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/CORPUS.json)・[環境記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/ENVIRONMENT.json)に結び付け、初稿のsnapshotを上書きしない。

| 資料 | 根拠に使う範囲 |
|---|---|
| [Dayo公式解説](https://github.com/pennennennennennenem/MikuMikuDayo/blob/main/tutorial/fxdayo.md) | 形式、category、起動方式の概要。公開mainを配布1.30と同一とは扱わない |
| ローカルDayo 1.30の`src/YRZFx.ixx` | 定義生成、controller、`ParsePassCond`と`PassCond`。pathとhashはsnapshotに記録 |
| ローカル1.30の`postprocess/motionblur/MotionBlur.fxdayo` | system include、複数pass、履歴、端数dispatchの具体例 |
| [同梱SDK manifest](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Resources/Dayo130SDK/manifest.json) | headerの出典とhash。対応upstream commitは未確認 |
| [v0.56.16実装記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-06-motionblur-generic-proof-plan/IMPLEMENTATION.md) | 既存の限定実行・保存・動画検証。今回の再試験結果ではない |
| [build402 Release記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-06-motionblur-generic-proof-plan/RELEASE.md) | 同梱compiler、署名、GUI読込・1024×576短尺出力。Dayo画像比較と正式性能は未受入 |
| [2026-10-14 postprocess研究](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-14-fxdayo-postprocess-research/README.md) | 20原文の静的要求、現行コードの制約、色処理・依存・テスト環境案。動作試験ではない |

v0.56.20では`STATUS.md`と旧adapter文書の全面未実装という記述も更新した。当時の実行根拠は[v0.56.20の実装記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-07-fxdayo-interface-v05620/IMPLEMENTATION.md)へ保持し、現在の能力は実コードで再確認する。今回の更新はWindows版Dayoの教材実行・同条件画像比較、20本の動作、正式性能を新たに検証したものではない。


## 停止・再試行・保存（v0.56.21で導入）

初回の未知原文は、PMXと原文bytesを読み込んだ後に別jobで検査する。PMX表示と保存はcompile完了を待たない。未承認fingerprintは「試行待ち」となり、「この原文を試す」で一度の実行を許可する。既存projectの明示的な原文選択は継承する。

Metal／LE、RealTime、AA、native混在、材質や内部寸法の不適合は原文を一時停止し、設定を維持して通常表示を続ける。適合条件へ戻ると再検査する。encode／GPU失敗とwatchdogは実行世代を隔離し、resizeや再生操作では解除しない。「再試行」は未完了GPU処理が退役してから使える。「効果OFF」は意図として保存し、原文やcontrollerは削除しない。

採用はViewerの実表示を待つため、別ウインドウなどでViewerが覆われている間は「GPU成功と表示を待っています」が続く場合がある。エフェクト画面を閉じてViewerを表示してから、読込状況で採用結果を確認する。build410の実操作ではこの手順で採用を確認した。

通常画像と原文処理は別commandで実行する。原文が表示期限に間に合わない場合は同じ姿勢の通常画像を使用し、500 ms watchdogでは新規試行を停止する。timerでGPUを取消したり未完了資源を再利用したりはしない。共有GPUのhangやdevice失効で通常描画も失敗する場合まで、無停止を保証するものではない。

原文packageの保存はschema25で導入し、schema27で実行ON／OFF・承認fingerprintの保存を追加した。v0.56.42のproject全体のcurrent schemaは33で、明示した色契約を保存する場合はminimumReaderVersion33を要求する。旧nilの色設定は従来のHDR契約とreader条件を保持する。正常なpackageはcompilerが使えなくても復元できる。CRC／hashやpathの破損は引き続きproject読込失敗とする。失敗・未完了試行の記録は端末内へ保存し、同じ環境での自動再実行を抑止する。[保存形式](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Scene/SceneDocument.swift)、[reader検査](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/Sources/VMDViewer/Project/ProjectArchiveReader.swift)

動画は停止中の有効な原文があると既定で開始を拒否する。必要な場合だけ動画書出し画面の「停止中の効果を除いて書き出す」を選び、表示された除外対象を確定する。OFFの効果は通常どおり実行しない。残った効果の実行途中の失敗は書出し失敗となり、不完全な完成動画へ置き換えない。

詳細は[フェイルセーフ設計](FAILSAFE_DESIGN.md)と[実装・検証記録](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-07-fxdayo-failsafe-v05621/IMPLEMENTATION.md)を参照する。
