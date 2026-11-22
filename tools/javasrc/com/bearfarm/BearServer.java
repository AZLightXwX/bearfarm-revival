package com.bearfarm;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.provider.Settings;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class BearServer {

    private static String server = null;

    public static void init(final Activity act) {
        try {
            Context ctx = act.getApplicationContext();
            SharedPreferences sp = ctx.getSharedPreferences("bearfarm", 0);
            server = sp.getString("server", "");

            // best-effort identity seeding (idempotent)
            seedIdentity(ctx);

            if (server != null && server.length() > 0) {
                return;
            }
            // first run: persist a default immediately so the game has something
            sp.edit().putString("server", "192.168.2.20").commit();
            server = "192.168.2.20";
            // first run: show private-server address dialog
            LinearLayout box = new LinearLayout(act);
            box.setOrientation(LinearLayout.VERTICAL);
            TextView tip = new TextView(act);
            tip.setText("\u8BF7\u8F93\u5165\u79C1\u670D\u5730\u5740\uFF08IP\u6216\u57DF\u540D\uFF09:");
            final EditText input = new EditText(act);
            input.setSingleLine();
            input.setText("192.168.2.20");
            box.addView(tip);
            box.addView(input);
            new AlertDialog.Builder(act)
                    .setTitle("\u718A\u5927\u519C\u573A \u79C1\u670D\u8BBE\u7F6E")
                    .setView(box)
                    .setCancelable(false)
                    .setPositiveButton("\u786E\u5B9A", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface d, int w) {
                            try {
                                String s = normalize(input.getText().toString().trim());
                                if (s.length() == 0) {
                                    s = "192.168.2.20";
                                }
                                act.getApplicationContext()
                                        .getSharedPreferences("bearfarm", 0)
                                        .edit().putString("server", s).commit();
                                server = s;
                                seedIdentity(act.getApplicationContext());
                                // restart the game so managed statics pick up the address
                                android.os.Process.killProcess(android.os.Process.myPid());
                            } catch (Throwable t) {
                                t.printStackTrace();
                                android.os.Process.killProcess(android.os.Process.myPid());
                            }
                        }
                    })
                    .show();
        } catch (Throwable t) {
            t.printStackTrace();
        }
    }

    private static String normalize(String s) {
        if (s.startsWith("http://")) {
            s = s.substring(7);
        }
        if (s.startsWith("https://")) {
            s = s.substring(8);
        }
        if (s.startsWith("tcp://")) {
            s = s.substring(6);
        }
        while (s.endsWith("/")) {
            s = s.substring(0, s.length() - 1);
        }
        return s.trim();
    }

    /** Deterministic per-device uid; only writes when empty. */
    private static void seedIdentity(Context ctx) {
        try {
            String uid = "";
            try {
                String aid = Settings.Secure.getString(ctx.getContentResolver(), "android_id");
                int h = (aid == null || aid.length() == 0) ? 12345 : aid.hashCode();
                if (h < 0) {
                    h = -h;
                }
                uid = String.valueOf(100000 + h % 900000);
            } catch (Throwable t) {
                uid = "100000";
            }
            SharedPreferences pkgSp = ctx.getSharedPreferences(ctx.getPackageName(), 0);
            if (pkgSp.getString("LtAddressKey", "").length() == 0) {
                pkgSp.edit().putString("LtAddressKey", uid)
                        .putString("LtPlayerKey", uid).commit();
            }
            // unblocks TrySendWeb family (money tree / sign-in / legacy paths):
            // v1.6.3 never writes WebRegistId anywhere (dead code), and features
            // gated on it deadlock forever when it is missing.
            if (pkgSp.getString("WebRegistId", "").length() == 0) {
                pkgSp.edit().putString("WebRegistId", uid).commit();
            }
            SharedPreferences gfSp = ctx.getSharedPreferences("game_file", 0);
            if (gfSp.getString("baseParam", "").length() == 0) {
                gfSp.edit().putString("baseParam", "{\"guid\":\"" + uid + "\"}").commit();
            }
        } catch (Throwable t) {
            t.printStackTrace();
        }
    }

    /** Rewrite game-domain URLs to the configured private server. */
    public static String url(String u) {
        try {
            if (u == null) {
                return u;
            }
            if (server == null) {
                server = "";
            }
            if (server.length() == 0) {
                return u;
            }
            if (u.indexOf(".joymeng.com") < 0 && u.indexOf(".joyapi.com") < 0
                    && u.indexOf(".hvapi.com") < 0) {
                return u;
            }
            int p = u.indexOf("://");
            if (p < 0) {
                return u;
            }
            String scheme = u.substring(0, p + 3);
            String rest = u.substring(p + 3);
            int slash = rest.indexOf('/');
            String hostport;
            String path;
            if (slash < 0) {
                hostport = rest;
                path = "";
            } else {
                hostport = rest.substring(0, slash);
                path = rest.substring(slash);
            }
            int colon = hostport.indexOf(':');
            String port = colon >= 0 ? hostport.substring(colon) : "";
            return scheme + server + port + path;
        } catch (Throwable t) {
            return u;
        }
    }
}
