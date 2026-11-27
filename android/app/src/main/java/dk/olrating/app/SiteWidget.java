package dk.olrating.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.widget.RemoteViews;

import org.json.JSONObject;

import java.util.Locale;

/** Widget: tal for hele hjemmesiden. Besøg i alt og i dag, antal øl, bedømmelser og smagere. */
public class SiteWidget extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) mgr.updateAppWidget(id, build(ctx));
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        for (int id : mgr.getAppWidgetIds(new ComponentName(ctx, SiteWidget.class))) mgr.updateAppWidget(id, build(ctx));
    }

    /** 12345 bliver til 12.345. Et tal under 0 betyder, at vi ikke kender det. */
    static String num(long n) {
        return n < 0 ? "–" : String.format(Locale.forLanguageTag("da"), "%,d", n);
    }

    static RemoteViews build(Context ctx) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget_site);
        String raw = ctx.getSharedPreferences(TopWidget.PREFS, Context.MODE_PRIVATE).getString(TopWidget.KEY, null);
        long visits = -1, today = -1, beers = -1, reviews = -1, tasters = -1;
        try {
            if (raw != null) {
                JSONObject d = new JSONObject(raw);
                beers = d.optLong("beers", -1);
                reviews = d.optLong("reviews", -1);
                JSONObject s = d.optJSONObject("site");
                if (s != null) {
                    visits = s.isNull("visits") ? -1 : s.optLong("visits", -1);
                    today = s.isNull("today") ? -1 : s.optLong("today", -1);
                    tasters = s.optLong("tasters", -1);
                }
            }
        } catch (Exception ignored) {}
        v.setTextViewText(R.id.visits, num(visits));
        v.setTextViewText(R.id.today, visits < 0 ? ctx.getString(R.string.w_open_app) : ctx.getString(R.string.w_today_n, num(today)));
        v.setTextViewText(R.id.beers, num(beers));
        v.setTextViewText(R.id.reviews, num(reviews));
        v.setTextViewText(R.id.tasters, num(tasters));
        v.setOnClickPendingIntent(R.id.root, TopWidget.open(ctx, "#om", 11));
        return v;
    }
}
