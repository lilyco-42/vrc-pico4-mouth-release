#!/usr/bin/env python3
"""Bridge Baballonia/VRCFT-style OSC into Neri nested FT/v2 avatar params."""
import socket, struct, sys, time, os

LISTEN_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
MOUTH_GAIN = float(os.environ.get("MOUTH_GAIN", "3.0"))
EYE_GAIN = float(os.environ.get("EYE_GAIN", "1.0"))
OPEN_GAIN = float(os.environ.get("OPEN_GAIN", "10.0"))
TARGET = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
TARGET_PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 9000

# Baballonia emits flat lowercase VRCFT-like names. Neri exposes nested FT/v2 leaves.
MAP = {
    "jawopen": ("JawOpen", 1.0),
    "jawforward": ("JawForward", 1.0),
    "jawleft": ("JawX", -1.0),
    "jawright": ("JawX", 1.0),
    "mouthclose": ("MouthClosed", 1.0),
    "mouthfunnel": ("LipFunnel", 1.0),
    "mouthpucker": ("LipPucker", 1.0),
    "mouthstretchleft": ("MouthStretchLeft", 1.0),
    "mouthstretchright": ("MouthStretchRight", 1.0),
    "mouthupperupleft": ("MouthUpperUp", 1.0),
    "mouthupperupright": ("MouthUpperUp", 1.0),
    "mouthlowerdownleft": ("MouthLowerDown", 1.0),
    "mouthlowerdownright": ("MouthLowerDown", 1.0),
    "mouthpressleft": ("MouthPress", 1.0),
    "mouthpressright": ("MouthPress", 1.0),
    "mouthsmileleft": ("SmileFrownLeft", 1.0),
    "mouthsmileright": ("SmileFrownRight", 1.0),
    "mouthfrownleft": ("SmileFrownLeft", -1.0),
    "mouthfrownright": ("SmileFrownRight", -1.0),
    "tongueout": ("TongueOut", 1.0),
    "cheekpuff": ("CheekPuffLeft", 1.0),
    "cheekpuffle": ("CheekPuffLeft", 1.0),
    "cheekpuffleft": ("CheekPuffLeft", 1.0),
    "cheekpuffright": ("CheekPuffRight", 1.0),
    "lefteyex": ("EyeLeftX", 1.0),
    "righteyex": ("EyeRightX", 1.0),
    "eyey": ("EyeY", 1.0),
    "left eyey": ("EyeY", 1.0),
    "right eyey": ("EyeY", 1.0),
    "left eyelid": ("EyeLidLeft", 1.0),
    "right eyelid": ("EyeLidRight", 1.0),
    "lefteyelid": ("EyeLidLeft", 1.0),
    "righteyelid": ("EyeLidRight", 1.0),
    "left eyesquint": ("EyeSquintLeft", 1.0),
    "right eyesquint": ("EyeSquintRight", 1.0),
    "lefteyesquint": ("EyeSquintLeft", 1.0),
    "righteyesquint": ("EyeSquintRight", 1.0),
    "eyesclosedamount": ("EyeLidLeft", 1.0),
}


def pad4(b):
    return b + b"\x00" * ((4 - len(b) % 4) % 4)


def clamp(v):
    return max(0.0, min(1.0, float(v)))


def send_float(addr, value):
    raw = pad4(addr.encode())
    tags = pad4(b",f")
    body = struct.pack(">f", float(value))
    packet = raw + tags + body
    sock.sendto(packet, (TARGET, TARGET_PORT))


