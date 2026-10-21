# -*- coding: utf-8 -*-
"""
六爻专断模块（《卜筮正宗·黄金策》各事项）：功名（仕宦）、考试（求名）、婚姻、疾病。
统一三段式：
  一、《黄金策》经典原文与释义（随卦象动态选取贴合条文）；
  二、本卦逐条详断（用神、原神、忌神、世应、动变、伏神、格局）；
  三、综合断语与应期。
理论依据：《卜筮正宗·黄金策》《总断千金赋》，兼参《增删卜易》。
"""
from liuyao_core import (
    DIZHI, TIANGAN, DIZHI_WUXING, WUXING_SHENG, WUXING_KE,
    LIUHE, LIUCHONG, LIUQIN,
    get_liuqin, get_wuxing_relation, hua_jin_tui, num_to_cn,
    yao_wangshuai, find_fushen, sanhe_ju,
    _yao_brief, _yao_by_pos, _bian_by_pos, _liuqin_wuxing,
    _MUKU, _JUEDI, _CHANGSHENG,
)

# 六合卦、六冲卦
LIUHE_GUA = ['天地否', '地天泰', '水泽节', '山水蒙', '风雷益', '雷地豫', '地山谦', '泽水困']
LIUCHONG_GUA = ['乾为天', '兑为泽', '离为火', '震为雷', '巽为风', '坎为水', '艮为山', '坤为地',
                '天雷无妄', '雷天大壮']

_YQ_TAIL = "（应期以地支日推，具体公历日期请查万年历最近的相应地支日；近事以日断，远事以月断。）"


# ============================================================
# 通用框架
# ============================================================
def _head(paipan):
    """卦头：卦象、日月、旬空、动爻"""
    L = []
    gong_wx = paipan['gong_wuxing']
    head = f"【卦象】{paipan['name']}（{paipan['gong']}宫{paipan['gongwei']}，{gong_wx}）"
    if paipan['bian_gua']:
        head += f" 之 {paipan['bian_gua']['name']}"
    L.append(head)
    L.append(f"【日月】月建{paipan['yue_zhi']}{DIZHI_WUXING[paipan['yue_zhi']]}　"
             f"日辰{paipan['ri_gan']}{paipan['ri_zhi']}{DIZHI_WUXING[paipan['ri_zhi']]}　"
             f"旬空{paipan['xunkong'][0]}{paipan['xunkong'][1]}")
    L.append("【动爻】" + ('、'.join(f"{num_to_cn(d)}爻动" for d in paipan['dong_yao'])
                         if paipan['dong_yao'] else '六爻安静，无动爻'))
    return L


def _setup(paipan):
    """统一上下文"""
    yx = list(reversed(paipan['yaos']))          # 初爻→上爻
    yue, ri = paipan['yue_zhi'], paipan['ri_zhi']
    gong_wx = paipan['gong_wuxing']
    shi = next(y for y in yx if y['is_shi'])
    ying = next((y for y in yx if y['is_ying']), None)

    def st_of(y):
        return yao_wangshuai(y, paipan)

    byqin = {q: [y for y in yx if y['liuqin'] == q] for q in LIUQIN}
    return dict(paipan=paipan, yx=yx, yue=yue, ri=ri, gong_wx=gong_wx,
                shi=shi, ying=ying, st_of=st_of, byqin=byqin)


def _yong_yao_duan(y, C, extra=''):
    """详断某一爻，返回一行（用于用神、原神、忌神、世应等）"""
    brief, s = _yao_brief(y, C['paipan'])
    d = []
    if s['yue']:
        d.append(s['yue'])
    if s['ri']:
        d.append(s['ri'])
    if s['dong_sheng']:
        d.append('受动爻生：' + '、'.join(s['dong_sheng']))
    if s['dong_ke']:
        d.append('受动爻克：' + '、'.join(s['dong_ke']))
    if s['changsheng']:
        d.append(f"逢长生于{s['changsheng']}")
    if s['mu']:
        d.append(f"入墓于{s['mu']}，主阻滞，待冲墓")
    if s['jue']:
        d.append(f"逢绝于{s['jue']}，须逢生旺")
    if y['is_dong'] and s['ri_he']:
        d.append('动而被日辰合住（绊住），待冲开之日')
    if y['is_kong']:
        d.append('旺相空为假空，待出旬值日即应；衰弱空为真空，难应' if s['score'] >= 2
                 else '衰弱又空，为真空，难应')
    if y['is_po']:
        d.append('月破，待出月填实、逢合之日')
    if extra:
        d.append(extra)
    return "　· " + brief + "：" + ('；'.join(d) if d else '无明显刑冲克害，平和') + '。'


def _fushen_duan(C, yong_qin):
    """伏神详断（用神不上卦）"""
    fs = find_fushen(C['paipan'], yong_qin)
    if not fs:
        return [f"　· 本宫亦寻伏「{yong_qin}」不得，用爻毫无其根，大不利。"]
    fei = fs['feishen']
    yue, ri = C['yue'], C['ri']
    yue_rel = get_wuxing_relation(DIZHI_WUXING[yue], fs['wuxing']) if yue else '无'
    ri_rel = get_wuxing_relation(DIZHI_WUXING[ri], fs['wuxing']) if ri else '无'
    fei_rel = get_wuxing_relation(fei['wuxing'], fs['wuxing'])
    fei_map = {
        '生': '飞神生伏，伏得生扶易出，吉',
        '克': '飞神克伏（伤身），伏被压难出',
        '被生': '伏生飞而泄气，难出现',
        '被克': '伏克飞为「出暴」，事机急暴、乍起乍落',
        '同': '飞伏比和，伏易出',
    }
    tian = []
    if yue_rel in ('同', '生'):
        tian.append('得月建生扶')
    if ri_rel in ('同', '生'):
        tian.append('得日辰生扶')
    if LIUCHONG.get(C['yue']) == fs['zhi']:
        tian.append('伏神逢月破，待填实逢合')
    elif yue_rel == '克':
        tian.append('伏神被月建所克')
    if LIUCHONG.get(C['ri']) == fs['zhi']:
        tian.append('伏神逢日冲（日破）')
    elif ri_rel == '克':
        tian.append('伏神被日辰所克')
    if fs['zhi'] in C['paipan']['xunkong']:
        tian.append('伏神又逢旬空')
    L = [f"　· 于本宫{C['paipan']['gong']}卦寻得伏神：{num_to_cn(fs['pos'])}爻{yong_qin}"
         f"{fs['zhi']}{fs['wuxing']}，伏于{num_to_cn(fei['pos'])}爻飞神「{fei['liuqin']}"
         f"{fei['zhi']}{fei['wuxing']}」之下。"]
    L.append("　· 伏神待日月动爻生扶拱合、或冲开飞神、伏神值日出现方应；"
             + ('、'.join(tian) if tian else '目前不得日月生扶') + '；'
             + fei_map.get(fei_rel, '飞伏无克，待时可出') + '。')
    return L


def _geju_duan(C, he_txt, chong_txt, hua_he_txt=None, hua_chong_txt=None):
    """六合、六冲格局"""
    L = []
    p = C['paipan']
    if p['name'] in LIUHE_GUA:
        L.append("　· 本卦为六合卦：" + he_txt)
    if p['name'] in LIUCHONG_GUA:
        L.append("　· 本卦为六冲卦：" + chong_txt)
    if p['bian_gua'] and p['bian_gua']['name'] in LIUHE_GUA:
        L.append("　· 动而化六合：" + (hua_he_txt or he_txt))
    if p['bian_gua'] and p['bian_gua']['name'] in LIUCHONG_GUA:
        L.append("　· 动而化六冲：" + (hua_chong_txt or chong_txt))
    return L


def _sanhe_duan(C, yong_qin, yong_wx):
    """三合用神局"""
    L = []
    for j in sanhe_ju(C['paipan']):
        if j['wuxing'] != yong_wx:
            continue
        sheng_shi = get_wuxing_relation(j['wuxing'], C['shi']['wuxing']) in ('生', '同')
        L.append("　· 卦会三合" + yong_qin + "局（" + ''.join(j['zhi'])
                 + f"成{j['wuxing']}局，{j['kind']}）"
                 + ('，动来生合世身，大吉。' if sheng_shi
                    else '，然不生世，事未归己，待生合日月。'))
    return L


def _bian_duan(C, xi_ji, hua_qin_img=None):
    """
    动变详断。
    xi_ji: {动爻六亲: '喜'（宜旺，生扶为吉）或 '忌'（宜衰，被克为吉）}
    hua_qin_img: {(动六亲, 变六亲): 意象断语}
    """
    L = []
    p = C['paipan']
    gong_wx = C['gong_wx']
    any_ = False
    for y in C['yx']:
        if not y['is_dong']:
            continue
        by = _bian_by_pos(p, y['pos'])
        if not by:
            continue
        any_ = True
        bq = get_liuqin(gong_wx, by['wuxing'])
        rel = get_wuxing_relation(by['wuxing'], y['wuxing'])
        seg = f"　· {num_to_cn(y['pos'])}爻{y['liuqin']}{y['zhi']}动，变{bq}{by['zhi']}"
        tags = []
        direction = xi_ji.get(y['liuqin'], '喜')
        jt = hua_jin_tui(y['zhi'], by['zhi'])
        if rel == '生':
            tags.append('回头生，' + ('吉神得益，吉' if direction == '喜' else '凶神得势，凶'))
        elif rel == '克':
            tags.append('回头克，' + ('吉神受伤，凶' if direction == '喜' else '凶神被制，反吉'))
        elif rel == '同' and jt and jt != '化比和':
            if jt == '化进神':
                tags.append('化进神，' + ('势盛，吉' if direction == '喜' else '凶势益盛，凶'))
            else:
                tags.append('化退神，' + ('势退，凶' if direction == '喜' else '凶势渐退，吉'))
        else:
            # 非回头生克、非进退：动生变（被生）/动克变（被克），查六亲化意象
            img = hua_qin_img.get((y['liuqin'], bq)) if hua_qin_img else None
            if img:
                tags.append(img)
            elif rel == '被生':
                if not _youli(y, C):
                    tags.append('动爻空破，暂不生「' + bq + '」，待填实')
                else:
                    tags.append('动爻转生「' + bq + '」，本爻力泄，再看「' + bq + '」与用神生克')
            elif rel == '被克':
                if not _youli(y, C):
                    tags.append('动爻空破，暂不克「' + bq + '」，待填实')
                else:
                    tags.append('动爻去制「' + bq + '」，化出之神受克；若「' + bq
                                + '」为用神、原神则不利')
        if not tags:
            tags.append('化比和，平顺' if jt == '化比和' else '化' + bq)
        L.append(seg + '：' + '；'.join(tags) + '。')
    if not any_:
        L.append("　· 卦无动爻（或动而不化），六爻安静，以本卦旺衰、世应生合静断。")
    return L


def _yong_yingqi(C, yong_qin, yongs, fushen, verb='应事'):
    """通用应期（地支日）"""
    q = []
    if not yongs and fushen:
        chong_fei = LIUCHONG.get(fushen['feishen']['zhi'], '')
        q.append(f"伏「{yong_qin}」{fushen['zhi']}：待值日（{fushen['zhi']}日）或冲开飞神"
                 f"（{chong_fei}日）、日月引拔之时{verb}。")
        q.append(_YQ_TAIL)
        return q
    if not yongs:
        return q
    y = max(yongs, key=lambda y: (y['is_shi'], y['is_dong'], C['st_of'](y)['score']))
    s = C['st_of'](y)
    chong = LIUCHONG.get(y['zhi'], '')
    he = LIUHE.get(y['zhi'], '')
    if y['is_kong']:
        q.append(f"「{yong_qin}」{y['zhi']}旬空：旺者出旬逢值（{y['zhi']}日）或逢冲（{chong}日）{verb}；衰者难。")
    elif y['is_po']:
        q.append(f"「{yong_qin}」{y['zhi']}月破：待填实（{y['zhi']}日）或逢合（{he}日）{verb}。")
    elif s['mu']:
        q.append(f"入墓于{_MUKU[y['wuxing']]}：待冲墓（{LIUCHONG.get(_MUKU[y['wuxing']], '')}日）"
                 f"或冲（{chong}日）{verb}。")
    elif y['is_dong'] and s['ri_he']:
        q.append(f"动被合住：待冲开（{chong}日）{verb}。")
    elif y['is_dong']:
        q.append(f"「{yong_qin}」发动：逢值（{y['zhi']}日）或逢合（{he}日）{verb}。")
    else:
        if s['ri_he']:
            q.append(f"静逢日合为「合起」：逢冲（{chong}日）、逢值（{y['zhi']}日）{verb}。")
        elif s['level'] in ('旺相', '有气'):
            q.append(f"「{yong_qin}」安静有气：逢冲（{chong}日）暗动、逢值（{y['zhi']}日）{verb}。")
        else:
            q.append(f"「{yong_qin}」安静休囚：待生旺、逢冲（{chong}日）、逢值（{y['zhi']}日）{verb}。")
    q.append(_YQ_TAIL)
    return q


def _youli(y, C):
    """该爻有无实际生克之力：月破、真空、休囚无气则无力（动而空破亦暂不生克）。"""
    if y is None:
        return False
    s = C['st_of'](y)
    if y['is_po']:
        return False
    if y['is_kong'] and s['score'] < 2:
        return False
    if s['score'] < 0 and s['level'] in ('无气', '休囚'):
        return False
    return True


# ============================================================
# 功名（仕宦）
# ============================================================
_GONG_HUA = {
    ('官鬼', '父母'): '官化印绶，文书相生，官名益固，吉',
    ('父母', '官鬼'): '印绶化官，官印相生，升迁之象，吉',
    ('官鬼', '妻财'): '官化财禄，财来生官，吉',
    ('妻财', '官鬼'): '财化官，原神生用，吉',
    ('官鬼', '子孙'): '官化子孙，用神被克，剥官削职，凶',
    ('官鬼', '兄弟'): '官化兄弟，同僚争竞、减俸，凶',
    ('父母', '子孙'): '印绶化子孙，克官之神得生，凶',
    ('兄弟', '官鬼'): '兄弟化官，官来制兄，减俸之患得除，吉',
    ('子孙', '父母'): '子孙化父母，忌神被印绶所制，先阻后解，吉凶相半',
    ('子孙', '官鬼'): '子孙化官，忌神化用，然子孙已动先克官，先凶后解',
}


