/* 六爻预测核心算法 —— 移植自 liuyao_core.py（《卜筮正宗》《增删卜易》） */
(function (global) {
  "use strict";

  // ================= 基础数据 =================
  const TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
  const DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
  const DIZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水'
  };
  const TIANGAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
  };
  const TIANGAN_YINYANG = {
    '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳',
    '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'
  };
  const WUXING_SHENG = { '金': '水', '水': '木', '木': '火', '火': '土', '土': '金' };
  const WUXING_KE = { '金': '木', '木': '土', '土': '水', '水': '火', '火': '金' };

  const BAGUA = {
    '乾': { xiang: '天', wuxing: '金', yinyang: '阳', yao: [1, 1, 1],
      nazhi_nei: ['子', '寅', '辰'], nazhi_wai: ['午', '申', '戌'], tiangan_nei: '甲', tiangan_wai: '壬' },
    '兑': { xiang: '泽', wuxing: '金', yinyang: '阴', yao: [1, 1, 0],
      nazhi_nei: ['巳', '卯', '丑'], nazhi_wai: ['亥', '酉', '未'], tiangan_nei: '丁', tiangan_wai: '丁' },
    '离': { xiang: '火', wuxing: '火', yinyang: '阴', yao: [1, 0, 1],
      nazhi_nei: ['卯', '丑', '亥'], nazhi_wai: ['酉', '未', '巳'], tiangan_nei: '己', tiangan_wai: '己' },
    '震': { xiang: '雷', wuxing: '木', yinyang: '阳', yao: [1, 0, 0],
      nazhi_nei: ['子', '寅', '辰'], nazhi_wai: ['午', '申', '戌'], tiangan_nei: '庚', tiangan_wai: '庚' },
    '巽': { xiang: '风', wuxing: '木', yinyang: '阴', yao: [0, 1, 1],
      nazhi_nei: ['丑', '亥', '酉'], nazhi_wai: ['未', '巳', '卯'], tiangan_nei: '辛', tiangan_wai: '辛' },
    '坎': { xiang: '水', wuxing: '水', yinyang: '阳', yao: [0, 1, 0],
      nazhi_nei: ['寅', '辰', '午'], nazhi_wai: ['申', '戌', '子'], tiangan_nei: '戊', tiangan_wai: '戊' },
    '艮': { xiang: '山', wuxing: '土', yinyang: '阳', yao: [0, 0, 1],
      nazhi_nei: ['辰', '午', '申'], nazhi_wai: ['戌', '子', '寅'], tiangan_nei: '丙', tiangan_wai: '丙' },
    '坤': { xiang: '地', wuxing: '土', yinyang: '阴', yao: [0, 0, 0],
      nazhi_nei: ['未', '巳', '卯'], nazhi_wai: ['丑', '亥', '酉'], tiangan_nei: '乙', tiangan_wai: '癸' }
  };

  // 八宫：每宫 [本宫, 一世, 二世, 三世, 四世, 五世, 游魂, 归魂]，元素 [上卦, 下卦, 卦名]
  const BAGONG = {
    '乾': [
      ['乾', '乾', '乾为天'], ['乾', '巽', '天风姤'], ['乾', '艮', '天山遁'], ['乾', '坤', '天地否'],
      ['巽', '坤', '风地观'], ['艮', '坤', '山地剥'], ['离', '坤', '火地晋'], ['离', '乾', '火天大有']
    ],
    '兑': [
      ['兑', '兑', '兑为泽'], ['兑', '坎', '泽水困'], ['兑', '坤', '泽地萃'], ['兑', '艮', '泽山咸'],
      ['坎', '艮', '水山蹇'], ['坤', '艮', '地山谦'], ['震', '艮', '雷山小过'], ['震', '兑', '雷泽归妹']
    ],
    '离': [
      ['离', '离', '离为火'], ['离', '艮', '火山旅'], ['离', '巽', '火风鼎'], ['离', '坎', '火水未济'],
      ['艮', '坎', '山水蒙'], ['巽', '坎', '风水涣'], ['乾', '坎', '天水讼'], ['乾', '离', '天火同人']
    ],
    '震': [
      ['震', '震', '雷为雷'], ['震', '坤', '雷地豫'], ['震', '坎', '雷水解'], ['震', '巽', '雷风恒'],
      ['坤', '巽', '地风升'], ['坎', '巽', '水风井'], ['兑', '巽', '泽风大过'], ['兑', '震', '泽雷随']
    ],
    '巽': [
      ['巽', '巽', '巽为风'], ['巽', '乾', '风天小畜'], ['巽', '离', '风火家人'], ['巽', '震', '风雷益'],
      ['乾', '震', '天雷无妄'], ['离', '震', '火雷噬嗑'], ['艮', '震', '山雷颐'], ['艮', '巽', '山风蛊']
    ],
    '坎': [
      ['坎', '坎', '坎为水'], ['坎', '兑', '水泽节'], ['坎', '震', '水雷屯'], ['坎', '离', '水火既济'],
      ['兑', '离', '泽火革'], ['震', '离', '雷丰'], ['坤', '离', '地火明夷'], ['坤', '坎', '地水师']
    ],
    '艮': [
      ['艮', '艮', '艮为山'], ['艮', '离', '山火贲'], ['艮', '乾', '山天大畜'], ['艮', '兑', '山泽损'],
      ['离', '兑', '火泽睽'], ['乾', '兑', '天泽履'], ['巽', '兑', '风泽中孚'], ['巽', '艮', '风山渐']
    ],
    '坤': [
      ['坤', '坤', '坤为地'], ['坤', '震', '地雷复'], ['坤', '兑', '地泽临'], ['坤', '乾', '地天泰'],
      ['震', '乾', '雷大壮'], ['兑', '乾', '泽天夬'], ['坎', '乾', '水天需'], ['坎', '坤', '水地比']
    ]
  };

  // 世爻位置：宫位序号 0~7（本宫、一世~五世、游魂、归魂）
  const SHI_POS = [6, 1, 2, 3, 4, 5, 4, 3];
  const GONGWEI_NAME = ['本宫', '一世', '二世', '三世', '四世', '五世', '游魂', '归魂'];

  const LIUSHEN = ['青龙', '朱雀', '勾陈', '腾蛇', '白虎', '玄武'];
  const LIUSHEN_QISHI = {
    '甲': 0, '乙': 0, '丙': 1, '丁': 1, '戊': 2,
    '己': 3, '庚': 4, '辛': 4, '壬': 5, '癸': 5
  };

  const LIUQIN = ['兄弟', '子孙', '妻财', '官鬼', '父母'];

  const LIUCHONG = {
    '子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
    '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'
  };
  const LIUHE = {
    '子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯',
    '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'
  };
  const SANHE = [
    [['申', '子', '辰'], '水'],
    [['寅', '午', '戌'], '火'],
    [['巳', '酉', '丑'], '金'],
    [['亥', '卯', '未'], '木']
  ];

  // ================= 工具函数 =================
  function get_ganzhi_index(gan, zhi) {
    const gan_idx = TIANGAN.indexOf(gan);
    const zhi_idx = DIZHI.indexOf(zhi);
    for (let n = 0; n < 60; n++) {
      if (n % 10 === gan_idx && n % 12 === zhi_idx) return n;
    }
    return -1;
  }

  function get_xunkong(ri_gan, ri_zhi) {
    const ganzhi_n = get_ganzhi_index(ri_gan, ri_zhi);
    if (ganzhi_n < 0) return [];
    const xun_shou = ganzhi_n - (ganzhi_n % 10);
    const xun_shou_zhi_idx = xun_shou % 12;
    const k1 = (xun_shou_zhi_idx + 10) % 12;
    const k2 = (xun_shou_zhi_idx + 11) % 12;
    return [DIZHI[k1], DIZHI[k2]];
  }

  // ================= 公历日期转干支 =================
  // 换月十二节（公历近似日期）[月, 日, 进入的月支]
  const _JIEQI = [
    [2, 4, '寅'], [3, 6, '卯'], [4, 5, '辰'], [5, 6, '巳'],
    [6, 6, '午'], [7, 7, '未'], [8, 8, '申'], [9, 8, '酉'],
    [10, 8, '戌'], [11, 7, '亥'], [12, 7, '子'], [1, 6, '丑']
  ];
  const _WUHU_DUN = {
    '甲': '丙', '己': '丙', '乙': '戊', '庚': '戊', '丙': '庚', '辛': '庚',
    '丁': '壬', '壬': '壬', '戊': '甲', '癸': '甲'
  };
  const _YUE_ZHI_ORDER = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'];
  const _RI_BASE = Date.UTC(1900, 0, 1);
  const _RI_BASE_IDX = 10; // 1900-01-01 为甲戌日

  function get_month_zhi(month, day) {
    const md = month * 100 + day;
    if (md >= 204) {
      for (const [m, d, zhi] of _JIEQI) {
        if (md < m * 100 + d) {
          const idx = _YUE_ZHI_ORDER.indexOf(zhi);
          return _YUE_ZHI_ORDER[(idx - 1 + 12) % 12];
        }
      }
      return '子';
    }
    if (md >= 106) return '丑';
    return '子';
  }

  function get_year_pillar(year, month, day) {
    const md = month * 100 + day;
    const gz_year = md >= 204 ? year : year - 1;
    const idx = ((gz_year - 4) % 60 + 60) % 60;
    return { gan: TIANGAN[idx % 10], zhi: DIZHI[idx % 12], gz_year };
  }

  function get_month_gan(year_gan, month_zhi) {
    const yin_gan = _WUHU_DUN[year_gan];
    const offset = _YUE_ZHI_ORDER.indexOf(month_zhi);
    const gi = (TIANGAN.indexOf(yin_gan) + offset) % 10;
    return TIANGAN[gi];
  }

  function get_day_pillar(year, month, day) {
    const t = Date.UTC(year, month - 1, day);
    const delta = Math.round((t - _RI_BASE) / 86400000);
    const idx = ((_RI_BASE_IDX + delta) % 60 + 60) % 60;
    return [TIANGAN[idx % 10], DIZHI[idx % 12]];
  }

  function date_to_ganzhi(year, month, day) {
    const yp = get_year_pillar(year, month, day);
    const month_zhi = get_month_zhi(month, day);
    const month_gan = get_month_gan(yp.gan, month_zhi);
    const [ri_gan, ri_zhi] = get_day_pillar(year, month, day);
    return {
      year_gan: yp.gan, year_zhi: yp.zhi,
      month_gan, month_zhi,
      ri_gan, ri_zhi,
      xunkong: get_xunkong(ri_gan, ri_zhi)
    };
  }

  function get_liuqin(gong_wuxing, yao_wuxing) {
    if (yao_wuxing === gong_wuxing) return '兄弟';
    if (WUXING_SHENG[yao_wuxing] === gong_wuxing) return '父母';
    if (WUXING_SHENG[gong_wuxing] === yao_wuxing) return '子孙';
    if (WUXING_KE[yao_wuxing] === gong_wuxing) return '官鬼';
    if (WUXING_KE[gong_wuxing] === yao_wuxing) return '妻财';
    return '未知';
  }

  function get_wuxing_relation(wx1, wx2) {
    if (wx1 === wx2) return '同';
    if (WUXING_SHENG[wx1] === wx2) return '生';
    if (WUXING_SHENG[wx2] === wx1) return '被生';
    if (WUXING_KE[wx1] === wx2) return '克';
    if (WUXING_KE[wx2] === wx1) return '被克';
    return '无';
  }

  // ================= 卦象查找与构建 =================
  function find_gua(shang_gua, xia_gua) {
    for (const gong_name in BAGONG) {
      const list = BAGONG[gong_name];
      for (let idx = 0; idx < list.length; idx++) {
        const [s, x, name] = list[idx];
        if (s === shang_gua && x === xia_gua) return [gong_name, idx, name];
      }
    }
    return null;
  }

  function match_gua(yao3) {
    for (const name in BAGUA) {
      const a = BAGUA[name].yao;
      if (a[0] === yao3[0] && a[1] === yao3[1] && a[2] === yao3[2]) return name;
    }
    return null;
  }

  function build_gua_from_yaos(yao_list) {
    const xia = match_gua(yao_list.slice(0, 3));
    const shang = match_gua(yao_list.slice(3, 6));
    return [shang, xia];
  }

  // ================= 装卦 =================
  function zhuang_gua(shang_gua, xia_gua, dong_yao, yue_zhi, ri_gan, ri_zhi) {
    dong_yao = dong_yao || [];
    const info = find_gua(shang_gua, xia_gua);
    if (!info) return null;
    const [gong_name, gongwei_idx, gua_name] = info;
    const gong_wuxing = BAGUA[gong_name].wuxing;

    const shi_pos = SHI_POS[gongwei_idx];
    const ying_pos = shi_pos <= 3 ? shi_pos + 3 : shi_pos - 3;

    const xia_nazhi = BAGUA[xia_gua].nazhi_nei;
    const shang_nazhi = BAGUA[shang_gua].nazhi_wai;
    const nazhi = xia_nazhi.concat(shang_nazhi);

    const naggan = [BAGUA[xia_gua].tiangan_nei, BAGUA[xia_gua].tiangan_nei, BAGUA[xia_gua].tiangan_nei,
      BAGUA[shang_gua].tiangan_wai, BAGUA[shang_gua].tiangan_wai, BAGUA[shang_gua].tiangan_wai];

    const yao_yinyang = BAGUA[xia_gua].yao.concat(BAGUA[shang_gua].yao);

    const liuqin_list = nazhi.map(z => get_liuqin(gong_wuxing, DIZHI_WUXING[z]));

    const liushen_list = ['', '', '', '', '', ''];
    if (ri_gan && ri_gan in LIUSHEN_QISHI) {
      const start = LIUSHEN_QISHI[ri_gan];
      for (let i = 0; i < 6; i++) liushen_list[i] = LIUSHEN[(start + i) % 6];
    }

    const xunkong = (ri_gan && ri_zhi) ? get_xunkong(ri_gan, ri_zhi) : [];

    const yaos = [];
    for (let pos = 6; pos >= 1; pos--) {
      const idx = pos - 1;
      const zhi = nazhi[idx];
      yaos.push({
        pos,
        yinyang: yao_yinyang[idx],
        gan: naggan[idx],
        zhi,
        wuxing: DIZHI_WUXING[zhi],
        liuqin: liuqin_list[idx],
        liushen: liushen_list[idx],
        is_dong: dong_yao.indexOf(pos) >= 0,
        is_shi: pos === shi_pos,
        is_ying: pos === ying_pos,
        is_kong: xunkong ? xunkong.indexOf(zhi) >= 0 : false,
        is_po: !!(yue_zhi && zhi === LIUCHONG[yue_zhi])
      });
    }

    // 变卦
    const bian_yaos = yao_yinyang.slice();
    for (const d of dong_yao) bian_yaos[d - 1] = 1 - bian_yaos[d - 1];
    const [bian_shang, bian_xia] = build_gua_from_yaos(bian_yaos);
    const bian_info = (bian_shang && bian_xia) ? find_gua(bian_shang, bian_xia) : null;

    let bian_gua = null;
    if (bian_info && dong_yao.length) {
      const [b_gong, b_gw_idx, b_name] = bian_info;
      const b_nazhi = BAGUA[bian_xia].nazhi_nei.concat(BAGUA[bian_shang].nazhi_wai);
      const b_gong_wx = BAGUA[b_gong].wuxing;
      // 六亲仍按本卦宫论（《增删卜易·动变章》：泽天夬变天风姤，变卦六爻皆标本卦坤宫六亲）
      const b_liuqin = b_nazhi.map(z => get_liuqin(gong_wuxing, DIZHI_WUXING[z]));
      const bian_yaos_data = [];
      for (let pos = 6; pos >= 1; pos--) {
        const idx = pos - 1;
        bian_yaos_data.push({
          pos,
          yinyang: bian_yaos[idx],
          zhi: b_nazhi[idx],
          wuxing: DIZHI_WUXING[b_nazhi[idx]],
          liuqin: b_liuqin[idx],
          is_dong: dong_yao.indexOf(pos) >= 0
        });
      }
      bian_gua = {
        name: b_name, gong: b_gong, gongwei: GONGWEI_NAME[b_gw_idx],
        shang: bian_shang, xia: bian_xia, yaos: bian_yaos_data
      };
    }

    return {
      name: gua_name, gong: gong_name, gongwei: GONGWEI_NAME[gongwei_idx],
      gong_wuxing, shang: shang_gua, xia: xia_gua,
      shi_pos, ying_pos, dong_yao: dong_yao.slice(),
      yue_zhi: yue_zhi || null, ri_gan: ri_gan || null, ri_zhi: ri_zhi || null,
      xunkong, yaos, bian_gua
    };
  }

  // ================= 起卦 =================
  function tongqian_yao(bei) {
    if (bei === 1) return [1, false, '单', '━━━'];
    if (bei === 2) return [0, false, '拆', '━ ━'];
    if (bei === 3) return [1, true, '重', '━━━ ○'];
    if (bei === 0) return [0, true, '交', '━ ━ ×'];
    return [0, false, '?', '?'];
  }

  function qigua_from_tongqian(liu_ci) {
    const yao_list = [], dong_list = [];
    for (let i = 0; i < liu_ci.length; i++) {
      const [yy, dong] = tongqian_yao(liu_ci[i]);
      yao_list.push(yy);
      if (dong) dong_list.push(i + 1);
    }
    return [yao_list, dong_list];
  }

  // ================= 数字转中文 / 化进退神 =================
  const _CN = { 1: '初', 2: '二', 3: '三', 4: '四', 5: '五', 6: '上' };
  function num_to_cn(n) { return (n in _CN) ? _CN[n] : String(n); }

  const _JIN = {
    '寅': '卯', '巳': '午', '申': '酉', '亥': '子',
    '丑': '辰', '辰': '未', '未': '戌', '戌': '丑'
  };
  const _TUI = {};
  for (const k in _JIN) _TUI[_JIN[k]] = k;

  function hua_jin_tui(dong_zhi, bian_zhi) {
    if (dong_zhi === bian_zhi) return '化伏吟';
    if (_JIN[dong_zhi] === bian_zhi) return '化进神';
    if (_TUI[dong_zhi] === bian_zhi) return '化退神';
    return '化比和';
  }

  // ================= 描述爻在月日下的状态 =================
  function miao_yao_zhuangtai(yao, yue_zhi, ri_zhi) {
    const wx = yao['wuxing'];
    const tags = [];
    if (yue_zhi) {
      const yue_wx = DIZHI_WUXING[yue_zhi];
      const yue_rel = get_wuxing_relation(yue_wx, wx);
      if (yue_rel === '同') tags.push('临月建（旺）');
      else if (yue_rel === '生') tags.push('得月生（相）');
      else if (yue_rel === '克') tags.push('被月克（休）');
      else if (yue_rel === '被生') tags.push('生月（休）');
      else if (yue_rel === '被克') tags.push('月克（囚）');
    }
    if (ri_zhi) {
      const ri_wx = DIZHI_WUXING[ri_zhi];
      const ri_rel = get_wuxing_relation(ri_wx, wx);
      if (ri_rel === '同') tags.push('临日建（旺）');
      else if (ri_rel === '生') tags.push('得日生');
      else if (ri_rel === '克') tags.push('被日克');
      if (LIUHE[ri_zhi] === yao['zhi']) tags.push('日合');
      if (LIUCHONG[ri_zhi] === yao['zhi']) tags.push('日冲（暗动/日破）');
    }
    if (yao['is_po']) tags.push('月破');
    if (yao['is_kong']) tags.push('旬空');
    if (yao['is_dong']) tags.push('动爻');
    if (!tags.length) tags.push('平常');
    return tags.join('、');
  }

  // ================= 用神映射 =================
  const YONGSHEN_MAP = {
    '功名': '官鬼', '官运': '官鬼', '事业': '官鬼', '工作': '官鬼',
    '升职': '官鬼', '升迁': '官鬼', '考试': '父母', '学业': '父母',
    '文书': '父母', '合同': '父母', '房子': '父母', '车辆': '父母',
    '求财': '妻财', '财运': '生意', '买卖': '妻财',
    '妻子': '妻财', '钱财': '妻财', '婚姻': '官鬼', '感情': '官鬼',
    '丈夫': '官鬼', '男友': '官鬼', '疾病': '官鬼', '病': '官鬼',
    '子女': '子孙', '孩子': '子孙', '儿子': '子孙', '女儿': '子孙',
    '兄弟': '兄弟', '朋友': '兄弟', '姐妹': '兄弟', '同事': '兄弟',
    '官司': '官鬼', '盗贼': '官鬼', '出行': '妻财', '行人': '六亲'
  };

  // ================= 通用断卦 =================
  function fenxi_gua(paipan, yongshen_type) {
    const fenxi = [];
    const yaos = paipan['yaos'];
    const yaos_shunxu = yaos.slice().reverse();
    const yue = paipan['yue_zhi'];
    const ri_g = paipan['ri_gan'];
    const ri_z = paipan['ri_zhi'];
    const xunkong = paipan['xunkong'];
    const dong = paipan['dong_yao'];

    let head = `【卦名】${paipan['name']}（${paipan['gong']}宫${paipan['gongwei']}卦，${paipan['gong_wuxing']}）`;
    if (paipan['bian_gua']) {
      const bg = paipan['bian_gua'];
      head += ` 之  ${bg['name']}（${bg['gong']}宫${bg['gongwei']}卦）`;
    }
    fenxi.push(head);

    const riyue = [];
    if (yue) riyue.push(`月建${yue}${DIZHI_WUXING[yue]}`);
    if (ri_g && ri_z) riyue.push(`日辰${ri_g}${ri_z}${DIZHI_WUXING[ri_z]}`);
    if (xunkong && xunkong.length) riyue.push(`旬空${xunkong[0]}${xunkong[1]}`);
    if (riyue.length) fenxi.push('【日月】' + riyue.join('，'));

    if (dong && dong.length) {
      const dong_desc = dong.map(d => `${num_to_cn(d)}爻动`).join('、');
      fenxi.push(`【动爻】${dong_desc}`);
    } else {
      fenxi.push('【动爻】六爻安静，无动爻');
    }

    if (yongshen_type && yongshen_type !== '六亲') {
      const yongshen_yaos = yaos_shunxu.filter(y => y['liuqin'] === yongshen_type);
      if (yongshen_yaos.length) {
        fenxi.push(`【用神】取${yongshen_type}爻为用神`);
        for (const y of yongshen_yaos) {
          const status = miao_yao_zhuangtai(y, yue, ri_z);
          const pos_name = num_to_cn(y['pos']) + '爻';
          const mark = [];
          if (y['is_shi']) mark.push('持世');
          if (y['is_ying']) mark.push('临应');
          if (y['is_dong']) mark.push('动爻');
          if (y['is_kong']) mark.push('旬空');
          if (y['is_po']) mark.push('月破');
          const mark_str = mark.length ? '（' + mark.join('、') + '）' : '';
          fenxi.push(`  ${pos_name} ${y['liushen']} ${y['liuqin']}${y['zhi']}${y['wuxing']}${mark_str}：${status}`);
        }
      } else {
        fenxi.push(`【用神】卦中不见${yongshen_type}爻，需寻伏神`);
      }
    }

    const shi_yao = yaos_shunxu.find(y => y['is_shi']) || null;
    if (shi_yao) {
      const shi_status = miao_yao_zhuangtai(shi_yao, yue, ri_z);
      const dong_mark = shi_yao['is_dong'] ? '，动爻' : '，安静';
      const kong_mark = shi_yao['is_kong'] ? '，旬空' : '';
      const po_mark = shi_yao['is_po'] ? '，月破' : '';
      fenxi.push(`【世爻】${num_to_cn(shi_yao['pos'])}爻 ${shi_yao['liushen']} ${shi_yao['liuqin']}${shi_yao['zhi']}${shi_yao['wuxing']}${dong_mark}${kong_mark}${po_mark}：${shi_status}`);
    }

    if (dong && dong.length) {
      const guanxi_lines = [];
      const dong_yaos_data = yaos_shunxu.filter(y => y['is_dong']);
      for (const dy of dong_yaos_data) {
        const dy_wx = dy['wuxing'];
        const rels = [];
        if (shi_yao) {
          const rel = get_wuxing_relation(dy_wx, shi_yao['wuxing']);
          if (rel === '生') rels.push(`动爻${dy['liuqin']}${dy['zhi']}生世爻`);
          else if (rel === '克') rels.push(`动爻${dy['liuqin']}${dy['zhi']}克世爻`);
          else if (rel === '同') rels.push(`动爻${dy['liuqin']}${dy['zhi']}助世爻`);
        }
        if (paipan['bian_gua']) {
          const b_yaos_shunxu = paipan['bian_gua']['yaos'].slice().reverse();
          const b_y = b_yaos_shunxu.find(b => b['pos'] === dy['pos']) || null;
          if (b_y) {
            const b_rel = get_wuxing_relation(b_y['wuxing'], dy_wx);
            const biao = `（变${b_y['liuqin']}${b_y['zhi']}）`;
            if (b_rel === '生') rels.push(`化回头生${biao}`);
            else if (b_rel === '克') rels.push(`化回头克${biao}`);
            else if (b_rel === '同') {
              const jin_tui = hua_jin_tui(dy['zhi'], b_y['zhi']);
              rels.push(`${jin_tui}${biao}`);
            }
          }
        }
        if (rels.length) guanxi_lines.push(`  ${num_to_cn(dy['pos'])}爻动：${rels.join('；')}`);
      }
      if (guanxi_lines.length) fenxi.push('【动爻作用】\n' + guanxi_lines.join('\n'));
    }
    return fenxi;
  }

  // ================= 墓绝长生 =================
  const _MUKU = { '木': '未', '火': '戌', '金': '丑', '水': '辰', '土': '辰' };
  const _JUEDI = { '木': '申', '火': '亥', '金': '寅', '水': '巳', '土': '巳' };
  const _CHANGSHENG = { '木': '亥', '火': '寅', '金': '巳', '水': '申', '土': '申' };

  function _yao_by_pos(paipan, pos) {
    return paipan['yaos'].find(y => y['pos'] === pos) || null;
  }
  function _bian_by_pos(paipan, pos) {
    if (!paipan['bian_gua']) return null;
    return paipan['bian_gua']['yaos'].find(y => y['pos'] === pos) || null;
  }

  // ================= 爻旺衰评分 =================
  function yao_wangshuai(yao, paipan) {
    const wx = yao['wuxing'];
    const yue = paipan['yue_zhi'];
    const ri = paipan['ri_zhi'];
    let score = 0.0;
    let yue_desc = '';
    let ri_desc = '';

    if (yue) {
      if (yao['zhi'] === yue) {
        score += 3; yue_desc = '临月建（值月）而旺';
      } else {
        const yue_wx = DIZHI_WUXING[yue];
        const rel = get_wuxing_relation(yue_wx, wx);
        if (rel === '同') { score += 1.5; yue_desc = '得月建比扶（同气）'; }
        else if (rel === '生') { score += 2; yue_desc = '得月建相生（相）'; }
        else if (rel === '克') { score -= 2; yue_desc = '被月建所克'; }
        else if (rel === '被生') { score -= 1; yue_desc = '爻生月建而泄'; }
        else if (rel === '被克') { score -= 1; yue_desc = '爻克月建而囚'; }
      }
    }

    let ri_he = false, ri_chong = false;
    if (ri) {
      if (yao['zhi'] === ri) {
        score += 2.5; ri_desc = '临日建（值日）而旺';
      } else {
        const ri_wx = DIZHI_WUXING[ri];
        const rel = get_wuxing_relation(ri_wx, wx);
        if (rel === '同') { score += 1; ri_desc = '得日辰比扶（同气）'; }
        else if (rel === '生') { score += 1.5; ri_desc = '得日辰相生'; }
        else if (rel === '克') { score -= 2; ri_desc = '被日辰所克'; }
        else if (rel === '被生') { score -= 0.5; ri_desc = '爻生日辰而泄'; }
      }
      ri_he = (LIUHE[ri] === yao['zhi']);
      ri_chong = (LIUCHONG[ri] === yao['zhi']);
      if (ri_he) score += 0.5;
      if (ri_chong) {
        if (yao['is_dong']) {
          ri_desc = (ri_desc + '、逢日冲则散').replace(/^、/, '');
        } else if (yao['is_kong']) {
          ri_desc = (ri_desc + '、空逢日冲为冲实').replace(/^、/, '');
          score += 1;
        } else {
          score += 1;
          ri_desc = (ri_desc + '、静逢日冲为暗动').replace(/^、/, '');
        }
      }
    }

    const dong_sheng = [], dong_ke = [], dong_bi = [];
    for (const other of paipan['yaos']) {
      if (!other['is_dong'] || other['pos'] === yao['pos']) continue;
      const rel = get_wuxing_relation(other['wuxing'], wx);
      const label = `${num_to_cn(other['pos'])}爻${other['liuqin']}${other['zhi']}`;
      if (rel === '生') { dong_sheng.push(label); score += 1.5; }
      else if (rel === '克') { dong_ke.push(label); score -= 2; }
      else if (rel === '同') { dong_bi.push(label); score += 0.5; }
    }

    let mu = '', jue = '', cs = '';
    const mu_zhi = _MUKU[wx], jue_zhi = _JUEDI[wx], cs_zhi = _CHANGSHENG[wx];
    const cand = [['日辰', ri]];
    for (const other of paipan['yaos']) {
      if (other['is_dong'] && other['pos'] !== yao['pos'])
        cand.push([`${num_to_cn(other['pos'])}爻动`, other['zhi']]);
    }
    const by = _bian_by_pos(paipan, yao['pos']);
    if (yao['is_dong'] && by) cand.push(['化出', by['zhi']]);
    const wang_xiang = score >= 2 && !yao['is_po'] && !yao['is_kong'];
    for (const [src, zhi] of cand) {
      if (!zhi) continue;
      if (zhi === mu_zhi && !mu) { if (src === '化出' || !wang_xiang) mu = src; }
      if (zhi === jue_zhi && !jue) { if (src === '化出' || !wang_xiang) jue = src; }
      if (zhi === cs_zhi && !cs) cs = src;
    }
    if (mu) score -= 1;
    if (jue) score -= 1.5;
    if (cs) score += 1;

    if (yao['is_po']) score -= 2;
    if (yao['is_kong']) score -= 1.5;

    let level;
    if (score >= 4) level = '旺相';
    else if (score >= 2) level = '有气';
    else if (score >= 0) level = '平和';
    else if (score >= -2) level = '休囚';
    else level = '无气';

    return {
      score, level, yue: yue_desc, ri: ri_desc, ri_he, ri_chong,
      dong_sheng, dong_ke, dong_bi, mu, jue, changsheng: cs
    };
  }

  // ================= 伏神 =================
  function find_fushen(paipan, yongshen_type) {
    const gong = paipan['gong'];
    const gong_wx = BAGUA[gong]['wuxing'];
    const nazhi = BAGUA[gong]['nazhi_nei'].concat(BAGUA[gong]['nazhi_wai']);
    for (let idx = 0; idx < nazhi.length; idx++) {
      const zhi = nazhi[idx];
      const lq = get_liuqin(gong_wx, DIZHI_WUXING[zhi]);
      if (lq === yongshen_type) {
        const pos = idx + 1;
        const fei = _yao_by_pos(paipan, pos);
        return { pos, zhi, wuxing: DIZHI_WUXING[zhi], liuqin: lq, feishen: fei };
      }
    }
    return null;
  }

  // ================= 三合局 =================
  function sanhe_ju(paipan) {
    const ju_list = [];
    const dong_zhi = {};
    for (const y of paipan['yaos']) if (y['is_dong']) dong_zhi[y['zhi']] = `${num_to_cn(y['pos'])}爻动`;
    const ri = paipan['ri_zhi'];
    const yue = paipan['yue_zhi'];
    for (const [trio, wx] of SANHE) {
      const have = [], sources = [];
      for (const z of trio) {
        if (z in dong_zhi) { have.push(z); sources.push(dong_zhi[z]); }
      }
      const missing = trio.filter(z => !(z in dong_zhi));
      let fill = '';
      if (have.length === 3) {
        fill = '三爻动会局';
      } else if (have.length === 2 && (missing.indexOf(ri) >= 0 || missing.indexOf(yue) >= 0)) {
        const fillz = missing.indexOf(ri) >= 0 ? ri : yue;
        have.push(fillz);
        sources.push(fillz === ri ? '日辰' : '月建');
        fill = '两爻动得日/月补局';
      }
      if (have.length === 3) ju_list.push({ wuxing: wx, zhi: trio, src: sources, kind: fill });
    }
    return ju_list;
  }

  // ================= 财世向背 =================
  function _qincai_shiji(cais, shi) {
    if (!cais || !cais.length) return [null, ''];
    const shi_wx = shi['wuxing'];
    const rels = [];
    for (const c of cais) {
      const cwx = c['wuxing'];
      let chonghe = '';
      if (LIUHE[c['zhi']] === shi['zhi']) chonghe = '六合';
      else if (LIUCHONG[c['zhi']] === shi['zhi']) chonghe = '相冲';
      if (c['is_shi']) {
        rels.push(['持世', c, '财爻持世']);
      } else {
        const r = get_wuxing_relation(cwx, shi_wx);
        if (r === '生') {
          rels.push(['生世', c, `财爻${c['zhi']}生世爻` + (chonghe === '六合' ? `、与世${chonghe}` : '')]);
        } else if (r === '克') {
          rels.push(['克世', c, `财爻${c['zhi']}克世爻（物来寻我，财来就我）` + (chonghe ? `、与世${chonghe}` : '')]);
        } else if (r === '同') {
          rels.push(['比世', c, `财爻${c['zhi']}与世比和`]);
        } else {
          const r2 = get_wuxing_relation(shi_wx, cwx);
          if (r2 === '生') rels.push(['世生财', c, `世爻生财爻${c['zhi']}（我去生财，须费力）`]);
          else if (r2 === '克') rels.push(['世克财', c, `世爻克财爻${c['zhi']}（我去寻财，求之难）`]);
          else rels.push(['无关', c, `财爻${c['zhi']}与世无直接生克`]);
        }
      }
    }
    const order = { '持世': 0, '生世': 1, '克世': 2, '比世': 3, '世生财': 4, '世克财': 5, '无关': 6 };
    rels.sort((a, b) => (order[a[0]] - order[b[0]]) || (a[1]['is_dong'] ? 0 : 1) - (b[1]['is_dong'] ? 0 : 1));
    return [rels[0][0], rels[0][2]];
  }

  // 求财六亲化意象
  const HUA_QIN_CAI = {
    '子孙|妻财': '福神化财，利源不竭，大吉',
    '妻财|子孙': '财化福德，财源有继，绵绵得利',
    '官鬼|妻财': '官鬼化财，若生合世身最利公门谒贵、九流求财，克世则否',
    '兄弟|妻财': '兄弟化财，先散后聚、先难后得，利在最后',
    '父母|妻财': '父母化财，辛勤劳苦而后有得',
    '妻财|官鬼': '财化官鬼，因财生忧、耗折惊惶，世伤恐因财致祸，凶',
    '妻财|兄弟': '财化兄弟，得而复失，被人分夺劫耗，凶',
    '妻财|父母': '财化父母，主因文书、宅舍、长辈或劳碌而耗财，且克财源',
    '子孙|官鬼': '福神化鬼，乐极生忧、财源化祸，求财不利',
    '子孙|父母': '子孙化父母，财源被克伤、福神受损，利源断绝',
    '子孙|兄弟': '兄弟生子孙，财源得助；然兄弟终为分财之神，吉凶相半',
    '兄弟|官鬼': '兄弟化官鬼，劫财之神受制，不能夺财，反吉',
    '兄弟|子孙': '兄弟化子孙，兄生子、子生财，连环生益，先阻后得',
    '兄弟|父母': '兄弟化父母，父母生兄弟，劫财更盛，凶',
    '官鬼|子孙': '官鬼化子孙，忧解福生、阻滞消散，求财反吉',
    '官鬼|兄弟': '官鬼化兄弟，阻扰未除又逢分财争夺，凶',
    '官鬼|父母': '官鬼化父母，父母生官，阻隔劳扰益甚',
    '父母|官鬼': '父母化官鬼，劳碌中生忧惊阻隔，求财费力',
    '父母|兄弟': '父母化兄弟，生助劫财之神，不利求财',
    '父母|子孙': '父母化子孙，仇神化福，财源由阻而通，先劳后利'
  };

  function _liuqin_wuxing(gong_wx, qin) {
    if (qin === '兄弟') return gong_wx;
    if (qin === '妻财') return WUXING_KE[gong_wx];
    if (qin === '子孙') return WUXING_SHENG[gong_wx];
    if (qin === '官鬼') {
      for (const x in WUXING_KE) if (WUXING_KE[x] === gong_wx) return x;
    }
    if (qin === '父母') {
      for (const x in WUXING_SHENG) if (WUXING_SHENG[x] === gong_wx) return x;
    }
    return null;
  }

  function _yao_brief(y, paipan) {
    const st = yao_wangshuai(y, paipan);
    const marks = [];
    if (y['is_shi']) marks.push('持世');
    if (y['is_ying']) marks.push('临应');
    if (y['is_dong']) marks.push('发动');
    if (y['is_kong']) marks.push('旬空');
    if (y['is_po']) marks.push('月破');
    if (st['mu']) marks.push(`入墓(${st['mu']})`);
    if (st['jue']) marks.push(`逢绝(${st['jue']})`);
    const mk = marks.length ? '（' + marks.join('、') + '）' : '';
    return [`${num_to_cn(y['pos'])}爻${y['liushen']}${y['liuqin']}${y['zhi']}${y['wuxing']}${mk}【${st['level']}】`, st];
  }

  // ================= 求财专断 =================
  function _cai_yingqi(paipan, cais, fushen, shi, cai_wx) {
    const q = [];
    const yue = paipan['yue_zhi'], ri = paipan['ri_zhi'];
    if (!cais.length && fushen) {
      const chong_fei = LIUCHONG[fushen['feishen']['zhi']] || '';
      q.push(`伏财${fushen['zhi']}：待财爻值日（${fushen['zhi']}日）、或冲开飞神（${chong_fei}日）、或日月引拔之时得财。`);
      return q;
    }
    if (!cais.length) return q;
    const keyf = y => {
      const s = yao_wangshuai(y, paipan);
      return [y['is_shi'] ? 1 : 0, y['is_dong'] ? 1 : 0, s['score']];
    };
    let y = cais[0];
    for (const c of cais) {
      const kc = keyf(c), ky = keyf(y);
      if (kc[0] > ky[0] || (kc[0] === ky[0] && kc[1] > ky[1]) ||
          (kc[0] === ky[0] && kc[1] === ky[1] && kc[2] > ky[2])) y = c;
    }
    const s = yao_wangshuai(y, paipan);
    const chong = LIUCHONG[y['zhi']] || '';
    const he = LIUHE[y['zhi']] || '';
    if (y['is_kong']) {
      q.push(`财爻${y['zhi']}旬空：旺者出旬后逢${y['zhi']}（值日）或${chong}（冲实）日得；衰者难。`);
    } else if (y['is_po']) {
      q.push(`财爻${y['zhi']}月破：待填实（${y['zhi']}日）或逢合（${he}日）得。`);
    } else if (s['mu']) {
      const chong_mu = LIUCHONG[_MUKU[y['wuxing']]] || '';
      q.push(`财入墓于${_MUKU[y['wuxing']]}：待冲墓（${chong_mu}日）或冲财（${chong}日）得。`);
    } else if (y['is_dong'] && (s['ri_he'] ||
        paipan['yaos'].some(o => LIUHE[o['zhi']] === y['zhi'] && o['is_dong']))) {
      q.push(`财动被合住（绊住）：待冲开（${chong}日）得财；合住如财被人把住，冲日方到我手。`);
    } else if (y['is_dong']) {
      if (s['jue']) {
        q.push(`动财逢绝：待长生/生旺财爻之日（如${_CHANGSHENG[y['wuxing']]}日及生${y['wuxing']}之日）得。`);
      } else {
        q.push(`财爻发动：逢值（${y['zhi']}日）或逢合（${he}日）得；动而克世者来尤速。`);
      }
    } else {
      if (s['ri_he']) {
        q.push(`静财逢日辰六合为「合起」（暗助旺相）：逢冲（${chong}日）、逢值（${y['zhi']}日）得财。`);
      } else if (s['level'] === '旺相' || s['level'] === '有气') {
        q.push(`财爻安静有气：逢冲（${chong}日）暗动得财，或逢值（${y['zhi']}日）得。`);
      } else {
        q.push(`财爻安静休囚：待生旺财爻之月日（生${y['wuxing']}或${y['wuxing']}旺之月日），逢冲（${chong}日）、逢值（${y['zhi']}日）方得。`);
      }
    }
    q.push('（应期以地支日推，具体公历日期请查万年历最近的相应地支日；近事以日断，远事以月断。）');
    return q;
  }

  function fenxi_caiyun(paipan) {
    const L = [];
    const yx = paipan['yaos'].slice().reverse();
    const yue = paipan['yue_zhi'], ri = paipan['ri_zhi'];
    const gong_wx = paipan['gong_wuxing'];
    const dong = paipan['dong_yao'];
    const shi = yx.find(y => y['is_shi']);
    const ying = yx.find(y => y['is_ying']) || null;

    const cais = yx.filter(y => y['liuqin'] === '妻财');
    const zis = yx.filter(y => y['liuqin'] === '子孙');
    const xiongs = yx.filter(y => y['liuqin'] === '兄弟');
    const guans = yx.filter(y => y['liuqin'] === '官鬼');
    const fus = yx.filter(y => y['liuqin'] === '父母');

    const cai_wx = cais.length ? cais[0]['wuxing'] : _liuqin_wuxing(gong_wx, '妻财');
    const zi_wx = zis.length ? zis[0]['wuxing'] : _liuqin_wuxing(gong_wx, '子孙');

    const st_of = y => yao_wangshuai(y, paipan);
    const cai_sts = cais.map(y => [y, st_of(y)]);
    const zi_sts = zis.map(y => [y, st_of(y)]);
    const xiong_sts = xiongs.map(y => [y, st_of(y)]);
    const guan_sts = guans.map(y => [y, st_of(y)]);
    const fu_sts = fus.map(y => [y, st_of(y)]);
    const shi_st = st_of(shi);

    const xiong_bei_zhi = xy => {
      if (ri && get_wuxing_relation(DIZHI_WUXING[ri], xy['wuxing']) === '克') return true;
      for (const g of guans) {
        if (g['is_dong'] && !g['is_kong'] && !g['is_po'] &&
            ['旺相', '有气', '平和'].indexOf(st_of(g)['level']) >= 0 &&
            get_wuxing_relation(g['wuxing'], xy['wuxing']) === '克') return true;
      }
      return false;
    };

    let fushen = null;
    if (!cais.length) fushen = find_fushen(paipan, '妻财');

    // 伏神相关（无现财时）
    let yue_rel = '无', ri_rel = '无';
    if (fushen) {
      if (yue) yue_rel = get_wuxing_relation(DIZHI_WUXING[yue], fushen['wuxing']);
      if (ri) ri_rel = get_wuxing_relation(DIZHI_WUXING[ri], fushen['wuxing']);
    }

    let head = `【卦象】${paipan['name']}（${paipan['gong']}宫${paipan['gongwei']}，${gong_wx}）`;
    if (paipan['bian_gua']) head += ` 之 ${paipan['bian_gua']['name']}`;
    L.push(head);
    L.push(`【日月】月建${yue}${DIZHI_WUXING[yue]}　日辰${paipan['ri_gan']}${ri}${DIZHI_WUXING[ri]}　旬空${paipan['xunkong'][0]}${paipan['xunkong'][1]}`);
    L.push(`【动爻】` + (dong.length ? dong.map(d => `${num_to_cn(d)}爻动`).join('、') : '六爻安静，无动爻'));

    L.push('【一、《黄金策·商贾》论求财（经典）】');
    L.push('· 总纲：「居货曰贾，行货曰商，总为资生之计……要问吉凶，但看财福——财为本，福为利，二者不可损坏。」卦中子孙之爻称曰福神，乃财之根源。');
    L.push('· 六亲取用：妻财为禄神（所求之财）；子孙为福德、为财源（子孙生财）；兄弟为劫财之神（克财）；父母为仇神（克子孙、生兄弟，坏财源）；官鬼能制兄弟以护财，然发动又主阻隔耗财、忧惊。');

    const _CAI_JING = [
      ['居货曰贾，行货曰商，总为资生之计，要问吉凶，但看财福，财为本、福为利，二者不可损坏',
       '商贾求财，只看妻财（财）与子孙（福）两爻；财是本钱、福是利润，二者皆不宜被伤克；子孙是财之根源。'],
      ['财旺福兴，无问公私皆称意；财空福绝，不拘营运总违心',
       '财爻旺、子孙兴，无论公干私商皆称心；财空、福绝，做什么买卖都违心。'],
      ['有福无财，兄弟交重偏有望',
       '有子孙财源而财暂不现，兄弟发动去生子孙，财源愈厚，连环相生（兄生子、子生财），反有得财之望。'],
      ['有财无福，官爻发动亦堪求',
       '财现而子孙不现，财无生气，一遇兄弟便被劫夺；须得官鬼发动（或日辰为官）克制兄弟、护住财，亦可求谋。'],
      ['财福俱无，何异守株而待兔',
       '卦中财爻、子孙皆不现，财源两失，妄求无益，如守株待兔；若有拱扶伏神，待值日亦有得。'],
      ['父兄皆动，无殊缘木以求鱼',
       '父母克子孙、生兄弟，父兄俱动，财源被坏、劫夺又兴，求之不得，如缘木求鱼。'],
      ['身遇旺财，似取囊中之物',
       '世为求财之人，世临旺财，求财如取囊中之物，虽无气亦主易得，旺相尤美。'],
      ['世持动弟，如捞水底之针',
       '兄弟持世发动，如同水底捞针，不拘何买卖皆主破财难遂；安静尚难，发动尤甚。'],
      ['财来就我终须易，我去寻财必是难',
       '财爻生合世、持世、克世，皆为财来就我，求之易得；财与世不相干，乃我去寻财，必难。'],
      ['福变财生，滚滚利源不竭',
       '子孙发动又化财、财又生合世身，利源滚滚，绵绵不绝；财化子孙亦同。'],
      ['财化鬼兄，防耗折而惊忧',
       '财爻化官鬼、化兄弟最凶，主损财、驳耗、忧惊；世爻若再受伤，恐因财致祸。'],
      ['财局会福神，万倍利源可许',
       '三合会成财局、福局，动来生合世身，更得财旺，可许厚利。'],
      ['多财反复，必须墓库以收藏',
       '财爻叠现太过，其财反复难求；须得财之库爻持世临身，谓之财有收藏，方得厚利。'],
      ['无鬼分争，又怕交重而阻滞',
       '无官鬼克制兄弟，则兄弟专权分争、劫财；兄弟交重发动，又主阻滞、耗散。'],
      ['应空难靠他人，世空有财难得',
       '应爻为交易、合伙之人，应空则彼方不实、虚约难凭；世爻空，自己谋为不实、心退悔，纵有财亦难入手。'],
      ['月带财神，卦中无而月中必有',
       '月建为提纲而带财爻，虽正卦无财，伏财亦明，月内可求。'],
      ['鬼克身爻，商贩者必遭盗贼',
       '官鬼临玄武发动来克世，商贩远行须防盗贼之祸。'],
      ['路上有官休出外，宅中有鬼莫居家',
       '官鬼动而克世，路上有官则不可出外，宅中有鬼则不可居家，出行经商宜避。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _CAI_JING) L.push(`　· 「${_j}」——${_s}`);

    L.push('· 本卦特别贴合之经文：');
    const cai_wang = cai_sts.some(([y, s]) => ['旺相', '有气'].indexOf(s['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const cai_kong_po = cais.some(y => y['is_kong'] || y['is_po']);
    const zi_dong_wang = zi_sts.some(([y, s]) => y['is_dong'] && ['旺相', '有气', '平和'].indexOf(s['level']) >= 0);
    const zi_shang = zi_sts.some(([y, s]) => s['dong_ke'].length ||
        s['yue'].indexOf('被月') === 0 || s['ri'].indexOf('被日') === 0) ||
      fu_sts.some(([f]) => f['is_dong']);
    const xiong_dong = xiongs.some(y => y['is_dong']);
    const xiong_wu_zhi = xiong_sts.some(([y, s]) => y['is_dong'] &&
        ['旺相', '有气'].indexOf(s['level']) >= 0 && !xiong_bei_zhi(y) &&
        !zis.some(z => z['is_dong']));
    const fu_dong = fus.some(y => y['is_dong']);
    const fu_xiong_dong = fu_dong && xiong_dong;
    const guan_dong = guans.some(y => y['is_dong']);
    const shi_xiong = shi['liuqin'] === '兄弟';
    const cai_duo = cais.length >= 3;

    const [xiangbei, xiangbei_desc] = cais.length ? _qincai_shiji(cais, shi) : [null, ''];

    const bian_info = [];
    for (const y of yx) {
      if (!y['is_dong']) continue;
      const by = _bian_by_pos(paipan, y['pos']);
      if (!by) continue;
      const b_qin = get_liuqin(gong_wx, by['wuxing']);
      const rel = get_wuxing_relation(by['wuxing'], y['wuxing']);
      const hui = rel === '生' ? '回头生' : (rel === '克' ? '回头克' : '');
      const jt = rel === '同' ? hua_jin_tui(y['zhi'], by['zhi']) : '';
      bian_info.push([y, by, b_qin, hui, jt]);
    }

    const ju = sanhe_ju(paipan);
    const cai_ju = ju.filter(j => j['wuxing'] === cai_wx);
    const fu_ju = ju.filter(j => j['wuxing'] === zi_wx);
    const zi_hua_xiong = bian_info.some(([y, b, bq]) => y['liuqin'] === '子孙' && (bq === '官鬼' || bq === '父母'));
    const zi_huike = bian_info.some(([y, b, bq, h]) => y['liuqin'] === '子孙' && h === '回头克');

    if (cai_wang && zi_dong_wang) {
      L.push('· 「财旺福兴，无问公私皆称意；财空福绝，不拘营运总违心」——财爻旺相、子孙发动，公私之谋皆称意；财被伤克、临墓绝无救，则买卖违心。');
    } else if (!cais.length && !zis.length) {
      L.push('· 「财福俱无，何异守株而待兔」——卦中财爻、子孙俱不现，财源两失，妄求无益；若拱扶所伏之神，待值日亦有得。');
    }
    if (['持世', '生世', '克世'].indexOf(xiangbei) >= 0 && cai_wang) {
      L.push('· 「财来就我终须易，我去寻财必是难」——财爻生合世爻、持世克世，皆为财来就我，求之易得；财与世不相干，乃我去寻财，必难。');
    }
    if (xiangbei === '持世' && shi['liuqin'] === '妻财') {
      L.push('· 「身遇旺财，似取囊中之物」——世为求财之人，世临财爻，虽无气亦主易得，旺相尤美。');
    }
    if (shi_xiong) {
      L.push('· 「身或兄临，必难求望」「世持动弟，如捞水底之针」——兄弟持世临身，不拘何买卖皆主破财难遂，安静尚难，发动尤甚。');
    }
    const fubian = bian_info.some(([y, b, bq]) => y['liuqin'] === '子孙' && bq === '妻财');
    const cai_bian_zi = bian_info.some(([y, b, bq]) => y['liuqin'] === '妻财' && bq === '子孙');
    if (fubian || cai_bian_zi || (zi_dong_wang && !zi_hua_xiong && cai_wang)) {
      L.push('· 「福变财生，滚滚利源不竭」——子孙发动，利必久远；更兼财爻生合世身，乃绵绵不绝之象，财化子孙亦同。');
    }
    if (zi_hua_xiong || zi_huike) {
      L.push('· 子孙为财之根源、解忧之福神，若发动而化官鬼、化父母或回头克，是福神受伤、财源化祸，不唯利薄，且恐因财生忧，《千金赋》所谓「子虽福德，多反无功」。');
    }
    const cai_hua_xiong = bian_info.some(([y, b, bq]) => y['liuqin'] === '妻财' && (bq === '官鬼' || bq === '兄弟'));
    if (cai_hua_xiong) {
      L.push('· 「财化鬼兄，防耗折而惊忧」——财爻化官鬼、化兄弟最凶，主损财驳耗；世爻若再受伤，恐因财致祸。');
    }
    if (xiong_dong && zi_dong_wang) {
      L.push('· 「有福无财，兄弟交重偏有望」——子孙发动无伤，财源本厚，兄弟发动反生扶子孙，连环相生（兄生子、子生财），其财根深蒂固。');
    } else if (xiong_wu_zhi) {
      L.push('· 兄弟乃占财之忌神，发动则克财劫夺、分财散物；「无鬼分争，又怕交重而阻滞」，无官鬼制之，则兄弟专权，财虽有气亦多虚耗。');
    }
    if (fu_xiong_dong) {
      L.push('· 「父兄皆动，无殊缘木以求鱼」——父母克子孙、生兄弟，父兄俱动，财源被坏、劫夺又兴，必不能得。');
    } else if (fu_dong && zis.length) {
      L.push('· 父母为仇神，发动则克伤子孙（财源），福神受伤，利源不畅。');
    }
    if ((!zis.length || zis.every(y => y['is_kong'])) && guan_dong && cais.length) {
      L.push('· 「有财无福，官爻发动亦堪求」——子孙藏伏，财无生气，一遇兄弟便被劫夺；须得官爻发动、或日辰为官克制兄弟，亦可求谋（然有子孙而官鬼动，又主阻滞）。');
    }
    if (cai_ju.length || fu_ju.length) {
      L.push('· 「财局会福神，万倍利源可许」——三合会成财局、福局动来生合世身，财利绵绵，更得财旺，可许厚利。');
    }
    if (cai_duo) {
      L.push('· 「多财反复，必须墓库以收藏」——卦中财爻叠现太过，其财反复难求；须得财之库爻持世临身，谓之财有收藏，方得厚利。');
    }
    if (shi['is_kong']) {
      L.push('· 「世空有财难得」「心退悔兮世空」——世爻旬空，自己心虚怠惰、谋为不实，纵有财亦难入手。');
    }
    if (ying && ying['is_kong']) {
      L.push('· 「应空难靠他人」——应爻为交易之人、合伙之伴，应空则彼方不实，虚约难凭。');
    }
    if (guan_dong && !cai_ju.length) {
      L.push('· 占财皆忌官鬼发动，主阻隔、耗财、忧惊；唯求公门之财、九流艺术之财，反宜官鬼旺相生合世身。');
    }
    const xuanwu_guan_ke_shi = yx.some(y => y['is_dong'] && y['liushen'] === '玄武' && y['liuqin'] === '官鬼' &&
      get_wuxing_relation(y['wuxing'], shi['wuxing']) === '克');
    if (xuanwu_guan_ke_shi) {
      L.push('· 「鬼克身爻，商贩者必遭盗贼」——官鬼临玄武发动来克世，须防盗贼之祸。');
    }
    if (!cais.length && yue && DIZHI_WUXING[yue] === cai_wx) {
      L.push('· 「月带财神，卦中无而月中必有」——月建为提纲而带财，虽正卦无财，伏财亦明，月内可求。');
    }

    L.push('【二、本卦财福逐条详断】');
    L.push('（1）用神·妻财爻（所求之财）');
    if (cais.length) {
      for (const [y, s] of cai_sts) {
        const [brief] = _yao_brief(y, paipan);
        const detail = [`月建：${s['yue'] || '无涉'}`, `日辰：${s['ri'] || '无涉'}`];
        if (s['dong_sheng'].length) detail.push('受动爻生：' + s['dong_sheng'].join('、'));
        if (s['dong_ke'].length) detail.push('受动爻克：' + s['dong_ke'].join('、'));
        if (s['mu']) detail.push(`入墓于${s['mu']}，主阻滞，待冲墓冲财之日方得`);
        if (s['jue']) detail.push(`逢绝于${s['jue']}，须逢生旺`);
        if (y['is_kong']) {
          if (s['score'] >= 2) detail.push('旺相而空为「真空/假空」之辨——旺空待出旬值日即得');
          else detail.push('衰弱又空，为真空，求财难就');
        }
        if (y['is_po']) detail.push('月破之财，须出月填实、逢合之日方有');
        L.push('　· ' + brief + '：' + detail.join('；') + '。');
      }
    } else {
      L.push('　· 卦中不见妻财爻，用神不上卦。');
      if (fushen) {
        const fs = fushen;
        const fei = fs['feishen'];
        const fs_wx = fs['wuxing'];
        const yue_r = yue ? get_wuxing_relation(DIZHI_WUXING[yue], fs_wx) : '无';
        const ri_r = ri ? get_wuxing_relation(DIZHI_WUXING[ri], fs_wx) : '无';
        const tian = [];
        if (yue_r === '同' || yue_r === '生') tian.push('得月建生扶');
        if (ri_r === '同' || ri_r === '生') tian.push('得日辰生扶');
        if (paipan['xunkong'].indexOf(fs['zhi']) >= 0) tian.push('伏神又逢旬空');
        const fei_rel = get_wuxing_relation(fei['wuxing'], fs_wx);
        const fei_map = {
          '生': '飞神生伏神，伏得生扶而易出，为吉',
          '克': '飞神克伏神（伤身），伏神被压难出，求财尤难',
          '被生': '伏神生飞神，伏神泄气于飞，亦难出现',
          '被克': '伏神克飞神，为「出暴」，伏神易出而事机急暴、乍起乍落',
          '同': '飞伏比和相助，伏神易出'
        };
        const fei_text = fei_map[fei_rel] || '飞伏无克，待时可出';
        L.push(`　· 于本宫${paipan['gong']}卦寻得伏神：${num_to_cn(fs['pos'])}爻妻财${fs['zhi']}${fs_wx}，伏于${num_to_cn(fei['pos'])}爻飞神「${fei['liuqin']}${fei['zhi']}${fei['wuxing']}」之下。`);
        L.push('　· 伏神须待日辰、动爻生扶拱合，或冲开飞神、伏神值日出现方可得财；' +
          (tian.length ? tian.join('、') : '伏神目前不得日月生扶') + '；' + fei_text + '。');
      } else {
        L.push('　· 本宫亦寻伏财不得，财毫无根，求财大不利（可参看月建、日辰是否带财）。');
      }
    }

    L.push('（2）财与求财之人（世爻）向背');
    const [shi_brief] = _yao_brief(shi, paipan);
    L.push('　· 世爻（我）：' + shi_brief);
    if (cais.length) {
      const beishu = {
        '持世': '财来就我', '生世': '财来就我', '克世': '财来就我',
        '比世': '财我比和', '世生财': '我去寻财', '世克财': '我去寻财', '无关': '财我无关'
      };
      L.push(`　· 向背：${xiangbei_desc}——${beishu[xiangbei] || ''}。`);
      if (['持世', '生世', '克世'].indexOf(xiangbei) >= 0) {
        L.push('　· 财来就我，如物来寻我，不劳多求而自得；唯须财爻有气、不空不破。');
      } else if (['世生财', '世克财', '无关'].indexOf(xiangbei) >= 0) {
        L.push('　· 我去寻财，应 beishu 逻辑略');
      }
    }
    if (ying) {
      const [yb] = _yao_brief(ying, paipan);
      L.push('　· 应爻（交易/合伙之人）：' + yb + (ying['is_kong'] ? '；应空则对方不实、合约难凭。' : '。'));
    }

    L.push('（3）福神·子孙爻（财源）');
    if (zis.length) {
      for (const [y, s] of zi_sts) {
        const [brief] = _yao_brief(y, paipan);
        const notes = [];
        if (y['is_dong']) {
          if (s['ri_he']) {
            notes.push('子孙发动而被日辰合住，「动值合而绊住」，暂不能生财，待冲开之日方有');
          } else if (yx.some(o => LIUHE[o['zhi']] === y['zhi'] && o['is_dong'])) {
            notes.push('子孙动被他爻合绊，待冲日方生财');
          } else {
            notes.push('子孙发动，财源流动，能生妻财，为求财之吉象');
          }
        } else {
          if (s['ri_chong']) notes.push('子孙安静而逢日冲，为暗动，暗动亦能生财');
          else notes.push('子孙安静，财源未动，待日月冲起（暗动）或发动，方能生财');
        }
        if (s['dong_ke'].length) notes.push('被' + s['dong_ke'].join('、') + '克伤，财源受损');
        if (fus.some(f => f['is_dong'])) notes.push('父母发动克子孙，财源受制（仇神动）');
        if (y['is_kong']) notes.push('子孙旬空，财源落空，出旬方有生气');
        if (s['level'] === '休囚' || s['level'] === '无气') notes.push('子孙休囚无气，财源浅薄，得日月动爻生扶则有源');
        L.push('　· ' + brief + '：' + notes.join('；') + '。');
      }
    } else {
      L.push('　· 卦中子孙不现，财源隐伏。有财则财无生气，一遇兄弟便被劫夺；须官鬼发动或日辰为官制兄，方可求。宜兼查伏神。');
    }

    L.push('（4）忌神·兄弟爻（劫财）');
    if (xiongs.length) {
      for (const [y, s] of xiong_sts) {
        const [brief] = _yao_brief(y, paipan);
        const notes = [];
        if (y['is_dong']) {
          if (zis.some(z => z['is_dong'])) {
            notes.push('兄弟虽动，喜子孙亦动，兄生子、子生财，反主财源根深（须防中分财之嫌）');
          } else if (xiong_bei_zhi(y)) {
            notes.push('兄弟发动本欲劫财，喜有官鬼动克、或日辰克之，忌神有制，劫财无力');
          } else {
            const qd = ['旺相', '有气'].indexOf(s['level']) >= 0 ? '旺动无制' : '发动而无制';
            notes.push(`兄弟${qd}（官鬼空破无力则同无制），必主劫夺分财、成本耗散，求财大忌`);
          }
        } else {
          notes.push('兄弟安静，暂不劫财；逢冲逢值之日须防破财');
        }
        if (y['is_shi']) notes.push('兄弟持世，自身为劫财之象，求财难遂');
        L.push('　· ' + brief + '：' + notes.join('；') + '。');
      }
    } else {
      L.push('　· 卦无兄弟，劫财之神不现，无人分夺，财可入手（唯兄伏待时亦防）。');
    }

    L.push('（5）官鬼（制兄·阻隔）与父母（克财源）');
    if (guans.length) {
      for (const [y, s] of guan_sts) {
        const [brief] = _yao_brief(y, paipan);
        let note = y['is_dong'] ? '官鬼发动' : '官鬼安静';
        if (y['is_dong']) {
          const wuli = (y['is_kong'] || y['is_po']) ? '（唯官鬼空破，制兄无力）' : '';
          if (xiongs.some(x => x['is_dong'])) {
            note += `，可制伏兄弟以护财${wuli}；然官动亦主阻隔、耗财、忧惊，吉凶相半`;
          } else {
            note += '，无兄弟可制，反主求财阻隔、关节耗财、意外惊忧';
          }
          if (get_wuxing_relation(y['wuxing'], shi['wuxing']) === '生') note += '；官生世，公门、九流艺术之财反吉';
          if (get_wuxing_relation(y['wuxing'], shi['wuxing']) === '克') note += '；官克世，助鬼伤身，因财致患';
        } else {
          note += '，静而有气则暗制兄弟，不为害';
        }
        L.push('　· ' + brief + '：' + note + '。');
      }
    } else {
      L.push('　· 卦无官鬼，兄弟易当权专夺，财多虚耗；然寻常小本经营无官亦不忌。');
    }
    if (fus.length) {
      const fd = fus.filter(y => y['is_dong']);
      if (fd.length) {
        L.push('　· 父母发动：' + fd.map(y => `${num_to_cn(y['pos'])}爻${y['zhi']}`).join('、') +
          '，克子孙、生兄弟，坏财源而助劫夺，主劳碌伤本。');
      }
    } else {
      L.push('　· 父母不现，财源不受伤，吉。');
    }

    L.push('（6）动爻变化吉凶');
    if (bian_info.length) {
      for (const [y, by, bq, hui, jt] of bian_info) {
        const seg = `　· ${num_to_cn(y['pos'])}爻${y['liuqin']}${y['zhi']}动，变${bq}${by['zhi']}`;
        const tags = [];
        if (hui) {
          const sheng = hui === '回头生';
          const role_txt = {
            '妻财': ['财得生益，吉', '财被回头克，求财大忌，凶'],
            '子孙': ['财源得益，吉', '财源被回头克伤，凶'],
            '兄弟': ['劫财之神得生，夺财更力，凶', '劫财之神被克，不能夺财，反吉'],
            '官鬼': ['官鬼得势，阻隔耗财更甚（唯公门、九流之财喜官旺）', '官鬼被克，阻隔消散，反吉'],
            '父母': ['仇神得势，克财源、生兄弟，凶', '仇神被克，财源得护，反吉']
          };
          tags.push(hui + '，' + role_txt[y['liuqin']][sheng ? 0 : 1]);
        }
        if (jt && jt !== '化比和') {
          const jin = jt === '化进神';
          const jt_txt = {
            '妻财': ['财势增进，吉', '财势衰退'],
            '子孙': ['财源益旺，吉', '财源渐退'],
            '兄弟': ['劫财之势益盛，凶', '劫财渐退，吉'],
            '官鬼': ['阻隔耗财益甚，凶', '阻隔渐消，吉'],
            '父母': ['仇神益旺、克财源，凶', '仇神渐退，吉']
          };
          tags.push(jt + '，' + jt_txt[y['liuqin']][jin ? 0 : 1]);
        }
        if (!hui && y['liuqin'] !== bq) {
          tags.push(HUA_QIN_CAI[`${y['liuqin']}|${bq}`] || ('化' + bq));
        }
        if (!tags.length) tags.push(jt === '化比和' ? '化比和，平顺' : ('化' + bq));
        L.push(seg + '：' + tags.join('；') + '。');
      }
    } else {
      L.push('　· 卦无动爻（或动而不化），六爻安静，当以本卦财福旺衰、世应生合静断。');
    }

    L.push('（7）卦象格局');
    if (cai_ju.length) {
      const j = cai_ju[0];
      const sheng_shi = ['生', '同'].indexOf(get_wuxing_relation(j['wuxing'], shi['wuxing'])) >= 0;
      L.push('　· 卦会三合财局（' + j['zhi'].join('') + `成${j['wuxing']}局，${j['kind']}`) +
        (sheng_shi ? '，动来生世，财利绵绵，可许厚利。' : '，然不生世，利未归己，待生合日月。'));
    }
    if (fu_ju.length) {
      const j = fu_ju[0];
      L.push('　· 卦会三合福/子孙局（' + j['zhi'].join('') + `成${j['wuxing']}局），财源大成，生合世身者利源万倍。`);
    }
    const liuhe_gua = ['天地否', '地天泰', '水泽节', '山水蒙', '风雷益', '雷地豫', '地山谦', '泽水困'];
    const liuchong_gua = ['乾为天', '兑为泽', '离为火', '震为雷', '巽为风', '坎为水', '艮为山', '坤为地', '天雷无妄', '雷大壮'];
    if (liuhe_gua.indexOf(paipan['name']) >= 0) L.push('　· 本卦为六合卦，主谋为和顺、交易易成、财可久守。');
    if (liuchong_gua.indexOf(paipan['name']) >= 0) L.push('　· 本卦为六冲卦，主买卖反复、不久而散，求财有始无终；唯散事宜之。');
    if (paipan['bian_gua'] && liuhe_gua.indexOf(paipan['bian_gua']['name']) >= 0) L.push('　· 动而化六合，主先难后易、散而复聚，求财终成。');
    if (paipan['bian_gua'] && liuchong_gua.indexOf(paipan['bian_gua']['name']) >= 0) L.push('　· 动而化六冲，主先成后败、得而复失，求财终散。');

    L.push('【三、综合断语与应期】');
    const zong = [];
    let shi_branch_handled = false;
    let zhu_cai = null;
    if (cais.length) {
      zhu_cai = cais[0];
      for (const c of cais) {
        if ((c['is_shi'] ? 1 : 0) > (zhu_cai['is_shi'] ? 1 : 0) ||
            ((c['is_shi'] ? 1 : 0) === (zhu_cai['is_shi'] ? 1 : 0) && (c['is_dong'] ? 1 : 0) > (zhu_cai['is_dong'] ? 1 : 0)) ||
            ((c['is_shi'] ? 1 : 0) === (zhu_cai['is_shi'] ? 1 : 0) && (c['is_dong'] ? 1 : 0) === (zhu_cai['is_dong'] ? 1 : 0) &&
              st_of(c)['score'] > st_of(zhu_cai)['score'])) zhu_cai = c;
      }
    }
    const zhu_lv = zhu_cai ? st_of(zhu_cai)['level'] : '';
    const cai_lv_word = zhu_lv === '旺相' ? '旺相' : (zhu_lv === '有气' ? '有气' : '衰弱');
    if (!cais.length) {
      if (fushen && (yue_rel === '同' || yue_rel === '生' || ri_rel === '同' || ri_rel === '生')) {
        zong.push('卦中无现财，然伏财得日月生扶，待伏神出现、冲开飞神之日，财尚可求，属「先无后有」。');
      } else {
        zong.push('卦中无财，伏财又不得时令，财福两空，此财强求无益，宜守不宜进。');
      }
    } else {
      const xiong_dong_wang_ke = xiong_sts.some(([y, s]) => y['is_dong'] &&
        ['旺相', '有气'].indexOf(s['level']) >= 0 && !xiong_bei_zhi(y) && !zis.some(z => z['is_dong']));
      const cai_hua_xiong_flag = bian_info.some(([y, b, bq]) => y['liuqin'] === '妻财' && (bq === '官鬼' || bq === '兄弟'));
      const cai_huike = bian_info.some(([y, b, bq, h]) => y['liuqin'] === '妻财' && h === '回头克');
      const zi_bei_ke = zis.some(y => y['is_dong'] && (st_of(y)['dong_ke'].length || fus.some(f => f['is_dong'])));

      if (cai_wang && ['持世', '生世', '克世'].indexOf(xiangbei) >= 0 && !xiong_dong_wang_ke &&
          !cai_hua_xiong_flag && !cai_huike && !shi['is_kong']) {
        if ((zi_dong_wang && !zi_hua_xiong && !zi_huike) || cai_ju.length || fu_ju.length) {
          zong.push(`财爻${cai_lv_word}、财来就我，又得福神（财源）发动/财局生世，财福双美——此乃求财上上之卦，公私称意，利源丰厚而久远。`);
        } else {
          zong.push(`财爻${cai_lv_word}而来生合持世，财来就我，求之易得；唯财源（子孙）未得纯旺（或静、或受伤化泄），利虽有而未必丰厚长久，待子孙生旺日更进。`);
        }
      } else if (cai_wang && ['世生财', '世克财', '无关'].indexOf(xiangbei) >= 0) {
        zong.push(`财爻${cai_wang ? '旺' : ''}，然与世无情，须主动经营、劳心劳力，待世爻或财爻逢冲合之日方得。`);
      } else if (xiong_dong_wang_ke) {
        zong.push('财爻纵有气，奈何兄弟旺动无制，劫财分夺、成本耗散；须待官鬼制兄之日，或兄弟受克之期方可得，目前断以破财、竞争。');
      } else if (cai_hua_xiong_flag || cai_huike) {
        zong.push('财爻发动而化官鬼、化兄弟或回头克，是得而复失、因财生忧、劫耗之象；世爻有伤则恐因财致祸，此财不取为安。');
      } else if (cai_kong_po) {
        zong.push('财爻现而逢旬空、月破，目前虚而不实；旺者待出旬、填实逢合之日可得，衰者则为真空真破，难望。');
      } else if (shi['is_kong'] || shi['is_po']) {
        shi_branch_handled = true;
        const pk = (shi['is_kong'] && shi['is_po']) ? '旬空又月破' : (shi['is_kong'] ? '旬空' : '月破');
        zong.push(`世爻为求财之人，今${pk}，己身无力、心志不固（月破主事多破败），纵卦中有财亦难就手；须待世爻出空、填实逢合之月日方有准实，此时只宜守静，不宜妄动求财。`);
      } else if (zhu_lv === '休囚' || zhu_lv === '无气' || cai_sts.some(([y, s]) => s['dong_ke'].length)) {
        const yuan_ruo = !zis.length || zis.every(z => z['is_kong'] || ['休囚', '无气'].indexOf(st_of(z)['level']) >= 0);
        if (yuan_ruo) {
          zong.push('财爻休囚无气或受克伤，且财源子孙不现、衰弱，求财费力而难得，纵得亦薄；宜待财爻生旺、子孙得令、克神受制之月日再图。');
        } else {
          zong.push('财爻虽现而休囚受克，喜财源子孙尚可生扶，待财爻生旺、克神受制之月日得，目前迟滞。');
        }
      } else {
        zong.push('财爻有气而无伤，大体可求，唯须详上述世应、财源、动变，中和而断，难易介于迟速之间。');
      }

      if (zi_bei_ke && cais.length) zong.push('财源子孙被父母/动爻克伤，利源受损，纵得眼前小利，亦难长久，恐先得后失。');
      if ((zi_hua_xiong || zi_huike) && cais.length) zong.push('财源子孙发动而化官鬼、父母或回头克，福神受伤化祸，求财中途恐生忧惊波折，得利减色，慎防乐极生忧。');
    }
    if (fu_xiong_dong) zong.push('父兄皆动，如缘木求鱼，财源坏、劫夺兴，此财必不可得。');
    if (xuanwu_guan_ke_shi) zong.push('官鬼临玄武动来克世，经商贩卖须严防盗贼、诈骗、圈套。');
    if (ying && ying['is_kong']) zong.push('应爻空亡，交易对方、合伙之人不实，虚约难凭，谨防失信。');
    if (shi['is_kong'] && !shi_branch_handled) zong.push('世爻旬空，自己心志不坚、底气不足，事宜缓图，待世爻出空逢值。');
    if (shi['is_po'] && !shi_branch_handled) zong.push('世爻月破，事多破败，待出月填实、逢合之月日方有转机。');
    for (const z of zong) L.push('· ' + z);

    const yq = _cai_yingqi(paipan, cais, fushen, shi, cai_wx);
    if (yq.length) {
      L.push('【得财应期】');
      for (const q of yq) L.push('· ' + q);
    }

    L.push('（以上依《卜筮正宗·黄金策》商贾章、总断千金赋之法推演，为软件据卦理之分析；实际求财尚须结合事理、时令与经营本身综合判断。）');
    return L;
  }

  // ================= 暴露 API =================
  const api = {
    TIANGAN, DIZHI, DIZHI_WUXING, TIANGAN_WUXING, TIANGAN_YINYANG,
    WUXING_SHENG, WUXING_KE, BAGUA, BAGONG, SHI_POS, GONGWEI_NAME,
    LIUSHEN, LIUSHEN_QISHI, LIUQIN, LIUCHONG, LIUHE, SANHE,
    get_ganzhi_index, get_xunkong,
    get_month_zhi, get_year_pillar, get_month_gan, get_day_pillar, date_to_ganzhi,
    get_liuqin, get_wuxing_relation,
    find_gua, match_gua, build_gua_from_yaos,
    zhuang_gua, tongqian_yao, qigua_from_tongqian,
    YONGSHEN_MAP, fenxi_gua, miao_yao_zhuangtai,
    num_to_cn, hua_jin_tui,
    _MUKU, _JUEDI, _CHANGSHENG, _yao_by_pos, _bian_by_pos,
    yao_wangshuai, find_fushen, sanhe_ju,
    _qincai_shiji, HUA_QIN_CAI, _liuqin_wuxing, _yao_brief,
    fenxi_caiyun, _cai_yingqi
  };

  global.LY = global.LY || {};
  for (const k in api) global.LY[k] = api[k];
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
