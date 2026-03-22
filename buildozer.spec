[app]

# (str) Title of your application
title = 老奶快跑

# (str) Package name
package.name = laonaipaokuai

# (str) Package domain (needed for android/ios packaging)
package.domain = org.laonai

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,kv,png,jpg,atlas,ttf

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = True

#
# Android specific
#

[android]

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (bool) Indicate whether the screen should stay on
# Don't go to full sleep mode but keep the screen on.
android.wakelock = True

# (list) Permissions
android.permissions = INTERNET

# (int) Android SDK version to use
#android.sdk = 33

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) Path to buildozer executable
#buildozer.bin = /usr/local/bin/buildozer