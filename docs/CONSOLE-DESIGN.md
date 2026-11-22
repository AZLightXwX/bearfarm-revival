# GUI 运维控制台 — 设计文档 (v1 待评审)

## 1. 架构

```
┌─────────────────────────────────────────────┐
│  浏览器 http://127.0.0.1:8090                │
│  单页应用 (内嵌 HTML/CSS/JS, 无构建步骤)       │
└──────────────┬──────────────────────────────┘
               │ fetch + 3s 轮询
┌──────────────▼──────────────────────────────┐
│  server/gui.py  (独立进程, 纯标准库)           │
│  ThreadingHTTPServer :8090  仅绑定 127.0.0.1  │
│  ├─ 静态: 内嵌单页 (无 CDN/无外部资源)          │
│  └─ /api/*: REST JSON                        │
├─────────────────────────────────────────────┤
│  数据层 (与 game server 同源, 只读为主)        │
│  ├─ SQLite (WAL, 跨进程并发安全)               │
│  ├─ server.log (追加读, 请求统计/实时日志)      │
│  └─ protostrings.txt (合法物品ID目录)          │
└─────────────────────────────────────────────┘
```

**关键决策**
- **零新依赖**: 后端纯 Python 标准库 (http.server + sqlite3 + json)，前端原生 JS。
  与主服务器解耦——GUI 崩了不影响游戏。
- **不改主服务器代码**: 通过 SQLite 共享状态 (已有 WAL 模式)。在线状态用 `users.last_seen`。
- **Token 认证 (始终开启)**: GUI 首次启动生成随机 Token 存
  `server/data/gui_token.txt` 并打印到终端；浏览器登录页输入一次，存
  localStorage；所有 `/api/*` 请求校验 Token 头，失败返回 401。
- **默认绑 127.0.0.1**: 管理端口默认不对局域网开放；`--host 0.0.0.0` 可开放
  (手机/其他电脑管理)，此时 Token 是唯一防线。
- **实时性**: 3 秒轮询 (足够运维用，避免 SSE/WebSocket 复杂度)。

## 2. 页面与功能

### ① 总览 Dashboard (默认页)
- 顶部状态卡: 四个端口 通/断 (TCP 探测) · 运行时长 · 数据库体积
- 在线玩家卡: 当前心跳在线列表 (绿色圆点 + 名字 + 等级)
- 数据卡: 注册玩家 / 好友对数 / 生长中摇钱树 / 在售商品总数
- 请求速率: 最近 5 分钟 FZ+API 请求数 (来自日志解析)
- 最近事件: 最新 15 条请求日志流

### ② 玩家管理
- 表格: 头像ID · 名字 · 等级 · VIP · 好友数 · 金币/钻石(档案) · 最近活跃(在线高亮)
- 搜索框 (uid/名字模糊)
- 点击行 → **右侧详情面板**:
  - 档案: coin/key/level/face + 存档体积 + 上传时间
  - 好友列表 (可移除)
  - 商店摘要 · 摇钱树状态
- 操作 (服务端权威数据):
  - ✏️ 改名 (input + 保存)
  - ➕➖ 加/删好友 (uid 输入)
- ⚠️ 金币/钻石为客户端权威 (该版本无云还原)，只读展示，不可编辑 (防误导)

### ③ 集市管理
- 全服摊位总览: 每个玩家一行 (名字 · 在售 N 件 · 摊位缩略)
- 摊位编辑器 (点玩家进入):
  - 8 个摊位卡片: 物品图标ID · 数量 · 价格 · 状态徽章 (在售/已售/空/锁定)
  - 合法性检查: 物品ID是否在 ProtoDB 中 (红标无效物品)
  - 编辑/清空/解锁摊位
- **物品选择器**: 下拉 + 搜索 (来自 protostrings.txt, 显示是否合法)
- 批量: 一键给玩家上架 (物品/数量/价格/摊位号)

### ④ 摇钱树
- 表格: 玩家 · 状态 (生长中倒计时/已成熟/未种植) · 产出 · 剩余 · 被偷次数
- 操作: ⚡立即成熟 · 🔄重置

### ⑤ 实时日志
- 日志流 (自动滚动, 悬停暂停)
- 过滤: FZ/API 类型 · uid · 关键字
- 请求统计: 按 endpoint 的 Top-20 条形图 (纯 CSS bar, 无图表库)
- 清屏/暂停/导出按钮

### ⑥ 设置与维护
- 数据库: 体积 · 一键备份 (带时间戳) · 备份列表
- 公告编辑: notice.xml 在线编辑 (游戏内公告)
- 签到奖励编辑: SIGN_REWARDS 表格化编辑 (服务器当前硬编码 → 迁移为 JSON 文件)
- ⚠️ 高危区 (需二次确认): 重启 game server (杀端口进程 + WMI 重启)

## 3. REST API

| Method | Path | 说明 |
|---|---|---|
| GET | /api/status | 端口/在线/统计卡数据 (Dashboard) |
| GET | /api/players?q= | 玩家列表 |
| GET | /api/player/{uid} | 详情 (档案/好友/商店/树) |
| POST | /api/player/{uid}/rename | {name} |
| POST | /api/player/{uid}/friends | {action:add\|remove, fid} |
| GET | /api/shops | 全服摊位总览 |
| GET | /api/shop/{uid} | 摊位详情 |
| POST | /api/shop/{uid}/offer | {itemId, amount, price, index?} |
| POST | /api/shop/{uid}/clear | |
| POST | /api/shop/{uid}/unlock | {index} |
| GET | /api/items?q= | 物品目录 (合法ID) |
| GET | /api/trees | 摇钱树列表 |
| POST | /api/tree/{uid}/mature \| reset | |
| GET | /api/log?n=&type=&uid=&q= | 日志 (默认最新200条) |
| GET | /api/stats | 请求统计 |
| POST | /api/backup | 备份 |
| GET | /api/notice / POST | 公告读写 |
| GET | /api/signrewards / POST | 签到奖励读写 |

写操作全部 POST + JSON body，返回 {ok:true} 或 {ok:false,error}。

## 4. UI 风格

- 深色主题 (游戏运维风格), 中文界面
- 左侧固定导航栏 (6 项) + 顶部状态条
- 纯 CSS (无框架), 单文件内嵌, ~500 行
- 危险操作红色 + 确认弹窗

## 5. 已知约束 (设计即规避)

1. **金币/钻石客户端权威** → GUI 只读展示 (不做"发金币"这种假功能)
2. **日志解析统计** 是近似值 (取最近 N 行采样) — 标注清楚
3. **重启 game server** 有 2-5 秒服务中断 → 高危区 + 二次确认
4. GUI 与主服务器 SQLite 并发写 → WAL 已支持, 写操作加 timeout=10s

## 6. 分期

- **Phase 1 (先做)**: 总览 / 玩家 / 集市 / 日志 — 核心运维四页
- **Phase 2**: 摇钱树页 / 设置与维护 (备份/公告/签到奖励/重启)
- 物品目录选择器 Phase 1 简化版 (下拉+校验), Phase 2 加分类

## 7. 启动方式

```
python server/gui.py            # 默认 127.0.0.1:8090
python server/gui.py 8091       # 自定义端口
start_gui.bat                  # 双击启动 (自动打开浏览器)
```