def fenxi_gongming(paipan):
    """《黄金策·仕宦》功名事业专断：官鬼为用神，妻财为俸禄原神，父母为印绶，子孙为忌。"""
    C = _setup(paipan)
    L = _head(paipan)
    guans = C['byqin']['官鬼']; cais = C['byqin']['妻财']
    fus = C['byqin']['父母']; zis = C['byqin']['子孙']; xiongs = C['byqin']['兄弟']
    shi = C['shi']; gong_wx = C['gong_wx']
    yong_wx = _liuqin_wuxing(gong_wx, '官鬼')

    fushen = find_fushen(paipan, '官鬼') if not guans else None

    guan_sts = [(y, C['st_of'](y)) for y in guans]
    guan_wang = any(s['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po']
                    for y, s in guan_sts)
    guan_kong_po = any(y['is_kong'] or y['is_po'] for y in guans)
    zi_dong = any(y['is_dong'] for y in zis)
    fu_kong = any(y['is_kong'] or y['is_po'] for y in fus) or not fus
    xiong_dong = any(y['is_dong'] for y in xiongs)
    cai_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in cais)
    cai_kong = (not cais) or all(y['is_kong'] or y['is_po'] for y in cais)

    def grel(y):
        if y['is_shi']:
            return '持世'
        return get_wuxing_relation(y['wuxing'], shi['wuxing'])
    guan_chishi = any(y['is_shi'] for y in guans)
    guan_shengshi = any(grel(y) == '生' for y in guans)
    guan_keshi = any(grel(y) == '克' for y in guans)
    yue_ri_sheng = any(get_wuxing_relation(DIZHI_WUXING[C['yue']], y['wuxing']) == '生'
                       or get_wuxing_relation(DIZHI_WUXING[C['ri']], y['wuxing']) == '生'
                       for y in guans)
    guan_ju = [j for j in sanhe_ju(paipan) if j['wuxing'] == yong_wx]

    # ---------- 一、经典 ----------
    L.append("【一、《黄金策·仕宦》论功名（经典）】")
    L.append("· 总纲：「为国求贤，治民为本；致身辅相，禄养为先。旺相妻财，必得千钟之粟；"
             "兴隆官鬼，定居一品之尊」——未仕求名不要财爻，已仕贵人要见财爻，盖有爵必有禄，"
             "未有无俸而居官者。官星旺相，俸禄必多；官鬼旺相，官高爵大；休囚死绝，官小职卑。")
    L.append("· 六亲取用：官鬼为用神（功名职位）；妻财为俸禄、为原神（生官）；父母为印绶"
             "（官之凭、文书，制伤官之子）；子孙为忌神（克官、剥官削职）；兄弟发动主减俸除粮。")
    # 固定核心经文（每卦必列，先通论）
    _GM_JING = [
        ("官爻隐伏，莫思爵位升迁", "官鬼即官职，卦中无官鬼或官星空破，求官无分；官临持身世、或动来生合世，"
                                  "又不受月日冲克，凡有谋为方能升迁。"),
        ("子若交重，当虑剥官削职", "子孙克官鬼，子孙若在卦中发动，所谋必不遂意；已任者恐有褫职剥官之祸。"),
        ("父母空亡，休望差除宣敕", "父母为印绶、文书、诰牒、宣敕、奏书、表章，卦中不可无、宜旺不宜衰、"
                                  "扶世最吉；空亡则无任命文凭，休望差除。"),
        ("兄如发动，须防减俸除粮", "兄弟发动，不免费财招谤、减俸除粮；若与子孙同发、或化出子孙，"
                                  "必有除粮减俸之事，持身临世皆不吉。"),
        ("身边伏鬼若非空，头上乌纱终不脱", "官鬼临身持世、或本宫鬼伏于世下而不空，虽见责罚，官职犹在；"
                                            "若不临身世、不伏世下、或伏而空亡，必遭黜革。"),
        ("月建生身，当际风云之会；岁君合世，必承雨露之恩", "月建为执政之官、太岁为君象，官星得月建生合、"
                                            "岁君加父母扶出官爻世爻者，必有举荐升擢、朝廷天恩。"),
        ("鬼煞伤身，因见灾殃之不免", "官鬼动来生合世者为用神，主进取升迁；动来刑冲克伤世者则为鬼煞，"
                                     "必有凶祸，太岁加刑则贬谪难逃。"),
        ("太岁加刑不顺，贬谪难逃", "太岁刑伤世爻必遭贬谪，更加刑害腾蛇白虎，主锁拘擒拿之辱。"),
        ("卦静世空，退休之兆；身空煞动，避祸之征", "已任而世爻空亡、六爻安静、日月岁君未伤，是休官之象；"
                                                    "若官鬼同日月岁君克世而世又空，急宜避祸可免。"),
        ("财空鬼动，声名震而囊箧空虚", "官动生合世、日月不冲克，为官有声名；更得财生扶则内实贪赂、外不丧名；"
                                       "若世爻空伏、财爻死绝，虚名虽有而贿赂无也。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _GM_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    if guan_wang and (guan_chishi or guan_shengshi):
        L.append("· 官鬼为仕宦之主，得官星旺相、持临身世或动来生合世，凡有谋为必升，官高爵大。")
    if guan_chishi and not guan_kong_po:
        L.append("· 「身边伏鬼若非空，头上乌纱终不脱」——官临身世或鬼伏世下，虽见责罚，官职犹在。")
    if (not guans or guan_kong_po) and not guan_chishi:
        L.append("· 「官爻隐伏，莫思爵位升迁」——卦无官鬼或官星空破，求官无分，头上乌纱难保。")
    if zi_dong:
        L.append("· 「子若交重，当虑剥官削职」——子孙为克官之煞，发动所谋不遂，已任者恐褫职。")
    if fu_kong:
        L.append("· 「父母空亡，休望差除宣敕」——父母为印绶文书、诰牒宣敕，空亡则无任命文凭。")
    if cai_wang:
        L.append("· 「妻财为俸禄，财旺得禄千钟」——已仕占官，财爻旺相则俸禄丰厚。")
    if cai_kong:
        L.append("· 「财爻休囚空伏，未得俸禄」——财空则俸禄薄、官无生源。")
    if xiong_dong:
        L.append("· 「兄如发动，须防减俸除粮」——兄弟动，费财招诽、减俸。")
    if yue_ri_sheng or guan_ju:
        L.append("· 「月建生身，当际风云之会；岁君合世，必承雨露之恩」——官星得月日生合、"
                 "或会成官局，必有举荐升擢。")
    if guan_keshi:
        L.append("· 「鬼煞伤身，因见灾殃之不免」——官鬼生合世为用神（升迁）；动来克伤世为鬼煞，"
                 "刑冲克世必有凶祸，太岁加刑则贬谪难逃。")

    # ---------- 二、逐条详断 ----------
    L.append("【二、本卦功名逐条详断】")
    L.append("（1）用神·官鬼爻（功名职位）")
    if guans:
        for y in guans:
            L.append(_yong_yao_duan(y, C))
    else:
        L.append("　· 卦中不见官鬼爻，用神不上卦。")
        for ln in _fushen_duan(C, '官鬼'):
            L.append(ln)

    L.append("（2）世爻（求官之人）与官鬼向背")
    L.append(_yong_yao_duan(shi, C))
    if guans:
        if guan_chishi:
            L.append("　· 官鬼持世，官在己身，求官最切、官来就我。")
        elif guan_shengshi:
            if guan_wang:
                L.append("　· 官鬼旺相生合世爻，官来就我，升迁大吉。")
            else:
                L.append("　· 官鬼虽生合世，然官爻休囚无气，生世无力，主官小、欲升而力不足，"
                         "待官逢生旺日月。")
        elif guan_keshi:
            L.append("　· 官鬼克世，是鬼煞伤身，非官来就我，主灾咎。")
        else:
            L.append("　· 官与世无生合，乃我去求官，须凭荐举、劳心劳力，世旺方得。")
    if C['ying']:
        L.append(_yong_yao_duan(C['ying'], C, extra='应爻为所任之地、同僚或所托之人'))

    L.append("（3）印绶·父母爻（官之凭、宣敕，制伤官之子）")
    if fus:
        for y in fus:
            L.append(_yong_yao_duan(y, C))
    else:
        L.append("　· 父母不现，印绶文凭隐伏，任命文书无力；须查伏神、待值日。")

    L.append("（4）俸禄·妻财爻（原神·生官·俸禄）")
    if cais:
        for y in cais:
            L.append(_yong_yao_duan(y, C))
    else:
        L.append("　· 妻财不现，俸禄无气、官无生源，仕宦之禄薄。")

    L.append("（5）忌神·子孙（剥官）与兄弟（减俸）")
    if zis:
        for y in zis:
            if y['is_dong']:
                ex = '子孙发动克官，剥官削职，大忌'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '子孙静而旺，暗有夺官之忧，待逢冲值日发动则凶'
            else:
                ex = '子孙静而休囚，不主动克官，暂无害'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 子孙不现，克官之神不兴，官无剥夺，吉。")
    if xiongs:
        for y in xiongs:
            if y['is_dong']:
                ex = '兄弟发动，减俸除粮、同僚争'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '兄弟静旺，同僚同辈多、分禄，待发动方减俸'
            else:
                ex = '兄弟静衰，同僚不争，无害'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 兄弟不现，无减俸争竞之患。")

    L.append("（6）动爻变化吉凶")
    xi_ji = {'官鬼': '喜', '妻财': '喜', '父母': '喜', '子孙': '忌', '兄弟': '忌'}
    for ln in _bian_duan(C, xi_ji, _GONG_HUA):
        L.append(ln)

    L.append("（7）卦象格局")
    for ln in _sanhe_duan(C, '官鬼', yong_wx):
        L.append(ln)
    for ln in _geju_duan(C, "六合主仕途和顺、上下同心，任事久安。",
                         "六冲主任所不久、调动反复，有始无终。",
                         "动化六合，先调动后安定，终得久任。",
                         "动化六冲，先安后散，终主离任。"):
        L.append(ln)

    # ---------- 三、综合与应期 ----------
    L.append("【三、综合断语与升迁应期】")
    zong = []
    if not guans:
        if fushen and any(get_wuxing_relation(DIZHI_WUXING[z], fushen['wuxing']) in ('同', '生')
                          for z in (C['yue'], C['ri'])):
            zong.append("卦中无现官，然伏官得日月生扶，待伏神出现、冲开飞神之日，官尚可求，属先无后有。")
        else:
            zong.append("卦无官鬼，伏官又不得时令，功名两空，求官无分，宜守。")
    else:
        if guan_wang and (guan_chishi or guan_shengshi) and not zi_dong and not fu_kong \
                and not shi['is_kong'] and not shi['is_po']:
            if yue_ri_sheng or guan_ju or cai_wang:
                zong.append("官星旺相、官来就我（持世/生合世），印绶不空、子孙不兴，又得日月生扶、"
                            "财禄相生——此乃仕宦上上之卦，必得升迁，官高爵大。")
            else:
                zong.append("官星旺相、官来就我，求官易得、升迁有望；唯印绶、荐扶或财禄未得纯旺，"
                            "待日月生合、官爻逢值之日更进。")
        elif guan_chishi and not guan_kong_po:
            zong.append("官爻持世（或伏官于世下）不空，「头上乌纱终不脱」，虽有小责、同僚摩擦，"
                        "官职犹在，主小吉。")
        elif zi_dong:
            zong.append("子孙发动克官，主剥官削职、降官离任；须待官爻受克或子孙值日之期应，目前断以不吉。")
        elif guan_kong_po:
            zong.append("官鬼空破（或兼印绶空亡），求官无分、职位难保；旺者待填实出旬，衰者无望。")
        elif guan_keshi:
            zong.append("官鬼动来克世（非生合），为鬼煞伤身，主任上灾咎、贬谪，须防灾祸。")
        elif shi['is_kong'] or shi['is_po']:
            pk = '旬空' if shi['is_kong'] else '月破'
            zong.append(f"世爻{pk}，己身无力、居官不久，待出空填实逢合方有转机。")
        else:
            zong.append("官爻有气而未得纯旺，或休囚平和，主官小职卑、平稳待时，"
                        "待官逢生旺、生合世身之日升迁。")
    for z in zong:
        L.append("· " + z)

    yq = _yong_yingqi(C, '官鬼', guans, fushen, verb='升迁得官')
    if yq:
        L.append("【升迁应期】")
        for q in yq:
            L.append("· " + q)

    L.append("（以上依《卜筮正宗·黄金策》仕宦章、总断千金赋之法推演，为软件据卦理之分析；"
             "实际功名尚须结合才德、人事、时势综合判断。）")
    return L


# ============================================================
# 考试（求名）
# ============================================================
_KAO_HUA = {
    ('父母', '官鬼'): '文书化官，文章得名，吉',
    ('官鬼', '父母'): '官化文书，官名与文章相生，吉',
    ('父母', '妻财'): '文书化财，财回头克父，文章破绽，凶',
    ('官鬼', '子孙'): '官化子孙，名次被克，凶',
    ('父母', '子孙'): '文书化子孙，子孙生财、财克父，文事有阻，凶',
    ('官鬼', '兄弟'): '官化兄弟，同经争名次，凶',
    ('妻财', '父母'): '财化父母，财不克父，文书得复，吉凶相半',
    ('子孙', '官鬼'): '子孙化官，忌神化用，然子已动先克官，先阻后解',
    ('子孙', '父母'): '子孙化父母，父克子，忌神受制，先阻后解',
    ('兄弟', '官鬼'): '兄弟化官，夺标者反助官，先争后让',
    ('兄弟', '父母'): '兄弟化父母，文书得生，然兄为同经，得失相半',
}


def fenxi_kaoshi(paipan):
    """《黄金策·求名》考试学业专断：父母为文章、官鬼为名次，二者皆宜旺；妻财、子孙为忌。"""
    C = _setup(paipan)
    L = _head(paipan)
    fus = C['byqin']['父母']; guans = C['byqin']['官鬼']
    cais = C['byqin']['妻财']; zis = C['byqin']['子孙']; xiongs = C['byqin']['兄弟']
    shi = C['shi']; gong_wx = C['gong_wx']
    fu_wx = _liuqin_wuxing(gong_wx, '父母'); guan_wx = _liuqin_wuxing(gong_wx, '官鬼')

    fu_shen = find_fushen(paipan, '父母') if not fus else None
    guan_shen = find_fushen(paipan, '官鬼') if not guans else None

    fu_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po']
                  for y in fus)
    guan_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po']
                    for y in guans)
    fu_kp = any(y['is_kong'] or y['is_po'] for y in fus)
    guan_kp = any(y['is_kong'] or y['is_po'] for y in guans)
    cai_dong = any(y['is_dong'] for y in cais)
    zi_dong = any(y['is_dong'] for y in zis)
    xiong_dong = any(y['is_dong'] for y in xiongs)
    fu_chishi = any(y['is_shi'] for y in fus)
    guan_chishi = any(y['is_shi'] for y in guans)
    fu_shengshi = any(get_wuxing_relation(y['wuxing'], shi['wuxing']) == '生' for y in fus)
    guan_shengshi = any(get_wuxing_relation(y['wuxing'], shi['wuxing']) == '生' for y in guans)
    fu_guan_chong = any(LIUCHONG.get(fy['zhi']) == gy['zhi'] for fy in fus for gy in guans)
    yue_ri_fu = any(get_wuxing_relation(DIZHI_WUXING[C['yue']], y['wuxing']) in ('同', '生')
                    or get_wuxing_relation(DIZHI_WUXING[C['ri']], y['wuxing']) in ('同', '生')
                    for y in fus + guans)
    long_hu = any(y['is_dong'] and y['liushen'] in ('青龙', '白虎') for y in C['yx'])

    # 一、经典
    L.append("【一、《黄金策·求名》论考试（经典）】")
    L.append("· 总纲：「读书五车，固欲置身于廊庙；胸藏万卷，肯甘遁迹于丘园？要相国家，当详易卦。"
             "父爻旺相，其文掷地金声；鬼位兴隆，家报泥金捷喜」——凡占功名，以父爻为文章、"
             "鬼为官职，二者一卦之主，伤一则不成。父爻旺相，文章必佳；官鬼得地，功名有望。")
    L.append("· 六亲取用：父母为文章试卷（主用神），官鬼为功名名次（主用神），二者皆宜旺相有气、"
             "不空破、生合世身；妻财克父母、子孙克官鬼，皆为忌神；兄弟为同经之士，动则夺标。")
    # 固定核心经文（每卦必列，先通论）
    _KS_JING = [
        ("财若交重，休望青钱之中选；福如发动，难期金榜之题名", "唯卜功名，以财、福反为恶煞，"
                                          "盖财能克父、子能克鬼也；妻财发动则文章破绽，子孙发动则名次被克。"
                                          "唯官爻持世得财动来生，而财无忌。"),
        ("兄弟同经，乃夺标之恶客", "兄弟即与我同经赴考之人，若发动、或月建日辰俱带兄弟，则同经者多，"
                                   "必能夺我之标，纵大象可成，名亦落后。"),
        ("月克文书，程式背而不中", "父母旺而得动爻日辰生合，其文字字锦绣；妻财伤克必多破绽，"
                                   "月建冲克，其文必不合主司程式而不中。"),
        ("两用相冲，题目生疏而不熟", "以官爻为用爻，喜合而不喜冲；官父相冲，主出题生涩不熟。"),
        ("日辰辅德，实劝驾之良朋", "父母官鬼无气，若得日辰扶起、克制恶煞，仍旧有望；或世爻衰静空亡，"
                                   "得日辰生扶冲实，主有亲友资助盘费、辅其赴考。"),
        ("父旺官衰，可惜刘蕡之下第；父衰官旺，堪嗟张爽之登科", "父母官鬼皆宜有力无损，功名可成；"
                                          "父旺官空则文章虽好而不第，父衰官旺则文字平常反可成名。"),
        ("世伤官鬼，仕途窒而不通", "世乃求名之人，世持官鬼或得官鬼生合，功名有望；若临子孙克制官鬼，"
                                   "是仕途未通，徒去求谋无济。"),
        ("龙虎二爻俱动，一举成名", "青龙白虎俱在卦中动来生合世爻，必中魁选；若持官父或持身世尤妙。"),
        ("父官三合相逢，连科及第", "卦有三合会成官局者，主连科及第，会成父母局亦吉。"),
        ("卦值六冲，此去难题雁塔；爻达六合，这回必占鳌头", "占功名得六冲卦必难成，得六合卦必易得。"),
        ("六爻竞发，功名恍惚以难成", "六爻皆喜安静，只要官鬼有气不空、月日不来伤克则吉；乱动则多变化，"
                                     "变出死墓绝空刑克，皆为破败，大概不吉。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _KS_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    if cai_dong:
        L.append("· 「财若交重，休望青钱之中选」——妻财发动克父母，文书被伤，文章破绽。")
    if zi_dong:
        L.append("· 「福如发动，难期金榜之题名」——子孙发动克官鬼，名次被克。")
    if xiong_dong:
        L.append("· 「兄弟同经，乃夺标之恶客」——兄弟发动，同经者多，纵可成名亦落后。")
    if fu_wang and guan_wang:
        L.append("· 父爻旺相文章必佳，官鬼得地名次有望，官父两全。")
    if fu_wang and not guan_wang:
        L.append("· 「父旺官衰，可惜刘蕡之下第」——文字虽佳，名次不足，恐不中式。")
    if not fu_wang and guan_wang:
        L.append("· 「父衰官旺，堪嗟张爽之登科」——文字虽平，得官旺扶，亦可成名。")
    if fu_kp or not fus:
        L.append("· 父母空破或不上卦，文章试卷不力，「月克文书，程式背而不中」。")
    if guan_kp or not guans:
        L.append("· 官鬼空破或不上卦，名次无分。")
    if fu_guan_chong:
        L.append("· 「两用相冲，题目生疏而不熟」——官父相冲，题目不就。")
    if yue_ri_fu:
        L.append("· 「日辰辅德，实劝驾之良朋」——官父无气，得日月生扶拱合，仍有指望。")
    if long_hu:
        L.append("· 「龙虎二爻俱动，一举成名」——青龙、白虎动生合世，必中魁选。")

    # 二、逐条
    L.append("【二、本卦考试逐条详断】")
    L.append("（1）主用神·父母爻（文章试卷）")
    if fus:
        for y in fus:
            L.append(_yong_yao_duan(y, C))
    else:
        L.append("　· 卦中不见父母爻，文章之主不上卦。")
        for ln in _fushen_duan(C, '父母'):
            L.append(ln)
    L.append("（2）主用神·官鬼爻（功名名次）")
    if guans:
        for y in guans:
            L.append(_yong_yao_duan(y, C))
    else:
        L.append("　· 卦中不见官鬼爻，名次之主不上卦。")
        for ln in _fushen_duan(C, '官鬼'):
            L.append(ln)
    L.append("（3）世爻（考生自己）与官父向背")
    L.append(_yong_yao_duan(shi, C))
    if fu_chishi or guan_chishi:
        L.append("　· 父母或官鬼持世，文章、功名在己身，最切。")
    elif fu_shengshi or guan_shengshi:
        L.append("　· 官父生合世身，功名来就，吉。")
    else:
        L.append("　· 官父不生合身世，须凭文章自奋、他人荐举，世旺方得。")
    L.append("（4）忌神·妻财（克父母、坏文书）")
    if cais:
        for y in cais:
            if y['is_dong']:
                ex = '妻财发动克父母，文书大忌'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '妻财静旺，暗伤文书，待发动则凶'
            else:
                ex = '妻财静衰，不克父，暂无害'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 妻财不现，文书不受克，文章无破绽，吉。")
    L.append("（5）忌神·子孙（克官）与兄弟（同经夺标）")
    if zis:
        for y in zis:
            if y['is_dong']:
                ex = '子孙发动克官，名次大忌'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '子孙静旺，暗有夺名之忧'
            else:
                ex = '子孙静衰，不克官，暂无害'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 子孙不现，官鬼不受克，名次稳固，吉。")
    if xiongs:
        for y in xiongs:
            if y['is_dong']:
                ex = '兄弟发动，同经夺标，然兄克财亦能护父'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '兄弟静旺，同经之士多，分名次'
            else:
                ex = '兄弟静衰，无夺标之争'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 兄弟不现，无同经夺标之争。")
    L.append("（6）动爻变化吉凶")
    xi_ji = {'父母': '喜', '官鬼': '喜', '妻财': '忌', '子孙': '忌', '兄弟': '忌'}
    for ln in _bian_duan(C, xi_ji, _KAO_HUA):
        L.append(ln)
    L.append("（7）卦象格局（三合、龙虎、六合六冲）")
    for ln in _sanhe_duan(C, '父母', fu_wx):
        L.append(ln)
    for ln in _sanhe_duan(C, '官鬼', guan_wx):
        L.append(ln)
    for ln in _geju_duan(C, "六合主功名易得，「这回必占鳌头」。",
                         "六冲主功名难成，「此去难题雁塔」。",
                         "动化六合，先难后易，终得中式。",
                         "动化六冲，先易后散，终主不中。"):
        L.append(ln)
    if long_hu:
        L.append("　· 青龙、白虎爻发动，「一举成名」，主科名之喜。")

    # 三、综合
    L.append("【三、综合断语与放榜应期】")
    zong = []
    if fu_wang and guan_wang and not cai_dong and not zi_dong and not shi['is_kong'] and not shi['is_po']:
        if fu_chishi or guan_chishi or fu_shengshi or guan_shengshi:
            zong.append("官父俱旺、文章与名次两全，又生合世身，财子不兴——此乃考试上上之卦，"
                        "金榜题名，名次必高。")
        else:
            zong.append("官父俱旺，文章佳、名次稳，然官父不生合世身，须得荐举或临场加力，放榜可中。")
    elif cai_dong:
        zong.append("妻财发动克父母，文书破绽，主不中；待财受克、父得生旺之期再考。")
    elif zi_dong:
        zong.append("子孙发动克官鬼，名次被克，主不中。")
    elif xiong_dong:
        zong.append("兄弟发动，同经夺标，主虽可成亦落后、名次不高。")
    elif fu_wang and not guan_wang:
        if not guans:
            zong.append("文章佳而卦无名次（官不现），刘蕡下第之象，主不中式。")
        else:
            zong.append("父旺官衰，文字好而名次低，恐落榜。")
    elif not fu_wang and guan_wang:
        zong.append("父衰官旺，文字平而得官扶，可侥幸成名，名次不高。")
    elif fu_kp or guan_kp or not fus or not guans:
        zong.append("官父空破或不上卦，文章、名次两虚，主不中。")
    elif shi['is_kong'] or shi['is_po']:
        zong.append("世爻空破，考生己身无力，或病阻试期，待出空填实。")
    else:
        zong.append("官父有气而未旺，或休囚平和，主学业未精、待时，待官父逢生旺、生合世身之日可中。")
    for z in zong:
        L.append("· " + z)
    yq = _yong_yingqi(C, '父母', fus, fu_shen, verb='放榜得名')
    if yq:
        L.append("【放榜应期】")
        for q in yq:
            L.append("· " + q)
    L.append("（以上依《卜筮正宗·黄金策》求名章、总断千金赋之法推演；学业功名尤在自身勤勉，"
             "卦理仅作参考。）")
    return L


# ============================================================
# 婚姻（分男女）
# ============================================================
_HUN_HUA_M = {   # 男占女，用神妻财
    ('妻财', '官鬼'): '财化官，财去生官，妇心或向他人，先私后公，凶',
    ('妻财', '子孙'): '财化子孙，子孙生财，吉',
    ('妻财', '兄弟'): '财化兄弟，回头克财，劫妻，凶',
    ('妻财', '父母'): '财化父母，财去克父，主与尊长不和',
    ('官鬼', '妻财'): '鬼化财，阻隔之神化出妻财，先阻后成，吉',
    ('官鬼', '子孙'): '鬼化子孙，子孙克官制阻，吉',
    ('兄弟', '妻财'): '兄弟化财，克妻者化财，先争后成',
    ('子孙', '妻财'): '子孙化财，子来生财，吉',
    ('父母', '妻财'): '父母化财，财克父，主庚帖与妇不和',
}
_HUN_HUA_F = {   # 女占男，用神官鬼
    ('官鬼', '妻财'): '官化财，财来生官（回头生），吉',
    ('官鬼', '子孙'): '官化子孙，回头克官，凶',
    ('官鬼', '兄弟'): '官化兄弟，兄弟泄财争竞，凶',
    ('官鬼', '父母'): '官化父母，父母生官（回头生），吉',
    ('妻财', '官鬼'): '财化官，财生官，吉',
    ('子孙', '官鬼'): '子孙化官，忌神化用，然子已动先克官，先阻后解',
    ('子孙', '父母'): '子孙化父母，父克子，忌神受制，先阻后解',
    ('兄弟', '官鬼'): '兄弟化官，官来制兄，先争后让',
}


def fenxi_hunyin(paipan, gender='男'):
    """《黄金策·婚姻》感情专断：男以妻财为妇、女以官鬼为夫；世为己、应为彼；重世应生合、阴阳得位。"""
    C = _setup(paipan)
    L = _head(paipan)
    nan = (gender == '男')
    yong_qin = '妻财' if nan else '官鬼'
    yong_lbl = '妻（妇）' if nan else '夫'
    yongs = C['byqin'][yong_qin]
    zis = C['byqin']['子孙']; xiongs = C['byqin']['兄弟']
    cais = C['byqin']['妻财']; guans = C['byqin']['官鬼']; fus = C['byqin']['父母']
    shi = C['shi']; ying = C['ying']; gong_wx = C['gong_wx']
    yong_wx = _liuqin_wuxing(gong_wx, yong_qin)
    fushen = find_fushen(paipan, yong_qin) if not yongs else None

    yong_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po']
                    for y in yongs)
    yong_kp = any(y['is_kong'] or y['is_po'] for y in yongs)
    yong_duo = len(yongs) >= 2
    ji_dong = any(y['is_dong'] for y in (xiongs if nan else zis))
    yuan_dong = any(y['is_dong'] for y in (zis if nan else cais))
    shi_kp = shi['is_kong'] or shi['is_po']
    ying_kp = ying['is_kong'] or ying['is_po']

    # 阴阳得位
    shi_yang = shi['yinyang'] == 1
    ying_yang = ying['yinyang'] == 1
    dewei = (shi_yang and not ying_yang) if nan else ((not shi_yang) and ying_yang)
    yong_yy = any(y['yinyang'] == (0 if nan else 1) for y in yongs)

    # 世应关系
    sy_rel = get_wuxing_relation(shi['wuxing'], ying['wuxing'])
    ys_rel = get_wuxing_relation(ying['wuxing'], shi['wuxing'])
    shi_ying_chong = (LIUCHONG.get(shi['zhi']) == ying['zhi'])
    shi_ying_he = (LIUHE.get(shi['zhi']) == ying['zhi'])
    shi_ying_bi = (shi['wuxing'] == ying['wuxing'])

    # 间爻（三、四爻）为媒人
    jian = [C['yx'][2], C['yx'][3]]
    jian_dong = [j for j in jian if j['is_dong']]
    jian_kong = [j for j in jian if j['is_kong']]
    # 财官动合（先私后公）
    si_he = any(LIUHE.get(y['zhi']) == shi['zhi'] and y['is_dong'] for y in yongs)

    # 一、经典
    L.append("【一、《黄金策·婚姻》论嫁娶（经典）】")
    L.append("· 总纲：「男女婚契于前定，朱陈缔结分在夙成。然非月老，焉知夫妇于当时；不有宓羲，"
             "岂识吉凶于今日。欲谐伉俪，须定阴阳」——阳奇阴偶，配合成婚。如男家卜，宜世属阳、"
             "应属阴，用神阴阳得位；女家卜，宜世阴、应阳。")
    L.append("· 六亲取用：男占女以妻财为用神（妇），女占男以官鬼为用神（夫）；世为己、应为彼，"
             "世应生合比和则两愿成婚；间爻为媒人，父母为庚帖主婚；"
             "男占女鬼空不妨，女占男财空不妨。")
    # 固定核心经文（每卦必列，先通论）
    _HY_JING = [
        ("阴阳相得，乃成夫妇之道；阴阳交错，难期琴瑟之鸣", "男卜女遇世阳应阴、用神得位为相得，"
                                          "主夫妻和顺；若世阴应阳、阴阳错位，后主夫妻欺凌、终朝反目。"),
        ("六合则易而且吉，六冲则难而又凶", "六合卦一阴一阳配合、世应相生、六爻相合，占主得之必成而吉；"
                                          "六冲卦纯阳纯阴，其象如二女同居、两男并处，志必不合，主难成，"
                                          "纵成亦不利。"),
        ("世合应应合世，终成种玉之缘", "男家卜世为男家、应女家，若得相合是两愿之象，主易成，后亦吉利。"),
        ("如逢财鬼空亡，乃婚姻之大忌；苟遇阴阳得位，实天命之所关", "卜女以财、卜男以官为用神，"
                                          "若值空亡必不吉利；然不可执泥——男占女以财为主，鬼空不妨，"
                                          "女占男以鬼为主，财空不妨。"),
        ("应财世鬼，终须夫唱妇随；应鬼世财，不免夫权妻夺", "男自占世持鬼应持财，阴阳得位，夫秉男权、"
                                          "妻操妇道，夫唱妇随；若世持财应持鬼，是阴阳失位，必夫权妻夺，"
                                          "唯入赘反吉。"),
        ("鬼克世爻，果信绿窗之难嫁；用合身位，方知绮席之易婚", "如鬼煞克世，不独不愿为婚，更防祸殃；"
                                          "若用神合身合世位，不独易成，日后必恩爱。"),
        ("财鬼如无刑害，夫妻定主和谐", "财、鬼不被刑冲克害，夫妻必到老和谐；若刑冲克害，必不睦。"),
        ("财官动合，先私而后公", "夫占以财为妇，世与动合、或财与世爻动合，是必先通而后娶；"
                                "财爻动与旁爻合，是与他人有情，财遇合多亦然。"),
        ("两父齐兴，必有争盟之象；双官俱动，斯为竞娶之端", "卦中动变见两重父母，主有两人主婚、"
                                          "两家庚帖；两鬼俱动则有两家争婚、事多反复。"),
        ("欲通媒妁，须论间爻", "占庚帖以间爻（三、四爻）为媒人；间爻与世生合言我家亲，与应生合"
                              "言彼家亲，与世应俱生合则两家皆亲，旺相新亲、休囚旧眷。"),
        ("世应化空，始成而终悔", "世动生合应则男家愿成、应动生合世则女家愿嫁，皆易成；"
                                "但怕变入空亡，必初成而后悔。"),
        ("内外互摇，定见家庭之挠括", "占婚姻卦宜安静，安静则家庭和睦；财动则不和公姑，鬼动则不和妯娌，"
                                    "父动则不和子侄，兄动则不和妻妾，加月建日辰不唯不和更有刑克。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _HY_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    if dewei:
        L.append("· 「阴阳相得，乃成夫妇之道」——世应阴阳得位，主夫妻和顺。")
    else:
        L.append("· 「阴阳交错，难期琴瑟之鸣」——世应阴阳错位，主夫妻欺凌、终朝反目。")
    if yong_wang:
        L.append("· 「用神」旺相，配偶得地、姻缘有望。")
    if yong_kp or not yongs:
        L.append("· 「如逢财鬼空亡，乃婚姻之大忌」——用神空破或不上卦，无对象、姻缘难成。")
    if yong_duo:
        L.append("· 「财官叠见，重为一度之新人」——用神两现，主再婚、多角，事有反复。")
    if shi_ying_he or (sy_rel == '生' and ys_rel == '生'):
        L.append("· 「世合应、应合世，终成种玉之缘」——两愿相合，主易成、后吉。")
    if shi_ying_chong:
        L.append("· 世应相冲克：旺世克衰应，恃强劫娶；得日辰动爻生合，赖人吹嘘可成。")
    if ji_dong:
        if nan:
            L.append("· 兄弟发动克妻财，主劫妻、争财、婚姻破财。")
        else:
            L.append("· 子孙发动克官鬼，主克夫、婚事不就。")
    if si_he:
        L.append("· 「财官动合，先私而后公」——用神动合世身，先有私情后论婚嫁。")
    if shi_kp or ying_kp:
        if shi_kp and ying_kp:
            L.append("· 「世应俱空，难遂百年之连理」——双方皆无心，勉强终不遂。")
        else:
            L.append("· 世或应空：" + ("世空我无心，" if shi_kp else "") + ("应空彼无心。" if ying_kp else ""))

    # 二、逐条
    L.append("【二、本卦婚姻逐条详断】")
    L.append(f"（1）用神·{yong_qin}爻（{yong_lbl}）")
    if yongs:
        for y in yongs:
            ex = ''
            if y['is_dong'] and y['liushen'] in ('青龙',):
                ex = '用神临青龙发动，主喜庆、貌美、恩爱'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append(f"　· 卦中不见{yong_qin}爻，{yong_lbl}之主不上卦。")
        for ln in _fushen_duan(C, yong_qin):
            L.append(ln)

    L.append("（2）世应（己与彼）生合、阴阳得位")
    L.append(_yong_yao_duan(shi, C))
    L.append(_yong_yao_duan(ying, C))
    if shi_ying_he:
        L.append("　· 世应相合（六合），两情相悦，婚易成。")
    if shi_ying_chong:
        L.append("　· 世应相冲，彼此不睦，须间爻媒人说合、日月生扶方解。")
    if shi_ying_bi:
        L.append("　· 世应比和，两不相下、亦不相伤，赖媒人与日辰撮合。")
    if sy_rel == '生' and not shi_ying_chong:
        L.append("　· 我生合彼，我家求亲，心诚；彼生合我，彼家相就。")
    L.append("　· 阴阳：" + ("世阳应阴，男家得位，吉。" if (nan and dewei)
                            else "世阴应阳，女家得位，吉。" if dewei
                            else "世应阴阳错位，主日后失序，宜调节。"))
    if yong_yy:
        L.append("　· 用神阴阳得位（" + ("妻财为阴" if nan else "官鬼为阳") + "），配身相称。")

    L.append("（3）原神·" + ("子孙（生妻财）" if nan else "妻财（生官鬼）"))
    yuan = zis if nan else cais
    if yuan:
        for y in yuan:
            if y['is_dong']:
                ex = '原神发动生用，吉'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '原神静旺，暗中生用'
            else:
                ex = '原神静衰，生用无力'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 原神不现，用神不得其生。")

    L.append("（4）忌神·" + ("兄弟（克妻财）" if nan else "子孙（克官鬼）"))
    ji = xiongs if nan else zis
    if ji:
        for y in ji:
            if y['is_dong']:
                ex = '忌神发动，克伤用神，大忌'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '忌神静旺，暗有克用之忧'
            else:
                ex = '忌神静衰，不克用，暂无害'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 忌神不现，用神不受克，吉。")

    L.append("（5）媒人·间爻（三、四爻）与庚帖·父母")
    for j in jian:
        ex = '间爻为媒人，' + ('媒人发动，主动说合' if j['is_dong'] else '媒人安静')
        if j['is_kong']:
            ex += '，媒人落空，无力'
        L.append(_yong_yao_duan(j, C, extra=ex))
    if not jian_dong:
        L.append("　· 间爻安静，须世应冲合、或日月冲起媒人，方有人出为说合。")
    if fus:
        for y in fus:
            ex = '父母为庚帖、主婚，' + ('两父母动则争盟' if len(fus) >= 2 else '')
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 父母不现，无主婚、庚帖无力。")

    L.append("（6）动爻变化吉凶")
    if nan:
        xi_ji = {'妻财': '喜', '子孙': '喜', '父母': '喜', '兄弟': '忌', '官鬼': '忌'}
        hua_img = _HUN_HUA_M
    else:
        xi_ji = {'官鬼': '喜', '妻财': '喜', '父母': '喜', '子孙': '忌', '兄弟': '忌'}
        hua_img = _HUN_HUA_F
    for ln in _bian_duan(C, xi_ji, hua_img):
        L.append(ln)

    L.append("（7）卦象格局与配偶容貌")
    sec7 = []
    for ln in _sanhe_duan(C, yong_qin, yong_wx):
        sec7.append(ln)
    for ln in _geju_duan(C, "六合主夫妻和美、姻缘易成。",
                         "六冲主夫妻离散、婚事难成，纵成不利。",
                         "动化六合，先有阻后和好，终成。",
                         "动化六冲，先成后散，终主离异。"):
        sec7.append(ln)
    # 容貌
    for y in yongs:
        s = C['st_of'](y)
        if y['liushen'] in ('青龙',) or y['wuxing'] in ('木', '金'):
            sec7.append("　· 用神临青龙、或属木金，主容貌秀丽；"
                        + ("旺则身肥、美而有才。" if s['level'] in ('旺相', '有气') else ""))
        if y['liushen'] in ('白虎', '腾蛇', '勾陈', '玄武') or y['wuxing'] in ('土', '火'):
            sec7.append("　· 用神临虎蛇勾陈玄武、或属土火，主容貌平平或丑；"
                        + ("入墓则美偏愚拙。" if s['mu'] else "衰而有扶则丑有才能。"))
    if not sec7:
        if not yongs:
            sec7.append("　· 用神伏藏未现，配偶容貌未显；本卦又非六合六冲，姻缘以用神得出、"
                        "世应生合之日为断。")
        else:
            sec7.append("　· 本卦非六合、非六冲，亦无三合，配偶容貌平和，以世应、用神旺衰生合为主。")
    for ln in sec7:
        L.append(ln)

    # 三、综合
    L.append("【三、综合断语与成婚应期】")
    zong = []
    if yongs and yong_wang and not shi_kp and not ying_kp and not shi_ying_chong:
        if dewei or shi_ying_he:
            zong.append("用神旺相、世应生合、阴阳得位，又逢相合——此乃婚姻上上之卦，姻缘易成，"
                        "夫妻恩爱，主大吉。")
        else:
            zong.append("用神旺、双方不空，然世应未得生合、阴阳未纯，须媒人撮合、日月生扶，可成，成后亦吉。")
    elif not yongs or yong_kp:
        zong.append("用神空破或不上卦，无对象、姻缘难成；旺者待填实出旬、伏神得现，衰者无望。")
    elif yong_duo:
        zong.append("用神两现，主再婚、多角或两家争婚，事有反复，须辨其旺衰取舍。")
    elif shi_kp or ying_kp:
        if shi_kp and ying_kp:
            zong.append("世应俱空，双方无心，百年之缘难遂。")
        else:
            zong.append("世或应空，一方无心，婚难成。")
    elif ji_dong:
        zong.append("忌神发动克伤用神，主劫财、争婚或克妻克夫，目前断以不吉。")
    elif shi_ying_chong:
        zong.append("世应相冲，本主难成，须得间爻媒人、日月生合两边吹嘘，方可成。")
    else:
        zong.append("用神有气而未旺，或休囚平和，主姻缘迟滞、待时，待用神逢生旺、六合、生合世应之日可成。")
    for z in zong:
        L.append("· " + z)
    yq = _yong_yingqi(C, yong_qin, yongs, fushen, verb='成婚')
    if yq:
        L.append("【成婚应期】")
        for q in yq:
            L.append("· " + q)
    L.append("（以上依《卜筮正宗·黄金策》婚姻章、总断千金赋之法推演；百年姻缘尤在双方诚意与相处，"
             "卦理仅作参考。）")
    return L


# ============================================================
# 疾病（病症·病体·医药）
# ============================================================
_BING_WX = {
    '火': '心经之症：发热、咽干、口燥',
    '水': '肾经之症：恶寒、盗汗、遗精、白浊',
    '金': '肺经之症：咳嗽、虚怯、气喘、痰多',
    '木': '肝经之症：感冒风寒、四肢不和、筋骨酸痛',
    '土': '脾经之症：虚黄、浮肿、时气、瘟疫',
}
_BING_WEI = {1: '足', 2: '腿膝', 3: '股、腰、小腹', 4: '背、胸', 5: '面、项、胸', 6: '头'}
_BING_SHEN = {
    '螣蛇': '心惊、坐卧不安，重则癫狂、惊风',
    '青龙': '酒色过度、身体虚弱',
    '勾陈': '胸满肿胀、脾胃不和',
    '朱雀': '狂言乱语、身热面赤',
    '白虎': '跌打损伤、骨痛；女人血崩血晕、产后之症（白虎血神）',
    '玄武': '色欲郁闷、阴虚',
}
_JI_HUA = {
    ('官鬼', '子孙'): '病神化子孙，鬼被药克，病退，吉',
    ('子孙', '父母'): '药化父母，回头克药，误药，凶',
    ('父母', '子孙'): '克药者化药，先阻后愈，吉',
    ('妻财', '官鬼'): '财化鬼，饮食伤复，病增，凶',
    ('兄弟', '子孙'): '兄化子孙，药得生扶，吉',
    ('兄弟', '官鬼'): '兄化鬼，病势又起，凶',
    ('官鬼', '官鬼'): '鬼化鬼，新旧两病，迁变百端',
}


def fenxi_jibing(paipan, patient='世'):
    """
    《黄金策》病症、病体、医药三章疾病专断。
    patient：'世'=自占（以世为病人，官鬼为病、子孙为药）；
             '父母'/'官鬼'/'妻财'/'子孙'=代占（以该六亲为病人，原神生用、忌神克用）。
    """
    C = _setup(paipan)
    L = _head(paipan)
    gong_wx = C['gong_wx']; shi = C['shi']; ying = C['ying']
    guans = C['byqin']['官鬼']; zis = C['byqin']['子孙']; cais = C['byqin']['妻财']
    zizhan = (patient == '世')

    # 用神（病人）
    if zizhan:
        yongs = [shi]; yong_qin = '世爻（病人自身）'; yong_wx = shi['wuxing']
    else:
        yong_qin = patient; yongs = C['byqin'][patient]
        yong_wx = _liuqin_wuxing(gong_wx, patient)
    yongshen = find_fushen(paipan, patient) if (not zizhan and not yongs) else None

    # 原神（生用）、忌神（克用），按五行
    yuan_wx = next(x for x in WUXING_SHENG if WUXING_SHENG[x] == yong_wx)
    ji_wx = next(x for x in WUXING_KE if WUXING_KE[x] == yong_wx)
    yuans = [y for y in C['yx'] if y['wuxing'] == yuan_wx]
    jis = [y for y in C['yx'] if y['wuxing'] == ji_wx]
    yuan_dong = any(y['is_dong'] for y in yuans)
    ji_dong = any(y['is_dong'] for y in jis)
    # 原神/忌神是否有力：空破、休囚无气则暂不生克，待时（动而空破，出旬填实方应）
    yuan_li = [y for y in yuans if y['is_dong'] and _youli(y, C)]
    ji_li = [y for y in jis if y['is_dong'] and _youli(y, C)]
    ji_kp_dong = [y for y in jis if y['is_dong'] and not _youli(y, C)]
    yuan_li_dong = bool(yuan_li)
    ji_li_dong = bool(ji_li)

    # 病神（官鬼）、医药（子孙）
    guan_sts = [(y, C['st_of'](y)) for y in guans]
    guan_wang = any(s['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po']
                    for y, s in guan_sts)
    guan_kp = any(y['is_kong'] or y['is_po'] for y in guans)
    guan_dong = any(y['is_dong'] for y in guans)
    zi_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in zis)
    zi_kp = (not zis) or all(y['is_kong'] or y['is_po'] or C['st_of'](y)['level'] in ('无气', '休囚')
                             for y in zis)
    zi_dong = any(y['is_dong'] for y in zis)

    # 病人状态
    yong = yongs[0] if yongs else None
    yong_s = C['st_of'](yong) if yong else None
    yong_kp = yong is not None and (yong['is_kong'] or yong['is_po'])
    yong_mu = yong_s is not None and bool(yong_s['mu'])
    yong_ruo = yong_s is not None and yong_s['level'] in ('无气', '休囚')
    # 官鬼（病神）与病人（世/用）的关系：持、克、生、比——决定病与我有情无情
    def grel_yong(y):
        if zizhan and y['is_shi']:
            return '持世'
        return get_wuxing_relation(y['wuxing'], yong_wx)
    guan_chishi = zizhan and any(y['is_shi'] for y in guans)
    guan_keshi = any(grel_yong(y) == '克' for y in guans)
    guan_shengshi = any(grel_yong(y) == '生' for y in guans)
    # 病人化鬼、化回头克
    yong_bian_xiong = False
    if yong and yong['is_dong']:
        by = _bian_by_pos(C['paipan'], yong['pos'])
        if by:
            rel = get_wuxing_relation(by['wuxing'], yong['wuxing'])
            if rel == '克' or get_liuqin(gong_wx, by['wuxing']) == '官鬼':
                yong_bian_xiong = True

    # 动变喜忌（按六亲对病人的五行生克；官鬼生世则非"病克身"，自动归喜）
    xi_ji = {}
    for q in LIUQIN:
        qwx = _liuqin_wuxing(gong_wx, q)
        r = get_wuxing_relation(qwx, yong_wx)
        xi_ji[q] = '喜' if r in ('同', '生', '被克') else '忌'

    # ---------- 一、经典 ----------
    L.append("【一、《黄金策》病症·病体·医药论疾病（经典）】")
    L.append("· 症候总纲：「凡占疾症，以官鬼爻为轻重；得病根由，独发之爻亦可推之。」")
    L.append("· 安危总纲：「欲决病痊，当究福神之动静；要知命尽，须详鬼煞之旺衰。」福神，其义轻于"
             "子孙、重于原神；鬼煞，其理在于忌神、而不在于官鬼。凡占病遇原神旺动，即使用神空破伏藏，"
             "其病可愈；遇忌神旺动，即使用神出现不空破，禄命当尽。")
    L.append("· 六亲取用：" + ("自占以世爻为病人，官鬼为病神、子孙为医药（解神），应爻为医生。"
                             "原神（生世者）旺则生，忌神（克世者）动则危。"
                             if zizhan else
                             f"代占以「{yong_qin}」为病人，以生「{yong_qin}」之爻为原神、"
                             f"克「{yong_qin}」之爻为忌神；推占父母、丈夫病，不宜子孙发动。"))
    L.append("· 医药总纲：「病不求医生全者寡，药不对症枉死者多，欲择善者而从之，须就蓍人而问也。"
             "应作医人，空则䏦亡而不遇；子为药饵，伏则扞格以无功」——以子孙爻为药饵、以应爻为医生，"
             "子孙受伤墓绝或官鬼生旺，是药不对症、不能去病；应爻旬空，是医生难遇、用药无效。")
    # 固定核心经文（每卦必列，先通论）
    _JB_JING = [
        ("人孰无常？疾病无常；事孰为大？死生为大", "凡占疾症，以官鬼爻为轻重：官鬼衰则病轻、旺则病重，"
                                    "动则煎迫身体、安静则安卧；得病根由，独发之爻亦可推之。"),
        ("既明症候，当决安危……先看子孙，最喜生扶拱合", "子孙能克制鬼煞，古人谓之解神、福德，占病又为"
                                    "医药；卦中无子孙则财鬼无制，服药无效、祷神不灵。唯推占父母、丈夫病"
                                    "不宜子孙发动，动则伤克夫星、又克父母之原神。"),
        ("欲决病痊，当究福神之动静；要知命尽，须详鬼煞之旺衰", "福神义在子孙、重于原神，鬼煞理在忌神、"
                                    "不专在官鬼：原神旺动则用神空破伏藏亦愈，忌神旺动则用神不空破、禄命亦尽。"),
        ("官临福衰，药饵轻而病重", "官鬼无气、子孙旺相，是药能胜病，服之有效；若子孙休囚、官鬼旺相，"
                                  "是药轻病重，服之无功。"),
        ("鬼动卦中，眼下速难取效", "占药要鬼爻安静无气，若鬼发动，纵有良药，眼下取效亦迟；待鬼爻入墓、"
                                  "逢绝之日用药，方有效。"),
        ("世持鬼爻，病纵轻而难疗", "自占病最怕官鬼持世，病难脱体；待子孙发动、官鬼受克之日，方可言愈。"),
        ("鬼伏卦中病来莫觉，官藏世下症起如前", "官鬼不现，必是隐伏，得症不知何由；官鬼伏于世下，"
                                              "必是旧症复发、不时举发。"),
        ("用绝逢生，危而有救", "用神逢绝，得卦中动爻、日辰生合，是绝处逢生、凶中回吉，虽危有救；"
                              "唯用神太弱，亦主病久体虚。"),
        ("主空无救，须防中道而殂", "主象（用神、病人）墓绝空破，得卦中动爻、日辰生扶拱合者无妨，"
                                  "无救者必死；救者，生扶拱合也。"),
        ("日加福去生扶，药医则愈", "日辰临子孙，生扶拱合用神，必得药力而愈；若子孙化出回头克、化官鬼，"
                                  "服药不效。"),
        ("福化忌爻，病势增加于小愈", "子孙发动本制官鬼，若化回头克、化出官鬼，必因病势稍愈时不谨慎，"
                                    "以致复加沉重。"),
        ("应临官鬼，防投增病之药汤", "应爻为医生，应临官鬼必非良医，或临忌神、化官鬼，俱不宜用此人之药；"
                                    "应临子孙乃专门医士，可托。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _JB_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    if guan_wang and (guan_keshi or guan_chishi):
        L.append("· 官鬼旺相、又克世或持世，病神伤身，病势重；「鬼化长生，日下正当沉重」，发动则烦躁。")
    elif guan_wang and guan_shengshi:
        L.append("· 官鬼虽旺，然不克病人、反生之，病虽有而与我有情，主病轻、渐有转机。")
    elif guan_dong and not guan_wang:
        L.append("· 官鬼发动而不旺，病在变化，化进神则重、化退神则减。")
    if not guans:
        L.append("· 「鬼伏卦中，病来莫觉」——官鬼不现，病隐伏、根因不知；伏于世下，必旧症复发。")
    if zi_wang and (guan_keshi or guan_chishi):
        L.append("· 子孙旺相，医药得力，能制克身之鬼，服药有效。")
    elif zi_wang:
        L.append("· 子孙旺相，药有其力；官鬼既不克身，药力平和，调理为主。")
    if zi_kp:
        L.append("· 子孙空绝或不上卦，是无药、药不效，「服药无效、祷神不灵」。")
    if yuan_li_dong:
        L.append("· 原神（生病人）有力发动，病人有救，病可愈。")
    if ji_li_dong:
        L.append("· 忌神（克病人）有力发动，病人受克，病危。")
    if ji_kp_dong:
        zs = '、'.join(y['zhi'] for y in ji_kp_dong)
        L.append("· 忌神「" + zs + "」虽动，然旬空、月破或休囚无气，当前不能克病人，病暂不重；"
                 "待出旬填实、得令之日方有克，须防其日。")
    if guan_chishi:
        L.append("· 「世持鬼爻，病纵轻而难疗」——官鬼持世，病难脱体，待子动、鬼受克之日。")

    # ---------- 二、逐条详断 ----------
    L.append("【二、本卦疾病逐条详断】")

    L.append("（1）症候·病神官鬼（病在何处、何因）")
    if guans:
        # 取最有力官鬼
        gy = max(guans, key=lambda y: (y['is_shi'], y['is_dong'], C['st_of'](y)['score']))
        gs = C['st_of'](gy)
        gr = grel_yong(gy)
        if gr in ('克', '持世'):
            qq = '（鬼克/持病人，病在身，重则凶）'
        elif gr == '生':
            qq = '（鬼不克、反生病人，病有情，主轻）'
        else:
            qq = '（鬼与病人比和，症轻）'
        if gy['is_kong'] or gy['is_po']:
            qq = '（鬼空、月破，病神暂不发力，症轻；待填实、出破）'
        L.append("　· 五行病象：" + _BING_WX.get(gy['wuxing'], '') + qq)
        L.append("　· 部位：病在" + _BING_WEI.get(gy['pos'], '') + "（官临" + num_to_cn(gy['pos'])
                 + "爻" + gy['wuxing'] + "）" + "；又《易》以乾头、坤腹、兑喉、艮手、震足、巽股、"
                 "坎耳、离目，可参看本卦上下卦。")
        if gy['liushen']:
            L.append("　· 六神病象：官临" + gy['liushen'] + "，" + _BING_SHEN.get(gy['liushen'], '') + "。")
        if len(guans) >= 2:
            L.append("　· 卦中两现官鬼，主新旧两病、内外兼感，或症候迁变。")
        for y in guans:
            L.append(_yong_yao_duan(y, C))
    else:
        fs = find_fushen(paipan, '官鬼')
        if fs:
            L.append(f"　· 官鬼不现，伏于{num_to_cn(fs['pos'])}爻「{fs['feishen']['liuqin']}"
                     f"{fs['feishen']['zhi']}」之下——病隐伏、根因不知"
                     + ("，伏于世下，必旧症复发。" if fs['pos'] == shi['pos'] else "。"))
            L.append("　· 伏病因由：伏财伤饥失饱、伏子酒醉耽淫、伏父劳心忧虑、伏兄口舌争竞。")
        else:
            L.append("　· 卦无官鬼，病神不现，邪气已退（新病），或病非鬼祟、药石易为。")

    L.append("（2）病人·" + yong_qin + "（安危之本）")
    if yongs:
        L.append(_yong_yao_duan(yong, C))
        if yong_bian_xiong:
            L.append("　· 病人动而化出官鬼、或化回头克，无日月解救，目前必见倾危，大凶。")
        if yong_mu:
            L.append("　· 病人入墓，「神思困而不清」，主昏沉，待冲墓、出墓。")
        if guan_chishi and zizhan:
            L.append("　· 官鬼持世，病在己身、难脱体，待鬼受克、子动之日。")
    else:
        L.append(f"　· 卦中不见「{yong_qin}」，病人之主不上卦。")
        if yongshen:
            for ln in _fushen_duan(C, patient):
                L.append(ln)
        L.append("　· 「主象伏藏，定主迁延岁月」——病人伏藏，待值日、久病待值年值月方愈。")

    L.append("（3）医药·子孙爻（药饵、解神，制鬼）")
    zhen_bing = guan_keshi or guan_chishi
    if zis:
        for y in zis:
            if y['is_dong']:
                if not _youli(y, C):
                    ex = '子孙动而空破，药虽有而暂不得力，待填实'
                elif zhen_bing:
                    ex = '子孙发动，药能制克身之鬼，吉'
                else:
                    ex = '子孙发动，官鬼本不克身，药以调理为主；防过剂伤原神'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '子孙静旺，药有其力，待发动用之'
            else:
                ex = '子孙休囚，药轻病重，无功'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 子孙不现，无药、求医不得力，待子值日。")

    L.append("（4）原神（生病人）与忌神（克病人）")
    if yuans:
        for y in yuans:
            if y['is_dong']:
                ex = '原神，' + ('有力发动生病人，大吉' if _youli(y, C)
                                else '发动而空破，生力暂弱，待时')
            else:
                ex = '原神，安静，待生旺生扶'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 原神不现，病人不得生扶。")
    if jis:
        for y in jis:
            if y['is_dong']:
                if _youli(y, C):
                    ex = '忌神，有力发动克病人，大忌'
                else:
                    ex = ('忌神，动而空破（旬空/月破），当前不能克病人，待填实「'
                          + y['zhi'] + '日」方有克，须防')
            else:
                ex = '忌神，静而旺，暗有克伐之忧'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 忌神不现，病人不受克，吉。")

    L.append("（5）医生·应爻与用药宜忌")
    L.append(_yong_yao_duan(ying, C))
    if ying['is_kong']:
        L.append("　· 应爻空亡，医生非它出不来，定用药无效，须另觅良医。")
    if any(y['is_shi'] is False and y['pos'] == ying['pos'] and y['liuqin'] == '官鬼' for y in guans):
        L.append("　· 应临官鬼，非良医，更防投增病之药。")
    if ying['liuqin'] == '子孙':
        L.append("　· 应临子孙，乃专门医士，可托。")
    if zis:
        zy = max(zis, key=lambda y: C['st_of'](y)['score'])
        L.append("　· 看子孙何爻，知医在何方：子北、丑寅东北、卯东、午南、酉西；"
                 f"本卦子孙临「{zy['zhi']}」，可向其方位求医。")
    # 用药寒热、饮食
    if guans:
        gy = max(guans, key=lambda y: (y['is_shi'], y['is_dong'], C['st_of'](y)['score']))
        if gy['wuxing'] in ('火', '土'):
            L.append("　· 「察官爻而用药，火土寒凉」——火土鬼病热，宜寒凉药。")
        else:
            L.append("　· 金水官鬼病寒，宜温热之剂。")
    if not cais or any(y['is_kong'] for y in cais):
        L.append("　· 「卦内无财，饮食不纳」——财空或不现，不思饮食。")
    else:
        if guans:
            gy = max(guans, key=lambda y: (y['is_shi'], y['is_dong'], C['st_of'](y)['score']))
            ji_kou = {'水': '忌鱼鲜生冷', '木': '忌动风之物', '火': '忌炙煿热物',
                      '金': '忌坚硬咸物', '土': '忌油腻滑物'}
            L.append("　· 饮食所忌：鬼属" + gy['wuxing'] + "，" + ji_kou.get(gy['wuxing'], '') + "。")

    L.append("（6）动爻变化吉凶")
    for ln in _bian_duan(C, xi_ji, _JI_HUA):
        L.append(ln)

    L.append("（7）卦象格局")
    sec7 = []
    for ln in _geju_duan(C, "六合主病气缠绵、不易顿解。",
                         "近病（新病）逢六冲则散，主速愈；久病逢六冲则凶。",
                         "动化六合，病势缠结。",
                         "动化六冲，近病主散、久病主危。"):
        sec7.append(ln)
    if not sec7:
        sec7.append("　· 本卦非六合、非六冲，病势以病人、官鬼、原神、忌神旺衰动静为主。")
    for ln in sec7:
        L.append(ln)

    # ---------- 三、综合与应期 ----------
    L.append("【三、综合断语（安危）与病愈应期】")
    zong = []
    yong_ok = (yong_s is not None and yong_s['level'] in ('旺相', '有气')) or yuan_li_dong
    kpz = '、'.join(y['zhi'] for y in ji_kp_dong)
    if yong_bian_xiong:
        zong.append("病人动而化鬼、化回头克，无日月动爻解救，「目前必见倾危」，主大凶。")
    elif yongs:
        if ji_li_dong and not (yuan_li_dong or zi_wang):
            zong.append("忌神（克病人）有力发动，病人衰弱、无救，「禄命当尽」之象，主危；"
                        "急需制忌神、扶病人。")
        elif ji_li_dong and (yuan_li_dong or zi_wang):
            zong.append("虽忌神发动克病人，然病人得原神生扶、或医药制之，主先凶后解，可愈，"
                        "待忌神受克、原神值日。")
        elif yuan_li_dong and ji_kp_dong:
            zong.append("病人得原神有力动生，忌神「" + kpz + "」动而空破，当前不能克病人——"
                        "目前有转机、可愈；唯须防忌神出旬填实、得令之日（" + kpz + "日）病势反复，"
                        "药宜早备。")
        elif yuan_li_dong and (yong_ruo or yong_kp or yong_mu):
            zong.append("病人虽休囚、空破或入墓，原神有力发动相生，「绝处逢生」，其病可愈，待生扶之日。")
        elif yuan_li_dong or (yong_ok and not ji_li_dong and (zi_wang or zi_dong)):
            zong.append("病人得原神生扶、医药得力，忌神不克——病虽现，可治，主愈，吉。")
        elif ji_kp_dong:
            zong.append("忌神「" + kpz + "」动而空破，当前不能克病人，病暂不重；待出旬填实、"
                        "得令之日（" + kpz + "日）方有克，须防。")
        elif guan_wang and (guan_keshi or guan_chishi) and zi_kp:
            zong.append("病神旺、克身或持世，医药子孙空绝，「药轻病重」，难治，待子旺、鬼受克之日方有转机。")
        elif guan_chishi:
            zong.append("官鬼持世，病难脱体，待子动、鬼受克墓绝之日方愈。")
        elif yong_ok and not ji_li_dong:
            zong.append("病人有气、不受克，病势轻，调理得宜，待生旺、子动之日愈。")
        else:
            zong.append("病人、病神各有强弱，吉凶未定，以原神、医药（子孙）旺动为愈，忌神、病神旺动为危。")
    else:
        if yongshen and yuan_li_dong:
            zong.append("病人不上卦、伏藏，原神有力发动，待伏神得现、生扶之日可愈，属先凶后解。")
        elif guan_wang and zi_kp:
            zong.append("病神旺、医药无，病人之主又伏藏，主危，急需良医良药。")
        else:
            zong.append("病人伏藏，症候迁延，待值日、值月方愈。")
    for z in zong:
        L.append("· " + z)

    # 应期
    if yongs:
        yq = _yong_yingqi(C, yong_qin.replace('（病人自身）', ''), yongs, yongshen, verb='病愈')
        if yq:
            L.append("【病愈应期】")
            for q in yq:
                L.append("· " + q)
    # 病神受克日（愈）/ 忌神值日（危）
    if guans:
        gy = max(guans, key=lambda y: (y['is_shi'], y['is_dong'], C['st_of'](y)['score']))
        L.append("· 病愈又可候：子孙（医药）值日、或官鬼入墓绝受克之日；"
                 f"本病鬼{gy['zhi']}，墓于{_MUKU[gy['wuxing']]}、绝于{_JUEDI[gy['wuxing']]}，"
                 "至其日病退。")
    if ji_li_dong or ji_kp_dong:
        jj = max(jis, key=lambda y: (y['is_dong'], C['st_of'](y)['score']))
        if ji_kp_dong and not ji_li_dong:
            L.append(f"· 须防：忌神「{jj['zhi']}」出旬填实、得令之日，病势反复；"
                     "得日月动爻冲克忌神可免。")
        else:
            L.append(f"· 须防：忌神值日、得令之日，即「{jj['zhi']}」前后；"
                     "得日月动爻冲克忌神可免。")
    L.append(_YQ_TAIL)
    L.append("（以上依《卜筮正宗·黄金策》病症、病体、医药三章及总断千金赋推演；有病应及时就医，"
             "卦理仅作参考，切勿因此延误诊治。）")
    return L


# 阳支 / 阴支（产育定男女：子孙阳爻旺相为男，阴爻休囚为女）
_YANG_ZHI = set("子寅辰午申戌")
_YIN_ZHI = set("丑卯巳未酉亥")


# ============================================================
# 子女（产育）
# ============================================================
_ZINV_HUA = {
    ('妻财', '子孙'): '财化子孙，产母化出儿女，分娩即当勿药之喜，大吉',
    ('子孙', '妻财'): '子孙化财，儿女化出回头之生，子易养，吉',
    ('官鬼', '子孙'): '鬼化子孙，忧化解为福德，先忧后喜，吉',
    ('子孙', '官鬼'): '子孙化官鬼，福被伤而胎化鬼，子当屈死腹中，大凶',
    ('父母', '子孙'): '父母化子孙，忌神化用，然父已先动克子，先险后安',
    ('子孙', '父母'): '子孙化父母，儿女化回头之克，难为厥子，凶',
    ('兄弟', '妻财'): '兄弟化财，产母受克，防产母不安',
    ('父母', '官鬼'): '父母化官鬼，忧神并起，难产、伤子，凶',
}


def fenxi_zinv(paipan):
    """《黄金策·产育》子女（生产、求子息）专断：子孙为占产用神，妻财为原神（产母），
    父母为忌神（克子孙），官鬼为忧（病、血光）。"""
    C = _setup(paipan)
    L = _head(paipan)
    p = C['paipan']; shi = C['shi']; ying = C['ying']; gong_wx = C['gong_wx']
    zis = C['byqin']['子孙']; cais = C['byqin']['妻财']
    fus = C['byqin']['父母']; guans = C['byqin']['官鬼']; xiongs = C['byqin']['兄弟']
    yong_wx = _liuqin_wuxing(gong_wx, '子孙')

    fushen = find_fushen(paipan, '子孙') if not zis else None

    zi_sts = [(y, C['st_of'](y)) for y in zis]
    zi_wang = any(s['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po']
                  for y, s in zi_sts)
    zi_kp = any(y['is_kong'] or y['is_po'] for y in zis)
    fu_dong = any(y['is_dong'] and _youli(y, C) for y in fus)
    fu_kp = (not fus) or all(y['is_kong'] or y['is_po'] for y in fus)
    guan_dong = any(y['is_dong'] and _youli(y, C) for y in guans)
    cai_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in cais)
    cai_kp = (not cais) or all(y['is_kong'] or y['is_po'] for y in cais)
    xiong_dong = any(y['is_dong'] and _youli(y, C) for y in xiongs)

    # 男女：取最有力的子孙爻（阳支为男、阴支为女），临青龙更吉
    def zrel(y):
        if y['is_shi']:
            return '持世'
        return get_wuxing_relation(y['wuxing'], shi['wuxing'])
    zi_keshi = any(zrel(y) == '克' for y in zis)
    zi_chongshi = any(LIUCHONG.get(y['zhi']) == shi['zhi'] for y in zis)
    zi_long = False
    if zis:
        zy = max(zis, key=lambda y: (y['is_dong'], C['st_of'](y)['score']))
        is_nan = (zy['zhi'] in _YANG_ZHI)
        zi_long = zy['liushen'] == '青龙'
        if is_nan and (zi_wang or zi_long):
            nannv = '男（子孙临阳支%s，旺相/青龙，主俊秀男儿）' % zy['zhi']
        elif (not is_nan) and not zi_wang:
            nannv = '女（子孙临阴支%s，休囚，主女儿）' % zy['zhi']
        elif is_nan:
            nannv = '偏男（子孙阳支%s）' % zy['zhi']
        else:
            nannv = '偏女（子孙阴支%s）' % zy['zhi']
    else:
        nannv = '子孙不现，须查伏神定男女'

    # ---------- 一、经典 ----------
    L.append("【一、《黄金策·产育》论子女（经典）】")
    L.append("· 总纲：「盖得阴阳交感，方能胎孕相生，先看子孙，便知男女。阳为男子，掌中探见一枝新；"
             "阴是女儿，门右喜看弧蜕设」——子孙为占产用神，旺相单重为阳爻是男，休囚交拆为阴爻是女。")
    L.append("· 六亲取用：子孙爻为占产、占子息之用神（儿女）；妻财为原神、为产母（生子孙）；"
             "父母为忌神（克子孙，主伤子、难产）；官鬼为忧神（疾病、血光）；兄弟发动则克妻财，不利产母。")
    _ZN_JING = [
        ("主星生旺，当生俊秀之肥儿；命曜休囚，必产委糜之弱子",
         "子孙生旺，子必肥大，异日主俊秀不凡；休囚无气，子必弱小，异日主萎靡不振。"),
        ("如无福德，莫究胎爻",
         "用神（子孙）不出现，当查伏于何爻之下，以伏神旺衰吉凶断之，不必拘泥胎爻。"),
        ("双胎双福必双生，一克一刑终一梦",
         "卦有两重子孙、又有两重胎爻，纵不发动亦主双生；卦无子孙、胎爻又被月建日辰动爻刑克，"
         "大凶，一场春梦，言其子必亡。"),
        ("胎临官鬼，怀妊便有采薪忧；财化子孙，分娩即当勿药喜",
         "鬼临胎爻主孕妇有疾；若财合福爻、或财化子孙，则分娩安泰，不药而喜。"),
        ("妻财一位喜见持持，胎福二爻怕逢伤害",
         "占产以财为产母、福为儿女，皆喜月建日辰动爻生扶合助，则产母安、子易养；"
         "见刑冲克害、化入死墓空绝，则产母多灾、子难养。"),
        ("虎作血神，值事交重胎已破",
         "白虎为血神，若临子孙或胎爻发动，其胎已破；临财爻发动亦然。"),
        ("龙为喜气，遇胎发动日将临",
         "占产以青龙为喜，若在胎福财爻上动者，生期已速，必当日临盆。"),
        ("福遇龙空，胎动乃堕胎虚喜",
         "福临青龙却空亡受制，又见胎爻发动或被日辰动爻冲，乃堕胎虚喜。"),
        ("福被伤而胎仍化鬼，子当屈死于腹中",
         "子孙墓绝、又被日月动爻刑冲克害者大凶；或胎临官鬼、动化鬼，必是死胎。"),
        ("兄动兮不利其妻，父兴兮难为厥子",
         "兄动则克妻财（产母不安），父动则克子孙（难为厥子）；夫卜妻产，见兄动产母不安，"
         "见父动难为其子。"),
        ("用在空亡逢恶煞，何妨坐草之虞",
         "父爻发动本克子孙，若福爻得月建日辰生扶、或避空不受克，谓之无虞。"),
        ("克世克身诞生日迫，不冲不发产日时迟",
         "子孙胎爻冲克身世，生期以速，当日可断；胎福不动又无暗冲，必然迟缓，待冲月日时方分娩。"),
        ("胎福齐兴官父合，临产难生",
         "胎福二爻发动本主易生，若被官鬼、父母动爻合住或日辰合住，皆主临产难生，待冲破日时方娩。"),
        ("阳福会青龙，无异桂庭之秀子；阴孙非月建，何殊桃洞之仙姬",
         "子孙临月建、青龙或月建带青龙生合子孙者，必是男喜，后主俊秀聪明；子孙非月建日辰、"
         "又无月日生之、临阴象阴爻者，必是女。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _ZN_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    L.append("· 本卦子孙之象：" + nannv + "。")
    if zi_wang and cai_wang and not fu_dong:
        L.append("· 「主星生旺，当生俊秀之肥儿」，又得妻财（产母）生扶、父母不克——母子平安，子易养成。")
    if not zis and fushen:
        L.append("· 「如无福德，莫究胎爻」——子孙不现，查伏神以断子女有无、吉凶。")
    if fu_dong:
        L.append("· 「父兴兮难为厥子」——父母爻有力发动，克伤子孙，主伤子、难产、子难养，大忌。")
    if guan_dong and not zi_wang:
        L.append("· 「胎临官鬼，怀妊便有采薪忧」「福被伤而胎仍化鬼，子当屈死于腹中」——"
                 "官鬼有力发动、子孙无气，主孕妇有疾、胞胎不安，须防。")
    if guan_dong and cai_wang:
        L.append("· 「财化子孙，分娩即当勿药喜」——虽官鬼发动有忧，然财爻旺相、福神有根，分娩安泰。")
    if zi_kp and zis:
        L.append("· 子孙空亡、月破，主儿女之福不实，旺者待填实出旬，衰者主子息艰难。")
    if xiong_dong:
        L.append("· 「兄动兮不利其妻」——兄弟发动克妻财，主产母不安、费财。")
    if (zi_keshi or zi_chongshi) and zi_wang:
        L.append("· 「克世克身诞生日迫」——子孙旺而动冲克身世，生期已速，当日可待。")
    if zi_long:
        L.append("· 「龙为喜气，遇胎发动日将临」——青龙临子孙，临产之喜，生期近。")
    if not (zi_keshi or zi_chongshi) and zis and not any(y['is_dong'] for y in zis):
        L.append("· 「不冲不发产日时迟」——子孙安静、不冲身世，产期尚缓，待逢冲月日时。")

    # ---------- 二、逐条详断 ----------
    L.append("【二、本卦子女逐条详断】")
    L.append("（1）用神·子孙爻（儿女）与男女之辨")
    if zis:
        for y in zis:
            xx = []
            if y['zhi'] in _YANG_ZHI:
                xx.append('阳支，子孙旺相单重为男' if C['st_of'](y)['level'] in ('旺相', '有气')
                          else '阳支而休囚，男女须再参青龙月建')
            else:
                xx.append('阴支，休囚交拆为女' if C['st_of'](y)['level'] in ('无气', '休囚')
                          else '阴支而旺相，男女须再参青龙月建')
            if y['liushen'] == '青龙':
                xx.append('临青龙，主喜气、俊秀')
            if y['liushen'] == '白虎':
                xx.append('临白虎血神，防血光、胎破')
            if len(zis) >= 2:
                xx.append('卦中两重子孙，主双生或子女多')
            L.append(_yong_yao_duan(y, C, extra='；'.join(xx)))
    else:
        L.append("　· 卦中不见子孙爻，儿女之主不上卦。")
        for ln in _fushen_duan(C, '子孙'):
            L.append(ln)

    L.append("（2）原神·妻财爻（产母，生子孙）")
    if cais:
        for y in cais:
            L.append(_yong_yao_duan(y, C))
    else:
        L.append("　· 妻财不现，产母之爻伏藏，子失其生源，子息较难。")

    L.append("（3）忌神·父母爻（克子孙，主伤子难产）")
    if fus:
        for y in fus:
            if y['is_dong']:
                ex = '父母发动克子孙，「难为厥子」，主伤子、难产，大忌' if _youli(y, C) \
                     else '父母动而空破，暂不克子，待填实须防'
            elif C['st_of'](y)['level'] in ('旺相', '有气'):
                ex = '父母静旺，暗有克子之势，待发动则伤'
            else:
                ex = '父母休囚，不克子孙，无碍'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 父母不现，克子之神不兴，子易养成，吉。")

    L.append("（4）忧神·官鬼（疾病、血光）与兄弟（克产母）")
    if guans:
        for y in guans:
            if y['is_dong']:
                ex = '官鬼发动，主孕妇有疾、忧惊、血光' if _youli(y, C) \
                     else '官鬼动而空破，忧而不实'
            else:
                ex = '官鬼安静，忧疑轻'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 官鬼不现，无疾病、血光之忧。")
    if xiongs:
        for y in xiongs:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='兄弟发动克妻财，主产母不安、耗财'))
    else:
        L.append("　· 兄弟不现，产母不受克。")

    L.append("（5）动爻变化吉凶")
    for ln in _bian_duan(C, {'子孙': '喜', '妻财': '喜', '官鬼': '忌', '父母': '忌', '兄弟': '忌'},
                         _ZINV_HUA):
        L.append(ln)

    L.append("（6）卦象格局")
    for ln in _sanhe_duan(C, '子孙', yong_wx):
        L.append(ln)
    for ln in _geju_duan(C, "六合主怀胎安稳、子易养成。",
                         "六冲主胎动不安、子息难成，占产逢冲亦主速生。",
                         "动化六合，先险后安。",
                         "动化六冲，占产主速生，然子息难留。"):
        L.append(ln)

    # ---------- 三、综合与应期 ----------
    L.append("【三、综合断语与分娩应期】")
    zong = []
    if not zis:
        if fushen:
            _help = []
            if get_wuxing_relation(DIZHI_WUXING[C['yue']], fushen['wuxing']) in ('同', '生'):
                _help.append('月建')
            if get_wuxing_relation(DIZHI_WUXING[C['ri']], fushen['wuxing']) in ('同', '生'):
                _help.append('日辰')
        else:
            _help = []
        if fushen and _help:
            zong.append("卦中无子孙，然伏子得%s生扶，「如无福德，莫究胎爻」，待伏神出现、冲开飞神之日"
                        "方得子息，属先无后有。" % '、'.join(_help))
        else:
            zong.append("卦无子孙、伏子又不得时令，子息艰难，宜静养待时，多积德行善以求。")
        if guan_dong:
            zong.append("卦中官鬼发动，「胎临官鬼，怀妊便有采薪忧」，主孕期有疾、临产忧惊，宜加意调护、"
                        "按时产检；伏子待引，官鬼之动未必即伤子，然忧惊不可不防。")
        if xiong_dong:
            zong.append("兄弟发动克妻财（产母），「兄动兮不利其妻」，主产母不安、耗费。")
        if fu_dong:
            zong.append("父母发动克子孙，「父兴兮难为厥子」，纵得子亦防难养。")
    else:
        if zi_wang and cai_wang and not fu_dong and not (guan_dong and not zi_wang):
            zong.append("子孙旺相、妻财（产母）生扶、父母不克，官鬼不肆——此乃产育、子息之吉卦，"
                        "母子平安，孩子俊秀易养。")
        elif fu_dong and not zi_wang:
            zong.append("父母爻有力发动克子孙，「父兴兮难为厥子」，主伤子、难产、子难养，"
                        "须待父母受克、子孙逢值之日方解。")
        elif guan_dong and zi_kp:
            zong.append("官鬼发动、子孙空破，「福被伤而胎仍化鬼」，胞胎、产妇可忧，须防；"
                        "得财爻生合子孙方有救。")
        elif zi_kp:
            zong.append("子孙空亡、月破，儿女之福不实，旺者待填实出旬可得，衰者主子息迟、虚喜。")
        elif guan_dong:
            zong.append("官鬼发动，主孕妇有疾、临产忧惊；所幸子孙有根、得财生扶，「分娩即当勿药喜」，"
                        "先忧后吉。")
        else:
            zong.append("子孙平和有气，无父母、官鬼之克，主子息平稳，产期待子孙逢冲、逢值之日。")
    for z in zong:
        L.append("· " + z)

    yq = _yong_yingqi(C, '子孙', zis, fushen, verb='分娩/得子')
    if yq:
        L.append("【分娩应期】")
        for q in yq:
            L.append("· " + q)
    L.append("（以上依《卜筮正宗·黄金策》产育章之法推演，为软件据卦理之分析；生育之事顺遂自然，"
             "务必按时产检、就医院分娩，卦理仅作参考。）")
    return L


# ============================================================
# 出行（出行、行人之理，散见商贾章、逃亡章）
# ============================================================
def fenxi_chuxing(paipan):
    """出行专断：世为出行人，应为地头/彼处，五爻为道路；官鬼为途中灾，子孙为福德解神，
    妻财为盘缠利息，父母为行李舟车，兄弟为同伴耗财。六冲、游魂主速行，六合、归魂主牵绊、行不成。"""
    C = _setup(paipan)
    L = _head(paipan)
    p = C['paipan']; shi = C['shi']; ying = C['ying']
    guans = C['byqin']['官鬼']; zis = C['byqin']['子孙']; cais = C['byqin']['妻财']
    fus = C['byqin']['父母']; xiongs = C['byqin']['兄弟']
    yao5 = C['yx'][4]   # 五爻为道路

    def srel_to_shi(y):
        if y['is_shi']:
            return '持世'
        return get_wuxing_relation(y['wuxing'], shi['wuxing'])
    guan_keshi = any(srel_to_shi(y) == '克' for y in guans)
    guan_dong_li = any(y['is_dong'] and _youli(y, C) for y in guans)
    guan_yao5 = (yao5['liuqin'] == '官鬼') and yao5['is_dong'] and _youli(yao5, C)
    guan_chishi_dong = any(y['is_shi'] and y['is_dong'] and _youli(y, C) for y in guans)
    zi_dong = any(y['is_dong'] and _youli(y, C) for y in zis)
    zi_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in zis)
    shi_s = C['st_of'](shi)
    shi_wang = shi_s['level'] in ('旺相', '有气')
    # 世应关系
    ying_rel = get_wuxing_relation(ying['wuxing'], shi['wuxing'])
    shi_rel = get_wuxing_relation(shi['wuxing'], ying['wuxing'])
    you_hun = (p['gongwei'] == '游魂')
    gui_hun = (p['gongwei'] == '归魂')
    liu_chong = p['name'] in LIUCHONG_GUA
    liu_he = p['name'] in LIUHE_GUA
    bian_chong = bool(p['bian_gua'] and p['bian_gua']['name'] in LIUCHONG_GUA)
    bian_he = bool(p['bian_gua'] and p['bian_gua']['name'] in LIUHE_GUA)

    # ---------- 一、经典 ----------
    L.append("【一、《黄金策》论出行（经典）】")
    L.append("· 说明：《黄金策》无出行专章，出行、行人之理散见于「商贾」（出行经商）与「逃亡」"
             "（行人归否）二章，其理一贯。世为出行之人，应为所往之地，五爻为道路。")
    L.append("· 六亲取用：世爻为出行人自己；应爻为地头、彼处、所投之人；五爻为道路；"
             "官鬼为途中灾厄、风波盗贼；子孙为福德、解神（制鬼消灾）；妻财为盘缠、利息；"
             "父母为行李、文书、舟车（动则辛劳、克子孙）；兄弟为同伴、为耗财。")
    _CX_JING = [
        ("路上有官休出外",
         "五爻为道路，临官鬼发动，途中必多惊险，不宜出外；以所临六神断灾——白虎为风波、"
         "玄武为盗贼、勾陈为阻滞、螣蛇为惊恐、朱雀为口舌。"),
        ("鬼克身爻，商贩者必遭盗贼",
         "买卖经商、出行在外，若遇官鬼临玄武发动来克世爻，必遭盗贼之祸。"),
        ("日月相合，开行定主有人投",
         "开行、出行占吉凶，世应俱要不空、财福要全备、官鬼要有气（或静而受克）、父兄要衰静，"
         "斯为上吉；更得月建、日辰、动爻生合世爻，则近悦远来，财利必顺；动出官兄常有是非口舌，"
         "应空主开不成、彼处无依。"),
        ("归魂卦用遇生合，不捕而自回；游魂卦应又交重，能潜而会遁",
         "出行行人占，归魂主归、主恋家不出；游魂主游走、行远、去而不定。"),
        ("内近外远，生世则终有归期",
         "用爻在内卦人在近处，在外卦在远处；最喜生合持世，人虽远去，日后自当归来，寻之易见。"),
        ("静易动难，坐空则必无寻路",
         "用爻不动，人易寻、行有定；动则迁移无常，指东言西；若落空亡，杳无踪迹。"),
        ("合起合住，若非容隐即相留",
         "用静逢合则合起、用动逢合则合住；日辰动爻合住用神，必有牵绊、容留，主欲行而被留、"
         "动身迟滞。"),
        ("冲动冲开，不是使令当败露",
         "静爻逢冲为冲动，动爻逢冲为冲开；逢冲则动，主速行、起程、阻滞被冲开。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _CX_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    if guan_yao5:
        L.append("· 「路上有官休出外」——五爻（道路）临官鬼发动，途中多惊险，不宜出行；"
                 "临" + yao5['liushen'] + "，"
                 + {'白虎': '主风波、跌打', '玄武': '主盗贼、失脱', '勾陈': '主阻滞、羁留',
                    '螣蛇': '主惊恐、虚惊', '朱雀': '主口舌、官非'}.get(yao5['liushen'], '主灾厄') + "。")
    if guan_keshi and guan_dong_li:
        L.append("· 「鬼克身爻，商贩者必遭盗贼」——官鬼有力发动来克世，出行有灾，宜暂缓。")
    if gui_hun:
        L.append("· 「归魂卦用遇生合，不捕而自回」——归魂主归、恋家，「归魂不出疆」，"
                 "占出行主行不成、欲行又止、去而复返。")
    if you_hun:
        L.append("· 「游魂卦应又交重，能潜而会遁」——游魂主游走、行远，占出行利起身、行踪不定。")
    if liu_chong or bian_chong:
        L.append("· 六冲主动、主散，占出行逢冲则行期速、动身快；动化六冲，先动后散。")
    if liu_he or bian_he:
        L.append("· 「合起合住，若非容隐即相留」——六合主牵绊、合住，占出行主行期迟、被事绊住、"
                 "动身不易。")
    if ying['is_kong']:
        L.append("· 应爻（地头）空亡，彼处无依、所投落空，去之无益。")
    if ying_rel == '生' and not ying['is_kong']:
        L.append("· 应爻生合世爻，到地头得人照拂、诸事顺遂。")
    if zi_dong and not (guan_keshi and guan_dong_li):
        L.append("· 子孙（福德、解神）发动，能制鬼消灾，出行一路平安，吉。")
    if shi['is_kong'] or shi['is_po']:
        L.append("· 世爻（出行人）空亡、月破，己身无力，不宜远行，待出空填实。")

    # ---------- 二、逐条详断 ----------
    L.append("【二、本卦出行逐条详断】")
    L.append("（1）出行人·世爻")
    L.append(_yong_yao_duan(shi, C))
    if shi_wang and not shi['is_kong'] and not shi['is_po']:
        L.append("　· 世爻旺相有气，出行人自身强健、谋为得力。")
    else:
        L.append("　· 世爻休囚、空破，自身力弱，远行不利，宜缓行或改期。")

    L.append("（2）地头·应爻（彼处、所投之人）")
    L.append(_yong_yao_duan(ying, C))
    if ying_rel == '生':
        L.append("　· 应生世，彼处得益、人来就我，吉。")
    elif ying_rel == '克':
        L.append("　· 应克世，彼处有压、人地不宜，须防。")
    elif shi_rel == '生':
        L.append("　· 世生应，我去求人、劳心费力。")
    elif ying['is_kong']:
        L.append("　· 应空，地头无依、所求不遂。")
    else:
        L.append("　· 世应比和，彼我相安，平稳。")

    L.append("（3）道路·五爻与灾厄·官鬼")
    L.append(_yong_yao_duan(yao5, C, extra='五爻为道路'))
    if guans:
        for y in guans:
            if y['is_dong']:
                if not _youli(y, C):
                    ex = '官鬼动而空破，险而不实，待填实须防'
                elif y['pos'] == 5:
                    ex = '官鬼在道路（五爻）发动，途中有险，尤忌'
                elif y['is_shi']:
                    ex = '官鬼持世发动，灾近身，出行有阻、有忧惊'
                else:
                    ex = '官鬼发动，途中有险、忧惊'
                if y['liushen']:
                    ex += '；临' + y['liushen'] + ('主风波、水患' if y['liushen'] == '白虎'
                          else '主盗贼' if y['liushen'] == '玄武'
                          else '主阻滞' if y['liushen'] == '勾陈'
                          else '主惊恐' if y['liushen'] == '螣蛇'
                          else '主口舌' if y['liushen'] == '朱雀' else '')
            else:
                ex = '官鬼安静，途中无大灾'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 官鬼不现，途中无灾，吉。")

    L.append("（4）福德·子孙（解神）、盘缠·妻财、行李·父母、同伴·兄弟")
    if zis:
        for y in zis:
            ex = '子孙发动，制鬼消灾，出行得福' if y['is_dong'] and _youli(y, C) \
                 else '子孙安静，逢官鬼发动之日宜提防'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 子孙不现，福德解神不现，官鬼无制，出行宜谨慎。")
    if cais:
        for y in cais:
            L.append(_yong_yao_duan(y, C, extra='妻财为盘缠、利息'))
    else:
        L.append("　· 妻财不现，盘缠不足、出外少利。")
    if fus:
        for y in fus:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='父母为行李、舟车、文书，动则行程劳碌、且克子孙'))
    if xiongs:
        for y in xiongs:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='兄弟为同伴、为耗财，动则同伴多、破费、口舌'))

    L.append("（5）卦象格局（行期迟速、远近）")
    ge = []
    if you_hun:
        ge.append("　· 游魂卦：主行远、好动，利起身、外出，行踪不定。")
    if gui_hun:
        ge.append("　· 归魂卦：主归、主恋家，「归魂不出疆」，占出行主行不成、欲行又止、去而复返。")
    if liu_chong:
        ge.append("　· 六冲卦：主动主散，行期速、动身快。")
    if liu_he:
        ge.append("　· 六冲之反，六合卦主牵绊、合住，行期迟、被事绊住。")
    if bian_chong:
        ge.append("　· 动化六冲：先起身后分散，行程有变动。")
    if bian_he:
        ge.append("　· 动化六合：初欲行而终被合住，迟滞、留连。")
    if not ge:
        ge.append("　· 非游魂、归魂、六冲、六合，行期迟速以世爻、道路（五爻）、合冲动静为主。")
    for ln in ge:
        L.append(ln)

    # ---------- 三、综合与应期 ----------
    L.append("【三、综合断语与动身应期】")
    zong = []
    if guan_yao5 or (guan_keshi and guan_dong_li and not zi_dong) or (guan_chishi_dong and not zi_dong):
        if guan_yao5:
            zong.append("五爻（道路）临官鬼发动，又无子孙解救——「路上有官休出外」，途中必有惊险"
                        "（风波、盗贼、阻滞），此行不宜，宜暂缓、改期，待官鬼受克、子孙值日再行。")
        elif guan_chishi_dong:
            zong.append("官鬼持世发动、又无子孙福德制鬼，灾近身，主出行有阻、途中忧惊惊险——"
                        "「路上有官休出外」，宜暂缓，待官鬼受克、子孙值日再行。")
        else:
            zong.append("官鬼有力发动克世，又无子孙解救——「路上有官休出外」，途中必有惊险"
                        "（风波、盗贼、阻滞），此行不宜，宜暂缓、改期，待官鬼受克、子孙值日再行。")
    elif gui_hun or (liu_he and not (you_hun or liu_chong)):
        zong.append("卦逢归魂（或六合牵绊），「归魂不出疆」，主行不成、欲行又止、被事绊住，"
                    "勉强行之亦迟滞、去而复返；待冲开合绊之日方动身。")
    elif shi_wang and not shi['is_kong'] and not shi['is_po'] and (zi_dong or zi_wang) \
            and not (guan_keshi and guan_dong_li) and not guan_chishi_dong and not ying['is_kong']:
        if you_hun or liu_chong:
            zong.append("世爻旺相、子孙福德制鬼、应不空，又逢游魂、六冲——出行大吉，行期迅速、"
                        "一路平安、到地头得意。")
        else:
            zong.append("世爻旺相、子孙得力、官鬼不克、应不空——出行平稳吉利，唯行期以冲开、"
                        "逢值之日为定。")
    elif shi['is_kong'] or shi['is_po']:
        zong.append("世爻空亡、月破，出行人己身无力，不宜远行，待出空、填实、逢合之日再议。")
    elif ying['is_kong']:
        zong.append("应爻（地头）空亡，彼处无依、所投落空，去之无益，宜另图或改期。")
    else:
        zong.append("出行卦象平中带小阻，世爻有气、官鬼不肆则可行，行期待冲开合绊、"
                    "世爻逢值之日；若临官鬼受克之日，途中须防灾。")
    for z in zong:
        L.append("· " + z)

    L.append("【动身应期】")
    chong_shi = LIUCHONG.get(shi['zhi'], '')
    he_shi = LIUHE.get(shi['zhi'], '')
    if (liu_he or gui_hun) and not (you_hun or liu_chong):
        L.append(f"· 六合、归魂合绊主迟，待冲开合绊（{chong_shi}日）、或世爻逢值（{shi['zhi']}日）动身。")
    elif you_hun or liu_chong:
        L.append(f"· 游魂、六冲主速，近则世爻逢值（{shi['zhi']}日）、逢冲（{chong_shi}日）即起身。")
    else:
        L.append(f"· 以世爻为行人：逢值（{shi['zhi']}日）、逢冲（{chong_shi}日）、合住待冲开（{chong_shi}日）动身。")
    if guan_keshi:
        L.append("· 行期又宜避官鬼当值、受克之日，候子孙（福德）值日则一路无虞。")
    L.append(_YQ_TAIL)
    L.append("（以上依《卜筮正宗·黄金策》商贾章、逃亡章及六爻出行通例推演，为软件据卦理之分析；"
             "出行仍须注意天气、交通与安全，卦理仅作参考。）")
    return L


