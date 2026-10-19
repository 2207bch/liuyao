/* 六爻十类专断框架与引擎 —— 移植自 liuyao_zhuan.py（《卜筮正宗·黄金策》） */
(function (global) {
  "use strict";
  const LY = global.LY || (typeof require === "function" ? require("./liuyao_core.js") : {});
  const {
    TIANGAN, DIZHI, DIZHI_WUXING, WUXING_SHENG, WUXING_KE, BAGUA,
    LIUQIN, LIUHE, LIUCHONG, LIUSHEN,
    get_liuqin, get_wuxing_relation, yao_wangshuai, find_fushen, sanhe_ju,
    hua_jin_tui, num_to_cn, _yao_brief, _bian_by_pos, _MUKU, _JUEDI, _CHANGSHENG,
    _liuqin_wuxing
  } = LY;

  const LIUHE_GUA = ['天地否', '地天泰', '水泽节', '山水蒙', '风雷益', '雷地豫', '地山谦', '泽水困'];
  const LIUCHONG_GUA = ['乾为天', '兑为泽', '离为火', '震为雷', '巽为风', '坎为水', '艮为山', '坤为地',
    '天雷无妄', '雷天大壮'];
  const _YQ_TAIL = "（应期以地支日推，具体公历日期请查万年历最近的相应地支日；近事以日断，远事以月断。）";

  // ================= 卦头 =================
  function _head(paipan) {
    const L = [];
    const gong_wx = paipan['gong_wuxing'];
    let head = `【卦象】${paipan['name']}（${paipan['gong']}宫${paipan['gongwei']}，${gong_wx}）`;
    if (paipan['bian_gua']) head += ` 之 ${paipan['bian_gua']['name']}`;
    L.push(head);
    L.push(`【日月】月建${paipan['yue_zhi']}${DIZHI_WUXING[paipan['yue_zhi']]}　` +
      `日辰${paipan['ri_gan']}${paipan['ri_zhi']}${DIZHI_WUXING[paipan['ri_zhi']]}　` +
      `旬空${paipan['xunkong'][0]}${paipan['xunkong'][1]}`);
    L.push('【动爻】' + (paipan['dong_yao'].length
      ? paipan['dong_yao'].map(d => `${num_to_cn(d)}爻动`).join('、')
      : '六爻安静，无动爻'));
    return L;
  }

  // ================= 上下文 =================
  function _setup(paipan) {
    const yx = paipan['yaos'].slice().reverse();
    const yue = paipan['yue_zhi'], ri = paipan['ri_zhi'];
    const gong_wx = paipan['gong_wuxing'];
    const shi = yx.find(y => y['is_shi']);
    const ying = yx.find(y => y['is_ying']) || null;
    const st_of = y => yao_wangshuai(y, paipan);
    const byqin = {};
    for (const q of LIUQIN) byqin[q] = yx.filter(y => y['liuqin'] === q);
    return { paipan, yx, yue, ri, gong_wx, shi, ying, st_of, byqin };
  }

  // ================= 详断一爻 =================
  function _yong_yao_duan(y, C, extra) {
    extra = extra || '';
    const [brief, s] = _yao_brief(y, C['paipan']);
    const d = [];
    if (s['yue']) d.push(s['yue']);
    if (s['ri']) d.push(s['ri']);
    if (s['dong_sheng'].length) d.push('受动爻生：' + s['dong_sheng'].join('、'));
    if (s['dong_ke'].length) d.push('受动爻克：' + s['dong_ke'].join('、'));
    if (s['changsheng']) d.push(`逢长生于${s['changsheng']}`);
    if (s['mu']) d.push(`入墓于${s['mu']}，主阻滞，待冲墓`);
    if (s['jue']) d.push(`逢绝于${s['jue']}，须逢生旺`);
    if (y['is_dong'] && s['ri_he']) d.push('动而被日辰合住（绊住），待冲开之日');
    if (y['is_kong']) {
      d.push(s['score'] >= 2 ? '旺相空为假空，待出旬值日即应；衰弱空为真空，难应'
        : '衰弱又空，为真空，难应');
    }
    if (y['is_po']) d.push('月破，待出月填实、逢合之日');
    if (extra) d.push(extra);
    return '　· ' + brief + '：' + (d.length ? d.join('；') : '无明显刑冲克害，平和') + '。';
  }

  // ================= 伏神详断 =================
  function _fushen_duan(C, yong_qin) {
    const fs = find_fushen(C['paipan'], yong_qin);
    if (!fs) return [`　· 本宫亦寻伏「${yong_qin}」不得，用爻毫无其根，大不利。`];
    const fei = fs['feishen'];
    const yue = C['yue'], ri = C['ri'];
    const yue_rel = yue ? get_wuxing_relation(DIZHI_WUXING[yue], fs['wuxing']) : '无';
    const ri_rel = ri ? get_wuxing_relation(DIZHI_WUXING[ri], fs['wuxing']) : '无';
    const fei_rel = get_wuxing_relation(fei['wuxing'], fs['wuxing']);
    const fei_map = {
      '生': '飞神生伏，伏得生扶易出，吉',
      '克': '飞神克伏（伤身），伏被压难出',
      '被生': '伏生飞而泄气，难出现',
      '被克': '伏克飞为「出暴」，事机急暴、乍起乍落',
      '同': '飞伏比和，伏易出'
    };
    const tian = [];
    if (yue_rel === '同' || yue_rel === '生') tian.push('得月建生扶');
    if (ri_rel === '同' || ri_rel === '生') tian.push('得日辰生扶');
    if (LIUCHONG[C['yue']] === fs['zhi']) tian.push('伏神逢月破，待填实逢合');
    else if (yue_rel === '克') tian.push('伏神被月建所克');
    if (LIUCHONG[C['ri']] === fs['zhi']) tian.push('伏神逢日冲（日破）');
    else if (ri_rel === '克') tian.push('伏神被日辰所克');
    if (C['paipan']['xunkong'].indexOf(fs['zhi']) >= 0) tian.push('伏神又逢旬空');
    const L = [`　· 于本宫${C['paipan']['gong']}卦寻得伏神：${num_to_cn(fs['pos'])}爻${yong_qin}` +
      `${fs['zhi']}${fs['wuxing']}，伏于${num_to_cn(fei['pos'])}爻飞神「${fei['liuqin']}` +
      `${fei['zhi']}${fei['wuxing']}」之下。`];
    L.push('　· 伏神待日月动爻生扶拱合、或冲开飞神、伏神值日出现方应；' +
      (tian.length ? tian.join('、') : '目前不得日月生扶') + '；' +
      (fei_map[fei_rel] || '飞伏无克，待时可出') + '。');
    return L;
  }

  // ================= 格局 =================
  function _geju_duan(C, he_txt, chong_txt, hua_he_txt, hua_chong_txt) {
    const L = [];
    const p = C['paipan'];
    if (LIUHE_GUA.indexOf(p['name']) >= 0) L.push('　· 本卦为六合卦：' + he_txt);
    if (LIUCHONG_GUA.indexOf(p['name']) >= 0) L.push('　· 本卦为六冲卦：' + chong_txt);
    if (p['bian_gua'] && LIUHE_GUA.indexOf(p['bian_gua']['name']) >= 0)
      L.push('　· 动而化六合：' + (hua_he_txt || he_txt));
    if (p['bian_gua'] && LIUCHONG_GUA.indexOf(p['bian_gua']['name']) >= 0)
      L.push('　· 动而化六冲：' + (hua_chong_txt || chong_txt));
    return L;
  }

  // ================= 三合用神局 =================
  function _sanhe_duan(C, yong_qin, yong_wx) {
    const L = [];
    for (const j of sanhe_ju(C['paipan'])) {
      if (j['wuxing'] !== yong_wx) continue;
      const sheng_shi = ['生', '同'].indexOf(get_wuxing_relation(j['wuxing'], C['shi']['wuxing'])) >= 0;
      L.push('　· 卦会三合' + yong_qin + '局（' + j['zhi'].join('') +
        `成${j['wuxing']}局，${j['kind']}）` +
        (sheng_shi ? '，动来生合世身，大吉。' : '，然不生世，事未归己，待生合日月。'));
    }
    return L;
  }

  // ================= 动变详断 =================
  function _bian_duan(C, xi_ji, hua_qin_img) {
    const L = [];
    const p = C['paipan'];
    const gong_wx = C['gong_wx'];
    let any_ = false;
    for (const y of C['yx']) {
      if (!y['is_dong']) continue;
      const by = _bian_by_pos(p, y['pos']);
      if (!by) continue;
      any_ = true;
      const bq = get_liuqin(gong_wx, by['wuxing']);
      const rel = get_wuxing_relation(by['wuxing'], y['wuxing']);
      const seg = `　· ${num_to_cn(y['pos'])}爻${y['liuqin']}${y['zhi']}动，变${bq}${by['zhi']}`;
      const tags = [];
      const direction = xi_ji[y['liuqin']] || '喜';
      const jt = hua_jin_tui(y['zhi'], by['zhi']);
      if (rel === '生') {
        tags.push('回头生，' + (direction === '喜' ? '吉神得益，吉' : '凶神得势，凶'));
      } else if (rel === '克') {
        tags.push('回头克，' + (direction === '喜' ? '吉神受伤，凶' : '凶神被制，反吉'));
      } else if (rel === '同' && jt && jt !== '化比和') {
        if (jt === '化进神') tags.push('化进神，' + (direction === '喜' ? '势盛，吉' : '凶势益盛，凶'));
        else tags.push('化退神，' + (direction === '喜' ? '势退，凶' : '凶势渐退，吉'));
      } else {
        let img = null;
        if (hua_qin_img) {
          for (const k in hua_qin_img) {
            const [a, b] = k.split('|');
            if (a === y['liuqin'] && b === bq) { img = hua_qin_img[k]; break; }
          }
        }
        if (img) tags.push(img);
        else if (rel === '被生') {
          if (!_youli(y, C)) tags.push('动爻空破，暂不生「' + bq + '」，待填实');
          else tags.push('动爻转生「' + bq + '」，本爻力泄，再看「' + bq + '」与用神生克');
        } else if (rel === '被克') {
          if (!_youli(y, C)) tags.push('动爻空破，暂不克「' + bq + '」，待填实');
          else tags.push('动爻去制「' + bq + '」，化出之神受克；若「' + bq + '」为用神、原神则不利');
        }
      }
      if (!tags.length) tags.push(jt === '化比和' ? '化比和，平顺' : ('化' + bq));
      L.push(seg + '：' + tags.join('；') + '。');
    }
    if (!any_) L.push('　· 卦无动爻（或动而不化），六爻安静，以本卦旺衰、世应生合静断。');
    return L;
  }

  // ================= 通用应期 =================
  function _yong_yingqi(C, yong_qin, yongs, fushen, verb) {
    verb = verb || '应事';
    const q = [];
    if (!yongs.length && fushen) {
      const chong_fei = LIUCHONG[fushen['feishen']['zhi']] || '';
      q.push(`伏「${yong_qin}」${fushen['zhi']}：待值日（${fushen['zhi']}日）或冲开飞神（${chong_fei}日）、日月引拔之时${verb}。`);
      q.push(_YQ_TAIL);
      return q;
    }
    if (!yongs.length) return q;
    let y = yongs[0];
    for (const c of yongs) {
      const kc = [c['is_shi'] ? 1 : 0, c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
      const ky = [y['is_shi'] ? 1 : 0, y['is_dong'] ? 1 : 0, C['st_of'](y)['score']];
      if (kc[0] > ky[0] || (kc[0] === ky[0] && kc[1] > ky[1]) ||
        (kc[0] === ky[0] && kc[1] === ky[1] && kc[2] > ky[2])) y = c;
    }
    const s = C['st_of'](y);
    const chong = LIUCHONG[y['zhi']] || '';
    const he = LIUHE[y['zhi']] || '';
    if (y['is_kong']) {
      q.push(`「${yong_qin}」${y['zhi']}旬空：旺者出旬逢值（${y['zhi']}日）或逢冲（${chong}日）${verb}；衰者难。`);
    } else if (y['is_po']) {
      q.push(`「${yong_qin}」${y['zhi']}月破：待填实（${y['zhi']}日）或逢合（${he}日）${verb}。`);
    } else if (s['mu']) {
      q.push(`入墓于${_MUKU[y['wuxing']]}：待冲墓（${LIUCHONG[_MUKU[y['wuxing']]] || ''}日）或冲（${chong}日）${verb}。`);
    } else if (y['is_dong'] && s['ri_he']) {
      q.push(`动被合住：待冲开（${chong}日）${verb}。`);
    } else if (y['is_dong']) {
      q.push(`「${yong_qin}」发动：逢值（${y['zhi']}日）或逢合（${he}日）${verb}。`);
    } else {
      if (s['ri_he']) q.push(`静逢日合为「合起」：逢冲（${chong}日）、逢值（${y['zhi']}日）${verb}。`);
      else if (s['level'] === '旺相' || s['level'] === '有气')
        q.push(`「${yong_qin}」安静有气：逢冲（${chong}日）暗动、逢值（${y['zhi']}日）${verb}。`);
      else q.push(`「${yong_qin}」安静休囚：待生旺、逢冲（${chong}日）、逢值（${y['zhi']}日）${verb}。`);
    }
    q.push(_YQ_TAIL);
    return q;
  }

  // ================= 有力与否 =================
  function _youli(y, C) {
    if (y === null || y === undefined) return false;
    const s = C['st_of'](y);
    if (y['is_po']) return false;
    if (y['is_kong'] && s['score'] < 2) return false;
    if (s['score'] < 0 && (s['level'] === '无气' || s['level'] === '休囚')) return false;
    return true;
  }

  // ================= 功名（仕宦） =================
  const _GONG_HUA = {
    '官鬼|父母': '官化印绶，文书相生，官名益固，吉',
    '父母|官鬼': '印绶化官，官印相生，升迁之象，吉',
    '官鬼|妻财': '官化财禄，财来生官，吉',
    '妻财|官鬼': '财化官，原神生用，吉',
    '官鬼|子孙': '官化子孙，用神被克，剥官削职，凶',
    '官鬼|兄弟': '官化兄弟，同僚争竞、减俸，凶',
    '父母|子孙': '印绶化子孙，克官之神得生，凶',
    '兄弟|官鬼': '兄弟化官，官来制兄，减俸之患得除，吉',
    '子孙|父母': '子孙化父母，忌神被印绶所制，先阻后解，吉凶相半',
    '子孙|官鬼': '子孙化官，忌神化用，然子孙已动先克官，先凶后解'
  };

  function fenxi_gongming(paipan) {
    const C = _setup(paipan);
    const L = _head(paipan);
    const guans = C['byqin']['官鬼'], cais = C['byqin']['妻财'];
    const fus = C['byqin']['父母'], zis = C['byqin']['子孙'], xiongs = C['byqin']['兄弟'];
    const shi = C['shi'], gong_wx = C['gong_wx'];
    const yong_wx = _liuqin_wuxing(gong_wx, '官鬼');

    const fushen = !guans.length ? find_fushen(paipan, '官鬼') : null;

    const guan_sts = guans.map(y => [y, C['st_of'](y)]);
    const guan_wang = guan_sts.some(([y, s]) => ['旺相', '有气'].indexOf(s['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const guan_kong_po = guans.some(y => y['is_kong'] || y['is_po']);
    const zi_dong = zis.some(y => y['is_dong']);
    const fu_kong = (!fus.length) || fus.some(y => y['is_kong'] || y['is_po']);
    const xiong_dong = xiongs.some(y => y['is_dong']);
    const cai_wang = cais.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const cai_kong = (!cais.length) || cais.every(y => y['is_kong'] || y['is_po']);

    const grel = y => y['is_shi'] ? '持世' : get_wuxing_relation(y['wuxing'], shi['wuxing']);
    const guan_chishi = guans.some(y => y['is_shi']);
    const guan_shengshi = guans.some(y => grel(y) === '生');
    const guan_keshi = guans.some(y => grel(y) === '克');
    const yue_ri_sheng = guans.some(y =>
      get_wuxing_relation(DIZHI_WUXING[C['yue']], y['wuxing']) === '生' ||
      get_wuxing_relation(DIZHI_WUXING[C['ri']], y['wuxing']) === '生');
    const guan_ju = sanhe_ju(paipan).filter(j => j['wuxing'] === yong_wx);

    L.push('【一、《黄金策·仕宦》论功名（经典）】');
    L.push('· 总纲：「为国求贤，治民为本；致身辅相，禄养为先。旺相妻财，必得千钟之粟；' +
      '兴隆官鬼，定居一品之尊」——未仕求名不要财爻，已仕贵人要见财爻，盖有爵必有禄，' +
      '未有无俸而居官者。官星旺相，俸禄必多；官鬼旺相，官高爵大；休囚死绝，官小职卑。');
    L.push('· 六亲取用：官鬼为用神（功名职位）；妻财为俸禄、为原神（生官）；父母为印绶' +
      '（官之凭、文书，制伤官之子）；子孙为忌神（克官、剥官削职）；兄弟发动主减俸除粮。');
    const _GM_JING = [
      ['官爻隐伏，莫思爵位升迁', '官鬼即官职，卦中无官鬼或官星空破，求官无分；官临持身世、或动来生合世，又不受月日冲克，凡有谋为方能升迁。'],
      ['子若交重，当虑剥官削职', '子孙克官鬼，子孙若在卦中发动，所谋必不遂意；已任者恐有褫职剥官之祸。'],
      ['父母空亡，休望差除宣敕', '父母为印绶、文书、诰牒、宣敕、奏书、表章，卦中不可无、宜旺不宜衰、扶世最吉；空亡则无任命文凭，休望差除。'],
      ['兄如发动，须防减俸除粮', '兄弟发动，不免费财招谤、减俸除粮；若与子孙同发、或化出子孙，必有除粮减俸之事，持身临世皆不吉。'],
      ['身边伏鬼若非空，头上乌纱终不脱', '官鬼临身持世、或本宫鬼伏于世下而不空，虽见责罚，官职犹在；若不临身世、不伏世下、或伏而空亡，必遭黜革。'],
      ['月建生身，当际风云之会；岁君合世，必承雨露之恩', '月建为执政之官、太岁为君象，官星得月建生合、岁君加父母扶出官爻世爻者，必有举荐升擢、朝廷天恩。'],
      ['鬼煞伤身，因见灾殃之不免', '官鬼动来生合世者为用神，主进取升迁；动来刑冲克伤世者则为鬼煞，必有凶祸，太岁加刑则贬谪难逃。'],
      ['太岁加刑不顺，贬谪难逃', '太岁刑伤世爻必遭贬谪，更加刑害腾蛇白虎，主锁拘擒拿之辱。'],
      ['卦静世空，退休之兆；身空煞动，避祸之征', '已任而世爻空亡、六爻安静、日月岁君未伤，是休官之象；若官鬼同日月岁君克世而世又空，急宜避祸可免。'],
      ['财空鬼动，声名震而囊箧空虚', '官动生合世、日月不冲克，为官有声名；更得财生扶则内实贪赂、外不丧名；若世爻空伏、财爻死绝，虚名虽有而贿赂无也。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _GM_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    if (guan_wang && (guan_chishi || guan_shengshi))
      L.push('· 官鬼为仕宦之主，得官星旺相、持临身世或动来生合世，凡有谋为必升，官高爵大。');
    if (guan_chishi && !guan_kong_po)
      L.push('· 「身边伏鬼若非空，头上乌纱终不脱」——官临身世或鬼伏世下，虽见责罚，官职犹在。');
    if ((!guans.length || guan_kong_po) && !guan_chishi)
      L.push('· 「官爻隐伏，莫思爵位升迁」——卦无官鬼或官星空破，求官无分，头上乌纱难保。');
    if (zi_dong)
      L.push('· 「子若交重，当虑剥官削职」——子孙为克官之煞，发动所谋不遂，已任者恐褫职。');
    if (fu_kong)
      L.push('· 「父母空亡，休望差除宣敕」——父母为印绶文书、诰牒宣敕，空亡则无任命文凭。');
    if (cai_wang)
      L.push('· 「妻财为俸禄，财旺得禄千钟」——已仕占官，财爻旺相则俸禄丰厚。');
    if (cai_kong)
      L.push('· 「财爻休囚空伏，未得俸禄」——财空则俸禄薄、官无生源。');
    if (xiong_dong)
      L.push('· 「兄如发动，须防减俸除粮」——兄弟动，费财招诽、减俸。');
    if (yue_ri_sheng || guan_ju.length)
      L.push('· 「月建生身，当际风云之会；岁君合世，必承雨露之恩」——官星得月日生合、或会成官局，必有举荐升擢。');
    if (guan_keshi)
      L.push('· 「鬼煞伤身，因见灾殃之不免」——官鬼生合世为用神（升迁）；动来克伤世为鬼煞，刑冲克世必有凶祸，太岁加刑则贬谪难逃。');

    L.push('【二、本卦功名逐条详断】');
    L.push('（1）用神·官鬼爻（功名职位）');
    if (guans.length) {
      for (const y of guans) L.push(_yong_yao_duan(y, C));
    } else {
      L.push('　· 卦中不见官鬼爻，用神不上卦。');
      for (const ln of _fushen_duan(C, '官鬼')) L.push(ln);
    }

    L.push('（2）世爻（求官之人）与官鬼向背');
    L.push(_yong_yao_duan(shi, C));
    if (guans.length) {
      if (guan_chishi) L.push('　· 官鬼持世，官在己身，求官最切、官来就我。');
      else if (guan_shengshi) {
        if (guan_wang) L.push('　· 官鬼旺相生合世爻，官来就我，升迁大吉。');
        else L.push('　· 官鬼虽生合世，然官爻休囚无气，生世无力，主官小、欲升而力不足，待官逢生旺日月。');
      } else if (guan_keshi) {
        L.push('　· 官鬼克世，是鬼煞伤身，非官来就我，主灾咎。');
      } else {
        L.push('　· 官与世无生合，乃我去求官，须凭荐举、劳心劳力，世旺方得。');
      }
    }
    if (C['ying']) L.push(_yong_yao_duan(C['ying'], C, '应爻为所任之地、同僚或所托之人'));

    L.push('（3）印绶·父母爻（官之凭、宣敕，制伤官之子）');
    if (fus.length) {
      for (const y of fus) L.push(_yong_yao_duan(y, C));
    } else {
      L.push('　· 父母不现，印绶文凭隐伏，任命文书无力；须查伏神、待值日。');
    }

    L.push('（4）俸禄·妻财爻（原神·生官·俸禄）');
    if (cais.length) {
      for (const y of cais) L.push(_yong_yao_duan(y, C));
    } else {
      L.push('　· 妻财不现，俸禄无气、官无生源，仕宦之禄薄。');
    }

    L.push('（5）忌神·子孙（剥官）与兄弟（减俸）');
    if (zis.length) {
      for (const y of zis) {
        let ex;
        if (y['is_dong']) ex = '子孙发动克官，剥官削职，大忌';
        else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0)
          ex = '子孙静而旺，暗有夺官之忧，待逢冲值日发动则凶';
        else ex = '子孙静而休囚，不主动克官，暂无害';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 子孙不现，克官之神不兴，官无剥夺，吉。');
    }
    if (xiongs.length) {
      for (const y of xiongs) {
        let ex;
        if (y['is_dong']) ex = '兄弟发动，减俸除粮、同僚争';
        else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0)
          ex = '兄弟静旺，同僚同辈多、分禄，待发动方减俸';
        else ex = '兄弟静衰，同僚不争，无害';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 兄弟不现，无减俸争竞之患。');
    }

    L.push('（6）动爻变化吉凶');
    for (const ln of _bian_duan(C, { '官鬼': '喜', '妻财': '喜', '父母': '喜', '子孙': '忌', '兄弟': '忌' }, _GONG_HUA))
      L.push(ln);

    L.push('（7）卦象格局');
    for (const ln of _sanhe_duan(C, '官鬼', yong_wx)) L.push(ln);
    for (const ln of _geju_duan(C, '六合主仕途和顺、上下同心，任事久安。',
      '六冲主任所不久、调动反复，有始无终。',
      '动化六合，先调动后安定，终得久任。',
      '动化六冲，先安后散，终主离任。'))
      L.push(ln);

    L.push('【三、综合断语与升迁应期】');
    const zong = [];
    if (!guans.length) {
      if (fushen && [C['yue'], C['ri']].some(z =>
        ['同', '生'].indexOf(get_wuxing_relation(DIZHI_WUXING[z], fushen['wuxing'])) >= 0)) {
        zong.push('卦中无现官，然伏官得日月生扶，待伏神出现、冲开飞神之日，官尚可求，属先无后有。');
      } else {
        zong.push('卦无官鬼，伏官又不得时令，功名两空，求官无分，宜守。');
      }
    } else {
      if (guan_wang && (guan_chishi || guan_shengshi) && !zi_dong && !fu_kong &&
          !shi['is_kong'] && !shi['is_po']) {
        if (yue_ri_sheng || guan_ju.length || cai_wang) {
          zong.push('官星旺相、官来就我（持世/生合世），印绶不空、子孙不兴，又得日月生扶、财禄相生——此乃仕宦上上之卦，必得升迁，官高爵大。');
        } else {
          zong.push('官星旺相、官来就我，求官易得、升迁有望；唯印绶、荐扶或财禄未得纯旺，待日月生合、官爻逢值之日更进。');
        }
      } else if (guan_chishi && !guan_kong_po) {
        zong.push('官爻持世（或伏官于世下）不空，「头上乌纱终不脱」，虽有小责、同僚摩擦，官职犹在，主小吉。');
      } else if (zi_dong) {
        zong.push('子孙发动克官，主剥官削职、降官离任；须待官爻受克或子孙值日之期应，目前断以不吉。');
      } else if (guan_kong_po) {
        zong.push('官鬼空破（或兼印绶空亡），求官无分、职位难保；旺者待填实出旬，衰者无望。');
      } else if (guan_keshi) {
        zong.push('官鬼动来克世（非生合），为鬼煞伤身，主任上灾咎、贬谪，须防灾祸。');
      } else if (shi['is_kong'] || shi['is_po']) {
        const pk = shi['is_kong'] ? '旬空' : '月破';
        zong.push(`世爻${pk}，己身无力、居官不久，待出空填实逢合方有转机。`);
      } else {
        zong.push('官爻有气而未得纯旺，或休囚平和，主官小职卑、平稳待时，待官逢生旺、生合世身之日升迁。');
      }
    }
    for (const z of zong) L.push('· ' + z);

    const yq = _yong_yingqi(C, '官鬼', guans, fushen, '升迁得官');
    if (yq.length) {
      L.push('【升迁应期】');
      for (const q of yq) L.push('· ' + q);
    }

    L.push('（以上依《卜筮正宗·黄金策》仕宦章、总断千金赋之法推演，为软件据卦理之分析；实际功名尚须结合才德、人事、时势综合判断。）');
    return L;
  }

  // ================= 考试（求名） =================
  const _KAO_HUA = {
    '父母|官鬼': '文书化官，文章得名，吉',
    '官鬼|父母': '官化文书，官名与文章相生，吉',
    '父母|妻财': '文书化财，财回头克父，文章破绽，凶',
    '官鬼|子孙': '官化子孙，名次被克，凶',
    '父母|子孙': '文书化子孙，子孙生财、财克父，文事有阻，凶',
    '官鬼|兄弟': '官化兄弟，同经争名次，凶',
    '妻财|父母': '财化父母，财不克父，文书得复，吉凶相半',
    '子孙|官鬼': '子孙化官，忌神化用，然子已动先克官，先阻后解',
    '子孙|父母': '子孙化父母，父克子，忌神受制，先阻后解',
    '兄弟|官鬼': '兄弟化官，夺标者反助官，先争后让',
    '兄弟|父母': '兄弟化父母，文书得生，然兄为同经，得失相半'
  };

  function fenxi_kaoshi(paipan) {
    const C = _setup(paipan);
    const L = _head(paipan);
    const fus = C['byqin']['父母'], guans = C['byqin']['官鬼'];
    const cais = C['byqin']['妻财'], zis = C['byqin']['子孙'], xiongs = C['byqin']['兄弟'];
    const shi = C['shi'], gong_wx = C['gong_wx'];
    const fu_wx = _liuqin_wuxing(gong_wx, '父母'), guan_wx = _liuqin_wuxing(gong_wx, '官鬼');

    const fu_shen = !fus.length ? find_fushen(paipan, '父母') : null;
    const guan_shen = !guans.length ? find_fushen(paipan, '官鬼') : null;

    const fu_wang = fus.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const guan_wang = guans.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const fu_kp = fus.some(y => y['is_kong'] || y['is_po']);
    const guan_kp = guans.some(y => y['is_kong'] || y['is_po']);
    const cai_dong = cais.some(y => y['is_dong']);
    const zi_dong = zis.some(y => y['is_dong']);
    const xiong_dong = xiongs.some(y => y['is_dong']);
    const fu_chishi = fus.some(y => y['is_shi']);
    const guan_chishi = guans.some(y => y['is_shi']);
    const fu_shengshi = fus.some(y => get_wuxing_relation(y['wuxing'], shi['wuxing']) === '生');
    const guan_shengshi = guans.some(y => get_wuxing_relation(y['wuxing'], shi['wuxing']) === '生');
    const fu_guan_chong = fus.some(fy => guans.some(gy => LIUCHONG[fy['zhi']] === gy['zhi']));
    const yue_ri_fu = fus.concat(guans).some(y =>
      ['同', '生'].indexOf(get_wuxing_relation(DIZHI_WUXING[C['yue']], y['wuxing'])) >= 0 ||
      ['同', '生'].indexOf(get_wuxing_relation(DIZHI_WUXING[C['ri']], y['wuxing'])) >= 0);
    const long_hu = C['yx'].some(y => y['is_dong'] && (y['liushen'] === '青龙' || y['liushen'] === '白虎'));

    L.push('【一、《黄金策·求名》论考试（经典）】');
    L.push('· 总纲：「读书五车，固欲置身于廊庙；胸藏万卷，肯甘遁迹于丘园？要相国家，当详易卦。' +
      '父爻旺相，其文掷地金声；鬼位兴隆，家报泥金捷喜」——凡占功名，以父爻为文章、' +
      '鬼为官职，二者一卦之主，伤一则不成。父爻旺相，文章必佳；官鬼得地，功名有望。');
    L.push('· 六亲取用：父母为文章试卷（主用神），官鬼为功名名次（主用神），二者皆宜旺相有气、' +
      '不空破、生合世身；妻财克父母、子孙克官鬼，皆为忌神；兄弟为同经之士，动则夺标。');
    const _KS_JING = [
      ['财若交重，休望青钱之中选；福如发动，难期金榜之题名', '唯卜功名，以财、福反为恶煞，盖财能克父、子能克鬼也；妻财发动则文章破绽，子孙发动则名次被克。唯官爻持世得财动来生，而财无忌。'],
      ['兄弟同经，乃夺标之恶客', '兄弟即与我同经赴考之人，若发动、或月建日辰俱带兄弟，则同经者多，必能夺我之标，纵大象可成，名亦落后。'],
      ['月克文书，程式背而不中', '父母旺而得动爻日辰生合，其文字字锦绣；妻财伤克必多破绽，月建冲克，其文必不合主司程式而不中。'],
      ['两用相冲，题目生疏而不熟', '以官爻为用爻，喜合而不喜冲；官父相冲，主出题生涩不熟。'],
      ['日辰辅德，实劝驾之良朋', '父母官鬼无气，若得日辰扶起、克制恶煞，仍旧有望；或世爻衰静空亡，得日辰生扶冲实，主有亲友资助盘费、辅其赴考。'],
      ['父旺官衰，可惜刘蕡之下第；父衰官旺，堪嗟张爽之登科', '父母官鬼皆宜有力无损，功名可成；父旺官空则文章虽好而不第，父衰官旺则文字平常反可成名。'],
      ['世伤官鬼，仕途窒而不通', '世乃求名之人，世持官鬼或得官鬼生合，功名有望；若临子孙克制官鬼，是仕途未通，徒去求谋无济。'],
      ['龙虎二爻俱动，一举成名', '青龙白虎俱在卦中动来生合世爻，必中魁选；若持官父或持身世尤妙。'],
      ['父官三合相逢，连科及第', '卦有三合会成官局者，主连科及第，会成父母局亦吉。'],
      ['卦值六冲，此去难题雁塔；爻达六合，这回必占鳌头', '占功名得六冲卦必难成，得六合卦必易得。'],
      ['六爻竞发，功名恍惚以难成', '六爻皆喜安静，只要官鬼有气不空、月日不来伤克则吉；乱动则多变化，变出死墓绝空刑克，皆为破败，大概不吉。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _KS_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    if (cai_dong) L.push('· 「财若交重，休望青钱之中选」——妻财发动克父母，文书被伤，文章破绽。');
    if (zi_dong) L.push('· 「福如发动，难期金榜之题名」——子孙发动克官鬼，名次被克。');
    if (xiong_dong) L.push('· 「兄弟同经，乃夺标之恶客」——兄弟发动，同经者多，纵可成名亦落后。');
    if (fu_wang && guan_wang) L.push('· 父爻旺相文章必佳，官鬼得地名次有望，官父两全。');
    if (fu_wang && !guan_wang) L.push('· 「父旺官衰，可惜刘蕡之下第」——文字虽佳，名次不足，恐不中式。');
    if (!fu_wang && guan_wang) L.push('· 「父衰官旺，堪嗟张爽之登科」——文字虽平，得官旺扶，亦可成名。');
    if (fu_kp || !fus.length) L.push('· 父母空破或不上卦，文章试卷不力，「月克文书，程式背而不中」。');
    if (guan_kp || !guans.length) L.push('· 官鬼空破或不上卦，名次无分。');
    if (fu_guan_chong) L.push('· 「两用相冲，题目生疏而不熟」——官父相冲，题目不就。');
    if (yue_ri_fu) L.push('· 「日辰辅德，实劝驾之良朋」——官父无气，得日月生扶拱合，仍有指望。');
    if (long_hu) L.push('· 「龙虎二爻俱动，一举成名」——青龙、白虎动生合世，必中魁选。');

    L.push('【二、本卦考试逐条详断】');
    L.push('（1）主用神·父母爻（文章试卷）');
    if (fus.length) {
      for (const y of fus) L.push(_yong_yao_duan(y, C));
    } else {
      L.push('　· 卦中不见父母爻，文章之主不上卦。');
      for (const ln of _fushen_duan(C, '父母')) L.push(ln);
    }
    L.push('（2）主用神·官鬼爻（功名名次）');
    if (guans.length) {
      for (const y of guans) L.push(_yong_yao_duan(y, C));
    } else {
      L.push('　· 卦中不见官鬼爻，名次之主不上卦。');
      for (const ln of _fushen_duan(C, '官鬼')) L.push(ln);
    }
    L.push('（3）世爻（考生自己）与官父向背');
    L.push(_yong_yao_duan(shi, C));
    if (fu_chishi || guan_chishi) L.push('　· 父母或官鬼持世，文章、功名在己身，最切。');
    else if (fu_shengshi || guan_shengshi) L.push('　· 官父生合世身，功名来就，吉。');
    else L.push('　· 官父不生合身世，须凭文章自奋、他人荐举，世旺方得。');

    L.push('（4）忌神·妻财（克父母、坏文书）');
    if (cais.length) {
      for (const y of cais) {
        let ex;
        if (y['is_dong']) ex = '妻财发动克父母，文书大忌';
        else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0) ex = '妻财静旺，暗伤文书，待发动则凶';
        else ex = '妻财静衰，不克父，暂无害';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 妻财不现，文书不受克，文章无破绽，吉。');
    }
    L.push('（5）忌神·子孙（克官）与兄弟（同经夺标）');
    if (zis.length) {
      for (const y of zis) {
        let ex;
        if (y['is_dong']) ex = '子孙发动克官，名次大忌';
        else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0) ex = '子孙静旺，暗有夺名之忧';
        else ex = '子孙静衰，不克官，暂无害';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 子孙不现，官鬼不受克，名次稳固，吉。');
    }
    if (xiongs.length) {
      for (const y of xiongs) {
        let ex;
        if (y['is_dong']) ex = '兄弟发动，同经夺标，然兄克财亦能护父';
        else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0) ex = '兄弟静旺，同经之士多，分名次';
        else ex = '兄弟静衰，无夺标之争';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 兄弟不现，无同经夺标之争。');
    }
    L.push('（6）动爻变化吉凶');
    for (const ln of _bian_duan(C, { '父母': '喜', '官鬼': '喜', '妻财': '忌', '子孙': '忌', '兄弟': '忌' }, _KAO_HUA))
      L.push(ln);
    L.push('（7）卦象格局（三合、龙虎、六合六冲）');
    for (const ln of _sanhe_duan(C, '父母', fu_wx)) L.push(ln);
    for (const ln of _sanhe_duan(C, '官鬼', guan_wx)) L.push(ln);
    for (const ln of _geju_duan(C, '六合主功名易得，「这回必占鳌头」。',
      '六冲主功名难成，「此去难题雁塔」。',
      '动化六合，先难后易，终得中式。',
      '动化六冲，先易后散，终主不中。'))
      L.push(ln);
    if (long_hu) L.push('　· 青龙、白虎爻发动，「一举成名」，主科名之喜。');

    L.push('【三、综合断语与放榜应期】');
    const zong = [];
    if (fu_wang && guan_wang && !cai_dong && !zi_dong && !shi['is_kong'] && !shi['is_po']) {
      if (fu_chishi || guan_chishi || fu_shengshi || guan_shengshi) {
        zong.push('官父俱旺、文章与名次两全，又生合世身，财子不兴——此乃考试上上之卦，金榜题名，名次必高。');
      } else {
        zong.push('官父俱旺，文章佳、名次稳，然官父不生合世身，须得荐举或临场加力，放榜可中。');
      }
    } else if (cai_dong) {
      zong.push('妻财发动克父母，文书破绽，主不中；待财受克、父得生旺之期再考。');
    } else if (zi_dong) {
      zong.push('子孙发动克官鬼，名次被克，主不中。');
    } else if (xiong_dong) {
      zong.push('兄弟发动，同经夺标，主虽可成亦落后、名次不高。');
    } else if (fu_wang && !guan_wang) {
      if (!guans.length) zong.push('文章佳而卦无名次（官不现），刘蕡下第之象，主不中式。');
      else zong.push('父旺官衰，文字好而名次低，恐落榜。');
    } else if (!fu_wang && guan_wang) {
      zong.push('父衰官旺，文字平而得官扶，可侥幸成名，名次不高。');
    } else if (fu_kp || guan_kp || !fus.length || !guans.length) {
      zong.push('官父空破或不上卦，文章、名次两虚，主不中。');
    } else if (shi['is_kong'] || shi['is_po']) {
      zong.push('世爻空破，考生己身无力，或病阻试期，待出空填实。');
    } else {
      zong.push('官父有气而未旺，或休囚平和，主学业未精、待时，待官父逢生旺、生合世身之日可中。');
    }
    for (const z of zong) L.push('· ' + z);
    const yq = _yong_yingqi(C, '父母', fus, fu_shen, '放榜得名');
    if (yq.length) {
      L.push('【放榜应期】');
      for (const q of yq) L.push('· ' + q);
    }
    L.push('（以上依《卜筮正宗·黄金策》求名章、总断千金赋之法推演；学业功名尤在自身勤勉，卦理仅作参考。）');
    return L;
  }

  // ================= 婚姻（分男女） =================
  const _HUN_HUA_M = {
    '妻财|官鬼': '财化官，财去生官，妇心或向他人，先私后公，凶',
    '妻财|子孙': '财化子孙，子孙生财，吉',
    '妻财|兄弟': '财化兄弟，回头克财，劫妻，凶',
    '妻财|父母': '财化父母，财去克父，主与尊长不和',
    '官鬼|妻财': '鬼化财，阻隔之神化出妻财，先阻后成，吉',
    '官鬼|子孙': '鬼化子孙，子孙克官制阻，吉',
    '兄弟|妻财': '兄弟化财，克妻者化财，先争后成',
    '子孙|妻财': '子孙化财，子来生财，吉',
    '父母|妻财': '父母化财，财克父，主庚帖与妇不和'
  };
  const _HUN_HUA_F = {
    '官鬼|妻财': '官化财，财来生官（回头生），吉',
    '官鬼|子孙': '官化子孙，回头克官，凶',
    '官鬼|兄弟': '官化兄弟，兄弟泄财争竞，凶',
    '官鬼|父母': '官化父母，父母生官（回头生），吉',
    '妻财|官鬼': '财化官，财生官，吉',
    '子孙|官鬼': '子孙化官，忌神化用，然子已动先克官，先阻后解',
    '子孙|父母': '子孙化父母，父克子，忌神受制，先阻后解',
    '兄弟|官鬼': '兄弟化官，官来制兄，先争后让'
  };

  function fenxi_hunyin(paipan, gender) {
    gender = gender || '男';
    const C = _setup(paipan);
    const L = _head(paipan);
    const nan = gender === '男';
    const yong_qin = nan ? '妻财' : '官鬼';
    const yong_lbl = nan ? '妻（妇）' : '夫';
    const yongs = C['byqin'][yong_qin];
    const zis = C['byqin']['子孙'], xiongs = C['byqin']['兄弟'];
    const cais = C['byqin']['妻财'], guans = C['byqin']['官鬼'], fus = C['byqin']['父母'];
    const shi = C['shi'], ying = C['ying'], gong_wx = C['gong_wx'];
    const yong_wx = _liuqin_wuxing(gong_wx, yong_qin);
    const fushen = !yongs.length ? find_fushen(paipan, yong_qin) : null;

    const yong_wang = yongs.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const yong_kp = yongs.some(y => y['is_kong'] || y['is_po']);
    const yong_duo = yongs.length >= 2;
    const ji_dong = (nan ? xiongs : zis).some(y => y['is_dong']);
    const yuan_dong = (nan ? zis : cais).some(y => y['is_dong']);
    const shi_kp = shi['is_kong'] || shi['is_po'];
    const ying_kp = ying['is_kong'] || ying['is_po'];

    const shi_yang = shi['yinyang'] === 1;
    const ying_yang = ying['yinyang'] === 1;
    const dewei = nan ? (shi_yang && !ying_yang) : ((!shi_yang) && ying_yang);
    const yong_yy = yongs.some(y => y['yinyang'] === (nan ? 0 : 1));

    const sy_rel = get_wuxing_relation(shi['wuxing'], ying['wuxing']);
    const ys_rel = get_wuxing_relation(ying['wuxing'], shi['wuxing']);
    const shi_ying_chong = (LIUCHONG[shi['zhi']] === ying['zhi']);
    const shi_ying_he = (LIUHE[shi['zhi']] === ying['zhi']);
    const shi_ying_bi = (shi['wuxing'] === ying['wuxing']);

    const jian = [C['yx'][2], C['yx'][3]];
    const jian_dong = jian.filter(j => j['is_dong']);
    const jian_kong = jian.filter(j => j['is_kong']);
    const si_he = yongs.some(y => LIUHE[y['zhi']] === shi['zhi'] && y['is_dong']);

    L.push('【一、《黄金策·婚姻》论嫁娶（经典）】');
    L.push('· 总纲：「男女婚契于前定，朱陈缔结分在夙成。然非月老，焉知夫妇于当时；不有宓羲，' +
      '岂识吉凶于今日。欲谐伉俪，须定阴阳」——阳奇阴偶，配合成婚。如男家卜，宜世属阳、' +
      '应属阴，用神阴阳得位；女家卜，宜世阴、应阳。');
    L.push('· 六亲取用：男占女以妻财为用神（妇），女占男以官鬼为用神（夫）；世为己、应为彼，' +
      '世应生合比和则两愿成婚；间爻为媒人，父母为庚帖主婚；' +
      '男占女鬼空不妨，女占男财空不妨。');
    const _HY_JING = [
      ['阴阳相得，乃成夫妇之道；阴阳交错，难期琴瑟之鸣', '男卜女遇世阳应阴、用神得位为相得，主夫妻和顺；若世阴应阳、阴阳错位，后主夫妻欺凌、终朝反目。'],
      ['六合则易而且吉，六冲则难而又凶', '六合卦一阴一阳配合、世应相生、六爻相合，占主得之必成而吉；六冲卦纯阳纯阴，其象如二女同居、两男并处，志必不合，主难成，纵成亦不利。'],
      ['世合应应合世，终成种玉之缘', '男家卜世为男家、应女家，若得相合是两愿之象，主易成，后亦吉利。'],
      ['如逢财鬼空亡，乃婚姻之大忌；苟遇阴阳得位，实天命之所关', '卜女以财、卜男以官为用神，若值空亡必不吉利；然不可执泥——男占女以财为主，鬼空不妨，女占男以鬼为主，财空不妨。'],
      ['应财世鬼，终须夫唱妇随；应鬼世财，不免夫权妻夺', '男自占世持鬼应持财，阴阳得位，夫秉男权、妻操妇道，夫唱妇随；若世持财应持鬼，是阴阳失位，必夫权妻夺，唯入赘反吉。'],
      ['鬼克世爻，果信绿窗之难嫁；用合身位，方知绮席之易婚', '如鬼煞克世，不独不愿为婚，更防祸殃；若用神合身合世位，不独易成，日后必恩爱。'],
      ['财鬼如无刑害，夫妻定主和谐', '财、鬼不被刑冲克害，夫妻必到老和谐；若刑冲克害，必不睦。'],
      ['财官动合，先私而后公', '夫占以财为妇，世与动合、或财与世爻动合，是必先通而后娶；财爻动与旁爻合，是与他人有情，财遇合多亦然。'],
      ['两父齐兴，必有争盟之象；双官俱动，斯为竞娶之端', '卦中动变见两重父母，主有两人主婚、两家庚帖；两鬼俱动则有两家争婚、事多反复。'],
      ['欲通媒妁，须论间爻', '占庚帖以间爻（三、四爻）为媒人；间爻与世生合言我家亲，与应生合言彼家亲，与世应俱生合则两家皆亲，旺相新亲、休囚旧眷。'],
      ['世应化空，始成而终悔', '世动生合应则男家愿成、应动生合世则女家愿嫁，皆易成；但怕变入空亡，必初成而后悔。'],
      ['内外互摇，定见家庭之挠括', '占婚姻卦宜安静，安静则家庭和睦；财动则不和公姑，鬼动则不和妯娌，父动则不和子侄，兄动则不和妻妾，加月建日辰不唯不和更有刑克。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _HY_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    if (dewei) L.push('· 「阴阳相得，乃成夫妇之道」——世应阴阳得位，主夫妻和顺。');
    else L.push('· 「阴阳交错，难期琴瑟之鸣」——世应阴阳错位，主夫妻欺凌、终朝反目。');
    if (yong_wang) L.push('· 「用神」旺相，配偶得地、姻缘有望。');
    if (yong_kp || !yongs.length) L.push('· 「如逢财鬼空亡，乃婚姻之大忌」——用神空破或不上卦，无对象、姻缘难成。');
    if (yong_duo) L.push('· 「财官叠见，重为一度之新人」——用神两现，主再婚、多角，事有反复。');
    if (shi_ying_he || (sy_rel === '生' && ys_rel === '生'))
      L.push('· 「世合应、应合世，终成种玉之缘」——两愿相合，主易成、后吉。');
    if (shi_ying_chong)
      L.push('· 世应相冲克：旺世克衰应，恃强劫娶；得日辰动爻生合，赖人吹嘘可成。');
    if (ji_dong) {
      if (nan) L.push('· 兄弟发动克妻财，主劫妻、争财、婚姻破财。');
      else L.push('· 子孙发动克官鬼，主克夫、婚事不就。');
    }
    if (si_he) L.push('· 「财官动合，先私而后公」——用神动合世身，先有私情后论婚嫁。');
    if (shi_kp || ying_kp) {
      if (shi_kp && ying_kp) L.push('· 「世应俱空，难遂百年之连理」——双方皆无心，勉强终不遂。');
      else L.push('· 世或应空：' + (shi_kp ? '世空我无心，' : '') + (ying_kp ? '应空彼无心。' : ''));
    }

    L.push('【二、本卦婚姻逐条详断】');
    L.push(`（1）用神·${yong_qin}爻（${yong_lbl}）`);
    if (yongs.length) {
      for (const y of yongs) {
        let ex = '';
        if (y['is_dong'] && y['liushen'] === '青龙') ex = '用神临青龙发动，主喜庆、貌美、恩爱';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push(`　· 卦中不见${yong_qin}爻，${yong_lbl}之主不上卦。`);
      for (const ln of _fushen_duan(C, yong_qin)) L.push(ln);
    }

    L.push('（2）世应（己与彼）生合、阴阳得位');
    L.push(_yong_yao_duan(shi, C));
    L.push(_yong_yao_duan(ying, C));
    if (shi_ying_he) L.push('　· 世应相合（六合），两情相悦，婚易成。');
    if (shi_ying_chong) L.push('　· 世应相冲，彼此不睦，须间爻媒人说合、日月生扶方解。');
    if (shi_ying_bi) L.push('　· 世应比和，两不相下、亦不相伤，赖媒人与日辰撮合。');
    if (sy_rel === '生' && !shi_ying_chong) L.push('　· 我生合彼，我家求亲，心诚；彼生合我，彼家相就。');
    L.push('　· 阴阳：' + ((nan && dewei) ? '世阳应阴，男家得位，吉。'
      : (dewei ? '世阴应阳，女家得位，吉。' : '世应阴阳错位，主日后失序，宜调节。')));
    if (yong_yy) L.push('　· 用神阴阳得位（' + (nan ? '妻财为阴' : '官鬼为阳') + '），配身相称。');

    L.push('（3）原神·' + (nan ? '子孙（生妻财）' : '妻财（生官鬼）'));
    const yuan = nan ? zis : cais;
    if (yuan.length) {
      for (const y of yuan) {
        let ex;
        if (y['is_dong']) ex = '原神发动生用，吉';
        else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0) ex = '原神静旺，暗中生用';
        else ex = '原神静衰，生用无力';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 原神不现，用神不得其生。');
    }

    L.push('（4）忌神·' + (nan ? '兄弟（克妻财）' : '子孙（克官鬼）'));
    const ji = nan ? xiongs : zis;
    if (ji.length) {
      for (const y of ji) {
        let ex;
        if (y['is_dong']) ex = '忌神发动，克伤用神，大忌';
        else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0) ex = '忌神静旺，暗有克用之忧';
        else ex = '忌神静衰，不克用，暂无害';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 忌神不现，用神不受克，吉。');
    }

    L.push('（5）媒人·间爻（三、四爻）与庚帖·父母');
    for (const j of jian) {
      let ex = '间爻为媒人，' + (j['is_dong'] ? '媒人发动，主动说合' : '媒人安静');
      if (j['is_kong']) ex += '，媒人落空，无力';
      L.push(_yong_yao_duan(j, C, ex));
    }
    if (!jian_dong.length) L.push('　· 间爻安静，须世应冲合、或日月冲起媒人，方有人出为说合。');
    if (fus.length) {
      for (const y of fus) {
        const ex = '父母为庚帖、主婚，' + (fus.length >= 2 ? '两父母动则争盟' : '');
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 父母不现，无主婚、庚帖无力。');
    }

    L.push('（6）动爻变化吉凶');
    let xi_ji, hua_img;
    if (nan) {
      xi_ji = { '妻财': '喜', '子孙': '喜', '父母': '喜', '兄弟': '忌', '官鬼': '忌' };
      hua_img = _HUN_HUA_M;
    } else {
      xi_ji = { '官鬼': '喜', '妻财': '喜', '父母': '喜', '子孙': '忌', '兄弟': '忌' };
      hua_img = _HUN_HUA_F;
    }
    for (const ln of _bian_duan(C, xi_ji, hua_img)) L.push(ln);

    L.push('（7）卦象格局与配偶容貌');
    const sec7 = [];
    for (const ln of _sanhe_duan(C, yong_qin, yong_wx)) sec7.push(ln);
    for (const ln of _geju_duan(C, '六合主夫妻和美、姻缘易成。',
      '六冲主夫妻离散、婚事难成，纵成不利。',
      '动化六合，先有阻后和好，终成。',
      '动化六冲，先成后散，终主离异。'))
      sec7.push(ln);
    for (const y of yongs) {
      const s = C['st_of'](y);
      if (y['liushen'] === '青龙' || y['wuxing'] === '木' || y['wuxing'] === '金') {
        sec7.push('　· 用神临青龙、或属木金，主容貌秀丽；' +
          (['旺相', '有气'].indexOf(s['level']) >= 0 ? '旺则身肥、美而有才。' : ''));
      }
      if (['白虎', '腾蛇', '勾陈', '玄武'].indexOf(y['liushen']) >= 0 || y['wuxing'] === '土' || y['wuxing'] === '火') {
        sec7.push('　· 用神临虎蛇勾陈玄武、或属土火，主容貌平平或丑；' +
          (s['mu'] ? '入墓则美偏愚拙。' : '衰而有扶则丑有才能。'));
      }
    }
    if (!sec7.length) {
      if (!yongs.length) sec7.push('　· 用神伏藏未现，配偶容貌未显；本卦又非六合六冲，姻缘以用神得出、世应生合之日为断。');
      else sec7.push('　· 本卦非六合、非六冲，亦无三合，配偶容貌平和，以世应、用神旺衰生合为主。');
    }
    for (const ln of sec7) L.push(ln);

    L.push('【三、综合断语与成婚应期】');
    const zong = [];
    if (yongs.length && yong_wang && !shi_kp && !ying_kp && !shi_ying_chong) {
      if (dewei || shi_ying_he) {
        zong.push('用神旺相、世应生合、阴阳得位，又逢相合——此乃婚姻上上之卦，姻缘易成，夫妻恩爱，主大吉。');
      } else {
        zong.push('用神旺、双方不空，然世应未得生合、阴阳未纯，须媒人撮合、日月生扶，可成，成后亦吉。');
      }
    } else if (!yongs.length || yong_kp) {
      zong.push('用神空破或不上卦，无对象、姻缘难成；旺者待填实出旬、伏神得现，衰者无望。');
    } else if (yong_duo) {
      zong.push('用神两现，主再婚、多角或两家争婚，事有反复，须辨其旺衰取舍。');
    } else if (shi_kp || ying_kp) {
      if (shi_kp && ying_kp) zong.push('世应俱空，双方无心，百年之缘难遂。');
      else zong.push('世或应空，一方无心，婚难成。');
    } else if (ji_dong) {
      zong.push('忌神发动克伤用神，主劫财、争婚或克妻克夫，目前断以不吉。');
    } else if (shi_ying_chong) {
      zong.push('世应相冲，本主难成，须得间爻媒人、日月生合两边吹嘘，方可成。');
    } else {
      zong.push('用神有气而未旺，或休囚平和，主姻缘迟滞、待时，待用神逢生旺、六合、生合世应之日可成。');
    }
    for (const z of zong) L.push('· ' + z);
    const yq = _yong_yingqi(C, yong_qin, yongs, fushen, '成婚');
    if (yq.length) {
      L.push('【成婚应期】');
      for (const q of yq) L.push('· ' + q);
    }
    L.push('（以上依《卜筮正宗·黄金策》婚姻章、总断千金赋之法推演；百年姻缘尤在双方诚意与相处，卦理仅作参考。）');
    return L;
  }

  // ================= 疾病（病症·病体·医药） =================
  const _BING_WX = {
    '火': '心经之症：发热、咽干、口燥',
    '水': '肾经之症：恶寒、盗汗、遗精、白浊',
    '金': '肺经之症：咳嗽、虚怯、气喘、痰多',
    '木': '肝经之症：感冒风寒、四肢不和、筋骨酸痛',
    '土': '脾经之症：虚黄、浮肿、时气、瘟疫'
  };
  const _BING_WEI = { 1: '足', 2: '腿膝', 3: '股、腰、小腹', 4: '背、胸', 5: '面、项、胸', 6: '头' };
  const _BING_SHEN = {
    '螣蛇': '心惊、坐卧不安，重则癫狂、惊风',
    '青龙': '酒色过度、身体虚弱',
    '勾陈': '胸满肿胀、脾胃不和',
    '朱雀': '狂言乱语、身热面赤',
    '白虎': '跌打损伤、骨痛；女人血崩血晕、产后之症（白虎血神）',
    '玄武': '色欲郁闷、阴虚'
  };
  const _JI_HUA = {
    '官鬼|子孙': '病神化子孙，鬼被药克，病退，吉',
    '子孙|父母': '药化父母，回头克药，误药，凶',
    '父母|子孙': '克药者化药，先阻后愈，吉',
    '妻财|官鬼': '财化鬼，饮食伤复，病增，凶',
    '兄弟|子孙': '兄化子孙，药得生扶，吉',
    '兄弟|官鬼': '兄化鬼，病势又起，凶',
    '官鬼|官鬼': '鬼化鬼，新旧两病，迁变百端'
  };

  function fenxi_jibing(paipan, patient) {
    patient = patient || '世';
    const C = _setup(paipan);
    const L = _head(paipan);
    const gong_wx = C['gong_wx']; const shi = C['shi']; const ying = C['ying'];
    const guans = C['byqin']['官鬼']; const zis = C['byqin']['子孙']; const cais = C['byqin']['妻财'];
    const zizhan = patient === '世';

    let yongs, yong_qin, yong_wx;
    if (zizhan) {
      yongs = [shi]; yong_qin = '世爻（病人自身）'; yong_wx = shi['wuxing'];
    } else {
      yong_qin = patient; yongs = C['byqin'][patient];
      yong_wx = _liuqin_wuxing(gong_wx, patient);
    }
    const yongshen = (!zizhan && !yongs.length) ? find_fushen(paipan, patient) : null;

    const yuan_wx = Object.keys(WUXING_SHENG).find(x => WUXING_SHENG[x] === yong_wx);
    const ji_wx = Object.keys(WUXING_KE).find(x => WUXING_KE[x] === yong_wx);
    const yuans = C['yx'].filter(y => y['wuxing'] === yuan_wx);
    const jis = C['yx'].filter(y => y['wuxing'] === ji_wx);
    const yuan_dong = yuans.some(y => y['is_dong']);
    const ji_dong = jis.some(y => y['is_dong']);
    const yuan_li = yuans.filter(y => y['is_dong'] && _youli(y, C));
    const ji_li = jis.filter(y => y['is_dong'] && _youli(y, C));
    const ji_kp_dong = jis.filter(y => y['is_dong'] && !_youli(y, C));
    const yuan_li_dong = yuan_li.length > 0;
    const ji_li_dong = ji_li.length > 0;

    const guan_sts = guans.map(y => [y, C['st_of'](y)]);
    const guan_wang = guan_sts.some(([y, s]) => ['旺相', '有气'].indexOf(s['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const guan_kp = guans.some(y => y['is_kong'] || y['is_po']);
    const guan_dong = guans.some(y => y['is_dong']);
    const zi_wang = zis.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const zi_kp = (!zis.length) || zis.every(y => y['is_kong'] || y['is_po'] ||
      ['无气', '休囚'].indexOf(C['st_of'](y)['level']) >= 0);
    const zi_dong = zis.some(y => y['is_dong']);

    const yong = yongs.length ? yongs[0] : null;
    const yong_s = yong ? C['st_of'](yong) : null;
    const yong_kp = yong !== null && (yong['is_kong'] || yong['is_po']);
    const yong_mu = yong_s !== null && !!yong_s['mu'];
    const yong_ruo = yong_s !== null && (yong_s['level'] === '无气' || yong_s['level'] === '休囚');

    const grel_yong = y => {
      if (zizhan && y['is_shi']) return '持世';
      return get_wuxing_relation(y['wuxing'], yong_wx);
    };
    const guan_chishi = zizhan && guans.some(y => y['is_shi']);
    const guan_keshi = guans.some(y => grel_yong(y) === '克');
    const guan_shengshi = guans.some(y => grel_yong(y) === '生');
    let yong_bian_xiong = false;
    if (yong && yong['is_dong']) {
      const by = _bian_by_pos(C['paipan'], yong['pos']);
      if (by) {
        const rel = get_wuxing_relation(by['wuxing'], yong['wuxing']);
        if (rel === '克' || get_liuqin(gong_wx, by['wuxing']) === '官鬼') yong_bian_xiong = true;
      }
    }

    const xi_ji = {};
    for (const q of LIUQIN) {
      const qwx = _liuqin_wuxing(gong_wx, q);
      const r = get_wuxing_relation(qwx, yong_wx);
      xi_ji[q] = (r === '同' || r === '生' || r === '被克') ? '喜' : '忌';
    }

    L.push('【一、《黄金策》病症·病体·医药论疾病（经典）】');
    L.push('· 症候总纲：「凡占疾症，以官鬼爻为轻重；得病根由，独发之爻亦可推之。」');
    L.push('· 安危总纲：「欲决病痊，当究福神之动静；要知命尽，须详鬼煞之旺衰。」福神，其义轻于' +
      '子孙、重于原神；鬼煞，其理在于忌神、而不在于官鬼。凡占病遇原神旺动，即使用神空破伏藏，' +
      '其病可愈；遇忌神旺动，即使用神出现不空破，禄命当尽。');
    L.push('· 六亲取用：' + (zizhan
      ? '自占以世爻为病人，官鬼为病神、子孙为医药（解神），应爻为医生。原神（生世者）旺则生，忌神（克世者）动则危。'
      : `代占以「${yong_qin}」为病人，以生「${yong_qin}」之爻为原神、克「${yong_qin}」之爻为忌神；推占父母、丈夫病，不宜子孙发动。`));
    L.push('· 医药总纲：「病不求医生全者寡，药不对症枉死者多，欲择善者而从之，须就蓍人而问也。' +
      '应作医人，空则䏦亡而不遇；子为药饵，伏则扞格以无功」——以子孙爻为药饵、以应爻为医生，' +
      '子孙受伤墓绝或官鬼生旺，是药不对症、不能去病；应爻旬空，是医生难遇、用药无效。');
    const _JB_JING = [
      ['人孰无常？疾病无常；事孰为大？死生为大', '凡占疾症，以官鬼爻为轻重：官鬼衰则病轻、旺则病重，动则煎迫身体、安静则安卧；得病根由，独发之爻亦可推之。'],
      ['既明症候，当决安危……先看子孙，最喜生扶拱合', '子孙能克制鬼煞，古人谓之解神、福德，占病又为医药；卦中无子孙则财鬼无制，服药无效、祷神不灵。唯推占父母、丈夫病不宜子孙发动，动则伤克夫星、又克父母之原神。'],
      ['欲决病痊，当究福神之动静；要知命尽，须详鬼煞之旺衰', '福神义在子孙、重于原神，鬼煞理在忌神、不专在官鬼：原神旺动则用神空破伏藏亦愈，忌神旺动则用神不空破、禄命亦尽。'],
      ['官临福衰，药饵轻而病重', '官鬼无气、子孙旺相，是药能胜病，服之有效；若子孙休囚、官鬼旺相，是药轻病重，服之无功。'],
      ['鬼动卦中，眼下速难取效', '占药要鬼爻安静无气，若鬼发动，纵有良药，眼下取效亦迟；待鬼爻入墓、逢绝之日用药，方有效。'],
      ['世持鬼爻，病纵轻而难疗', '自占病最怕官鬼持世，病难脱体；待子孙发动、官鬼受克之日，方可言愈。'],
      ['鬼伏卦中病来莫觉，官藏世下症起如前', '官鬼不现，必是隐伏，得症不知何由；官鬼伏于世下，必是旧症复发、不时举发。'],
      ['用绝逢生，危而有救', '用神逢绝，得卦中动爻、日辰生合，是绝处逢生、凶中回吉，虽危有救；唯用神太弱，亦主病久体虚。'],
      ['主空无救，须防中道而殂', '主象（用神、病人）墓绝空破，得卦中动爻、日辰生扶拱合者无妨，无救者必死；救者，生扶拱合也。'],
      ['日加福去生扶，药医则愈', '日辰临子孙，生扶拱合用神，必得药力而愈；若子孙化出回头克、化官鬼，服药不效。'],
      ['福化忌爻，病势增加于小愈', '子孙发动本制官鬼，若化回头克、化出官鬼，必因病势稍愈时不谨慎，以致复加沉重。'],
      ['应临官鬼，防投增病之药汤', '应爻为医生，应临官鬼必非良医，或临忌神、化官鬼，俱不宜用此人之药；应临子孙乃专门医士，可托。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _JB_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    if (guan_wang && (guan_keshi || guan_chishi)) {
      L.push('· 官鬼旺相、又克世或持世，病神伤身，病势重；「鬼化长生，日下正当沉重」，发动则烦躁。');
    } else if (guan_wang && guan_shengshi) {
      L.push('· 官鬼虽旺，然不克病人、反生之，病虽有而与我有情，主病轻、渐有转机。');
    } else if (guan_dong && !guan_wang) {
      L.push('· 官鬼发动而不旺，病在变化，化进神则重、化退神则减。');
    }
    if (!guans.length) {
      L.push('· 「鬼伏卦中，病来莫觉」——官鬼不现，病隐伏、根因不知；伏于世下，必旧症复发。');
    }
    if (zi_wang && (guan_keshi || guan_chishi)) {
      L.push('· 子孙旺相，医药得力，能制克身之鬼，服药有效。');
    } else if (zi_wang) {
      L.push('· 子孙旺相，药有其力；官鬼既不克身，药力平和，调理为主。');
    }
    if (zi_kp) {
      L.push('· 子孙空绝或不上卦，是无药、药不效，「服药无效、祷神不灵」。');
    }
    if (yuan_li_dong) L.push('· 原神（生病人）有力发动，病人有救，病可愈。');
    if (ji_li_dong) L.push('· 忌神（克病人）有力发动，病人受克，病危。');
    if (ji_kp_dong.length) {
      const zs = ji_kp_dong.map(y => y['zhi']).join('、');
      L.push('· 忌神「' + zs + '」虽动，然旬空、月破或休囚无气，当前不能克病人，病暂不重；待出旬填实、得令之日方有克，须防其日。');
    }
    if (guan_chishi) L.push('· 「世持鬼爻，病纵轻而难疗」——官鬼持世，病难脱体，待子动、鬼受克之日。');

    L.push('【二、本卦疾病逐条详断】');
    L.push('（1）症候·病神官鬼（病在何处、何因）');
    if (guans.length) {
      let gy = guans[0];
      for (const c of guans) {
        const kc = [c['is_shi'] ? 1 : 0, c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [gy['is_shi'] ? 1 : 0, gy['is_dong'] ? 1 : 0, C['st_of'](gy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1]) ||
          (kc[0] === kg[0] && kc[1] === kg[1] && kc[2] > kg[2])) gy = c;
      }
      const gs = C['st_of'](gy);
      const gr = grel_yong(gy);
      let qq;
      if (gr === '克' || gr === '持世') qq = '（鬼克/持病人，病在身，重则凶）';
      else if (gr === '生') qq = '（鬼不克、反生病人，病有情，主轻）';
      else qq = '（鬼与病人比和，症轻）';
      if (gy['is_kong'] || gy['is_po']) qq = '（鬼空、月破，病神暂不发力，症轻；待填实、出破）';
      L.push('　· 五行病象：' + (_BING_WX[gy['wuxing']] || '') + qq);
      L.push('　· 部位：病在' + (_BING_WEI[gy['pos']] || '') + '（官临' + num_to_cn(gy['pos']) +
        '爻' + gy['wuxing'] + '）' + '；又《易》以乾头、坤腹、兑喉、艮手、震足、巽股、' +
        '坎耳、离目，可参看本卦上下卦。');
      if (gy['liushen']) L.push('　· 六神病象：官临' + gy['liushen'] + '，' + (_BING_SHEN[gy['liushen']] || '') + '。');
      if (guans.length >= 2) L.push('　· 卦中两现官鬼，主新旧两病、内外兼感，或症候迁变。');
      for (const y of guans) L.push(_yong_yao_duan(y, C));
    } else {
      const fs = find_fushen(paipan, '官鬼');
      if (fs) {
        L.push(`　· 官鬼不现，伏于${num_to_cn(fs['pos'])}爻「${fs['feishen']['liuqin']}${fs['feishen']['zhi']}」之下——病隐伏、根因不知` +
          (fs['pos'] === shi['pos'] ? '，伏于世下，必旧症复发。' : '。'));
        L.push('　· 伏病因由：伏财伤饥失饱、伏子酒醉耽淫、伏父劳心忧虑、伏兄口舌争竞。');
      } else {
        L.push('　· 卦无官鬼，病神不现，邪气已退（新病），或病非鬼祟、药石易为。');
      }
    }

    L.push('（2）病人·' + yong_qin + '（安危之本）');
    if (yongs.length) {
      L.push(_yong_yao_duan(yong, C));
      if (yong_bian_xiong) L.push('　· 病人动而化出官鬼、或化回头克，无日月解救，目前必见倾危，大凶。');
      if (yong_mu) L.push('　· 病人入墓，「神思困而不清」，主昏沉，待冲墓、出墓。');
      if (guan_chishi && zizhan) L.push('　· 官鬼持世，病在己身、难脱体，待鬼受克、子动之日。');
    } else {
      L.push(`　· 卦中不见「${yong_qin}」，病人之主不上卦。`);
      if (yongshen) { for (const ln of _fushen_duan(C, patient)) L.push(ln); }
      L.push('　· 「主象伏藏，定主迁延岁月」——病人伏藏，待值日、久病待值年值月方愈。');
    }

    L.push('（3）医药·子孙爻（药饵、解神，制鬼）');
    const zhen_bing = guan_keshi || guan_chishi;
    if (zis.length) {
      for (const y of zis) {
        let ex;
        if (y['is_dong']) {
          if (!_youli(y, C)) ex = '子孙动而空破，药虽有而暂不得力，待填实';
          else if (zhen_bing) ex = '子孙发动，药能制克身之鬼，吉';
          else ex = '子孙发动，官鬼本不克身，药以调理为主；防过剂伤原神';
        } else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0) {
          ex = '子孙静旺，药有其力，待发动用之';
        } else {
          ex = '子孙休囚，药轻病重，无功';
        }
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 子孙不现，无药、求医不得力，待子值日。');
    }

    L.push('（4）原神（生病人）与忌神（克病人）');
    if (yuans.length) {
      for (const y of yuans) {
        let ex;
        if (y['is_dong']) ex = '原神，' + (_youli(y, C) ? '有力发动生病人，大吉' : '发动而空破，生力暂弱，待时');
        else ex = '原神，安静，待生旺生扶';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 原神不现，病人不得生扶。');
    }
    if (jis.length) {
      for (const y of jis) {
        let ex;
        if (y['is_dong']) {
          if (_youli(y, C)) ex = '忌神，有力发动克病人，大忌';
          else ex = '忌神，动而空破（旬空/月破），当前不能克病人，待填实「' + y['zhi'] + '日」方有克，须防';
        } else {
          ex = '忌神，静而旺，暗有克伐之忧';
        }
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 忌神不现，病人不受克，吉。');
    }

    L.push('（5）医生·应爻与用药宜忌');
    L.push(_yong_yao_duan(ying, C));
    if (ying['is_kong']) L.push('　· 应爻空亡，医生非它出不来，定用药无效，须另觅良医。');
    if (ying['liuqin'] === '官鬼') L.push('　· 应临官鬼，非良医，更防投增病之药。');
    if (ying['liuqin'] === '子孙') L.push('　· 应临子孙，乃专门医士，可托。');
    if (zis.length) {
      let zy = zis[0];
      for (const c of zis) if (C['st_of'](c)['score'] > C['st_of'](zy)['score']) zy = c;
      L.push('　· 看子孙何爻，知医在何方：子北、丑寅东北、卯东、午南、酉西；' +
        `本卦子孙临「${zy['zhi']}」，可向其方位求医。`);
    }
    if (guans.length) {
      let gy = guans[0];
      for (const c of guans) {
        const kc = [c['is_shi'] ? 1 : 0, c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [gy['is_shi'] ? 1 : 0, gy['is_dong'] ? 1 : 0, C['st_of'](gy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1]) ||
          (kc[0] === kg[0] && kc[1] === kg[1] && kc[2] > kg[2])) gy = c;
      }
      if (gy['wuxing'] === '火' || gy['wuxing'] === '土')
        L.push('　· 「察官爻而用药，火土寒凉」——火土鬼病热，宜寒凉药。');
      else L.push('　· 金水官鬼病寒，宜温热之剂。');
    }
    if (!cais.length || cais.some(y => y['is_kong'])) {
      L.push('　· 「卦内无财，饮食不纳」——财空或不现，不思饮食。');
    } else if (guans.length) {
      let gy = guans[0];
      for (const c of guans) {
        const kc = [c['is_shi'] ? 1 : 0, c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [gy['is_shi'] ? 1 : 0, gy['is_dong'] ? 1 : 0, C['st_of'](gy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1]) ||
          (kc[0] === kg[0] && kc[1] === kg[1] && kc[2] > kg[2])) gy = c;
      }
      const ji_kou = {
        '水': '忌鱼鲜生冷', '木': '忌动风之物', '火': '忌炙煿热物',
        '金': '忌坚硬咸物', '土': '忌油腻滑物'
      };
      L.push('　· 饮食所忌：鬼属' + gy['wuxing'] + '，' + ji_kou[gy['wuxing']] + '。');
    }

    L.push('（6）动爻变化吉凶');
    for (const ln of _bian_duan(C, xi_ji, _JI_HUA)) L.push(ln);

    L.push('（7）卦象格局');
    const sec7 = [];
    for (const ln of _geju_duan(C, '六合主病气缠绵、不易顿解。',
      '近病（新病）逢六冲则散，主速愈；久病逢六冲则凶。',
      '动化六合，病势缠结。',
      '动化六冲，近病主散、久病主危。'))
      sec7.push(ln);
    if (!sec7.length) sec7.push('　· 本卦非六合、非六冲，病势以病人、官鬼、原神、忌神旺衰动静为主。');
    for (const ln of sec7) L.push(ln);

    L.push('【三、综合断语（安危）与病愈应期】');
    const zong = [];
    const yong_ok = ((yong_s !== null && (yong_s['level'] === '旺相' || yong_s['level'] === '有气')) || yuan_li_dong);
    const kpz = ji_kp_dong.map(y => y['zhi']).join('、');
    if (yong_bian_xiong) {
      zong.push('病人动而化鬼、化回头克，无日月动爻解救，「目前必见倾危」，主大凶。');
    } else if (yongs.length) {
      if (ji_li_dong && !(yuan_li_dong || zi_wang)) {
        zong.push('忌神（克病人）有力发动，病人衰弱、无救，「禄命当尽」之象，主危；急需制忌神、扶病人。');
      } else if (ji_li_dong && (yuan_li_dong || zi_wang)) {
        zong.push('虽忌神发动克病人，然病人得原神生扶、或医药制之，主先凶后解，可愈，待忌神受克、原神值日。');
      } else if (yuan_li_dong && ji_kp_dong.length) {
        zong.push('病人得原神有力动生，忌神「' + kpz + '」动而空破，当前不能克病人——' +
          '目前有转机、可愈；唯须防忌神出旬填实、得令之日（' + kpz + '日）病势反复，药宜早备。');
      } else if (yuan_li_dong && (yong_ruo || yong_kp || yong_mu)) {
        zong.push('病人虽休囚、空破或入墓，原神有力发动相生，「绝处逢生」，其病可愈，待生扶之日。');
      } else if (yuan_li_dong || (yong_ok && !ji_li_dong && (zi_wang || zi_dong))) {
        zong.push('病人得原神生扶、医药得力，忌神不克——病虽现，可治，主愈，吉。');
      } else if (ji_kp_dong.length) {
        zong.push('忌神「' + kpz + '」动而空破，当前不能克病人，病暂不重；待出旬填实、得令之日（' + kpz + '日）方有克，须防。');
      } else if (guan_wang && (guan_keshi || guan_chishi) && zi_kp) {
        zong.push('病神旺、克身或持世，医药子孙空绝，「药轻病重」，难治，待子旺、鬼受克之日方有转机。');
      } else if (guan_chishi) {
        zong.push('官鬼持世，病难脱体，待子动、鬼受克墓绝之日方愈。');
      } else if (yong_ok && !ji_li_dong) {
        zong.push('病人有气、不受克，病势轻，调理得宜，待生旺、子动之日愈。');
      } else {
        zong.push('病人、病神各有强弱，吉凶未定，以原神、医药（子孙）旺动为愈，忌神、病神旺动为危。');
      }
    } else {
      if (yongshen && yuan_li_dong) {
        zong.push('病人不上卦、伏藏，原神有力发动，待伏神得现、生扶之日可愈，属先凶后解。');
      } else if (guan_wang && zi_kp) {
        zong.push('病神旺、医药无，病人之主又伏藏，主危，急需良医良药。');
      } else {
        zong.push('病人伏藏，症候迁延，待值日、值月方愈。');
      }
    }
    for (const z of zong) L.push('· ' + z);

    if (yongs.length) {
      const yq = _yong_yingqi(C, yong_qin.replace('（病人自身）', ''), yongs, yongshen, '病愈');
      if (yq.length) {
        L.push('【病愈应期】');
        for (const q of yq) L.push('· ' + q);
      }
    }
    if (guans.length) {
      let gy = guans[0];
      for (const c of guans) {
        const kc = [c['is_shi'] ? 1 : 0, c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [gy['is_shi'] ? 1 : 0, gy['is_dong'] ? 1 : 0, C['st_of'](gy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1]) ||
          (kc[0] === kg[0] && kc[1] === kg[1] && kc[2] > kg[2])) gy = c;
      }
      L.push('· 病愈又可候：子孙（医药）值日、或官鬼入墓绝受克之日；' +
        `本病鬼${gy['zhi']}，墓于${_MUKU[gy['wuxing']]}、绝于${_JUEDI[gy['wuxing']]}，至其日病退。`);
    }
    if (ji_li_dong || ji_kp_dong.length) {
      let jj = jis[0];
      for (const c of jis) {
        const kc = [c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [jj['is_dong'] ? 1 : 0, C['st_of'](jj)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1])) jj = c;
      }
      if (ji_kp_dong.length && !ji_li_dong) {
        L.push(`· 须防：忌神「${jj['zhi']}」出旬填实、得令之日，病势反复；得日月动爻冲克忌神可免。`);
      } else {
        L.push(`· 须防：忌神值日、得令之日，即「${jj['zhi']}」前后；得日月动爻冲克忌神可免。`);
      }
    }
    L.push(_YQ_TAIL);
    L.push('（以上依《卜筮正宗·黄金策》病症、病体、医药三章及总断千金赋推演；有病应及时就医，卦理仅作参考，切勿因此延误诊治。）');
    return L;
  }

  // ================= 子女（产育） =================
  const _YANG_ZHI = ['子', '寅', '辰', '午', '申', '戌'];
  const _YIN_ZHI = ['丑', '卯', '巳', '未', '酉', '亥'];
  const _ZINV_HUA = {
    '妻财|子孙': '财化子孙，产母化出儿女，分娩即当勿药之喜，大吉',
    '子孙|妻财': '子孙化财，儿女化出回头之生，子易养，吉',
    '官鬼|子孙': '鬼化子孙，忧化解为福德，先忧后喜，吉',
    '子孙|官鬼': '子孙化官鬼，福被伤而胎化鬼，子当屈死腹中，大凶',
    '父母|子孙': '父母化子孙，忌神化用，然父已先动克子，先险后安',
    '子孙|父母': '子孙化父母，儿女化回头之克，难为厥子，凶',
    '兄弟|妻财': '兄弟化财，产母受克，防产母不安',
    '父母|官鬼': '父母化官鬼，忧神并起，难产、伤子，凶'
  };

  function fenxi_zinv(paipan) {
    const C = _setup(paipan);
    const L = _head(paipan);
    const p = C['paipan']; const shi = C['shi']; const ying = C['ying']; const gong_wx = C['gong_wx'];
    const zis = C['byqin']['子孙']; const cais = C['byqin']['妻财'];
    const fus = C['byqin']['父母']; const guans = C['byqin']['官鬼']; const xiongs = C['byqin']['兄弟'];
    const yong_wx = _liuqin_wuxing(gong_wx, '子孙');

    const fushen = !zis.length ? find_fushen(paipan, '子孙') : null;

    const zi_sts = zis.map(y => [y, C['st_of'](y)]);
    const zi_wang = zi_sts.some(([y, s]) => ['旺相', '有气'].indexOf(s['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const zi_kp = zis.some(y => y['is_kong'] || y['is_po']);
    const fu_dong = fus.some(y => y['is_dong'] && _youli(y, C));
    const fu_kp = (!fus.length) || fus.every(y => y['is_kong'] || y['is_po']);
    const guan_dong = guans.some(y => y['is_dong'] && _youli(y, C));
    const cai_wang = cais.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const cai_kp = (!cais.length) || cais.every(y => y['is_kong'] || y['is_po']);
    const xiong_dong = xiongs.some(y => y['is_dong'] && _youli(y, C));

    const zrel = y => {
      if (y['is_shi']) return '持世';
      return get_wuxing_relation(y['wuxing'], shi['wuxing']);
    };
    const zi_keshi = zis.some(y => zrel(y) === '克');
    const zi_chongshi = zis.some(y => LIUCHONG[y['zhi']] === shi['zhi']);
    let zi_long = false, nannv;
    if (zis.length) {
      let zy = zis[0];
      for (const c of zis) {
        const kc = [c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [zy['is_dong'] ? 1 : 0, C['st_of'](zy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1])) zy = c;
      }
      const is_nan = _YANG_ZHI.indexOf(zy['zhi']) >= 0;
      zi_long = zy['liushen'] === '青龙';
      if (is_nan && (zi_wang || zi_long)) nannv = `男（子孙临阳支${zy['zhi']}，旺相/青龙，主俊秀男儿）`;
      else if ((!is_nan) && !zi_wang) nannv = `女（子孙临阴支${zy['zhi']}，休囚，主女儿）`;
      else if (is_nan) nannv = `偏男（子孙阳支${zy['zhi']}）`;
      else nannv = `偏女（子孙阴支${zy['zhi']}）`;
    } else {
      nannv = '子孙不现，须查伏神定男女';
    }

    L.push('【一、《黄金策·产育》论子女（经典）】');
    L.push('· 总纲：「盖得阴阳交感，方能胎孕相生，先看子孙，便知男女。阳为男子，掌中探见一枝新；' +
      '阴是女儿，门右喜看弧蜕设」——子孙为占产用神，旺相单重为阳爻是男，休囚交拆为阴爻是女。');
    L.push('· 六亲取用：子孙爻为占产、占子息之用神（儿女）；妻财为原神、为产母（生子孙）；' +
      '父母为忌神（克子孙，主伤子、难产）；官鬼为忧神（疾病、血光）；兄弟发动则克妻财，不利产母。');
    const _ZN_JING = [
      ['主星生旺，当生俊秀之肥儿；命曜休囚，必产委糜之弱子', '子孙生旺，子必肥大，异日主俊秀不凡；休囚无气，子必弱小，异日主萎靡不振。'],
      ['如无福德，莫究胎爻', '用神（子孙）不出现，当查伏于何爻之下，以伏神旺衰吉凶断之，不必拘泥胎爻。'],
      ['双胎双福必双生，一克一刑终一梦', '卦有两重子孙、又有两重胎爻，纵不发动亦主双生；卦无子孙、胎爻又被月建日辰动爻刑克，大凶，一场春梦，言其子必亡。'],
      ['胎临官鬼，怀妊便有采薪忧；财化子孙，分娩即当勿药喜', '鬼临胎爻主孕妇有疾；若财合福爻、或财化子孙，则分娩安泰，不药而喜。'],
      ['妻财一位喜见持持，胎福二爻怕逢伤害', '占产以财为产母、福为儿女，皆喜月建日辰动爻生扶合助，则产母安、子易养；见刑冲克害、化入死墓空绝，则产母多灾、子难养。'],
      ['虎作血神，值事交重胎已破', '白虎为血神，若临子孙或胎爻发动，其胎已破；临财爻发动亦然。'],
      ['龙为喜气，遇胎发动日将临', '占产以青龙为喜，若在胎福财爻上动者，生期已速，必当日临盆。'],
      ['福遇龙空，胎动乃堕胎虚喜', '福临青龙却空亡受制，又见胎爻发动或被日辰动爻冲，乃堕胎虚喜。'],
      ['福被伤而胎仍化鬼，子当屈死于腹中', '子孙墓绝、又被日月动爻刑冲克害者大凶；或胎临官鬼、动化鬼，必是死胎。'],
      ['兄动兮不利其妻，父兴兮难为厥子', '兄动则克妻财（产母不安），父动则克子孙（难为厥子）；夫卜妻产，见兄动产母不安，见父动难为其子。'],
      ['用在空亡逢恶煞，何妨坐草之虞', '父爻发动本克子孙，若福爻得月建日辰生扶、或避空不受克，谓之无虞。'],
      ['克世克身诞生日迫，不冲不发产日时迟', '子孙胎爻冲克身世，生期以速，当日可断；胎福不动又无暗冲，必然迟缓，待冲月日时方分娩。'],
      ['胎福齐兴官父合，临产难生', '胎福二爻发动本主易生，若被官鬼、父母动爻合住或日辰合住，皆主临产难生，待冲破日时方娩。'],
      ['阳福会青龙，无异桂庭之秀子；阴孙非月建，何殊桃洞之仙姬', '子孙临月建、青龙或月建带青龙生合子孙者，必是男喜，后主俊秀聪明；子孙非月建日辰、又无月日生之、临阴象阴爻者，必是女。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _ZN_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    L.push('· 本卦子孙之象：' + nannv + '。');
    if (zi_wang && cai_wang && !fu_dong)
      L.push('· 「主星生旺，当生俊秀之肥儿」，又得妻财（产母）生扶、父母不克——母子平安，子易养成。');
    if (!zis.length && fushen)
      L.push('· 「如无福德，莫究胎爻」——子孙不现，查伏神以断子女有无、吉凶。');
    if (fu_dong)
      L.push('· 「父兴兮难为厥子」——父母爻有力发动，克伤子孙，主伤子、难产、子难养，大忌。');
    if (guan_dong && !zi_wang)
      L.push('· 「胎临官鬼，怀妊便有采薪忧」「福被伤而胎仍化鬼，子当屈死于腹中」——官鬼有力发动、子孙无气，主孕妇有疾、胞胎不安，须防。');
    if (guan_dong && cai_wang)
      L.push('· 「财化子孙，分娩即当勿药喜」——虽官鬼发动有忧，然财爻旺相、福神有根，分娩安泰。');
    if (zi_kp && zis.length)
      L.push('· 子孙空亡、月破，主儿女之福不实，旺者待填实出旬，衰者主子息艰难。');
    if (xiong_dong)
      L.push('· 「兄动兮不利其妻」——兄弟发动克妻财，主产母不安、费财。');
    if ((zi_keshi || zi_chongshi) && zi_wang)
      L.push('· 「克世克身诞生日迫」——子孙旺而动冲克身世，生期已速，当日可待。');
    if (zi_long)
      L.push('· 「龙为喜气，遇胎发动日将临」——青龙临子孙，临产之喜，生期近。');
    if (!(zi_keshi || zi_chongshi) && zis.length && !zis.some(y => y['is_dong']))
      L.push('· 「不冲不发产日时迟」——子孙安静、不冲身世，产期尚缓，待逢冲月日时。');

    L.push('【二、本卦子女逐条详断】');
    L.push('（1）用神·子孙爻（儿女）与男女之辨');
    if (zis.length) {
      for (const y of zis) {
        const xx = [];
        if (_YANG_ZHI.indexOf(y['zhi']) >= 0) {
          xx.push(['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0
            ? '阳支，子孙旺相单重为男'
            : '阳支而休囚，男女须再参青龙月建');
        } else {
          xx.push(['无气', '休囚'].indexOf(C['st_of'](y)['level']) >= 0
            ? '阴支，休囚交拆为女'
            : '阴支而旺相，男女须再参青龙月建');
        }
        if (y['liushen'] === '青龙') xx.push('临青龙，主喜气、俊秀');
        if (y['liushen'] === '白虎') xx.push('临白虎血神，防血光、胎破');
        if (zis.length >= 2) xx.push('卦中两重子孙，主双生或子女多');
        L.push(_yong_yao_duan(y, C, xx.join('；')));
      }
    } else {
      L.push('　· 卦中不见子孙爻，儿女之主不上卦。');
      for (const ln of _fushen_duan(C, '子孙')) L.push(ln);
    }

    L.push('（2）原神·妻财爻（产母，生子孙）');
    if (cais.length) {
      for (const y of cais) L.push(_yong_yao_duan(y, C));
    } else {
      L.push('　· 妻财不现，产母之爻伏藏，子失其生源，子息较难。');
    }

    L.push('（3）忌神·父母爻（克子孙，主伤子难产）');
    if (fus.length) {
      for (const y of fus) {
        let ex;
        if (y['is_dong']) {
          ex = _youli(y, C)
            ? '父母发动克子孙，「难为厥子」，主伤子、难产，大忌'
            : '父母动而空破，暂不克子，待填实须防';
        } else if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0) {
          ex = '父母静旺，暗有克子之势，待发动则伤';
        } else {
          ex = '父母休囚，不克子孙，无碍';
        }
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 父母不现，克子之神不兴，子易养成，吉。');
    }

    L.push('（4）忧神·官鬼（疾病、血光）与兄弟（克产母）');
    if (guans.length) {
      for (const y of guans) {
        let ex;
        if (y['is_dong']) ex = _youli(y, C)
          ? '官鬼发动，主孕妇有疾、忧惊、血光'
          : '官鬼动而空破，忧而不实';
        else ex = '官鬼安静，忧疑轻';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 官鬼不现，无疾病、血光之忧。');
    }
    if (xiongs.length) {
      for (const y of xiongs) {
        if (y['is_dong']) L.push(_yong_yao_duan(y, C, '兄弟发动克妻财，主产母不安、耗财'));
      }
    } else {
      L.push('　· 兄弟不现，产母不受克。');
    }

    L.push('（5）动爻变化吉凶');
    for (const ln of _bian_duan(C, { '子孙': '喜', '妻财': '喜', '官鬼': '忌', '父母': '忌', '兄弟': '忌' }, _ZINV_HUA))
      L.push(ln);

    L.push('（6）卦象格局');
    for (const ln of _sanhe_duan(C, '子孙', yong_wx)) L.push(ln);
    for (const ln of _geju_duan(C, '六合主怀胎安稳、子易养成。',
      '六冲主胎动不安、子息难成，占产逢冲亦主速生。',
      '动化六合，先险后安。',
      '动化六冲，占产主速生，然子息难留。'))
      L.push(ln);

    L.push('【三、综合断语与分娩应期】');
    const zong = [];
    if (!zis.length) {
      let _help = [];
      if (fushen) {
        if (['同', '生'].indexOf(get_wuxing_relation(DIZHI_WUXING[C['yue']], fushen['wuxing'])) >= 0) _help.push('月建');
        if (['同', '生'].indexOf(get_wuxing_relation(DIZHI_WUXING[C['ri']], fushen['wuxing'])) >= 0) _help.push('日辰');
      }
      if (fushen && _help.length) {
        zong.push('卦中无子孙，然伏子得' + _help.join('、') + '生扶，「如无福德，莫究胎爻」，待伏神出现、冲开飞神之日方得子息，属先无后有。');
      } else {
        zong.push('卦无子孙、伏子又不得时令，子息艰难，宜静养待时，多积德行善以求。');
      }
      if (guan_dong)
        zong.push('卦中官鬼发动，「胎临官鬼，怀妊便有采薪忧」，主孕期有疾、临产忧惊，宜加意调护、按时产检；伏子待引，官鬼之动未必即伤子，然忧惊不可不防。');
      if (xiong_dong)
        zong.push('兄弟发动克妻财（产母），「兄动兮不利其妻」，主产母不安、耗费。');
      if (fu_dong)
        zong.push('父母发动克子孙，「父兴兮难为厥子」，纵得子亦防难养。');
    } else {
      if (zi_wang && cai_wang && !fu_dong && !(guan_dong && !zi_wang)) {
        zong.push('子孙旺相、妻财（产母）生扶、父母不克，官鬼不肆——此乃产育、子息之吉卦，母子平安，孩子俊秀易养。');
      } else if (fu_dong && !zi_wang) {
        zong.push('父母爻有力发动克子孙，「父兴兮难为厥子」，主伤子、难产、子难养，须待父母受克、子孙逢值之日方解。');
      } else if (guan_dong && zi_kp) {
        zong.push('官鬼发动、子孙空破，「福被伤而胎仍化鬼」，胞胎、产妇可忧，须防；得财爻生合子孙方有救。');
      } else if (zi_kp) {
        zong.push('子孙空亡、月破，儿女之福不实，旺者待填实出旬可得，衰者主子息迟、虚喜。');
      } else if (guan_dong) {
        zong.push('官鬼发动，主孕妇有疾、临产忧惊；所幸子孙有根、得财生扶，「分娩即当勿药喜」，先忧后吉。');
      } else {
        zong.push('子孙平和有气，无父母、官鬼之克，主子息平稳，产期待子孙逢冲、逢值之日。');
      }
    }
    for (const z of zong) L.push('· ' + z);

    const yq = _yong_yingqi(C, '子孙', zis, fushen, '分娩/得子');
    if (yq.length) {
      L.push('【分娩应期】');
      for (const q of yq) L.push('· ' + q);
    }
    L.push('（以上依《卜筮正宗·黄金策》产育章之法推演，为软件据卦理之分析；生育之事顺遂自然，务必按时产检、就医院分娩，卦理仅作参考。）');
    return L;
  }

  // ================= 出行（商贾·逃亡） =================
  function fenxi_chuxing(paipan) {
    const C = _setup(paipan);
    const L = _head(paipan);
    const p = C['paipan']; const shi = C['shi']; const ying = C['ying'];
    const guans = C['byqin']['官鬼']; const zis = C['byqin']['子孙']; const cais = C['byqin']['妻财'];
    const fus = C['byqin']['父母']; const xiongs = C['byqin']['兄弟'];
    const yao5 = C['yx'][4];

    const srel_to_shi = y => {
      if (y['is_shi']) return '持世';
      return get_wuxing_relation(y['wuxing'], shi['wuxing']);
    };
    const guan_keshi = guans.some(y => srel_to_shi(y) === '克');
    const guan_dong_li = guans.some(y => y['is_dong'] && _youli(y, C));
    const guan_yao5 = (yao5['liuqin'] === '官鬼') && yao5['is_dong'] && _youli(yao5, C);
    const guan_chishi_dong = guans.some(y => y['is_shi'] && y['is_dong'] && _youli(y, C));
    const zi_dong = zis.some(y => y['is_dong'] && _youli(y, C));
    const zi_wang = zis.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const shi_s = C['st_of'](shi);
    const shi_wang = shi_s['level'] === '旺相' || shi_s['level'] === '有气';
    const ying_rel = get_wuxing_relation(ying['wuxing'], shi['wuxing']);
    const shi_rel = get_wuxing_relation(shi['wuxing'], ying['wuxing']);
    const you_hun = (p['gongwei'] === '游魂');
    const gui_hun = (p['gongwei'] === '归魂');
    const liu_chong = LIUCHONG_GUA.indexOf(p['name']) >= 0;
    const liu_he = LIUHE_GUA.indexOf(p['name']) >= 0;
    const bian_chong = !!(p['bian_gua'] && LIUCHONG_GUA.indexOf(p['bian_gua']['name']) >= 0);
    const bian_he = !!(p['bian_gua'] && LIUHE_GUA.indexOf(p['bian_gua']['name']) >= 0);

    L.push('【一、《黄金策》论出行（经典）】');
    L.push('· 说明：《黄金策》无出行专章，出行、行人之理散见于「商贾」（出行经商）与「逃亡」（行人归否）二章，其理一贯。世为出行之人，应为所往之地，五爻为道路。');
    L.push('· 六亲取用：世爻为出行人自己；应爻为地头、彼处、所投之人；五爻为道路；' +
      '官鬼为途中灾厄、风波盗贼；子孙为福德、解神（制鬼消灾）；妻财为盘缠、利息；' +
      '父母为行李、文书、舟车（动则辛劳、克子孙）；兄弟为同伴、为耗财。');
    const _CX_JING = [
      ['路上有官休出外', '五爻为道路，临官鬼发动，途中必多惊险，不宜出外；以所临六神断灾——白虎为风波、玄武为盗贼、勾陈为阻滞、螣蛇为惊恐、朱雀为口舌。'],
      ['鬼克身爻，商贩者必遭盗贼', '买卖经商、出行在外，若遇官鬼临玄武发动来克世爻，必遭盗贼之祸。'],
      ['日月相合，开行定主有人投', '开行、出行占吉凶，世应俱要不空、财福要全备、官鬼要有气（或静而受克）、父兄要衰静，斯为上吉；更得月建、日辰、动爻生合世爻，则近悦远来，财利必顺；动出官兄常有是非口舌，应空主开不成、彼处无依。'],
      ['归魂卦用遇生合，不捕而自回；游魂卦应又交重，能潜而会遁', '出行行人占，归魂主归、主恋家不出；游魂主游走、行远、去而不定。'],
      ['内近外远，生世则终有归期', '用爻在内卦人在近处，在外卦在远处；最喜生合持世，人虽远去，日后自当归来，寻之易见。'],
      ['静易动难，坐空则必无寻路', '用爻不动，人易寻、行有定；动则迁移无常，指东言西；若落空亡，杳无踪迹。'],
      ['合起合住，若非容隐即相留', '用静逢合则合起、用动逢合则合住；日辰动爻合住用神，必有牵绊、容留，主欲行而被留、动身迟滞。'],
      ['冲动冲开，不是使令当败露', '静爻逢冲为冲动，动爻逢冲为冲开；逢冲则动，主速行、起程、阻滞被冲开。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _CX_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    if (guan_yao5) {
      const zai = {
        '白虎': '主风波、跌打', '玄武': '主盗贼、失脱', '勾陈': '主阻滞、羁留',
        '螣蛇': '主惊恐、虚惊', '朱雀': '主口舌、官非'
      }[yao5['liushen']] || '主灾厄';
      L.push('· 「路上有官休出外」——五爻（道路）临官鬼发动，途中多惊险，不宜出行；临' + yao5['liushen'] + '，' + zai + '。');
    }
    if (guan_keshi && guan_dong_li)
      L.push('· 「鬼克身爻，商贩者必遭盗贼」——官鬼有力发动来克世，出行有灾，宜暂缓。');
    if (gui_hun)
      L.push('· 「归魂卦用遇生合，不捕而自回」——归魂主归、恋家，「归魂不出疆」，占出行主行不成、欲行又止、去而复返。');
    if (you_hun)
      L.push('· 「游魂卦应又交重，能潜而会遁」——游魂主游走、行远，占出行利起身、行踪不定。');
    if (liu_chong || bian_chong)
      L.push('· 六冲主动、主散，占出行逢冲则行期速、动身快；动化六冲，先动后散。');
    if (liu_he || bian_he)
      L.push('· 「合起合住，若非容隐即相留」——六合主牵绊、合住，占出行主行期迟、被事绊住、动身不易。');
    if (ying['is_kong'])
      L.push('· 应爻（地头）空亡，彼处无依、所投落空，去之无益。');
    if (ying_rel === '生' && !ying['is_kong'])
      L.push('· 应爻生合世爻，到地头得人照拂、诸事顺遂。');
    if (zi_dong && !(guan_keshi && guan_dong_li))
      L.push('· 子孙（福德、解神）发动，能制鬼消灾，出行一路平安，吉。');
    if (shi['is_kong'] || shi['is_po'])
      L.push('· 世爻（出行人）空亡、月破，己身无力，不宜远行，待出空填实。');

    L.push('【二、本卦出行逐条详断】');
    L.push('（1）出行人·世爻');
    L.push(_yong_yao_duan(shi, C));
    if (shi_wang && !shi['is_kong'] && !shi['is_po'])
      L.push('　· 世爻旺相有气，出行人自身强健、谋为得力。');
    else
      L.push('　· 世爻休囚、空破，自身力弱，远行不利，宜缓行或改期。');

    L.push('（2）地头·应爻（彼处、所投之人）');
    L.push(_yong_yao_duan(ying, C));
    if (ying_rel === '生') L.push('　· 应生世，彼处得益、人来就我，吉。');
    else if (ying_rel === '克') L.push('　· 应克世，彼处有压、人地不宜，须防。');
    else if (shi_rel === '生') L.push('　· 世生应，我去求人、劳心费力。');
    else if (ying['is_kong']) L.push('　· 应空，地头无依、所求不遂。');
    else L.push('　· 世应比和，彼我相安，平稳。');

    L.push('（3）道路·五爻与灾厄·官鬼');
    L.push(_yong_yao_duan(yao5, C, '五爻为道路'));
    if (guans.length) {
      for (const y of guans) {
        let ex;
        if (y['is_dong']) {
          if (!_youli(y, C)) ex = '官鬼动而空破，险而不实，待填实须防';
          else if (y['pos'] === 5) ex = '官鬼在道路（五爻）发动，途中有险，尤忌';
          else if (y['is_shi']) ex = '官鬼持世发动，灾近身，出行有阻、有忧惊';
          else ex = '官鬼发动，途中有险、忧惊';
          if (y['liushen']) {
            ex += '；临' + y['liushen'] + (
              y['liushen'] === '白虎' ? '主风波、水患'
              : y['liushen'] === '玄武' ? '主盗贼'
              : y['liushen'] === '勾陈' ? '主阻滞'
              : y['liushen'] === '螣蛇' ? '主惊恐'
              : y['liushen'] === '朱雀' ? '主口舌' : '');
          }
        } else {
          ex = '官鬼安静，途中无大灾';
        }
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 官鬼不现，途中无灾，吉。');
    }

    L.push('（4）福德·子孙（解神）、盘缠·妻财、行李·父母、同伴·兄弟');
    if (zis.length) {
      for (const y of zis) {
        const ex = (y['is_dong'] && _youli(y, C))
          ? '子孙发动，制鬼消灾，出行得福'
          : '子孙安静，逢官鬼发动之日宜提防';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 子孙不现，福德解神不现，官鬼无制，出行宜谨慎。');
    }
    if (cais.length) {
      for (const y of cais) L.push(_yong_yao_duan(y, C, '妻财为盘缠、利息'));
    } else {
      L.push('　· 妻财不现，盘缠不足、出外少利。');
    }
    if (fus.length) {
      for (const y of fus) {
        if (y['is_dong']) L.push(_yong_yao_duan(y, C, '父母为行李、舟车、文书，动则行程劳碌、且克子孙'));
      }
    }
    if (xiongs.length) {
      for (const y of xiongs) {
        if (y['is_dong']) L.push(_yong_yao_duan(y, C, '兄弟为同伴、为耗财，动则同伴多、破费、口舌'));
      }
    }

    L.push('（5）卦象格局（行期迟速、远近）');
    const ge = [];
    if (you_hun) ge.push('　· 游魂卦：主行远、好动，利起身、外出，行踪不定。');
    if (gui_hun) ge.push('　· 归魂卦：主归、主恋家，「归魂不出疆」，占出行主行不成、欲行又止、去而复返。');
    if (liu_chong) ge.push('　· 六冲卦：主动主散，行期速、动身快。');
    if (liu_he) ge.push('　· 六冲之反，六合卦主牵绊、合住，行期迟、被事绊住。');
    if (bian_chong) ge.push('　· 动化六冲：先起身后分散，行程有变动。');
    if (bian_he) ge.push('　· 动化六合：初欲行而终被合住，迟滞、留连。');
    if (!ge.length) ge.push('　· 非游魂、归魂、六冲、六合，行期迟速以世爻、道路（五爻）、合冲动静为主。');
    for (const ln of ge) L.push(ln);

    L.push('【三、综合断语与动身应期】');
    const zong = [];
    if (guan_yao5 || (guan_keshi && guan_dong_li && !zi_dong) || (guan_chishi_dong && !zi_dong)) {
      if (guan_yao5) {
        zong.push('五爻（道路）临官鬼发动，又无子孙解救——「路上有官休出外」，途中必有惊险（风波、盗贼、阻滞），此行不宜，宜暂缓、改期，待官鬼受克、子孙值日再行。');
      } else if (guan_chishi_dong) {
        zong.push('官鬼持世发动、又无子孙福德制鬼，灾近身，主出行有阻、途中忧惊惊险——「路上有官休出外」，宜暂缓，待官鬼受克、子孙值日再行。');
      } else {
        zong.push('官鬼有力发动克世，又无子孙解救——「路上有官休出外」，途中必有惊险（风波、盗贼、阻滞），此行不宜，宜暂缓、改期，待官鬼受克、子孙值日再行。');
      }
    } else if (gui_hun || (liu_he && !(you_hun || liu_chong))) {
      zong.push('卦逢归魂（或六合牵绊），「归魂不出疆」，主行不成、欲行又止、被事绊住，勉强行之亦迟滞、去而复返；待冲开合绊之日方动身。');
    } else if (shi_wang && !shi['is_kong'] && !shi['is_po'] && (zi_dong || zi_wang)
      && !(guan_keshi && guan_dong_li) && !guan_chishi_dong && !ying['is_kong']) {
      if (you_hun || liu_chong) {
        zong.push('世爻旺相、子孙福德制鬼、应不空，又逢游魂、六冲——出行大吉，行期迅速、一路平安、到地头得意。');
      } else {
        zong.push('世爻旺相、子孙得力、官鬼不克、应不空——出行平稳吉利，唯行期以冲开、逢值之日为定。');
      }
    } else if (shi['is_kong'] || shi['is_po']) {
      zong.push('世爻空亡、月破，出行人己身无力，不宜远行，待出空、填实、逢合之日再议。');
    } else if (ying['is_kong']) {
      zong.push('应爻（地头）空亡，彼处无依、所投落空，去之无益，宜另图或改期。');
    } else {
      zong.push('出行卦象平中带小阻，世爻有气、官鬼不肆则可行，行期待冲开合绊、世爻逢值之日；若临官鬼受克之日，途中须防灾。');
    }
    for (const z of zong) L.push('· ' + z);

    L.push('【动身应期】');
    const chong_shi = LIUCHONG[shi['zhi']] || '';
    const he_shi = LIUHE[shi['zhi']] || '';
    if ((liu_he || gui_hun) && !(you_hun || liu_chong)) {
      L.push(`· 六合、归魂合绊主迟，待冲开合绊（${chong_shi}日）、或世爻逢值（${shi['zhi']}日）动身。`);
    } else if (you_hun || liu_chong) {
      L.push(`· 游魂、六冲主速，近则世爻逢值（${shi['zhi']}日）、逢冲（${chong_shi}日）即起身。`);
    } else {
      L.push(`· 以世爻为行人：逢值（${shi['zhi']}日）、逢冲（${chong_shi}日）、合住待冲开（${chong_shi}日）动身。`);
    }
    if (guan_keshi)
      L.push('· 行期又宜避官鬼当值、受克之日，候子孙（福德）值日则一路无虞。');
    L.push(_YQ_TAIL);
    L.push('（以上依《卜筮正宗·黄金策》商贾章、逃亡章及六爻出行通例推演，为软件据卦理之分析；出行仍须注意天气、交通与安全，卦理仅作参考。）');
    return L;
  }

  // ================= 官司（词讼） =================
  const _GUANSI_HUA = {
    '官鬼|子孙': '官化子孙，官符化出和解之神，事将散，吉',
    '子孙|官鬼': '子孙化官，先欲和而后兴讼，先和后争',
    '父母|官鬼': '状词化官鬼，词讼益炽，凶',
    '官鬼|父母': '官鬼化父母，官方文书相催，事难解',
    '妻财|父母': '财化父母，财不克状词，文书复立，先阻后成',
    '父母|妻财': '父母化财，状词回头被克，词讼不成立，凶于告者',
    '妻财|官鬼': '财化官鬼，以财贿生官，事反炽',
    '兄弟|官鬼': '兄弟化官，中证反被官事牵连'
  };

  function fenxi_guansi(paipan) {
    const C = _setup(paipan);
    const L = _head(paipan);
    const p = C['paipan']; const shi = C['shi']; const ying = C['ying'];
    const guans = C['byqin']['官鬼']; const fus = C['byqin']['父母']; const zis = C['byqin']['子孙'];
    const cais = C['byqin']['妻财']; const xiongs = C['byqin']['兄弟'];

    const shi_s = C['st_of'](shi); const ying_s = C['st_of'](ying);
    const shi_wang = ['旺相', '有气'].indexOf(shi_s['level']) >= 0 && !shi['is_kong'] && !shi['is_po'];
    const ying_wang = ['旺相', '有气'].indexOf(ying_s['level']) >= 0 && !ying['is_kong'] && !ying['is_po'];
    const grel = y => get_wuxing_relation(y['wuxing'], shi['wuxing']);
    const grel_y = y => get_wuxing_relation(y['wuxing'], ying['wuxing']);
    const guan_ke_ying = guans.some(y => grel_y(y) === '克' && _youli(y, C));
    const guan_ke_shi = guans.some(y => grel(y) === '克' && _youli(y, C));
    const guan_dong = guans.some(y => y['is_dong']);
    const zi_dong = zis.some(y => y['is_dong'] && _youli(y, C));
    const zi_wang = zis.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const fu_wang = fus.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const fu_kp = (!fus.length) || fus.every(y => y['is_kong'] || y['is_po']);
    const cai_dong = cais.some(y => y['is_dong'] && _youli(y, C));
    const ysheng_shi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) === '生';
    const yke_shi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) === '克';
    const shisheng_y = get_wuxing_relation(shi['wuxing'], ying['wuxing']) === '生';
    const shi_he_ying = (LIUHE[shi['zhi']] === ying['zhi']);
    const shi_chong_ying = (LIUCHONG[shi['zhi']] === ying['zhi']);
    const bihe = (shi['wuxing'] === ying['wuxing']);
    const jian = [C['yx'][2], C['yx'][3]];
    const jian_xiong = jian.some(y => y['liuqin'] === '兄弟' && y['is_dong']);
    const fu_lin_ying = ying['liuqin'] === '父母';
    const fu_lin_shi = shi['liuqin'] === '父母';

    L.push('【一、《黄金策·词讼》论官司（经典）】');
    L.push('· 总纲：「小忿不惩，必至争长竞短；大亏既负，宁不诉枉申冤？欲定输赢，须详世应」' +
      '——卦中世应，即状中原被（原告、被告），详此则两边胜负可知。');
    L.push('· 六亲取用：世爻为自己，应爻为对头（对方）；官鬼为官符、官府、罪名；父母为状词、文书；' +
      '子孙为和解之神、制官之煞（子孙动则劝和、散讼）；妻财为嘱托官府之费（财生官、财克父）；' +
      '兄弟在间爻为中证、干众。');
    const _GS_JING = [
      ['应乃对头，要休囚死绝；世为自己，宜帝旺长生', '不拘原、被，占以世为自己、应为对头；应旺世衰他强我弱，世旺应衰他弱我强。'],
      ['相冲相克，乃是欺凌之象', '世爻刑克应爻，未为我胜，乃是欺他之象；必是官鬼克应爻、或动爻月日克应，方为我胜。'],
      ['相生相合，终成合好之情', '世应生合，原被有和释之意；世生应我欲求和，应生世他欲求和；应、世动空、化空者，俱是假意言和。'],
      ['世应比合官鬼动，恐公家捉打官司', '世应比和本是和释之象，倘官鬼动克，主官府捉打官司、不欲和议；子孙亦动，终成和议。'],
      ['卦爻安静子孙兴，喜亲友劝和公事', '六爻安静、世应虽不生合，而子孙发动者，必有亲邻劝和。'],
      ['世空则我欲息争', '世空则我欲息争，应空则他欲息争，世应俱空，两怨销意。'],
      ['官逢太岁，必非州县之词', '官居第五爻若值太岁，此事必干朝廷；逢月建必涉台宪。'],
      ['内外有官，事涉一司终不了', '官不上卦，无官主张；内外有官，权不归一，主事体反复，必经两司然后了事。'],
      ['上下有父，词兴两度始能成', '官、父两爻不宜重见，主转变不定、事主缠绵，卒难了结；占告遇此，必再告之成。'],
      ['官父两强，词讼表章皆准理；妻财一动，申呈诉告总徒劳', '上表、申奏、告诉皆要官父两全、有气不空则能准理；最怕财动伤父，必不可成。'],
      ['父旺官衰，雀角鼠牙之讼', '父母旺相、官鬼休囚，情词若大，事实细微，故乃鼠牙雀角之争。'],
      ['变衰动旺，虎头蛇尾之人', '凡世应旺动，是有并吞六国之势；若变入墓绝空亡，乃先强后弱、虎头蛇尾。'],
      ['无合无生纵旺，何殊独脚虎；有刑有克逢空，当效缩头龟', '应爻旺动无生合者，彼虽刚强，只是独脚虎，不足畏；世无生合又遇日月动爻刑克，当效缩头龟，且勿与对理。'],
      ['兄在间中，事必干众', '兄弟在间爻，词内干犯众多；动则中证贪贿，克应索赔资财，克世须用财托。'],
      ['父临应上，彼欲兴词', '父母为文书，临世我欲告理，临应他欲申诉；动则欲行，静则不举。'],
      ['墓逢日德刑冲，目下即当出狱；岁挈福神生合，狱中必遇天恩', '世墓、鬼墓交动皆入狱之象，若得日辰刑冲破，目下即当出狱；在狱最喜太岁生合世爻，主有天恩赦宥。'],
      ['若问罪名，须详官鬼；要知消散，当看子孙', '罪名轻重以官鬼定，旺则罪重、衰则罪轻；散讼消灾看子孙，福动鬼静以生旺日月断。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _GS_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    if (shi_wang && ying_wang === false && !shi['is_kong'])
      L.push('· 「应乃对头要休囚死绝，世为自己宜帝旺长生」——世旺应衰，他弱我强，我占便宜。');
    if (shi_wang === false && ying_wang)
      L.push('· 「应乃对头要休囚死绝」——应旺世衰，他强我弱，我处下风。');
    if (guan_ke_ying)
      L.push('· 「相冲相克，乃是欺凌之象」——必是官鬼克应爻，方为我胜，官符偏向于我。');
    if (guan_ke_shi)
      L.push('· 官鬼克世，是官符、刑责加于我身，主我败、我受责。');
    if ((ysheng_shi || shi_he_ying || shisheng_y || bihe) && !guan_dong)
      L.push('· 「相生相合，终成合好之情」——世应生合、比和，两边有和释之意。');
    if (zi_dong)
      L.push('· 「卦爻安静子孙兴，喜亲友劝和公事」——子孙发动，制官鬼、散讼，主有劝和、事可息。');
    if (shi['is_kong'])
      L.push('· 「世空则我欲息争」——世空，我方欲息讼、不欲究。');
    if (ying['is_kong'])
      L.push('· 「应空则他欲息争」——应空，对方心虚、欲息讼、或其讼不实。');
    if (fu_lin_ying)
      L.push('· 「父临应上，彼欲兴词」——父母临应，对方欲申诉告状。');
    if (fu_kp)
      L.push('· 父母（状词）空亡、不上卦，词讼表章无气、难准。');
    if (cai_dong && fu_wang === false)
      L.push('· 「妻财一动，申呈诉告总徒劳」——财动伤父母（状词），诉讼难成。');
    if (jian_xiong)
      L.push('· 「兄在间中，事必干众」——间爻兄弟发动，中证贪贿、干犯众、要费用。');
    if (shi_chong_ying)
      L.push('· 世应相冲，两家凌竞、互不相让。');

    L.push('【二、本卦官司逐条详断】');
    L.push('（1）胜负·世应（自己与对头）');
    L.push(_yong_yao_duan(shi, C));
    L.push(_yong_yao_duan(ying, C));
    if (shi_wang && !ying_wang) L.push('　· 世旺应衰，我强他弱，理势在我。');
    else if (ying_wang && !shi_wang) L.push('　· 应旺世衰，他强我弱，我处下风。');
    if (shi_he_ying || ysheng_shi || shisheng_y)
      L.push('　· 世应相生相合，「终成合好之情」，有和解之基。');
    if (shi_chong_ying || yke_shi)
      L.push('　· 世应相冲相克，两家争斗激烈；须官鬼克应方为我胜。');
    if (bihe && !guan_dong)
      L.push('　· 世应比和，本是和释之象；官鬼不动则和，官鬼动则公家捉打官司。');

    L.push('（2）官符·官鬼爻（官府、罪名、刑责）');
    if (guans.length) {
      for (const y of guans) {
        const xx = [];
        if (y['is_shi']) xx.push('官鬼持世，官符缠身、自己亦被官司牵累');
        if (grel(y) === '克' && _youli(y, C)) xx.push('官鬼克世，刑责加身，我败');
        else if (grel_y(y) === '克' && _youli(y, C)) xx.push('官鬼克应，官符制他，为我胜');
        if (y['is_dong'])
          xx.push(_youli(y, C) ? '官鬼发动，官府捉打、讼事方兴' : '官鬼动而空破，虚张声势');
        L.push(_yong_yao_duan(y, C, xx.join('；') || '官鬼安静，官事不紧'));
      }
    } else {
      L.push('　· 官鬼不现，无官主张，讼事不成、无人受理。');
    }

    L.push('（3）状词·父母爻（词讼、表章）');
    if (fus.length) {
      for (const y of fus) {
        const xx = [];
        if (y['is_shi']) xx.push('父临世，我欲告理');
        if (y['is_ying']) xx.push('父临应，彼欲申诉');
        if (y['is_dong'] && _youli(y, C)) xx.push('父母发动，状词欲行，官父两全则准理');
        L.push(_yong_yao_duan(y, C, xx.join('；') || '父母为状词'));
      }
    } else {
      L.push('　· 父母不现，无状词、文书无气，讼难成立。');
    }

    L.push('（4）和解·子孙（制官散讼）与嘱托·妻财、中证·兄弟');
    if (zis.length) {
      for (const y of zis) {
        const ex = (y['is_dong'] && _youli(y, C))
          ? '子孙发动，制官鬼、散讼，主有劝和、大事化小'
          : '子孙安静，待发动则和';
        L.push(_yong_yao_duan(y, C, ex));
      }
    } else {
      L.push('　· 子孙不现，散讼、和解之神不现，官鬼无制，事难解。');
    }
    if (cais.length) {
      for (const y of cais) {
        if (y['is_dong']) L.push(_yong_yao_duan(y, C, '妻财动则生官、伤状词，须用财嘱托，然伤父则告诉徒劳'));
      }
    }
    if (xiongs.length) {
      for (const y of xiongs) {
        if (y['is_dong']) L.push(_yong_yao_duan(y, C, '兄弟动，中证贪贿、干众、耗财'));
      }
    }

    L.push('（5）动爻变化吉凶');
    for (const ln of _bian_duan(C, { '官鬼': '忌', '妻财': '忌', '父母': '喜', '子孙': '喜', '兄弟': '忌' }, _GUANSI_HUA))
      L.push(ln);

    L.push('（6）卦象格局');
    for (const ln of _geju_duan(C, '六合主讼事和释、绊住。',
      '六冲主讼起而散、矛盾激烈，亦主官司易结。',
      '动化六合，先争后和。',
      '动化六冲，讼终解散。'))
      L.push(ln);

    L.push('【三、综合断语（输赢）与散讼应期】');
    const zong = [];
    if (zi_dong || (shi['is_kong'] && ying['is_kong'])) {
      zong.push('子孙发动（或世应俱空），「喜亲友劝和」「两怨销意」，主官司可息、和解收场，于子孙值日、官鬼受克之日散。');
    } else if ((ysheng_shi || shi_he_ying || bihe) && !guan_ke_shi) {
      if (guan_dong && !zi_dong) {
        if (shi_he_ying && ying['is_kong']) {
          zong.push('世应本相合、应又空亡，对方心虚已有息讼之意；然官鬼发动、子孙（散讼之神）不现，讼事方兴而一时难散，主拖延。宜趁彼虚主动求和，候子孙值日、官鬼受克日方息。');
        } else {
          zong.push('世应虽生合比和，然官鬼发动、子孙不现，讼事方兴而无和解之神，一时难散、主拖延；宜求和，候子孙值日、官鬼受克日方息。');
        }
      } else {
        zong.push('世应生合比和、官鬼不克世，两家有和释之意；官鬼静、子孙一动即散讼和解。');
      }
    } else if (guan_ke_shi && !(zi_dong || guan_ke_ying)) {
      zong.push('官鬼有力克世、应爻不弱，「官符加身」，主我败、我受刑责，宜早求和解、用财托人，候子孙发动制官方解。');
    } else if (shi_wang && (guan_ke_ying || (!ying_wang && !guan_ke_shi))) {
      zong.push('世旺应衰、官鬼克应（或官不克世），理势在我，主我胜、对方受制；然「世克应只是欺他，必鬼克应方为我胜」，以官鬼不克身为准。');
    } else if (ying_wang && !shi_wang) {
      zong.push('应旺世衰，他强我弱，我处下风；若世又无生合、逢刑克，当效「缩头龟」，不宜硬争，宜求和。');
    } else {
      zong.push('世应强弱互见、胜负未定，以官鬼生克为断：官鬼克应我胜、克世我败；子孙发动则散讼和解，世应生合则和好。');
    }
    for (const z of zong) L.push('· ' + z);

    L.push('【散讼应期】');
    if (guans.length) {
      let gy = guans[0];
      for (const c of guans) {
        const kc = [c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [gy['is_dong'] ? 1 : 0, C['st_of'](gy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1])) gy = c;
      }
      L.push(`· 散讼候：子孙（福德）值日、官鬼入墓绝受克之日；本病官${gy['zhi']}，墓于${_MUKU[gy['wuxing']]}、绝于${_JUEDI[gy['wuxing']]}，至其日官事退。`);
    }
    if (zis.length) {
      let zy = zis[0];
      for (const c of zis) {
        const kc = [c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [zy['is_dong'] ? 1 : 0, C['st_of'](zy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1])) zy = c;
      }
      const chong = LIUCHONG[zy['zhi']] || '';
      L.push(`· 子孙（和解）逢值（${zy['zhi']}日）、逢冲（${chong}日），有人劝和、官司可息。`);
    }
    L.push('· 世空、应空者，出空、填实之月日见分晓；牵连牢狱，逢日辰刑冲克破世墓、鬼墓日出狱。');
    L.push(_YQ_TAIL);
    L.push('（以上依《卜筮正宗·黄金策》词讼章之法推演，为软件据卦理之分析；实际纠纷宜依法、理性处理，优先协商、寻求专业法律帮助，卦理仅作参考。）');
    return L;
  }

  // ================= 房子（家宅） =================
  const _ZHAI_SHEN = {
    '青龙': '青龙临宅，主鼎新创造、喜气、门庭吉庆',
    '白虎': '白虎临宅，主老旧破败、孝服、刑伤，交重休囚主远年建造',
    '螣蛇': '螣蛇临宅，主怪异虚惊、阴人小灾',
    '玄武': '玄武临宅，主盗贼暗昧、阴私破财',
    '朱雀': '朱雀临宅，主口舌官非、火光',
    '勾陈': '勾陈临宅，主停滞、田土坟塚之事'
  };
  const _ZHAI_GUI_SHEN = {
    '青龙': '官鬼临青龙，喜中藏忧、酒色财气之扰，灾较轻',
    '白虎': '官鬼临白虎，主孝服、刑伤、疾病、人口丧亡，最凶',
    '螣蛇': '官鬼临螣蛇，主怪异虚惊、梦寐不宁、阴邪',
    '玄武': '官鬼临玄武，主盗贼暗昧、阴私破财',
    '朱雀': '官鬼临朱雀，主口舌官非、火光、骂詈',
    '勾陈': '官鬼临勾陈，主田土争讼、阻滞、坟塚牵连'
  };

  function fenxi_fangzi(paipan) {
    const C = _setup(paipan);
    const L = _head(paipan);
    const p = C['paipan']; const shi = C['shi']; const ying = C['ying']; const gong_wx = C['gong_wx'];
    const er = C['yx'][1]; const wu = C['yx'][4];
    const guans = C['byqin']['官鬼']; const zis = C['byqin']['子孙']; const cais = C['byqin']['妻财'];
    const fus = C['byqin']['父母']; const xiongs = C['byqin']['兄弟'];

    const er_s = C['st_of'](er); const wu_s = C['st_of'](wu);
    const er_ke_wu = get_wuxing_relation(er['wuxing'], wu['wuxing']) === '克';
    const wu_ke_er = get_wuxing_relation(wu['wuxing'], er['wuxing']) === '克';
    const er_sheng_wu = get_wuxing_relation(er['wuxing'], wu['wuxing']) === '生';
    const fu_wang = fus.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const fu_kp = (!fus.length) || fus.every(y => y['is_kong'] || y['is_po']);
    const guan_dong = guans.some(y => y['is_dong'] && _youli(y, C));
    const guan_ke_shi = guans.some(y => get_wuxing_relation(y['wuxing'], shi['wuxing']) === '克' && _youli(y, C));
    const guan_lin_er = guans.some(y => y['pos'] === 2);
    const guan_zhi = guans.some(y => (y['is_dong'] && _youli(y, C)) || (y['pos'] === 2 && y['liushen'] === '白虎'));
    const zi_dong = zis.some(y => y['is_dong'] && _youli(y, C));
    const zi_wang = zis.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const cai_wang = cais.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong']);
    const cai_kp = (!cais.length) || cais.every(y => y['is_kong'] || y['is_po']);
    const xiong_dong = xiongs.some(y => y['is_dong'] && _youli(y, C));
    const tu_jin_dong = C['yx'].some(y => y['is_dong'] && (y['wuxing'] === '土' || y['wuxing'] === '金'));

    L.push('【一、《黄金策·家宅》论房子（经典）】');
    L.push('· 总纲：「创基立业，虽本人之维纬，关风敛气，每由宅以肇端。故要知人宅之兴衰，' +
      '当察卦爻之内外。内为宅，外为人，详审爻中之真假」——内卦第二爻为宅舍，外卦第五爻为人口。');
    L.push('· 六亲取用：内卦二爻为宅舍，外卦五爻为人口；父母爻为房屋、栋宇；官鬼为灾患、' +
      '官非、邪祟；妻财为家业、财源；子孙为福德、消灾之神；兄弟为耗财、同辈争竞。' +
      '内二爻克外五爻，谓宅去克人，凶；外五爻克内二爻，谓人来克宅，吉；内二爻生外五爻，' +
      '谓宅去生人，吉。');
    const _FZ_JING = [
      ['合为门，冲为路，不论卦内之有无', '合二爻为门、冲二爻为路，卦内不必明现冲合；以二爻（宅）所合、所冲之支断门、路之方位。'],
      ['龙德贵人乘旺，岳岳之侯门；官星父母长生，深深之相府', '青龙、文书（父母）、官鬼、天乙贵人临年月日建、临宅临身临命，主出官职、门第显赫。'],
      ['门庭新气象，交重得合青龙', '交重青龙不空、在日辰旬内得生旺，主鼎新创造；休囚主修旧合新。临财新修膳厨、临父新修旧堂、临兄新修门户、临子新修房舍、临官新修厅堂屋宇。'],
      ['堂宇旧规模，宅舍重侵白虎', '白虎交重、休囚空绝，主远年建造、破旧不整。'],
      ['土金发动开辟之基，父母空亡租赁之宅', '土化金、金化土为开辟之基，主新造；父母为房屋，逢空无气，又逢应爻、日辰、动爻化文书与宅相生相合，主是租赁之屋。'],
      ['门庭热闹，财官临帝旺之乡', '财、鬼、龙、德、贵人乘旺长生之位，临财生合世爻，主家庭热闹。'],
      ['家道兴隆，福禄在长生之地', '福即子孙、禄即妻财，在长生之位临身生世，主家道兴隆；二爻发动，或生或克，主改造厅堂。'],
      ['宅无破而逢生，宅兴财旺', '岁、日、月三不破宅爻，更逢动爻生宅、与财爻旺相有气，为宅兴财旺。'],
      ['有财无鬼耗散多端', '若无鬼爻，则兄弟无制，恐兄弟当权之时财爻破散，妻宫亦有驳杂。'],
      ['有鬼无财灾生不已', '鬼不宜动、财不可无；若官鬼动克世爻、克宅爻，主连生灾咎。'],
      ['有人制鬼鬼动无妨', '以本命克鬼为制，或子孙动来制鬼，鬼虽动，乃无害。'],
      ['助鬼伤身财多何益', '若妻财动而生官鬼、鬼又克身，纵然财多，助鬼伤身，亦无益。'],
      ['忌鬼爻交重临白虎，须防人眷刑伤', '忌鬼爻并白虎发动，冲克本命，主其人有灾殃、人口刑伤。'],
      ['催尸煞身命入黄泉，大忌墓门开合', '鬼动克人命为催尸煞，人命逢死绝为黄泉路，忌人命爻冲合墓爻；日辰动爻合墓爻为墓门开合，凡卦中必见鬼墓便是。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _FZ_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    if (er_sheng_wu) L.push('· 「内二爻生五爻，谓宅去生人，吉」——宅舍生人口，居之得荫，人丁兴旺。');
    if (er_ke_wu) L.push('· 「内卦二爻克五爻，谓宅去克人，凶」——宅舍克人口，居之不利人丁，宜改修。');
    if (wu_ke_er) L.push('· 「外卦五爻克二爻，谓人来克宅，吉」——人能制宅，主人能胜宅、可改造得利。');
    if (fu_kp) L.push('· 「父母空亡租赁之宅」——房屋（父母）空亡无气，多是租赁之屋、或产权无凭据。');
    if (tu_jin_dong && fu_wang) L.push('· 「土金发动开辟之基」——土金爻动，主新造、开辟，父母有气则新宅可成。');
    if (er['liushen'] === '青龙') L.push('· 「门庭新气象，交重得合青龙」——青龙临宅，主鼎新创造、吉庆。');
    if (er['liushen'] === '白虎') L.push('· 「堂宇旧规模，宅舍重侵白虎」——白虎临宅，主屋宇破旧、孝服刑伤。');
    if (guan_dong && guan_ke_shi) L.push('· 「有鬼无财灾生不已」——官鬼发动克世、克宅，宅不安、连生灾咎，须子孙制之。');
    if (guan_zhi && !zi_dong) L.push('· 「忌鬼爻交重临白虎，须防人眷刑伤」——鬼临宅、白虎，宅有灾患、人口不安。');
    if (zi_dong && guan_dong) L.push('· 「有人制鬼鬼动无妨」——子孙（福德）发动制鬼，宅中灾患可解。');
    if (cai_wang && fu_wang && !guan_ke_shi)
      L.push('· 「宅无破而逢生，宅兴财旺」「家道兴隆，福禄在长生之地」——房屋有气、财福旺，家道兴隆。');
    if (xiong_dong && !guan_dong) L.push('· 「有财无鬼耗散多端」——兄弟发动而无官鬼制之，财爻破散，主破财、争竞。');

    L.push('【二、本卦房子逐条详断】');
    L.push('（1）宅舍·二爻（内卦为宅）');
    L.push(_yong_yao_duan(er, C, '二爻为宅舍'));
    if (er_s['level'] === '旺相' || er_s['level'] === '有气') L.push('　· 宅爻旺相有气，宅舍兴旺、结构牢固。');
    else L.push('　· 宅爻休囚空破，宅舍衰败、或有破损。');
    if (er['liushen']) L.push('　· 宅爻临' + er['liushen'] + '：' + (_ZHAI_SHEN[er['liushen']] || '') + '。');

    L.push('（2）人口·五爻（外卦为人）与人宅生克');
    L.push(_yong_yao_duan(wu, C, '五爻为人口'));
    if (er_sheng_wu) L.push('　· 宅生人（二爻生五爻），居之得荫，吉。');
    else if (er_ke_wu) L.push('　· 宅克人（二爻克五爻），居之不利人丁，凶，宜改修或换宅。');
    else if (wu_ke_er) L.push('　· 人克宅（五爻克二爻），人能胜宅，吉，改造可成。');
    else L.push('　· 人宅比和，无冲克，平稳。');

    L.push('（3）房屋·父母爻（栋宇、产权、租赁）');
    if (fus.length) {
      for (const y of fus) {
        const xx = [];
        if (y['is_kong']) xx.push('父母空亡，主租赁之宅、产权无凭');
        if (y['is_dong'] && _youli(y, C)) xx.push('父母发动，主迁动、修造、换房');
        if (['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0) xx.push('父母有气，房屋牢固、有凭据');
        L.push(_yong_yao_duan(y, C, xx.join('；') || '父母为房屋'));
      }
    } else {
      L.push('　· 父母不现，房屋之象不显，或无自己房产、居无定所。');
    }

    L.push('（4）灾患·官鬼与福德·子孙（制鬼）');
    if (guans.length) {
      for (const y of guans) {
        const xx = [];
        if (y['pos'] === 2) xx.push('官鬼临宅爻，宅中不安');
        if (y['liushen']) xx.push(_ZHAI_GUI_SHEN[y['liushen']] || '官鬼临' + y['liushen'] + '，主灾患');
        if (y['is_dong'] && _youli(y, C)) xx.push('官鬼发动，灾患方兴，克世则伤人');
        L.push(_yong_yao_duan(y, C, xx.join('；') || '官鬼安静，灾患轻'));
      }
    } else {
      L.push('　· 官鬼不现，宅无灾患、邪祟，吉。');
    }
    if (zis.length) {
      for (const y of zis) {
        if (y['is_dong'])
          L.push(_yong_yao_duan(y, C, _youli(y, C) ? '子孙福德发动，制鬼消灾，宅中安吉' : '子孙动而空破，解灾力暂弱'));
      }
    } else {
      L.push('　· 子孙不现，福德不现，官鬼无制，须防灾。');
    }

    L.push('（5）家业·妻财与耗财·兄弟');
    if (cais.length) {
      for (const y of cais) L.push(_yong_yao_duan(y, C, '妻财为家业、财源'));
    } else {
      L.push('　· 妻财不现，家业财源空薄。');
    }
    if (xiongs.length) {
      for (const y of xiongs) {
        if (y['is_dong']) L.push(_yong_yao_duan(y, C, '兄弟发动，耗财、同辈争竞，无官制则财散'));
      }
    }

    L.push('（6）动爻变化与卦象格局');
    for (const ln of _bian_duan(C, { '妻财': '喜', '子孙': '喜', '父母': '喜', '官鬼': '忌', '兄弟': '忌' }))
      L.push(ln);
    for (const ln of _geju_duan(C, '六合主宅气聚、人安、宜久居。',
      '六冲主宅气散、人口不宁、居之不久，亦主迁动。',
      '动化六合，迁居后安定。',
      '动化六冲，迁居后仍散、不利久居。'))
      L.push(ln);

    L.push('【三、综合断语与宅运应期】');
    const zong = [];
    if (er_ke_wu || (guan_dong && guan_ke_shi && !zi_dong)) {
      zong.push('宅爻克人（或官鬼旺动克世、克宅而无子孙制），「宅去克人，凶」「灾生不已」，宅不安、人口不利，宜择子孙制鬼之日修造、安镇，或迁善地。');
    } else if (fu_kp && cai_wang === false) {
      zong.push('父母（房屋）空亡、妻财（家业）又不旺，「父母空亡租赁之宅」，多无自己房产、或产权无凭、宅运平常，待父母逢生旺填实方有自己基业。');
    } else if (cai_wang && fu_wang && !er_ke_wu && !guan_ke_shi) {
      zong.push('房屋（父母）有气、宅不克人、财福旺相、官鬼不肆，「宅兴财旺、家道兴隆」，是宜居、可置的吉宅，子孙临宅更吉。');
    } else if (zi_dong && guan_dong) {
      zong.push('宅虽有官鬼发动之灾，然子孙福德动而制之，「鬼动无妨」，灾患可解，修造后转吉。');
    } else {
      zong.push('宅运平中：以宅爻（二爻）、人口（五爻）生克为纲，宅生人、人克宅则吉，宅克人则凶；官鬼静、子孙财福旺则安居。');
    }
    for (const z of zong) L.push('· ' + z);

    L.push('【宅运、修造应期】');
    L.push(`· 宅爻（二爻）${er['zhi']}：逢值（${er['zhi']}日/月）、逢冲（${LIUCHONG[er['zhi']] || ''}日）应宅之动静；新造、迁居宜选宅爻、子孙、妻财生旺之日。`);
    if (guans.length) {
      let gy = guans[0];
      for (const c of guans) {
        const kc = [c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [gy['is_dong'] ? 1 : 0, C['st_of'](gy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1])) gy = c;
      }
      L.push(`· 宅中灾患候官鬼受克、子孙值日；本鬼${gy['zhi']}，墓于${_MUKU[gy['wuxing']]}、绝于${_JUEDI[gy['wuxing']]}，至其日灾退。`);
    }
    L.push(_YQ_TAIL);
    L.push('（以上依《卜筮正宗·黄金策》家宅章之法推演，为软件据卦理之分析；置业、迁居、风水调整尚须结合实际房屋、产权与现实条件，卦理仅作参考。）');
    return L;
  }

  // ================= 合同（文书·契约） =================
  function fenxi_hetong(paipan) {
    const C = _setup(paipan);
    const L = _head(paipan);
    const p = C['paipan']; const shi = C['shi']; const ying = C['ying'];
    const fus = C['byqin']['父母']; const guans = C['byqin']['官鬼']; const cais = C['byqin']['妻财'];
    const zis = C['byqin']['子孙']; const xiongs = C['byqin']['兄弟'];

    const fu_wang = fus.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const fu_kp = (!fus.length) || fus.every(y => y['is_kong'] || y['is_po']);
    const fu_dong = fus.some(y => y['is_dong']);
    const frel = y => {
      if (y['is_shi']) return '持世';
      return get_wuxing_relation(y['wuxing'], shi['wuxing']);
    };
    const fu_chishi = fus.some(y => y['is_shi']);
    const fu_shengshi = fus.some(y => frel(y) === '生');
    const fu_lin_ying = ying['liuqin'] === '父母';
    const cai_dong_li = cais.filter(y => y['is_dong'] && _youli(y, C));
    let guan_sheng_fu = false;
    const guan_ke_shi = guans.some(y => get_wuxing_relation(y['wuxing'], shi['wuxing']) === '克' && _youli(y, C));
    for (const g of guans) {
      for (const f of fus) {
        if (get_wuxing_relation(g['wuxing'], f['wuxing']) === '生' && _youli(g, C)) guan_sheng_fu = true;
      }
    }
    const ysheng_shi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) === '生';
    const yke_shi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) === '克';
    const shisheng_y = get_wuxing_relation(shi['wuxing'], ying['wuxing']) === '生';
    const shi_he_ying = LIUHE[shi['zhi']] === ying['zhi'];
    const shi_chong_ying = LIUCHONG[shi['zhi']] === ying['zhi'];
    const liu_he = LIUHE_GUA.indexOf(p['name']) >= 0;
    const liu_chong = LIUCHONG_GUA.indexOf(p['name']) >= 0;
    const bian_he = !!(p['bian_gua'] && LIUHE_GUA.indexOf(p['bian_gua']['name']) >= 0);
    const bian_chong = !!(p['bian_gua'] && LIUCHONG_GUA.indexOf(p['bian_gua']['name']) >= 0);

    L.push('【一、《黄金策》论合同文书（经典）】');
    L.push('· 说明：《黄金策》无合同专章，文书、契约、字据之理散见「求名」（文章、文书）、' +
      '「仕宦」（印绶、宣敕）、「婚姻」（庚帖、婚书）、「词讼」（状词）各章，' +
      '再以世应（双方）、六冲六合（成散）合参，其理自明。');
    L.push('· 六亲取用：父母爻为文书、契约、字据、条款，是合同之用神；世爻为自己、应爻为对方；' +
      '官鬼为官方、章印、约束（官生父则有官方背书，官克世则有违约官非）；妻财动则克父母，' +
      '主因财毁约、条款受损；子孙为和解之神。卦逢六合、世应生合，合同易成；六冲、世应冲克，' +
      '合同难成、终散。');
    const _HT_JING = [
      ['月克文书，考试逢之不第；官摇父母，交重无气空嗟', '父母为文书、凭据，最宜旺相、得日月动爻生扶；若被月建日辰克伤、或官鬼带父母动而无气，文书不济、凭据不立。'],
      ['父母空亡，休望差除宣敕', '父母为印绶、文书、诰牒、凭据；空亡则无凭无据，所主文书之事不成。占合同，父母空亡，契约难立、条款落空、或无保障。'],
      ['官父两强，词讼表章皆准理', '官鬼、父母两爻俱全、有气不空，则文书得官方之准理、有章印保障；占合同主条款成立、有官方或权威背书。'],
      ['妻财一动，申呈诉告总徒劳', '上表、申呈、告诉最怕妻财发动伤了父母文书；占合同，财动克父母，多因钱财、利益毁约、条款受阻，合同难成。'],
      ['相生相合，终成合好之情', '世应生合，双方有合好、相得之意；世生应我欲成、应生世他欲就，合作、契约由此而合。'],
      ['相冲相克，乃是欺凌之象', '世应相冲相克，双方凌竞、互不相让，合同难成；勉强成之，日后亦生争端。'],
      ['卦见六冲，往来亦徒迎迓；爻当六合，晨昏幸尔盘桓', '六冲主散，占交易、合同逢六冲，往来空忙、终难成就；六合主合，得六合卦则情分相投、内外相合，主成、主久。'],
      ['应生合者易成，逢冲克者必就', '应爻为对方，应来生合世爻，对方有诚意、合作易成；应逢冲克世爻，对方无情或相压，事难成就。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _HT_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 本卦特别贴合之经文：');
    if (fu_wang && (fu_chishi || fu_shengshi))
      L.push('· 父母（文书）旺相、持世或生合世，合同成立、条款于我有利、有凭据保障。');
    if (fu_kp)
      L.push('· 「父母空亡，休望差除宣敕」——合同文书空亡、不上卦，契约难立、条款落空、无保障。');
    if (cai_dong_li.length && !fu_wang)
      L.push('· 「妻财一动，申呈诉告总徒劳」——妻财有力发动，克伤父母文书，主因钱财毁约、合同受阻。');
    if (guan_sheng_fu && fu_wang)
      L.push('· 「官父两强，词讼表章皆准理」——官鬼生父母，文书得官方、章印背书，合同更有保障。');
    if (guan_ke_shi)
      L.push('· 官鬼克世，主约束、官非加身，防合同中有对己不利的条款、或日后违约争讼。');
    if ((ysheng_shi || shi_he_ying || liu_he) && !(yke_shi || shi_chong_ying || liu_chong)
      && !ying['is_kong'] && !fu_kp) {
      const _he = [];
      if (liu_he) _he.push('卦逢六合');
      if (ysheng_shi || shi_he_ying) _he.push('世应生合');
      L.push('· 「相生相合，终成合好之情」「爻当六合」——' + _he.join('、') + '，双方情投，合同易成且能长久。');
    }
    if (shi_he_ying && ying['is_kong'])
      L.push(`· 世${shi['zhi']}、应${ying['zhi']}本相合，然应爻空亡，是为「合空」，对方暂无实意，待应爻填实方算真合。`);
    if (yke_shi || shi_chong_ying || liu_chong)
      L.push('· 「相冲相克，乃是欺凌之象」「卦见六冲，往来亦徒迎迓」——世应冲克、卦逢六冲，合同难成、成亦终散。');
    if (ying['is_kong'] && !shi_he_ying)
      L.push('· 应爻（对方）空亡，对方无诚意、实力不实，合作落空。');
    if (fu_lin_ying)
      L.push('· 父母临应，文书、条款在对方手中，须看其旺衰生克。');

    L.push('【二、本卦合同逐条详断】');
    L.push('（1）文书·父母爻（合同、条款、凭据）');
    if (fus.length) {
      for (const y of fus) {
        const xx = [];
        if (y['is_shi']) xx.push('父母持世，凭据在我、条款由我主');
        if (y['is_ying']) xx.push('父母临应，凭据在对方');
        if (frel(y) === '生') xx.push('文书生合世爻，条款于我有利');
        if (frel(y) === '克') xx.push('文书克世，条款压我、束缚于我');
        if (y['is_kong'] || y['is_po']) xx.push('文书空破，合同不实、无保障');
        L.push(_yong_yao_duan(y, C, xx.join('；') || '父母为文书'));
      }
    } else {
      L.push('　· 父母不现，合同文书之主不上卦，无凭据、契约难立。');
      for (const ln of _fushen_duan(C, '父母')) L.push(ln);
    }

    L.push('（2）双方·世应（诚意、强弱）');
    L.push(_yong_yao_duan(shi, C, '世为自己'));
    L.push(_yong_yao_duan(ying, C, '应为对方'));
    if (shi_he_ying) {
      if (ying['is_kong']) L.push(`　· 世${shi['zhi']}、应${ying['zhi']}本相合，然应爻空亡，合而不实，待应爻填实方是真合。`);
      else L.push(`　· 世${shi['zhi']}、应${ying['zhi']}相合，双方情投，合作易成。`);
    } else if (ysheng_shi) {
      L.push('　· 应生世，对方有诚意、来就我，合作易成。');
    } else if (shisheng_y) {
      L.push('　· 世生应，我去求合、我方让步，劳心。');
    } else if (yke_shi || shi_chong_ying) {
      L.push('　· 应克世、世应相冲，对方压我、双方不让，合同难成。');
    }
    if (ying['is_kong'] && !shi_he_ying)
      L.push('　· 应空，对方不实、无诚意，合作落空。');
    if (ying['liuqin'] === '兄弟')
      L.push('　· 应临兄弟，对方为同辈、竞争者或合伙之伴，防分利、争财，账目须清。');

    L.push('（3）官方·官鬼（章印、约束）与毁约·妻财、和解·子孙');
    if (guans.length) {
      for (const y of guans) {
        const xx = [];
        if (guan_sheng_fu) xx.push('官生父母，文书有官方/章印背书');
        if (get_wuxing_relation(y['wuxing'], shi['wuxing']) === '克' && _youli(y, C))
          xx.push('官克世，防违约官非、条款压制');
        if (y['is_dong'] && !_youli(y, C)) xx.push('官动而空破，官非虚惊不实');
        L.push(_yong_yao_duan(y, C, xx.join('；') || '官鬼为约束'));
      }
    } else {
      L.push('　· 官鬼不现，无官方章印之事，亦无官非。');
    }
    if (cais.length) {
      for (const y of cai_dong_li)
        L.push(_yong_yao_duan(y, C, '妻财发动，生官、克父母文书，因财毁约、条款受损'));
    }
    if (zis.length) {
      for (const y of zis) {
        if (y['is_dong'])
          L.push(_yong_yao_duan(y, C, _youli(y, C) ? '子孙发动，制官、和解，合同有争可散' : '子孙动而空破，和解力暂弱'));
      }
    }
    if (xiongs.length) {
      for (const y of xiongs) {
        if (y['is_dong']) L.push(_yong_yao_duan(y, C, '兄弟动，同伴、第三方竞争，争财分利'));
      }
    }

    L.push('（4）动爻变化与卦象格局（成散）');
    for (const ln of _bian_duan(C, { '父母': '喜', '官鬼': '喜', '妻财': '忌', '子孙': '忌', '兄弟': '忌' }))
      L.push(ln);
    const ge = [];
    if (liu_he) ge.push('　· 六合卦：「爻当六合，晨昏幸尔盘桓」，主合同成、双方相合、能久。');
    if (liu_chong) ge.push('　· 六冲卦：「卦见六冲，往来亦徒迎迓」，主合同难成、成亦终散。');
    if (bian_he) ge.push('　· 动化六合：初有分歧，终归于合，合同后成。');
    if (bian_chong) ge.push('　· 动化六冲：初欲合而终散，先成后毁。');
    if (!ge.length) ge.push('　· 非六合、六冲，以父母（文书）旺衰、世应生合冲克为主断成散。');
    for (const ln of ge) L.push(ln);

    L.push('【三、综合断语（成否）与签约应期】');
    const zong = [];
    const cheng = fu_wang && !(yke_shi || shi_chong_ying || liu_chong) && !ying['is_kong']
      && !(cai_dong_li.length && !fu_chishi);
    if ((yke_shi || shi_chong_ying || liu_chong) && !(liu_he || ysheng_shi)) {
      zong.push('世应冲克、卦逢六冲，「相冲相克乃是欺凌」「往来亦徒迎迓」，双方不合、合同难成，勉强成之亦终散，不宜勉强。');
    } else if (fu_kp) {
      zong.push('父母（文书）空亡、不上卦，「休望差除宣敕」，合同难立、条款落空、无保障；旺者待父母填实出旬、得生扶之日再签。');
      if (shi_he_ying && ying['is_kong']) {
        zong.push(`又世${shi['zhi']}、应${ying['zhi']}虽本相合，然应爻空亡，「合空」而不实，对方暂无实意；须文书、应爻俱填实生扶之日再签。`);
      } else if (ying['is_kong']) {
        zong.push('且应爻空亡，对方暂无诚意、实力不实，合作落空。');
      }
    } else if (cai_dong_li.length && !fu_chishi) {
      zong.push('妻财有力发动克父母文书，「申呈诉告总徒劳」，多因钱财、利益分配毁约、条款受损，须先把利益、款项写清，候财爻受克、父母值日方成。');
    } else if (cheng && (ysheng_shi || shi_he_ying || liu_he || fu_chishi)) {
      zong.push('父母文书旺相、世应生合（或卦逢六合、文书持世），对方有诚意、条款有据——合同易成、于我有利、可以久守' +
        (guan_sheng_fu ? '，且官父两全，有官方章印保障。' : '。'));
    } else if (fu_wang && !ying['is_kong']) {
      zong.push('文书有气、对方不空，合同基本可成，唯世应未纯合，须再协商条款，候父母逢值、世应生合之日签。');
    } else {
      zong.push('合同成否未定：以父母文书为凭、世应生合为成、六冲财动克父为败，文书旺、世应合则签，文书空、世应冲则缓。');
    }
    for (const z of zong) L.push('· ' + z);

    L.push('【签约应期】');
    if (fus.length) {
      let fy = fus[0];
      for (const c of fus) {
        const kc = [c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [fy['is_dong'] ? 1 : 0, C['st_of'](fy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1])) fy = c;
      }
      const chong = LIUCHONG[fy['zhi']] || '';
      if (fy['is_kong'] || fy['is_po']) {
        L.push(`· 父母${fy['zhi']}空破：待出旬填实、逢值（${fy['zhi']}日）或逢冲（${chong}日）文书得力，方可签约。`);
      } else {
        L.push(`· 父母（文书）逢值（${fy['zhi']}日）、逢合（${LIUHE[fy['zhi']] || ''}日）合同成立、落定；逢冲日防变更。`);
      }
    }
    L.push('· 六冲、财动克父者，宜待冲散、财爻受克、父母逢生旺之日再签。');
    L.push(_YQ_TAIL);
    L.push('（以上依《卜筮正宗·黄金策》文书印绶之法、世应六冲六合之理推演，为软件据卦理之分析；' +
      '实际签约须审阅条款、核实对方资质、依法办理，卦理仅作参考。）');
    return L;
  }

  // ================= 朋友（兄弟·进人口） =================
  function fenxi_pengyou(paipan) {
    const C = _setup(paipan);
    const L = _head(paipan);
    const p = C['paipan']; const shi = C['shi']; const ying = C['ying'];
    const xiongs = C['byqin']['兄弟']; const guans = C['byqin']['官鬼']; const cais = C['byqin']['妻财'];
    const fus = C['byqin']['父母']; const zis = C['byqin']['子孙'];

    const xrel = y => {
      if (y['is_shi']) return '持世';
      return get_wuxing_relation(y['wuxing'], shi['wuxing']);
    };
    const xiong_wang = xiongs.some(y => ['旺相', '有气'].indexOf(C['st_of'](y)['level']) >= 0 && !y['is_kong'] && !y['is_po']);
    const xiong_kp = (!xiongs.length) || xiongs.every(y => y['is_kong'] || y['is_po']);
    const xiong_shengshi = xiongs.some(y => xrel(y) === '生');
    const xiong_keshi = xiongs.some(y => xrel(y) === '克' && _youli(y, C));
    const xiong_lin_ying = xiongs.some(y => y['is_ying']);
    const xiong_chishi = xiongs.some(y => y['is_shi']);
    const xiong_dong = xiongs.filter(y => y['is_dong'] && _youli(y, C));
    const xiong_ying_kong = xiongs.some(y => y['is_ying'] && (y['is_kong'] || y['is_po']));
    const xiong_she_xuan_dong = xiongs.some(y => y['is_dong'] && (y['liushen'] === '螣蛇' || y['liushen'] === '玄武'));
    let xiong_hua_kong = false, xiong_hua_guan = false;
    for (const y of xiongs) {
      if (y['is_dong']) {
        const by = _bian_by_pos(p, y['pos']);
        if (by) {
          const bq = get_liuqin(C['gong_wx'], by['wuxing']);
          if (bq === '官鬼') xiong_hua_guan = true;
          if (p['xunkong'].indexOf(by['zhi']) >= 0) xiong_hua_kong = true;
        }
      }
    }
    const ying_s = C['st_of'](ying);
    const ying_shengshi = get_wuxing_relation(ying['wuxing'], shi['wuxing']) === '生';
    const ying_he = LIUHE[ying['zhi']] === shi['zhi'];
    const ying_ke = get_wuxing_relation(ying['wuxing'], shi['wuxing']) === '克';
    const xiong_wx = _liuqin_wuxing(C['gong_wx'], '兄弟');
    const guan_ke_xiong = guans.some(y => get_wuxing_relation(y['wuxing'], xiong_wx) === '克' && _youli(y, C));
    const xiong_ke_cai = !!(xiong_dong.length) && !!cais.length;

    L.push('【一、《黄金策·进人口》论朋友（经典）】');
    L.push('· 说明：《黄金策》无朋友专章，「进人口」章明言「朋友以兄弟为主」——占朋友、同伴、' +
      '合伙，以兄弟爻为朋友之主；若专指某一位友人，则兼看应爻。其生合世爻、克冲身象、' +
      '动化空亡、临青龙玄武，皆是判断可信、得力与否的依据。');
    L.push('· 六亲取用：兄弟爻为朋友、同侪、伙伴（用神）；应爻为所占之具体友人；生兄弟者父母，' +
      '为长辈、文书之助；克兄弟者官鬼，主朋友有灾、是非；兄弟动则克妻财，合伙、同财时' +
      '防破财、争利；子孙为兄弟之生源（兄生子、子生财，子孙亦为调和、解纷之神）。');
    const _PY_JING = [
      ['须别来占，方知主用', '过继小儿以子孙为主，买妾婢童仆、收留迷失之人以财为主；若窝藏有难之人，看其人与我如何相识——朋友以兄弟为主，尊长以父母为主，妇人以妻财为主。'],
      ['用不宜动，动必难留', '用爻发动，其人难托；若遇游魂、或化入游魂，异日主逃散、去留不定；若来生合世爻，则不致连累。'],
      ['主不可伤，伤须夭折', '主象（所占之人）衰弱，而被日辰动爻乘旺刑伤克害，更无解救者，必然无情、不得力。'],
      ['衰入墓中，拟定萎靡不振；旺临世上，决然干蛊有成', '用爻入墓，其人性慵懒、衰弱无气空绝，主萎靡不振；若得旺相临身持世、或生合世爻，乃大吉，其人能干事、有担当。'],
      ['用爻生合世爻，必得其力；主象克冲身象，难服其心', '用爻生合世爻，其人可用，凡有相干必然用心；若克冲身象，难以使其心服、为我所用。'],
      ['动化空亡，有始无终之辈；蛇合官鬼，多谋少德之人', '用爻发动变入空亡，其人有头无尾；若临螣蛇动合官鬼，其人虽多谋，然奸诈不实、少德。'],
      ['临玄武而化兄爻，门户须防出入；遇青龙而连福德，资财可付经营', '用临玄武动化兄弟，主其人贪财好色，莫用出入；用临青龙动化子孙、生合世爻，其人至诚忠厚，托以财物则守而不失，使之经营则利归于主。'],
      ['若逢太过及空亡，反主少诚兼懒惰', '卦中用爻见有三四重、或旬空者，其人暗藏机巧、反复不实。'],
      ['受动变之伤，向后终难称意；得日月之助，他日定见如心', '月建日辰动爻克世，其为不可用，世爻衰必被其害；若得变动、日月生扶合助，方为吉、交情耐久。'],
      ['世与卦身，以和为贵', '世、身二爻相合、相生、比合为吉，相克、相冲、刑害为凶；占朋友，世与用爻（兄弟/应）生合比和则两相得。']
    ];
    L.push('· 本章核心经文（先明通例）：');
    for (const [_j, _s] of _PY_JING) L.push(`　· 「${_j}」——${_s}`);
    L.push('· 商贾章论兄弟（合伙同财参用）：');
    L.push('　· 「兄动兮频遇，劫财叠叠」——兄弟爻发动，为劫财之神、为同伴分利，合伙、同财' +
      '最忌兄弟发动克世、克财，主破财、争竞。');
    L.push('· 本卦特别贴合之经文：');
    if (xiong_wang && (xiong_shengshi || xiong_chishi || xiong_lin_ying || ying_shengshi))
      L.push('· 「用爻生合世爻，必得其力」「旺临世上，决然干蛊有成」——兄弟（朋友）旺相、生合世或临应，朋友得力、可托。');
    if (xiong_kp)
      L.push('· 「主不可伤，伤须夭折」——兄弟空亡、不上卦，朋友之缘薄、其人不得力、或朋友难聚。');
    if (xiong_keshi)
      L.push('· 「主象克冲身象，难服其心」——兄弟（朋友）克世，朋友相负、为我所累，难以为我所用。');
    if (xiong_hua_kong)
      L.push('· 「动化空亡，有始无终之辈」——兄弟动化空亡，朋友有始无终、交情不久。');
    if (xiong_hua_guan)
      L.push('· 「蛇合官鬼，多谋少德之人」——兄弟动化官鬼，朋友多谋少实、或招是非牵连。');
    if (xiongs.some(y => y['liushen'] === '玄武' && y['is_dong']))
      L.push('· 「临玄武而化兄爻，门户须防出入」——兄弟临玄武发动，防朋友贪财、欺瞒、暗中损我。');
    if (xiongs.some(y => y['liushen'] === '青龙') && xiong_wang)
      L.push('· 「遇青龙而连福德，资财可付经营」——兄弟临青龙旺相，朋友至诚忠厚，可托财、可共事。');
    if (xiong_ke_cai)
      L.push('· 「兄动兮频遇，劫财叠叠」——兄弟发动，合伙同财主破财、分利、争财，须明算账。');
    if (ying_ke)
      L.push('· 应爻（友人）克世，其人压我、相负，不宜深交、合作。');
    if (ying_shengshi || ying_he)
      L.push('· 应爻（友人）生合世爻，其人有情、于我有助。');
    if (ying['is_kong'])
      L.push('· 应爻（友人）空亡，其人不实、或所求落空。');
    if (guan_ke_xiong)
      L.push('· 官鬼克兄弟，主朋友有灾、或朋友之事牵上官非。');

    L.push('【二、本卦朋友逐条详断】');
    L.push('（1）朋友·兄弟爻（可交、得力与否）');
    if (xiongs.length) {
      for (const y of xiongs) {
        const xx = [];
        if (y['is_ying']) xx.push('兄弟临应，正是所占之友');
        if (y['is_shi']) xx.push('兄弟持世，友如手足、与我一体');
        if (xrel(y) === '生') xx.push('朋友生合世，必得其力');
        if (xrel(y) === '克' && _youli(y, C)) xx.push('朋友克世，相负、为累');
        if (y['is_dong'])
          xx.push(_youli(y, C) ? '兄弟发动，劫财、分利、多变，合伙防破财' : '兄弟动而空破，事暂不成');
        if (['青龙', '玄武', '螣蛇', '白虎'].indexOf(y['liushen']) >= 0) {
          xx.push({
            '青龙': '临青龙，忠厚喜气可交', '玄武': '临玄武，防欺瞒贪财',
            '螣蛇': '临螣蛇，多谋虚诈', '白虎': '临白虎，性刚、有刑伤'
          }[y['liushen']]);
        }
        if (xiongs.length >= 2) xx.push('兄弟多现，朋友多、或有朋党，须防太过（卦中兄多反主少诚）');
        L.push(_yong_yao_duan(y, C, xx.join('；') || '兄弟为朋友'));
      }
    } else {
      L.push('　· 卦中不见兄弟爻，朋友之主不上卦。');
      for (const ln of _fushen_duan(C, '兄弟')) L.push(ln);
    }

    L.push('（2）友人·应爻（特指其人）');
    L.push(_yong_yao_duan(ying, C, '应爻为所占之友'));
    if (ying_he && ying['is_kong'])
      L.push(`　· 世${shi['zhi']}、应${ying['zhi']}本相合，然应爻空亡，「合空」，交情暂虚、其人不实，待应填实方真。`);
    else if (ying_he)
      L.push(`　· 世${shi['zhi']}、应${ying['zhi']}相合，友人有情、与我相得，可交。`);
    else if (ying_shengshi)
      L.push('　· 应生世，友人有情、来就我，可交。');
    else if (ying_ke)
      L.push('　· 应克世，友人负我、压我，不宜深交。');
    if (ying['is_kong'] && !ying_he)
      L.push('　· 应空，友人不实、交情落空。');
    if (ying['liushen'])
      L.push('　· 应临' + ying['liushen'] + '，可参友人性情：青龙忠厚、玄武暗昧、朱雀多言、勾陈迟钝、螣蛇多谋、白虎刚急。');

    L.push('（3）朋友之灾·官鬼（克兄弟）、长辈之助·父母、合伙财利·妻财');
    if (guans.length) {
      for (const y of guans) {
        if (get_wuxing_relation(y['wuxing'], xiong_wx) === '克' && _youli(y, C))
          L.push(_yong_yao_duan(y, C, '官鬼克兄弟，朋友有灾、是非、官非牵连'));
      }
    }
    if (fus.length) {
      for (const y of fus) {
        if (get_wuxing_relation(y['wuxing'], xiong_wx) === '生') {
          if (y['is_dong']) L.push(_yong_yao_duan(y, C, '父母生兄弟，得长辈、文书之助而益友'));
        }
      }
    }
    if (cais.length && xiong_dong.length) {
      for (const y of xiong_dong)
        L.push(_yong_yao_duan(y, C, '兄弟动克妻财，合伙、同财必分利、破财，账目须清'));
    }
    if (zis.length) {
      for (const y of zis) {
        if (y['is_dong'])
          L.push(_yong_yao_duan(y, C, '子孙为兄弟之生源、解纷之神，发动主朋友调和、合伙有后生之利'));
      }
    }

    L.push('（4）动爻变化与卦象格局');
    for (const ln of _bian_duan(C, { '兄弟': '喜', '父母': '喜', '子孙': '喜', '官鬼': '忌', '妻财': '忌' }))
      L.push(ln);
    for (const ln of _geju_duan(C, '六合主朋友相聚、交情长久、合伙同心。',
      '六冲主朋友离散、合伙不终、人情冷暖。',
      '动化六合，先疏后亲、终得合好。',
      '动化六冲，先亲后疏、终至散伙。'))
      L.push(ln);

    L.push('【三、综合断语（可交、合伙）与应期】');
    const zong = [];
    if (xiong_keshi || xiong_hua_kong || xiong_ying_kong || xiong_she_xuan_dong || ying_ke) {
      const _why = [];
      if (xiong_keshi || ying_ke) _why.push('兄弟（朋友）克世、应爻克我，「难服其心」');
      if (xiong_hua_kong) _why.push('兄弟动化空亡，「有始无终之辈」');
      if (xiong_ying_kong) _why.push('所占之友（应临兄弟）空亡，「用爻空亡，反复少诚」，其人不实、交情落空');
      if (xiong_she_xuan_dong) _why.push('兄弟临螣蛇、玄武发动，「蛇合官鬼多谋少德」「门户须防出入」，防虚诈、贪财');
      zong.push(_why.join('；') + '——此人不可深交、不宜托付财物、不宜合伙，宜疏远。');
    } else if (xiong_ke_cai) {
      zong.push('兄弟旺动，朋友本身或可交，然合伙同财逢「劫财叠叠」，必分利、争财、破财，不宜共财合伙；若合作，须账目分明、立好字据（父母文书）。');
    } else if (xiong_wang && (xiong_shengshi || xiong_chishi || xiong_lin_ying || ying_shengshi)
      && !xiong_kp) {
      zong.push('兄弟（朋友）旺相、生合世或临应，「用爻生合世必得其力」「资财可付经营」，朋友可靠、得力、可共事；临青龙尤主忠厚长久。');
    } else if (xiong_kp) {
      zong.push('兄弟空亡、不上卦，朋友之缘薄、眼下不得其力，或友人难聚；待兄弟填实、逢值之年月方得良朋。');
    } else {
      zong.push('朋友之情平中：以兄弟、应爻旺衰生合为断，旺而生合世者可交，克世、空破、化空、临玄武者防之；合伙尤忌兄弟动克财。');
    }
    for (const z of zong) L.push('· ' + z);

    L.push('【交友、合伙应期】');
    if (xiongs.length) {
      let xy = xiongs[0];
      for (const c of xiongs) {
        const kc = [c['is_dong'] ? 1 : 0, C['st_of'](c)['score']];
        const kg = [xy['is_dong'] ? 1 : 0, C['st_of'](xy)['score']];
        if (kc[0] > kg[0] || (kc[0] === kg[0] && kc[1] > kg[1])) xy = c;
      }
      const chong = LIUCHONG[xy['zhi']] || '';
      L.push(`· 兄弟（朋友）逢值（${xy['zhi']}日）、逢合（${LIUHE[xy['zhi']] || ''}日）得友、见友、合伙定；逢冲（${chong}日）主朋友聚散、变动。`);
    }
    L.push('· 合伙签约同合同断，宜父母（字据）旺、世应合、兄弟静之日；兄弟当值动而克财之日，防争财。');
    L.push(_YQ_TAIL);
    L.push('（以上依《卜筮正宗·黄金策》进人口章及商贾章兄弟爻之法推演，为软件据卦理之分析；' +
      '交友、合伙重在知人和契约，卦理仅作参考。）');
    return L;
  }

  /* ===== 导出 ===== */

  const ZH = {
    LIUHE_GUA, LIUCHONG_GUA, _YQ_TAIL,
    _head, _setup, _yong_yao_duan, _fushen_duan, _geju_duan, _sanhe_duan,
    _bian_duan, _yong_yingqi, _youli,
    fenxi_gongming, fenxi_kaoshi, fenxi_hunyin, fenxi_jibing,
    fenxi_zinv, fenxi_chuxing, fenxi_guansi, fenxi_fangzi,
    fenxi_hetong, fenxi_pengyou
  };

  global.LYZH = global.LYZH || {};
  for (const k in ZH) global.LYZH[k] = ZH[k];
  if (typeof module !== 'undefined' && module.exports) module.exports = ZH;
})(typeof window !== 'undefined' ? window : globalThis);
