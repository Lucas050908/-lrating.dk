package dk.olrating.app;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapShader;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Shader;
import android.util.Base64;
import android.view.View;
import android.widget.RemoteViews;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

/** Små billeder af øllene til widgets. Hjemmesiden sender dem gennem broen, og de ligger i appens egen mappe. */
final class WImg {
    private WImg() {}

    static final String OK_ID = "[A-Za-z0-9_-]{1,40}";
    /** Billederne fra siden er 288 × 288. Større giver intet, og Android afviser widget-opdateringer på over ca. 1 MB. */
    static final int MAX_PX = 288;

    static File dir(Context ctx) {
        File d = new File(ctx.getFilesDir(), "wimg");
        if (!d.exists()) d.mkdirs();
        return d;
    }

    /** Gemmer de billeder, der følger med, og sletter dem, widgets ikke bruger længere. */
    static void save(Context ctx, String json) {
        try {
            JSONObject o = new JSONObject(json);
            Set<String> keep = new HashSet<>();
            Iterator<String> it = o.keys();
            while (it.hasNext() && keep.size() < 12) {
                String id = it.next();
                String d = o.optString(id);
                if (!id.matches(OK_ID) || !d.startsWith("data:image/jpeg;base64,") || d.length() > 90000) continue;
                byte[] b = Base64.decode(d.substring(d.indexOf(',') + 1), Base64.DEFAULT);
                // Skriv først til en midlertidig fil og omdøb den bagefter, så en widget aldrig læser et halvt skrevet billede
                File tmp = new File(dir(ctx), id + ".tmp");
                try (FileOutputStream f = new FileOutputStream(tmp)) { f.write(b); }
                if (!tmp.renameTo(new File(dir(ctx), id + ".jpg"))) { tmp.delete(); continue; }
                keep.add(id + ".jpg");
            }
            File[] all = dir(ctx).listFiles();
            if (all != null) for (File f : all) if (!keep.contains(f.getName())) f.delete();
        } catch (Exception ignored) {}
    }

    /** Billedet af en øl som kvadrat med runde hjørner. Null, hvis øllen ikke har et billede. */
    static Bitmap load(Context ctx, String id, int px, float radius) {
        try {
            if (id == null || !id.matches(OK_ID) || px < 1) return null;
            if (px > MAX_PX) { radius = radius * MAX_PX / px; px = MAX_PX; }   // hjørnerne skal se ens ud, også når billedet bliver mindre
            File f = new File(dir(ctx), id + ".jpg");
            if (!f.exists()) return null;
            Bitmap src = BitmapFactory.decodeFile(f.getPath());
            if (src == null) return null;
            Bitmap out = Bitmap.createBitmap(px, px, Bitmap.Config.ARGB_8888);
            float s = Math.max(px / (float) src.getWidth(), px / (float) src.getHeight());
            Matrix m = new Matrix();
            m.setScale(s, s);
            m.postTranslate((px - src.getWidth() * s) / 2f, (px - src.getHeight() * s) / 2f);
            BitmapShader sh = new BitmapShader(src, Shader.TileMode.CLAMP, Shader.TileMode.CLAMP);
            sh.setLocalMatrix(m);
            Paint p = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
            p.setShader(sh);
            new Canvas(out).drawRoundRect(new RectF(0, 0, px, px), radius, radius, p);
            return out;
        } catch (Throwable t) {
            return null;
        }
    }

    /** Viser billedet i en ImageView i en widget. Skjuler den, hvis der ikke er noget billede. */
    static boolean into(Context ctx, RemoteViews v, int viewId, String id, int dp, int radiusDp) {
        float den = ctx.getResources().getDisplayMetrics().density;
        Bitmap b = load(ctx, id, Math.round(dp * den), radiusDp * den);
        if (b == null) {
            v.setViewVisibility(viewId, View.GONE);
            return false;
        }
        v.setImageViewBitmap(viewId, b);
        v.setViewVisibility(viewId, View.VISIBLE);
        return true;
    }
}
