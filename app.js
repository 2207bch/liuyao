/* 六爻预测 H5 交互逻辑 */
(function () {
  const LY = window.LY;
  const LYZH = window.LYZH;

  const SHIQINGS = ['求财','功名','事业','工作','考试','学业','婚姻','感情',
    '疾病','子女','出行','官司','房子','合同','朋友','其他'];

  const GROUPS = {
    caiyun: ['求财','财运','生意','买卖','钱财'],
    gongming: ['功名','事业','工作','升职','升迁','官运'],
    kaoshi: ['考试','学业','文书'],
    hunyin: ['婚姻','感情','妻子','丈夫','男友'],
    jibing: ['疾病','病'],
    zinv: ['子女','孩子','儿子','女儿','生产','怀孕'],
    chuxing: ['出行','旅行','远行','出门'],
    guansi: ['官司','诉讼','词讼','官非'],
    fangzi: ['房子','房屋','住宅','家宅','房产'],
    hetong: ['合同','契约','签约'],
    pengyou: ['朋友','伙伴','合伙','同事']
  };
  const HUNYIN_ROLES = ['男占','女占'];
  const JIBING_ROLES = ['自占（自己）','代占父母','代占丈夫','代占妻子','代占子女'];
  const JIBING_MAP = { '自占（自己）':'世','代占父母':'父母','代占丈夫':'官鬼',
    '代占妻子':'妻财','代占子女':'子孙' };

  const YAO_INFO = {
    1: { sym:'━━━',     tag:'单', dong:false },
    2: { sym:'━ ━',     tag:'拆', dong:false },
    3: { sym:'━━━ ○',  tag:'重', dong:true },
    0: { sym:'━ ━ ×',  tag:'交', dong:true }
  };
  const POS_NAMES = ['初爻','二爻','三爻','四爻','五爻','上爻'];

  // ---- 状态 ----
  const now = new Date();
  let selDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  let beis = [1,1,1,1,1,1].map(() => randBei());

  function randBei(){ return Math.floor(Math.random()*4); }

  // ---- DOM ----
  const $ = id => document.getElementById(id);
  const dateVal = $('dateVal'), shiqingSel = $('shiqing'), roleSel = $('role'),
        yaoBox = $('yaoBox');

  // 事项下拉
  SHIQINGS.forEach(s => {
    const o = document.createElement('option'); o.value = s; o.textContent = s;
    shiqingSel.appendChild(o);
  });

  function groupOf(sq){
    for (const g in GROUPS) if (GROUPS[g].indexOf(sq) >= 0) return g;
    return null;
  }

  // 事项切换 → 角色下拉
  function onShiqingChange(){
    const g = groupOf(shiqingSel.value);
    roleSel.innerHTML = '';
    if (g === 'hunyin') {
      HUNYIN_ROLES.forEach(r => roleSel.add(new Option(r, r)));
      roleSel.hidden = false;
    } else if (g === 'jibing') {
      JIBING_ROLES.forEach(r => roleSel.add(new Option(r, r)));
      roleSel.hidden = false;
    } else {
      roleSel.hidden = true;
    }
  }
  shiqingSel.addEventListener('change', onShiqingChange);
  onShiqingChange();

  // ---- 日期显示 ----
  function fmtDate(d){
    return d.getFullYear() + '年' + (d.getMonth()+1) + '月' + d.getDate() + '日';
  }
  function renderDate(){ dateVal.textContent = fmtDate(selDate); }
  renderDate();

  // ---- 爻区（上爻在上，初爻在下）----
  function renderYaos(){
    yaoBox.innerHTML = '';
    for (let i = 5; i >= 0; i--) {
      const b = beis[i], info = YAO_INFO[b];
      const row = document.createElement('div');
      row.className = 'yao-row';
      row.innerHTML =
        '<div class="pos">' + POS_NAMES[i] + '</div>' +
        '<div class="sym">' + info.sym + '</div>' +
        '<div class="tag' + (info.dong ? ' dong' : '') + '">' + info.tag + '</div>';
      row.addEventListener('click', () => {
        beis[i] = [1,2,3,0][ [1,2,3,0].indexOf(beis[i]) ]; // 1→2→3→0→1
        renderYaos();
      });
      yaoBox.appendChild(row);
    }
  }
  renderYaos();

  $('shakeBtn').addEventListener('click', () => {
    beis = beis.map(() => randBei());
    renderYaos();
  });

  // ---- 排盘断卦 ----
  $('goBtn').addEventListener('click', () => {
    const y = selDate.getFullYear(), m = selDate.getMonth()+1, d = selDate.getDate();
    const [yao_list, dong] = LY.qigua_from_tongqian(beis);
    const [shang, xia] = LY.build_gua_from_yaos(yao_list);
    const gz = LY.date_to_ganzhi(y, m, d);
    const pan = LY.zhuang_gua(shang, xia, dong, gz.month_zhi, gz.ri_gan, gz.ri_zhi);
    renderGua(pan, gz);
    renderFenxi(pan);
    $('guaCard').hidden = false;
    $('fenxiCard').hidden = false;
    setTimeout(() => $('guaCard').scrollIntoView({behavior:'smooth'}), 50);
  });

  function renderGua(pan, gz){
    let nm = pan.name;
    if (pan.bian_gua) nm += '　之　' + pan.bian_gua.name;
    $('guaName').textContent = nm;
    $('guaGong').textContent = pan.gong + '宫 · ' + pan.gongwei +
      '（' + pan.gong_wuxing + '）';
    const yueWx = LY.DIZHI_WUXING[gz.month_zhi], riWx = LY.DIZHI_WUXING[gz.ri_zhi];
    $('guaRq').textContent =
      '月建 ' + gz.month_zhi + '(' + yueWx + ')　·　日辰 ' +
      gz.ri_gan + gz.ri_zhi + '(' + riWx + ')　·　旬空 ' +
      gz.xunkong[0] + gz.xunkong[1];

    const bianYaos = pan.bian_gua ? pan.bian_gua.yaos : null;
    let html = '';
    for (let i = 0; i < pan.yaos.length; i++) {
      const yao = pan.yaos[i];
      const info = YAO_INFO[yao.yinyang === 1 ? (yao.is_dong ? 3 : 1)
                                              : (yao.is_dong ? 0 : 2)];
      let sy = yao.is_shi ? '世' : (yao.is_ying ? '应' : '');
      let bd = '';
      if (yao.is_dong && bianYaos) {
        const by = bianYaos[i];
        bd = '→' + by.liuqin + by.zhi;
      }
      let kp = '';
      if (yao.is_kong) kp += '空';
      if (yao.is_po) kp += '破';
      const cls = (yao.is_dong ? 'dong ' : '') + (yao.is_kong ? 'kong' : '');
      html += '<tr class="' + cls.trim() + '">' +
        '<td class="ls">' + yao.liushen + '</td>' +
        '<td class="lq">' + yao.liuqin + '</td>' +
        '<td class="naz">' + yao.gan + yao.zhi + '<div class="kp">' + yao.wuxing + '</div></td>' +
        '<td class="yf">' + info.sym + '</td>' +
        '<td class="sy">' + sy + '</td>' +
        '<td class="bd">' + bd + (kp ? '<div class="kp">' + kp + '</div>' : '') + '</td>' +
      '</tr>';
    }
    $('guaTable').innerHTML = html;
  }

  // ---- 断语分流 ----
  function fenxiByShiqing(pan){
    const sq = shiqingSel.value, role = roleSel.value;
    const g = groupOf(sq);
    switch (g) {
      case 'caiyun':  return LY.fenxi_caiyun(pan);
      case 'gongming':return LYZH.fenxi_gongming(pan);
      case 'kaoshi':  return LYZH.fenxi_kaoshi(pan);
      case 'hunyin':  return LYZH.fenxi_hunyin(pan, role.indexOf('女') === 0 ? '女' : '男');
      case 'jibing':  return LYZH.fenxi_jibing(pan, JIBING_MAP[role] || '世');
      case 'zinv':    return LYZH.fenxi_zinv(pan);
      case 'chuxing': return LYZH.fenxi_chuxing(pan);
      case 'guansi':  return LYZH.fenxi_guansi(pan);
      case 'fangzi':  return LYZH.fenxi_fangzi(pan);
      case 'hetong':  return LYZH.fenxi_hetong(pan);
      case 'pengyou': return LYZH.fenxi_pengyou(pan);
      default:        return LY.fenxi_gua(pan);
    }
  }

  function esc(s){
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
  function renderFenxi(pan){
    const lines = fenxiByShiqing(pan);
    let html = '';
    for (const line of lines) {
      if (line.indexOf('【') === 0) {
        html += '<div class="sec">' + esc(line) + '</div>';
      } else if (line.indexOf('（') === 0 && line.length < 24 &&
                 line.indexOf('（以上') !== 0) {
        html += '<div class="sub">' + esc(line) + '</div>';
      } else {
        html += '<p>' + esc(line) + '</p>';
      }
    }
    $('fenxiBody').innerHTML = html;
    // 若处于放大态，保持；新排盘默认缩回
    setZoom(false);
  }

  // ---- 放大/缩回 ----
  const fenxiCard = $('fenxiCard'), zoomBtn = $('zoomBtn');
  let zoomed = false;
  function setZoom(z){
    zoomed = z;
    fenxiCard.classList.toggle('zoomed', z);
    zoomBtn.innerHTML = z ? '&#10006; 缩回' : '&#9974; 放大';
    if (z) window.scrollTo(0,0);
  }
  zoomBtn.addEventListener('click', () => setZoom(!zoomed));

  // ================= 自绘日历 =================
  const calMask = $('calMask'), calGrid = $('calGrid'), calTitle = $('calTitle');
  let calY = selDate.getFullYear(), calM = selDate.getMonth();
  const WD = ['一','二','三','四','五','六','日'];

  function renderCal(){
    calTitle.textContent = calY + '年' + (calM+1) + '月';
    let html = '';
    WD.forEach(w => html += '<div class="wd">' + w + '</div>');
    const first = new Date(calY, calM, 1);
    const lead = (first.getDay() + 6) % 7; // 周一起
    const days = new Date(calY, calM+1, 0).getDate();
    const prevDays = new Date(calY, calM, 0).getDate();
    const cells = [];
    for (let k = lead-1; k >= 0; k--) cells.push({y:calM===0?calY-1:calY, m:calM===0?11:calM-1, d:prevDays-k, muted:true});
    for (let d = 1; d <= days; d++) cells.push({y:calY, m:calM, d:d, muted:false});
    let nx = 1;
    while (cells.length % 7 !== 0) cells.push({y:calM===11?calY+1:calY, m:calM===11?0:calM+1, d:nx++, muted:true});
    const t = new Date();
    cells.forEach(c => {
      let cls = 'd';
      if (c.muted) cls += ' muted';
      if (c.y === t.getFullYear() && c.m === t.getMonth() && c.d === t.getDate()) cls += ' today';
      if (c.y === selDate.getFullYear() && c.m === selDate.getMonth() && c.d === selDate.getDate()) cls += ' sel';
      html += '<div class="' + cls + '" data-y="' + c.y + '" data-m="' + c.m + '" data-d="' + c.d + '">' + c.d + '</div>';
    });
    calGrid.innerHTML = html;
    calGrid.querySelectorAll('.d').forEach(el => {
      el.addEventListener('click', () => {
        selDate = new Date(+el.dataset.y, +el.dataset.m, +el.dataset.d);
        calY = selDate.getFullYear(); calM = selDate.getMonth();
        renderDate(); renderCal();
        calMask.classList.remove('show');
      });
    });
  }
  $('calBtn').addEventListener('click', () => {
    calY = selDate.getFullYear(); calM = selDate.getMonth();
    renderCal(); calMask.classList.add('show');
  });
  $('calPrev').addEventListener('click', () => {
    calM--; if (calM < 0){ calM = 11; calY--; } renderCal();
  });
  $('calNext').addEventListener('click', () => {
    calM++; if (calM > 11){ calM = 0; calY++; } renderCal();
  });
  calMask.addEventListener('click', e => {
    if (e.target === calMask) calMask.classList.remove('show');
  });

  // ================= PWA 注册 =================
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('sw.js').catch(() => {});
    });
  }
})();
