# 熊出没之熊大农场 (Boonie Bears Farm) — 网络协议逆向文档

版本: APK 1.6.3 (com.joym.bearfarm.wali, GameID=260, 内部代号 BigBear/TinyFarm)
开发商: 乐堂动漫 (LT/LeTang, joymeng.com) | 引擎: Unity 5 Mono (基于 FarmVille 2 移动版框架)

## 1. 总体架构

| 服务 | 地址 | 状态(2026-10) | 协议 | 用途 |
|---|---|---|---|---|
| 游戏逻辑主服务 | `http://farmzone.joymeng.com:8080/BearFarm/Bear` | **已死**(DNS失效) | 明文 HTTP GET/表单 | 核心玩法 |
| SDK/API 服务 | `http://api.joyapi.com/` | 部分仍存活 | POST `data=Base64(DES(JSON))` | 账号/存档/集市/好友DES API |
| 账号服务 | `http://netuser.joymeng.com/user/` | 仍存活 | 明文 HTTP GET | 登录 quickReg/login (v1.6.3 死代码) |
| ESB 长连接 | `farmesb1.joymeng.com:60000` | 已死 | TCP 二进制帧 | 聊天/家族/红包 (v1.6.3 死代码, 见§4) |
| 资源 CDN | `http://hijoyres.joymeng.com/260/...` | 已死 | HTTP | 商店XML/AssetBundle/ProtoDB |
| 礼包列表 | `hijoyusers.joymeng.com:8100/bigbear/getPacksList` | 已死 | HTTP | 月卡/开关配置 |

## 2. DES JSON 协议 (api.joyapi.com)

- 算法: **DES/ECB/PKCS5Padding**, 密钥 `abc12345` (libsupport.so 内 "DES" transformation)
- 请求: `POST`, body = `data=` + Base64(DES(JSON)), `Content-Type: text/plain`
- 响应: Base64(DES(JSON)); 信封 `{"status":int, "msg":str, "data":...}`; status=1 成功
- **客户端 native 层检查 `needStop` 字段, 非 0 会强退游戏 — 私服响应勿带**
- 公共参数(native post2 自动附加): `app_id(需GSDKApplication初始化=260), channel_id, guid(需baseParam预置), androidid, mobile, brand, time, versionCode, sdk_ver=3, _reqTime_, singing(设备签名,与APK签名相关,私服无需校验), log_status`
- `singing` 由 getSingInfoReal(libsupport.so) 计算, 重签名 APK 后会改变 — 私服忽略即可

### 关键端点 (全部 POST DES)

