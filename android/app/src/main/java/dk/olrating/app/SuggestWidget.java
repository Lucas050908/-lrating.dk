package dk.olrating.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.widget.RemoteViews;

import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

/** Widget: et forslag til en øl, du ikke har bedømt, og nedtælling til næste øl-dag. */
public class SuggestWidget extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) mgr.updateAppWidget(id, build(ctx));
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        for (int id : mgr.getAppWidgetIds(new ComponentName(ctx, SuggestWidget.class))) mgr.updateAppWidget(id, build(ctx));
    }

    /** Hele dage fra i dag til datoen (åååå-mm-dd). -1 hvis datoen ikke kan læses. */
    static long daysUntil(String iso) {
        try {
            Date t = new SimpleDateFormat("yyyy-MM-dd", Locale.US).parse(iso);
            Calendar c = Calendar.getInstance();
            c.set(Calendar.HOUR_OF_DAY, 0); c.set(Calendar.MINUTE, 0); c.set(Calendar.SECOND, 0); c.set(Calendar.MILLISECOND, 0);
            return Math.round((t.getTime() - c.getTimeInMillis()) / 86400000.0);
        } catch (Exception e) {
            return -1;
        }
    }

    static RemoteViews build(Context ctx) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget_suggest);
        String raw = ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE).getString(TopWidget.KEY, null);
        String hash = "", img = "";
        String name = "Bedøm et par øl", why = "Så foreslår vi nogle, du nok kan lide", score = "", next = "";
        try {
            JSONObject d = raw == null ? new JSONObject() : new JSONObject(raw);
            JSONObject r = d.optJSONObject("rec");
            if (r != null && !r.optString("name").isEmpty()) {
                name = r.optString("name"); why = r.optString("why"); score = r.optString("score");
                String id = r.optString("id");
                if (id.matches("[A-Za-z0-9_-]{1,40}")) hash = "#beer-" + id;
                img = id;
            }
            JSONObject n = d.optJSONObject("next");
            if (n != null) {
                long days = daysUntil(n.optString("date"));
                if (days >= 0) next = (days == 0 ? "I dag" : days == 1 ? "I morgen" : "Om " + days + " dage") + " er det " + n.optString("n");
            }
        } catch (Exception ignored) {}
        v.setTextViewText(R.id.name, name);
        v.setTextViewText(R.id.why, why);
        v.setTextViewText(R.id.score, score);
        v.setTextViewText(R.id.next, next);
        WImg.into(ctx, v, R.id.img, img, 52, 12);
        v.setOnClickPendingIntent(R.id.root, TopWidget.open(ctx, hash, 9));
        return v;
    }
}
