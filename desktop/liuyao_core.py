# -*- coding: utf-8 -*-
"""
六爻预测核心算法
基于《卜筮正宗》《增删卜易》理论体系
"""

# ============================================================
# 一、基础数据
# ============================================================

# 天干
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 地支五行
DIZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 天干五行
TIANGAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}

# 天干阴阳（甲丙戊庚壬为阳，乙丁己辛癸为阴）
TIANGAN_YINYANG = {
    '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳',
    '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'
}

# 五行相生
WUXING_SHENG = {'金': '水', '水': '木', '木': '火', '火': '土', '土': '金'}
# 五行相克
WUXING_KE = {'金': '木', '木': '土', '土': '水', '水': '火', '火': '金'}

# 八卦：键为卦名，值为 (自然象, 五行, 阴阳, 三爻[初,二,三], 纳甲地支[初~上(内+外)])
BAGUA = {
    '乾': {'xiang': '天', 'wuxing': '金', 'yinyang': '阳',
           'yao': [1, 1, 1],
           'nazhi_nei': ['子', '寅', '辰'], 'nazhi_wai': ['午', '申', '戌'],
           'tiangan_nei': '甲', 'tiangan_wai': '壬'},
    '兑': {'xiang': '泽', 'wuxing': '金', 'yinyang': '阴',
           'yao': [1, 1, 0],
           'nazhi_nei': ['巳', '卯', '丑'], 'nazhi_wai': ['亥', '酉', '未'],
           'tiangan_nei': '丁', 'tiangan_wai': '丁'},
    '离': {'xiang': '火', 'wuxing': '火', 'yinyang': '阴',
           'yao': [1, 0, 1],
           'nazhi_nei': ['卯', '丑', '亥'], 'nazhi_wai': ['酉', '未', '巳'],
           'tiangan_nei': '己', 'tiangan_wai': '己'},
    '震': {'xiang': '雷', 'wuxing': '木', 'yinyang': '阳',
           'yao': [1, 0, 0],
           'nazhi_nei': ['子', '寅', '辰'], 'nazhi_wai': ['午', '申', '戌'],
           'tiangan_nei': '庚', 'tiangan_wai': '庚'},
    '巽': {'xiang': '风', 'wuxing': '木', 'yinyang': '阴',
           'yao': [0, 1, 1],
           'nazhi_nei': ['丑', '亥', '酉'], 'nazhi_wai': ['未', '巳', '卯'],
           'tiangan_nei': '辛', 'tiangan_wai': '辛'},
    '坎': {'xiang': '水', 'wuxing': '水', 'yinyang': '阳',
           'yao': [0, 1, 0],
           'nazhi_nei': ['寅', '辰', '午'], 'nazhi_wai': ['申', '戌', '子'],
           'tiangan_nei': '戊', 'tiangan_wai': '戊'},
    '艮': {'xiang': '山', 'wuxing': '土', 'yinyang': '阳',
           'yao': [0, 0, 1],
           'nazhi_nei': ['辰', '午', '申'], 'nazhi_wai': ['戌', '子', '寅'],
           'tiangan_nei': '丙', 'tiangan_wai': '丙'},
    '坤': {'xiang': '地', 'wuxing': '土', 'yinyang': '阴',
           'yao': [0, 0, 0],
           'nazhi_nei': ['未', '巳', '卯'], 'nazhi_wai': ['丑', '亥', '酉'],
           'tiangan_nei': '乙', 'tiangan_wai': '癸'},
}

# 八宫卦序：每宫 (本宫, 一世, 二世, 三世, 四世, 五世, 游魂, 归魂)
# 每个卦为 (上卦, 下卦, 卦名)
BAGONG = {
    '乾': [
        ('乾', '乾', '乾为天'),
        ('乾', '巽', '天风姤'),
        ('乾', '艮', '天山遁'),
        ('乾', '坤', '天地否'),
        ('巽', '坤', '风地观'),
        ('艮', '坤', '山地剥'),
        ('离', '坤', '火地晋'),
        ('离', '乾', '火天大有'),
    ],
    '兑': [
        ('兑', '兑', '兑为泽'),
        ('兑', '坎', '泽水困'),
        ('兑', '坤', '泽地萃'),
        ('兑', '艮', '泽山咸'),
        ('坎', '艮', '水山蹇'),
        ('坤', '艮', '地山谦'),
        ('震', '艮', '雷山小过'),
        ('震', '兑', '雷泽归妹'),
    ],
    '离': [
        ('离', '离', '离为火'),
        ('离', '艮', '火山旅'),
        ('离', '巽', '火风鼎'),
        ('离', '坎', '火水未济'),
        ('艮', '坎', '山水蒙'),
        ('巽', '坎', '风水涣'),
        ('乾', '坎', '天水讼'),
        ('乾', '离', '天火同人'),
    ],
    '震': [
        ('震', '震', '震为雷'),
        ('震', '坤', '雷地豫'),
        ('震', '坎', '雷水解'),
        ('震', '巽', '雷风恒'),
        ('坤', '巽', '地风升'),
        ('坎', '巽', '水风井'),
        ('兑', '巽', '泽风大过'),
        ('兑', '震', '泽雷随'),
    ],
    '巽': [
        ('巽', '巽', '巽为风'),
        ('巽', '乾', '风天小畜'),
        ('巽', '离', '风火家人'),
        ('巽', '震', '风雷益'),
        ('乾', '震', '天雷无妄'),
        ('离', '震', '火雷噬嗑'),
        ('艮', '震', '山雷颐'),
        ('艮', '巽', '山风蛊'),
    ],
    '坎': [
        ('坎', '坎', '坎为水'),
        ('坎', '兑', '水泽节'),
        ('坎', '震', '水雷屯'),
        ('坎', '离', '水火既济'),
        ('兑', '离', '泽火革'),
        ('震', '离', '雷火丰'),
        ('坤', '离', '地火明夷'),
        ('坤', '坎', '地水师'),
    ],
    '艮': [
        ('艮', '艮', '艮为山'),
        ('艮', '离', '山火贲'),
        ('艮', '乾', '山天大畜'),
        ('艮', '兑', '山泽损'),
        ('离', '兑', '火泽睽'),
        ('乾', '兑', '天泽履'),
        ('巽', '兑', '风泽中孚'),
        ('巽', '艮', '风山渐'),
    ],
    '坤': [
        ('坤', '坤', '坤为地'),
        ('坤', '震', '地雷复'),
        ('坤', '兑', '地泽临'),
        ('坤', '乾', '地天泰'),
        ('震', '乾', '雷天大壮'),
        ('兑', '乾', '泽天夬'),
        ('坎', '乾', '水天需'),
        ('坎', '坤', '水地比'),
    ],
}

# 世爻位置（按宫位序号0~7：本宫、一世~五世、游魂、归魂）
# 索引0=本宫(世在6爻), 1=一世(世在1爻), ..., 5=五世(世在5爻), 6=游魂(世在4爻), 7=归魂(世在3爻)
SHI_POS = [6, 1, 2, 3, 4, 5, 4, 3]
# 宫位名称
GONGWEI_NAME = ['本宫', '一世', '二世', '三世', '四世', '五世', '游魂', '归魂']

# 六神顺序
LIUSHEN = ['青龙', '朱雀', '勾陈', '腾蛇', '白虎', '玄武']
# 根据日干确定初爻起始六神
LIUSHEN_QISHI = {
    '甲': 0, '乙': 0,  # 青龙
    '丙': 1, '丁': 1,  # 朱雀
    '戊': 2,            # 勾陈
    '己': 3,            # 腾蛇
    '庚': 4, '辛': 4,  # 白虎
    '壬': 5, '癸': 5,  # 玄武
}

# 六亲
LIUQIN = ['兄弟', '子孙', '妻财', '官鬼', '父母']

# 六冲（地支对冲）
LIUCHONG = {
    '子': '午', '午': '子',
    '丑': '未', '未': '丑',
    '寅': '申', '申': '寅',
    '卯': '酉', '酉': '卯',
    '辰': '戌', '戌': '辰',
    '巳': '亥', '亥': '巳',
}

# 六合
LIUHE = {
    '子': '丑', '丑': '子',
    '寅': '亥', '亥': '寅',
    '卯': '戌', '戌': '卯',
    '辰': '酉', '酉': '辰',
    '巳': '申', '申': '巳',
    '午': '未', '未': '午',
}

# 三合局
SANHE = [
    (['申', '子', '辰'], '水'),
    (['寅', '午', '戌'], '火'),
    (['巳', '酉', '丑'], '金'),
    (['亥', '卯', '未'], '木'),
]

# 旬空表：每旬开头的天干地支序号 -> 空亡地支
XUNKONG = {
    0: ['戌', '亥'],   # 甲子旬
    10: ['申', '酉'],  # 甲戌旬（甲在序号0，戌在序号10）
    8: ['午', '未'],   # 甲申旬（申序号8）
    6: ['辰', '巳'],   # 甲午旬（午序号6）
    4: ['寅', '卯'],   # 甲辰旬（辰序号4）
    2: ['子', '丑'],   # 甲寅旬（寅序号2）
}


# ============================================================
# 二、工具函数
# ============================================================

def get_ganzhi_index(gan, zhi):
    """根据天干地支返回六十甲子序号（0~59）"""
    gan_idx = TIANGAN.index(gan)
    zhi_idx = DIZHI.index(zhi)
    # 六十甲子中，天干序号和地支序号奇偶必须一致
    # 序号 n 满足 n % 10 == gan_idx, n % 12 == zhi_idx
    for n in range(60):
        if n % 10 == gan_idx and n % 12 == zhi_idx:
            return n
    return -1


def get_xunkong(ri_gan, ri_zhi):
    """根据日干支计算旬空地支"""
    ganzhi_n = get_ganzhi_index(ri_gan, ri_zhi)
    if ganzhi_n < 0:
        return []
    # 旬首 = ganzhi_n - (ganzhi_n % 10)
    xun_shou = ganzhi_n - (ganzhi_n % 10)
    xun_shou_zhi_idx = xun_shou % 12
    # 空亡 = 旬首地支往前推两个
    kong1_idx = (xun_shou_zhi_idx + 10) % 12
    kong2_idx = (xun_shou_zhi_idx + 11) % 12
    return [DIZHI[kong1_idx], DIZHI[kong2_idx]]


# ============================================================
# 公历日期转干支（年柱以立春为界，月柱按十二节，日柱连续推算）
# ============================================================
import datetime as _dt

# 换月的十二个“节”及其后进入的月支（公历近似日期，实际节气多在该日前后1天内）
# (月, 日, 进入的月支)
_JIEQI = [
    (2, 4, '寅'),    # 立春 → 正月寅
    (3, 6, '卯'),    # 惊蛰 → 二月卯
    (4, 5, '辰'),    # 清明 → 三月辰
    (5, 6, '巳'),    # 立夏 → 四月巳
    (6, 6, '午'),    # 芒种 → 五月午
    (7, 7, '未'),    # 小暑 → 六月未
    (8, 8, '申'),    # 立秋 → 七月申
    (9, 8, '酉'),    # 白露 → 八月酉
    (10, 8, '戌'),   # 寒露 → 九月戌
    (11, 7, '亥'),   # 立冬 → 十月亥
    (12, 7, '子'),   # 大雪 → 十一月子
    (1, 6, '丑'),    # 小寒 → 十二月丑
]

