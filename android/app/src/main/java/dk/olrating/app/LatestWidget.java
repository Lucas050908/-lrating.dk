package dk.olrating.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.widget.RemoteViews;

import org.json.JSONArray;
import org.json.JSONObject;

/** Widget: de seneste bedømmelser. */
public class LatestWidget extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) mgr.updateAppWidget(id, build(ctx));
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        for (int id : mgr.getAppWidgetIds(new ComponentName(ctx, LatestWidget.class))) mgr.updateAppWidget(id, build(ctx));
    }

    static RemoteViews build(Context ctx) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget_latest);
        int[] rows = {R.id.l1, R.id.l2, R.id.l3, R.id.l4};
        int[] scores = {R.id.s1, R.id.s2, R.id.s3, R.id.s4};
        int[] imgs = {R.id.i1, R.id.i2, R.id.i3, R.id.i4};
        String raw = ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE).getString(TopWidget.KEY, null);
        JSONArray a = null;
        try { if (raw != null) a = new JSONObject(raw).optJSONArray("latest"); } catch (Exception ignored) {}
        int n = a == null ? 0 : a.length();
        for (int i = 0; i < rows.length; i++) {
            if (i < n) {
                JSONObject r = a.optJSONObject(i);
                v.setTextViewText(rows[i], r.optString("name") + "  ·  " + r.optString("who"));
                v.setTextViewText(scores[i], r.optString("score"));
                WImg.into(ctx, v, imgs[i], r.optString("id"), 22, 6);
            } else {
                v.setViewVisibility(imgs[i], android.view.View.GONE);
                v.setTextViewText(rows[i], i == 0 && n == 0 ? "Ingen bedømmelser endnu" : "");
                v.setTextViewText(scores[i], "");
            }
        }
        v.setOnClickPendingIntent(R.id.root, TopWidget.open(ctx, "", 4));
        v.setOnClickPendingIntent(R.id.add, TopWidget.open(ctx, "#tilfoej", 5));
        return v;
    }
}
