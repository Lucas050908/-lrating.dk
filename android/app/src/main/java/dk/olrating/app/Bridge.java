package dk.olrating.app;

import android.content.Context;
import android.webkit.JavascriptInterface;

/** Hjemmesiden kalder window.OlratingApp.updateWidget(json), når data ændrer sig. */
public class Bridge {
    private final Context ctx;

    Bridge(Context ctx) { this.ctx = ctx.getApplicationContext(); }

    @JavascriptInterface
    public void updateWidget(String json) {
        if (json == null || json.length() > 20000) return;
        ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE)
           .edit().putString(TopWidget.KEY, json).apply();
        TopWidget.refreshAll(ctx);
    }

    @JavascriptInterface
    public boolean isApp() { return true; }
}