# ============================================================
# 官司（词讼）
# ============================================================
_GUANSI_HUA = {
    ('官鬼', '子孙'): '官化子孙，官符化出和解之神，事将散，吉',
    ('子孙', '官鬼'): '子孙化官，先欲和而后兴讼，先和后争',
    ('父母', '官鬼'): '状词化官鬼，词讼益炽，凶',
    ('官鬼', '父母'): '官鬼化父母，官方文书相催，事难解',
    ('妻财', '父母'): '财化父母，财不克状词，文书复立，先阻后成',
    ('父母', '妻财'): '父母化财，状词回头被克，词讼不成立，凶于告者',
    ('妻财', '官鬼'): '财化官鬼，以财贿生官，事反炽',
    ('兄弟', '官鬼'): '兄弟化官，中证反被官事牵连',
}


def fenxi_guansi(paipan):
    """《黄金策·词讼》官司专断：世为自己、应为对头，官鬼为官符、罪名，父母为状词，
    子孙为和解制官之神，妻财为嘱托官府，兄弟为中证、干众。"""
    C = _setup(paipan)
    L = _head(paipan)
    p = C['paipan']; shi = C['shi']; ying = C['ying']
    guans = C['byqin']['官鬼']; fus = C['byqin']['父母']; zis = C['byqin']['子孙']
    cais = C['byqin']['妻财']; xiongs = C['byqin']['兄弟']

    shi_s = C['st_of'](shi); ying_s = C['st_of'](ying)
    shi_wang = shi_s['level'] in ('旺相', '有气') and not shi['is_kong'] and not shi['is_po']
    ying_wang = ying_s['level'] in ('旺相', '有气') and not ying['is_kong'] and not ying['is_po']
    # 官鬼克应/克世（鬼克应为我胜、鬼克世为我败）
    def grel(y):
        return get_wuxing_relation(y['wuxing'], shi['wuxing'])
    def grel_y(y):
        return get_wuxing_relation(y['wuxing'], ying['wuxing'])
    guan_ke_ying = any(grel_y(y) == '克' and _youli(y, C) for y in guans)
    guan_ke_shi = any(grel(y) == '克' and _youli(y, C) for y in guans)
    guan_dong = any(y['is_dong'] for y in guans)
    zi_dong = any(y['is_dong'] and _youli(y, C) for y in zis)
    zi_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in zis)
    fu_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in fus)
    fu_kp = (not fus) or all(y['is_kong'] or y['is_po'] for y in fus)
    cai_dong = any(y['is_dong'] and _youli(y, C) for y in cais)
    # 世应生合/冲克
    ysheng_shi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) == '生'
    yke_shi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) == '克'
    shisheng_y = get_wuxing_relation(shi['wuxing'], ying['wuxing']) == '生'
    shi_he_ying = (LIUHE.get(shi['zhi']) == ying['zhi'])
    shi_chong_ying = (LIUCHONG.get(shi['zhi']) == ying['zhi'])
    bihe = (shi['wuxing'] == ying['wuxing'])
    # 间爻（三、四爻）：中证
    jian = [C['yx'][2], C['yx'][3]]
    jian_xiong = any(y['liuqin'] == '兄弟' and y['is_dong'] for y in jian)
    # 父临应/临世
    fu_lin_ying = ying['liuqin'] == '父母'
    fu_lin_shi = shi['liuqin'] == '父母'

    # ---------- 一、经典 ----------
    L.append("【一、《黄金策·词讼》论官司（经典）】")
    L.append("· 总纲：「小忿不惩，必至争长竞短；大亏既负，宁不诉枉申冤？欲定输赢，须详世应」"
             "——卦中世应，即状中原被（原告、被告），详此则两边胜负可知。")
    L.append("· 六亲取用：世爻为自己，应爻为对头（对方）；官鬼为官符、官府、罪名；父母为状词、文书；"
             "子孙为和解之神、制官之煞（子孙动则劝和、散讼）；妻财为嘱托官府之费（财生官、财克父）；"
             "兄弟在间爻为中证、干众。")
    _GS_JING = [
        ("应乃对头，要休囚死绝；世为自己，宜帝旺长生",
         "不拘原、被，占以世为自己、应为对头；应旺世衰他强我弱，世旺应衰他弱我强。"),
        ("相冲相克，乃是欺凌之象",
         "世爻刑克应爻，未为我胜，乃是欺他之象；必是官鬼克应爻、或动爻月日克应，方为我胜。"),
        ("相生相合，终成合好之情",
         "世应生合，原被有和释之意；世生应我欲求和，应生世他欲求和；应、世动空、化空者，"
         "俱是假意言和。"),
        ("世应比合官鬼动，恐公家捉打官司",
         "世应比和本是和释之象，倘官鬼动克，主官府捉打官司、不欲和议；子孙亦动，终成和议。"),
        ("卦爻安静子孙兴，喜亲友劝和公事",
         "六爻安静、世应虽不生合，而子孙发动者，必有亲邻劝和。"),
        ("世空则我欲息争",
         "世空则我欲息争，应空则他欲息争，世应俱空，两怨销意。"),
        ("官逢太岁，必非州县之词",
         "官居第五爻若值太岁，此事必干朝廷；逢月建必涉台宪。"),
        ("内外有官，事涉一司终不了",
         "官不上卦，无官主张；内外有官，权不归一，主事体反复，必经两司然后了事。"),
        ("上下有父，词兴两度始能成",
         "官、父两爻不宜重见，主转变不定、事主缠绵，卒难了结；占告遇此，必再告之成。"),
        ("官父两强，词讼表章皆准理；妻财一动，申呈诉告总徒劳",
         "上表、申奏、告诉皆要官父两全、有气不空则能准理；最怕财动伤父，必不可成。"),
        ("父旺官衰，雀角鼠牙之讼",
         "父母旺相、官鬼休囚，情词若大，事实细微，故乃鼠牙雀角之争。"),
        ("变衰动旺，虎头蛇尾之人",
         "凡世应旺动，是有并吞六国之势；若变入墓绝空亡，乃先强后弱、虎头蛇尾。"),
        ("无合无生纵旺，何殊独脚虎；有刑有克逢空，当效缩头龟",
         "应爻旺动无生合者，彼虽刚强，只是独脚虎，不足畏；世无生合又遇日月动爻刑克，"
         "当效缩头龟，且勿与对理。"),
        ("兄在间中，事必干众",
         "兄弟在间爻，词内干犯众多；动则中证贪贿，克应索赔资财，克世须用财托。"),
        ("父临应上，彼欲兴词",
         "父母为文书，临世我欲告理，临应他欲申诉；动则欲行，静则不举。"),
        ("墓逢日德刑冲，目下即当出狱；岁挈福神生合，狱中必遇天恩",
         "世墓、鬼墓交动皆入狱之象，若得日辰刑冲破，目下即当出狱；在狱最喜太岁生合世爻，"
         "主有天恩赦宥。"),
        ("若问罪名，须详官鬼；要知消散，当看子孙",
         "罪名轻重以官鬼定，旺则罪重、衰则罪轻；散讼消灾看子孙，福动鬼静以生旺日月断。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _GS_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    if shi_wang and ying_wang is False and not shi['is_kong']:
        L.append("· 「应乃对头要休囚死绝，世为自己宜帝旺长生」——世旺应衰，他弱我强，我占便宜。")
    if shi_wang is False and ying_wang:
        L.append("· 「应乃对头要休囚死绝」——应旺世衰，他强我弱，我处下风。")
    if guan_ke_ying:
        L.append("· 「相冲相克，乃是欺凌之象」——必是官鬼克应爻，方为我胜，官符偏向于我。")
    if guan_ke_shi:
        L.append("· 官鬼克世，是官符、刑责加于我身，主我败、我受责。")
    if (ysheng_shi or shi_he_ying or shisheng_y or bihe) and not guan_dong:
        L.append("· 「相生相合，终成合好之情」——世应生合、比和，两边有和释之意。")
    if zi_dong:
        L.append("· 「卦爻安静子孙兴，喜亲友劝和公事」——子孙发动，制官鬼、散讼，主有劝和、事可息。")
    if shi['is_kong']:
        L.append("· 「世空则我欲息争」——世空，我方欲息讼、不欲究。")
    if ying['is_kong']:
        L.append("· 「应空则他欲息争」——应空，对方心虚、欲息讼、或其讼不实。")
    if fu_lin_ying:
        L.append("· 「父临应上，彼欲兴词」——父母临应，对方欲申诉告状。")
    if fu_kp:
        L.append("· 父母（状词）空亡、不上卦，词讼表章无气、难准。")
    if cai_dong and fu_wang is False:
        L.append("· 「妻财一动，申呈诉告总徒劳」——财动伤父母（状词），诉讼难成。")
    if jian_xiong:
        L.append("· 「兄在间中，事必干众」——间爻兄弟发动，中证贪贿、干犯众、要费用。")
    if shi_chong_ying:
        L.append("· 世应相冲，两家凌竞、互不相让。")

    # ---------- 二、逐条详断 ----------
    L.append("【二、本卦官司逐条详断】")
    L.append("（1）胜负·世应（自己与对头）")
    L.append(_yong_yao_duan(shi, C))
    L.append(_yong_yao_duan(ying, C))
    if shi_wang and not ying_wang:
        L.append("　· 世旺应衰，我强他弱，理势在我。")
    elif ying_wang and not shi_wang:
        L.append("　· 应旺世衰，他强我弱，我处下风。")
    if shi_he_ying or ysheng_shi or shisheng_y:
        L.append("　· 世应相生相合，「终成合好之情」，有和解之基。")
    if shi_chong_ying or yke_shi:
        L.append("　· 世应相冲相克，两家争斗激烈；须官鬼克应方为我胜。")
    if bihe and not guan_dong:
        L.append("　· 世应比和，本是和释之象；官鬼不动则和，官鬼动则公家捉打官司。")

    L.append("（2）官符·官鬼爻（官府、罪名、刑责）")
    if guans:
        for y in guans:
            xx = []
            if y['is_shi']:
                xx.append('官鬼持世，官符缠身、自己亦被官司牵累')
            if grel(y) == '克' and _youli(y, C):
                xx.append('官鬼克世，刑责加身，我败')
            elif grel_y(y) == '克' and _youli(y, C):
                xx.append('官鬼克应，官符制他，为我胜')
            if y['is_dong']:
                xx.append('官鬼发动，官府捉打、讼事方兴' if _youli(y, C) else '官鬼动而空破，虚张声势')
            L.append(_yong_yao_duan(y, C, extra='；'.join(xx) or '官鬼安静，官事不紧'))
    else:
        L.append("　· 官鬼不现，无官主张，讼事不成、无人受理。")

    L.append("（3）状词·父母爻（词讼、表章）")
    if fus:
        for y in fus:
            xx = []
            if y['is_shi']:
                xx.append('父临世，我欲告理')
            if y['is_ying']:
                xx.append('父临应，彼欲申诉')
            if y['is_dong'] and _youli(y, C):
                xx.append('父母发动，状词欲行，官父两全则准理')
            L.append(_yong_yao_duan(y, C, extra='；'.join(xx) or '父母为状词'))
    else:
        L.append("　· 父母不现，无状词、文书无气，讼难成立。")

    L.append("（4）和解·子孙（制官散讼）与嘱托·妻财、中证·兄弟")
    if zis:
        for y in zis:
            ex = '子孙发动，制官鬼、散讼，主有劝和、大事化小' if y['is_dong'] and _youli(y, C) \
                 else '子孙安静，待发动则和'
            L.append(_yong_yao_duan(y, C, extra=ex))
    else:
        L.append("　· 子孙不现，散讼、和解之神不现，官鬼无制，事难解。")
    if cais:
        for y in cais:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='妻财动则生官、伤状词，须用财嘱托，然伤父则告诉徒劳'))
    if xiongs:
        for y in xiongs:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='兄弟动，中证贪贿、干众、耗财'))

    L.append("（5）动爻变化吉凶")
    for ln in _bian_duan(C, {'官鬼': '忌', '妻财': '忌', '父母': '喜', '子孙': '喜', '兄弟': '忌'},
                         _GUANSI_HUA):
        L.append(ln)

    L.append("（6）卦象格局")
    for ln in _geju_duan(C, "六合主讼事和释、绊住。",
                         "六冲主讼起而散、矛盾激烈，亦主官司易结。",
                         "动化六合，先争后和。",
                         "动化六冲，讼终解散。"):
        L.append(ln)

    # ---------- 三、综合与应期 ----------
    L.append("【三、综合断语（输赢）与散讼应期】")
    zong = []
    if zi_dong or (shi['is_kong'] and ying['is_kong']):
        zong.append("子孙发动（或世应俱空），「喜亲友劝和」「两怨销意」，主官司可息、和解收场，"
                    "于子孙值日、官鬼受克之日散。")
    elif (ysheng_shi or shi_he_ying or bihe) and not guan_ke_shi:
        if guan_dong and not zi_dong:
            if shi_he_ying and ying['is_kong']:
                zong.append("世应本相合、应又空亡，对方心虚已有息讼之意；然官鬼发动、子孙（散讼之神）"
                            "不现，讼事方兴而一时难散，主拖延。宜趁彼虚主动求和，候子孙值日、官鬼受克日方息。")
            else:
                zong.append("世应虽生合比和，然官鬼发动、子孙不现，讼事方兴而无和解之神，一时难散、"
                            "主拖延；宜求和，候子孙值日、官鬼受克日方息。")
        else:
            zong.append("世应生合比和、官鬼不克世，两家有和释之意；官鬼静、子孙一动即散讼和解。")
    elif guan_ke_shi and not (zi_dong or guan_ke_ying):
        zong.append("官鬼有力克世、应爻不弱，「官符加身」，主我败、我受刑责，宜早求和解、"
                    "用财托人，候子孙发动制官方解。")
    elif shi_wang and (guan_ke_ying or (not ying_wang and not guan_ke_shi)):
        zong.append("世旺应衰、官鬼克应（或官不克世），理势在我，主我胜、对方受制；"
                    "然「世克应只是欺他，必鬼克应方为我胜」，以官鬼不克身为准。")
    elif ying_wang and not shi_wang:
        zong.append("应旺世衰，他强我弱，我处下风；若世又无生合、逢刑克，当效「缩头龟」，"
                    "不宜硬争，宜求和。")
    else:
        zong.append("世应强弱互见、胜负未定，以官鬼生克为断：官鬼克应我胜、克世我败；"
                    "子孙发动则散讼和解，世应生合则和好。")
    for z in zong:
        L.append("· " + z)

    L.append("【散讼应期】")
    if guans:
        gy = max(guans, key=lambda y: (y['is_dong'], C['st_of'](y)['score']))
        L.append(f"· 散讼候：子孙（福德）值日、官鬼入墓绝受克之日；本病官{gy['zhi']}，"
                 f"墓于{_MUKU[gy['wuxing']]}、绝于{_JUEDI[gy['wuxing']]}，至其日官事退。")
    if zis:
        zy = max(zis, key=lambda y: (y['is_dong'], C['st_of'](y)['score']))
        chong = LIUCHONG.get(zy['zhi'], '')
        L.append(f"· 子孙（和解）逢值（{zy['zhi']}日）、逢冲（{chong}日），有人劝和、官司可息。")
    L.append("· 世空、应空者，出空、填实之月日见分晓；牵连牢狱，逢日辰刑冲克破世墓、鬼墓日出狱。")
    L.append(_YQ_TAIL)
    L.append("（以上依《卜筮正宗·黄金策》词讼章之法推演，为软件据卦理之分析；实际纠纷宜依法、"
             "理性处理，优先协商、寻求专业法律帮助，卦理仅作参考。）")
    return L


