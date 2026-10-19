#!/usr/bin/env bash
# 不用 Gradle / 不下载任何 Maven 依赖，仅用镜像预装 SDK 工具手工构建。
# 每步通过 GitHub API 上报心跳，便于精确定位。
set -e

issue() {
  local msg="$1"
  curl -s --max-time 15 --connect-timeout 10 -o /dev/null -X POST \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$GITHUB_REPOSITORY/issues" \
    -d '{"title":"【构建心跳】","body":"'"$msg"'"}' || true
}

issue "开始构建 $(date -u +%H:%M:%S)"

APP_DIR="$(cd "$(dirname "$0")/app" && pwd)"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT}}"
ANDROID_JAR="$(ls "$SDK"/platforms/android-*/android.jar | sort -V | tail -1)"
BT="$(ls -d "$SDK"/build-tools/*/ | sort -V | tail -1)"
AAPT2="${BT}aapt2"; D8="${BT}d8"; ZIPALIGN="${BT}zipalign"; APKSIGNER="${BT}apksigner"
issue "环境就绪 jar=$ANDROID_JAR bt=$BT"

B="manual_out"
rm -rf "$B"
mkdir -p "$B/gen" "$B/obj" "$B/dex" "$B/assets/web"
sed 's|<manifest |<manifest package="com.liuyao.app" |' \
  "$APP_DIR/src/main/AndroidManifest.xml" > "$B/AndroidManifest.xml"
cp index.html app.js liuyao_core.js liuyao_zhuan.js manifest.json sw.js "$B/assets/web/"
cp -r icons "$B/assets/web/"

issue "步骤1：aapt2 compile"
"$AAPT2" compile --dir "$APP_DIR/src/main/res" -o "$B/res.zip"

issue "步骤2：aapt2 link"
"$AAPT2" link \
  -I "$ANDROID_JAR" --manifest "$B/AndroidManifest.xml" -A "$B/assets" \
  --min-sdk-version 21 --target-sdk-version 34 \
  --version-code 1 --version-name 1.0 \
  --java "$B/gen" -o "$B/base.apk" "$B/res.zip"

issue "步骤3：javac"
find "$B/gen" "$APP_DIR/src/main/java" -name '*.java' > "$B/sources.txt"
javac -source 17 -target 17 -nowarn -classpath "$ANDROID_JAR" -d "$B/obj" @"$B/sources.txt"

issue "步骤4：d8"
find "$B/obj" -name '*.class' > "$B/classes.txt"
"$D8" --output "$B/dex" --lib "$ANDROID_JAR" --min-api 21 @"$B/classes.txt"

issue "步骤5：合并 dex"
cp "$B/base.apk" "$B/with-dex.apk"
(cd "$B/dex" && zip -j -q "../with-dex.apk" classes.dex)

issue "步骤6：生成密钥"
keytool -keystore "$B/debug.keystore" -storepass android -keypass android \
  -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=Android Debug,O=Android,C=US" >/dev/null 2>&1

issue "步骤7：zipalign"
"$ZIPALIGN" -f 4 "$B/with-dex.apk" "$B/aligned.apk"

issue "步骤8：apksigner"
"$APKSIGNER" sign --ks "$B/debug.keystore" --ks-pass pass:android --key-pass pass:android \
  --out "六爻预测.apk" "$B/aligned.apk"

issue "完成：$(ls -lh 六爻预测.apk | awk '{print $5}')"
"$APKSIGNER" verify "六爻预测.apk" && issue "签名校验通过"
