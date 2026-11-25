package dk.olrating.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.widget.RemoteViews;

import org.json.JSONObject;

/** Widget: din egen øl-statistik. */
public class StatsWidget extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) mgr.updateAppWidget(id, build(ctx));
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        for (int id : mgr.getAppWidgetIds(new ComponentName(ctx, StatsWidget.class))) mgr.updateAppWidget(id, build(ctx));
    }

    static RemoteViews build(Context ctx) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget_stats);
        String raw = ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE).getString(TopWidget.KEY, null);
        JSONObject me = null;
        try { if (raw != null) me = new JSONObject(raw).optJSONObject("me"); } catch (Exception ignored) {}
        if (me == null || me.optString("name").isEmpty()) {
            v.setTextViewText(R.id.who, "Min statistik");
            v.setTextViewText(R.id.count, "–");
            v.setTextViewText(R.id.avg, "–");
            v.setTextViewText(R.id.style, "Skriv dit navn i appen");
        } else {
            v.setTextViewText(R.id.who, me.optString("name"));
            v.setTextViewText(R.id.count, String.valueOf(me.optInt("beers")));
            v.setTextViewText(R.id.avg, me.optString("avg").isEmpty() ? "–" : me.optString("avg"));
            String st = me.optString("style");
            v.setTextViewText(R.id.style, st.isEmpty() ? "Bedøm din første øl" : "Yndlingsstil: " + st);
        }
        v.setOnClickPendingIntent(R.id.root, TopWidget.open(ctx, "#profil", 6));
        return v;
    }
}
