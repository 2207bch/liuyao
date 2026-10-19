# -*- coding: utf-8 -*-
"""生成十类专断 + 通用的 Python 期望输出，供 Node 逐类严格对照。"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
PRED = os.path.join(os.path.dirname(HERE), "六爻预测")
sys.path.insert(0, PRED)
import liuyao_core as core
import liuyao_zhuan as zhuan

random.seed(20261019)
cases = []
PATIENTS = ['父母', '官鬼', '妻财', '子孙']


def make_case(beis, y, m, d, idx):
    yao_list, dong = core.qigua_from_tongqian(beis)
    shang, xia = core.build_gua_from_yaos(yao_list)
    gz = core.date_to_ganzhi(y, m, d)
    pan = core.zhuang_gua(shang, xia, dong_yao=dong,
                         yue_zhi=gz["month_zhi"], ri_gan=gz["ri_gan"], ri_zhi=gz["ri_zhi"])
    patient = PATIENTS[idx % 4]
    out = {
        "input": {"beis": beis, "y": y, "m": m, "d": d},
        "求财": core.fenxi_caiyun(pan),
        "功名": zhuan.fenxi_gongming(pan),
        "考试": zhuan.fenxi_kaoshi(pan),
        "婚姻男": zhuan.fenxi_hunyin(pan, "男"),
        "婚姻女": zhuan.fenxi_hunyin(pan, "女"),
        "疾病世": zhuan.fenxi_jibing(pan, "世"),
        "疾病代": zhuan.fenxi_jibing(pan, patient),
        "子女": zhuan.fenxi_zinv(pan),
        "出行": zhuan.fenxi_chuxing(pan),
        "官司": zhuan.fenxi_guansi(pan),
        "房子": zhuan.fenxi_fangzi(pan),
        "合同": zhuan.fenxi_hetong(pan),
        "朋友": zhuan.fenxi_pengyou(pan),
        "通用": core.fenxi_gua(pan),
    }
    cases.append(out)


fixed = [
    ([1, 3, 2, 1, 0, 2], 2026, 10, 19),
    ([1, 1, 1, 1, 1, 1], 2026, 10, 19),
    ([2, 2, 2, 2, 2, 2], 2026, 10, 19),
    ([0, 0, 0, 0, 0, 0], 2024, 2, 4),
    ([3, 3, 3, 3, 3, 3], 1999, 7, 7),
]
idx = 0
for f in fixed:
    make_case(f[0], f[1], f[2], f[3], idx)
    idx += 1

for _ in range(150):
    beis = [random.randint(0, 3) for _ in range(6)]
    if random.random() < 0.2:
        beis = [random.choice([1, 2]) for _ in range(6)]
    y = random.randint(1950, 2050)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    make_case(beis, y, m, d, idx)
    idx += 1

outp = os.path.join(HERE, "zhuan_expected.json")
with open(outp, "w", encoding="utf-8") as f:
    json.dump(cases, f, ensure_ascii=False)
print("cases:", len(cases))
print("out:", outp)
