# -*- coding: utf-8 -*-
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
PRED = os.path.join(os.path.dirname(HERE), "六爻预测")
sys.path.insert(0, PRED)
import liuyao_core as core

random.seed(20261019)
cases = []

def make_case(beis, y, m, d):
    yao_list, dong = core.qigua_from_tongqian(beis)
    shang, xia = core.build_gua_from_yaos(yao_list)
    gz = core.date_to_ganzhi(y, m, d)
    pan = core.zhuang_gua(shang, xia, dong_yao=dong,
                          yue_zhi=gz["month_zhi"], ri_gan=gz["ri_gan"], ri_zhi=gz["ri_zhi"])
    cai = core.fenxi_caiyun(pan)
    cases.append({
        "input": {"beis": beis, "y": y, "m": m, "d": d},
        "gz": gz,
        "paipan": pan,
        "caiyun": cai,
    })

# 固定卦例
fixed = [
    ([1,3,2,1,0,2], 2026, 10, 19),
    ([1,1,1,1,1,1], 2026, 10, 19),
    ([2,2,2,2,2,2], 2026, 10, 19),
    ([0,0,0,0,0,0], 2024, 2, 4),
    ([3,3,3,3,3,3], 1999, 7, 7),
]
for f in fixed:
    make_case(*f)

# 随机卦例（含安静、多动）
for _ in range(300):
    beis = [random.randint(0,3) for _ in range(6)]
    if random.random() < 0.2:
        beis = [random.choice([1,2]) for _ in range(6)]  # 安静卦
    y = random.randint(1950, 2050)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    make_case(beis, y, m, d)

out = os.path.join(HERE, "expected.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(cases, f, ensure_ascii=False)
print("cases:", len(cases))
print("out:", out)
