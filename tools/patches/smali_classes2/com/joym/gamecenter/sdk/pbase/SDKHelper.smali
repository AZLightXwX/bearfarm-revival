.class public Lcom/joym/gamecenter/sdk/pbase/SDKHelper;
.super Ljava/lang/Object;
.source "SDKHelper.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 36
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static GetUserData(Landroid/content/Context;)Ljava/lang/String;
    .locals 7
    .param p0, "context"    # Landroid/content/Context;

    .line 52
    new-instance v0, Lorg/json/JSONObject;

    invoke-direct {v0}, Lorg/json/JSONObject;-><init>()V

    .line 54
    .local v0, "json":Lorg/json/JSONObject;
    :try_start_0
    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v1

    const/4 v2, 0x0

    invoke-virtual {p0, v1, v2}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v1

    .line 55
    .local v1, "sp":Landroid/content/SharedPreferences;
    invoke-interface {v1}, Landroid/content/SharedPreferences;->getAll()Ljava/util/Map;

    move-result-object v2

    .line 56
    .local v2, "maps":Ljava/util/Map;, "Ljava/util/Map<Ljava/lang/String;*>;"
    if-eqz v2, :cond_3

    invoke-interface {v2}, Ljava/util/Map;->size()I

    move-result v3

    if-nez v3, :cond_0

    goto :goto_2

    .line 57
    :cond_0
    invoke-interface {v2}, Ljava/util/Map;->keySet()Ljava/util/Set;

    move-result-object v3

    invoke-interface {v3}, Ljava/util/Set;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :goto_0
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v4

    if-eqz v4, :cond_2

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v4

    check-cast v4, Ljava/lang/String;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_1

    .line 59
    .local v4, "s":Ljava/lang/String;
    :try_start_1
    invoke-interface {v2, v4}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    .line 60
    .local v5, "o":Ljava/lang/Object;
    if-nez v5, :cond_1

    goto :goto_0

    .line 61
    :cond_1
    invoke-virtual {v5}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v6

    .line 62
    .local v6, "value":Ljava/lang/String;
    invoke-virtual {v0, v4, v6}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0

    .line 65
    nop

    .end local v5    # "o":Ljava/lang/Object;
    .end local v6    # "value":Ljava/lang/String;
    goto :goto_1

    .line 63
    :catch_0
    move-exception v5

    .line 64
    .local v5, "e":Ljava/lang/Exception;
    :try_start_2
    invoke-virtual {v5}, Ljava/lang/Exception;->printStackTrace()V

    .line 66
    .end local v4    # "s":Ljava/lang/String;
    .end local v5    # "e":Ljava/lang/Exception;
    :goto_1
    goto :goto_0

    .line 69
    .end local v1    # "sp":Landroid/content/SharedPreferences;
    .end local v2    # "maps":Ljava/util/Map;, "Ljava/util/Map<Ljava/lang/String;*>;"
    :cond_2
    goto :goto_3

    .line 56
    .restart local v1    # "sp":Landroid/content/SharedPreferences;
    .restart local v2    # "maps":Ljava/util/Map;, "Ljava/util/Map<Ljava/lang/String;*>;"
    :cond_3
    :goto_2
    const-string v3, ""
    :try_end_2
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_1

    return-object v3

    .line 67
    .end local v1    # "sp":Landroid/content/SharedPreferences;
    .end local v2    # "maps":Ljava/util/Map;, "Ljava/util/Map<Ljava/lang/String;*>;"
    :catch_1
    move-exception v1

    .line 68
    .local v1, "e":Ljava/lang/Exception;
    invoke-virtual {v1}, Ljava/lang/Exception;->printStackTrace()V

    .line 70
    .end local v1    # "e":Ljava/lang/Exception;
    :goto_3
    invoke-virtual {v0}, Lorg/json/JSONObject;->toString()Ljava/lang/String;

    move-result-object v1

    return-object v1
.end method

