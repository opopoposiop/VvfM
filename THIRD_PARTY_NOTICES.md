# Third-party notices

## この文書とライセンスの適用範囲

この文書は、アプリに使用する第三者ライブラリ・画像・エフェクト等の通知を掲載するものです。VvfMの公開文書に適用する[MIT License](LICENSE)、将来の独自バイナリに適用する[補足EULA案](Licenses/VMDViewer-EULA-ja.md)、第三者部分の元の許諾は、[LICENSING.md](LICENSING.md)のとおり区別します。EULAの解析禁止条項で第三者ライセンスや既に付与されたMITの権利を制限しません。

補足EULAは公開案であり、既存版の条件を変更しません。各配布版の適用条件は、そのReleaseと同梱文書を確認してください。本文に記すソースのパスは開発側・上流の参照元を表し、VvfMでアプリ本体のソースコードを公開する案内ではありません。

## 追加収録した許諾原文

- [MMDayo_MobFesのMIT原文](Licenses/MMDayo_MobFes/LICENSE)：Copyright (c) 2026 opopoposiop, opoposio。元の許諾を保持します。原文の収録によって外部のPMX・エフェクト一式を新たに配布するものではありません。
- Bullet内の追加通知・出典は[ライセンス原文一覧](Licenses/README.md)と[原文の取得元・ハッシュ](Licenses/manifest.json)を参照してください。

## Bullet Continuous Collision Detection and Physics Library 3.25

VMD Viewer includes the required Bullet 3.25 bridge sources under
`Sources/MMDBulletBridge`.  The source distribution carries the following
zlib license notice (also present in `Sources/MMDBulletBridge/Bullet-LICENSE.txt`):

The files in this repository are licensed under the zlib license, except for the files under 'Extras' and examples/ThirdPartyLibs.

Bullet Continuous Collision Detection and Physics Library
http://bulletphysics.org

This software is provided 'as-is', without any express or implied warranty.
In no event will the authors be held liable for any damages arising from the use of this software.
Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it freely,
subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.

### PMX 2.1 SoftBody subset (v0.56.0)

The required BulletSoftBody subset (34 headers and 9 C++ files) is from the
official Bullet `3.25` tag. Original file hashes are recorded in
[the provenance manifest](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-09-29-pmx21-conformance-review/BULLET_SOFTBODY_UPSTREAM.json).
`BulletSoftBody/btSoftBody.cpp` is modified by VMD Viewer: a symmetric
pseudoinverse handles singular planar-cloth / collinear-rope pose and cluster
inertia matrices. The change is marked in that file; it is not an unmodified
upstream source. No external Bullet runtime dependency is introduced.

### Opt-in PMX 2.75 compatibility (v0.56.1)

VMD Viewer modifies the vendored Bullet 3.25 files `btSoftBody.h/.cpp`,
`btContactSolverInfo.h`, `btSequentialImpulseConstraintSolver.cpp`, and
`btConeTwistConstraint.h/.cpp` to select known Bullet 2.75 aero, anchor,
contact and motor rules per world/body. Alterations are marked in source.
The original notices and the numerical protections above remain intact.
The app still links only the bundled 3.25-based library; this is not a full
Bullet 2.75 replacement. Original reference provenance and limits are in
[the comparison](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-09-30-bullet-275-325-pmx21-comparison/REVIEW.md)
and [implementation](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-09-30-bullet-mode-v0561/IMPLEMENTATION.md).

## ZIPFoundation 0.9.20

VMD Viewer uses ZIPFoundation for ZIP container encoding and decoding.

- Project: https://github.com/weichsel/ZIPFoundation
- Version: 0.9.20
- Resolved revision: 22787ffb59de99e5dc1fbfe80b19c97a904ad48d
- License: MIT

The following notice is reproduced from the ZIPFoundation distribution:

MIT License

