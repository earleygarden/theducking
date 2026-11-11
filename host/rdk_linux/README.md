# Linux / Tkinter S288 调试入口

- 早期实验工具，主要维护入口见 [Windows README](../win11/README.md)。
- Windows 主线仍复用这里的控制基础，因此本目录保留。
- 关节表、限位界面和看门狗策略与 Windows 主线不同，不能混用操作假设。

## 本机运行

- 前置条件：Python 3、tkinter；真实串口还需 pyserial 与权限。
- 在仓库根目录执行离线预览：

```bash
python3 host/rdk_linux/servo_ui.py --sim
```

- 实物连接示例：

```bash
python3 host/rdk_linux/servo_ui.py --port /dev/ttyACM0 --ids 7,8,14
```

- 默认波特率 `6000000`，先确认适配器、型号与端口支持。
- `KNOWN` 只含 `7/8/14` 的既有语义与保守行程，其他 ID 要现场核对。
- `--limit-max` 扩大行程可设置上界，`--amp-max` 扩大顺序运动幅度上界，参数不是安全认证。
- `motor_random.py` 会发运动指令，不能作为首次只读连通检查。

## Mac 远程显示辅助脚本

- `ui.sh` 是 Mac + XQuartz + SSH X11 辅助脚本，先配置自己的 SSH 别名、密钥与板端环境。
- 从 `host/rdk_linux/` 执行 `./ui.sh 7,8,14`。
- `HOST` 默认别名 `rdk`，`PORT` 默认 `/dev/ttyACM0`，按实际环境覆盖。
- 脚本同步 `host/` 到远端 `~/duck-host/` 后起界面，执行前检查目标位置。
- 仓库不提供个人网络地址、SSH 凭据或已配置好免密登录的假设。

## 控制边界

- 早期入口与底层收发默认超时策略不同于 Windows，退出与异常依赖显式卸力。
- 远程显示有网络延迟，台架旁需能直接切断电机电源。
- 供电按实际 S288 手册核对；旧文档中的其他型号高压示例不作本项目接线依据。