.method static synthetic access$000(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    .locals 1
    .param p0, "x0"    # Ljava/lang/String;
    .param p1, "x1"    # Ljava/lang/String;

    .line 36
    invoke-static {p0, p1}, Lcom/joym/gamecenter/sdk/pbase/SDKHelper;->updateUser(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method static synthetic access$100(Ljava/lang/String;Ljava/lang/String;)V
    .locals 0
    .param p0, "x0"    # Ljava/lang/String;
    .param p1, "x1"    # Ljava/lang/String;

    .line 36
    invoke-static {p0, p1}, Lcom/joym/gamecenter/sdk/pbase/SDKHelper;->synLocalNickname(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method public static activityPage(Ljava/lang/String;Ljava/lang/String;)V
    .locals 4
    .param p0, "list"    # Ljava/lang/String;
    .param p1, "id"    # Ljava/lang/String;

    .line 176
    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/utils/UrlUtils;->getInstance()Lcom/joym/gamecenter/sdk/offline/utils/UrlUtils;

    move-result-object v0

    const-string v1, "http://games.joyapi.com/activity/"

    invoke-virtual {v0, v1}, Lcom/joym/gamecenter/sdk/offline/utils/UrlUtils;->getUrlConfig(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 177
    .local v0, "url":Ljava/lang/String;
    new-instance v1, Ljava/util/HashMap;

    invoke-direct {v1}, Ljava/util/HashMap;-><init>()V

    .line 178
    .local v1, "param":Ljava/util/HashMap;, "Ljava/util/HashMap<Ljava/lang/String;Ljava/lang/String;>;"
    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Lcom/joym/gamecenter/sdk/offline/utils/EncryptUtil;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    .line 179
    const-string v2, "data"

    invoke-virtual {v1, v2, p0}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 180
    const-string v2, "id"

    invoke-virtual {v1, v2, p1}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 181
    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/api/SdkAPI;->getAppId()I

    move-result v2

    const/16 v3, 0x133

    if-eq v3, v2, :cond_1

    const v2, 0xc35b

    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/api/SdkAPI;->getAppId()I

    move-result v3

    if-ne v2, v3, :cond_0

    goto :goto_0

    .line 184
    :cond_0
    const/4 v2, 0x0

    new-array v2, v2, [Landroid/os/Bundle;

    invoke-static {v0, v1, v2}, Lcom/joym/gamecenter/sdk/offline/inner/SingleAPI;->showWebViewByDialog(Ljava/lang/String;Ljava/util/HashMap;[Landroid/os/Bundle;)V

    goto :goto_1

    .line 182
    :cond_1
    :goto_0
    const-string v2, "JumpActivity"

    invoke-static {v2, v0}, Lcom/joym/gamecenter/sdk/offline/inner/SingleAPI;->sendMessageToUnity(Ljava/lang/String;Ljava/lang/String;)V

    .line 186
    :goto_1
    return-void
.end method

.method public static checkInvalidContentT(Ljava/lang/String;)Ljava/lang/String;
    .locals 6
    .param p0, "context"    # Ljava/lang/String;

    .line 189
    const-string v0, ""

    .line 192
    .local v0, "invalidKeys":Ljava/lang/String;
    :try_start_0
    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/api/SdkAPI;->getContext()Landroid/content/Context;

    move-result-object v1

    invoke-virtual {v1}, Landroid/content/Context;->getAssets()Landroid/content/res/AssetManager;

    move-result-object v1

    const-string v2, "invalid_keys.txt"

    invoke-virtual {v1, v2}, Landroid/content/res/AssetManager;->open(Ljava/lang/String;)Ljava/io/InputStream;

    move-result-object v1

    invoke-static {v1}, Lcom/joym/gamecenter/sdk/offline/net/FJFile;->read(Ljava/io/InputStream;)Ljava/lang/String;

    move-result-object v1

    move-object v0, v1

    .line 193
    const/4 v1, 0x5

    invoke-virtual {v0, v1}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v1

    const v2, -0x10001

    invoke-static {v1, v2}, Lcom/joym/gamecenter/sdk/offline/net/Encrypt;->Encryption(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v1
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    move-object v0, v1

    .line 196
    goto :goto_0

    .line 194
    :catch_0
    move-exception v1

    .line 195
    .local v1, "e":Ljava/lang/Exception;
    invoke-virtual {v1}, Ljava/lang/Exception;->printStackTrace()V

    .line 197
    .end local v1    # "e":Ljava/lang/Exception;
    :goto_0
    invoke-static {v0}, Landroid/text/TextUtils;->isEmpty(Ljava/lang/CharSequence;)Z

    move-result v1

    const-string v2, "Payment"

    if-eqz v1, :cond_0

    .line 198
    const-string v1, "invalidKeys \u4e3a\u7a7a"

    invoke-static {v2, v1}, Lcom/joym/gamecenter/sdk/offline/utils/Log;->i(Ljava/lang/String;Ljava/lang/String;)V

    .line 200
    :cond_0
    invoke-static {p0}, Lcom/joym/gamecenter/sdk/offline/utils/Tools;->getHanziPinYin(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 201
    .local v1, "s":Ljava/lang/String;
    invoke-virtual {v0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v3

    const-string v4, "type"

    const-string v5, "status"

    if-eqz v3, :cond_1

    .line 202
    const-string v3, "\u8fdb\u5165\u654f\u611f\u8bcd"

    invoke-static {v2, v3}, Lcom/joym/gamecenter/sdk/offline/utils/Log;->i(Ljava/lang/String;Ljava/lang/String;)V

    .line 203
    new-instance v2, Lorg/json/JSONObject;

    invoke-direct {v2}, Lorg/json/JSONObject;-><init>()V

    .line 205
    .local v2, "json":Lorg/json/JSONObject;
    const/4 v3, 0x0

    :try_start_1
    invoke-virtual {v2, v5, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    .line 206
    const-string v3, "\u672c\u5730\u68c0\u6d4b\u7ed3\u679c"

    invoke-virtual {v2, v4, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_1

    .line 209
    goto :goto_1

    .line 207
    :catch_1
    move-exception v3

    .line 208
    .local v3, "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 210
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_1
    invoke-virtual {v2}, Lorg/json/JSONObject;->toString()Ljava/lang/String;

    move-result-object v3

    return-object v3

    .line 212
    .end local v2    # "json":Lorg/json/JSONObject;
    :cond_1
    const-string v3, "\u672a\u8fdb\u5165\u654f\u611f\u8bcd"

    invoke-static {v2, v3}, Lcom/joym/gamecenter/sdk/offline/utils/Log;->i(Ljava/lang/String;Ljava/lang/String;)V

    .line 213
    new-instance v2, Lorg/json/JSONObject;

    invoke-direct {v2}, Lorg/json/JSONObject;-><init>()V

    .line 215
    .restart local v2    # "json":Lorg/json/JSONObject;
    const/4 v3, 0x1

    :try_start_2
    invoke-virtual {v2, v5, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    .line 216
    const-string v3, "\u975e\u654f\u611f\u8bcd"

    invoke-virtual {v2, v4, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_2
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_2

    .line 219
    goto :goto_2

    .line 217
    :catch_2
    move-exception v3

    .line 218
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 220
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_2
    invoke-virtual {v2}, Lorg/json/JSONObject;->toString()Ljava/lang/String;

    move-result-object v3

    return-object v3
.end method

.method public static doRestart(I)V
    .locals 2
    .param p0, "timeDelay"    # I

    .line 143
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "doRestart  timeDelay="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V

    .line 144
    const-string v0, "doRestart start="

    invoke-static {v0}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V

    .line 145
    invoke-static {}, Lcom/joym/sdk/base/SDKConfig;->getActivity()Landroid/app/Activity;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/Activity;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v0

    invoke-static {}, Lcom/joym/sdk/base/utils/GameUtil;->getPackageName()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/content/pm/PackageManager;->getLaunchIntentForPackage(Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v0

    .line 146
    .local v0, "intent":Landroid/content/Intent;
    const/high16 v1, 0x4000000

    invoke-virtual {v0, v1}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    .line 147
    invoke-static {}, Lcom/joym/sdk/base/SDKConfig;->getActivity()Landroid/app/Activity;

    move-result-object v1

    invoke-virtual {v1, v0}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V

    .line 148
    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v1

    invoke-static {v1}, Landroid/os/Process;->killProcess(I)V

    .line 149
    const-string v1, "doRestart end="

    invoke-static {v1}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V

    .line 151
    return-void
.end method

.method public static getClipboardStr()Ljava/lang/String;
    .locals 7

    .line 75
    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/api/SdkAPI;->getContext()Landroid/content/Context;

    move-result-object v0

    .line 76
    .local v0, "con":Landroid/content/Context;
    const-string v1, "clipboard"

    invoke-virtual {v0, v1}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Landroid/content/ClipboardManager;

    .line 77
    .local v1, "clipboard":Landroid/content/ClipboardManager;
    const-string v2, ""

    if-nez v1, :cond_0

    return-object v2

    .line 78
    :cond_0
    const/4 v3, 0x0

    .line 80
    .local v3, "item":Landroid/content/ClipData$Item;
    invoke-virtual {v1}, Landroid/content/ClipboardManager;->hasPrimaryClip()Z

    move-result v4

    if-nez v4, :cond_1

    return-object v2

    .line 82
    :cond_1
    invoke-virtual {v1}, Landroid/content/ClipboardManager;->getPrimaryClipDescription()Landroid/content/ClipDescription;

    move-result-object v4

    .line 83
    .local v4, "cd":Landroid/content/ClipDescription;
    if-nez v4, :cond_2

    return-object v2

    .line 84
    :cond_2
    const-string v5, "text/plain"

    invoke-virtual {v4, v5}, Landroid/content/ClipDescription;->hasMimeType(Ljava/lang/String;)Z

    move-result v5

    if-nez v5, :cond_3

    return-object v2

    .line 87
    :cond_3
    invoke-virtual {v1}, Landroid/content/ClipboardManager;->getPrimaryClip()Landroid/content/ClipData;

    move-result-object v5

    .line 88
    .local v5, "cdText":Landroid/content/ClipData;
    if-nez v5, :cond_4

    return-object v2

    .line 90
    :cond_4
    const/4 v6, 0x0

    invoke-virtual {v5, v6}, Landroid/content/ClipData;->getItemAt(I)Landroid/content/ClipData$Item;

    move-result-object v3

    .line 92
    invoke-virtual {v3}, Landroid/content/ClipData$Item;->getText()Ljava/lang/CharSequence;

    move-result-object v6

    if-nez v6, :cond_5

    return-object v2

    .line 94
    :cond_5
    invoke-virtual {v3}, Landroid/content/ClipData$Item;->getText()Ljava/lang/CharSequence;

    move-result-object v2

    invoke-interface {v2}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;

    move-result-object v2

    return-object v2
.end method

.method public static getGameArchivePath()Ljava/lang/String;
    .locals 3

    .line 42
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "/data/data/"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {}, Lcom/joym/sdk/base/utils/GameUtil;->getPackageName()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, "/shared_prefs/"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {}, Lcom/joym/sdk/base/utils/GameUtil;->getPackageName()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, ".v2.playerprefs.xml"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 43
    .local v0, "path":Ljava/lang/String;
    new-instance v1, Ljava/io/File;

    invoke-direct {v1, v0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    .line 44
    .local v1, "f":Ljava/io/File;
    invoke-virtual {v1}, Ljava/io/File;->exists()Z

    move-result v2

    if-eqz v2, :cond_0

    return-object v0

    .line 45
    :cond_0
    const-string v2, ""

    return-object v2
.end method

.method public static goToMarket(Ljava/lang/String;)V
    .locals 1
    .param p0, "marketPackagename"    # Ljava/lang/String;

    .line 119
    :try_start_0
    invoke-static {p0}, Landroid/text/TextUtils;->isEmpty(Ljava/lang/CharSequence;)Z

    move-result v0

    if-eqz v0, :cond_0

    return-void

    .line 121
    :cond_0
    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/api/SdkAPI;->getContext()Landroid/content/Context;

    move-result-object v0

    invoke-static {v0, p0}, Lcom/joym/gamecenter/sdk/offline/utils/SysCaller;->isInstall(Landroid/content/Context;Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_1

    .line 122
    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/api/SdkAPI;->getContext()Landroid/content/Context;

    move-result-object v0

    invoke-static {p0, v0}, Lcom/joym/gamecenter/sdk/offline/utils/SysCaller;->openApp(Ljava/lang/String;Landroid/content/Context;)V

    goto :goto_0

    .line 124
    :cond_1
    const-string v0, "goToMarket  parm is null"

    invoke-static {v0}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 128
    :goto_0
    goto :goto_1

    .line 126
    :catch_0
    move-exception v0

    .line 127
    .local v0, "e":Ljava/lang/Exception;
    invoke-virtual {v0}, Ljava/lang/Exception;->printStackTrace()V

    .line 129
    .end local v0    # "e":Ljava/lang/Exception;
    :goto_1
    return-void
.end method

.method public static setClipboardStr(Ljava/lang/String;)Ljava/lang/String;
    .locals 3
    .param p0, "content"    # Ljava/lang/String;

    .line 101
    const-string v0, ""

    :try_start_0
    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/api/SdkAPI;->getActivity()Landroid/app/Activity;

    move-result-object v1

    const-string v2, "clipboard"

    invoke-virtual {v1, v2}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Landroid/content/ClipboardManager;

    .line 102
    .local v1, "myClipboard":Landroid/content/ClipboardManager;
    if-nez v1, :cond_0

    return-object v0

    .line 104
    :cond_0
    const-string v2, "text"

    invoke-static {v2, p0}, Landroid/content/ClipData;->newPlainText(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Landroid/content/ClipData;

    move-result-object v2

    .line 105
    .local v2, "myClip":Landroid/content/ClipData;
    invoke-virtual {v1, v2}, Landroid/content/ClipboardManager;->setPrimaryClip(Landroid/content/ClipData;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 108
    .end local v1    # "myClipboard":Landroid/content/ClipboardManager;
    .end local v2    # "myClip":Landroid/content/ClipData;
    goto :goto_0

    .line 106
    :catch_0
    move-exception v1

    .line 107
    .local v1, "ex":Ljava/lang/Exception;
    invoke-virtual {v1}, Ljava/lang/Exception;->printStackTrace()V

    .line 109
    .end local v1    # "ex":Ljava/lang/Exception;
    :goto_0
    return-object v0
.end method

.method public static showDialog(Ljava/lang/String;)V
    .locals 2
    .param p0, "text"    # Ljava/lang/String;

    .line 154
    new-instance v0, Lcom/joym/gamecenter/sdk/offline/ui/dialog/ShowInfoDialog;

    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/api/SdkAPI;->getContext()Landroid/content/Context;

    move-result-object v1

    invoke-direct {v0, v1, p0}, Lcom/joym/gamecenter/sdk/offline/ui/dialog/ShowInfoDialog;-><init>(Landroid/content/Context;Ljava/lang/String;)V

    .line 155
    .local v0, "dialog":Lcom/joym/gamecenter/sdk/offline/ui/dialog/ShowInfoDialog;
    invoke-virtual {v0}, Lcom/joym/gamecenter/sdk/offline/ui/dialog/ShowInfoDialog;->show()V

    .line 156
    return-void
.end method

.method public static showWebPage(Ljava/lang/String;)V
    .locals 4
    .param p0, "id"    # Ljava/lang/String;

    .line 163
    invoke-static {}, Lcom/joym/gamecenter/sdk/offline/utils/UrlUtils;->getInstance()Lcom/joym/gamecenter/sdk/offline/utils/UrlUtils;

    move-result-object v0

    const-string v1, "http://games.joyapi.com/activity/"

    invoke-virtual {v0, v1}, Lcom/joym/gamecenter/sdk/offline/utils/UrlUtils;->getUrlConfig(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 164
    .local v0, "url":Ljava/lang/String;
    sget-object v1, Lcom/joym/gamecenter/sdk/offline/Global;->activityData:Lcom/joym/gamecenter/sdk/offline/models/ActivityData;

    sget-object v2, Lcom/joym/gamecenter/sdk/offline/Global;->activityData:Lcom/joym/gamecenter/sdk/offline/models/ActivityData;

    invoke-virtual {v1, v2}, Lcom/joym/gamecenter/sdk/offline/models/ActivityData;->toJson(Lcom/joym/gamecenter/sdk/offline/models/ActivityData;)Ljava/lang/String;

    move-result-object v1

    sput-object v1, Lcom/joym/gamecenter/sdk/offline/Global;->activityList:Ljava/lang/String;

    .line 165
    new-instance v1, Ljava/util/HashMap;

    invoke-direct {v1}, Ljava/util/HashMap;-><init>()V

    .line 166
    .local v1, "param":Ljava/util/HashMap;, "Ljava/util/HashMap<Ljava/lang/String;Ljava/lang/String;>;"
    sget-object v2, Lcom/joym/gamecenter/sdk/offline/Global;->activityList:Ljava/lang/String;

    invoke-static {v2}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Lcom/joym/gamecenter/sdk/offline/utils/EncryptUtil;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 167
    .local v2, "list":Ljava/lang/String;
    const-string v3, "data"

    invoke-virtual {v1, v3, v2}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 168
    const-string v3, "id"

    invoke-virtual {v1, v3, p0}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 169
    const/4 v3, 0x0

    new-array v3, v3, [Landroid/os/Bundle;

    invoke-static {v0, v1, v3}, Lcom/joym/gamecenter/sdk/offline/inner/SingleAPI;->showWebViewByDialog(Ljava/lang/String;Ljava/util/HashMap;[Landroid/os/Bundle;)V

    .line 170
    return-void
.end method

.method private static synLocalNickname(Ljava/lang/String;Ljava/lang/String;)V
    .locals 3
    .param p0, "serverData"    # Ljava/lang/String;
    .param p1, "newNickname"    # Ljava/lang/String;

    .line 279
    const-string v0, "status"

    :try_start_0
    new-instance v1, Lorg/json/JSONObject;

    invoke-direct {v1, p0}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    .line 280
    .local v1, "json":Lorg/json/JSONObject;
    invoke-virtual {v1, v0}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_0

    return-void

    .line 281
    :cond_0
    invoke-virtual {v1, v0}, Lorg/json/JSONObject;->getInt(Ljava/lang/String;)I

    move-result v0

    .line 282
    .local v0, "status":I
    if-gtz v0, :cond_1

    return-void

    .line 283
    :cond_1
    invoke-static {p1}, Lcom/joym/sdk/user/UserAPI;->syncLocalNickName(Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 286
    .end local v0    # "status":I
    .end local v1    # "json":Lorg/json/JSONObject;
    goto :goto_0

    .line 284
    :catch_0
    move-exception v0

    .line 285
    .local v0, "e":Ljava/lang/Exception;
    invoke-virtual {v0}, Ljava/lang/Exception;->printStackTrace()V

    .line 287
    .end local v0    # "e":Ljava/lang/Exception;
    :goto_0
    return-void
.end method

.method private static updateUser(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    .locals 1
    .param p0, "nickname"    # Ljava/lang/String;
    .param p1, "phoneNumber"    # Ljava/lang/String;

    const-string v0, "{\"status\":1}"

    return-object v0
.end method

.method public static updateUserT(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .locals 1
    .param p0, "nickName"    # Ljava/lang/String;
    .param p1, "phoneNumber"    # Ljava/lang/String;
    .param p2, "callback"    # Ljava/lang/String;

    .line 233
    new-instance v0, Lcom/joym/gamecenter/sdk/pbase/SDKHelper$1;

    invoke-direct {v0, p0, p1, p2}, Lcom/joym/gamecenter/sdk/pbase/SDKHelper$1;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 239
    invoke-virtual {v0}, Lcom/joym/gamecenter/sdk/pbase/SDKHelper$1;->start()V

    .line 240
    return-void
.end method