# 五虎遁：年干起寅月（正月）天干
_WUHU_DUN = {
    '甲': '丙', '己': '丙',   # 甲己之年丙作首
    '乙': '戊', '庚': '戊',   # 乙庚之岁戊为头
    '丙': '庚', '辛': '庚',   # 丙辛之岁寻庚起
    '丁': '壬', '壬': '壬',   # 丁壬壬位顺行流
    '戊': '甲', '癸': '甲',   # 戊癸甲寅好追求
}
# 月支从寅开始的顺序
_YUE_ZHI_ORDER = ['寅', '卯', '辰', '巳', '午', '未',
                  '申', '酉', '戌', '亥', '子', '丑']

# 日柱基准：1900-01-01 为甲戌日（六十甲子序号10，甲子=0）
_RI_BASE_DATE = _dt.date(1900, 1, 1)
_RI_BASE_IDX = 10


def get_month_zhi(month, day):
    """根据公历月日，按十二节确定月建地支"""
    md = month * 100 + day
    if md >= 204:   # 立春之后，按节气顺推
        for m, d, zhi in _JIEQI:
            if md < m * 100 + d:
                # 落在“上一个节”之后：返回该节之前的月支
                idx = _YUE_ZHI_ORDER.index(zhi)
                return _YUE_ZHI_ORDER[(idx - 1) % 12]
        return '子'   # 12月7日大雪之后
    if md >= 106:   # 小寒(1/6)后、立春前 → 丑月
        return '丑'
    return '子'     # 1月1日~小寒前，仍是子月（上年十一月）


def get_year_pillar(year, month, day):
    """年柱（以立春2/4为界，立春前算上一年），返回(年干, 年支, 实际干支年)"""
    md = month * 100 + day
    ganzhi_year = year if md >= 204 else year - 1
    idx = (ganzhi_year - 4) % 60
    return TIANGAN[idx % 10], DIZHI[idx % 12], ganzhi_year


def get_month_gan(year_gan, month_zhi):
    """五虎遁：由年干、月支推月干"""
    yin_gan = _WUHU_DUN[year_gan]
    offset = _YUE_ZHI_ORDER.index(month_zhi)
    gan_idx = (TIANGAN.index(yin_gan) + offset) % 10
    return TIANGAN[gan_idx]


def get_day_pillar(year, month, day):
    """日柱：由公历日期连续推算，返回(日干, 日支)"""
    d = _dt.date(year, month, day)
    delta = (d - _RI_BASE_DATE).days
    idx = (_RI_BASE_IDX + delta) % 60
    return TIANGAN[idx % 10], DIZHI[idx % 12]


def date_to_ganzhi(year, month, day):
    """
    公历日期 → 四柱中的年月日干支
    返回 dict：year_gan, year_zhi, month_gan, month_zhi(月建),
              ri_gan, ri_zhi, xunkong(旬空地支列表)
    """
    year_gan, year_zhi, _ = get_year_pillar(year, month, day)
    month_zhi = get_month_zhi(month, day)
    month_gan = get_month_gan(year_gan, month_zhi)
    ri_gan, ri_zhi = get_day_pillar(year, month, day)
    xunkong = get_xunkong(ri_gan, ri_zhi)
    return {
        'year_gan': year_gan, 'year_zhi': year_zhi,
        'month_gan': month_gan, 'month_zhi': month_zhi,
        'ri_gan': ri_gan, 'ri_zhi': ri_zhi,
        'xunkong': xunkong,
    }


def get_liuqin(gong_wuxing, yao_wuxing):
    """根据卦宫五行和爻的五行确定六亲"""
    if yao_wuxing == gong_wuxing:
        return '兄弟'
    # 生我者父母
    if WUXING_SHENG.get(yao_wuxing) == gong_wuxing:
        return '父母'
    # 我生者子孙
    if WUXING_SHENG.get(gong_wuxing) == yao_wuxing:
        return '子孙'
    # 克我者官鬼
    if WUXING_KE.get(yao_wuxing) == gong_wuxing:
        return '官鬼'
    # 我克者妻财
    if WUXING_KE.get(gong_wuxing) == yao_wuxing:
        return '妻财'
    return '未知'


def get_wuxing_relation(wx1, wx2):
    """判断wx1对wx2的关系：同我/生我/我生/克我/我克"""
    if wx1 == wx2:
        return '同'
    if WUXING_SHENG.get(wx1) == wx2:
        return '生'  # wx1生wx2
    if WUXING_SHENG.get(wx2) == wx1:
        return '被生'  # wx2生wx1
    if WUXING_KE.get(wx1) == wx2:
        return '克'  # wx1克wx2
    if WUXING_KE.get(wx2) == wx1:
        return '被克'  # wx2克wx1
    return '无'


# ============================================================
# 三、卦象查找与构建
# ============================================================

def find_gua(shang_gua, xia_gua):
    """根据上下卦查找六十四卦信息，返回 (宫名, 宫位序号, 卦名) 或 None"""
    for gong_name, gua_list in BAGONG.items():
        for idx, (shang, xia, name) in enumerate(gua_list):
            if shang == shang_gua and xia == xia_gua:
                return gong_name, idx, name
    return None


def build_gua_from_yaos(yao_list):
    """
    根据六爻阴阳构建卦象
    yao_list: [初爻, 二爻, 三爻, 四爻, 五爻, 上爻]，1=阳，0=阴
    返回 (上卦名, 下卦名)
    """
    xia_yao = yao_list[0:3]  # 初二三爻为下卦
    shang_yao = yao_list[3:6]  # 四五上爻为上卦

    def match_gua(yao3):
        for name, info in BAGUA.items():
            if info['yao'] == yao3:
                return name
        return None

    xia_gua = match_gua(xia_yao)
    shang_gua = match_gua(shang_yao)
    return shang_gua, xia_gua


# ============================================================
# 四、装卦（纳甲、六亲、世应、六神）
# ============================================================

def zhuang_gua(shang_gua, xia_gua, dong_yao=None, yue_zhi=None, ri_gan=None, ri_zhi=None):
    """
    装卦主函数
    参数：
        shang_gua: 上卦名
        xia_gua: 下卦名
        dong_yao: 动爻列表（1~6），如 [3, 5] 表示三爻五爻动
        yue_zhi: 月建地支，如 '子'
        ri_gan: 日干，如 '甲'
        ri_zhi: 日支，如 '子'
    返回完整卦盘字典
    """
    if dong_yao is None:
        dong_yao = []

    gua_info = find_gua(shang_gua, xia_gua)
    if gua_info is None:
        return None
    gong_name, gongwei_idx, gua_name = gua_info
    gong_wuxing = BAGUA[gong_name]['wuxing']

    # 世应位置
    shi_pos = SHI_POS[gongwei_idx]  # 1~6
    ying_pos = shi_pos + 3 if shi_pos <= 3 else shi_pos - 3

    # 纳甲地支：下卦用内卦纳支，上卦用外卦纳支
    xia_nazhi = BAGUA[xia_gua]['nazhi_nei']  # 初~三爻
    shang_nazhi = BAGUA[shang_gua]['nazhi_wai']  # 四~上爻
    nazhi = xia_nazhi + shang_nazhi  # 初~上爻，共6个

    # 纳甲天干
    xia_tiangan = BAGUA[xia_gua]['tiangan_nei']
    shang_tiangan = BAGUA[shang_gua]['tiangan_wai']
    naggan = [xia_tiangan]*3 + [shang_tiangan]*3

    # 六爻阴阳
    xia_yao = BAGUA[xia_gua]['yao']  # 初~三
    shang_yao = BAGUA[shang_gua]['yao']  # 四~上（注意：外卦的初爻对应全卦四爻）
    yao_yinyang = xia_yao + shang_yao

    # 六亲
    liuqin_list = []
    for zhi in nazhi:
        yao_wx = DIZHI_WUXING[zhi]
        liuqin_list.append(get_liuqin(gong_wuxing, yao_wx))

    # 六神（根据日干）
    liushen_list = [''] * 6
    if ri_gan and ri_gan in LIUSHEN_QISHI:
        start = LIUSHEN_QISHI[ri_gan]
        for i in range(6):
            liushen_list[i] = LIUSHEN[(start + i) % 6]

    # 旬空
    xunkong = []
    if ri_gan and ri_zhi:
        xunkong = get_xunkong(ri_gan, ri_zhi)

    # 组装每爻信息（从上爻到初爻排列，方便显示）
    yaos = []
    for pos in range(6, 0, -1):  # 上爻=6 到 初爻=1
        idx = pos - 1
        zhi = nazhi[idx]
        is_dong = pos in dong_yao
        is_shi = (pos == shi_pos)
        is_ying = (pos == ying_pos)

        # 旬空判断
        is_kong = zhi in xunkong if xunkong else False
        # 月破判断
        is_po = False
        if yue_zhi and zhi == LIUCHONG.get(yue_zhi):
            is_po = True

        yao_data = {
            'pos': pos,           # 爻位 1~6
            'yinyang': yao_yinyang[idx],  # 1阳0阴
            'gan': naggan[idx],
            'zhi': zhi,
            'wuxing': DIZHI_WUXING[zhi],
            'liuqin': liuqin_list[idx],
            'liushen': liushen_list[idx],
            'is_dong': is_dong,
            'is_shi': is_shi,
            'is_ying': is_ying,
            'is_kong': is_kong,
            'is_po': is_po,
        }
        yaos.append(yao_data)

    # 变卦（动爻阴阳反转）
    bian_yaos = list(yao_yinyang)
    bian_dong = []
    for d in dong_yao:
        bian_yaos[d-1] = 1 - bian_yaos[d-1]
        bian_dong.append(d)

    bian_shang, bian_xia = build_gua_from_yaos(bian_yaos)
    bian_info = find_gua(bian_shang, bian_xia) if bian_shang and bian_xia else None

    bian_gua = None
    if bian_info and dong_yao:
        b_gong, b_gw_idx, b_name = bian_info
        # 变卦的纳甲（地支按变卦上下卦）；六亲仍按本卦宫论（《增删卜易·动变章》：
        # 泽天夬变出天风姤，变卦六爻皆标本卦坤宫之六亲，不按变卦乾宫）。
        b_xia_nazhi = BAGUA[bian_xia]['nazhi_nei']
        b_shang_nazhi = BAGUA[bian_shang]['nazhi_wai']
        b_nazhi = b_xia_nazhi + b_shang_nazhi
        b_gong_wx = BAGUA[b_gong]['wuxing']
        b_liuqin = [get_liuqin(gong_wuxing, DIZHI_WUXING[z]) for z in b_nazhi]

        bian_yaos_data = []
        for pos in range(6, 0, -1):
            idx = pos - 1
            bian_yaos_data.append({
                'pos': pos,
                'yinyang': bian_yaos[idx],
                'zhi': b_nazhi[idx],
                'wuxing': DIZHI_WUXING[b_nazhi[idx]],
                'liuqin': b_liuqin[idx],
                'is_dong': pos in dong_yao,
            })
        bian_gua = {
            'name': b_name,
            'gong': b_gong,
            'gongwei': GONGWEI_NAME[b_gw_idx],
            'shang': bian_shang,
            'xia': bian_xia,
            'yaos': bian_yaos_data,
        }

    result = {
        'name': gua_name,
        'gong': gong_name,
        'gongwei': GONGWEI_NAME[gongwei_idx],
        'gong_wuxing': gong_wuxing,
        'shang': shang_gua,
        'xia': xia_gua,
        'shi_pos': shi_pos,
        'ying_pos': ying_pos,
        'dong_yao': dong_yao,
        'yue_zhi': yue_zhi,
        'ri_gan': ri_gan,
        'ri_zhi': ri_zhi,
        'xunkong': xunkong,
        'yaos': yaos,  # 从上爻到初爻排列
        'bian_gua': bian_gua,
    }
    return result


