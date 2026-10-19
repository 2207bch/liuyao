/* Python vs Node 对照测试：干支、排盘、求财断语 */
const fs = require("fs");
const path = require("path");
const LY = require("./liuyao_core.js");

const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "expected.json"), "utf8"));

let fail = 0;
function deepEq(a, b, p) {
  if (typeof a === "number" && typeof b === "number") {
    if (Math.abs(a - b) > 1e-9) { fail++; console.log("NUM 不符 @", p, a, "!==", b); }
    return;
  }
  if (a === null || b === null || typeof a !== "object" || typeof b !== "object") {
    if (a !== b) { fail++; console.log("VAL 不符 @", p, JSON.stringify(a), "!==", JSON.stringify(b)); }
    return;
  }
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) {
      fail++; console.log("ARR 不符 @", p, JSON.stringify(a), "!==", JSON.stringify(b)); return;
    }
    for (let i = 0; i < a.length; i++) deepEq(a[i], b[i], p + "[" + i + "]");
    return;
  }
  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) {
    const onlyA = ka.filter(k => !(k in b)), onlyB = kb.filter(k => !(k in a));
    fail++; console.log("KEY 不符 @", p, "仅A:", onlyA, "仅B:", onlyB);
  }
  for (const k of ka) {
    if (k in b) deepEq(a[k], b[k], p + "." + k);
  }
}

let gzFail = 0, panFail = 0, caiFail = 0;
cases.forEach((c, idx) => {
  const { beis, y, m, d } = c.input;
  const [yao_list, dong] = LY.qigua_from_tongqian(beis);
  const [shang, xia] = LY.build_gua_from_yaos(yao_list);
  const gz = LY.date_to_ganzhi(y, m, d);

  const before = fail;
  deepEq(gz, c.gz, `#${idx}.gz`);
  if (fail > before) gzFail++;

  const pan = LY.zhuang_gua(shang, xia, dong, gz.month_zhi, gz.ri_gan, gz.ri_zhi);
  const before2 = fail;
  deepEq(pan, c.paipan, `#${idx}.pan`);
  if (fail > before2) panFail++;

  const cai = LY.fenxi_caiyun(pan);
  if (JSON.stringify(cai) !== JSON.stringify(c.caiyun)) {
    caiFail++;
    if (caiFail <= 3) {
      console.log(`--- 求财 #${idx} 文本不符 beis=${JSON.stringify(beis)} ${y}-${m}-${d}`);
      for (let i = 0; i < Math.max(cai.length, c.caiyun.length); i++) {
        if (cai[i] !== c.caiyun[i]) {
          console.log("  PY:", c.caiyun[i]);
          console.log("  JS:", cai[i]);
        }
      }
    }
  }
});

console.log("================================");
console.log("总用例:", cases.length);
console.log("干支不符用例:", gzFail);
console.log("排盘不符用例:", panFail);
console.log("求财断语不符用例:", caiFail);
console.log("深度比较问题总数:", fail);
if (gzFail === 0 && panFail === 0 && caiFail === 0 && fail === 0) {
  console.log("PASS: 核心排盘/干支/求财 与 Python 完全一致");
} else {
  process.exit(1);
}
