[app]
title = Spy Game
package.name = spygame
package.domain = com.bensahla

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,ttc

version = 0.1
requirements = python3,kivy,arabic_reshaper,pillow

# إضافة مجلدات الصور إلى التطبيق
source.include_patterns = ui_images/*, player_images/*

# إعدادات الأندرويد
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.gradle_dependencies = ''

# ميزات إضافية
android.permissions = INTERNET
android.arch = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1