# 部署手册 — 熊出没之熊大农场私服

本手册覆盖在 **Windows / Linux / macOS** 上部署私服的完整步骤，以及客户端安装和运维。

---

## 1. 环境要求

| 组件 | 最低版本 | 说明 |
|---|---|---|
| Python | 3.10+ | 服务端运行时 |
| pycryptodome | 任意 | DES 加解密 (`pip install pycryptodome`) |
| 磁盘 | 50 MB | SQLite 数据库 + 日志 |
| 网络 | 开放 80/8080/60000/8100 端口 | 客户端连接 |

**无需**: MySQL / Redis / Docker / Node.js / 任何数据库服务 — 纯 Python + SQLite。

---

## 2. Windows 部署

### 2.1 安装 Python

从 [python.org](https://www.python.org/downloads/) 下载 Python 3.10+ 并安装（勾选 "Add to PATH"）。

验证:
```cmd
python --version
```

### 2.2 获取项目

```cmd
git clone <项目地址> bearfarm-server
cd bearfarm-server
```
或直接复制 `server/` 目录到任意位置。

### 2.3 安装依赖

```cmd
pip install pycryptodome
```

### 2.4 启动服务器

```cmd
cd server
python main.py 8080 80 60000 8100
```

或双击项目根目录的 `start_server.bat`。

**持久化运行**（脱离终端，推荐）:
```cmd
wmic process call create "C:\Path\To\Python\pythonw.exe C:\Path\To\server\main.py 8080 80 60000 8100"
```

**开机自启**:
```cmd
schtasks /create /tn "BearFarmServer" /tr "\"C:\Path\To\start_server.bat\"" /sc onstart /ru <用户名> /f
```

### 2.5 启动 GUI 控制台（可选）

```cmd
cd server
python gui.py
```
或双击 `start_gui.bat`（自动打开浏览器）。

Token 首次自动生成于 `server/data/gui_token.txt`，浏览器登录页粘贴即可。

### 2.6 防火墙

如果玩家从其他设备连接，需要开放入站端口:
```cmd
netsh advfirewall firewall add rule name="BearFarm" dir=in action=allow protocol=TCP localport=80,8080,8100,60000
```

---

## 3. Linux 部署

### 3.1 安装 Python

大多数发行版已内置 Python 3。如需安装:

```bash
# Ubuntu / Debian
sudo apt install python3 python3-pip

# CentOS / RHEL / Rocky
sudo yum install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

### 3.2 获取项目

```bash
git clone <项目地址> bearfarm-server
cd bearfarm-server
```

### 3.3 安装依赖

```bash
pip3 install pycryptodome
# 或虚拟环境:
python3 -m venv venv && source venv/bin/activate && pip install pycryptodome
```

### 3.4 启动服务器

```bash
cd server
python3 main.py 8080 80 60000 8100
```

**注意**: Linux 上 80 端口需要 root 权限:
```bash
sudo python3 main.py 8080 80 60000 8100
```
或用 `setcap` 免 root:
```bash
sudo setcap 'cap_net_bind_service=+ep' $(which python3)
python3 main.py 8080 80 60000 8100
```

### 3.5 systemd 服务（持久化 + 开机自启）

创建 `/etc/systemd/system/bearfarm.service`:
```ini
[Unit]
Description=BearFarm Private Server
After=network.target

[Service]
Type=simple
User=<你的用户名>
WorkingDirectory=/home/<用户>/bearfarm-server/server
ExecStart=/usr/bin/python3 main.py 8080 80 60000 8100
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable bearfarm
sudo systemctl start bearfarm
sudo systemctl status bearfarm    # 检查运行状态
journalctl -u bearfarm -f        # 查看实时日志
```

### 3.6 防火墙

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 80/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 8100/tcp
sudo ufw allow 60000/tcp

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8100/tcp
sudo firewall-cmd --permanent --add-port=60000/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8100 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 60000 -j ACCEPT
```

### 3.7 GUI 控制台

```bash
cd server
python3 gui.py 8090 --host 0.0.0.0
```

`--host 0.0.0.0` 使 GUI 可从局域网访问（如手机浏览器）。
Token 在 `server/data/gui_token.txt`。

---

## 4. macOS 部署

### 4.1 安装 Python

macOS 自带 Python 3（较旧版本可能需安装）:
```bash
brew install python
```

### 4.2 获取项目 + 依赖

```bash
git clone <项目地址> bearfarm-server
cd bearfarm-server
pip3 install pycryptodome
```

### 4.3 启动服务器

```bash
cd server
python3 main.py 8080 80 60000 8100
```

macOS 上 80 端口无需 root（无与 Linux 相同的限制），但如果被占用可换端口。

### 4.4 launchd 持久化（可选）

创建 `~/Library/LaunchAgents/com.bearfarm.server.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.bearfarm.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/<用户>/bearfarm-server/server/main.py</string>
        <string>8080</string>
        <string>80</string>
        <string>60000</string>
        <string>8100</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.bearfarm.server.plist
launchctl start com.bearfarm.server
```

### 4.5 防火墙

macOS 防火墙默认关闭。如果开启了:
系统偏好设置 → 安全性与隐私 → 防火墙 → 防火墙选项 → 允许 Python 接收连接。

---

## 5. 端口规划

| 端口 | 用途 | 必须开放 |
|---|---|---|
| **80** | DES JSON API（存档/集市/好友/邮件） | ✅ 玩家连接 |
| **8080** | farmzone 游戏逻辑（心跳/签到/公告/摇钱树） | ✅ 玩家连接 |
| **8100** | 礼包/月卡开关 | ✅ 玩家连接 |
| **60000** | ESB 聊天（客户端死代码，仅留骨架） | 可选 |
| **8090** | GUI 控制台 | 仅运维访问 |

**端口冲突**: 如果 80 被占用（如 IIS/Apache），可改用其他端口，
但需要同步修改补丁 APK 中 `BearPatch.cs` 里的端口硬编码并重打包。

---

## 6. 客户端安装

### 6.1 补丁 APK（推荐）

安装项目根目录的 `game-patched.apk`。首次启动弹出"熊大农场 私服设置"对话框，
输入服务器 IP 或域名 → 确定 → 游戏自动重启生效。

**无需 root、无需 hosts、无需手动分配账号**（设备指纹自动生成 uid）。

### 6.2 已安装原版 APK 的设备

如果设备已安装原版 APK 且无法卸载重装：
1. 获取设备 root 权限
2. 编辑 `/system/etc/hosts`，添加:
   ```
   <服务器IP> farmzone.joymeng.com
   <服务器IP> api.joyapi.com
   <服务器IP> netuser.joymeng.com
   <服务器IP> hijoyres.joymeng.com
   <服务器IP> hijoyusers.joymeng.com
   <服务器IP> netvoice.joymeng.com
   <服务器IP> farmesb1.joymeng.com
   <服务器IP> pay.joyapi.com
   <服务器IP> games.joyapi.com
   <服务器IP> log.joyapi.com
   <服务器IP> netapi.joyapi.com
   ```
3. 在 Unity PlayerPrefs 种入身份:
   ```
   /data/data/com.joym.bearfarm.wali/shared_prefs/com.joym.bearfarm.wali.xml
   <string name="LtAddressKey">10001</string>
   <string name="LtPlayerKey">10001</string>
   <string name="WebRegistId">10001</string>
   ```
4. Android 9+ 设备需关闭 captive portal:
   ```
   settings put global captive_portal_detection_enabled 0
   ```

### 6.3 服务器地址

补丁 APK 弹窗输入的地址即为玩家连接的私服地址。如果玩家与服务器在同一局域网，
填局域网 IP（如 `192.168.1.100`）；如果是公网服务器，填公网 IP 或域名。

---

## 7. 数据管理

### 数据库位置

```
server/data/bearfarm.db    # SQLite（玩家/存档/好友/摇钱树/公告/邮件/配置）
server/server.log           # 请求日志（追加写入）
```

### 备份

```bash
# GUI: 设置页 → 💾 立即备份
# CLI:
python server/console.py   # 然后 backup
# 手动:
cp server/data/bearfarm.db server/data/bearfarm_$(date +%Y%m%d).bak
```

### 恢复

```bash
# GUI: 设置页 → 备份列表 → 恢复
# 手动:
cp server/data/bearfarm_20261021.bak server/data/bearfarm.db
```

### 迁移到新服务器

1. 停止旧服务器
2. 复制整个 `server/` 目录（含 `data/bearfarm.db`）到新机器
3. 在新机器安装 Python + pycryptodone
4. 启动: `python main.py 8080 80 60000 8100`
5. 玩家在弹窗中输入新服务器地址（或地址不变则无需操作）

---

## 8. 常见问题

### Q: 玩家连接不上

1. 检查服务器是否运行: `curl http://127.0.0.1:8080/BearFarm/Bear?logic=Heart&id=1`
2. 检查防火墙端口是否开放
3. 检查玩家输入的服务器地址是否正确（补丁 APK 弹窗）
4. Android 9+ 设备检查 captive portal 设置

### Q: 玩家数据丢失

金币/等级等以客户端本地存档为准（该版本无云还原），服务器侧存档仅为备份。
如果玩家卸载重装，本地存档丢失，需要从服务器侧手动恢复（将 `archives.memory` 写回客户端本地文件）。

### Q: 80 端口被占用

- Windows: 检查 IIS / Apache / SQL Server Reporting Service
- Linux: `sudo lsof -i :80` 查看占用进程
- 解决: 停掉占用进程，或改用其他端口并修改客户端硬编码

### Q: GUI 打不开

- 检查 8090 端口是否被占用
- Token 在 `server/data/gui_token.txt`，首次启动自动生成
- 如果忘记 Token，删除该文件重启 GUI 即可重新生成

### Q: 集市商品不显示

- 物品ID必须为 ProtoDB 真实ID（带 `_01` 后缀）: `Wheat_01`, `Egg_01`
- 商品必须 `status=3`（在售）才会被客户端渲染
- 用 GUI 集市页的物品选择器确保ID合法
