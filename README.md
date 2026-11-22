# 熊出没之熊大农场 私服复活项目

> ⚠️ **免责声明**: 本项目为个人学习与游戏保存目的的独立作品，与乐堂动漫/《熊出没之熊大农场》
> 版权方无任何关联，不包含任何游戏资产或原始程序文件。游戏及其素材的版权归原权利人所有。
> 使用本项目产生的一切后果由使用者自行承担。

让 2013 年发行、已停服的《熊出没之熊大农场》(com.joym.bearfarm.wali v1.6.3) 重新联机。
通过逆向客户端(Unity Mono + Java SDK + native libsupport.so)还原全部网络协议，用 Python 重写服务器，
并产出"自定义私服地址"的免 root 补丁 APK。

## 当前状态 (2026-10-21 已验收)

| 功能 | 状态 |
|---|---|
| 私服核心 (farmzone + DES API + ESB 骨架 + 礼包) | ✅ 完成 |
| 账号/身份 (uid 注入 + guid 绑定 + 存档云备份) | ✅ 完成 |
| 心跳 / 签到 / 改名 / 商店状态 / 公告 | ✅ 完成 |
| 好友系统 (列表/添加/删除/搜索/访问农场) | ✅ 完成 (含无存档好友模板兜底) |
| 集市交易 (卖出/购买/好友市场/世界市场) | ✅ 完成 (用户已验收, 含首屏缓存修复) |
| 摇钱树 (种树/收获/偷树, 服务端计时) | ✅ 完成 |
| 补丁 APK: 去实名弹窗 → 自定义私服地址弹窗 | ✅ 完成 (免 root) |
| 运维控制台 (console.py) | ✅ 完成 |
| ESB 聊天/家族 | ⏭️ 跳过 — v1.6.3 客户端聊天链路是死代码(见 PROTOCOL.md §4) |
| 升级材料不足自动钻石补足 | ℹ️ 原版设计, 保持原行为 |

详细变更见 [CHANGELOG.md](CHANGELOG.md)，协议细节见 [docs/PROTOCOL.md](docs/PROTOCOL.md)，
API 参考 [docs/API.md](docs/API.md)，部署指南 [docs/DEPLOY.md](docs/DEPLOY.md)。

## 快速开始

### 1. 启动私服

```
依赖: Python 3.10+, pycryptodome
cd server
python main.py [farm_port=8080] [api_port=80] [esb_port=60000] [packs_port=8100]
```
或双击 `start_server.bat`。
数据存 `server/data/bearfarm.db` (SQLite)，日志 `server/server.log`。
80 端口被本机 127.0.0.1 占用不影响（服务器绑 0.0.0.0）。

Windows 上持久化运行（脱离会话、不受重启影响需重新执行）:
```
wmic process call create 'C:\PROGRA~1\Python314\pythonw.exe <项目路径>\server\main.py 8080 80 60000 8100'
```
开机自启（可选）:
```
schtasks /create /tn "BearFarmServer" /tr "\"<项目路径>\start_server.bat\"" /sc onstart /ru 用户名 /f
```

### 2. 运维控制台

**GUI 控制台** (推荐) — 浏览器访问，Token 认证:
```
双击 start_gui.bat        # 自动打开 http://127.0.0.1:8090
Token 在 server/data/gui_token.txt (首次自动生成)
局域网管理: python server/gui.py 8090 --host 0.0.0.0
```
功能: 总览(端口/在线/统计/请求速率) · 玩家管理(搜索/详情/改名/好友/创建/删除) ·
集市管理(摊位编辑/物品选择器/上下架/解锁) · 摇钱树(成熟/重置/种植/设定产出) ·
**公告管理(添加/删除,版本自动递增)** · **邮件系统(发送/查看/删除)** ·
**签到奖励编辑(7天物品表格)** · **摇钱树参数配置(成熟时间/产出公式)** ·
**备份管理(一键备份/恢复)** · **日志维护(清空)** ·
实时日志(过滤/统计)。深色主题，中文界面，3 秒自动刷新。

