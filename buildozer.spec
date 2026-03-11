[app]
title = Spy Game
package.name = spygame
package.domain = com.bensahla

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,ttc

version = 0.1
requirements = python3,kivy,arabic_reshaper,pillow

source.include_patterns = ui_images/*, player_images/*

# إعدادات الأندرويد
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.build_tools = 34.0.0   # سيطلب buildozer تثبيت هذه النسخة
android.gradle_dependencies = ''
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
