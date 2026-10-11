# ADR 0002: Android In-App Seamless Auto-Update (No Reinstall Required)

## Status
Accepted

## Context
When Android users update an APK manually, they frequently encounter two barriers:
1. `INSTALL_FAILED_UPDATE_INCOMPATIBLE`: Occurs when consecutive APK builds are signed with different keystores (e.g. random CI-generated keystores or debug keys). Android strictly enforces signature identity across updates; any signature change forces an uninstall and data loss.
2. Manual downloading and navigation: Users must leave the app, open a browser, download the APK, locate it in their downloads folder, and trigger package installation.

The user explicitly requested that the installed APK be able to update automatically without having to uninstall or reinstall manually.

## Decision
1. **Permanent Signing Keystore (`release.keystore`)**:
   - Provide and track a persistent, reproducible PKCS#12 keystore (`mobile/android/app/release.keystore`) with fixed alias `mori` and password `android123`.
   - Configure Gradle `buildTypes` so both `release` and `debug` builds sign with this identical certificate.
   - Any future APK built locally or on CI will share the same cryptographic fingerprint, ensuring Android permits seamless in-place package replacement.

2. **Native Package Installation Pipeline**:
   - Declare `<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />` in `AndroidManifest.xml`.
   - Add native methods in `MainActivity.java` (`MoriMainBridge`):
     - `canInstallPackages()`: Checks `getPackageManager().canRequestPackageInstalls()`.
     - `requestInstallPackagesPermission()`: Launches `Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES`.
     - `installApk(filePath)`: Passes the APK URI via `FileProvider` to `Intent.ACTION_VIEW` (`application/vnd.android.package-archive`).
     - `downloadAndInstallApk(apkUrl, callbackId)`: Asynchronously streams the new APK using native `OkHttpClient` with real-time download progress broadcasted to the UI, then immediately launches the installer.

3. **In-App Updater UI (shadcn/ui)**:
   - Provide `updaterService.ts` to check GitHub Releases API (`LanaaAyeraa/Ayeraa-Save-Downloader/releases/latest`) on launch and on user demand in Settings.
   - Render a shadcn/ui Dialog with changelog notes, animated download progress bar, and one-tap update trigger.

## Consequences
- Zero-friction updates: Users get an update alert inside the app, tap "Update Sekarang", watch the progress bar, and confirm the system "Update" prompt without losing any downloaded files or settings.
