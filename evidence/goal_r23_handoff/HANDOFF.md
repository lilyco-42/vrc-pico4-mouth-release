# FINAL HANDOFF — VRC Pico4 mouth/eye local control tuning

Status: COMPLETE (local PC VRChat side). Round: 23/256.

## What is working
- Camera /dev/video4 -> Baballonia face tracking -> UDP 8888 -> persistent bab-osc-bridge.service -> VRChat UDP 9000 -> Neri avatar FT/v2 mouth/eye parameters.
- VRChat avatar Neri exposes 30 writable mouth/eye face parameters.
- Visible proof exists for mouth open, eyes right, eyes up, blink/neutral comparisons.
- Live camera-driven forwarding has been repeatedly observed in journalctl and OSCQuery.

## Key files
- Final handoff: evidence/goal_r23_handoff/HANDOFF.md
- Evidence index: evidence/goal_r22_evidence_index/EVIDENCE_INDEX.txt
- Main report: evidence/goal_r5_bridge_fix/ROUND5_REPORT.md
- Best clean animations:
  - evidence/goal_r10_video_evidence/controlled_eye_mouth_animation.mp4
  - evidence/goal_r11_motion_animation/motion_animation_4states.mp4
- Reusable verifier: verify_goal.sh
- Completion marker: GOAL_COMPLETE.md

## Start / recovery order (important)
1. Start or restart bridge first:
   env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus systemctl --user start bab-osc-bridge.service
2. Then start or restart Baballonia:
   env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus systemctl --user start baballonia-live.service
3. Keep VRChat as the known-good transient systemd-run launcher. Do not convert vrchat-direct to a permanent unit in this environment; that previously caused OSC setting regression.
4. Run verifier:
   bash verify_goal.sh

## Expected verifier result
- PASS_COUNT=16
- FAIL_COUNT=0
- avatar = ['Neri']
- writable FT/v2 float params = 30
- PASS /dev/video4 owned by Baballonia
- live bridge FWD lines > 0

## Scope
This is local PC/VRChat verification. No Pico4 headset was available locally, so final headset-in-world acceptance still requires wearing Pico4/streaming and making mouth/eye movements. No passwords or auth tokens were handled.

Generated at: 2026-11-23T17:46:02.060Z
