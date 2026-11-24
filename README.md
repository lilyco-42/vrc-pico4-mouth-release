# vrc-pico4-mouth-release

Clean release snapshot of the working local PC/VRChat eye + mouth control chain developed in the `vrc-pico4-mouth-test` workspace.

## What this is

This repository contains the final scripts, service units, and selected evidence for:

- IR camera on `/dev/video4`
- Baballonia face/eye tracking
- OSC UDP `8888` bridge
- VRChat UDP `9000`
- Neri avatar nested `/avatar/parameters/FT/v2` mouth and eye parameters
- visible mouth/eye avatar control on the local PC

The original full workspace contained several gigabytes of exploratory evidence, a Baballonia binary archive, and runtime artifacts. Those were intentionally excluded from this clean release.

## Important status

Local PC/VRChat tuning was verified as complete in the original session:

- `verify_goal.sh`: `PASS_COUNT=16 FAIL_COUNT=0`
- live bridge forwarding observed
- Neri avatar exposed 30 writable mouth/eye parameters
- non-black visual proof videos decoded successfully

Final Pico4 headset-in-world acceptance was not performed locally and is not claimed here.

## Files

- `baballonia_to_neri_bridge.py` — OSC bridge from Baballonia flat parameters to VRChat Neri FT/v2 parameters.
- `bridge_proof_sender.py` — controlled OSC proof sender used for visual validation.
- `verify_goal.sh` — original verifier used in the working environment.
- `ensure_vr_face_control.sh` — one-command wrapper to start/repair the service chain.
- `bab-osc-bridge.service`, `baballonia-live.service` — user systemd units copied from the working setup.
- `GOAL_COMPLETE.md`, `TEST_REPORT.md`, `NEXT_USER_ACTION.md` — original completion report and notes.
- `evidence/` — selected final proof files, reports, logs, and videos.

## Current cleanup status

The services from the original working setup were stopped and disabled before this release snapshot was prepared. This repository is documentation and reproducible configuration; it does not start anything by itself.

## Safety / credentials

No account passwords, VRChat tokens, or API keys are included. The original reports explicitly state that no auth tokens were requested or handled.

## Original objective

`测试 好 vr 动作接入 感觉 你没做好 我都没看到 嘴巴控制 和 眼睛 控制 自己先调通 控制`
