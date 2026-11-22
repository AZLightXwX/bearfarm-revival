# 更新日志 (Changelog)

本项目所有显著变更记录于此。日期为工作日，非发布日。

## [0.5.1] - 2026-10-21 (下午)

### 新增 — GUI Phase 2 (4 个新页面)
- **公告管理页**: 添加/删除游戏内公告，版本号自动递增（玩家下次启动拉取新公告）;
  notice 数据从静态文件迁移到 SQLite，`farmzone.py` 从 DB 动态生成 XML
- **邮件系统**: 服务端邮件存储 + `dreammarket/getMails`/`rmMail` DES API 对接;
  GUI 发送/查看/删除邮件，奖励格式 `itemId|数量,itemId|数量`
- **签到奖励编辑**: 7 天奖励表格编辑器（3 物品位/天），数据从硬编码迁移到 kv 表
- **摇钱树参数配置**: 成熟时间/产出基数/每级加成 可调，通过 kv 表热生效
- **备份管理**: 一键备份 + 备份列表 + 恢复
- **日志维护**: 清空日志
- **玩家管理增强**: 创建测试玩家（自动生成 uid + 商店模板）、删除玩家（级联清除）

### 修复
- GUI JS 语法错误: `login()` 多余括号导致整个前端瘫痪
- `esc()` HTML 实体转义失效（实体名被吞）
- GUI API 路由: `"/delete" in path` 误匹配 `/api/notice/delete` → 加 `startswith` 前缀
- `farmzone.handle()` 从未解析 `?id=` 参数 (uid=0 Boss bug) — 上线心跳追踪后暴露
- Windows `mktime` 对 strptime 默认年份(1900)的兼容 (改用 datetime)
- **购买页首屏缓存 bug**: `PerformFetchStorey` 恢复旧 blob 缓存 → IL 补丁 `_list=null`

### 变更
- **升级材料不足自动钻石补足** — 确认为原版客户端设计, 保持原行为

## [0.5.0] - 2026-10-21 (上午)

### 新增
- **GUI 运维控制台** `server/gui.py` (零新依赖, 纯标准库 + 内嵌前端):
  - Token 认证 (首次自动生成于 `server/data/gui_token.txt`, 浏览器登录页存 localStorage,
    API 统一校验, 401 拒绝); 默认绑 127.0.0.1, `--host 0.0.0.0` 可开局域网
  - 总览页: 四端口状态 / 在线玩家 / 数据卡 / 请求速率(5min) / 启动横幅检测 / 事件流
  - 玩家页: 搜索 + 表格 + 详情抽屉 (改名 / 加删好友 / 摇钱树快捷操作)
  - 集市页: 全服摊位总览 + 摊位编辑器 (8 格卡片, 物品ID合法性校验, datalist 物品
    选择器, 上架/下架/解锁/清空)
  - 摇钱树页: 状态列表 (生长倒计时/成熟/未种植) + 立即成熟/重置
  - 日志页: 类型/uid/关键字过滤 + 自动刷新暂停 + 请求统计条形图
  - 一键备份
  - `start_gui.bat` 一键启动并打开浏览器

### 修复
- **摇钱树/签到不可见**: v1.6.3 客户端 `WebRegistId` 无任何写入点 (死代码)，
  `TrySendWeb` 永远卡死 → 摇钱树、每日签到等整条功能链不可用。
  - 设备侧: PlayerPrefs 种入 `WebRegistId`
  - 补丁 APK: `BearServer.seedIdentity` 自动播种 (新设备免手动)
  - 服务器: `TreeStatus` 自动建档 (未种植状态)，从种树起全程服务器权威

## [0.4.0] - 2026-10-21

### 修复
- **购买页首次打开只显示一个摊位**: 根因为全球购买页的
  `TradeBuyPanel_New.PerformFetchStorey` 会优先使用启动时从玩家存档 blob
  恢复的 `GlobalSellers` 旧缓存并短路拉取。通过 dnlib 对客户端打第三个 IL
  补丁，将 `_list = ...GlobalSellers` 中和为 `_list = null`，两个购买页
  现在永远从服务器拉取实时数据。
- **farmzone 全端点 uid 绑定错误 (隐藏 Boss bug)**: `handle()` 从未解析
  `?id=` 参数，所有 farmzone 请求一直以 uid=0 运行（摇钱树/改名/注册等
  依赖各处兜底掩盖）。上线心跳在线追踪后立刻暴露，已修复为以 `id` 参数为准。

### 变更
- **升级材料不足自动扣钻石补足** — 确认为原版客户端设计
  (`InventoryHelper.DeductRequirements` 的 buy-through 机制)，保持原行为不改。

### 新增
- **运维控制台** `server/console.py`: players/player/online/tree/shop/
  friends/rename/stats/log/backup 等 14 个命令，实时管理玩家与集市。
