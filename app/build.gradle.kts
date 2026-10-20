plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.forja.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.kaiquecupertino.forja"
        minSdk = 26
        targetSdk = 36
        // No GitHub Actions o número da compilação vira a versão (usado no aviso de "nova versão disponível")
        val numero = System.getenv("GITHUB_RUN_NUMBER")?.toIntOrNull() ?: 1
        versionCode = numero
        versionName = "1.$numero"
        // Build da Play Store (-Pplay): sem aviso de APK novo (a Play proíbe app que se atualiza por fora dela)
        buildConfigField("boolean", "LOJA_PLAY", if (project.hasProperty("play")) "true" else "false")
    }

    // Chave de assinatura própria (secrets do GitHub). Sem ela, assina com a chave de depuração.
    val chave = System.getenv("FORJA_KEYSTORE")?.let { file(it) }?.takeIf { it.exists() }
    signingConfigs {
        if (chave != null) create("forja") {
            storeFile = chave
            storePassword = System.getenv("FORJA_KEYSTORE_SENHA")
            keyAlias = System.getenv("FORJA_CHAVE_ALIAS") ?: "forja"
            keyPassword = System.getenv("FORJA_CHAVE_SENHA") ?: System.getenv("FORJA_KEYSTORE_SENHA")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.findByName("forja") ?: signingConfigs.getByName("debug")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true; buildConfig = true }
    androidResources { noCompress += listOf("webp", "json", "mp4") }
}

dependencies {
    val bom = platform("androidx.compose:compose-bom:2024.12.01")
    implementation(bom)
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.animation:animation")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.media3:media3-exoplayer:1.5.1")
}
