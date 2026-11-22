.class public Lcom/support/utils/HttpClientSupport;
.super Ljava/lang/Object;
.source "HttpClientSupport.java"


# static fields
.field private static isSanbox:Ljava/util/concurrent/atomic/AtomicBoolean;

.field private static isScend:Z


# direct methods
.method static constructor <clinit>()V
    .locals 2

    .line 64
    new-instance v0, Ljava/util/concurrent/atomic/AtomicBoolean;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Ljava/util/concurrent/atomic/AtomicBoolean;-><init>(Z)V

    sput-object v0, Lcom/support/utils/HttpClientSupport;->isSanbox:Ljava/util/concurrent/atomic/AtomicBoolean;

    .line 66
    sput-boolean v1, Lcom/support/utils/HttpClientSupport;->isScend:Z

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 22
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static check(Ljava/lang/String;)Ljava/lang/String;
    .locals 1
    .param p0, "data"    # Ljava/lang/String;

    .line 37
    invoke-static {p0}, Lcom/support/utils/Support;->check(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method private static isSandboxModel(Ljava/lang/String;)Ljava/lang/String;
    .locals 21
    .param p0, "url"    # Ljava/lang/String;

    move-object/from16 v1, p0

    invoke-static {v1}, Lcom/bearfarm/BearServer;->url(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 69
    const-string v0, ""

    const/4 v2, 0x1

    :try_start_0
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "isSanbox="

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget-object v4, Lcom/support/utils/HttpClientSupport;->isSanbox:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-static {v3}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V

    .line 70
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "isScend="

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    sget-boolean v4, Lcom/support/utils/HttpClientSupport;->isScend:Z

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-static {v3}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V

    .line 71
    sget-boolean v3, Lcom/support/utils/HttpClientSupport;->isScend:Z
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    const-string v4, "http"

    const-string v5, "https"

    const-string v6, "joyapi"

    const-string v7, "_test"

    const-string v8, "netlog"

    const-string v9, "log"

    const-string v10, "\\."

    const-string v11, "cgsbox"

    const/4 v12, 0x0

    if-eqz v3, :cond_1

    .line 72
    :try_start_1
    sget-object v0, Lcom/support/utils/HttpClientSupport;->isSanbox:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 73
    invoke-virtual {v1, v10}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v0

    aget-object v0, v0, v12

    .line 74
    .local v0, "s1":Ljava/lang/String;
    invoke-virtual {v0, v9}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_0

    invoke-virtual {v0, v8}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_0

    invoke-virtual {v0, v11}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_0

    .line 75
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v0, v3}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v3, v6, v11}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v3, v5, v4}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v3
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    move-object v1, v3

    .line 79
    .end local v0    # "s1":Ljava/lang/String;
    .end local p0    # "url":Ljava/lang/String;
    .local v1, "url":Ljava/lang/String;
    :cond_0
    nop

    .line 118
    sput-boolean v2, Lcom/support/utils/HttpClientSupport;->isScend:Z

    .line 79
    return-object v1

    .line 82
    .end local v1    # "url":Ljava/lang/String;
    .restart local p0    # "url":Ljava/lang/String;
    :cond_1
    :try_start_2
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-static {}, Landroid/os/Environment;->getExternalStorageDirectory()Ljava/io/File;

    move-result-object v13

    invoke-virtual {v13}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object v13

    invoke-virtual {v3, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v13, "/.aa/aa/aa/lttext.txt"

    invoke-virtual {v3, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 83
    .local v3, "filePath":Ljava/lang/String;
    new-instance v13, Ljava/io/File;

    invoke-direct {v13, v3}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    .line 84
    .local v13, "f":Ljava/io/File;
    move-object v14, v0

    .line 85
    .local v14, "openLog":Ljava/lang/String;
    const/4 v15, 0x0

    .line 86
    .local v15, "json":Lorg/json/JSONObject;
    const/16 v16, 0x0

    .line 87
    .local v16, "jarray":Lorg/json/JSONArray;
    invoke-virtual {v13}, Ljava/io/File;->exists()Z

    move-result v17

    if-eqz v17, :cond_5

    .line 88
    const-string v17, "file exist"

    invoke-static/range {v17 .. v17}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V

    .line 91
    invoke-static {v13}, Lcom/support/utils/HttpClientSupport;->readFile(Ljava/io/File;)Ljava/lang/String;

    move-result-object v17

    move-object/from16 v18, v17

    .line 92
    .local v18, "content":Ljava/lang/String;
    invoke-static/range {v18 .. v18}, Landroid/text/TextUtils;->isEmpty(Ljava/lang/CharSequence;)Z

    move-result v17
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    if-eqz v17, :cond_2

    .line 118
    sput-boolean v2, Lcom/support/utils/HttpClientSupport;->isScend:Z

    .line 92
    return-object v1

    .line 93
    :cond_2
    :try_start_3
    new-instance v2, Lorg/json/JSONArray;

    move-object/from16 v12, v18

    .end local v18    # "content":Ljava/lang/String;
    .local v12, "content":Ljava/lang/String;
    invoke-direct {v2, v12}, Lorg/json/JSONArray;-><init>(Ljava/lang/String;)V

    .line 94
    .end local v16    # "jarray":Lorg/json/JSONArray;
    .local v2, "jarray":Lorg/json/JSONArray;
    const/16 v16, 0x0

    move/from16 v18, v16

    move-object/from16 v16, v15

    move/from16 v15, v18

    .local v15, "i":I
    .local v16, "json":Lorg/json/JSONObject;
    :goto_0
    move-object/from16 v18, v3

    .end local v3    # "filePath":Ljava/lang/String;
    .local v18, "filePath":Ljava/lang/String;
    invoke-virtual {v2}, Lorg/json/JSONArray;->length()I

    move-result v3

    if-ge v15, v3, :cond_4

    .line 95
    invoke-virtual {v2, v15}, Lorg/json/JSONArray;->getJSONObject(I)Lorg/json/JSONObject;

    move-result-object v3

    .line 96
    .end local v16    # "json":Lorg/json/JSONObject;
    .local v3, "json":Lorg/json/JSONObject;
    move-object/from16 v19, v12

    .end local v12    # "content":Ljava/lang/String;
    .local v19, "content":Ljava/lang/String;
    const-string v12, "\u6d4b\u8bd5Log"

    move-object/from16 v20, v13

    .end local v13    # "f":Ljava/io/File;
    .local v20, "f":Ljava/io/File;
    const-string v13, "name"

    invoke-virtual {v3, v13}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v13

    invoke-virtual {v12, v13}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v12

    if-eqz v12, :cond_3

    .line 97
    new-instance v12, Ljava/lang/StringBuilder;

    invoke-direct {v12}, Ljava/lang/StringBuilder;-><init>()V

    const-string v13, "state"

    invoke-virtual {v3, v13}, Lorg/json/JSONObject;->getBoolean(Ljava/lang/String;)Z

    move-result v13

    invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    invoke-virtual {v12, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v12}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    move-object v14, v0

    .line 98
    move-object/from16 v16, v3

    goto :goto_1

    .line 94
    :cond_3
    add-int/lit8 v15, v15, 0x1

    move-object/from16 v16, v3

    move-object/from16 v3, v18

    move-object/from16 v12, v19

    move-object/from16 v13, v20

    goto :goto_0

    .end local v3    # "json":Lorg/json/JSONObject;
    .end local v19    # "content":Ljava/lang/String;
    .end local v20    # "f":Ljava/io/File;
    .restart local v12    # "content":Ljava/lang/String;
    .restart local v13    # "f":Ljava/io/File;
    .restart local v16    # "json":Lorg/json/JSONObject;
    :cond_4
    move-object/from16 v19, v12

    move-object/from16 v20, v13

    .line 102
    .end local v12    # "content":Ljava/lang/String;
    .end local v13    # "f":Ljava/io/File;
    .end local v15    # "i":I
    .restart local v19    # "content":Ljava/lang/String;
    .restart local v20    # "f":Ljava/io/File;
    :goto_1
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "json ="

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Lorg/json/JSONArray;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V

    .line 103
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "openLog111 ="

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lcom/joym/sdk/base/GLog;->i(Ljava/lang/String;)V

    .line 104
    const-string v0, "true"

    invoke-virtual {v0, v14}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_6

    .line 106
    sget-object v0, Lcom/support/utils/HttpClientSupport;->isSanbox:Ljava/util/concurrent/atomic/AtomicBoolean;

    const/4 v3, 0x1

    invoke-virtual {v0, v3}, Ljava/util/concurrent/atomic/AtomicBoolean;->set(Z)V

    .line 107
    invoke-static {}, Lcom/joym/sdk/base/SDKConfig;->getApp()Landroid/app/Application;

    move-result-object v0

    const-string v3, "\u5f53\u524d\u662f\u6c99\u7bb1\u6d4b\u8bd5\u6a21\u5f0f"

    invoke-static {v0, v3}, Lcom/fxlib/util/android/FAToast;->show(Landroid/content/Context;Ljava/lang/String;)V

    .line 108
    invoke-virtual {v1, v10}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v0

    const/4 v3, 0x0

    aget-object v0, v0, v3

    .line 109
    .restart local v0    # "s1":Ljava/lang/String;
    invoke-virtual {v0, v9}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_6

    invoke-virtual {v0, v8}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_6

    .line 110
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v0, v3}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v3, v6, v11}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v3, v5, v4}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v3
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    move-object v1, v3

    .end local p0    # "url":Ljava/lang/String;
    .restart local v1    # "url":Ljava/lang/String;
    goto :goto_2

    .line 87
    .end local v0    # "s1":Ljava/lang/String;
    .end local v1    # "url":Ljava/lang/String;
    .end local v2    # "jarray":Lorg/json/JSONArray;
    .end local v18    # "filePath":Ljava/lang/String;
    .end local v19    # "content":Ljava/lang/String;
    .end local v20    # "f":Ljava/io/File;
    .local v3, "filePath":Ljava/lang/String;
    .restart local v13    # "f":Ljava/io/File;
    .local v15, "json":Lorg/json/JSONObject;
    .local v16, "jarray":Lorg/json/JSONArray;
    .restart local p0    # "url":Ljava/lang/String;
    :cond_5
    move-object/from16 v18, v3

    move-object/from16 v20, v13

    .line 118
    .end local v3    # "filePath":Ljava/lang/String;
    .end local v13    # "f":Ljava/io/File;
    .end local v14    # "openLog":Ljava/lang/String;
    .end local v15    # "json":Lorg/json/JSONObject;
    .end local v16    # "jarray":Lorg/json/JSONArray;
    .end local p0    # "url":Ljava/lang/String;
    .restart local v1    # "url":Ljava/lang/String;
    :cond_6
    :goto_2
    const/4 v2, 0x1

    sput-boolean v2, Lcom/support/utils/HttpClientSupport;->isScend:Z

    .line 119
    goto :goto_3

    .line 115
    .end local v1    # "url":Ljava/lang/String;
    .restart local p0    # "url":Ljava/lang/String;
    :catchall_0
    move-exception v0

    .line 116
    .local v0, "ex":Ljava/lang/Throwable;
    :try_start_4
    invoke-virtual {v0}, Ljava/lang/Throwable;->printStackTrace()V
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_1

    .line 118
    .end local v0    # "ex":Ljava/lang/Throwable;
    const/4 v2, 0x1

    sput-boolean v2, Lcom/support/utils/HttpClientSupport;->isScend:Z

    .line 119
    nop

    .line 120
    .end local p0    # "url":Ljava/lang/String;
    .restart local v1    # "url":Ljava/lang/String;
    :goto_3
    return-object v1

    .line 118
    .end local v1    # "url":Ljava/lang/String;
    .restart local p0    # "url":Ljava/lang/String;
    :catchall_1
    move-exception v0

    const/4 v2, 0x1

    move-object v3, v0

    sput-boolean v2, Lcom/support/utils/HttpClientSupport;->isScend:Z

    .line 119
    goto :goto_5

    :goto_4
    throw v3

    :goto_5
    goto :goto_4
