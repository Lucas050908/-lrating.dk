package dk.olrating.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.widget.RemoteViews;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Calendar;
import java.util.Locale;

/** Genstand-tæller: +1 direkte fra hjemmeskærmen. Siden henter de nye genstande, næste gang appen åbnes. */
public class UnitsWidget extends AppWidgetProvider {
    static final String ADD = "dk.olrating.app.ADD_UNIT";
    static final String PENDING = "pending_units";
    static final String SAVED_AT = "saved_at";

    static long dayStart() {
        Calendar c = Calendar.getInstance();
        if (c.get(Calendar.HOUR_OF_DAY) < 6) c.add(Calendar.DAY_OF_MONTH, -1);
        c.set(Calendar.HOUR_OF_DAY, 6); c.set(Calendar.MINUTE, 0); c.set(Calendar.SECOND, 0); c.set(Calendar.MILLISECOND, 0);
        return c.getTimeInMillis();
    }

    static JSONArray pending(SharedPreferences p) {
        try { return new JSONArray(p.getString(PENDING, "[]")); } catch (Exception e) { return new JSONArray(); }
    }

    /** Kaldes fra Bridge: giver de ventende genstande til siden og tømmer listen. */
    static synchronized String take(Context ctx) {
        SharedPreferences p = ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE);
        String s = pending(p).toString();
        p.edit().putString(PENDING, "[]").apply();
        return s;
    }

    @Override
    public void onReceive(Context ctx, Intent intent) {
        if (ADD.equals(intent.getAction())) {
            synchronized (UnitsWidget.class) {
                SharedPreferences p = ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE);
                JSONArray a = pending(p);
                if (a.length() < 50) a.put(System.currentTimeMillis());
                p.edit().putString(PENDING, a.toString()).apply();
            }
            refreshAll(ctx);
            return;
        }
        super.onReceive(ctx, intent);
    }

    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) mgr.updateAppWidget(id, build(ctx));
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        for (int id : mgr.getAppWidgetIds(new ComponentName(ctx, UnitsWidget.class))) mgr.updateAppWidget(id, build(ctx));
    }

    static String fmt(double g) {
        String s = String.format(Locale.US, "%.1f", g);
        if (s.endsWith(".0")) s = s.substring(0, s.length() - 2);
        return s.replace('.', ',');
    }

    static RemoteViews build(Context ctx) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget_units);
        SharedPreferences p = ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE);
        long start = dayStart(), weekStart = System.currentTimeMillis() - 7L * 24 * 3600 * 1000;
        double today = 0, week = 0;
        try {
            JSONObject u = new JSONObject(p.getString(TopWidget.KEY, "{}")).optJSONObject("units");
            if (u != null) {
                week = u.optDouble("weekN", 0);
                if (p.getLong(SAVED_AT, 0) >= start) today = u.optDouble("todayN", 0);
            }
        } catch (Exception ignored) {}
        JSONArray a = pending(p);
        for (int i = 0; i < a.length(); i++) {
            long t = a.optLong(i);
            if (t >= start) today += 1;
            if (t >= weekStart) week += 1;
        }
        v.setTextViewText(R.id.today, fmt(today));
        v.setTextViewText(R.id.week, ctx.getString(R.string.w_units_week, fmt(week)));
        v.setTextColor(R.id.today, today > 4 ? 0xFFFF6B8A : 0xFFFFC85A);
        v.setTextViewText(R.id.note, today > 4 ? ctx.getString(R.string.w_units_pause) : ctx.getString(R.string.w_units_today));
        Intent add = new Intent(ctx, UnitsWidget.class).setAction(ADD);
        v.setOnClickPendingIntent(R.id.plus, PendingIntent.getBroadcast(ctx, 7, add, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE));
        v.setOnClickPendingIntent(R.id.root, TopWidget.open(ctx, "#genstande", 8));
        return v;
    }
}
