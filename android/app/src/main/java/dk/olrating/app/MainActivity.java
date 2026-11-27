package dk.olrating.app;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * ølrating.dk som Android-app: viser hjemmesiden i fuld skærm,
 * med billed-upload og kamera til stregkodescanneren.
 */
public class MainActivity extends Activity {

    private static final String SITE = "https://xn--lrating-p1a.dk/";
    private static final String SITE_HOST = "lucas050908.github.io";
    private static final String SITE_PATH = "/-lrating.dk";
    private static final int FILE_REQUEST = 1;
    private static final int CAMERA_REQUEST = 2;

    private WebView web;
    private ValueCallback<Uri[]> fileCallback;
    private PermissionRequest pendingPermission;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0F1D36"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);          // øl og bedømmelser gemmes her
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);
        s.setUserAgentString(s.getUserAgentString() + " olratingApp/1");
        CookieManager.getInstance().setAcceptCookie(true);
        web.addJavascriptInterface(new Bridge(this), "OlratingApp");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                if (isOwn(u)) return false;
                // Andre links (fx GitHub, mail, kort) åbnes i telefonens browser eller den app, der hører til.
                // Kun almindelige slags links, og kun i apps, der må åbnes fra en browser (CATEGORY_BROWSABLE).
                String sc = u.getScheme() == null ? "" : u.getScheme().toLowerCase(java.util.Locale.ROOT);
                if (sc.equals("https") || sc.equals("http") || sc.equals("mailto") || sc.equals("geo") || sc.equals("tel")) {
                    try {
                        Intent out = new Intent(Intent.ACTION_VIEW, u);
                        out.addCategory(Intent.CATEGORY_BROWSABLE);
                        startActivity(out);
                    } catch (Exception ignored) { }
                }
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                try {
                    Intent pick = params.createIntent();
                    pick.addCategory(Intent.CATEGORY_OPENABLE);
                    startActivityForResult(Intent.createChooser(pick, "Vælg billede af øllen"), FILE_REQUEST);
                } catch (Exception e) {
                    fileCallback = null;
                    return false;
                }
                return true;
            }

            @Override
            public void onPermissionRequest(PermissionRequest request) {
                runOnUiThread(() -> {
                    if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                        request.grant(request.getResources());
                    } else {
                        pendingPermission = request;
                        requestPermissions(new String[]{Manifest.permission.CAMERA}, CAMERA_REQUEST);
                    }
                });
            }
        });

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            Uri data = getIntent() != null ? getIntent().getData() : null;
            web.loadUrl(isOwn(data) ? data.toString() : SITE);
        }
        web.setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        // Åbnet fra en widget eller en genvej, mens appen allerede kører
        if (intent != null && isOwn(intent.getData())) web.loadUrl(intent.getData().toString());
    }

    /**
     * Kun ølrating.dk må vises i appen. Andre apps kan sende en adresse til appen,
     * og en fremmed side må ikke få adgang til broen til widgets og billeder.
     */
    static boolean isOwn(Uri u) {
        if (u == null || !"https".equals(u.getScheme())) return false;
        String h = u.getHost(), p = u.getPath();
        return "xn--lrating-p1a.dk".equals(h) || "www.xn--lrating-p1a.dk".equals(h) || "ølrating.dk".equals(h)
                || (SITE_HOST.equals(h) && p != null && (p.equals(SITE_PATH) || p.startsWith(SITE_PATH + "/")));
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_REQUEST && fileCallback != null) {
            fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            fileCallback = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        if (requestCode == CAMERA_REQUEST && pendingPermission != null) {
            if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) {
                pendingPermission.grant(pendingPermission.getResources());
            } else {
                pendingPermission.deny();
            }
            pendingPermission = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }
}