.end method

.method public static parse(Ljava/lang/String;I)Ljava/lang/String;
    .locals 1
    .param p0, "data"    # Ljava/lang/String;
    .param p1, "type"    # I

    .line 42
    invoke-static {p0, p1}, Lcom/support/utils/Support;->parse(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public static post1(Ljava/lang/String;Lorg/json/JSONObject;)V
    .locals 1
    .param p0, "url"    # Ljava/lang/String;
    .param p1, "params"    # Lorg/json/JSONObject;

    .line 27
    invoke-static {p0}, Lcom/support/utils/HttpClientSupport;->isSandboxModel(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0, p1}, Lcom/support/utils/Support;->post1(Ljava/lang/String;Lorg/json/JSONObject;)V

    .line 28
    return-void
.end method

.method public static post2(Ljava/lang/String;Lorg/json/JSONObject;)Ljava/lang/String;
    .locals 1
    .param p0, "url"    # Ljava/lang/String;
    .param p1, "params"    # Lorg/json/JSONObject;

    .line 32
    invoke-static {p0}, Lcom/support/utils/HttpClientSupport;->isSandboxModel(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0, p1}, Lcom/support/utils/Support;->post2(Ljava/lang/String;Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public static post3(Ljava/lang/String;Ljava/lang/String;Lorg/json/JSONObject;)Ljava/lang/String;
    .locals 1
    .param p0, "url"    # Ljava/lang/String;
    .param p1, "data"    # Ljava/lang/String;
    .param p2, "params"    # Lorg/json/JSONObject;

    .line 47
    invoke-static {p0}, Lcom/support/utils/HttpClientSupport;->isSandboxModel(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0, p1, p2}, Lcom/support/utils/Support;->post3(Ljava/lang/String;Ljava/lang/String;Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public static post4(Ljava/lang/String;Lorg/json/JSONObject;)Ljava/lang/String;
    .locals 1
    .param p0, "url"    # Ljava/lang/String;
    .param p1, "params"    # Lorg/json/JSONObject;

    .line 52
    invoke-static {p0}, Lcom/support/utils/HttpClientSupport;->isSandboxModel(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0, p1}, Lcom/support/utils/Support;->post4(Ljava/lang/String;Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public static printE(Ljava/lang/String;Ljava/lang/String;)V
    .locals 0
    .param p0, "tag"    # Ljava/lang/String;
    .param p1, "message"    # Ljava/lang/String;

    .line 59
    invoke-static {p0, p1}, Lcom/support/utils/Support;->printE(Ljava/lang/String;Ljava/lang/String;)V

    .line 60
    return-void
.end method

.method public static printI(Ljava/lang/String;Ljava/lang/String;)V
    .locals 0
    .param p0, "tag"    # Ljava/lang/String;
    .param p1, "message"    # Ljava/lang/String;

    .line 56
    invoke-static {p0, p1}, Lcom/support/utils/Support;->printI(Ljava/lang/String;Ljava/lang/String;)V

    .line 57
    return-void
.end method

.method public static readFile(Ljava/io/File;)Ljava/lang/String;
    .locals 5
    .param p0, "file"    # Ljava/io/File;

    .line 130
    :try_start_0
    invoke-virtual {p0}, Ljava/io/File;->exists()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 131
    new-instance v0, Ljava/io/FileInputStream;

    invoke-direct {v0, p0}, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V

    .line 132
    .local v0, "fis":Ljava/io/FileInputStream;
    invoke-virtual {v0}, Ljava/io/FileInputStream;->available()I

    move-result v1

    .line 133
    .local v1, "length":I
    new-array v2, v1, [B

    .line 134
    .local v2, "buffer":[B
    invoke-virtual {v0, v2}, Ljava/io/FileInputStream;->read([B)I

    .line 135
    invoke-virtual {v0}, Ljava/io/FileInputStream;->close()V

    .line 136
    new-instance v3, Ljava/lang/String;

    const-string v4, "UTF-8"

    invoke-direct {v3, v2, v4}, Ljava/lang/String;-><init>([BLjava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 137
    .local v3, "jsonStr":Ljava/lang/String;
    nop

    .line 138
    return-object v3

    .line 143
    .end local v0    # "fis":Ljava/io/FileInputStream;
    .end local v1    # "length":I
    .end local v2    # "buffer":[B
    .end local v3    # "jsonStr":Ljava/lang/String;
    :cond_0
    goto :goto_0

    .line 141
    :catch_0
    move-exception v0

    .line 142
    .local v0, "ex":Ljava/lang/Exception;
    invoke-virtual {v0}, Ljava/lang/Exception;->printStackTrace()V

    .line 144
    .end local v0    # "ex":Ljava/lang/Exception;
    :goto_0
    const/4 v0, 0x0

    return-object v0
.end method
