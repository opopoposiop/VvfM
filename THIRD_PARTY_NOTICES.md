# Third-party notices

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
[the provenance manifest](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/e2d50ce739684e1c83960646ef5c0135b513603f/reports/2026-09-29-pmx21-conformance-review/BULLET_SOFTBODY_UPSTREAM.json).
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
[the comparison](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/e2d50ce739684e1c83960646ef5c0135b513603f/reports/2026-09-30-bullet-275-325-pmx21-comparison/REVIEW.md)
and [implementation](https://github.com/opopoposiop/VMDviewer_for_Mac/blob/e2d50ce739684e1c83960646ef5c0135b513603f/reports/2026-09-30-bullet-mode-v0561/IMPLEMENTATION.md).

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