# ============================================================
# 房子（家宅）
# ============================================================
_ZHAI_SHEN = {
    '青龙': '青龙临宅，主鼎新创造、喜气、门庭吉庆',
    '白虎': '白虎临宅，主老旧破败、孝服、刑伤，交重休囚主远年建造',
    '螣蛇': '螣蛇临宅，主怪异虚惊、阴人小灾',
    '玄武': '玄武临宅，主盗贼暗昧、阴私破财',
    '朱雀': '朱雀临宅，主口舌官非、火光',
    '勾陈': '勾陈临宅，主停滞、田土坟塚之事',
}
# 官鬼（灾患）临六神之别
_ZHAI_GUI_SHEN = {
    '青龙': '官鬼临青龙，喜中藏忧、酒色财气之扰，灾较轻',
    '白虎': '官鬼临白虎，主孝服、刑伤、疾病、人口丧亡，最凶',
    '螣蛇': '官鬼临螣蛇，主怪异虚惊、梦寐不宁、阴邪',
    '玄武': '官鬼临玄武，主盗贼暗昧、阴私破财',
    '朱雀': '官鬼临朱雀，主口舌官非、火光、骂詈',
    '勾陈': '官鬼临勾陈，主田土争讼、阻滞、坟塚牵连',
}


def fenxi_fangzi(paipan):
    """《黄金策·家宅》房子（阳宅、迁居、置业）专断：内卦二爻为宅舍，外卦五爻为人口；
    父母为房屋，官鬼为灾患，妻财为家业，子孙为福德，兄弟为耗财。"""
    C = _setup(paipan)
    L = _head(paipan)
    p = C['paipan']; shi = C['shi']; ying = C['ying']; gong_wx = C['gong_wx']
    er = C['yx'][1]   # 二爻：宅舍
    wu = C['yx'][4]   # 五爻：人口
    guans = C['byqin']['官鬼']; zis = C['byqin']['子孙']; cais = C['byqin']['妻财']
    fus = C['byqin']['父母']; xiongs = C['byqin']['兄弟']

    er_s = C['st_of'](er); wu_s = C['st_of'](wu)
    # 宅（二爻）与人（五爻）生克
    er_ke_wu = get_wuxing_relation(er['wuxing'], wu['wuxing']) == '克'
    wu_ke_er = get_wuxing_relation(wu['wuxing'], er['wuxing']) == '克'
    er_sheng_wu = get_wuxing_relation(er['wuxing'], wu['wuxing']) == '生'
    # 房屋（父母）
    fu_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in fus)
    fu_kp = (not fus) or all(y['is_kong'] or y['is_po'] for y in fus)
    # 灾患（官鬼）
    guan_dong = any(y['is_dong'] and _youli(y, C) for y in guans)
    guan_ke_shi = any(get_wuxing_relation(y['wuxing'], shi['wuxing']) == '克' and _youli(y, C)
                      for y in guans)
    guan_lin_er = any(y['pos'] == 2 for y in guans)
    guan_zhi = any((y['is_dong'] and _youli(y, C)) or (y['pos'] == 2 and y['liushen'] == '白虎')
                   for y in guans)
    # 福德（子孙）制鬼
    zi_dong = any(y['is_dong'] and _youli(y, C) for y in zis)
    zi_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in zis)
    # 家业（妻财）
    cai_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] for y in cais)
    cai_kp = (not cais) or all(y['is_kong'] or y['is_po'] for y in cais)
    xiong_dong = any(y['is_dong'] and _youli(y, C) for y in xiongs)
    # 土金发动（开辟之基）
    tu_jin_dong = any(y['is_dong'] and y['wuxing'] in ('土', '金') for y in C['yx'])

    # ---------- 一、经典 ----------
    L.append("【一、《黄金策·家宅》论房子（经典）】")
    L.append("· 总纲：「创基立业，虽本人之维纬，关风敛气，每由宅以肇端。故要知人宅之兴衰，"
             "当察卦爻之内外。内为宅，外为人，详审爻中之真假」——内卦第二爻为宅舍，外卦第五爻为人口。")
    L.append("· 六亲取用：内卦二爻为宅舍，外卦五爻为人口；父母爻为房屋、栋宇；官鬼为灾患、"
             "官非、邪祟；妻财为家业、财源；子孙为福德、消灾之神；兄弟为耗财、同辈争竞。"
             "内二爻克外五爻，谓宅去克人，凶；外五爻克内二爻，谓人来克宅，吉；内二爻生外五爻，"
             "谓宅去生人，吉。")
    _FZ_JING = [
        ("合为门，冲为路，不论卦内之有无",
         "合二爻为门、冲二爻为路，卦内不必明现冲合；以二爻（宅）所合、所冲之支断门、路之方位。"),
        ("龙德贵人乘旺，岳岳之侯门；官星父母长生，深深之相府",
         "青龙、文书（父母）、官鬼、天乙贵人临年月日建、临宅临身临命，主出官职、门第显赫。"),
        ("门庭新气象，交重得合青龙",
         "交重青龙不空、在日辰旬内得生旺，主鼎新创造；休囚主修旧合新。临财新修膳厨、临父新修"
         "旧堂、临兄新修门户、临子新修房舍、临官新修厅堂屋宇。"),
        ("堂宇旧规模，宅舍重侵白虎",
         "白虎交重、休囚空绝，主远年建造、破旧不整。"),
        ("土金发动开辟之基，父母空亡租赁之宅",
         "土化金、金化土为开辟之基，主新造；父母为房屋，逢空无气，又逢应爻、日辰、动爻化文书"
         "与宅相生相合，主是租赁之屋。"),
        ("门庭热闹，财官临帝旺之乡",
         "财、鬼、龙、德、贵人乘旺长生之位，临财生合世爻，主家庭热闹。"),
        ("家道兴隆，福禄在长生之地",
         "福即子孙、禄即妻财，在长生之位临身生世，主家道兴隆；二爻发动，或生或克，主改造厅堂。"),
        ("宅无破而逢生，宅兴财旺",
         "岁、日、月三不破宅爻，更逢动爻生宅、与财爻旺相有气，为宅兴财旺。"),
        ("有财无鬼耗散多端",
         "若无鬼爻，则兄弟无制，恐兄弟当权之时财爻破散，妻宫亦有驳杂。"),
        ("有鬼无财灾生不已",
         "鬼不宜动、财不可无；若官鬼动克世爻、克宅爻，主连生灾咎。"),
        ("有人制鬼鬼动无妨",
         "以本命克鬼为制，或子孙动来制鬼，鬼虽动，乃无害。"),
        ("助鬼伤身财多何益",
         "若妻财动而生官鬼、鬼又克身，纵然财多，助鬼伤身，亦无益。"),
        ("忌鬼爻交重临白虎，须防人眷刑伤",
         "忌鬼爻并白虎发动，冲克本命，主其人有灾殃、人口刑伤。"),
        ("催尸煞身命入黄泉，大忌墓门开合",
         "鬼动克人命为催尸煞，人命逢死绝为黄泉路，忌人命爻冲合墓爻；日辰动爻合墓爻为墓门开合，"
         "凡卦中必见鬼墓便是。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _FZ_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    if er_sheng_wu:
        L.append("· 「内二爻生五爻，谓宅去生人，吉」——宅舍生人口，居之得荫，人丁兴旺。")
    if er_ke_wu:
        L.append("· 「内卦二爻克五爻，谓宅去克人，凶」——宅舍克人口，居之不利人丁，宜改修。")
    if wu_ke_er:
        L.append("· 「外卦五爻克二爻，谓人来克宅，吉」——人能制宅，主人能胜宅、可改造得利。")
    if fu_kp:
        L.append("· 「父母空亡租赁之宅」——房屋（父母）空亡无气，多是租赁之屋、或产权无凭据。")
    if tu_jin_dong and fu_wang:
        L.append("· 「土金发动开辟之基」——土金爻动，主新造、开辟，父母有气则新宅可成。")
    if er['liushen'] == '青龙':
        L.append("· 「门庭新气象，交重得合青龙」——青龙临宅，主鼎新创造、吉庆。")
    if er['liushen'] == '白虎':
        L.append("· 「堂宇旧规模，宅舍重侵白虎」——白虎临宅，主屋宇破旧、孝服刑伤。")
    if guan_dong and guan_ke_shi:
        L.append("· 「有鬼无财灾生不已」——官鬼发动克世、克宅，宅不安、连生灾咎，须子孙制之。")
    if guan_zhi and not zi_dong:
        L.append("· 「忌鬼爻交重临白虎，须防人眷刑伤」——鬼临宅、白虎，宅有灾患、人口不安。")
    if zi_dong and guan_dong:
        L.append("· 「有人制鬼鬼动无妨」——子孙（福德）发动制鬼，宅中灾患可解。")
    if cai_wang and fu_wang and not guan_ke_shi:
        L.append("· 「宅无破而逢生，宅兴财旺」「家道兴隆，福禄在长生之地」——房屋有气、财福旺，"
                 "家道兴隆。")
    if xiong_dong and not guan_dong:
        L.append("· 「有财无鬼耗散多端」——兄弟发动而无官鬼制之，财爻破散，主破财、争竞。")

    # ---------- 二、逐条详断 ----------
    L.append("【二、本卦房子逐条详断】")
    L.append("（1）宅舍·二爻（内卦为宅）")
    L.append(_yong_yao_duan(er, C, extra='二爻为宅舍'))
    if er_s['level'] in ('旺相', '有气'):
        L.append("　· 宅爻旺相有气，宅舍兴旺、结构牢固。")
    else:
        L.append("　· 宅爻休囚空破，宅舍衰败、或有破损。")
    if er['liushen']:
        L.append("　· 宅爻临" + er['liushen'] + "：" + _ZHAI_SHEN.get(er['liushen'], '') + "。")

    L.append("（2）人口·五爻（外卦为人）与人宅生克")
    L.append(_yong_yao_duan(wu, C, extra='五爻为人口'))
    if er_sheng_wu:
        L.append("　· 宅生人（二爻生五爻），居之得荫，吉。")
    elif er_ke_wu:
        L.append("　· 宅克人（二爻克五爻），居之不利人丁，凶，宜改修或换宅。")
    elif wu_ke_er:
        L.append("　· 人克宅（五爻克二爻），人能胜宅，吉，改造可成。")
    else:
        L.append("　· 人宅比和，无冲克，平稳。")

    L.append("（3）房屋·父母爻（栋宇、产权、租赁）")
    if fus:
        for y in fus:
            xx = []
            if y['is_kong']:
                xx.append('父母空亡，主租赁之宅、产权无凭')
            if y['is_dong'] and _youli(y, C):
                xx.append('父母发动，主迁动、修造、换房')
            if C['st_of'](y)['level'] in ('旺相', '有气'):
                xx.append('父母有气，房屋牢固、有凭据')
            L.append(_yong_yao_duan(y, C, extra='；'.join(xx) or '父母为房屋'))
    else:
        L.append("　· 父母不现，房屋之象不显，或无自己房产、居无定所。")

    L.append("（4）灾患·官鬼与福德·子孙（制鬼）")
    if guans:
        for y in guans:
            xx = []
            if y['pos'] == 2:
                xx.append('官鬼临宅爻，宅中不安')
            if y['liushen']:
                xx.append(_ZHAI_GUI_SHEN.get(y['liushen'], '官鬼临' + y['liushen'] + '，主灾患'))
            if y['is_dong'] and _youli(y, C):
                xx.append('官鬼发动，灾患方兴，克世则伤人')
            L.append(_yong_yao_duan(y, C, extra='；'.join(xx) or '官鬼安静，灾患轻'))
    else:
        L.append("　· 官鬼不现，宅无灾患、邪祟，吉。")
    if zis:
        for y in zis:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='子孙福德发动，制鬼消灾，宅中安吉'
                                         if _youli(y, C) else '子孙动而空破，解灾力暂弱'))
    else:
        L.append("　· 子孙不现，福德不现，官鬼无制，须防灾。")

    L.append("（5）家业·妻财与耗财·兄弟")
    if cais:
        for y in cais:
            L.append(_yong_yao_duan(y, C, extra='妻财为家业、财源'))
    else:
        L.append("　· 妻财不现，家业财源空薄。")
    if xiongs:
        for y in xiongs:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='兄弟发动，耗财、同辈争竞，无官制则财散'))

    L.append("（6）动爻变化与卦象格局")
    for ln in _bian_duan(C, {'妻财': '喜', '子孙': '喜', '父母': '喜', '官鬼': '忌', '兄弟': '忌'}):
        L.append(ln)
    for ln in _geju_duan(C, "六合主宅气聚、人安、宜久居。",
                         "六冲主宅气散、人口不宁、居之不久，亦主迁动。",
                         "动化六合，迁居后安定。",
                         "动化六冲，迁居后仍散、不利久居。"):
        L.append(ln)

    # ---------- 三、综合与应期 ----------
    L.append("【三、综合断语与宅运应期】")
    zong = []
    if er_ke_wu or (guan_dong and guan_ke_shi and not zi_dong):
        zong.append("宅爻克人（或官鬼旺动克世、克宅而无子孙制），「宅去克人，凶」「灾生不已」，"
                    "宅不安、人口不利，宜择子孙制鬼之日修造、安镇，或迁善地。")
    elif fu_kp and cai_wang is False:
        zong.append("父母（房屋）空亡、妻财（家业）又不旺，「父母空亡租赁之宅」，多无自己房产、"
                    "或产权无凭、宅运平常，待父母逢生旺填实方有自己基业。")
    elif cai_wang and fu_wang and not er_ke_wu and not guan_ke_shi:
        zong.append("房屋（父母）有气、宅不克人、财福旺相、官鬼不肆，「宅兴财旺、家道兴隆」，"
                    "是宜居、可置的吉宅，子孙临宅更吉。")
    elif zi_dong and guan_dong:
        zong.append("宅虽有官鬼发动之灾，然子孙福德动而制之，「鬼动无妨」，灾患可解，"
                    "修造后转吉。")
    else:
        zong.append("宅运平中：以宅爻（二爻）、人口（五爻）生克为纲，宅生人、人克宅则吉，宅克人则凶；"
                    "官鬼静、子孙财福旺则安居。")
    for z in zong:
        L.append("· " + z)

    L.append("【宅运、修造应期】")
    L.append(f"· 宅爻（二爻）{er['zhi']}：逢值（{er['zhi']}日/月）、逢冲（{LIUCHONG.get(er['zhi'],'')}日）"
             "应宅之动静；新造、迁居宜选宅爻、子孙、妻财生旺之日。")
    if guans:
        gy = max(guans, key=lambda y: (y['is_dong'], C['st_of'](y)['score']))
        L.append(f"· 宅中灾患候官鬼受克、子孙值日；本鬼{gy['zhi']}，墓于{_MUKU[gy['wuxing']]}、"
                 f"绝于{_JUEDI[gy['wuxing']]}，至其日灾退。")
    L.append(_YQ_TAIL)
    L.append("（以上依《卜筮正宗·黄金策》家宅章之法推演，为软件据卦理之分析；置业、迁居、"
             "风水调整尚须结合实际房屋、产权与现实条件，卦理仅作参考。）")
    return L


