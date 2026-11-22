# API 参考手册

本文档描述私服暴露给客户端的**全部网络接口**（游戏协议）以及 GUI 控制台的**管理 API**。

## 目录

1. [游戏协议 — farmzone (明文 HTTP)](#1-farmzone-游戏协议)
2. [游戏协议 — DES JSON API](#2-des-json-api)
3. [游戏协议 — 礼包 (明文 HTTP)](#3-礼包接口)
4. [GUI 控制台 — 管理 API](#4-gui-管理-api)

---

## 1. farmzone 游戏协议

**基础地址**: `http://<服务器IP>:8080/BearFarm/Bear`
**方式**: GET (参数在 query string) 或 POST (multipart form)
**编码**: 明文，无加密

所有请求自动附加 `id=<玩家uid>` 参数标识调用者身份。

### 心跳

```
GET ?logic=Heart&id=<uid>
→ 200 "ok"
```

客户端每 20 秒发送一次。服务端更新 `users.last_seen`（用于在线状态检测）。

### 登录后配置

```
GET ?logic=LoginAfter&id=<uid>
→ 200 "1,1"
```

响应 CSV: `IsOpenPayConfirm,IsOpenGift`（逗号分隔，1=开/0=关）。

### 签到

```
GET ?logic=Sign&id=<uid>
→ 200 {"time":"2026-10-21 12:00:00","reward":[...7天...]}
```

`reward` 为 7 个对象的 JSON 数组，每个:
```json
{"awardtype1":"coin","num1":300,"awardtype2":"","num2":0,"awardtype3":"","num3":0}
```
奖励在客户端本地发放，服务器仅负责下发配置。配置存储在 kv 表 `sign_rewards`。

### 公告

```
GET ?logic=Notice&type=0         → "版本号,0"  (版本检查)
GET ?logic=Notice&type=2&channel=xx  → XML 字节流
```

XML 格式:
```xml
<?xml version="1.0" encoding="utf-8"?>
<Notices>
  <Notice id="1" picname="" type="0" desc="公告内容"
          giftId="0" posbtnx="0" posbtny="0" poslabx="0" poslaby="0"/>
</Notices>
```
公告数据存储在 `notices` 表，版本号存储在 kv 表 `notice_version`。

### 日志上报

```
GET ?logic=Log&id=<uid>&vip=<n>&level=<n>&info=<csv>&channelid=<ch>
→ 200 "1"
```

### 好友系统

```
GET ?logic=Friend&type=1&fid=<uid>     添加好友
GET ?logic=Friend&type=2                 好友列表
GET ?logic=Friend&type=3&fid=<uid>     按 uid 查找
GET ?logic=Friend&type=4&fid=<uid>     删除好友
```

**type=2 响应**:
```json
{"curNum":2,"maxNum":50,"userList":[{"id":"10002","name":"小熊二","level":12,...}],"online":[]}
```

**type=3 响应**: 单个 FriendInfo JSON 对象。

### 访问好友农场

```
GET ?logic=Access&fid=<uid>&id=<caller>
→ 200 <binary>  (zlib 压缩的农场 blob JSON)
Headers: memoryLen: <字节数>
```

响应 body 为好友存档 `memory` 字段的 zlib 压缩格式。
无存档时 `memoryLen: 0`，客户端回落默认农场。
另走 DES 通道: `farm/getTargetArchive`。

### 搜索附近玩家

```
GET ?logic=SearchAround&keys=<uid1,uid2,...>&id=<caller>
→ 200 [{"id":"10002","name":"小熊二",...}]
```

### 偷菜

```
GET ?logic=Steal&fid=<uid>&key=<itemId>&id=<caller>
→ 200 "ok:数量"     成功
→ 200 "err:消息"    失败
```

### 商店状态

```
GET ?logic=Shop&type=7&id=<uid>       → int (是否有已售商品)
GET ?logic=Shop&type=9&fId=<uid>     → int (好友是否在售)
```

### 改名 / 换头像

```
GET ?logic=Rename&name=<新名字>&ageGroup=<n>&id=<uid>   → int
GET ?logic=Rename&face=<头像ID>&id=<uid>                 → int
```

### 激活码

```
GET ?logic=RewardGet&value=<激活码>&id=<uid>
→ 200 {"desc":"奖励描述","reward":"coin|100"}
→ 200 {"error":"错误信息"}
```

### 邀请好友

```
GET ?logic=InvitationFriend&ids=<uid1,uid2,...>&id=<caller>
→ 200 [{"id":"10002","name":"小熊二",...}]
```

### 摇钱树

```
GET ?logic=TreeStatus&id=<uid>
→ 200 {"status":1,"tree":{"joyId":10001,"level":5,"time":3600000,
        "output":200,"stealCount":0,"defCount":0,"plus":0,"left":200,
        "status":1,"guangLevel":1}}
→ 200 {"status":0,"message":"no tree"}  (无记录时自动建档)

GET ?logic=TreePlant&id=<uid>&bearLevel=<n>&motion=<n>&guangLevel=<n>...
→ 200 {"status":1,"tree":{...},"rate":8}

GET ?logic=TreeHarvest&id=<uid>
→ 200 {"status":1,"tree":{...}}

GET ?logic=TreeSteal&id=<uid>&fid=<目标uid>&bearLvel=<n>&motionBear=<n>&xeSkin=<n>
→ 200 {"status":1,"tree":{...},"money":20,"rate":8}
```

参数配置(kv 表):
| 键 | 默认值 | 说明 |
|---|---|---|
| `tree_grow_seconds` | 7200 | 成熟时间(秒) |
| `tree_output_base` | 100 | 产出基数 |
| `tree_output_per_level` | 20 | 每级加成 |

产出公式: `base + level * per + guangLevel * (per // 2)`

### 热销商品配置

```
GET ?logic=LoadHotsellsFile&channel=<ch>
→ 200 <XML 字节>
```

### 角色变更 (POST)

```
POST (multipart form)
  logic=Change
  setId,long=<uid>
  setName,String=<名字>
  setFace,int=<头像>
  setFaceType,byte=<类型>
→ 200 "<uid>"
```

### 注册 (POST)

```
POST (multipart form)
  logic=Regist
  setUid,String=<uid>
  setName,String=<名字>
  setUuid,String=<uuid>
→ 200 "<uid>"
```

---

## 2. DES JSON API

**基础地址**: `http://<服务器IP>:80/`
**方式**: POST
**加密**: DES/ECB/PKCS5Padding, 密钥 `abc12345`
**请求体**: `data=` + Base64(DES(JSON 参数))
**Content-Type**: `text/plain`
**响应**: Base64(DES(JSON 响应))

响应信封:
```json
{"status":1,"msg":"","data":...}
```
`status=1` 成功，`0/负数` 失败。

### 用户 / 账号

| 端点 | 参数 | 响应 data |
|---|---|---|
| `user/loginCombine` | `{}` (guid 自动) | `{uid, nickname, regTime, time, _real_reg_, ip}` |
| `user/quickReg` | `{}` | 同上 |
| `user/updateUser` | `{nickname}` | `{uid}` |

### 存档

| 端点 | 参数 | 响应 data |
|---|---|---|
| `farm/setArchiveNew` | `{data: "{\"role\":{...},\"memory\":{...}}"\}` | `{uid}` |
| `farm/setArchive` | `{data: "{\"shop\":{...}}"\}` | `{uid}` |
| `farm/getArchive` | `{archive_type}` | 存档 JSON |
| `farm/getTargetArchive` | `{targetId, archive_type}` | `{memory: <blob>}` |
| `farm/rmArchive` | `{}` | `{}` |

### 集市 (farm/shop)

**所有端点**: `farm/shop`，用 `type` 区分操作:

| type | 语义 | 响应 data |
|---|---|---|
| 0 | 我的商店 | `ShopCells` 对象 |
| 1 | 上架 | `{index}` |
| 2 | 世界市场 | `[ShopCells]` 数组 |
| 3 | 好友市场 | `[ShopCells]` 数组 |
| 4 | 租摊位 | `{index}` |
| 5 | 购买 | `{index}` |
| 6 | 下架 | `{index}` |
| 8 | 指定好友商店 | `[SeafarerOffer]` 数组 |

ShopCells / SeafarerOffer:
```json
{
  "cells": [
    {"id":null,"itemId":"Wheat_01","amount":10,"price":150,
     "costItem":"coin","status":3,"seller":"10002","buyer":null,
     "voyage":0,"createdAt":0,"autoBuy":false,"autobuyTime":0,
     "index":0,"buyed":false}
  ],
  "face":1,"faceData":"0","faceType":0,"level":12,
  "name":"小熊二","uId":"10002","shopStatus":1
}
```

**status 枚举**: 0=空位 1=已售 2=锁定 3=在售(STATUS_SELLING)
**itemId** 必须为 ProtoDB 真实ID(带 `_01` 后缀): `Wheat_01`, `Egg_01` 等。

### 好友 (farm/friend*)

| 端点 | 响应 data |
|---|---|
| `farm/friendList` | `{curNum, maxNum, userList: [CharacterInfo]}` |
| `farm/friendRecommend` | `{curNum, maxNum, userList: [...]}` |
| `farm/addFriend` | `{}` |
| `farm/delFriend` | `{}` |
| `farm/getFriendInfo` | CharacterInfo |

CharacterInfo:
```json
{"ageGroup":0,"channelId":"","coin":0,"constellation":"","face":1,
 "faceName":"0","faceType":0,"id":"10002","key":0,"level":12,
 "name":"小熊二","npc":false,"registerTime":"","sex":0,"vip":0}
```

### 邮件 (dreammarket)

| 端点 | 响应 data |
|---|---|
| `dreammarket/getMails` | `[{MailID, reward, desc}]` |
| `dreammarket/rmMail` | `{}` |

邮件存储在 `mails` 表，reward 格式: `itemId|数量,itemId|数量`

### SDK 配置

| 端点 | 响应 data |
|---|---|
| `game/getAllParam` | `{getLogInit:"", getAdList:[], getMailList:[], getActData:[]}` |
| `bigbear/getPacksList` | 月卡/运营开关 JSON |

---

## 3. 礼包接口

```
GET http://<IP>:8100/bigbear/getPacksList?app_id=260&channel_id=xx
→ {"status":1,"param":{"ShowBtUI":1,"isOpenADS":0,...}}
```

---

## 4. GUI 管理 API

**基础地址**: `http://127.0.0.1:8090`
**认证**: 请求头 `X-Token: <token>`（首次从 `server/data/gui_token.txt` 获取）
**错误**: 未认证 → 401；参数错 → `{"ok":false,"error":"..."}`

### 总览

```
GET /api/status
→ {ports:{farmzone:true,...}, online:[...], counts:{...},
   rate5m:4.0, server:{started,uptime}, gui_uptime:123,
   db_size:123456, recent:[...日志...]}
```

### 玩家

```
GET  /api/players?q=<搜索>          列表
GET  /api/player/<uid>              详情
POST /api/player/<uid>/rename       {name}
POST /api/player/<uid>/friends      {action:"add"|"remove", fid}
POST /api/player/<uid>/delete       删除玩家(级联)
POST /api/player/create             {name, face, level} → {uid}
```

### 集市

```
GET  /api/shops                     全服摊位总览
GET  /api/shop/<uid>                摊位详情(含物品合法性校验)
POST /api/shop/<uid>/offer          {itemId, amount, price, index?}
POST /api/shop/<uid>/clear          清空在售
POST /api/shop/<uid>/unlock         {index}
POST /api/shop/<uid>/offshelf       {index}
GET  /api/items?q=<搜索>            物品目录(ProtoDB提取)
```

### 摇钱树

```
GET  /api/trees                     全部摇钱树
POST /api/tree/<uid>/mature          立即成熟
POST /api/tree/<uid>/reset          重置
POST /api/tree/<uid>/plant          {level, guang} 服务端种树
POST /api/tree/<uid>/setoutput      {output} 设定产出
```

### 公告

```
GET  /api/notices                   公告列表
POST /api/notice/add               {desc, picname?, type?, giftId?, ...}
POST /api/notice/delete             {id}
POST /api/notice/version            递增版本号(触发客户端拉取)
```

### 邮件

```
POST /api/mail/send                 {uid, reward, desc}
GET  /api/mail/list?uid=<n>        邮件列表
POST /api/mail/delete              {id}
```

### 签到奖励

```
GET  /api/signrewards               7天奖励数组
POST /api/signrewards               {rewards:[...]}
```

### 配置

```
GET  /api/config                    摇钱树参数
POST /api/config                    {tree_grow_seconds, tree_output_base, ...}
```

### 日志 / 备份

```
GET  /api/log?n=200&type=FZ&uid=&q=   日志(过滤)
GET  /api/stats                       请求统计
POST /api/log/clear                   清空日志
POST /api/backup                      备份 → {file}
GET  /api/backups                     备份列表
POST /api/backup/restore              {file} 恢复
```