# ============================================================
# 五、起卦
# ============================================================

# 铜钱摇卦结果定义
# 三枚铜钱，每枚 1=背（阳面），0=字（阴面）
# 一背二字 = 单（少阳，静阳爻）
# 二背一字 = 拆（少阴，静阴爻）
# 三背     = 重（老阳，动爻，阳变阴）
# 三字     = 交（老阴，动爻，阴变阳）

def tongqian_yao(bei_count):
    """
    根据背的数量（0~3）返回爻的信息
    返回 (阴阳 1阳0阴, 是否动爻, 名称, 符号)
    """
    if bei_count == 1:   # 一背二字，少阳
        return 1, False, '单', '━━━'
    elif bei_count == 2:  # 二背一字，少阴
        return 0, False, '拆', '━ ━'
    elif bei_count == 3:  # 三背，老阳（动）
        return 1, True, '重', '━━━ ○'
    elif bei_count == 0:  # 三字，老阴（动）
        return 0, True, '交', '━ ━ ×'
    return 0, False, '?', '?'


def qigua_from_tongqian(liu_ci_results):
    """
    根据六次摇卦结果起卦
    liu_ci_results: 六次摇卦的背数列表，按顺序 [初爻, 二爻, 三爻, 四爻, 五爻, 上爻]
    返回 (六爻阴阳列表, 动爻列表)
    """
    yao_list = []
    dong_list = []
    for i, bei in enumerate(liu_ci_results):
        yy, dong, name, sym = tongqian_yao(bei)
        yao_list.append(yy)
        if dong:
            dong_list.append(i + 1)
    return yao_list, dong_list


# ============================================================
# 六、断卦分析
# ============================================================

# 常见占问事项与用神对照
YONGSHEN_MAP = {
    '功名': '官鬼', '官运': '官鬼', '事业': '官鬼', '工作': '官鬼',
    '升职': '官鬼', '升迁': '官鬼', '考试': '父母', '学业': '父母',
    '文书': '父母', '合同': '父母', '房子': '父母', '车辆': '父母',
    '求财': '妻财', '财运': '妻财', '生意': '妻财', '买卖': '妻财',
    '妻子': '妻财', '钱财': '妻财', '婚姻': '官鬼', '感情': '官鬼',
    '丈夫': '官鬼', '男友': '官鬼', '疾病': '官鬼', '病': '官鬼',
    '子女': '子孙', '孩子': '子孙', '儿子': '子孙', '女儿': '子孙',
    '兄弟': '兄弟', '朋友': '兄弟', '姐妹': '兄弟', '同事': '兄弟',
    '官司': '官鬼', '盗贼': '官鬼', '出行': '妻财', '行人': '六亲',
}


def fenxi_gua(paipan, yongshen_type=None):
    """
    分析卦盘，生成断卦分析文本
    paipan: zhuang_gua 返回的卦盘
    yongshen_type: 指定用神六亲类型，如 '官鬼'、'妻财' 等；None则不指定
    返回分析结果列表（每条为一段文字）
    """
    fenxi = []
    yaos = paipan['yaos']  # 从上爻到初爻
    # 转为初爻到上爻方便处理
    yaos_shunxu = list(reversed(yaos))

    yue = paipan['yue_zhi']
    ri_g = paipan['ri_gan']
    ri_z = paipan['ri_zhi']
    xunkong = paipan['xunkong']
    dong = paipan['dong_yao']

    # --- 1. 卦名卦宫 ---
    head = f"【卦名】{paipan['name']}（{paipan['gong']}宫{paipan['gongwei']}卦，{paipan['gong_wuxing']}）"
    if paipan['bian_gua']:
        bg = paipan['bian_gua']
        head += f"  之  {bg['name']}（{bg['gong']}宫{bg['gongwei']}卦）"
    fenxi.append(head)

    # --- 2. 日月与旬空 ---
    riyue = []
    if yue:
        riyue.append(f"月建{yue}{DIZHI_WUXING[yue]}")
    if ri_g and ri_z:
        riyue.append(f"日辰{ri_g}{ri_z}{DIZHI_WUXING[ri_z]}")
    if xunkong:
        riyue.append(f"旬空{xunkong[0]}{xunkong[1]}")
    if riyue:
        fenxi.append("【日月】" + '，'.join(riyue))

    # --- 3. 动爻 ---
    if dong:
        dong_desc = '、'.join([f"{num_to_cn(d)}爻动" for d in dong])
        fenxi.append(f"【动爻】{dong_desc}")
    else:
        fenxi.append("【动爻】六爻安静，无动爻")

    # --- 4. 用神分析 ---
    if yongshen_type and yongshen_type != '六亲':
        yongshen_yaos = [y for y in yaos_shunxu if y['liuqin'] == yongshen_type]
        if yongshen_yaos:
            fenxi.append(f"【用神】取{yongshen_type}爻为用神")
            for y in yongshen_yaos:
                status = miao_yao_zhuangtai(y, yue, ri_z, dong, paipan)
                pos_name = num_to_cn(y['pos']) + '爻'
                mark = []
                if y['is_shi']: mark.append('持世')
                if y['is_ying']: mark.append('临应')
                if y['is_dong']: mark.append('动爻')
                if y['is_kong']: mark.append('旬空')
                if y['is_po']: mark.append('月破')
                mark_str = '（' + '、'.join(mark) + '）' if mark else ''
                fenxi.append(f"  {pos_name} {y['liushen']} {y['liuqin']}{y['zhi']}{y['wuxing']}{mark_str}：{status}")
        else:
            fenxi.append(f"【用神】卦中不见{yongshen_type}爻，需寻伏神")

    # --- 5. 世爻旺衰 ---
    shi_yao = next((y for y in yaos_shunxu if y['is_shi']), None)
    if shi_yao:
        shi_status = miao_yao_zhuangtai(shi_yao, yue, ri_z, dong, paipan)
        dong_mark = '，动爻' if shi_yao['is_dong'] else '，安静'
        kong_mark = '，旬空' if shi_yao['is_kong'] else ''
        po_mark = '，月破' if shi_yao['is_po'] else ''
        fenxi.append(f"【世爻】{num_to_cn(shi_yao['pos'])}爻 {shi_yao['liushen']} {shi_yao['liuqin']}{shi_yao['zhi']}{shi_yao['wuxing']}{dong_mark}{kong_mark}{po_mark}：{shi_status}")

    # --- 6. 动爻生克关系 ---
    if dong:
        guanxi_lines = []
        dong_yaos_data = [y for y in yaos_shunxu if y['is_dong']]
        for dy in dong_yaos_data:
            # 看动爻对世爻和用神的作用
            dy_wx = dy['wuxing']
            rels = []
            if shi_yao:
                rel = get_wuxing_relation(dy_wx, shi_yao['wuxing'])
                if rel == '生':
                    rels.append(f"动爻{dy['liuqin']}{dy['zhi']}生世爻")
                elif rel == '克':
                    rels.append(f"动爻{dy['liuqin']}{dy['zhi']}克世爻")
                elif rel == '同':
                    rels.append(f"动爻{dy['liuqin']}{dy['zhi']}助世爻")
            # 变爻
            if paipan['bian_gua']:
                b_yaos_shunxu = list(reversed(paipan['bian_gua']['yaos']))
                b_y = next((b for b in b_yaos_shunxu if b['pos'] == dy['pos']), None)
                if b_y:
                    b_rel = get_wuxing_relation(b_y['wuxing'], dy_wx)
                    biao = f"（变{b_y['liuqin']}{b_y['zhi']}）"
                    if b_rel == '生':
                        rels.append(f"化回头生{biao}")
                    elif b_rel == '克':
                        rels.append(f"化回头克{biao}")
                    elif b_rel == '同':
                        # 判断化进神、退神、伏吟
                        jin_tui = hua_jin_tui(dy['zhi'], b_y['zhi'])
                        rels.append(f"{jin_tui}{biao}")
            if rels:
                guanxi_lines.append(f"  {num_to_cn(dy['pos'])}爻动：{'；'.join(rels)}")
        if guanxi_lines:
            fenxi.append("【动爻作用】\n" + '\n'.join(guanxi_lines))

    return fenxi


def miao_yao_zhuangtai(yao, yue_zhi, ri_zhi, dong_list, paipan):
    """描述某爻在月日下的旺衰状态"""
    wx = yao['wuxing']
    tags = []

    # 月建作用
    if yue_zhi:
        yue_wx = DIZHI_WUXING[yue_zhi]
        yue_rel = get_wuxing_relation(yue_wx, wx)
        if yue_rel == '同':
            tags.append('临月建（旺）')
        elif yue_rel == '生':
            tags.append('得月生（相）')
        elif yue_rel == '克':
            tags.append('被月克（休）')
        elif yue_rel == '被生':
            tags.append('生月（休）')
        elif yue_rel == '克':
            pass
        elif yue_rel == '被克':
            tags.append('月克（囚）')

    # 日辰作用
    if ri_zhi:
        ri_wx = DIZHI_WUXING[ri_zhi]
        ri_rel = get_wuxing_relation(ri_wx, wx)
        if ri_rel == '同':
            tags.append('临日建（旺）')
        elif ri_rel == '生':
            tags.append('得日生')
        elif ri_rel == '克':
            tags.append('被日克')
        # 日合、日冲
        if LIUHE.get(ri_zhi) == yao['zhi']:
            tags.append('日合')
        if LIUCHONG.get(ri_zhi) == yao['zhi']:
            tags.append('日冲（暗动/日破）')

    # 月破
    if yao['is_po']:
        tags.append('月破')

    # 旬空
    if yao['is_kong']:
        tags.append('旬空')

    # 动爻
    if yao['is_dong']:
        tags.append('动爻')

    if not tags:
        tags.append('平常')

    return '、'.join(tags)


