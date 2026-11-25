package dk.olrating.app;

import android.content.ContentValues;
import android.content.Context;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
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
        LatestWidget.refreshAll(ctx);
        StatsWidget.refreshAll(ctx);
    }

    /** Gemmer et delekort (data-URL med JPEG) i telefonens Billeder. */
    @JavascriptInterface
    public boolean saveImage(String dataUrl, String name) {
        try {
            if (dataUrl == null || !dataUrl.startsWith("data:image/jpeg;base64,")) return false;
            byte[] bytes = Base64.decode(dataUrl.substring(dataUrl.indexOf(',') + 1), Base64.DEFAULT);
            String file = (name == null ? "olrating.jpg" : name).replaceAll("[^\\p{L}\\p{N}._-]", "-");
            if (Build.VERSION.SDK_INT >= 29) {
                ContentValues v = new ContentValues();
                v.put(MediaStore.Images.Media.DISPLAY_NAME, file);
                v.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg");
                v.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/ølrating");
                Uri uri = ctx.getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, v);
                if (uri == null) return false;
                try (OutputStream o = ctx.getContentResolver().openOutputStream(uri)) { o.write(bytes); }
            } else {
                File dir = ctx.getExternalFilesDir(Environment.DIRECTORY_PICTURES);
                if (dir == null) return false;
                try (FileOutputStream o = new FileOutputStream(new File(dir, file))) { o.write(bytes); }
            }
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    @JavascriptInterface
    public boolean isApp() { return true; }
}