**farm/* 存档与好友:**
- `farm/setArchiveNew` `{data}` — 云存档 `{"role":{CharacterInfo},"memory":<农场blob JSON>}`
- `farm/setArchive` `{data}` — 商铺数据 `{"shop":{ShopCells}}`
- `farm/getArchive` `{archive_type}` — 自己存档
- `farm/getTargetArchive` `{targetId, archive_type}` — 他人存档; 响应 `{"status":1,"data":{"memory":<blob>}}`;
  **无存档时原版返回默认农场** — 私服已实现模板兜底(否则客户端弹"没有网络")
- `farm/friendList` → `{"status":1,"data":{"curNum","maxNum","userList":[CharacterInfo]}}`
- `farm/addFriend/delFriend/getFriendInfo/friendRecommend`

**farm/shop 集市 (type 参数区分):**
| type | 语义 | 响应 data 格式 |
|---|---|---|
| 0 | 我的商店 | `ShopCells` 对象 `{cells,face,faceData,faceType,level,name,uId,shopStatus}` |
| 1 | 上架商品 | 上架的 SeafarerOffer; 客户端自带 status=3 |
| 2 | 世界市场 | `[{ShopCells}]` 数组 |
| 3 | 好友市场 | `[{ShopCells}]` 数组(每个好友一个) |
| 4/5/6 | 租位/购买/下架 | 操作回执 |
| 8 | 指定好友商店 | `[SeafarerOffer]` 数组 |

- SeafarerOffer: `{id,itemId,amount,price,costItem,status,seller,buyer,voyage,createdAt,autoBuy,autobuyTime,index,buyed}`
- **status 枚举: 0=空位 1=已售 2=删除/锁定 3=在售(STATUS_SELLING)** — 购买面板只渲染 status=3
- **itemId 必须是 ProtoInventoryItem 真实ID(如 `Wheat_01`,`Carrot_01`,`Flour_01`,带 `_01` 后缀)**;
  客户端渲染时 `TryGetValue(itemId) && TryGetValue(costItem)` 双查表,查不到静默跳过
- costItem 标准值 `"coin"` (客户端上架时自己写)

**dreammarket/ 集市好友/邮件/排行榜:** friendList, friendRecommend, friendAdd, friendDel, friendVisit, friendSearch, friendInvite, friendInviteResult, getMails, rmMail, rankView, updateMarket, updateMarketMoney, workInfo, startWorkFriend, endPark, cars, parkLots, parkCar, buyCar, cellCars, pleaseLeaveCar, upgradeParkLot, unLockParkLot, addCarCountLimit

**user/game/bigbear:** user/loginCombine (响应 `{uid,nickname,regTime,time,_real_reg_,ip}`), user/quickReg, user/updateUser, game/getAllParam (SDK开关), bigbear/getPacksList (月卡/运营开关), bigbear/getCDKey, ranks/getRanks...

**身份说明: v1.6.3 的账号链路全是死代码**(GGameActivity/_Internal 从未运行), 请求天然无 guid。
私服方案: Java BearServer 向 SharedPreferences("game_file") 写 `baseParam={"guid":"<uid>"}`(BasicParams 会合并),
Unity PlayerPrefs 写 `LtAddressKey/LtPlayerKey`; 补丁 APK 已自动化此流程。

## 3. 游戏逻辑协议 (farmzone:8080/BearFarm/Bear)

`GET /BearFarm/Bear?<params>&id=<UserID>`

| 命令 | 响应 |
|---|---|
| `logic=Heart` | 任意(有响应即在线), 20s 一次 |
| `logic=LoginAfter&id=` | `"1,1"` (支付确认开关,礼包开关) |
| `logic=Sign` | `{"time":"<DateTime>","reward":[7天奖励]}` — 奖励由服务器下发,客户端本地发放 |
| `logic=Notice&type=0` | `"版本号,..."`; type=2 返回 Notice.xml 字节 |
| `logic=Friend&type=1/2/3/4&fid=` | 添加/列表/按ID查/删除 |
| `logic=Access&fid=` | **二进制**: zlib(对方农场blob JSON) + 响应头 `memoryLen: <字节数>`; 无存档时 memoryLen=0 → 客户端回落NPC默认农场 |
| `logic=SearchAround&keys=` | JSON 数组 [FriendInfo] |
| `logic=Steal&fid=&key=` | `"ok:数量"` 或 `"err:消息"` |
| `logic=Shop&type=7` | int (是否有已售商品标记) |
| `logic=Rename&name=&ageGroup=` / `logic=Rename&face=` | int |
| `logic=Change` (POST表单: setId,setName,setFace,setFaceType,setFaceData,setFaceName) | uid 文本; **uid 取表单 setId 而非 query id** |
| `logic=LoadHotsellsFile&channel=` | Hotsell.xml 字节 |
| `logic=RewardGet&value=&id=` | `{"desc","reward":"itemId\|数量,..."}` 或 `{"error"}` |
| `logic=InvitationFriend&ids=` | JSON 数组 [FriendInfo] |
| `logic=TreeStatus&id=` | `{"status":1,"tree":{joyId,level,time(剩余ms),output,stealCount,defCount,plus,left,status,guangLevel}}`; 无树→`{"status":0,"message"}` 客户端走本地 |
| `logic=TreePlant&id=&bearLevel=&motion=&guangLevel=&guangMotion=&xdSkin=&gtqSkin=` | `{"status":1,"tree":{...},"rate":N}` |
| `logic=TreeHarvest&id=` | `{"status":1,"tree":{...}}` |
| `logic=TreeSteal&id=&fid=&bearLvel=&motionBear=&xeSkin=` | `{"status":1,"tree":{...},"money":N,"rate":N}` — money>0偷成/money<0被抓罚款 |
| `logic=Regist` (POST表单) | **v1.6.3 死代码,客户端不发** |

## 4. ESB 长连接协议 (farmesb:60000) — 已确认客户端死代码,未实现

帧: `uint32 BE 长度 + 消息体`; protocol 0xFF=重定向(int port+string8 host), 1=消息(34字节头+payload)。
LoginRequest(msgId=2): u64 uid + string16 token("token")。
**结论: v1.6.3 中 `SocketManager.Connect(Action<int>)` 为空方法、`AccountCenter` 登录链路死代码、
`WebRegistId` 无写入点 → ESB 永远不会连接,聊天/家族在此版本不可用,与服务端无关。**
私服仅保留 :60000 TCP 骨架以备其他版本。

## 5. 存档 (blob) 系统

- 本地文件: `CCZ!`(17字节头) + 逐字节取反 + Mangle(2/3处插入 CheckSum1) + 首两字节 Fold — SVBlobIO
- zlib(UTF8 JSON): `{MetaData:{Details:{level,xp,coin,key}}, entities:{"static":[...管理器], "<x>,<y>":[<实体>]}}`
- 云路径: setArchiveNew 的 memory 字段(未压缩 JSON); 好友访问 Access 直接下发 zlib 压缩格式
- ProtoDB: `files/Bundles/ProtoDB.bytes_*.bytes` (同 blob 编码) → doDecode → 原生 protobuf
  `ProtoDatabase{map<string,ProtoData>}`; 物品=ProtoInventoryItem(field 110), ID 带 `_01` 后缀

## 6. 补丁 APK (免 root 分发方案)

- `UnityPlayerActivity.onCreate`: `AuthApplication.attach`(实名/防沉迷SDK,com.wh.authsdk) → 替换为 `BearServer.init`
- **BearServer**(新增Java类): 首启弹私服地址对话框 → 存 `SharedPreferences("bearfarm")/server`;
  同时播种 uid(设备指纹) 到 PlayerPrefs(LtAddressKey/LtPlayerKey) 和 game_file(baseParam); 确定后 killProcess 重启使 C# 静态字段生效
- **HttpClientSupport.isSandboxModel**(所有 DES 请求咽喉点): 先经 `BearServer.url()` 把 joymeng/joyapi 域名重写为自定义地址(保留端口)
- **Assembly-CSharp.dll**: 注入 BearPatch 类(dnlib), 12 处 ldstr URL 改为运行时调用;
  **BearPatch 用纯文件 IO 读 bearfarm.xml(禁用 AndroidJavaClass — 雷电 ARM→x86 翻译层下 C# 静态构造器中的 JNI 调用会触发 `JNI ERROR: accessed stale Local` 系统级崩溃)**
- `SDKHelper.updateUser`: 原版 `SdkAPI.getContext()` NPE(此版本 Activity 未初始化) → 直接返回 `{"status":1}`
- Manifest: `<application android:name="com.joym.sdk.core.GSDKApplication">` 修复 SDK 全套初始化(app_id=260 等)
- 签名: `tools/bearfarm.keystore` (jarsigner v1, targetSdk 23 兼容); 原生 checkSign 仅支付流程使用,重签名安全

## 7. 私服实现要点 (server/)

- farmzone(8080) 明文 HTTP; api(80) DES JSON + 静态资源; packs(8100) 礼包; esb(60000) 骨架
- 身份: guid(DES请求)/id(farmzone GET)/setId(Change表单) 三种来源统一解析
- 好友访问兜底: getTargetArchive 无存档时返回任一模板 blob
- 集市: 按 type 分别返回 ShopCells 对象/数组(§2 表格), 商品必须 status=3 + 真实物品ID
- 摇钱树: trees 表; 2h 成熟; 偷取=产出10%
- SQLite, 线程安全锁; 每请求实时读库(改数据无需重启)
