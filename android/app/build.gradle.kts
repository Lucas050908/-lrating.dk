plugins {
    id("com.android.application")
}

android {
    namespace = "dk.olrating.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "dk.olrating.app"
        minSdk = 24
        targetSdk = 34
        // Hver bygning på GitHub får et højere versionsnummer, så appen kan opdateres
        versionCode = (System.getenv("GITHUB_RUN_NUMBER") ?: "1").toInt()
        versionName = "1.0." + (System.getenv("GITHUB_RUN_NUMBER") ?: "0")
    }

    signingConfigs {
        // Nøglen ligger ikke i koden. GitHub Actions lægger den i en midlertidig fil
        // ud fra hemmelighederne i repoets indstillinger (se README).
        create("olrating") {
            storeFile = file(System.getenv("OLRATING_KEYSTORE") ?: "olrating.keystore")
            storePassword = System.getenv("OLRATING_KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("OLRATING_KEY_ALIAS") ?: "olrating"
            keyPassword = System.getenv("OLRATING_KEYSTORE_PASSWORD") ?: ""
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("olrating")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