**命令行控制台** (轻量备选):
```
cd server && python console.py
```
常用命令:
```
status                          # 端口/注册人数/在线心跳
players / player <uid>          # 玩家列表 / 详情(角色金币/好友/摇钱树/商店)
online [秒]                     # 最近心跳在线的玩家
tree <uid> mature|reset         # 摇钱树立即成熟 / 重置
shop <uid> add <物品ID> <数量> <价格> [摊位]   # 给玩家商店上架商品(运营)
shop <uid> clear                # 清空在售
friends <uid> add|remove <fid>  # 管理好友关系
rename <uid> <名字>             # 服务器侧改名
stats / log / backup            # 请求统计 / 实时日志 / 备份数据库
```
注意: 物品ID需为 ProtoInventoryItem 真实ID(带 `_01` 后缀, 如 `Wheat_01`/`Egg_01`,
完整列表可从 protostrings.txt 检索)。金币/等级等以客户端本地存档为准(该版本无云还原)，
服务器侧仅集市/摇钱树/好友数据可管理。

### 3. 客户端安装 (免 root)

安装 `game-patched.apk`（已含全部补丁），首次启动弹出"熊大农场 私服设置"对话框，
输入私服 IP 或域名(如 192.168.2.20) → 确定 → 游戏自动重启生效。
无需 hosts、无需 root、无需手动分配账号（设备指纹自动生成 uid）。

### 4. 已验收的可玩内容

好友互访(实时农场镜像)、好友/世界市场买卖、每日签到、摇钱树(2小时成熟,可偷好友)、
云存档(自动上传/还原)、改名换装。

## 补丁 APK 内容 (重打包自原版 1.6.3)

| 补丁点 | 文件 | 说明 |
|---|---|---|
| 移除实名认证强制弹窗 | smali UnityPlayerActivity | authsdk(com.wh) 整个移除 |
| 自定义私服地址弹窗 | smali BearServer(新增) | 首启显示,存 SharedPreferences("bearfarm"/server),并播种 uid |
| DES 请求 URL 重写 | smali HttpClientSupport | isSandboxModel 咽喉点 → BearServer.url() |
| C# 侧 URL 动态化 | Assembly-CSharp.dll + BearPatch(注入) | 12 处硬编码地址改为运行时读取(纯文件IO,避免雷电翻译层 JNI cctor 崩溃) |
| 起名修复 | smali SDKHelper.updateUser | 原版 getContext() 空指针 → 直接返回成功 |
| SDK 初始化 | AndroidManifest.xml | 声明 GSDKApplication,修复 app_id/channel_id/设备参数 |

重打包流程(工具都在 tools/):
```
apktool b apk-src → jarsigner 签名(tools/bearfarm.keystore) → adb install -r
C# 补丁: csc(对游戏自带 mscorlib/UnityEngine 编译 BearPatch.cs) → cs-patch(dnlib 合并+12处ldstr重写)
```

## 架构

```
客户端(APK) ──自定义地址──► 私服(Python)
  :8080 /BearFarm/Bear      明文HTTP   游戏逻辑(Heart/Sign/Friend/Shop/Tree/Access...)
  :80   /farm /user /game   DES-JSON   SDK+存档+集市+好友DES API
         /dreammarket ...              (market 子系统)
  :8100 /bigbear/getPacksList 明文HTTP  礼包开关
  :60000 farmesb             TCP帧     聊天(客户端死代码,仅留骨架)
  DES: ECB/PKCS5Padding, key="abc12345", body=data=<base64>
```

## 目录

- server/            私服 (main.py 入口; farmzone.py 游戏逻辑; httpapi.py DES API; store.py SQLite)
- docs/PROTOCOL.md   完整协议逆向文档
- apk-src/           apktool 反编译工程(已打好全部 smali/XML 补丁)
- tools/             逆向/测试/构建脚本, BearPatch.cs, 签名密钥
- decomp/ jadx-out/  反编译参考代码
- work/              APK 解包产物

## 已知限制

- 聊天/家族(ESB)不可用: 客户端 v1.6.3 相关链路为死代码(详见协议文档)
- 支付不可用: 支付渠道已死, 如需内购需自行扩展私服发放逻辑
- 服务器为单进程线程模型, 适合小圈子(几十人), 更大规模需重构
