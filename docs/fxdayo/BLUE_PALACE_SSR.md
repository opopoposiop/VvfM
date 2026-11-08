# Blue Palace floor SSR profile

> VvfM収録注（2026-10-19）：開発版v0.56.49／build453（記録ID `3620662`）から取り込みました。本文はbuild423等の限定SSR profileと当時の検証を記した資料です。配布素材やWindowsでの画像同値を保証するものではありません。現在版との関係は[資料の案内](README.md)を参照してください。本取込ではビルド・実機試験を再実施していません。


`Blue_Palace_SSR.fxdayo` is a closed derivative of opopoposiop/MMDayo_SSR at commit `492907e7ef738fe25c529e93daef7db3f5dc9bfb`. Its source SHA is registered explicitly in `MMDayoSSRDefinition` and the native adapter registry. It uses the existing single SSR owner and shared live/export WorkingFloor pass.

Four exact sources remain supported: original v1 (lower radius 200, upper inner radius 109) and compact v2 (lower radius 100, upper inner radius 100, central treads starting at Z=44, side treads at radius 73). The joined v3 profile uses ten continuous treads: a 90-unit straight center tangent to elliptical side wings. The upper floor starts at their shared landing curve. The lowered v4 profile keeps only the first three treads and extends the upper floor at Y=6 over the former higher treads. Existing v1/v2/v3 projects retain their original footprints.

| Variant | First build | Exact source SHA-256 |
|---|---|---|
| Original v1 | 420 | `c65ee4c598dd3566482fad7c4fc83725c49958b50ce34327955e9b599b8f9c8d` |
| Compact v2 | 421 | `5a909e6818cb72a11edbc212682d66cea3bc3f5144f6343f5a768741fc529506` |
| Joined stairs v3 | 422 | `98013c6a6d8a05eb291d0572afea9c1175be2bb8f929549be6101ef9c9bcdf44` |
| Lowered stairs v4 | 423 | `834a3681f79238fbfa136bbd64ea96f8ec2aadff26e594e8b32368ab3d8b3c60` |

The profile recognizes Blue Palace stage02's circular lower floor (Y=0), central treads (v1–v3: Y=2..20; v4: Y=2,4,6), curved side treads (v1/v2: Y=4..20; v3: Y=2..20; v4: Y=2,4,6), and semicircular upper floor (v1–v3: Y=20; v4: Y=6). The center bone translates that fixed footprint. FloorSizeX/Z crop its bounds; stage scaling/rotation is outside this profile. Native live rendering requires ToonShader HQ.

Visible scene depth reconstructs a surface point. Its footprint, height, and geometric normal admit only horizontal floor surfaces. A reflected ray searches the current color/depth buffers, with a bounded 96-step search and six-step hit refinement. A miss contributes no reflection; there is no off-screen fallback. Composite preserves scene alpha. The existing MirrorScene resource/pass graph remains present for source ABI compatibility; this profile's reflection search does not consume its single-plane image.

This is an approximate Metal adapter. Passing parser/Metal tests does not establish MikuMikuDayo image equivalence. The distributed HLSL compiles with the bundled Dayo 1.30 SDK, but Windows runtime verification is deferred.

Validation for build423:

- Source SHA, controller ABI, edited-source rejection, and missing-controller rejection for all four profiles.
- Independent floor probes for central/side treads and footprint gaps; v4 verifies all three risers and the expanded upper floor.
- Production GPU DrawReflect/Composite readback for v1–v3's 11 heights and v4's four heights, foreground exclusion, alpha preservation, OFF, translated center, and resize. Left/right wing checks cover ten v3 treads and three v4 treads.
- Existing SSR MirrorScene/depth/alpha regression.
- Focused suite: 12 tests, 11 passed and one real-asset test skipped because its environment was not specified.
- Full serial suite with real assets enabled: 2,610 tests (2,547 passed, 63 conditionally skipped), zero failures; the real-asset test passed here.
- Actual lowered stage with HQ rim enabled: SSR ON/OFF changed 40,907 pixels, starfield frame 0/300 changed 18,767 pixels; backward seek had a maximum one-level channel difference (within the allowed tolerance, not byte-identical). These are export-renderer still frames, not a codec export or performance qualification.

The PMX assets, VMDs, black curtain texture, reduced stage geometry, and penlight layout belong to the separate PMX_stage/stage02 package. These are asset changes, not additional Viewer features.

The current Release candidate is v0.56.26/build423. The recording audit rechecked strict signing, all 829 current inputs against the embedded fingerprint, executable/dSYM UUID, ZIP CRC and every archived app file. Build422's saved input manifest also matches its artifact fingerprint, but four implementation files now differ because they include v4; its source match is historical. Build422's focused log contains 10 passes and one skip out of 11 tests, correcting the earlier wording that all 11 passed. The real-asset test passed in each build's full run.

The preceding paragraphs summarize the recorded build423 and build422 checks. This recording audit did not rebuild or rerun Swift/GUI tests. Version 0.56.26 and both artifacts are retained. Application binaries, ZIPs, dSYMs and full logs remain local in dist; source, tests, fixtures and documentation are recorded in Git.

Build423 GUI rendering/playback, codec export, Windows image equivalence, endurance and formal performance remain unverified; `release_adopted=false` and `performance_accepted=false`. Earlier build420/421 GUI records apply to their recorded inputs only. The earlier build422 and build421 results are historical and do not extend this validation scope.