# ============================================================
# 合同（文书、契约；无独立专章，合参求名、仕宦、婚姻、词讼、六冲六合）
# ============================================================
def fenxi_hetong(paipan):
    """合同、契约专断：父母为文书、契约、字据（用神），世为自己、应为对方；官鬼为官方约束、
    章印（官生父为有官方背书），妻财动则克父母（因财毁约）；六合世应生合则成，六冲世应冲克则散。"""
    C = _setup(paipan)
    L = _head(paipan)
    p = C['paipan']; shi = C['shi']; ying = C['ying']
    fus = C['byqin']['父母']; guans = C['byqin']['官鬼']; cais = C['byqin']['妻财']
    zis = C['byqin']['子孙']; xiongs = C['byqin']['兄弟']

    fu_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po']
                  for y in fus)
    fu_kp = (not fus) or all(y['is_kong'] or y['is_po'] for y in fus)
    fu_dong = any(y['is_dong'] for y in fus)
    def frel(y):
        if y['is_shi']:
            return '持世'
        return get_wuxing_relation(y['wuxing'], shi['wuxing'])
    fu_chishi = any(y['is_shi'] for y in fus)
    fu_shengshi = any(frel(y) == '生' for y in fus)
    fu_lin_ying = ying['liuqin'] == '父母'
    # 财动克父（毁约）
    cai_dong_li = [y for y in cais if y['is_dong'] and _youli(y, C)]
    # 官生父（官方背书）/ 官克世（违约官非）
    guan_sheng_fu = False
    guan_ke_shi = any(get_wuxing_relation(y['wuxing'], shi['wuxing']) == '克' and _youli(y, C)
                      for y in guans)
    for g in guans:
        for f in fus:
            if get_wuxing_relation(g['wuxing'], f['wuxing']) == '生' and _youli(g, C):
                guan_sheng_fu = True
    # 世应生合/冲克
    ysheng_shi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) == '生'
    yke_shi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) == '克'
    shisheng_y = get_wuxing_relation(shi['wuxing'], ying['wuxing']) == '生'
    shi_he_ying = LIUHE.get(shi['zhi']) == ying['zhi']
    shi_chong_ying = LIUCHONG.get(shi['zhi']) == ying['zhi']
    liu_he = p['name'] in LIUHE_GUA
    liu_chong = p['name'] in LIUCHONG_GUA
    bian_he = bool(p['bian_gua'] and p['bian_gua']['name'] in LIUHE_GUA)
    bian_chong = bool(p['bian_gua'] and p['bian_gua']['name'] in LIUCHONG_GUA)

    # ---------- 一、经典 ----------
    L.append("【一、《黄金策》论合同文书（经典）】")
    L.append("· 说明：《黄金策》无合同专章，文书、契约、字据之理散见「求名」（文章、文书）、"
             "「仕宦」（印绶、宣敕）、「婚姻」（庚帖、婚书）、「词讼」（状词）各章，"
             "再以世应（双方）、六冲六合（成散）合参，其理自明。")
    L.append("· 六亲取用：父母爻为文书、契约、字据、条款，是合同之用神；世爻为自己、应爻为对方；"
             "官鬼为官方、章印、约束（官生父则有官方背书，官克世则有违约官非）；妻财动则克父母，"
             "主因财毁约、条款受损；子孙为和解之神。卦逢六合、世应生合，合同易成；六冲、世应冲克，"
             "合同难成、终散。")
    _HT_JING = [
        ("月克文书，考试逢之不第；官摇父母，交重无气空嗟",
         "父母为文书、凭据，最宜旺相、得日月动爻生扶；若被月建日辰克伤、或官鬼带父母动而无气，"
         "文书不济、凭据不立。"),
        ("父母空亡，休望差除宣敕",
         "父母为印绶、文书、诰牒、凭据；空亡则无凭无据，所主文书之事不成。占合同，父母空亡，"
         "契约难立、条款落空、或无保障。"),
        ("官父两强，词讼表章皆准理",
         "官鬼、父母两爻俱全、有气不空，则文书得官方之准理、有章印保障；占合同主条款成立、"
         "有官方或权威背书。"),
        ("妻财一动，申呈诉告总徒劳",
         "上表、申呈、告诉最怕妻财发动伤了父母文书；占合同，财动克父母，多因钱财、利益毁约、"
         "条款受阻，合同难成。"),
        ("相生相合，终成合好之情",
         "世应生合，双方有合好、相得之意；世生应我欲成、应生世他欲就，合作、契约由此而合。"),
        ("相冲相克，乃是欺凌之象",
         "世应相冲相克，双方凌竞、互不相让，合同难成；勉强成之，日后亦生争端。"),
        ("卦见六冲，往来亦徒迎迓；爻当六合，晨昏幸尔盘桓",
         "六冲主散，占交易、合同逢六冲，往来空忙、终难成就；六合主合，得六合卦则情分相投、"
         "内外相合，主成、主久。"),
        ("应生合者易成，逢冲克者必就",
         "应爻为对方，应来生合世爻，对方有诚意、合作易成；应逢冲克世爻，对方无情或相压，"
         "事难成就。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _HT_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 本卦特别贴合之经文：")
    if fu_wang and (fu_chishi or fu_shengshi):
        L.append("· 父母（文书）旺相、持世或生合世，合同成立、条款于我有利、有凭据保障。")
    if fu_kp:
        L.append("· 「父母空亡，休望差除宣敕」——合同文书空亡、不上卦，契约难立、条款落空、"
                 "无保障。")
    if cai_dong_li and not fu_wang:
        L.append("· 「妻财一动，申呈诉告总徒劳」——妻财有力发动，克伤父母文书，主因钱财毁约、"
                 "合同受阻。")
    if guan_sheng_fu and fu_wang:
        L.append("· 「官父两强，词讼表章皆准理」——官鬼生父母，文书得官方、章印背书，"
                 "合同更有保障。")
    if guan_ke_shi:
        L.append("· 官鬼克世，主约束、官非加身，防合同中有对己不利的条款、或日后违约争讼。")
    if (ysheng_shi or shi_he_ying or liu_he) and not (yke_shi or shi_chong_ying or liu_chong) \
            and not ying['is_kong'] and not fu_kp:
        _he = []
        if liu_he:
            _he.append('卦逢六合')
        if ysheng_shi or shi_he_ying:
            _he.append('世应生合')
        L.append("· 「相生相合，终成合好之情」「爻当六合」——%s，双方情投，合同易成且能长久。"
                 % '、'.join(_he))
    if shi_he_ying and ying['is_kong']:
        L.append(f"· 世{shi['zhi']}、应{ying['zhi']}本相合，然应爻空亡，是为「合空」，对方暂无实意，"
                 "待应爻填实方算真合。")
    if yke_shi or shi_chong_ying or liu_chong:
        L.append("· 「相冲相克，乃是欺凌之象」「卦见六冲，往来亦徒迎迓」——世应冲克、卦逢六冲，"
                 "合同难成、成亦终散。")
    if ying['is_kong'] and not shi_he_ying:
        L.append("· 应爻（对方）空亡，对方无诚意、实力不实，合作落空。")
    if fu_lin_ying:
        L.append("· 父母临应，文书、条款在对方手中，须看其旺衰生克。")

    # ---------- 二、逐条详断 ----------
    L.append("【二、本卦合同逐条详断】")
    L.append("（1）文书·父母爻（合同、条款、凭据）")
    if fus:
        for y in fus:
            xx = []
            if y['is_shi']:
                xx.append('父母持世，凭据在我、条款由我主')
            if y['is_ying']:
                xx.append('父母临应，凭据在对方')
            if frel(y) == '生':
                xx.append('文书生合世爻，条款于我有利')
            if frel(y) == '克':
                xx.append('文书克世，条款压我、束缚于我')
            if y['is_kong'] or y['is_po']:
                xx.append('文书空破，合同不实、无保障')
            L.append(_yong_yao_duan(y, C, extra='；'.join(xx) or '父母为文书'))
    else:
        L.append("　· 父母不现，合同文书之主不上卦，无凭据、契约难立。")
        for ln in _fushen_duan(C, '父母'):
            L.append(ln)

    L.append("（2）双方·世应（诚意、强弱）")
    L.append(_yong_yao_duan(shi, C, extra='世为自己'))
    L.append(_yong_yao_duan(ying, C, extra='应为对方'))
    if shi_he_ying:
        if ying['is_kong']:
            L.append(f"　· 世{shi['zhi']}、应{ying['zhi']}本相合，然应爻空亡，合而不实，待应爻填实方是真合。")
        else:
            L.append(f"　· 世{shi['zhi']}、应{ying['zhi']}相合，双方情投，合作易成。")
    elif ysheng_shi:
        L.append("　· 应生世，对方有诚意、来就我，合作易成。")
    elif shisheng_y:
        L.append("　· 世生应，我去求合、我方让步，劳心。")
    elif yke_shi or shi_chong_ying:
        L.append("　· 应克世、世应相冲，对方压我、双方不让，合同难成。")
    if ying['is_kong'] and not shi_he_ying:
        L.append("　· 应空，对方不实、无诚意，合作落空。")
    if ying['liuqin'] == '兄弟':
        L.append("　· 应临兄弟，对方为同辈、竞争者或合伙之伴，防分利、争财，账目须清。")

    L.append("（3）官方·官鬼（章印、约束）与毁约·妻财、和解·子孙")
    if guans:
        for y in guans:
            xx = []
            if guan_sheng_fu:
                xx.append('官生父母，文书有官方/章印背书')
            if get_wuxing_relation(y['wuxing'], shi['wuxing']) == '克' and _youli(y, C):
                xx.append('官克世，防违约官非、条款压制')
            if y['is_dong'] and not _youli(y, C):
                xx.append('官动而空破，官非虚惊不实')
            L.append(_yong_yao_duan(y, C, extra='；'.join(xx) or '官鬼为约束'))
    else:
        L.append("　· 官鬼不现，无官方章印之事，亦无官非。")
    if cais:
        for y in cai_dong_li:
            L.append(_yong_yao_duan(y, C, extra='妻财发动，生官、克父母文书，因财毁约、条款受损'))
    if zis:
        for y in zis:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='子孙发动，制官、和解，合同有争可散'
                                         if _youli(y, C) else '子孙动而空破，和解力暂弱'))
    if xiongs:
        for y in xiongs:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='兄弟动，同伴、第三方竞争，争财分利'))

    L.append("（4）动爻变化与卦象格局（成散）")
    for ln in _bian_duan(C, {'父母': '喜', '官鬼': '喜', '妻财': '忌', '子孙': '忌', '兄弟': '忌'}):
        L.append(ln)
    ge = []
    if liu_he:
        ge.append("　· 六合卦：「爻当六合，晨昏幸尔盘桓」，主合同成、双方相合、能久。")
    if liu_chong:
        ge.append("　· 六冲卦：「卦见六冲，往来亦徒迎迓」，主合同难成、成亦终散。")
    if bian_he:
        ge.append("　· 动化六合：初有分歧，终归于合，合同后成。")
    if bian_chong:
        ge.append("　· 动化六冲：初欲合而终散，先成后毁。")
    if not ge:
        ge.append("　· 非六合、六冲，以父母（文书）旺衰、世应生合冲克为主断成散。")
    for ln in ge:
        L.append(ln)

    # ---------- 三、综合与应期 ----------
    L.append("【三、综合断语（成否）与签约应期】")
    zong = []
    cheng = fu_wang and not (yke_shi or shi_chong_ying or liu_chong) and not ying['is_kong'] \
        and not (cai_dong_li and not fu_chishi)
    if (yke_shi or shi_chong_ying or liu_chong) and not (liu_he or ysheng_shi):
        zong.append("世应冲克、卦逢六冲，「相冲相克乃是欺凌」「往来亦徒迎迓」，双方不合、"
                    "合同难成，勉强成之亦终散，不宜勉强。")
    elif fu_kp:
        zong.append("父母（文书）空亡、不上卦，「休望差除宣敕」，合同难立、条款落空、无保障；"
                    "旺者待父母填实出旬、得生扶之日再签。")
        if shi_he_ying and ying['is_kong']:
            zong.append(f"又世{shi['zhi']}、应{ying['zhi']}虽本相合，然应爻空亡，「合空」而不实，"
                        "对方暂无实意；须文书、应爻俱填实生扶之日再签。")
        elif ying['is_kong']:
            zong.append("且应爻空亡，对方暂无诚意、实力不实，合作落空。")
    elif cai_dong_li and not fu_chishi:
        zong.append("妻财有力发动克父母文书，「申呈诉告总徒劳」，多因钱财、利益分配毁约、"
                    "条款受损，须先把利益、款项写清，候财爻受克、父母值日方成。")
    elif cheng and (ysheng_shi or shi_he_ying or liu_he or fu_chishi):
        zong.append("父母文书旺相、世应生合（或卦逢六合、文书持世），对方有诚意、条款有据——"
                    "合同易成、于我有利、可以久守"
                    + ("，且官父两全，有官方章印保障。" if guan_sheng_fu else "。"))
    elif fu_wang and not ying['is_kong']:
        zong.append("文书有气、对方不空，合同基本可成，唯世应未纯合，须再协商条款，"
                    "候父母逢值、世应生合之日签。")
    else:
        zong.append("合同成否未定：以父母文书为凭、世应生合为成、六冲财动克父为败，"
                    "文书旺、世应合则签，文书空、世应冲则缓。")
    for z in zong:
        L.append("· " + z)

    L.append("【签约应期】")
    if fus:
        fy = max(fus, key=lambda y: (y['is_dong'], C['st_of'](y)['score']))
        chong = LIUCHONG.get(fy['zhi'], '')
        if fy['is_kong'] or fy['is_po']:
            L.append(f"· 父母{fy['zhi']}空破：待出旬填实、逢值（{fy['zhi']}日）或逢冲（{chong}日）"
                     "文书得力，方可签约。")
        else:
            L.append(f"· 父母（文书）逢值（{fy['zhi']}日）、逢合（{LIUHE.get(fy['zhi'],'')}日）"
                     "合同成立、落定；逢冲日防变更。")
    L.append("· 六冲、财动克父者，宜待冲散、财爻受克、父母逢生旺之日再签。")
    L.append(_YQ_TAIL)
    L.append("（以上依《卜筮正宗·黄金策》文书印绶之法、世应六冲六合之理推演，为软件据卦理之分析；"
             "实际签约须审阅条款、核实对方资质、依法办理，卦理仅作参考。）")
    return L


