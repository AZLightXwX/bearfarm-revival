# 客户端补丁 APK 重建手册

从**原版 APK** (`熊出没之熊大农场_1.6.3.apk`, 包名 com.joym.bearfarm.wali) 重建
`game-patched.apk` 的完整流程。源 APK 由项目维护者自行保管（版权原因不在仓库内）。

## 修改清单

| # | 文件 | 修改 |
|---|---|---|
| 1 | `AndroidManifest.xml` | `<application>` 增加 `android:name="com.joym.sdk.core.GSDKApplication"` (修复 SDK 初始化) |
| 2 | `smali/com/unity3d/player/UnityPlayerActivity.smali` | `AuthApplication.attach` 替换为 `BearServer.init` (移除实名合规 SDK 挂钩) |
| 3 | `smali/com/support/utils/HttpClientSupport.smali` | `isSandboxModel()` 开头插入 `BearServer.url(url)` 重写调用 (DES 请求地址动态化) |
| 4 | `smali_classes2/.../offline/net/BasicParams.smali` | SharePreSaver 调用的 `SDKConfig.getActivity()` 改为 `getApp()` (Activity 无实例时空指针) |
| 5 | `smali_classes2/.../offline/pbase/SDKHelper.smali` | `updateUser()` 整段替换为 `return "{\"status\":1}"` (原实现空指针致起名失败) |
| 6 | `smali/com/bearfarm/BearServer.smali` | 新增 Java 类(源码 `cs-src/../javasrc/com/bearfarm/BearServer.java`) |
| 7 | `assets/bin/Data/Managed/Assembly-CSharp.dll` | 注入 BearPatch 类 + 12 处 URL ldstr 改为运行时读取(见下) |

其中 #1-#5 的成品文件在 `patches/` 目录，重建时直接覆盖。

## 环境依赖

```
JDK 8+          (javac, jarsigner)
Python 3.10+    (capstone 不需要; apktool 为 jar)
.NET SDK 8+     (cs-patch: dnlib 工具, 重定向 URL)
apktool 2.12+   https://github.com/iBotPeaches/Apktool
r8 8.x (jar)    https://maven.aliyun.com/repository/google/com/android/tools/r8/
android.jar     https://maven.aliyun.com/repository/central/com/google/android/android/4.1.1.4/
```

## 流程

```bash
# 1. 反编译原版
java -jar apktool.jar d original.apk -o apk-src

# 2. 覆盖手改补丁 (patches/ 保持原 apk 目录结构, 直接拷贝)
cp -r patches/smali/*      apk-src/smali/
cp -r patches/smali_classes2/* apk-src/smali_classes2/
cp patches/AndroidManifest.xml apk-src/

# 3. 生成 BearServer.smali (源码 → class → dex → smali)
#    若直接使用制品, 跳过本步:
javac --release 8 -bootclasspath android.jar -d javac-out \
      javasrc/com/bearfarm/BearServer.java
java -cp r8.jar com.android.tools.r8.D8 --release --min-api 23 \
     --output dex-out javac-out/com/bearfarm/BearServer*.class
python dex2smali.py    # 将 dex-out/classes.dex 转成 smali 放入 apk-src/smali/com/bearfarm/

# 4. 构建 C# 补丁 DLL
dotnet run --project cs-patch \
    <原版 Assembly-CSharp.dll 所在目录> \
    BearPatch.dll \
    Assembly-CSharp-patched.dll
#  BearPatch.dll 由 cs-src/BearPatch.cs 对游戏自带 mscorlib/UnityEngine 编译:
#    csc /nostdlib /noconfig /target:library \
#      /r:<原版>/mscorlib.dll /r:<原版>/UnityEngine.dll cs-src/BearPatch.cs
cp Assembly-CSharp-patched.dll apk-src/assets/bin/Data/Managed/Assembly-CSharp.dll

# 5. 打包
java -jar apktool.jar b apk-src -o game-patched-unsigned.apk

# 6. 签名 (密钥自管; 与线上版本同一签名才能覆盖安装)
jarsigner -keystore bearfarm.keystore -storepass <pw> \
          -signedjar game-patched.apk game-patched-unsigned.apk bearfarm
```

## 关键实现说明

- **BearServer (Java)**: 首启弹私服地址对话框 → 存 SharedPreferences("bearfarm")/server;
  同时播种 `LtAddressKey`/`LtPlayerKey`/`WebRegistId` 到 Unity PlayerPrefs,
  种入 `game_file` 的 `baseParam={"guid":<uid>"}` (BasicParams 合并进 DES 请求);
  确定后 `killProcess` 重启使 C# 静态字段读到新地址。
- **BearPatch (C#)**: 纯文件 IO 读 `shared_prefs/bearfarm.xml` 中的 server 字段并拼 URL。
  不要用 AndroidJavaClass 做 JNI — 雷电模拟器 ARM→x86 翻译层下, C# 静态构造器阶段
  的 JNI 调用会触发 `JNI ERROR: accessed stale Local` 导致进程 abort。
- **任务链**: 玩家登录流程以 DES /user/loginCombine 应答 `{status:1,uid,regTime,...}` 并落库;
  farmzone 端以 `?id=<uid>` 为准(uid=0 的旧 bug 已修)。