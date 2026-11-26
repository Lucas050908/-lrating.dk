package dk.olrating.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.graphics.Bitmap;
import android.widget.RemoteViews;

import org.json.JSONObject;

/** Widget: ugens øl med et stort billede af øllen. */
public class PhotoWidget extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) mgr.updateAppWidget(id, build(ctx));
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        for (int id : mgr.getAppWidgetIds(new ComponentName(ctx, PhotoWidget.class))) mgr.updateAppWidget(id, build(ctx));
    }

    static RemoteViews build(Context ctx) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget_photo);
        String raw = ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE).getString(TopWidget.KEY, null);
        String name = "Ingen øl endnu", meta = "Tryk for at tilføje den første", score = "", hash = "", id = "";
        try {
            JSONObject w = raw == null ? null : new JSONObject(raw).optJSONObject("week");
            if (w != null && !w.optString("name").isEmpty()) {
                name = w.optString("name");
                meta = w.optString("brewery");
                score = w.optString("score");
                id = w.optString("id");
                if (id.matches(WImg.OK_ID)) hash = "#beer-" + id;
            }
        } catch (Exception ignored) {}
        float den = ctx.getResources().getDisplayMetrics().density;
        Bitmap b = WImg.load(ctx, id, Math.min(480, Math.round(220 * den)), 18 * den);
        if (b != null) v.setImageViewBitmap(R.id.photo, b);
        else v.setImageViewResource(R.id.photo, R.mipmap.ic_launcher);
        v.setTextViewText(R.id.name, name);
        v.setTextViewText(R.id.meta, meta);
        v.setTextViewText(R.id.score, score);
        v.setOnClickPendingIntent(R.id.root, TopWidget.open(ctx, hash, 10));
        return v;
    }
}