# ============================================================
# 朋友（兄弟、朋友；依《进人口》章并参商贾章兄弟爻）
# ============================================================
def fenxi_pengyou(paipan):
    """朋友、同伴、合伙专断：兄弟爻为朋友（同侪），应爻为所占之友人；进人口章云「朋友以兄弟为主」。
    兄弟生合世、旺相临青龙则得力；空破、克世、化空、临玄武则难靠；兄弟动克财防合伙破财。"""
    C = _setup(paipan)
    L = _head(paipan)
    p = C['paipan']; shi = C['shi']; ying = C['ying']
    xiongs = C['byqin']['兄弟']; guans = C['byqin']['官鬼']; cais = C['byqin']['妻财']
    fus = C['byqin']['父母']; zis = C['byqin']['子孙']

    def xrel(y):
        if y['is_shi']:
            return '持世'
        return get_wuxing_relation(y['wuxing'], shi['wuxing'])
    xiong_wang = any(C['st_of'](y)['level'] in ('旺相', '有气') and not y['is_kong'] and not y['is_po']
                     for y in xiongs)
    xiong_kp = (not xiongs) or all(y['is_kong'] or y['is_po'] for y in xiongs)
    xiong_shengshi = any(xrel(y) == '生' for y in xiongs)
    xiong_keshi = any(xrel(y) == '克' and _youli(y, C) for y in xiongs)
    xiong_lin_ying = any(y['is_ying'] for y in xiongs)
    xiong_chishi = any(y['is_shi'] for y in xiongs)
    xiong_dong = [y for y in xiongs if y['is_dong'] and _youli(y, C)]
    # 所占之友（应临兄弟）空亡、兄弟临螣蛇/玄武发动——不实、多谋、贪财
    xiong_ying_kong = any(y['is_ying'] and (y['is_kong'] or y['is_po']) for y in xiongs)
    xiong_she_xuan_dong = any(y['is_dong'] and y['liushen'] in ('螣蛇', '玄武') for y in xiongs)
    # 兄弟化空亡/化退、化鬼
    xiong_hua_kong = False
    xiong_hua_guan = False
    for y in xiongs:
        if y['is_dong']:
            by = _bian_by_pos(p, y['pos'])
            if by:
                bq = get_liuqin(C['gong_wx'], by['wuxing'])
                if bq == '官鬼':
                    xiong_hua_guan = True
                if by['zhi'] in p['xunkong']:
                    xiong_hua_kong = True
    # 应爻（友人）
    ying_s = C['st_of'](ying)
    ying_shengshi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) == '生'
    ying_he = LIUHE.get(ying['zhi']) == shi['zhi']
    ying_ke = get_wuxing_relation(ying['wuxing'], shi['wuxing']) == '克'
    # 官鬼克兄弟（朋友灾）
    xiong_wx = _liuqin_wuxing(C['gong_wx'], '兄弟')
    guan_ke_xiong = any(get_wuxing_relation(y['wuxing'], xiong_wx) == '克' and _youli(y, C)
                        for y in guans)
    # 兄弟动克财（合伙破财）
    xiong_ke_cai = bool(xiong_dong) and cais

    # ---------- 一、经典 ----------
    L.append("【一、《黄金策·进人口》论朋友（经典）】")
    L.append("· 说明：《黄金策》无朋友专章，「进人口」章明言「朋友以兄弟为主」——占朋友、同伴、"
             "合伙，以兄弟爻为朋友之主；若专指某一位友人，则兼看应爻。其生合世爻、克冲身象、"
             "动化空亡、临青龙玄武，皆是判断可信、得力与否的依据。")
    L.append("· 六亲取用：兄弟爻为朋友、同侪、伙伴（用神）；应爻为所占之具体友人；生兄弟者父母，"
             "为长辈、文书之助；克兄弟者官鬼，主朋友有灾、是非；兄弟动则克妻财，合伙、同财时"
             "防破财、争利；子孙为兄弟之生源（兄生子、子生财，子孙亦为调和、解纷之神）。")
    _PY_JING = [
        ("须别来占，方知主用",
         "过继小儿以子孙为主，买妾婢童仆、收留迷失之人以财为主；若窝藏有难之人，看其人与我如何相识——"
         "朋友以兄弟为主，尊长以父母为主，妇人以妻财为主。"),
        ("用不宜动，动必难留",
         "用爻发动，其人难托；若遇游魂、或化入游魂，异日主逃散、去留不定；若来生合世爻，"
         "则不致连累。"),
        ("主不可伤，伤须夭折",
         "主象（所占之人）衰弱，而被日辰动爻乘旺刑伤克害，更无解救者，必然无情、不得力。"),
        ("衰入墓中，拟定萎靡不振；旺临世上，决然干蛊有成",
         "用爻入墓，其人性慵懒、衰弱无气空绝，主萎靡不振；若得旺相临身持世、或生合世爻，"
         "乃大吉，其人能干事、有担当。"),
        ("用爻生合世爻，必得其力；主象克冲身象，难服其心",
         "用爻生合世爻，其人可用，凡有相干必然用心；若克冲身象，难以使其心服、为我所用。"),
        ("动化空亡，有始无终之辈；蛇合官鬼，多谋少德之人",
         "用爻发动变入空亡，其人有头无尾；若临螣蛇动合官鬼，其人虽多谋，然奸诈不实、少德。"),
        ("临玄武而化兄爻，门户须防出入；遇青龙而连福德，资财可付经营",
         "用临玄武动化兄弟，主其人贪财好色，莫用出入；用临青龙动化子孙、生合世爻，"
         "其人至诚忠厚，托以财物则守而不失，使之经营则利归于主。"),
        ("若逢太过及空亡，反主少诚兼懒惰",
         "卦中用爻见有三四重、或旬空者，其人暗藏机巧、反复不实。"),
        ("受动变之伤，向后终难称意；得日月之助，他日定见如心",
         "月建日辰动爻克世，其为不可用，世爻衰必被其害；若得变动、日月生扶合助，"
         "方为吉、交情耐久。"),
        ("世与卦身，以和为贵",
         "世、身二爻相合、相生、比合为吉，相克、相冲、刑害为凶；占朋友，世与用爻（兄弟/应）"
         "生合比和则两相得。"),
    ]
    L.append("· 本章核心经文（先明通例）：")
    for _j, _s in _PY_JING:
        L.append("　· 「%s」——%s" % (_j, _s))
    L.append("· 商贾章论兄弟（合伙同财参用）：")
    L.append("　· 「兄动兮频遇，劫财叠叠」——兄弟爻发动，为劫财之神、为同伴分利，合伙、同财"
             "最忌兄弟发动克世、克财，主破财、争竞。")
    L.append("· 本卦特别贴合之经文：")
    if xiong_wang and (xiong_shengshi or xiong_chishi or xiong_lin_ying or ying_shengshi):
        L.append("· 「用爻生合世爻，必得其力」「旺临世上，决然干蛊有成」——兄弟（朋友）旺相、"
                 "生合世或临应，朋友得力、可托。")
    if xiong_kp:
        L.append("· 「主不可伤，伤须夭折」——兄弟空亡、不上卦，朋友之缘薄、其人不得力、"
                 "或朋友难聚。")
    if xiong_keshi:
        L.append("· 「主象克冲身象，难服其心」——兄弟（朋友）克世，朋友相负、为我所累，"
                 "难以为我所用。")
    if xiong_hua_kong:
        L.append("· 「动化空亡，有始无终之辈」——兄弟动化空亡，朋友有始无终、交情不久。")
    if xiong_hua_guan:
        L.append("· 「蛇合官鬼，多谋少德之人」——兄弟动化官鬼，朋友多谋少实、或招是非牵连。")
    if any(y['liushen'] == '玄武' and y['is_dong'] for y in xiongs):
        L.append("· 「临玄武而化兄爻，门户须防出入」——兄弟临玄武发动，防朋友贪财、欺瞒、"
                 "暗中损我。")
    if any(y['liushen'] == '青龙' for y in xiongs) and xiong_wang:
        L.append("· 「遇青龙而连福德，资财可付经营」——兄弟临青龙旺相，朋友至诚忠厚，"
                 "可托财、可共事。")
    if xiong_ke_cai:
        L.append("· 「兄动兮频遇，劫财叠叠」——兄弟发动，合伙同财主破财、分利、争财，须明算账。")
    if ying_ke:
        L.append("· 应爻（友人）克世，其人压我、相负，不宜深交、合作。")
    if ying_shengshi or ying_he:
        L.append("· 应爻（友人）生合世爻，其人有情、于我有助。")
    if ying['is_kong']:
        L.append("· 应爻（友人）空亡，其人不实、或所求落空。")
    if guan_ke_xiong:
        L.append("· 官鬼克兄弟，主朋友有灾、或朋友之事牵上官非。")

    # ---------- 二、逐条详断 ----------
    L.append("【二、本卦朋友逐条详断】")
    L.append("（1）朋友·兄弟爻（可交、得力与否）")
    if xiongs:
        for y in xiongs:
            xx = []
            if y['is_ying']:
                xx.append('兄弟临应，正是所占之友')
            if y['is_shi']:
                xx.append('兄弟持世，友如手足、与我一体')
            if xrel(y) == '生':
                xx.append('朋友生合世，必得其力')
            if xrel(y) == '克' and _youli(y, C):
                xx.append('朋友克世，相负、为累')
            if y['is_dong']:
                xx.append('兄弟发动，劫财、分利、多变，合伙防破财' if _youli(y, C)
                          else '兄弟动而空破，事暂不成')
            if y['liushen'] in ('青龙', '玄武', '螣蛇', '白虎'):
                xx.append({'青龙': '临青龙，忠厚喜气可交', '玄武': '临玄武，防欺瞒贪财',
                           '螣蛇': '临螣蛇，多谋虚诈', '白虎': '临白虎，性刚、有刑伤'}.get(y['liushen'], ''))
            if len(xiongs) >= 2:
                xx.append('兄弟多现，朋友多、或有朋党，须防太过（卦中兄多反主少诚）')
            L.append(_yong_yao_duan(y, C, extra='；'.join(xx) or '兄弟为朋友'))
    else:
        L.append("　· 卦中不见兄弟爻，朋友之主不上卦。")
        for ln in _fushen_duan(C, '兄弟'):
            L.append(ln)

    L.append("（2）友人·应爻（特指其人）")
    L.append(_yong_yao_duan(ying, C, extra='应爻为所占之友'))
    if ying_he and ying['is_kong']:
        L.append(f"　· 世{shi['zhi']}、应{ying['zhi']}本相合，然应爻空亡，「合空」，交情暂虚、其人不实，待应填实方真。")
    elif ying_he:
        L.append(f"　· 世{shi['zhi']}、应{ying['zhi']}相合，友人有情、与我相得，可交。")
    elif ying_shengshi:
        L.append("　· 应生世，友人有情、来就我，可交。")
    elif ying_ke:
        L.append("　· 应克世，友人负我、压我，不宜深交。")
    if ying['is_kong'] and not ying_he:
        L.append("　· 应空，友人不实、交情落空。")
    if ying['liushen']:
        L.append("　· 应临" + ying['liushen'] + "，可参友人性情：青龙忠厚、玄武暗昧、朱雀多言、"
                 "勾陈迟钝、螣蛇多谋、白虎刚急。")

    L.append("（3）朋友之灾·官鬼（克兄弟）、长辈之助·父母、合伙财利·妻财")
    if guans:
        for y in guans:
            if get_wuxing_relation(y['wuxing'], xiong_wx) == '克' and _youli(y, C):
                L.append(_yong_yao_duan(y, C, extra='官鬼克兄弟，朋友有灾、是非、官非牵连'))
    if fus:
        for y in fus:
            if get_wuxing_relation(y['wuxing'], xiong_wx) == '生':
                if y['is_dong']:
                    L.append(_yong_yao_duan(y, C, extra='父母生兄弟，得长辈、文书之助而益友'))
    if cais and xiong_dong:
        for y in xiong_dong:
            L.append(_yong_yao_duan(y, C, extra='兄弟动克妻财，合伙、同财必分利、破财，账目须清'))
    if zis:
        for y in zis:
            if y['is_dong']:
                L.append(_yong_yao_duan(y, C, extra='子孙为兄弟之生源、解纷之神，发动主朋友调和、'
                                                     '合伙有后生之利'))

    L.append("（4）动爻变化与卦象格局")
    for ln in _bian_duan(C, {'兄弟': '喜', '父母': '喜', '子孙': '喜', '官鬼': '忌', '妻财': '忌'}):
        L.append(ln)
    for ln in _geju_duan(C, "六合主朋友相聚、交情长久、合伙同心。",
                         "六冲主朋友离散、合伙不终、人情冷暖。",
                         "动化六合，先疏后亲、终得合好。",
                         "动化六冲，先亲后疏、终至散伙。"):
        L.append(ln)

    # ---------- 三、综合与应期 ----------
    L.append("【三、综合断语（可交、合伙）与应期】")
    zong = []
    if xiong_keshi or xiong_hua_kong or xiong_ying_kong or xiong_she_xuan_dong or ying_ke:
        _why = []
        if xiong_keshi or ying_ke:
            _why.append("兄弟（朋友）克世、应爻克我，「难服其心」")
        if xiong_hua_kong:
            _why.append("兄弟动化空亡，「有始无终之辈」")
        if xiong_ying_kong:
            _why.append("所占之友（应临兄弟）空亡，「用爻空亡，反复少诚」，其人不实、交情落空")
        if xiong_she_xuan_dong:
            _why.append("兄弟临螣蛇、玄武发动，「蛇合官鬼多谋少德」「门户须防出入」，防虚诈、贪财")
        zong.append("；".join(_why) + "——此人不可深交、不宜托付财物、不宜合伙，宜疏远。")
    elif xiong_ke_cai:
        zong.append("兄弟旺动，朋友本身或可交，然合伙同财逢「劫财叠叠」，必分利、争财、破财，"
                    "不宜共财合伙；若合作，须账目分明、立好字据（父母文书）。")
    elif xiong_wang and (xiong_shengshi or xiong_chishi or xiong_lin_ying or ying_shengshi) \
            and not xiong_kp:
        zong.append("兄弟（朋友）旺相、生合世或临应，「用爻生合世必得其力」「资财可付经营」，"
                    "朋友可靠、得力、可共事；临青龙尤主忠厚长久。")
    elif xiong_kp:
        zong.append("兄弟空亡、不上卦，朋友之缘薄、眼下不得其力，或友人难聚；待兄弟填实、"
                    "逢值之年月方得良朋。")
    else:
        zong.append("朋友之情平中：以兄弟、应爻旺衰生合为断，旺而生合世者可交，克世、空破、"
                    "化空、临玄武者防之；合伙尤忌兄弟动克财。")
    for z in zong:
        L.append("· " + z)

    L.append("【交友、合伙应期】")
    if xiongs:
        xy = max(xiongs, key=lambda y: (y['is_dong'], C['st_of'](y)['score']))
        chong = LIUCHONG.get(xy['zhi'], '')
        L.append(f"· 兄弟（朋友）逢值（{xy['zhi']}日）、逢合（{LIUHE.get(xy['zhi'],'')}日）"
                 "得友、见友、合伙定；逢冲（" + chong + "日）主朋友聚散、变动。")
    L.append("· 合伙签约同合同断，宜父母（字据）旺、世应合、兄弟静之日；兄弟当值动而克财之日，"
             "防争财。")
    L.append(_YQ_TAIL)
    L.append("（以上依《卜筮正宗·黄金策》进人口章及商贾章兄弟爻之法推演，为软件据卦理之分析；"
             "交友、合伙重在知人和契约，卦理仅作参考。）")
    return L
