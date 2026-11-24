# Round 5 — VR 嘴控/眼控本地接入调通证据

时间：2026-11-24 01:02 CST

## 目标
测试并调通“VR 动作接入”，重点确认嘴控与眼控在 VRChat 中可见地响应，而不是只在本地 OSC sink 里看到参数。

## 本轮结论
已完成本地 PC 侧闭环：
1. /dev/video4 由 Baballonia 独占，面捕模型启动并持续输出眼/嘴 OSC。
2. VRChat 当前头像 Neri 在运行中提供 /avatar/parameters/FT/v2 下的嘴/眼参数（ACCESS=3 可写）。
3. bab-osc-bridge-r5 持续运行，监听 127.0.0.1:8888，把 Baballonia 的扁平眼嘴参数映射到 VRChat 的嵌套 FT/v2 参数并转发到 UDP 9000。
4. OSCQuery 实际读到实时摄像头驱动值，例如 JawForward=0.0776、JawX=0.4293、LipFunnel=0.0385、LipPucker=0.2214、MouthUpperUp=0.0616、MouthLowerDown=0.1660、MouthPress=0.2210、EyeLeftX=0.3430。
5. 用 bridge_proof_sender.py 从同一入口 127.0.0.1:8888 注入三种可重复状态，截图确认 VRChat 头像视觉变化：
   - 嘴张开：crop RMSE 5.487，face 变化像素 77,690（阈值 10）。
   - 眼睛向右：crop RMSE 6.913，变化像素 54,209。
   - 眼睛向上：crop RMSE 8.378，变化像素 111,962。
6. 12 秒短视频已保存（h264 864x572，5fps，60帧）。

## 动态服务
- vrchat-direct: active
- baballonia-live: active
- bab-osc-bridge-r5: active
- VRChat OSCQuery port: 34915（VRChat 本轮实际端口，不是旧记录里的 36023）
- OSC UDP input: 9000
- 摄像头：Baballonia.Desktop PID 502928 独占 /dev/video4

## 证据文件
- /home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r5_bridge_fix/neutral.png
- /home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r5_bridge_fix/mouth_open.png
- /home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r5_bridge_fix/eyes_right.png
- /home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r5_bridge_fix/eyes_up.png
- /home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r5_bridge_fix/contact.png
- /home/lilyco/文档/deepseek-harness/default-workspace/vrc-pico4-mouth-test/evidence/goal_r5_bridge_fix/live_bridge_demo.mp4
- VRChat OSCQuery live value command output in this report

## 边界说明
- 这是本地 PC/VRChat 调试证明；当前机器上没有 Pico4/串流头显，不能替代甲方“戴 Pico4 进 VRChat”的最终验收。
- 未请求或使用任何账号密码/token。
- 眼睛控制使用的是安全成品模块方向，没有手搓红外眼模块。
