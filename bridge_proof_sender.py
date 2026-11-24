#!/usr/bin/env python3
"""Send Baballonia-style OSC into the bridge for a fixed proof state."""
import socket,struct,sys,time
HOST=sys.argv[1] if len(sys.argv)>1 else '127.0.0.1'
PORT=int(sys.argv[2]) if len(sys.argv)>2 else 8888
STATE=sys.argv[3] if len(sys.argv)>3 else 'mouth_open'
DUR=float(sys.argv[4]) if len(sys.argv)>4 else 8.0
STATES={
 'neutral': {'jawOpen':0.0,'mouthClose':0.0,'mouthFunnel':0.0,'mouthPucker':0.0,'mouthStretchLeft':0.0,'mouthStretchRight':0.0,'mouthUpperUpLeft':0.0,'mouthUpperUpRight':0.0,'mouthLowerDownLeft':0.0,'mouthLowerDownRight':0.0,'mouthSmileLeft':0.0,'mouthSmileRight':0.0,'LeftEyeX':0.0,'RightEyeX':0.0,'EyeY':0.0,'LeftEyeLid':1.0,'RightEyeLid':1.0},
 'mouth_open': {'jawOpen':1.0,'mouthClose':0.0,'mouthFunnel':0.35,'mouthPucker':0.35,'mouthStretchLeft':1.0,'mouthStretchRight':1.0,'mouthUpperUpLeft':1.0,'mouthUpperUpRight':1.0,'mouthLowerDownLeft':1.0,'mouthLowerDownRight':1.0,'mouthSmileLeft':0.0,'mouthSmileRight':0.0,'LeftEyeX':0.0,'RightEyeX':0.0,'EyeY':0.0,'LeftEyeLid':1.0,'RightEyeLid':1.0},
 'eyes_right': {'jawOpen':0.0,'mouthClose':0.0,'mouthFunnel':0.0,'mouthPucker':0.0,'mouthStretchLeft':0.0,'mouthStretchRight':0.0,'mouthUpperUpLeft':0.0,'mouthUpperUpRight':0.0,'mouthLowerDownLeft':0.0,'mouthLowerDownRight':0.0,'mouthSmileLeft':0.0,'mouthSmileRight':0.0,'LeftEyeX':1.0,'RightEyeX':1.0,'EyeY':0.0,'LeftEyeLid':1.0,'RightEyeLid':1.0},
 'eyes_up': {'jawOpen':0.0,'mouthClose':0.0,'mouthFunnel':0.0,'mouthPucker':0.0,'mouthStretchLeft':0.0,'mouthStretchRight':0.0,'mouthUpperUpLeft':0.0,'mouthUpperUpRight':0.0,'mouthLowerDownLeft':0.0,'mouthLowerDownRight':0.0,'mouthSmileLeft':0.0,'mouthSmileRight':0.0,'LeftEyeX':0.0,'RightEyeX':0.0,'EyeY':1.0,'LeftEyeLid':1.0,'RightEyeLid':1.0},
}
def pad(b): return b+b'\x00'*((4-len(b)%4)%4)
def send(a,v):
    pkt=pad(a.encode())+pad(b',f')+struct.pack('>f',float(v))
    s.sendto(pkt,(HOST,PORT))
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
vals=STATES[STATE]
t0=time.time()
while time.time()-t0<DUR:
    for k,v in vals.items(): send('/'+k,v)
    time.sleep(0.05)
print('PROOF_SENDER_DONE',STATE,len(vals),round(time.time()-t0,2),flush=True)