Copyright (c) 2017-2025 Thomas Zoechling (https://www.peakstep.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Three.js r169 shared Toon textures

The ten PNG resources in `Sources/VMDViewer/Resources/SharedToon` are the
unchanged embedded shared Toon images (indices 1 through 10) from
https://github.com/mrdoob/three.js/blob/r169/examples/jsm/loaders/MMDLoader.js.
PMX shared Toon indices 0 through 9 map to toon01.png through toon10.png.

The MIT License

Copyright © 2010-2024 three.js authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

## Holographic / ikHolographic

- 原エフェクト: ikeno（@ikeno_mmd）。使用・改変・再配布の許可は同梱の `Sources/VMDViewer/Resources/BuiltinEffects/Holographic/original_readme.txt`（CP932）を参照。配布appでは `VMDViewerForMac_VMDViewer.bundle/BuiltinEffects/Holographic/` に収容する。
- `.fxdayo`契約・Metal移植の参照元: [opopoposiop/MMDayo_Holographic](https://github.com/opopoposiop/MMDayo_Holographic)、commit `d4b8960db2d27d49ff1b856a783231e969ceac63`。
- `Sources/VMDViewer/Effects/IkHolographicContract.generated.swift`、Holographic関連実装・テスト素材は同repoの配布patchを基に現行Viewerへ統合・修正。原作者のREADMEを変更せず保持する。

## Rhinestone

- 原エフェクト・画像: ikeno（@ikeno_mmd）、Rhinestone Ver 0.02（2016-03-26）。通常版 `Rhinestone.fx` と発光用 `AL_Rhinestone.fx` を基にViewer専用のMetal実装を作成。
- 原readmeには利用・改造・再配布自由、連絡不要との記載がある。原文（CP932）を `Sources/VMDViewer/Resources/BuiltinEffects/Rhinestone/readme.txt` に変更せず保持する。
- source 2ファイル、PNG 20ファイル（Supplementsを含む参考素材）、原readmeを同梱。配布appでは `VMDViewerForMac_VMDViewer.bundle/BuiltinEffects/Rhinestone/` に収容し、共通の内容manifestで識別する。
- Viewer版は座標・微分・Toon・影を既存Metal描画へ接続した近似。発光用の計算はViewerのHDR emission／Bloomへ接続し、MMEやAutoLuminous全体の互換を表明するものではない。原ファイルとViewer側の実装を区別する。

## Generic `.fxdayo` source program toolchain (v0.56.16)

The app bundles project-built compiler tools in `Contents/Resources/FxDayoToolchain`.
They do not require Homebrew on the user's Mac. Exact revisions and file hashes
are recorded in the bundled `manifest.json`; upstream notices are preserved in
its `licenses` directory.

- [Google Jsonnet](https://github.com/google/jsonnet), v0.21.0 / `bbb38f1020be1f5aed560928fb839b2c448cefb4`: Apache-2.0, with the embedded md5, nlohmann/json, rapidyaml, c4core and fast_float notices. The amalgamated rapidyaml header is retained verbatim to preserve its embedded dependency notices.
- [Microsoft DirectXShaderCompiler](https://github.com/microsoft/DirectXShaderCompiler), v1.9.2609 / `01b62ad47db7dee3dd33f90e7339cf9e860b3f93`: upstream LLVM NCSA license and third-party notices, including the HLSL headers under Apache-2.0 with LLVM Exceptions, including its pinned DirectX-Headers, SPIRV-Headers and SPIRV-Tools dependencies.
- [Khronos SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross), `aa217aeb6c9f0ace7a0ab233b28807edf45eb165`: Apache-2.0.
- [MikuMikuDayo](https://github.com/pennennennennennenem/MikuMikuDayo) 1.30 SDK: six original HLSL headers under `Sources/VMDViewer/Resources/Dayo130SDK`, byte-preserving copies from the 1.30 distribution. Copyright (c) 2024 pennennennennennenem, MIT. The original license is `LICENSE.txt` in that directory, with header hashes in `manifest.json`. The distribution's corresponding upstream commit is unverified.

`scripts/build-fxdayo-toolchain.sh` builds the pinned tools locally with a macOS 14.0 deployment target; `scripts/stage-fxdayo-toolchain.py` stages their binaries and notices. The MikuMikuDayo application and the external MotionBlur PMX/effect test asset are not bundled with VMD Viewer.

## msToonCoordinator v2.1 shadow-color equations

The optional ToonShader HQ Type2 shadow-color mode adapts the HSY conversion and
automatic shade-color equations from ShadeColor/ShadeColor_common.fxsub in
msToonCoordinator v2.1 by ましまし (@Mashimashi_mmd).
The reference header credits full.fx v1.4 by 舞力介入P as its base.

- Author's explanation: https://note.com/mashimashi_note/n/n2c2144638054
- Reference readme terms: 「エフェクト自体の使用・改変・再配布は自己責任で実行してください。」
- Modified implementation: Sources/VMDViewer/Renderer/ToonShadowColorShader.swift
- [Reference hashes and implementation scope](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/36206626a7214ad8b8de5bba362189a38c285529/reports/2026-10-08-toon-shadow-color/IMPLEMENTATION.md)

This is a modified Metal implementation of the standard automatic shadow-color
transform, with guarded achromatic conversion and HQ color-space/HDR handling.
It does not bundle or reproduce the complete original MME post-effect,
ExcellentShadow, edge chroma/SSS, controllers, or normal-map workflow.
