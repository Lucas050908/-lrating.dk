package dk.olrating.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.widget.RemoteViews;

/** Lille widget: én knap, der åbner "Tilføj øl" direkte. */
public class QuickWidget extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) {
            RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget_quick);
            v.setOnClickPendingIntent(R.id.quick, TopWidget.open(ctx, "#tilfoej", 3));
            mgr.updateAppWidget(id, v);
        }
    }
}
