#!/bin/bash
set -euo pipefail
ROOT="/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test"
OUT="/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r13_final_check"
systemctl_user() { env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus systemctl --user "$@"; }
journal_user() { env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus journalctl --user "$@"; }
PASS=0
FAIL=0
echo "== service state =="
for u in vrchat-direct baballonia-live bab-osc-bridge.service; do
  st="$(systemctl_user is-active "$u" || true)"
  echo "$u = $st"
  if [ "$st" = active ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
done
en="$(systemctl_user is-enabled bab-osc-bridge.service || true)"
echo "bab-osc-bridge.service enabled = $en"
if [ "$en" = enabled ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
echo "== sockets and camera =="
if ss -lnup | grep -q '127.0.0.1:8888'; then echo 'PASS UDP 8888 bridge bound'; PASS=$((PASS+1)); else echo 'FAIL UDP 8888'; FAIL=$((FAIL+1)); fi
if ss -lnup | grep -q ':9000'; then echo 'PASS UDP 9000 VRChat bound'; PASS=$((PASS+1)); else echo 'FAIL UDP 9000'; FAIL=$((FAIL+1)); fi
if fuser -v /dev/video4 2>&1 | grep -q Baballonia; then echo 'PASS /dev/video4 owned by Baballonia'; PASS=$((PASS+1)); else echo 'FAIL /dev/video4 owner'; FAIL=$((FAIL+1)); fi
echo "== OSCQuery avatar/params =="
python3 - <<'PY'
import json, urllib.request
import re, pathlib
logdir=pathlib.Path('/home/lilyco/.local/share/Steam/steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat')
logs=sorted(logdir.glob('output_log_*.txt'))
port=None
for log in reversed(logs):
    text=log.read_text(errors='ignore')
    hits=re.findall(r'OSCQuery on (\d+)', text)
    if hits:
        port=int(hits[-1]); break
if not port: raise SystemExit('OSCQuery port not found')
r=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=5))['CONTENTS']
av=r['avatar']['CONTENTS']
ft=av['parameters']['CONTENTS']['FT']['CONTENTS']['v2']['CONTENTS']
writable=[k for k,v in ft.items() if v.get('TYPE')=='f' and v.get('ACCESS')==3]
print('avatar =', av.get('name',{}).get('VALUE'))
print('writable FT/v2 float params =', len(writable))
for k in ['JawOpen','MouthLowerDown','MouthUpperUp','EyeLeftX','EyeRightX','EyeY']:
    print(k, ft.get(k,{}).get('VALUE'))
assert len(writable) >= 30
assert all(k in ft for k in ['JawOpen','MouthLowerDown','MouthUpperUp','EyeLeftX','EyeRightX','EyeY'])
print('PASS OSCQuery face params')
PY
if [ $? -eq 0 ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
echo "== live bridge traffic =="
fwds="$(journal_user -u bab-osc-bridge.service --since "10 minutes ago" --no-pager | grep -c "FWD /" || true)"
echo "recent FWD lines = $fwds"
if [ "${fwds:-0}" -gt 0 ]; then echo "PASS live camera OSC forwarding"; PASS=$((PASS+1)); else echo "FAIL live forwarding"; FAIL=$((FAIL+1)); fi
echo "== evidence files =="
for f in "/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r5_bridge_fix/ROUND5_REPORT.md" "/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r5_bridge_fix/contact.png" "/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r10_video_evidence/controlled_eye_mouth_animation.mp4" "/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r11_motion_animation/motion_animation_4states.mp4" "/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r11_motion_animation/motion_contact.png" "/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/GOAL_COMPLETE.md"; do
  if [ -s "$f" ]; then echo "PASS $(basename "$f")"; PASS=$((PASS+1)); else echo "FAIL missing $(basename "$f")"; FAIL=$((FAIL+1)); fi
done
echo "== videos decode nonblack =="
python3 - <<'PY'
from PIL import Image, ImageStat
from pathlib import Path
import subprocess
root=Path('/home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test')
vids=[root/'evidence/goal_r10_video_evidence/controlled_eye_mouth_animation.mp4', root/'evidence/goal_r11_motion_animation/motion_animation_4states.mp4']
for v in vids:
    out=Path('/tmp')/(v.stem+'_r13.png')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(v),'-frames:v','1',str(out)],check=True)
    im=Image.open(out).convert('RGB'); st=ImageStat.Stat(im)
    mean=sum(st.mean)/3
    print(v.name,'mean',round(mean,2))
    assert mean > 5
print('PASS videos decode nonblack')
PY
if [ $? -eq 0 ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
echo "== summary =="
echo "PASS_COUNT=$PASS FAIL_COUNT=$FAIL"
[ "$FAIL" -eq 0 ]
