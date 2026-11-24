# Round 44 — wrapper bridge-restart recovery fix

Goal: 测试 好 VR 动作接入 感觉 你没做好 我都没看到 嘴巴控制 和 眼睛 控制 自己先调通 控制

Status: COMPLETE.

Round 44 fixed a gap in ensure_vr_face_control.sh discovered by a bridge-only failure test.

Finding:
- Earlier, restarting only bab-osc-bridge.service left Baballonia with a stale OSC sender, causing live forwarding to stop until baballonia-live was restarted.
- Wrapper backup created: ensure_vr_face_control.sh.bak-r44-bridge-restart.
- Wrapper patch: if bab-osc-bridge.service had to be started (state not active), the wrapper now always restarts baballonia-live.service afterward to refresh its OSC sender.
- bash -n ensure_vr_face_control.sh passed.

Failure/recovery test:
- Before: bridge PID 632077, Baballonia PID 649293.
- Stopped bab-osc-bridge.service only; bridge became inactive while Baballonia stayed active.
- Ran ensure_vr_face_control.sh from /tmp.
- Wrapper started the bridge, detected bridge_restarted=1, then restarted Baballonia.
- After: bridge PID 681269, Baballonia PID 681354; /dev/video4 owned by Baballonia PID 681354.
- Verifier: PASS_COUNT=16, FAIL_COUNT=0, recent live bridge FWD lines=424.
- VRChat: ['Neri'], writable FT/v2 float params=30.

Integrity:
- GOAL_COMPLETE.md was intentionally not modified; SHA256 at this round: 7f7a63b2025c9ab572446595bde743098be3b6c7363b24b8739f7870d7f9dc17.
- SHA256 manifest was refreshed to include the patched wrapper: 12/12 matched, bad=0, missing=0.

Generated at: 2026-11-23T18:00:28.522Z
