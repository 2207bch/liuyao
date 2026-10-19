/* Python vs Node 对照：十类专断 + 通用，逐行严格文本对比 */
const fs = require("fs");
const path = require("path");
const LY = require("./liuyao_core.js");
const LYZH = require("./liuyao_zhuan.js");

const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "zhuan_expected.json"), "utf8"));
const PATIENTS = ["父母", "官鬼", "妻财", "子孙"];

// 类别 -> 函数（pan, idx）=> 行数组
const FUNS = {
  "求财": (pan) => LY.fenxi_caiyun(pan),
  "功名": (pan) => LYZH.fenxi_gongming(pan),
  "考试": (pan) => LYZH.fenxi_kaoshi(pan),
  "婚姻男": (pan) => LYZH.fenxi_hunyin(pan, "男"),
  "婚姻女": (pan) => LYZH.fenxi_hunyin(pan, "女"),
  "疾病世": (pan) => LYZH.fenxi_jibing(pan, "世"),
  "疾病代": (pan, idx) => LYZH.fenxi_jibing(pan, PATIENTS[idx % 4]),
  "子女": (pan) => LYZH.fenxi_zinv(pan),
  "出行": (pan) => LYZH.fenxi_chuxing(pan),
  "官司": (pan) => LYZH.fenxi_guansi(pan),
  "房子": (pan) => LYZH.fenxi_fangzi(pan),
  "合同": (pan) => LYZH.fenxi_hetong(pan),
  "朋友": (pan) => LYZH.fenxi_pengyou(pan),
  "通用": (pan) => LY.fenxi_gua(pan)
};

let total = 0, fail = 0;
const shown = {};
cases.forEach((c, idx) => {
  const { beis, y, m, d } = c.input;
  const [yao_list, dong] = LY.qigua_from_tongqian(beis);
  const [shang, xia] = LY.build_gua_from_yaos(yao_list);
  const gz = LY.date_to_ganzhi(y, m, d);
  const pan = LY.zhuang_gua(shang, xia, dong, gz.month_zhi, gz.ri_gan, gz.ri_zhi);

  for (const cat in FUNS) {
    total++;
    const got = FUNS[cat](pan, idx);
    const exp = c[cat];
    if (JSON.stringify(got) !== JSON.stringify(exp)) {
      fail++;
      if (!shown[cat] || shown[cat] < 3) {
        shown[cat] = (shown[cat] || 0) + 1;
        console.log(`--- [${cat}] #${idx} 不符 beis=${JSON.stringify(beis)} ${y}-${m}-${d}`);
        for (let i = 0; i < Math.max(got.length, exp.length); i++) {
          if (got[i] !== exp[i]) {
            console.log("  PY[" + i + "]:", exp[i]);
            console.log("  JS[" + i + "]:", got[i]);
          }
        }
      }
    }
  }
});

console.log("\n==============================");
console.log("总对比:", total, " 不符:", fail);
console.log(fail === 0 ? "ALL PASS" : "HAS FAIL");
