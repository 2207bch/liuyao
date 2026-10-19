#!/usr/bin/env bash
# 不使用 Gradle / 不下载任何 Maven 依赖，
# 仅用 Android SDK 镜像预装的 aapt2 / d8 / zipalign / apksigner 手工构建 APK。
set -e

APP_DIR="$(cd "$(dirname "$0")/app" && pwd)"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT}}"
echo "SDK=$SDK"

ANDROID_JAR="$(ls "$SDK"/platforms/android-*/android.jar | sort -V | tail -1)"
BT="$(ls -d "$SDK"/build-tools/*/ | sort -V | tail -1)"
AAPT2="${BT}aapt2"
D8="${BT}d8"
ZIPALIGN="${BT}zipalign"
APKSIGNER="${BT}apksigner"
echo "ANDROID_JAR=$ANDROID_JAR"
echo "BUILD_TOOLS=$BT"

B="manual_out"
rm -rf "$B"
mkdir -p "$B/gen" "$B/obj" "$B/dex" "$B/assets"

# 注入 package 属性（源 Manifest 不改动）
sed 's|<manifest |<manifest package="com.liuyao.app" |' \
  "$APP_DIR/src/main/AndroidManifest.xml" > "$B/AndroidManifest.xml"

# 网页资源（assets/web）
mkdir -p "$B/assets/web"
cp index.html app.js liuyao_core.js liuyao_zhuan.js manifest.json sw.js "$B/assets/web/"
cp -r icons "$B/assets/web/"

# 1) 编译资源
"$AAPT2" compile --dir "$APP_DIR/src/main/res" -o "$B/res.zip"

# 2) 链接：生成 R.java 与未签名基础 APK（含 assets）
"$AAPT2" link \
  -I "$ANDROID_JAR" \
  --manifest "$B/AndroidManifest.xml" \
  -A "$B/assets" \
  --min-sdk-version 21 \
  --target-sdk-version 34 \
  --version-code 1 --version-name 1.0 \
  --java "$B/gen" \
  -o "$B/base.apk" \
  "$B/res.zip"

# 3) 编译 Java（含生成的 R.java）
find "$B/gen" "$APP_DIR/src/main/java" -name '*.java' > "$B/sources.txt"
javac -source 17 -target 17 -nowarn \
  -classpath "$ANDROID_JAR" \
  -d "$B/obj" @"$B/sources.txt"

# 4) 转 dex
find "$B/obj" -name '*.class' > "$B/classes.txt"
"$D8" --output "$B/dex" --lib "$ANDROID_JAR" --min-api 21 @"$B/classes.txt"

# 5) 把 classes.dex 并入 APK
cp "$B/base.apk" "$B/with-dex.apk"
(cd "$B/dex" && zip -j -q "../with-dex.apk" classes.dex)

# 6) 生成调试密钥并对齐、签名
keytool -keystore "$B/debug.keystore" -storepass android -keypass android \
  -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=Android Debug,O=Android,C=US" >/dev/null 2>&1

"$ZIPALIGN" -f 4 "$B/with-dex.apk" "$B/aligned.apk"
"$APKSIGNER" sign \
  --ks "$B/debug.keystore" --ks-pass pass:android --key-pass pass:android \
  --out "六爻预测.apk" "$B/aligned.apk"

echo "构建成功：六爻预测.apk"
"$APKSIGNER" verify "六爻预测.apk" && echo "签名校验通过"
ls -lh "六爻预测.apk"