def hua_jin_tui(dong_zhi, bian_zhi):
    """判断动爻化进神、退神还是伏吟（同五行地支变化）"""
    if dong_zhi == bian_zhi:
        return '化伏吟'
    # 化进神：寅化卯、巳化午、申化酉、亥化子、丑化辰、辰化未、未化戌、戌化丑
    jin = {
        '寅': '卯', '巳': '午', '申': '酉', '亥': '子',
        '丑': '辰', '辰': '未', '未': '戌', '戌': '丑'
    }
    # 化退神：反过来
    tui = {v: k for k, v in jin.items()}
    if jin.get(dong_zhi) == bian_zhi:
        return '化进神'
    if tui.get(dong_zhi) == bian_zhi:
        return '化退神'
    return '化比和'


def num_to_cn(n):
    """数字转中文（1~6）"""
    cn = {1: '初', 2: '二', 3: '三', 4: '四', 5: '五', 6: '上'}
    return cn.get(n, str(n))


# ============================================================
# 七、卦盘文本格式化
# ============================================================

def paipan_to_text(paipan):
    """将卦盘格式化为可读文本"""
    lines = []
    lines.append('=' * 50)
    title = f"  {paipan['name']}"
    if paipan['bian_gua']:
        title += f"  之  {paipan['bian_gua']['name']}"
    lines.append(title)
    lines.append(f"  {paipan['gong']}宫{paipan['gongwei']}（{paipan['gong_wuxing']}）")
    lines.append('=' * 50)

    if paipan['yue_zhi'] or paipan['ri_zhi']:
        rq = []
        if paipan['yue_zhi']:
            rq.append(f"月建 {paipan['yue_zhi']}{DIZHI_WUXING[paipan['yue_zhi']]}")
        if paipan['ri_gan']:
            rq.append(f"日辰 {paipan['ri_gan']}{paipan['ri_zhi']}{DIZHI_WUXING[paipan['ri_zhi']]}")
        if paipan['xunkong']:
            rq.append(f"旬空 {paipan['xunkong'][0]}{paipan['xunkong'][1]}")
        lines.append('  '.join(rq))
        lines.append('-' * 50)

    # 表头
    lines.append(f"{'六神':<6}{'六亲':<6}{'纳甲':<8}{'爻':<6}{'世应':<6}{'动静':<6}{'空破'}")
    lines.append('-' * 50)

    bian_yaos = None
    if paipan['bian_gua']:
        bian_yaos = paipan['bian_gua']['yaos']  # 上到下

    for idx, y in enumerate(paipan['yaos']):
        # 爻符号
        if y['yinyang'] == 1:
            yao_sym = '━━━'
        else:
            yao_sym = '━ ━'
        if y['is_dong']:
            yao_sym += ' ○' if y['yinyang'] == 1 else ' ×'

        # 世应
        sy = ''
        if y['is_shi']:
            sy = '世'
        elif y['is_ying']:
            sy = '应'

        # 动静
        dj = '动' if y['is_dong'] else ' '

        # 空破
        kp = ''
        if y['is_kong']:
            kp += '空'
        if y['is_po']:
            kp += '破'

        nazhi = f"{y['gan']}{y['zhi']}{y['wuxing']}"

        # 变爻纳甲
        bian_str = ''
        if bian_yaos and y['is_dong']:
            by = bian_yaos[idx]
            bian_str = f" → {by['liuqin']}{by['zhi']}{by['wuxing']}"

        pos_name = num_to_cn(y['pos']) + '爻'
        line = f"{y['liushen']:<6}{y['liuqin']:<6}{nazhi:<8}{yao_sym+' '+pos_name:<10}{sy:<6}{dj:<6}{kp}{bian_str}"
        lines.append(line)

    lines.append('=' * 50)
    return '\n'.join(lines)


# ============================================================
# 八、求财专断（《黄金策·商贾》《总断千金赋》）
# ============================================================

# 五行墓库（木墓未、火墓戌、金墓丑、水土墓辰）
_MUKU = {'木': '未', '火': '戌', '金': '丑', '水': '辰', '土': '辰'}
# 五行绝地（木绝申、火绝亥、金绝寅、水/土绝巳）
_JUEDI = {'木': '申', '火': '亥', '金': '寅', '水': '巳', '土': '巳'}
# 五行长生（木生亥、火生寅、金生巳、水/土生申）
_CHANGSHENG = {'木': '亥', '火': '寅', '金': '巳', '水': '申', '土': '申'}


def _yao_by_pos(paipan, pos):
    """按爻位(1~6)取本卦爻数据"""
    return next((y for y in paipan['yaos'] if y['pos'] == pos), None)


def _bian_by_pos(paipan, pos):
    """按爻位取变卦爻数据（无变卦返回None）"""
    if not paipan['bian_gua']:
        return None
    return next((y for y in paipan['bian_gua']['yaos'] if y['pos'] == pos), None)


def yao_wangshuai(yao, paipan):
    """
    综合月建、日辰、动爻，评估一爻旺衰。
    返回 dict: score(分值), level(旺相/有气/平和/休囚/无气),
              yue(月作用), ri(日作用), dong_sheng(被动爻生),
              dong_ke(被动爻克), mu(入墓), jue(逢绝), changsheng(逢长生)
    """
    wx = yao['wuxing']
    yue = paipan['yue_zhi']
    ri = paipan['ri_zhi']
    score = 0.0
    yue_desc = ''
    ri_desc = ''

    # 月建（司一月之权）：同支为值月（临月建），同五行异支为比扶
    if yue:
        if yao['zhi'] == yue:
            score += 3; yue_desc = '临月建（值月）而旺'
        else:
            yue_wx = DIZHI_WUXING[yue]
            rel = get_wuxing_relation(yue_wx, wx)
            if rel == '同':
                score += 1.5; yue_desc = '得月建比扶（同气）'
            elif rel == '生':
                score += 2; yue_desc = '得月建相生（相）'
            elif rel == '克':
                score -= 2; yue_desc = '被月建所克'
            elif rel == '被生':
                score -= 1; yue_desc = '爻生月建而泄'
            elif rel == '被克':
                score -= 1; yue_desc = '爻克月建而囚'

    # 日辰（长久有权）：同支为值日（临日建），同五行异支为比扶
    ri_he = ri_chong = False
    if ri:
        if yao['zhi'] == ri:
            score += 2.5; ri_desc = '临日建（值日）而旺'
        else:
            ri_wx = DIZHI_WUXING[ri]
            rel = get_wuxing_relation(ri_wx, wx)
            if rel == '同':
                score += 1; ri_desc = '得日辰比扶（同气）'
            elif rel == '生':
                score += 1.5; ri_desc = '得日辰相生'
            elif rel == '克':
                score -= 2; ri_desc = '被日辰所克'
            elif rel == '被生':
                score -= 0.5; ri_desc = '爻生日辰而泄'
        ri_he = (LIUHE.get(ri) == yao['zhi'])
        ri_chong = (LIUCHONG.get(ri) == yao['zhi'])
        if ri_he:
            score += 0.5
        if ri_chong:
            if yao['is_dong']:
                ri_desc = (ri_desc + '、逢日冲则散').strip('、')
            elif yao['is_kong']:
                ri_desc = (ri_desc + '、空逢日冲为冲实').strip('、')
                score += 1
            else:
                score += 1
                ri_desc = (ri_desc + '、静逢日冲为暗动').strip('、')

    # 动爻生克（本卦其他动爻）
    dong_sheng, dong_ke, dong_bi = [], [], []
    for other in paipan['yaos']:
        if not other['is_dong'] or other['pos'] == yao['pos']:
            continue
        rel = get_wuxing_relation(other['wuxing'], wx)
        label = f"{num_to_cn(other['pos'])}爻{other['liuqin']}{other['zhi']}"
        if rel == '生':
            dong_sheng.append(label); score += 1.5
        elif rel == '克':
            dong_ke.append(label); score -= 2
        elif rel == '同':
            dong_bi.append(label); score += 0.5

    # 墓、绝、长生（看日辰、动爻、变爻）
    mu = jue = cs = ''
    mu_zhi = _MUKU[wx]
    jue_zhi = _JUEDI[wx]
    cs_zhi = _CHANGSHENG[wx]
    cand = [('日辰', ri)]
    for other in paipan['yaos']:
        if other['is_dong'] and other['pos'] != yao['pos']:
            cand.append((f"{num_to_cn(other['pos'])}爻动", other['zhi']))
    by = _bian_by_pos(paipan, yao['pos'])
    if yao['is_dong'] and by:
        cand.append(('化出', by['zhi']))
    # 旺相之爻不入日辰、动爻之墓绝（旺不为墓、不绝）；唯动而化墓、化绝，虽旺亦论
    wang_xiang = score >= 2 and not yao['is_po'] and not yao['is_kong']
    for src, zhi in cand:
        if not zhi:
            continue
        if zhi == mu_zhi and not mu:
            if src == '化出' or not wang_xiang:
                mu = src
        if zhi == jue_zhi and not jue:
            if src == '化出' or not wang_xiang:
                jue = src
        if zhi == cs_zhi and not cs:
            cs = src
    if mu:
        score -= 1
    if jue:
        score -= 1.5
    if cs:
        score += 1

    # 旬空、月破
    if yao['is_po']:
        score -= 2
    if yao['is_kong']:
        score -= 1.5

    # 等级
    if score >= 4:
        level = '旺相'
    elif score >= 2:
        level = '有气'
    elif score >= 0:
        level = '平和'
    elif score >= -2:
        level = '休囚'
    else:
        level = '无气'

    return {
        'score': score, 'level': level, 'yue': yue_desc, 'ri': ri_desc,
        'ri_he': ri_he, 'ri_chong': ri_chong,
        'dong_sheng': dong_sheng, 'dong_ke': dong_ke, 'dong_bi': dong_bi,
        'mu': mu, 'jue': jue, 'changsheng': cs,
    }


def find_fushen(paipan, yongshen_type):
    """
    用神不上卦时，从本宫首卦（八纯卦）寻伏神。
    返回 dict(pos, zhi, wuxing, liuqin, feishen) 或 None。
    """
    gong = paipan['gong']
    gong_wx = BAGUA[gong]['wuxing']
    nazhi = BAGUA[gong]['nazhi_nei'] + BAGUA[gong]['nazhi_wai']
    for idx, zhi in enumerate(nazhi):
        lq = get_liuqin(gong_wx, DIZHI_WUXING[zhi])
        if lq == yongshen_type:
            pos = idx + 1
            fei = _yao_by_pos(paipan, pos)
            return {'pos': pos, 'zhi': zhi, 'wuxing': DIZHI_WUXING[zhi],
                    'liuqin': lq, 'feishen': fei}
    return None


def sanhe_ju(paipan):
    """
    检查卦中动爻（可与日辰、月建组合）是否会成三合局。
    返回 [(局五行, 组成地支列表, 来源)] ，经典以两爻动+日/月，或三爻动成局。
    """
    ju_list = []
    dong_zhi = {y['zhi']: f"{num_to_cn(y['pos'])}爻动" for y in paipan['yaos'] if y['is_dong']}
    ri = paipan['ri_zhi']
    yue = paipan['yue_zhi']
    for trio, wx in SANHE:
        have = []
        sources = []
        for z in trio:
            if z in dong_zhi:
                have.append(z); sources.append(dong_zhi[z])
        # 缺一字时看日辰、月建能否补
        missing = [z for z in trio if z not in dong_zhi]
        fill = ''
        if len(have) == 3:
            fill = '三爻动会局'
        elif len(have) == 2 and (ri in missing or yue in missing):
            fillz = ri if ri in missing else yue
            have.append(fillz)
            sources.append('日辰' if fillz == ri else '月建')
            fill = '两爻动得日/月补局'
        if len(have) == 3:
            ju_list.append({'wuxing': wx, 'zhi': trio, 'src': sources, 'kind': fill})
    return ju_list


