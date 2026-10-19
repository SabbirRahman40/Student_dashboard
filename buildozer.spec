[app]

# (str) Title of your application
title = Sabbir Smart Student Dashboard

# (str) Package name; lowercase letters and numbers only
package.name = studentdashboard

# (str) Package domain (reverse DNS style)
package.domain = com.sabbirrahman

# (str) Source directory containing main.py and student_data.json
source.dir = .

# (list) Files to include in the APK
source.include_exts = py,json,png,jpg,jpeg,kv,atlas,ttf,otf

# (list) Exclude build files and Git metadata
source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__,venv,.venv

# (str) Application version
version = 1.0.0

# (list) Python packages required by this app
requirements = python3,kivy

# (str) Screen orientation
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0

# (str) Android permissions; no permissions are required for the current code
android.permissions =

# (int) Android API target and minimum supported API
android.api = 34
android.minapi = 21

# (str) Android NDK version compatible with common python-for-android builds
android.ndk = 25b

# (bool) Accept Android SDK license prompts automatically
android.accept_sdk_license = True

# (str) Architectures to build
android.archs = arm64-v8a, armeabi-v7a

# (bool) Copy source files into the APK assets
android.copy_libs = 1

# (str) Android application category
android.category = education

# (str) Log level
log_level = 2

[buildozer]
# (int) Verbosity level
log_level = 2

# (str) Build directory
build_dir = ./.buildozer

# (str) Output directory
bin_dir = ./bin
