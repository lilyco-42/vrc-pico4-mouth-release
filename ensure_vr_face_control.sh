#!/bin/bash
set -euo pipefail
ROOT="/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test"
E=(env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus)
"${E[@]}" true

echo "== ensure VR face control stack =="

bridge_restarted=0
bridge_state="$("${E[@]}" systemctl --user is-active bab-osc-bridge.service || true)"
if [ "$bridge_state" = active ]; then
  echo "bab-osc-bridge.service already active"
else
  echo "starting bab-osc-bridge.service (state=$bridge_state)"
  "${E[@]}" systemctl --user start bab-osc-bridge.service
  bridge_restarted=1
  sleep 2
fi

bab_state="$("${E[@]}" systemctl --user is-active baballonia-live.service || true)"
if [ "$bridge_restarted" = 1 ]; then
  echo "bridge was restarted; restarting baballonia-live.service to refresh its OSC sender"
  "${E[@]}" systemctl --user restart baballonia-live.service
  sleep 8
elif [ "$bab_state" = active ]; then
  echo "baballonia-live.service already active"
else
  echo "starting baballonia-live.service (state=$bab_state)"
  "${E[@]}" systemctl --user start baballonia-live.service
  sleep 8
fi

vr_state="$("${E[@]}" systemctl --user is-active vrchat-direct.service || true)"
echo "vrchat-direct.service = $vr_state (kept as known-good transient launcher; not modified)"

echo
echo "== run full verifier =="
bash "$ROOT/verify_goal.sh"