def _qincai_shiji(cais, shi):
    """
    判断财爻与世爻（求财之人）的向背关系。
    返回 (关系代码, 说明)。
    财持世/生世/克世/合世 = 财来就我；世生财/克财 = 我去寻财。
    """
    if not cais:
        return None, ''
    shi_wx = shi['wuxing']
    # 取最有力的财爻（优先持世、动爻、旺相）
    rels = []
    for c in cais:
        cwx = c['wuxing']
        chonghe = ''
        if LIUHE.get(c['zhi']) == shi['zhi']:
            chonghe = '六合'
        elif LIUCHONG.get(c['zhi']) == shi['zhi']:
            chonghe = '相冲'
        if c['is_shi']:
            rels.append(('持世', c, '财爻持世'))
        else:
            r = get_wuxing_relation(cwx, shi_wx)
            if r == '生':
                rels.append(('生世', c, f"财爻{c['zhi']}生世爻" + (f'、与世{chonghe}' if chonghe == '六合' else '')))
            elif r == '克':
                rels.append(('克世', c, f"财爻{c['zhi']}克世爻（物来寻我，财来就我）" + (f'、与世{chonghe}' if chonghe else '')))
            elif r == '同':
                rels.append(('比世', c, f"财爻{c['zhi']}与世比和"))
            else:
                # 世生财 或 世克财
                r2 = get_wuxing_relation(shi_wx, cwx)
                if r2 == '生':
                    rels.append(('世生财', c, f"世爻生财爻{c['zhi']}（我去生财，须费力）"))
                elif r2 == '克':
                    rels.append(('世克财', c, f"世爻克财爻{c['zhi']}（我去寻财，求之难）"))
                else:
                    rels.append(('无关', c, f"财爻{c['zhi']}与世爻无直接生克"))
    # 优先级：持世 > 生世 > 克世 > 比世 > 世生财 > 世克财 > 无关；动爻优先
    order = {'持世': 0, '生世': 1, '克世': 2, '比世': 3, '世生财': 4, '世克财': 5, '无关': 6}
    rels.sort(key=lambda t: (order[t[0]], 0 if t[1]['is_dong'] else 1))
    return rels[0][0], rels[0][2]


# 求财视角：动爻六亲化出六亲的意象断语（回头生克、进退神另断；此表补六亲意象）
HUA_QIN_CAI = {
    ('子孙', '妻财'): '福神化财，利源不竭，大吉',
    ('妻财', '子孙'): '财化福德，财源有继，绵绵得利',
    ('官鬼', '妻财'): '官鬼化财，若生合世身最利公门谒贵、九流求财，克世则否',
    ('兄弟', '妻财'): '兄弟化财，先散后聚、先难后得，利在最后',
    ('父母', '妻财'): '父母化财，辛勤劳苦而后有得',
    ('妻财', '官鬼'): '财化官鬼，因财生忧、耗折惊惶，世伤恐因财致祸，凶',
    ('妻财', '兄弟'): '财化兄弟，得而复失，被人分夺劫耗，凶',
    ('妻财', '父母'): '财化父母，主因文书、宅舍、长辈或劳碌而耗财，且克财源',
    ('子孙', '官鬼'): '福神化鬼，乐极生忧、财源化祸，求财不利',
    ('子孙', '父母'): '子孙化父母，财源被克伤、福神受损，利源断绝',
    ('子孙', '兄弟'): '子孙化兄弟，兄弟生子孙，财源得助；然兄弟终为分财之神，吉凶相半',
    ('兄弟', '官鬼'): '兄弟化官鬼，劫财之神受制，不能夺财，反吉',
    ('兄弟', '子孙'): '兄弟化子孙，兄生子、子生财，连环生益，先阻后得',
    ('兄弟', '父母'): '兄弟化父母，父母生兄弟，劫财更盛，凶',
    ('官鬼', '子孙'): '官鬼化子孙，忧解福生、阻滞消散，求财反吉',
    ('官鬼', '兄弟'): '官鬼化兄弟，阻扰未除又逢分财争夺，凶',
    ('官鬼', '父母'): '官鬼化父母，父母生官，阻隔劳扰益甚',
    ('父母', '官鬼'): '父母化官鬼，劳碌中生忧惊阻隔，求财费力',
    ('父母', '兄弟'): '父母化兄弟，生助劫财之神，不利求财',
    ('父母', '子孙'): '父母化子孙，仇神化福，财源由阻而通，先劳后利',
}


def _liuqin_wuxing(gong_wx, qin):
    """由卦宫五行推某六亲对应的五行"""
    if qin == '兄弟':
        return gong_wx
    if qin == '妻财':
        return WUXING_KE[gong_wx]
    if qin == '子孙':
        return WUXING_SHENG[gong_wx]
    if qin == '官鬼':
        for x in WUXING_KE:
            if WUXING_KE[x] == gong_wx:
                return x
    if qin == '父母':
        for x in WUXING_SHENG:
            if WUXING_SHENG[x] == gong_wx:
                return x
    return None


def _yao_brief(y, paipan):
    """一爻的简明描述：X爻 六神 六亲地支五行 + 动静空破 + 旺衰"""
    st = yao_wangshuai(y, paipan)
    marks = []
    if y['is_shi']:
        marks.append('持世')
    if y['is_ying']:
        marks.append('临应')
    if y['is_dong']:
        marks.append('发动')
    if y['is_kong']:
        marks.append('旬空')
    if y['is_po']:
        marks.append('月破')
    if st['mu']:
        marks.append(f"入墓({st['mu']})")
    if st['jue']:
        marks.append(f"逢绝({st['jue']})")
    mk = '（' + '、'.join(marks) + '）' if marks else ''
    return f"{num_to_cn(y['pos'])}爻{y['liushen']}{y['liuqin']}{y['zhi']}{y['wuxing']}{mk}【{st['level']}】", st


