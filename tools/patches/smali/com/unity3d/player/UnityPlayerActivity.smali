.class public Lcom/unity3d/player/UnityPlayerActivity;
.super Lcom/unity3d/player/UnityPlayerNativeActivity;


# direct methods
.method public constructor <init>()V
    .locals 1

    invoke-direct {p0}, Lcom/unity3d/player/UnityPlayerNativeActivity;-><init>()V

    return-void
.end method


# virtual methods
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 1

    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    move-object/from16 v0, p0

    invoke-static {v0}, Lcom/bearfarm/BearServer;->init(Landroid/app/Activity;)V

    return-void
.end method
