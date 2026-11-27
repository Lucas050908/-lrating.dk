package dk.olrating.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.widget.RemoteViews;

import org.json.JSONArray;
import org.json.JSONObject;

/** Widget: ugens øl og top 3. */
public class TopWidget extends AppWidgetProvider {
    static final String PREFS = "olrating_widget";
    static final String KEY = "data";
    static final String SITE = "https://xn--lrating-p1a.dk/";

    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) mgr.updateAppWidget(id, build(ctx));
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        int[] ids = mgr.getAppWidgetIds(new ComponentName(ctx, TopWidget.class));
        for (int id : ids) mgr.updateAppWidget(id, build(ctx));
    }

    static PendingIntent open(Context ctx, String hash, int req) {
        Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(SITE + hash), ctx, MainActivity.class);
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        return PendingIntent.getActivity(ctx, req, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static RemoteViews build(Context ctx) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget_top);
        String raw = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY, null);
        int[] rows = {R.id.top1, R.id.top2, R.id.top3};
        try {
            JSONObject d = raw == null ? new JSONObject() : new JSONObject(raw);
            JSONObject w = d.optJSONObject("week");
            if (w != null) {
                v.setTextViewText(R.id.week_name, w.optString("name"));
                v.setTextViewText(R.id.week_meta, w.optString("brewery"));
                v.setTextViewText(R.id.week_score, w.optString("score"));
                WImg.into(ctx, v, R.id.week_img, w.optString("id"), 48, 12);
            } else {
                v.setViewVisibility(R.id.week_img, android.view.View.GONE);
                v.setTextViewText(R.id.week_name, ctx.getString(R.string.w_no_beer));
                v.setTextViewText(R.id.week_meta, ctx.getString(R.string.w_add_first));
                v.setTextViewText(R.id.week_score, "");
            }
            JSONArray top = d.optJSONArray("top");
            for (int i = 0; i < rows.length; i++) {
                if (top != null && i < top.length()) {
                    JSONObject t = top.getJSONObject(i);
                    v.setTextViewText(rows[i], (i + 1) + ". " + t.optString("name") + "  ·  " + t.optString("score"));
                } else {
                    v.setTextViewText(rows[i], "");
                }
            }
            v.setTextViewText(R.id.footer, ctx.getString(R.string.w_footer, d.optInt("beers"), d.optInt("reviews")));
        } catch (Exception e) {
            v.setTextViewText(R.id.week_name, "ølrating.dk");
        }
        v.setOnClickPendingIntent(R.id.root, open(ctx, "", 1));
        v.setOnClickPendingIntent(R.id.add, open(ctx, "#tilfoej", 2));
        return v;
    }
}