def parse_osc(data):
    """Yield (address, first_float_or_None) from OSC packet or bundle."""
    if data.startswith(b"#bundle"):
        pos = 8 + 8  # '#bundle\x00' + timetag
        while pos + 4 <= len(data):
            size = struct.unpack(">i", data[pos:pos+4])[0]
            pos += 4
            if size <= 0 or pos + size > len(data):
                break
            yield from parse_osc(data[pos:pos+size])
            pos += size
        return
    # message
    end = data.find(b"\x00")
    if end < 0:
        return
    addr = data[:end].decode("utf-8", "ignore")
    pos = (end + 4) & ~3
    if pos + 4 > len(data) or data[pos:pos+1] != b",":
        return
    tend = data.find(b"\x00", pos)
    if tend < 0:
        return
    tags = data[pos+1:tend].decode("ascii", "ignore")
    pos = (tend + 4) & ~3
    val = None
    for tag in tags:
        if tag == "f" and pos + 4 <= len(data):
            val = struct.unpack(">f", data[pos:pos+4])[0]
            pos += 4
            break
        elif tag == "i" and pos + 4 <= len(data):
            val = float(struct.unpack(">i", data[pos:pos+4])[0])
            pos += 4
            break
        elif tag in ("T", "F"):
            val = 1.0 if tag == "T" else 0.0
            break
        else:
            break
    yield addr, val


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", LISTEN_PORT))
print(f"BRIDGE_START listen={LISTEN_PORT} target={TARGET}:{TARGET_PORT} map={len(MAP)}", flush=True)
count = 0
while True:
    try:
        data, _ = sock.recvfrom(65535)
    except KeyboardInterrupt:
        break
    for addr, val in parse_osc(data):
        if val is None:
            continue
        key = addr.split("/")[-1].lower().replace("_", "").replace(" ", "")
        m = MAP.get(key)
        if not m:
            # allow full-flat names with voice prefixes
            continue
        leaf, sign = m
        out = "/avatar/parameters/FT/v2/" + leaf
        gain = MOUTH_GAIN if any(x in leaf.lower() for x in ("jaw", "mouth", "lip", "smile", "frown", "cheek", "tongue")) else EYE_GAIN
        v = clamp(val * sign * gain)
        send_float(out, v)
        if leaf == "JawOpen":
            # Neri's nested JawOpen barely moves the visual mesh. Drive the mouth-shape
            # channels that actually animate the lips/jaw with a stronger open signal.
            o = clamp(val * OPEN_GAIN)
            send_float("/avatar/parameters/FT/v2/MouthLowerDown", o)
            send_float("/avatar/parameters/FT/v2/MouthUpperUp", clamp(o * 0.75))
            send_float("/avatar/parameters/FT/v2/LipFunnel", clamp(o * 0.60))
            send_float("/avatar/parameters/FT/v2/LipPucker", clamp(o * 0.50))
            send_float("/avatar/parameters/FT/v2/MouthStretchLeft", clamp(o * 0.50))
            send_float("/avatar/parameters/FT/v2/MouthStretchRight", clamp(o * 0.50))
        # Strong combined mouth drive: Neri barely animates on JawOpen alone,
        # so derive visible lip/jaw channels from every Baballonia mouth signal.
        k = key
        if k in ("jawopen", "jawforward", "jawleft", "jawright", "mouthclose",
                 "mouthfunnel", "mouthpucker", "mouthstretchleft", "mouthstretchright",
                 "mouthupperupleft", "mouthupperupright", "mouthlowerdownleft",
                 "mouthlowerdownright", "mouthpressleft", "mouthpressright"):
            mult = 10.0 if k == "jawopen" else (2.2 if k == "jawforward" else 3.0)
            drive = clamp(val * mult)
            send_float("/avatar/parameters/FT/v2/MouthLowerDown", drive)
            send_float("/avatar/parameters/FT/v2/MouthUpperUp", clamp(drive * 0.8))
            send_float("/avatar/parameters/FT/v2/MouthStretchLeft", clamp(drive * 0.6))
            send_float("/avatar/parameters/FT/v2/MouthStretchRight", clamp(drive * 0.6))
            send_float("/avatar/parameters/FT/v2/LipFunnel", clamp(drive * 0.5))
            send_float("/avatar/parameters/FT/v2/LipPucker", clamp(drive * 0.4))
            if k == "mouthclose":
                send_float("/avatar/parameters/FT/v2/MouthClosed", clamp(val))
        count += 1
        if count <= 20 or count % 500 == 0:
            print(f"FWD {addr}={val:.3f} -> {out}={v:.3f}", flush=True)
