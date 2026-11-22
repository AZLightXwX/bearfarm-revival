.class public Lcom/joym/gamecenter/sdk/offline/net/BasicParams;
.super Ljava/lang/Object;
.source "BasicParams.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 21
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static getBasicParams()Lorg/json/JSONObject;
    .locals 7

    .line 25
    const-string v0, ""

    invoke-static {}, Lcom/joym/sdk/base/SDKConfig;->getApp()Landroid/app/Application;

    move-result-object v1

    .line 27
    .local v1, "mContext":Landroid/content/Context;
    invoke-static {}, Lcom/joym/sdk/base/ParamControl;->getParams()Lorg/json/JSONObject;

    move-result-object v2

    .line 30
    .local v2, "result":Lorg/json/JSONObject;
    :try_start_0
    const-string v3, "app_id"

    invoke-static {}, Lcom/joym/sdk/base/config/GameBaseConfig;->getInstance()Lcom/joym/sdk/base/config/GameBaseConfig;

    move-result-object v4

    invoke-virtual {v4}, Lcom/joym/sdk/base/config/GameBaseConfig;->getAppId()I

    move-result v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 33
    goto :goto_0

    .line 31
    :catch_0
    move-exception v3

    .line 32
    .local v3, "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 35
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_0
    :try_start_1
    const-string v3, "channel_id"

    invoke-static {}, Lcom/joym/sdk/base/config/GameBaseConfig;->getInstance()Lcom/joym/sdk/base/config/GameBaseConfig;

    move-result-object v4

    invoke-virtual {v4}, Lcom/joym/sdk/base/config/GameBaseConfig;->getChannelId()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_1

    .line 38
    goto :goto_1

    .line 36
    :catch_1
    move-exception v3

    .line 37
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 40
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_1
    :try_start_2
    const-string v3, "oaid"

    invoke-static {v1}, Lcom/joym/sdk/base/utils/OaidUtils;->getOaid(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_2
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_2

    .line 43
    goto :goto_2

    .line 41
    :catch_2
    move-exception v3

    .line 42
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 45
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_2
    :try_start_3
    const-string v3, "operator"

    invoke-static {}, Lcom/joym/sdk/base/utils/TelephonyUtil;->getSimOperator()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_3
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_3} :catch_3

    .line 48
    goto :goto_3

    .line 46
    :catch_3
    move-exception v3

    .line 47
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 50
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_3
    :try_start_4
    const-string v3, "country"

    invoke-static {}, Ljava/util/Locale;->getDefault()Ljava/util/Locale;

    move-result-object v4

    invoke-virtual {v4}, Ljava/util/Locale;->getCountry()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_4
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_4} :catch_4

    .line 53
    goto :goto_4

    .line 51
    :catch_4
    move-exception v3

    .line 52
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 55
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_4
    :try_start_5
    const-string v3, "time"

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    invoke-virtual {v2, v3, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;J)Lorg/json/JSONObject;
    :try_end_5
    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_5} :catch_5

    .line 58
    goto :goto_5

    .line 56
    :catch_5
    move-exception v3

    .line 57
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 60
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_5
    :try_start_6
    const-string v3, "versionCode"

    invoke-static {}, Lcom/joym/sdk/base/utils/GameUtil;->getVersionCode()I

    move-result v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;
    :try_end_6
    .catch Ljava/lang/Exception; {:try_start_6 .. :try_end_6} :catch_6

    .line 63
    goto :goto_6

    .line 61
    :catch_6
    move-exception v3

    .line 62
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 65
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_6
    :try_start_7
    const-string v3, "androidid"

    invoke-static {}, Lcom/joym/sdk/base/utils/TelephonyUtil;->getAndroidId()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_7
    .catch Ljava/lang/Exception; {:try_start_7 .. :try_end_7} :catch_7

    .line 68
    goto :goto_7

    .line 66
    :catch_7
    move-exception v3

    .line 67
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 73
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_7
    :try_start_8
    const-string v3, "mobile"

    sget-object v4, Landroid/os/Build;->MODEL:Ljava/lang/String;

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_8
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_8} :catch_8

    .line 76
    goto :goto_8

    .line 74
    :catch_8
    move-exception v3

    .line 75
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 80
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_8
    :try_start_9
    const-string v3, "brand"

    sget-object v4, Landroid/os/Build;->BRAND:Ljava/lang/String;

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_9
    .catch Ljava/lang/Exception; {:try_start_9 .. :try_end_9} :catch_9

    .line 83
    goto :goto_9

    .line 81
    :catch_9
    move-exception v3

    .line 82
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 85
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_9
    :try_start_a
    const-string v3, "language"

    invoke-static {}, Ljava/util/Locale;->getDefault()Ljava/util/Locale;

    move-result-object v4

    invoke-virtual {v4}, Ljava/util/Locale;->getLanguage()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_a
    .catch Ljava/lang/Exception; {:try_start_a .. :try_end_a} :catch_a

    .line 88
    goto :goto_a

    .line 86
    :catch_a
    move-exception v3

    .line 87
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 90
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_a
    :try_start_b
    const-string v3, "imsi"

    invoke-static {}, Lcom/joym/sdk/base/utils/TelephonyUtil;->getIMSI()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_b
    .catch Ljava/lang/Exception; {:try_start_b .. :try_end_b} :catch_b

    .line 93
    goto :goto_b

    .line 91
    :catch_b
    move-exception v3

    .line 92
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 95
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_b
    :try_start_c
    const-string v3, "imei"

    invoke-static {}, Lcom/joym/sdk/base/utils/TelephonyUtil;->getIMEI()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_c
    .catch Ljava/lang/Exception; {:try_start_c .. :try_end_c} :catch_c

    .line 98
    goto :goto_c

    .line 96
    :catch_c
    move-exception v3

    .line 97
    .local v3, "e16":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 100
    .end local v3    # "e16":Ljava/lang/Exception;
    :goto_c
    :try_start_d
    const-string v3, "sdk_ver"

    const-string v4, "3"

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_d
    .catch Ljava/lang/Exception; {:try_start_d .. :try_end_d} :catch_d

    .line 103
    goto :goto_d

    .line 101
    :catch_d
    move-exception v3

    .line 102
    .local v3, "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 110
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_d
    :try_start_e
    const-string v3, "opName"

    invoke-static {}, Lcom/joym/sdk/base/utils/TelephonyUtil;->getOpName()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_e
    .catch Ljava/lang/Exception; {:try_start_e .. :try_end_e} :catch_e

    .line 113
    goto :goto_e

    .line 111
    :catch_e
    move-exception v3

    .line 112
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 115
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_e
    :try_start_f
    const-string v3, "net_type"

    const-string v4, "1"

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_f
    .catch Ljava/lang/Exception; {:try_start_f .. :try_end_f} :catch_f

    .line 118
    goto :goto_f

    .line 116
    :catch_f
    move-exception v3

    .line 117
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 120
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_f
    :try_start_10
    const-string v3, "iccid"

    invoke-static {}, Lcom/joym/sdk/base/utils/TelephonyUtil;->getICCID()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_10
    .catch Ljava/lang/Exception; {:try_start_10 .. :try_end_10} :catch_10

    .line 123
    goto :goto_10

    .line 121
    :catch_10
    move-exception v3

    .line 122
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 125
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_10
    :try_start_11
    const-string v3, "AndroidSystem"

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    sget-object v5, Landroid/os/Build$VERSION;->RELEASE:Ljava/lang/String;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_11
    .catch Ljava/lang/Exception; {:try_start_11 .. :try_end_11} :catch_11

    .line 128
    goto :goto_11

    .line 126
    :catch_11
    move-exception v3

    .line 127
    .restart local v3    # "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V

    .line 133
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_11
    :try_start_12
    invoke-static {}, Lcom/joym/sdk/base/SDKConfig;->getApp()Landroid/app/Application;

    move-result-object v3

    const-string v4, "baseParam"

    invoke-static {v3, v4, v0}, Lcom/joym/sdk/base/SharePreSaver;->get(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 134
    .local v0, "info":Ljava/lang/String;
    invoke-static {v0}, Landroid/text/TextUtils;->isEmpty(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_0

    .line 135
    new-instance v3, Lorg/json/JSONObject;

    invoke-direct {v3, v0}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    .line 136
    .local v3, "obj":Lorg/json/JSONObject;
    invoke-virtual {v3}, Lorg/json/JSONObject;->keys()Ljava/util/Iterator;

    move-result-object v4

    .line 137
    .local v4, "it":Ljava/util/Iterator;, "Ljava/util/Iterator<Ljava/lang/String;>;"
    :goto_12
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_0

    .line 138
    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Ljava/lang/String;

    .line 139
    .local v5, "key":Ljava/lang/String;
    invoke-virtual {v3, v5}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    .line 140
    .local v6, "value":Ljava/lang/String;
    invoke-virtual {v2, v5, v6}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :try_end_12
    .catchall {:try_start_12 .. :try_end_12} :catchall_0

    .line 141
    nop

    .end local v5    # "key":Ljava/lang/String;
    .end local v6    # "value":Ljava/lang/String;
    goto :goto_12

    .line 146
    .end local v0    # "info":Ljava/lang/String;
    .end local v3    # "obj":Lorg/json/JSONObject;
    .end local v4    # "it":Ljava/util/Iterator;, "Ljava/util/Iterator<Ljava/lang/String;>;"
    :cond_0
    goto :goto_13

    .line 143
    :catchall_0
    move-exception v0

    .line 144
    .local v0, "t":Ljava/lang/Throwable;
    invoke-virtual {v0}, Ljava/lang/Throwable;->printStackTrace()V

    .line 149
    .end local v0    # "t":Ljava/lang/Throwable;
    :goto_13
    return-object v2
.end method