- 心跳在线追踪: `users.last_seen` 列 + Heart 自动更新 + 控制台 `online` 命令。
- SQLite 迁移机制与 WAL 并发模式；控制台与服务器可跨进程并发读写。
- 开机自启文档 (`schtasks /sc onstart`)。

## [0.3.0] - 2026-10-20

### 修复
- **集市购买链路全通** (用户验收):
  - `farm/shop` 按 type 正确分流 (0=我的商店/2=世界/3=好友市场/5=购买/8=指定好友)；
  - 商品必须 `status=3` (STATUS_SELLING) 才会被客户端渲染 — 播种数据修正;
  - **物品 ID 必须为 ProtoInventoryItem 真实 ID** (如 `Wheat_01`，带 `_01`
    后缀)。从模拟器提取游戏下载的 `ProtoDB.bytes`，用逆向的 doDecode 算法
    解出原生 protobuf 并交叉验证玩家背包，确认真实 ID 格式。
- **好友访问 10002 报"没有网络"**: `farm/getTargetArchive` 对无存档好友
  返回模板农场兜底 (与原版行为一致)，不再报错。
- **服务器进程意外死亡**: 改用 `pythonw` + WMI 脱离会话启动，免疫终端清理。

### 新增
- **摇钱树服务端逻辑**: 种植(2小时成熟)/收获/偷取(产出10%)/被抓罚款，服务端计时与持久化。
- 好友/集市/世界市场种子数据 (小熊二/光头强 + 5 件真实商品)。
- 请求日志带时间戳；日志双写 (控制台 + 文件)。

## [0.2.0] - 2026-10-19

### 新增 — 免 root 分发方案 (补丁 APK #4)
- **实名认证强制弹窗 → 自定义私服地址弹窗**: 移除 `com.wh.authsdk`
  (UnityPlayerActivity 挂钩)，替换为 `BearServer.init()`: 首启弹窗输入
  私服地址，存入 SharedPreferences，同时播种设备 uid。
- **Java 侧 URL 重写**: `HttpClientSupport.isSandboxModel` 作为所有 DES
  请求咽喉点，统一经 `BearServer.url()` 把 joymeng/joyapi 域名重写为
  自定义地址。
- **C# 侧 URL 动态化**: dnlib 注入 `BearPatch` 类，12 处硬编码 URL
  改为运行时读取配置。
- **无 hosts / 无 root 全链路验证通过**: 移除 magisk hosts 劫持后游戏
  仅凭弹窗配置的地址正常联机。

### 修复
- **JNI 系统级崩溃** (`accessed stale Local 0x1`): ARM→x86 翻译层下，
  C# 静态构造器中的 `AndroidJavaClass` 调用触发 ART abort。BearPatch
  改为纯文件 IO 读取配置 (`shared_prefs/bearfarm.xml`)，规避 cctor 阶段 JNI。
- **"继续"点击卡死**: BearPatch XML 解析 off-by-one，地址变成
  `>192.168.2.20`，`System.Uri` 抛异常导致 UI 挂起。修正标签长度计算。
- **卖出面板转圈**: `farm/shop` 响应格式与 C# 解析不匹配
  (`data:{cells:[]}` vs `data:[...]`)，按调用点分别修正。
- **首次配置后需重启**: 对话框确认后 killProcess 自动重启，确保 C#
  静态字段读到新地址。

## [0.1.0] - 2026-10-17 ~ 10-18

### 首次端到端联机

**逆向** (全部完成):
- APK 多层解包: jadx(Java) / ILSpy(C#) / dnfile+capstone(native)
- 通信协议完全还原: `docs/PROTOCOL.md`
  - DES/ECB/PKCS5 密钥 `abc12345` (libsupport.so 内证)
  - farmzone 明文 HTTP 游戏逻辑 (logic=* 全命令)
  - DES JSON API (farm/*, dreammarket/*, user/*, game/*)
  - ESB TCP 帧协议 (结论: v1.6.3 客户端聊天链路为死代码，跳过)
- 意外发现: 官方 `api.joyapi.com` 12 年后仍存活，用作协议参照物
- 存档 blob 编码 (CCZ! 头 + 取反 + Mangle/Fold + zlib) 完整还原

**服务器** (`server/`, Python):
- 四端口: farmzone:8080 / api:80 / esb:60000 / packs:8100
- SQLite 存储: 玩家/存档/好友/摇钱树
- 身份三源统一: guid(DES) / id(farmzone GET) / setId(Change表单)

**客户端补丁** (APK #1~#3):
- 起名失败: `SDKHelper.updateUser` 原版 `getContext()` 空指针 → 直接返回成功
- Manifest 声明 `GSDKApplication`: 修复 SDK 初始化 (app_id=260/渠道/设备参数)
- `BasicParams` 读 baseParam 改用 Application Context: 所有 DES 请求携带 guid
- 雷电模拟器接入: magisk hosts 劫持 + uid 注入 + captive portal 修复

**验证**: 游戏以 uid=10001 身份在私服运行 — 心跳/签到/存档云备份/
商店状态/改名换装全部走私服。