def fenxi_caiyun(paipan):
    """
    《黄金策·商贾》求财专断。
    输出三段：一、黄金策经典论断；二、本卦财福逐条详断；三、综合断语与应期。
    返回行列表（以【开头者为小节标题）。
    """
    L = []
    yx = list(reversed(paipan['yaos']))          # 初爻→上爻
    yue, ri = paipan['yue_zhi'], paipan['ri_zhi']
    gong_wx = paipan['gong_wuxing']
    dong = paipan['dong_yao']
    shi = next(y for y in yx if y['is_shi'])
    ying = next((y for y in yx if y['is_ying']), None)

    cais = [y for y in yx if y['liuqin'] == '妻财']
    zis = [y for y in yx if y['liuqin'] == '子孙']
    xiongs = [y for y in yx if y['liuqin'] == '兄弟']
    guans = [y for y in yx if y['liuqin'] == '官鬼']
    fus = [y for y in yx if y['liuqin'] == '父母']

    cai_wx = cais[0]['wuxing'] if cais else _liuqin_wuxing(gong_wx, '妻财')
    zi_wx = zis[0]['wuxing'] if zis else _liuqin_wuxing(gong_wx, '子孙')

    # 各爻旺衰
    def st_of(y):
        return yao_wangshuai(y, paipan)
    cai_sts = [(y, st_of(y)) for y in cais]
    zi_sts = [(y, st_of(y)) for y in zis]
    xiong_sts = [(y, st_of(y)) for y in xiongs]
    guan_sts = [(y, st_of(y)) for y in guans]
    fu_sts = [(y, st_of(y)) for y in fus]
    shi_st = st_of(shi)

    # 兄弟（劫财）是否被有效制伏：日辰克之，或动官鬼克之（官鬼须有气、不空不破）
    def xiong_bei_zhi(xy):
        if ri and get_wuxing_relation(DIZHI_WUXING[ri], xy['wuxing']) == '克':
            return True
        for g in guans:
            if (g['is_dong'] and not g['is_kong'] and not g['is_po']
                    and st_of(g)['level'] in ('旺相', '有气', '平和')
                    and get_wuxing_relation(g['wuxing'], xy['wuxing']) == '克'):
                return True
        return False

    # 伏神（卦无财时）
    fushen = None
    if not cais:
        fushen = find_fushen(paipan, '妻财')

    # ===== 卦头 =====
    head = f"【卦象】{paipan['name']}（{paipan['gong']}宫{paipan['gongwei']}，{gong_wx}）"
    if paipan['bian_gua']:
        head += f" 之 {paipan['bian_gua']['name']}"
    L.append(head)
    L.append(f"【日月】月建{yue}{DIZHI_WUXING[yue]}　日辰{paipan['ri_gan']}{ri}{DIZHI_WUXING[ri]}　"
             f"旬空{paipan['xunkong'][0]}{paipan['xunkong'][1]}")
    L.append(f"【动爻】" + ('、'.join(f"{num_to_cn(d)}爻动" for d in dong) if dong else '六爻安静，无动爻'))

    # ============================================================
    # 一、《黄金策》经典论断
    # ============================================================
    L.append("【一、《黄金策·商贾》论求财（经典）】")
    L.append("· 总纲：「居货曰贾，行货曰商，总为资生之计……要问吉凶，但看财福——财为本，福为利，二者不可损坏。」"
             "卦中子孙之爻称曰福神，乃财之根源。")
    L.append("· 六亲取用：妻财为禄神（所求之财）；子孙为福德、为财源（子孙生财）；兄弟为劫财之神（克财）；"
             "父母为仇神（克子孙、生兄弟，坏财源）；官鬼能制兄弟以护财，然发动又主阻隔耗财、忧惊。")

    # 商贾章核心经文（固定先明通例）
    _CAI_JING = [
        ("居货曰贾，行货曰商，总为资生之计，要问吉凶，但看财福，财为本、福为利，二者不可损坏",
         "商贾求财，只看妻财（财）与子孙（福）两爻；财是本钱、福是利润，二者皆不宜被伤克；子孙是财之根源。"),
        ("财旺福兴，无问公私皆称意；财空福绝，不拘营运总违心",
         "财爻旺、子孙兴，无论公干私商皆称心；财空、福绝，做什么买卖都违心。"),
        ("有福无财，兄弟交重偏有望",
         "有子孙财源而财暂不现，兄弟发动去生子孙，财源愈厚，连环相生（兄生子、子生财），反有得财之望。"),
        ("有财无福，官爻发动亦堪求",
         "财现而子孙不现，财无生气，一遇兄弟便被劫夺；须得官鬼发动（或日辰为官）克制兄弟、护住财，亦可求谋。"),
        ("财福俱无，何异守株而待兔",
         "卦中财爻、子孙皆不现，财源两失，妄求无益，如守株待兔；若有拱扶伏神，待值日亦有得。"),
        ("父兄皆动，无殊缘木以求鱼",
         "父母克子孙、生兄弟，父兄俱动，财源被坏、劫夺又兴，求之不得，如缘木求鱼。"),
        ("身遇旺财，似取囊中之物",
         "世为求财之人，世临旺财，求财如取囊中之物，虽无气亦主易得，旺相尤美。"),
        ("世持动弟，如捞水底之针",
         "兄弟持世发动，如同水底捞针，不拘何买卖皆主破财难遂；安静尚难，发动尤甚。"),
        ("财来就我终须易，我去寻财必是难",
         "财爻生合世、持世、克世，皆为财来就我，求之易得；财与世不相干，乃我去寻财，必难。"),
        ("福变财生，滚滚利源不竭",
         "子孙发动又化财、财又生合世身，利源滚滚，绵绵不绝；财化子孙亦同。"),
        ("财化鬼兄，防耗折而惊忧",
         "财爻化官鬼、化兄弟最凶，主损财、驳耗、忧惊；世爻若再受伤，恐因财致祸。"),
        ("财局会福神，万倍利源可许",
         "三合会成财局、福局，动来生合世身，更得财旺，可许厚利。"),
        ("多财反复，必须墓库以收藏",
         "财爻叠现太过，其财反复难求；须得财之库爻持世临身，谓之财有收藏，方得厚利。"),
        ("无鬼分争，又怕交重而阻滞",
         "无官鬼克制兄弟，则兄弟专权分争、劫财；兄弟交重发动，又主阻滞、耗散。"),
        ("应空难靠他人，世空有财难得",
         "应爻为交易、合伙之人，应空则彼方不实、虚约难凭；世爻空，自己谋为不实、心退悔，纵有财亦难入手。"),
        ("月带财神，卦中无而月中必有",
         "月建为提纲而带财爻，虽正卦无财，伏财亦明，月内可求。"),
        ("鬼克身爻，商贩者必遭盗贼",
         "官鬼临玄武发动来克世，商贩远行须防盗贼之祸。"),
        ("路上有官休出外，宅中有鬼莫居家",
         "官鬼动而克世，路上有官则不可出外，宅中有鬼则不可居家，出行经商宜避。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _CAI_JING:
        L.append("　· 「%s」——%s" % (_j, _s))

    # 动态贴合的经典条文（本卦特别贴合）
    L.append("· 本卦特别贴合之经文：")
    cai_wang = any(s['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po'] for y, s in cai_sts)
    cai_kong_po = any(y['is_kong'] or y['is_po'] for y in cais)
    zi_dong_wang = any(y['is_dong'] and s['level'] in ('旺相', '有气', '平和') for y, s in zi_sts)
    zi_shang = any(s['dong_ke'] or s['yue'].startswith('被月') or s['ri'].startswith('被日')
                   for y, s in zi_sts) or any(f['is_dong'] for f, s in fu_sts)
    xiong_dong = any(y['is_dong'] for y in xiongs)
    xiong_wu_zhi = any(y['is_dong'] and s['level'] in ('旺相', '有气')
                       and not xiong_bei_zhi(y) and not any(z['is_dong'] for z in zis)
                       for y, s in xiong_sts)
    fu_dong = any(y['is_dong'] for y in fus)
    fu_xiong_dong = fu_dong and xiong_dong
    guan_dong = any(y['is_dong'] for y in guans)
    shi_xiong = shi['liuqin'] == '兄弟'
    cai_duo = len(cais) >= 3

    # 财与世向背
    xiangbei, xiangbei_desc = _qincai_shiji(cais, shi) if cais else (None, '')

    # 动变归类（变爻六亲按本卦宫论）
    bian_info = []   # (动爻, 变爻, 变六亲, 回头关系)
    for y in yx:
        if not y['is_dong']:
            continue
        by = _bian_by_pos(paipan, y['pos'])
        if not by:
            continue
        b_qin = get_liuqin(gong_wx, by['wuxing'])
        rel = get_wuxing_relation(by['wuxing'], y['wuxing'])
        hui = '回头生' if rel == '生' else ('回头克' if rel == '克' else '')
        jt = hua_jin_tui(y['zhi'], by['zhi']) if rel == '同' else ''
        bian_info.append((y, by, b_qin, hui, jt))

    # 三合局
    ju = sanhe_ju(paipan)
    cai_ju = [j for j in ju if j['wuxing'] == cai_wx]
    fu_ju = [j for j in ju if j['wuxing'] == zi_wx]
    # 财源（子孙）化官鬼、化父母，或化回头克 = 福神受伤化祸
    zi_hua_xiong = any(y['liuqin'] == '子孙' and bq in ('官鬼', '父母')
                       for y, b, bq, h, jt in bian_info)
    zi_huike = any(y['liuqin'] == '子孙' and h == '回头克'
                   for y, b, bq, h, jt in bian_info)

    # 逐条经典（命中即列）
    if cai_wang and zi_dong_wang:
        L.append("· 「财旺福兴，无问公私皆称意；财空福绝，不拘营运总违心」——财爻旺相、子孙发动，"
                 "公私之谋皆称意；财被伤克、临墓绝无救，则买卖违心。")
    elif not cais and not zis:
        L.append("· 「财福俱无，何异守株而待兔」——卦中财爻、子孙俱不现，财源两失，妄求无益；"
                 "若拱扶所伏之神，待值日亦有得。")
    if xiangbei in ('持世', '生世', '克世') and cai_wang:
        L.append("· 「财来就我终须易，我去寻财必是难」——财爻生合世爻、持世克世，皆为财来就我，求之易得；"
                 "财与世不相干，乃我去寻财，必难。")
    if xiangbei == '持世' and shi['liuqin'] == '妻财':
        L.append("· 「身遇旺财，似取囊中之物」——世为求财之人，世临财爻，虽无气亦主易得，旺相尤美。")
    if shi_xiong:
        L.append("· 「身或兄临，必难求望」「世持动弟，如捞水底之针」——兄弟持世临身，不拘何买卖皆主破财难遂，"
                 "安静尚难，发动尤甚。")
    # 福变财生
    fubian = any(y['liuqin'] == '子孙' and bq == '妻财' for y, b, bq, h, jt in bian_info)
    cai_bian_zi = any(y['liuqin'] == '妻财' and bq == '子孙' for y, b, bq, h, jt in bian_info)
    if fubian or cai_bian_zi or (zi_dong_wang and not zi_hua_xiong and cai_wang):
        L.append("· 「福变财生，滚滚利源不竭」——子孙发动，利必久远；更兼财爻生合世身，乃绵绵不绝之象，"
                 "财化子孙亦同。")
    if zi_hua_xiong or zi_huike:
        L.append("· 子孙为财之根源、解忧之福神，若发动而化官鬼、化父母或回头克，是福神受伤、财源化祸，"
                 "不唯利薄，且恐因财生忧，《千金赋》所谓「子虽福德，多反无功」。")
    # 财化鬼兄
    cai_hua_xiong = any(y['liuqin'] == '妻财' and bq in ('官鬼', '兄弟') for y, b, bq, h, jt in bian_info)
    if cai_hua_xiong:
        L.append("· 「财化鬼兄，防耗折而惊忧」——财爻化官鬼、化兄弟最凶，主损财驳耗；世爻若再受伤，恐因财致祸。")
    # 兄弟
    if xiong_dong and zi_dong_wang:
        L.append("· 「有福无财，兄弟交重偏有望」——子孙发动无伤，财源本厚，兄弟发动反生扶子孙，"
                 "连环相生（兄生子、子生财），其财根深蒂固。")
    elif xiong_wu_zhi:
        L.append("· 兄弟乃占财之忌神，发动则克财劫夺、分财散物；「无鬼分争，又怕交重而阻滞」，"
                 "无官鬼制之，则兄弟专权，财虽有气亦多虚耗。")
    if fu_xiong_dong:
        L.append("· 「父兄皆动，无殊缘木以求鱼」——父母克子孙、生兄弟，父兄俱动，财源被坏、劫夺又兴，"
                 "必不能得。")
    elif fu_dong and zis:
        L.append("· 父母为仇神，发动则克伤子孙（财源），福神受伤，利源不畅。")
    if (not zis or all(y['is_kong'] for y in zis)) and guan_dong and cais:
        L.append("· 「有财无福，官爻发动亦堪求」——子孙藏伏，财无生气，一遇兄弟便被劫夺；"
                 "须得官爻发动、或日辰为官克制兄弟，亦可求谋（然有子孙而官鬼动，又主阻滞）。")
    if cai_ju or fu_ju:
        L.append("· 「财局会福神，万倍利源可许」——三合会成财局、福局动来生合世身，财利绵绵，"
                 "更得财旺，可许厚利。")
    if cai_duo:
        L.append("· 「多财反复，必须墓库以收藏」——卦中财爻叠现太过，其财反复难求；"
                 "须得财之库爻持世临身，谓之财有收藏，方得厚利。")
    if shi['is_kong']:
        L.append("· 「世空有财难得」「心退悔兮世空」——世爻旬空，自己心虚怠惰、谋为不实，纵有财亦难入手。")
    if ying and ying['is_kong']:
        L.append("· 「应空难靠他人」——应爻为交易之人、合伙之伴，应空则彼方不实，虚约难凭。")
    if guan_dong and not cai_ju:
        L.append("· 占财皆忌官鬼发动，主阻隔、耗财、忧惊；唯求公门之财、九流艺术之财，反宜官鬼旺相生合世身。")
    # 玄武官动克世防盗
    xuanwu_guan_ke_shi = any(y['is_dong'] and y['liushen'] == '玄武' and y['liuqin'] == '官鬼'
                             and get_wuxing_relation(y['wuxing'], shi['wuxing']) == '克' for y in yx)
    if xuanwu_guan_ke_shi:
        L.append("· 「鬼克身爻，商贩者必遭盗贼」——官鬼临玄武发动来克世，须防盗贼之祸。")
    # 月带财神
    if not cais and yue and DIZHI_WUXING[yue] == cai_wx:
        L.append("· 「月带财神，卦中无而月中必有」——月建为提纲而带财爻，虽正卦无财，伏财亦明，月内可求。")

    # ============================================================
    # 二、本卦财福逐条详断
    # ============================================================
    L.append("【二、本卦财福逐条详断】")

    # 1. 用神妻财
    L.append("（1）用神·妻财爻（所求之财）")
    if cais:
        for y, s in cai_sts:
            brief, _ = _yao_brief(y, paipan)
            detail = [f"月建：{s['yue'] or '无涉'}", f"日辰：{s['ri'] or '无涉'}"]
            if s['dong_sheng']:
                detail.append('受动爻生：' + '、'.join(s['dong_sheng']))
            if s['dong_ke']:
                detail.append('受动爻克：' + '、'.join(s['dong_ke']))
            if s['mu']:
                detail.append(f"入墓于{s['mu']}，主阻滞，待冲墓冲财之日方得")
            if s['jue']:
                detail.append(f"逢绝于{s['jue']}，须逢生旺")
            if y['is_kong']:
                if s['score'] >= 2:
                    detail.append('旺相而空为「真空/假空」之辨——旺空待出旬值日即得')
                else:
                    detail.append('衰弱又空，为真空，求财难就')
            if y['is_po']:
                detail.append('月破之财，须出月填实、逢合之日方有')
            L.append("　· " + brief + "：" + '；'.join(detail) + '。')
    else:
        L.append("　· 卦中不见妻财爻，用神不上卦。")
        if fushen:
            fs = fushen
            fei = fs['feishen']
            # 伏神旺衰（以月日粗断）
            fs_wx = fs['wuxing']
            yue_rel = get_wuxing_relation(DIZHI_WUXING[yue], fs_wx) if yue else '无'
            ri_rel = get_wuxing_relation(DIZHI_WUXING[ri], fs_wx) if ri else '无'
            tian = []
            if yue_rel in ('同', '生'):
                tian.append('得月建生扶')
            if ri_rel in ('同', '生'):
                tian.append('得日辰生扶')
            if fs['zhi'] in paipan['xunkong']:
                tian.append('伏神又逢旬空')
            # 飞伏生克五关系（rel 为飞神对伏神）
            fei_rel = get_wuxing_relation(fei['wuxing'], fs_wx)
            fei_map = {
                '生': '飞神生伏神，伏得生扶而易出，为吉',
                '克': '飞神克伏神（伤身），伏神被压难出，求财尤难',
                '被生': '伏神生飞神，伏神泄气于飞，亦难出现',
                '被克': '伏神克飞神，为「出暴」，伏神易出而事机急暴、乍起乍落',
                '同': '飞伏比和相助，伏神易出',
            }
            fei_text = fei_map.get(fei_rel, '飞伏无克，待时可出')
            L.append(f"　· 于本宫{paipan['gong']}卦寻得伏神：{num_to_cn(fs['pos'])}爻妻财{fs['zhi']}{fs_wx}，"
                     f"伏于{num_to_cn(fei['pos'])}爻飞神「{fei['liuqin']}{fei['zhi']}{fei['wuxing']}」之下。")
            L.append("　· 伏神须待日辰、动爻生扶拱合，或冲开飞神、伏神值日出现方可得财；"
                     + ('、'.join(tian) if tian else '伏神目前不得日月生扶') + '；' + fei_text + '。')
        else:
            L.append("　· 本宫亦寻伏财不得，财毫无根，求财大不利（可参看月建、日辰是否带财）。")

    # 2. 财与世爻向背
    L.append("（2）财与求财之人（世爻）向背")
    shi_brief, _ = _yao_brief(shi, paipan)
    L.append("　· 世爻（我）：" + shi_brief)
    if cais:
        beishu = {'持世': '财来就我', '生世': '财来就我', '克世': '财来就我',
                  '比世': '财我比和', '世生财': '我去寻财', '世克财': '我去寻财', '无关': '财我无关'}
        L.append(f"　· 向背：{xiangbei_desc}——{beishu.get(xiangbei, '')}。")
        if xiangbei in ('持世', '生世', '克世'):
            L.append("　· 财来就我，如物来寻我，不劳多求而自得；唯须财爻有气、不空不破方准。")
        elif xiangbei in ('世生财', '世克财', '无关'):
            L.append("　· 我去寻财，须我身旺、财源得力，劳心劳力方有所得；世若休囚空破，难矣。")
    if ying:
        yb, ys = _yao_brief(ying, paipan)
        L.append("　· 应爻（交易/合伙之人）：" + yb + ("；应空则对方不实、合约难凭。" if ying['is_kong'] else '。'))

    # 3. 财源福神（子孙）
    L.append("（3）福神·子孙爻（财源）")
    if zis:
        for y, s in zi_sts:
            brief, _ = _yao_brief(y, paipan)
            notes = []
            if y['is_dong']:
                # 子孙动而生财；是否被合住
                if s['ri_he']:
                    notes.append('子孙发动而被日辰合住，「动值合而绊住」，暂不能生财，待冲开之日方有财')
                elif any(LIUHE.get(o['zhi']) == y['zhi'] and o['is_dong'] for o in yx):
                    notes.append('子孙动被他爻合绊，待冲日方生财')
                else:
                    notes.append('子孙发动，财源流动，能生妻财，为求财之吉象')
            else:
                if s['ri_chong']:
                    notes.append('子孙安静而逢日辰冲，为暗动，暗动亦能生财')
                else:
                    notes.append('子孙安静，财源未动，待日月冲起（暗动）或发动，方能生财')
            if s['dong_ke']:
                notes.append('被' + '、'.join(s['dong_ke']) + '克伤，财源受损')
            if any(f['is_dong'] for f in fus):
                notes.append('卦中父母发动克子孙，财源受制（仇神动）')
            if y['is_kong']:
                notes.append('子孙旬空，财源落空，出旬方有生气')
            if s['level'] in ('休囚', '无气'):
                notes.append('子孙休囚无气，财源浅薄，得日月动爻生扶则有源')
            L.append("　· " + brief + "：" + '；'.join(notes) + '。')
    else:
        L.append("　· 卦中子孙不现，财源隐伏。有财则财无生气，一遇兄弟便被劫夺；"
                 "须官鬼发动或日辰为官制兄，方可求。宜兼查伏神。")

    # 4. 劫财忌神（兄弟）
    L.append("（4）忌神·兄弟爻（劫财）")
    if xiongs:
        for y, s in xiong_sts:
            brief, _ = _yao_brief(y, paipan)
            notes = []
            if y['is_dong']:
                if any(z['is_dong'] for z in zis):
                    notes.append('兄弟虽动，喜子孙亦动，兄生子、子生财，反主财源根深（须防中分财之嫌）')
                elif xiong_bei_zhi(y):
                    notes.append('兄弟发动本欲劫财，喜有气官鬼动克、或日辰克之，忌神有制，劫财无力')
                else:
                    qd = '旺动无制' if s['level'] in ('旺相', '有气') else '发动而无制'
                    notes.append(f'兄弟{qd}（官鬼空破无力则同无制），必主劫夺分财、成本耗散，求财大忌')
            else:
                notes.append('兄弟安静，暂不劫财；逢冲逢值之日须防破财')
            if y['is_shi']:
                notes.append('兄弟持世，自身为劫财之象，求财难遂')
            L.append("　· " + brief + "：" + '；'.join(notes) + '。')
    else:
        L.append("　· 卦无兄弟，劫财之神不现，无人分夺，财可入手（唯兄伏待时亦防）。")

    # 5. 官鬼、父母
    L.append("（5）官鬼（制兄·阻隔）与父母（克财源）")
    if guans:
        for y, s in guan_sts:
            brief, _ = _yao_brief(y, paipan)
            note = '官鬼发动' if y['is_dong'] else '官鬼安静'
            if y['is_dong']:
                wuli = '（唯官鬼空破，制兄无力）' if (y['is_kong'] or y['is_po']) else ''
                if xiongs and any(x['is_dong'] for x in xiongs):
                    note += f'，可制伏兄弟以护财{wuli}；然官动亦主阻隔、耗财、忧惊，吉凶相半'
                else:
                    note += '，无兄弟可制，反主求财阻隔、关节耗财、意外惊忧'
                if get_wuxing_relation(y['wuxing'], shi['wuxing']) == '生':
                    note += '；官生世，公门、九流艺术之财反吉'
                if get_wuxing_relation(y['wuxing'], shi['wuxing']) == '克':
                    note += '；官克世，助鬼伤身，因财致患'
            else:
                note += '，静而有气则暗制兄弟，不为害'
            L.append("　· " + brief + "：" + note + '。')
    else:
        L.append("　· 卦无官鬼，兄弟易当权专夺，财多虚耗；然寻常小本经营无官亦不忌。")
    if fus:
        fd = [y for y in fus if y['is_dong']]
        if fd:
            L.append("　· 父母发动：" + '、'.join(f"{num_to_cn(y['pos'])}爻{y['zhi']}" for y in fd)
                     + "，克子孙、生兄弟，坏财源而助劫夺，主劳碌伤本。")
    else:
        L.append("　· 父母不现，财源不受伤，吉。")

    # 6. 动变吉凶
    L.append("（6）动爻变化吉凶")
    if bian_info:
        for y, by, bq, hui, jt in bian_info:
            seg = f"　· {num_to_cn(y['pos'])}爻{y['liuqin']}{y['zhi']}动，变{bq}{by['zhi']}"
            tags = []
            # 回头生克：按六亲角色定求财吉凶（财、子宜生扶；兄、官、父宜受制）
            if hui:
                sheng = hui == '回头生'
                role_txt = {
                    '妻财': ('财得生益，吉', '财被回头克，求财大忌，凶'),
                    '子孙': ('财源得益，吉', '财源被回头克伤，凶'),
                    '兄弟': ('劫财之神得生，夺财更力，凶', '劫财之神被克，不能夺财，反吉'),
                    '官鬼': ('官鬼得势，阻隔耗财更甚（唯公门、九流之财喜官旺）', '官鬼被克，阻隔消散，反吉'),
                    '父母': ('仇神得势，克财源、生兄弟，凶', '仇神被克，财源得护，反吉'),
                }
                tags.append(hui + '，' + role_txt.get(y['liuqin'], ('', ''))[0 if sheng else 1])
            # 进神、退神：按六亲角色定倾向
            if jt and jt != '化比和':
                jin = jt == '化进神'
                jt_txt = {
                    '妻财': ('财势增进，吉', '财势衰退'),
                    '子孙': ('财源益旺，吉', '财源渐退'),
                    '兄弟': ('劫财之势益盛，凶', '劫财渐退，吉'),
                    '官鬼': ('阻隔耗财益甚，凶', '阻隔渐消，吉'),
                    '父母': ('仇神益旺、克财源，凶', '仇神渐退，吉'),
                }
                tags.append(jt + '，' + jt_txt.get(y['liuqin'], ('', ''))[0 if jin else 1])
            # 六亲化出意象（回头生克、进退神已断则不重列；不同六亲查求财意象表）
            if not hui and y['liuqin'] != bq:
                tags.append(HUA_QIN_CAI.get((y['liuqin'], bq), '化' + bq))
            if not tags:
                tags.append(('化比和，平顺' if jt == '化比和' else '化' + bq))
            L.append(seg + '：' + '；'.join(tags) + '。')
    else:
        L.append("　· 卦无动爻（或动而不化），六爻安静，当以本卦财福旺衰、世应生合静断。")

    # 7. 格局
    L.append("（7）卦象格局")
    if cai_ju:
        j = cai_ju[0]
        sheng_shi = get_wuxing_relation(j['wuxing'], shi['wuxing']) in ('生', '同')
        L.append("　· 卦会三合财局（" + ''.join(j['zhi']) + f"成{j['wuxing']}局，{j['kind']}）"
                 + ('，动来生世，财利绵绵，可许厚利。' if sheng_shi else '，然不生世，利未归己，待生合日月。'))
    if fu_ju:
        j = fu_ju[0]
        L.append("　· 卦会三合福/子孙局（" + ''.join(j['zhi']) + f"成{j['wuxing']}局），财源大成，生合世身者利源万倍。")
    liuhe_gua = ['天地否', '地天泰', '水泽节', '山水蒙', '风雷益', '雷地豫', '地山谦', '泽水困']
    liuchong_gua = ['乾为天', '兑为泽', '离为火', '震为雷', '巽为风', '坎为水', '艮为山', '坤为地',
                    '天雷无妄', '雷天大壮']
    if paipan['name'] in liuhe_gua:
        L.append("　· 本卦为六合卦，主谋为和顺、交易易成、财可久守。")
    if paipan['name'] in liuchong_gua:
        L.append("　· 本卦为六冲卦，主买卖反复、不久而散，求财有始无终；唯散事宜之。")
    if paipan['bian_gua'] and paipan['bian_gua']['name'] in liuhe_gua:
        L.append("　· 动而化六合，主先难后易、散而复聚，求财终成。")
    if paipan['bian_gua'] and paipan['bian_gua']['name'] in liuchong_gua:
        L.append("　· 动而化六冲，主先成后败、得而复失，求财终散。")

    # ============================================================
    # 三、综合断语与应期
    # ============================================================
    # 吉凶定性
    # 吉：财有气且财就我（持/生/克世），财源不受伤，无旺兄劫、无财化鬼兄
    xiong_dong_wang_ke = any(y['is_dong'] and s['level'] in ('旺相', '有气')
                             and not xiong_bei_zhi(y) and not any(z['is_dong'] for z in zis)
                             for y, s in xiong_sts)
    cai_hua_xiong_flag = any(y['liuqin'] == '妻财' and bq in ('官鬼', '兄弟')
                             for y, b, bq, h, jt in bian_info)
    cai_huike = any(y['liuqin'] == '妻财' and h == '回头克' for y, b, bq, h, jt in bian_info)
    zi_bei_ke = any(y['is_dong'] and (st_of(y)['dong_ke'] or any(f['is_dong'] for f in fus)) for y in zis)

    L.append("【三、综合断语与得财应期】")
    zong = []
    shi_branch_handled = False
    # 主财爻（持世、发动、旺者优先）及其旺衰措辞
    zhu_cai = max(cais, key=lambda y: (y['is_shi'], y['is_dong'], st_of(y)['score'])) if cais else None
    zhu_lv = st_of(zhu_cai)['level'] if zhu_cai else ''
    cai_lv_word = '旺相' if zhu_lv == '旺相' else ('有气' if zhu_lv == '有气' else '衰弱')
    if not cais:
        if fushen and (yue_rel in ('同', '生') or ri_rel in ('同', '生')):
            zong.append("卦中无现财，然伏财得日月生扶，待伏神出现、冲开飞神之日，财尚可求，属「先无后有」。")
        else:
            zong.append("卦中无财，伏财又不得时令，财福两空，此财强求无益，宜守不宜进。")
    else:
        if cai_wang and xiangbei in ('持世', '生世', '克世') and not xiong_dong_wang_ke \
                and not cai_hua_xiong_flag and not cai_huike and not shi['is_kong']:
            if (zi_dong_wang and not zi_hua_xiong and not zi_huike) or cai_ju or fu_ju:
                zong.append(f"财爻{cai_lv_word}、财来就我，又得福神（财源）发动/财局生世，财福双美——"
                            "此乃求财上上之卦，公私称意，利源丰厚而久远。")
            else:
                zong.append(f"财爻{cai_lv_word}而来生合持世，财来就我，求之易得；唯财源（子孙）未得纯旺"
                            "（或静、或受伤化泄），利虽有而未必丰厚长久，待子孙生旺日更进。")
        elif cai_wang and xiangbei in ('世生财', '世克财', '无关'):
            zong.append(f"财爻虽{cai_lv_word}，然与世无情（我去寻财），须主动经营、劳心劳力，"
                        "待世爻或财爻逢冲合之日方得。")
        elif xiong_dong_wang_ke:
            zong.append("财爻纵有气，奈何兄弟旺动无制，劫财分夺、成本耗散；须待官鬼制兄之日，或兄弟受克之期方可得，"
                        "目前断以破财、竞争。")
        elif cai_hua_xiong_flag or cai_huike:
            zong.append("财爻发动而化官鬼、化兄弟或回头克，是得而复失、因财生忧、劫耗之象；世爻有伤则恐因财致祸，"
                        "此财不取为安。")
        elif cai_kong_po:
            zong.append("财爻现而逢旬空、月破，目前虚而不实；旺者待出旬、填实逢合之日可得，衰者则为真空真破，难望。")
        elif shi['is_kong'] or shi['is_po']:
            shi_branch_handled = True
            pk = '旬空又逢月破' if (shi['is_kong'] and shi['is_po']) else ('旬空' if shi['is_kong'] else '月破')
            zong.append(f"世爻为求财之人，今{pk}，己身无力、心志不固（月破主事多破败），纵卦中有财亦难就手；"
                        "须待世爻出空、填实逢合之月日方有准实，此时只宜守静，不宜妄动求财。")
        elif zhu_lv in ('休囚', '无气') or any(s['dong_ke'] for y, s in cai_sts):
            yuan_ruo = (not zis) or all(z['is_kong'] or st_of(z)['level'] in ('休囚', '无气') for z in zis)
            if yuan_ruo:
                zong.append("财爻休囚无气或受克伤，且财源子孙不现、衰弱，求财费力而难得，纵得亦薄；"
                            "宜待财爻生旺、子孙得令、克神受制之月日再图。")
            else:
                zong.append("财爻虽现而休囚受克，喜财源子孙尚可生扶，待财爻生旺、克神受制之月日方得，目前迟滞。")
        else:
            zong.append("财爻有气而无伤，大体可求，唯须详上述世应、财源、动变，中和而断，难易介于迟速之间。")

    if zi_bei_ke and cais:
        zong.append("财源子孙被父母/动爻克伤，利源受损，纵得眼前小利，亦难长久，恐先得后失。")
    if (zi_hua_xiong or zi_huike) and cais:
        zong.append("财源子孙发动而化官鬼、父母或回头克，福神受伤化祸，求财中途恐生忧惊波折，"
                    "得利减色，慎防乐极生忧。")
    if fu_xiong_dong:
        zong.append("父兄皆动，如缘木求鱼，财源坏、劫夺兴，此财必不可得。")
    if xuanwu_guan_ke_shi:
        zong.append("官鬼临玄武动来克世，经商贩卖须严防盗贼、诈骗、圈套。")
    if ying and ying['is_kong']:
        zong.append("应爻空亡，交易对方、合伙之人不实，虚约难凭，谨防失信。")
    if shi['is_kong'] and not shi_branch_handled:
        zong.append("世爻旬空，自己心志不坚、底气不足，事宜缓图，待世爻出空逢值方有准实。")
    if shi['is_po'] and not shi_branch_handled:
        zong.append("世爻月破，事多破败难成，待出月填实、逢合之月日方有转机。")
    for z in zong:
        L.append("· " + z)

    # 应期
    yq = _cai_yingqi(paipan, cais, fushen, shi, cai_wx)
    if yq:
        L.append("【得财应期】")
        for q in yq:
            L.append("· " + q)

    L.append("（以上依《卜筮正宗·黄金策》商贾章、总断千金赋之法推演，为软件据卦理之分析；"
             "实际求财尚须结合事理、时令与经营本身综合判断。）")
    return L


def _cai_yingqi(paipan, cais, fushen, shi, cai_wx):
    """据财爻状态推断得财应期（地支日，提示查万年历）"""
    q = []
    yue, ri = paipan['yue_zhi'], paipan['ri_zhi']
    if not cais and fushen:
        chong_fei = LIUCHONG.get(fushen['feishen']['zhi'], '')
        q.append(f"伏财{fushen['zhi']}：待财爻值日（{fushen['zhi']}日）、或冲开飞神"
                 f"（{chong_fei}日）、或日月引拔之时得财。")
        return q
    if not cais:
        return q
    # 取最有力的财爻（动、持世、旺优先）
    def keyf(y):
        s = yao_wangshuai(y, paipan)
        return (y['is_shi'], y['is_dong'], s['score'])
    y = max(cais, key=keyf)
    s = yao_wangshuai(y, paipan)
    chong = LIUCHONG.get(y['zhi'], '')
    he = LIUHE.get(y['zhi'], '')
    if y['is_kong']:
        q.append(f"财爻{y['zhi']}旬空：旺者出旬后逢{y['zhi']}（值日）或{chong}（冲实）日得；衰者难。")
    elif y['is_po']:
        q.append(f"财爻{y['zhi']}月破：待填实（{y['zhi']}日）或逢合（{he}日）得。")
    elif s['mu']:
        chong_mu = LIUCHONG.get(_MUKU[y['wuxing']], '')
        q.append(f"财入墓于{_MUKU[y['wuxing']]}：待冲墓（{chong_mu}日）或冲财（{chong}日）得。")
    elif y['is_dong'] and (s['ri_he'] or
                           any(LIUHE.get(o['zhi']) == y['zhi'] and o['is_dong'] for o in paipan['yaos'])):
        q.append(f"财动被合住（绊住）：待冲开（{chong}日）得财；合住如财被人把住，冲日方到我手。")
    elif y['is_dong']:
        if s['jue']:
            q.append(f"动财逢绝：待长生/生旺财爻之日（如{_CHANGSHENG[y['wuxing']]}日及生{y['wuxing']}之日）得。")
        else:
            q.append(f"财爻发动：逢值（{y['zhi']}日）或逢合（{he}日）得；动而克世者来尤速。")
    else:
        if s['ri_he']:
            q.append(f"静财逢日辰六合为「合起」（暗助旺相）：逢冲（{chong}日）、逢值（{y['zhi']}日）得财。")
        elif s['level'] in ('旺相', '有气'):
            q.append(f"财爻安静有气：逢冲（{chong}日）暗动得财，或逢值（{y['zhi']}日）得。")
        else:
            q.append(f"财爻安静休囚：待生旺财爻之月日（生{y['wuxing']}或{y['wuxing']}旺之月日），"
                     f"逢冲（{chong}日）、逢值（{y['zhi']}日）方得。")
    q.append("（应期以地支日推，具体公历日期请查万年历最近的相应地支日；近事以日断，远事以月断。）")
    return q


# ============================================================
# 测试
# ============================================================
if __name__ == '__main__':
    # 测试：模拟摇卦（背数：初爻到上爻）
    # 例如：初爻一背(单)、二爻三背(重/动)、三爻二背(拆)、四爻一背(单)、五爻三字(交/动)、上爻二背(拆)
    ce_shi = [1, 3, 2, 1, 0, 2]
    yao_list, dong = qigua_from_tongqian(ce_shi)
    shang, xia = build_gua_from_yaos(yao_list)
    print(f"本卦：上{shang} 下{xia}，动爻：{dong}")

    pan = zhuang_gua(shang, xia, dong_yao=dong,
                     yue_zhi='卯', ri_gan='甲', ri_zhi='子')
    print(paipan_to_text(pan))
    print()
    result = fenxi_gua(pan, yongshen_type='官鬼')
    for r in result:
        print(r)
