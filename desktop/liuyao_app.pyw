# -*- coding: utf-8 -*-
"""
六爻预测桌面应用
基于《卜筮正宗》《增删卜易》
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import datetime
import calendar
import os
import sys

# 导入核心算法
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from liuyao_core import (
    DIZHI, TIANGAN, DIZHI_WUXING, BAGUA, BAGONG,
    LIUSHEN, LIUQIN, YONGSHEN_MAP,
    tongqian_yao, qigua_from_tongqian, build_gua_from_yaos,
    zhuang_gua, fenxi_gua, fenxi_caiyun, paipan_to_text, num_to_cn,
    get_xunkong
)
import liuyao_zhuan  # 功名/考试/婚姻/疾病 专断模块（确保打包时被收集）

# 启用《黄金策》各类专断的事项
CAIYUN_SHIQING = ('求财', '财运', '生意', '买卖', '钱财')
GONGMING_SHIQING = ('功名', '事业', '工作', '升职', '升迁', '官运')
KAOSHI_SHIQING = ('考试', '学业', '文书')
HUNYIN_SHIQING = ('婚姻', '感情', '妻子', '丈夫', '男友')
JIBING_SHIQING = ('疾病', '病')
ZINV_SHIQING = ('子女', '孩子', '儿子', '女儿', '生产', '怀孕')
CHUXING_SHIQING = ('出行', '旅行', '远行', '出门')
GUANSI_SHIQING = ('官司', '诉讼', '词讼', '官非')
FANGZI_SHIQING = ('房子', '房屋', '住宅', '家宅', '房产')
HETONG_SHIQING = ('合同', '契约', '签约')
PENGYOU_SHIQING = ('朋友', '伙伴', '合伙', '同事')

# 婚姻：男占 / 女占；疾病：自占 / 代占六亲
HUNYIN_ROLES = ('男占', '女占')
JIBING_ROLES = ('自占（自己）', '代占父母', '代占丈夫', '代占妻子', '代占子女')
JIBING_ROLE_MAP = {'自占（自己）': '世', '代占父母': '父母', '代占丈夫': '官鬼',
                   '代占妻子': '妻财', '代占子女': '子孙'}


def fenxi_by_shiqing(paipan, shiqing, role=''):
    """按事项返回《黄金策》专断结果；不在五类专断内的事项返回 None（走通用分析）。"""
    if shiqing in CAIYUN_SHIQING:
        return fenxi_caiyun(paipan)
    if shiqing in GONGMING_SHIQING:
        from liuyao_zhuan import fenxi_gongming
        return fenxi_gongming(paipan)
    if shiqing in KAOSHI_SHIQING:
        from liuyao_zhuan import fenxi_kaoshi
        return fenxi_kaoshi(paipan)
    if shiqing in HUNYIN_SHIQING:
        from liuyao_zhuan import fenxi_hunyin
        return fenxi_hunyin(paipan, '女' if role.startswith('女') else '男')
    if shiqing in JIBING_SHIQING:
        from liuyao_zhuan import fenxi_jibing
        return fenxi_jibing(paipan, JIBING_ROLE_MAP.get(role, '世'))
    if shiqing in ZINV_SHIQING:
        from liuyao_zhuan import fenxi_zinv
        return fenxi_zinv(paipan)
    if shiqing in CHUXING_SHIQING:
        from liuyao_zhuan import fenxi_chuxing
        return fenxi_chuxing(paipan)
    if shiqing in GUANSI_SHIQING:
        from liuyao_zhuan import fenxi_guansi
        return fenxi_guansi(paipan)
    if shiqing in FANGZI_SHIQING:
        from liuyao_zhuan import fenxi_fangzi
        return fenxi_fangzi(paipan)
    if shiqing in HETONG_SHIQING:
        from liuyao_zhuan import fenxi_hetong
        return fenxi_hetong(paipan)
    if shiqing in PENGYOU_SHIQING:
        from liuyao_zhuan import fenxi_pengyou
        return fenxi_pengyou(paipan)
    return None


class LiuYaoApp:
    def __init__(self, root):
        self.root = root
        self.root.title('六爻预测 · 卜筮正宗')
        self.root.geometry('1100x780')
        self.root.minsize(960, 700)

        # 配色（中式风格）
        self.bg_color = '#f5f0e6'       # 米黄底色
        self.panel_color = '#faf6ee'    # 面板色
        self.title_color = '#8b2500'    # 深红棕标题
        self.text_color = '#2c1810'     # 深棕文字
        self.accent_color = '#a0522d'   # 赭石色
        self.dong_color = '#c0392b'     # 动爻红色
        self.kong_color = '#7f8c8d'     # 空亡灰色
        self.line_yang = '#1a1a1a'
        self.gui_bg = '#e8dcc8'

        self.root.configure(bg=self.bg_color)

        # 六次摇卦结果（背数 0~3），初始None
        self.yao_results = [None] * 6
        # 当前排盘结果（注意：不能与 paipan() 方法同名）
        self.paipan_result = None

        self._build_ui()

    def _build_ui(self):
        # ===== 顶部标题 =====
        title_frame = tk.Frame(self.root, bg=self.title_color, height=56)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text='六 爻 预 测',
                 font=('微软雅黑', 20, 'bold'),
                 fg='#ffd700', bg=self.title_color).pack(side='left', padx=24)
        tk.Label(title_frame, text='卜筮正宗 · 增删卜易',
                 font=('微软雅黑', 11), fg='#f0d9a8', bg=self.title_color).pack(side='left', padx=10)

        # ===== 主体区域：左右分栏 =====
        main = tk.Frame(self.root, bg=self.bg_color)
        main.pack(fill='both', expand=True, padx=12, pady=10)

        # ---------- 左侧控制面板 ----------
        left = tk.Frame(main, bg=self.panel_color, bd=1, relief='solid')
        left.pack(side='left', fill='y', padx=(0, 8))
        left.config(width=340)
        left.pack_propagate(False)
        self.left_frame = left

        # ===== 起卦日期（默认今日，可点日历改期，干支自动推算）=====
        tk.Label(left, text='起卦日期', font=('微软雅黑', 13, 'bold'),
                 fg=self.title_color, bg=self.panel_color).pack(anchor='w', padx=16, pady=(14, 6))

        date_frame = tk.Frame(left, bg=self.panel_color)
        date_frame.pack(fill='x', padx=16)

        # 内部数据载体（排盘逻辑使用）：月建地支、日干、日支
        self.yue_var = tk.StringVar()
        self.ri_gan_var = tk.StringVar()
        self.ri_zhi_var = tk.StringVar()
        self.current_date = datetime.date.today()
        self._gz_cache = None

        self.date_label = tk.Label(date_frame, text='', font=('微软雅黑', 11, 'bold'),
                                   bg='#fffdf7', fg=self.text_color,
                                   bd=1, relief='solid', padx=10, pady=7, anchor='w')
        self.date_label.pack(side='left', fill='x', expand=True)
        tk.Button(date_frame, text='\U0001F4C5', font=('Segoe UI Emoji', 12), width=3,
                  bg=self.title_color, fg='white', activebackground='#a52a2a',
                  activeforeground='white', relief='flat', cursor='hand2',
                  command=self._pick_date).pack(side='left', padx=(6, 0), ipady=2)

        # 推算出的干支信息
        self.ganzhi_label = tk.Label(left, text='', font=('微软雅黑', 10, 'bold'),
                                     bg=self.panel_color, fg=self.text_color, justify='left')
        self.ganzhi_label.pack(anchor='w', padx=16, pady=(8, 0))
        self.xunkong_label = tk.Label(left, text='', font=('微软雅黑', 9),
                                      bg=self.panel_color, fg=self.accent_color, justify='left')
        self.xunkong_label.pack(anchor='w', padx=16, pady=(2, 0))

        # 默认应用今日
        self._apply_date(self.current_date)

        # 占问事项
        tk.Label(left, text='占问事项', font=('微软雅黑', 13, 'bold'),
                 fg=self.title_color, bg=self.panel_color).pack(anchor='w', padx=16, pady=(14, 6))
        self.shiqing_var = tk.StringVar(value='求财')
        shiqing_entry = ttk.Combobox(left, textvariable=self.shiqing_var,
                                     values=['求财', '功名', '事业', '工作', '考试', '学业',
                                             '婚姻', '感情', '疾病', '子女', '出行', '官司',
                                             '房子', '合同', '朋友', '其他'],
                                     font=('微软雅黑', 10))
        shiqing_entry.pack(fill='x', padx=16)
        shiqing_entry.bind('<<ComboboxSelected>>', self._on_shiqing_change)

        # 占者身份：婚姻选男占/女占，疾病选自占/代占；随事项显示（空时不占高度）
        self.role_frame = tk.Frame(left, bg=self.panel_color)
        self.role_frame.pack(fill='x', padx=16, pady=(2, 0))
        self.role_label = tk.Label(self.role_frame, text='占者身份', font=('微软雅黑', 10),
                                   fg=self.text_color, bg=self.panel_color)
        self.role_var = tk.StringVar(value='男占')
        self.role_combo = ttk.Combobox(self.role_frame, textvariable=self.role_var,
                                       values=list(HUNYIN_ROLES), font=('微软雅黑', 10),
                                       state='readonly')

        # 摇卦区
        tk.Label(left, text='摇卦（铜钱三枚，共六次）', font=('微软雅黑', 13, 'bold'),
                 fg=self.title_color, bg=self.panel_color).pack(anchor='w', padx=16, pady=(16, 6))

        # 一键摇卦按钮
        btn_frame = tk.Frame(left, bg=self.panel_color)
        btn_frame.pack(fill='x', padx=16, pady=(0, 8))
        tk.Button(btn_frame, text='🎲 一键摇卦', font=('微软雅黑', 11, 'bold'),
                  bg=self.title_color, fg='white', activebackground='#a52a2a',
                  activeforeground='white', relief='flat', cursor='hand2',
                  command=self.auto_yaogua, height=1).pack(side='left', fill='x', expand=True, padx=(0, 6))
        tk.Button(btn_frame, text='重置', font=('微软雅黑', 10),
                  bg='#999', fg='white', activebackground='#777',
                  relief='flat', cursor='hand2',
                  command=self.reset_gua).pack(side='left')

        # 六爻选择（从上爻到初爻显示）
        self.yao_buttons = []  # 每爻的4个按钮
        yao_names = ['上爻', '五爻', '四爻', '三爻', '二爻', '初爻']
        yao_types = ['单(阳)', '拆(阴)', '重(阳动)', '交(阴动)']
        yao_beis = [1, 2, 3, 0]  # 对应的背数

        yao_box = tk.Frame(left, bg=self.panel_color)
        yao_box.pack(fill='x', padx=12)

        for row_i, name in enumerate(yao_names):
            yao_idx = 5 - row_i  # 显示顺序：上爻=索引5 ... 初爻=索引0
            row = tk.Frame(yao_box, bg=self.panel_color)
            row.pack(fill='x', pady=2)
            tk.Label(row, text=name, font=('微软雅黑', 9), width=4,
                     bg=self.panel_color, fg=self.text_color).pack(side='left', padx=(4, 2))

            btns = []
            for btn_i, (label, bei) in enumerate(zip(yao_types, yao_beis)):
                b = tk.Button(row, text=label, font=('微软雅黑', 8),
                              width=7, relief='raised', bd=1,
                              bg='#eee', activebackground='#ddd',
                              command=lambda yi=yao_idx, b=bei: self.manual_set_yao(yi, b))
                b.pack(side='left', padx=1)
                btns.append(b)
            self.yao_buttons.append((yao_idx, btns))

        # 排盘按钮
        tk.Button(left, text='排 盘 断 卦', font=('微软雅黑', 14, 'bold'),
                  bg='#1f6e43', fg='white', activebackground='#155a35',
                  relief='flat', cursor='hand2', height=2,
                  command=self.paipan).pack(fill='x', padx=16, pady=(14, 10))

        # 保存卦例按钮
        tk.Button(left, text='保存卦例到文件', font=('微软雅黑', 10),
                  bg=self.accent_color, fg='white', activebackground='#8b4513',
                  relief='flat', cursor='hand2',
                  command=self.save_guali).pack(fill='x', padx=16, pady=(0, 10))

        # ---------- 右侧显示区 ----------
        right = tk.Frame(main, bg=self.bg_color)
        right.pack(side='left', fill='both', expand=True)
        self.right_frame = right

        # 卦盘显示
        pan_frame = tk.LabelFrame(right, text=' 卦 盘 ',
                                  font=('微软雅黑', 12, 'bold'),
                                  fg=self.title_color, bg=self.panel_color,
                                  bd=1, relief='solid')
        pan_frame.pack(fill='x', pady=(0, 8))
        self.pan_frame = pan_frame

        self.pan_canvas = tk.Canvas(pan_frame, bg=self.panel_color,
                                    height=340, highlightthickness=0)
        self.pan_canvas.pack(fill='x', padx=8, pady=8)

        # 断卦分析
        fenxi_frame = tk.LabelFrame(right, text=' 断 卦 分 析 ',
                                    font=('微软雅黑', 12, 'bold'),
                                    fg=self.title_color, bg=self.panel_color,
                                    bd=1, relief='solid')
        fenxi_frame.pack(fill='both', expand=True)
        self.fenxi_frame = fenxi_frame

        # 放大工具行（点击放大占满窗口，再点击还原）
        zoom_bar = tk.Frame(fenxi_frame, bg=self.panel_color)
        zoom_bar.pack(fill='x', padx=8, pady=(6, 0))
        self.fenxi_zoomed = False
        self.zoom_btn = tk.Button(zoom_bar, text='⛶ 放大', font=('微软雅黑', 9),
                                  bg=self.panel_color, fg=self.title_color,
                                  activebackground='#eee', relief='flat', cursor='hand2',
                                  command=self._toggle_fenxi_zoom)
        self.zoom_btn.pack(side='right')

        # 文本框+滚动条
        text_wrap = tk.Frame(fenxi_frame, bg=self.panel_color)
        text_wrap.pack(fill='both', expand=True, padx=8, pady=8)
        scroll = ttk.Scrollbar(text_wrap)
        scroll.pack(side='right', fill='y')
        self.fenxi_text = tk.Text(text_wrap, font=('微软雅黑', 10),
                                  bg='#fffdf7', fg=self.text_color,
                                  wrap='word', relief='flat',
                                  yscrollcommand=scroll.set,
                                  spacing1=2, spacing2=4, padx=8, pady=6)
        self.fenxi_text.pack(side='left', fill='both', expand=True)
        scroll.config(command=self.fenxi_text.yview)

        # 初始提示
        self._show_welcome()

    def _show_welcome(self):
        self.fenxi_text.insert('end', '欢迎使用六爻预测\n\n', 'title')
        self.fenxi_text.tag_config('title', font=('微软雅黑', 14, 'bold'),
                                   foreground=self.title_color, justify='center')
        self.fenxi_text.insert('end', '使用方法：\n\n')
        self.fenxi_text.insert('end', '1. 选择月建、日辰干支\n')
        self.fenxi_text.insert('end', '2. 选择占问事项（自动取用神）\n')
        self.fenxi_text.insert('end', '3. 点击「一键摇卦」随机起卦，或手动点选每爻\n')
        self.fenxi_text.insert('end', '   · 单：一背二字，少阳（静阳爻）━━━\n')
        self.fenxi_text.insert('end', '   · 拆：二背一字，少阴（静阴爻）━ ━\n')
        self.fenxi_text.insert('end', '   · 重：三背，老阳（阳动变阴）━━━ ○\n')
        self.fenxi_text.insert('end', '   · 交：三字，老阴（阴动变阳）━ ━ ×\n')
        self.fenxi_text.insert('end', '4. 点击「排盘断卦」查看卦盘与分析\n\n')
        self.fenxi_text.insert('end', '理论依据：《卜筮正宗》《增删卜易》\n', 'note')
        self.fenxi_text.tag_config('note', foreground='#888', font=('微软雅黑', 9))
        self.fenxi_text.config(state='disabled')

        # 画空卦盘提示
        self.pan_canvas.delete('all')
        self.pan_canvas.create_text(300, 170, text='请摇卦后排盘',
                                    font=('微软雅黑', 14), fill='#aaa')

    def _apply_date(self, date):
        """根据公历日期自动推算并设置月建、日干支、旬空"""
        from liuyao_core import date_to_ganzhi
        self.current_date = date
        gz = date_to_ganzhi(date.year, date.month, date.day)
        self._gz_cache = gz
        self.yue_var.set(gz['month_zhi'])
        self.ri_gan_var.set(gz['ri_gan'])
        self.ri_zhi_var.set(gz['ri_zhi'])

        week_cn = ['一', '二', '三', '四', '五', '六', '日'][date.weekday()]
        self.date_label.config(text=f' {date.year}年{date.month}月{date.day}日  周{week_cn}')
        self.ganzhi_label.config(
            text=f"{gz['year_gan']}{gz['year_zhi']}年  "
                 f"{gz['month_gan']}{gz['month_zhi']}月  "
                 f"{gz['ri_gan']}{gz['ri_zhi']}日")
        xk = ''.join(gz['xunkong'])
        self.xunkong_label.config(
            text=f"月建 {gz['month_zhi']}（{DIZHI_WUXING[gz['month_zhi']]}）　"
                 f"日辰 {gz['ri_gan']}{gz['ri_zhi']}（{DIZHI_WUXING[gz['ri_zhi']]}）　旬空 {xk}")

    def _pick_date(self):
        """打开日历选择弹窗"""
        DatePicker(self.root, self.current_date, self._apply_date,
                   title_color=self.title_color, panel_color=self.panel_color,
                   text_color=self.text_color, accent_color=self.accent_color)

    def _on_shiqing_change(self, event=None):
        """事项变化时，婚姻/疾病显示身份选择，其余隐藏。"""
        sq = self.shiqing_var.get()
        if sq in HUNYIN_SHIQING:
            self.role_combo['values'] = list(HUNYIN_ROLES)
            if self.role_var.get() not in HUNYIN_ROLES:
                self.role_var.set(HUNYIN_ROLES[0])
            self.role_label.pack(anchor='w', padx=2, pady=(6, 2))
            self.role_combo.pack(fill='x')
        elif sq in JIBING_SHIQING:
            self.role_combo['values'] = list(JIBING_ROLES)
            if self.role_var.get() not in JIBING_ROLES:
                self.role_var.set(JIBING_ROLES[0])
            self.role_label.pack(anchor='w', padx=2, pady=(6, 2))
            self.role_combo.pack(fill='x')
        else:
            self.role_label.pack_forget()
            self.role_combo.pack_forget()

    def _apply_fenxi_font(self, base):
        """按基础字号统一设置断语正文及各标签字体。"""
        self.fenxi_text.configure(font=('微软雅黑', base))
        self.fenxi_text.tag_configure('title', font=('微软雅黑', base + 4, 'bold'))
        self.fenxi_text.tag_configure('section', font=('微软雅黑', base + 1, 'bold'))
        self.fenxi_text.tag_configure('subsection', font=('微软雅黑', base, 'bold'))
        self.fenxi_text.tag_configure('normal', font=('微软雅黑', base))
        self.fenxi_text.tag_configure('note', font=('微软雅黑', base - 1))

    def _toggle_fenxi_zoom(self):
        """点击放大断语区（隐藏左侧与卦盘、字号调大）；再点击还原。"""
        self.fenxi_zoomed = not self.fenxi_zoomed
        z = self.fenxi_zoomed
        if z:
            self.left_frame.pack_forget()
            self.pan_frame.pack_forget()
        else:
            self.left_frame.pack(side='left', fill='y', padx=(0, 8),
                                 before=self.right_frame)
            self.pan_frame.pack(fill='x', pady=(0, 8),
                                before=self.fenxi_frame)
        self._apply_fenxi_font(13 if z else 10)
        self.zoom_btn.config(text='⛗ 还原' if z else '⛶ 放大')

    def auto_yaogua(self):
        """随机摇六次卦"""
        self.yao_results = [random.randint(0, 3) for _ in range(6)]
        self._refresh_yao_display()

    def manual_set_yao(self, yao_idx, bei):
        """手动设置某爻"""
        self.yao_results[yao_idx] = bei
        self._refresh_yao_display()

    def _refresh_yao_display(self):
        """刷新爻按钮的选中状态"""
        for yao_idx, btns in self.yao_buttons:
            result = self.yao_results[yao_idx]
            bei_list = [1, 2, 3, 0]
            for btn_i, btn in enumerate(btns):
                if result == bei_list[btn_i]:
                    btn.config(bg='#1f6e43', fg='white', relief='sunken')
                else:
                    btn.config(bg='#eee', fg='black', relief='raised')

    def reset_gua(self):
        self.yao_results = [None] * 6
        self.paipan_result = None
        for yao_idx, btns in self.yao_buttons:
            for btn in btns:
                btn.config(bg='#eee', fg='black', relief='raised')
        self.pan_canvas.delete('all')
        self.pan_canvas.create_text(300, 170, text='请摇卦后排盘',
                                    font=('微软雅黑', 14), fill='#aaa')
        self.fenxi_text.config(state='normal')
        self.fenxi_text.delete('1.0', 'end')
        self._show_welcome()

    def paipan(self):
        """排盘断卦主逻辑"""
        # 检查六爻是否齐全
        if any(r is None for r in self.yao_results):
            messagebox.showwarning('提示', '请先完成六次摇卦（六爻都要选择）')
            return

        # 日干支由所选日期推算（恒为合法干支），此处做兜底校验
        ri_gan = self.ri_gan_var.get()
        ri_zhi = self.ri_zhi_var.get()
        if not get_xunkong(ri_gan, ri_zhi):
            messagebox.showwarning('提示', '起卦日期或干支异常，请重新点日历选择日期。')
            return

        yao_list, dong = qigua_from_tongqian(self.yao_results)
        shang, xia = build_gua_from_yaos(yao_list)

        yue = self.yue_var.get()

        self.paipan_result = zhuang_gua(shang, xia, dong_yao=dong,
                                 yue_zhi=yue, ri_gan=ri_gan, ri_zhi=ri_zhi)

        # 绘制卦盘
        self._draw_paipan()

        # 断卦分析
        shiqing = self.shiqing_var.get()
        yongshen = YONGSHEN_MAP.get(shiqing, None)
        if shiqing == '其他':
            yongshen = None

        self.fenxi_text.config(state='normal')
        self.fenxi_text.delete('1.0', 'end')

        # 求财类事项：启用《黄金策·商贾》求财专断（含经典、详断、综合应期）；
        # 其余事项沿用通用分析。
        zhuan_result = fenxi_by_shiqing(self.paipan_result, shiqing, self.role_var.get())
        is_zhuan = zhuan_result is not None
        if is_zhuan:
            result = zhuan_result
        else:
            result = fenxi_gua(self.paipan_result, yongshen_type=yongshen)

        # 配置标签样式
        self.fenxi_text.tag_config('section', font=('微软雅黑', 11, 'bold'),
                                   foreground=self.title_color, spacing1=10, spacing3=2)
        self.fenxi_text.tag_config('subsection', font=('微软雅黑', 10, 'bold'),
                                   foreground=self.accent_color, spacing1=6, lmargin1=8, lmargin2=8)
        self.fenxi_text.tag_config('normal', font=('微软雅黑', 10),
                                   foreground=self.text_color, lmargin1=12, lmargin2=12)
        # 若当前处于放大状态，重排后仍保持大字号
        if getattr(self, 'fenxi_zoomed', False):
            self._apply_fenxi_font(13)

        for line in result:
            if line.startswith('【'):
                self.fenxi_text.insert('end', line + '\n', 'section')
            elif line.startswith('（') and len(line) < 24 and not line.startswith('（以上'):
                self.fenxi_text.insert('end', line + '\n', 'subsection')
            else:
                self.fenxi_text.insert('end', line + '\n', 'normal')

        # 非专断事项附加通用综合断语（五类专断已含综合断语与应期）
        if not is_zhuan:
            zonghe = self._zonghe_duanyu(yongshen)
            if zonghe:
                self.fenxi_text.insert('end', '\n【综合断语】\n', 'section')
                for z in zonghe:
                    self.fenxi_text.insert('end', z + '\n', 'normal')

        self.fenxi_text.config(state='disabled')

    def _zonghe_duanyu(self, yongshen):
        """生成综合断语"""
        if not self.paipan_result:
            return []
        duanyu = []
        p = self.paipan_result
        yaos_sx = list(reversed(p['yaos']))  # 初到上
        shi = next(y for y in yaos_sx if y['is_shi'])

        # 六冲卦判断（八纯卦、天雷无妄、雷天大壮）
        liuchong_gua = ['乾为天', '兑为泽', '离为火', '震为雷',
                        '巽为风', '坎为水', '艮为山', '坤为地',
                        '天雷无妄', '雷天大壮']
        if p['name'] in liuchong_gua:
            duanyu.append('· 本卦为六冲卦，主事多反复、不久、不顺，近病易愈、久病难医，谋事难成。')

        # 六合卦判断
        liuhe_gua = ['天地否', '地天泰', '水泽节', '山水蒙',
                     '风雷益', '雷地豫', '地山谦', '泽水困']
        if p['name'] in liuhe_gua:
            duanyu.append('· 本卦为六合卦，主事多和顺、谋事易成、婚姻美满。')

        # 世爻状态
        if shi['is_kong']:
            duanyu.append('· 世爻旬空，主事主心中无底、事难落实，旺空则出空有用，衰空则大凶。')
        if shi['is_po']:
            duanyu.append('· 世爻月破，主事多破败、难成，需逢合逢值之日月方有转机。')

        # 用神旺衰
        if yongshen:
            ys_yaos = [y for y in yaos_sx if y['liuqin'] == yongshen]
            if ys_yaos:
                y = ys_yaos[0]
                wx = y['wuxing']
                yue_wx = DIZHI_WUXING[p['yue_zhi']] if p['yue_zhi'] else None
                ri_wx = DIZHI_WUXING[p['ri_zhi']] if p['ri_zhi'] else None

                def wx_rel(a, b):
                    from liuyao_core import WUXING_SHENG, WUXING_KE
                    if a == b: return 'wang'
                    if WUXING_SHENG.get(a) == b: return 'xie'
                    if WUXING_SHENG.get(b) == a: return 'xiang'
                    if WUXING_KE.get(b) == a: return 'si'
                    if WUXING_KE.get(a) == b: return 'qiu'
                    return 'ping'

                yue_stat = wx_rel(yue_wx, wx) if yue_wx else 'ping'
                ri_stat = wx_rel(ri_wx, wx) if ri_wx else 'ping'

                if yue_stat in ('wang', 'xiang') and ri_stat in ('wang', 'xiang'):
                    duanyu.append(f'· 用神{yongshen}{y["zhi"]}{wx}旺相，得日月生扶，事必易成，吉。')
                elif y['is_kong'] or y['is_po']:
                    duanyu.append(f'· 用神{yongshen}{y["zhi"]}{wx}空破，事多阻滞，难遂人意。')
                elif yue_stat in ('si', 'qiu') and ri_stat in ('si', 'qiu'):
                    duanyu.append(f'· 用神{yongshen}{y["zhi"]}{wx}休囚受克，事难成就，凶。')

            # 用神动变
            dong_yong = [y for y in ys_yaos if y['is_dong']]
            if dong_yong and p['bian_gua']:
                b_yaos = list(reversed(p['bian_gua']['yaos']))
                for dy in dong_yong:
                    by = next((b for b in b_yaos if b['pos'] == dy['pos']), None)
                    if by:
                        from liuyao_core import WUXING_SHENG, WUXING_KE
                        if WUXING_SHENG.get(by['wuxing']) == dy['wuxing']:
                            duanyu.append(f'· 用神{yongshen}动化回头生，吉上加吉。')
                        elif WUXING_KE.get(by['wuxing']) == dy['wuxing']:
                            duanyu.append(f'· 用神{yongshen}动化回头克，先吉后凶，事终不利。')

        if not duanyu:
            duanyu.append('· 卦象平稳，需结合具体事项与日月生克细断。')

        duanyu.append('\n（以上为软件基础分析，仅供参考；实际断卦需结合卦象、事理综合判断）')
        return duanyu

    def _draw_paipan(self):
        """在Canvas上绘制卦盘"""
        if not self.paipan_result:
            return
        c = self.pan_canvas
        c.delete('all')
        p = self.paipan_result

        # 宽度自适应
        c.update_idletasks()
        W = c.winfo_width() or 720
        if W < 100:
            W = 720

        # 两列：本卦、变卦
        has_bian = p['bian_gua'] is not None
        col_w = W // 2 if has_bian else W

        # 标题
        c.create_rectangle(0, 0, W, 34, fill=self.title_color, outline='')
        title = f"【本卦】{p['name']}（{p['gong']}宫{p['gongwei']}）"
        c.create_text(col_w // 2, 17, text=title,
                      font=('微软雅黑', 12, 'bold'), fill='#ffd700')
        if has_bian:
            b = p['bian_gua']
            c.create_text(col_w + col_w // 2, 17,
                          text=f"【变卦】{b['name']}（{b['gong']}宫{b['gongwei']}）",
                          font=('微软雅黑', 12, 'bold'), fill='#ffd700')

        # 日月信息行
        rq_y = 52
        xk_str = (p['xunkong'][0] + p['xunkong'][1]) if len(p['xunkong']) == 2 else '干支无效'
        rq = f"月建 {p['yue_zhi']}{DIZHI_WUXING[p['yue_zhi']]}    日辰 {p['ri_gan']}{p['ri_zhi']}{DIZHI_WUXING[p['ri_zhi']]}    旬空 {xk_str}"
        c.create_text(W // 2, rq_y, text=rq, font=('微软雅黑', 10), fill=self.accent_color)

        # 六爻表格
        row_h = 42
        start_y = 72
        # 列定义：六神 | 六亲 | 纳甲 | 爻画 | 世应 | （变卦）六亲纳甲
        col_x_ben = [10, 70, 130, 210, 300]  # 本卦各列起始x
        if has_bian:
            col_x_ben = [10, 60, 115, 185, 260]
            col_x_bian = [col_w + 10, col_w + 70, col_w + 130, col_w + 210]

        # 表头
        head_y = start_y - 8
        headers = ['六神', '六亲', '纳甲', '爻象', '世应']
        for hx, ht in zip(col_x_ben, headers):
            c.create_text(hx + 25, head_y, text=ht,
                          font=('微软雅黑', 9, 'bold'), fill=self.accent_color)
        if has_bian:
            for hx, ht in zip(col_x_bian[:4], ['', '六亲', '纳甲', '变爻']):
                if ht:
                    c.create_text(hx + 25, head_y, text=ht,
                                  font=('微软雅黑', 9, 'bold'), fill=self.accent_color)

        # 六爻（上爻到初爻）
        bian_yaos = p['bian_gua']['yaos'] if has_bian else None

        for i, y in enumerate(p['yaos']):
            ry = start_y + i * row_h

            # 交替背景
            if i % 2 == 0:
                c.create_rectangle(4, ry - 14, col_w - 4, ry + 14,
                                   fill='#f0e8d8', outline='')
                if has_bian:
                    c.create_rectangle(col_w + 4, ry - 14, W - 4, ry + 14,
                                       fill='#f0e8d8', outline='')

            # 动爻高亮
            if y['is_dong']:
                c.create_rectangle(4, ry - 14, col_w - 4, ry + 14,
                                   fill='#fce4e0', outline='')

            # 六神
            ls_color = {'青龙': '#1f6e43', '朱雀': '#c0392b', '勾陈': '#8b6914',
                        '腾蛇': '#6c3483', '白虎': '#566573', '玄武': '#1a5276'}
            c.create_text(col_x_ben[0] + 25, ry, text=y['liushen'],
                          font=('微软雅黑', 10), fill=ls_color.get(y['liushen'], 'black'))

            # 六亲
            c.create_text(col_x_ben[1] + 25, ry, text=y['liuqin'],
                          font=('微软雅黑', 10, 'bold'), fill=self.text_color)

            # 纳甲
            nazhi = f"{y['gan']}{y['zhi']}{y['wuxing']}"
            c.create_text(col_x_ben[2] + 30, ry, text=nazhi,
                          font=('微软雅黑', 10), fill=self.text_color)

            # 爻画
            self._draw_yao_symbol(c, col_x_ben[3] + 30, ry, y)

            # 世应
            sy = '世' if y['is_shi'] else ('应' if y['is_ying'] else '')
            sy_color = self.title_color if sy == '世' else self.accent_color
            c.create_text(col_x_ben[4] + 15, ry, text=sy,
                          font=('微软雅黑', 11, 'bold'), fill=sy_color)

            # 空破标记
            kp = ''
            if y['is_kong']:
                kp += '空'
            if y['is_po']:
                kp += '破'
            if kp:
                c.create_text(col_x_ben[4] + 38, ry, text=kp,
                              font=('微软雅黑', 9), fill=self.kong_color)

            # 变卦列
            if has_bian and bian_yaos:
                by = bian_yaos[i]
                # 只在动爻位置显示变卦内容
                if y['is_dong']:
                    c.create_text(col_x_bian[1] + 25, ry, text=by['liuqin'],
                                  font=('微软雅黑', 10, 'bold'), fill=self.dong_color)
                    c.create_text(col_x_bian[2] + 30, ry,
                                  text=f"{by['zhi']}{by['wuxing']}",
                                  font=('微软雅黑', 10), fill=self.dong_color)
                    self._draw_yao_symbol(c, col_x_bian[3] + 30, ry, by,
                                          color=self.dong_color)
                else:
                    c.create_text(col_x_bian[1] + 25, ry, text='', font=('微软雅黑', 10))
                    self._draw_yao_symbol(c, col_x_bian[3] + 30, ry, by,
                                          color='#bbb')

        # 底部分隔线
        bottom_y = start_y + 6 * row_h + 4
        c.create_line(4, bottom_y, W - 4, bottom_y, fill='#ccc')

        # 动爻说明
        dong = p['dong_yao']
        if dong:
            dong_names = '、'.join([f"{num_to_cn(d)}爻" for d in dong])
            c.create_text(W // 2, bottom_y + 16,
                          text=f"动爻：{dong_names}（○老阳动变阴，×老阴动变阳）",
                          font=('微软雅黑', 9), fill=self.dong_color)
        else:
            c.create_text(W // 2, bottom_y + 16,
                          text='六爻安静，无动爻，以本卦卦象及世应用神断之',
                          font=('微软雅黑', 9), fill='#666')

        # 调整canvas高度
        c.config(height=bottom_y + 36)

    def _draw_yao_symbol(self, canvas, x, y, yao_data, color=None):
        """绘制单个爻的符号"""
        if color is None:
            color = self.line_yang
        w = 44
        if yao_data['yinyang'] == 1:
            # 阳爻：一条实线
            canvas.create_line(x - w // 2, y, x + w // 2, y,
                               fill=color, width=3)
            if yao_data.get('is_dong'):
                canvas.create_text(x + w // 2 + 10, y, text='○',
                                   font=('微软雅黑', 12, 'bold'),
                                   fill=self.dong_color)
        else:
            # 阴爻：两段断线
            canvas.create_line(x - w // 2, y, x - 6, y,
                               fill=color, width=3)
            canvas.create_line(x + 6, y, x + w // 2, y,
                               fill=color, width=3)
            if yao_data.get('is_dong'):
                canvas.create_text(x + w // 2 + 10, y, text='×',
                                   font=('微软雅黑', 12, 'bold'),
                                   fill=self.dong_color)

    def save_guali(self):
        """保存卦例到文件"""
        if not self.paipan_result:
            messagebox.showwarning('提示', '请先排盘再保存卦例')
            return

        # 默认文件名
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"卦例_{self.paipan_result['name'].replace('为','')}_{self.shiqing_var.get()}_{now}.txt"

        path = filedialog.asksaveasfilename(
            title='保存卦例',
            defaultextension='.txt',
            initialfile=default_name,
            filetypes=[('文本文件', '*.txt'), ('所有文件', '*.*')]
        )
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"六爻卦例\n")
                gz = self._gz_cache
                f.write(f"占问事项：{self.shiqing_var.get()}\n")
                f.write(f"起卦日期：{self.current_date.strftime('%Y-%m-%d')}\n")
                if gz:
                    f.write(f"干支：{gz['year_gan']}{gz['year_zhi']}年 "
                            f"{gz['month_gan']}{gz['month_zhi']}月 "
                            f"{gz['ri_gan']}{gz['ri_zhi']}日，"
                            f"月建{gz['month_zhi']}，旬空{gz['xunkong'][0]}{gz['xunkong'][1]}\n")
                f.write('\n')
                f.write(paipan_to_text(self.paipan_result))
                f.write('\n\n')
                sq = self.shiqing_var.get()
                zr = fenxi_by_shiqing(self.paipan_result, sq, self.role_var.get())
                if zr is not None:
                    for line in zr:
                        f.write(line + '\n')
                else:
                    yongshen = YONGSHEN_MAP.get(sq)
                    result = fenxi_gua(self.paipan_result, yongshen_type=yongshen)
                    for line in result:
                        f.write(line + '\n')
                    zonghe = self._zonghe_duanyu(yongshen)
                    f.write('\n【综合断语】\n')
                    for z in zonghe:
                        f.write(z + '\n')

            messagebox.showinfo('成功', f'卦例已保存到：\n{path}')
        except Exception as e:
            messagebox.showerror('保存失败', str(e))


class DatePicker:
    """日历选择弹窗（纯 tkinter 实现，无额外依赖）"""

    def __init__(self, parent, initial_date, on_pick,
                 title_color='#8b2500', panel_color='#faf6ee',
                 text_color='#2c1810', accent_color='#a0522d'):
        self.on_pick = on_pick
        self.title_color = title_color
        self.panel_color = panel_color
        self.text_color = text_color
        self.accent_color = accent_color

        self.sel_date = initial_date
        self.view_year = initial_date.year
        self.view_month = initial_date.month
        self.today = datetime.date.today()

        self.win = tk.Toplevel(parent)
        self.win.title('选择起卦日期')
        self.win.resizable(False, False)
        self.win.configure(bg=panel_color)
        self.win.transient(parent)
        self.win.grab_set()

        self._build()
        self._render()

        # 居中到父窗口
        self.win.update_idletasks()
        try:
            px, py = parent.winfo_rootx(), parent.winfo_rooty()
            pw, ph = parent.winfo_width(), parent.winfo_height()
            w, h = self.win.winfo_width(), self.win.winfo_height()
            self.win.geometry(f'+{max(px + (pw - w) // 2, 0)}+{max(py + ph // 6, 0)}')
        except Exception:
            pass

    def _build(self):
        top = tk.Frame(self.win, bg=self.title_color)
        top.pack(fill='x', padx=10, pady=(10, 6))
        nav = dict(bg=self.title_color, fg='#ffd700', activebackground='#a52a2a',
                   activeforeground='#ffd700', relief='flat',
                   font=('微软雅黑', 11, 'bold'), cursor='hand2', width=4)
        tk.Button(top, text='«', command=lambda: self._shift(0, -1), **nav).pack(side='left')
        tk.Button(top, text='‹', command=lambda: self._shift(-1, 0), **nav).pack(side='left')
        self.title_var = tk.StringVar()
        tk.Label(top, textvariable=self.title_var, font=('微软雅黑', 12, 'bold'),
                 fg='#ffd700', bg=self.title_color).pack(side='left', fill='x', expand=True)
        tk.Button(top, text='›', command=lambda: self._shift(1, 0), **nav).pack(side='right')
        tk.Button(top, text='»', command=lambda: self._shift(0, 1), **nav).pack(side='right')

        week_frame = tk.Frame(self.win, bg=self.panel_color)
        week_frame.pack(fill='x', padx=10)
        for i, wname in enumerate(['日', '一', '二', '三', '四', '五', '六']):
            color = '#c0392b' if i in (0, 6) else self.text_color
            tk.Label(week_frame, text=wname, font=('微软雅黑', 10, 'bold'),
                     fg=color, bg=self.panel_color, width=4).grid(
                         row=0, column=i, padx=1, pady=2)

        self.grid_frame = tk.Frame(self.win, bg=self.panel_color)
        self.grid_frame.pack(padx=10, pady=4)

        bottom = tk.Frame(self.win, bg=self.panel_color)
        bottom.pack(fill='x', padx=10, pady=(4, 10))
        tk.Button(bottom, text='回到今天', font=('微软雅黑', 10),
                  bg=self.accent_color, fg='white', activebackground='#8b4513',
                  activeforeground='white', relief='flat', cursor='hand2',
                  command=self._go_today).pack(side='left')
        tk.Button(bottom, text='取消', font=('微软雅黑', 10),
                  bg='#999', fg='white', activebackground='#777',
                  activeforeground='white', relief='flat', cursor='hand2',
                  command=self.win.destroy).pack(side='right')

    def _shift(self, dm, dy):
        m, y = self.view_month + dm, self.view_year + dy
        if m > 12:
            m, y = 1, y + 1
        elif m < 1:
            m, y = 12, y - 1
        self.view_month, self.view_year = m, y
        self._render()

    def _go_today(self):
        self.view_year, self.view_month = self.today.year, self.today.month
        self._render()

    def _render(self):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        self.title_var.set(f'{self.view_year}年 {self.view_month}月')
        first_wday, ndays = calendar.monthrange(self.view_year, self.view_month)
        start_col = (first_wday + 1) % 7   # 周日为第一列
        cell_cfg = dict(relief='flat', cursor='hand2', font=('微软雅黑', 10),
                        width=4, height=2, bd=0)
        for day in range(1, ndays + 1):
            cell = start_col + day - 1
            r, col = divmod(cell, 7)
            date = datetime.date(self.view_year, self.view_month, day)
            if date == self.sel_date:
                btn = tk.Button(self.grid_frame, text=str(day),
                                bg=self.title_color, fg='white',
                                activebackground=self.title_color,
                                activeforeground='white', **cell_cfg)
            elif date == self.today:
                btn = tk.Button(self.grid_frame, text=str(day), bg='#f3d9c0',
                                fg=self.title_color, activebackground='#e8c39e',
                                activeforeground=self.title_color, **cell_cfg)
            else:
                txt = '#c0392b' if col in (0, 6) else self.text_color
                btn = tk.Button(self.grid_frame, text=str(day), bg=self.panel_color,
                                fg=txt, activebackground='#e8dcc8',
                                activeforeground=txt, **cell_cfg)
            btn.grid(row=r, column=col, padx=1, pady=1)
            btn.config(command=lambda d=date: self._choose(d))

    def _choose(self, date):
        self.sel_date = date
        self.on_pick(date)
        self.win.destroy()


def main():
    root = tk.Tk()
    # 高DPI适配
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = LiuYaoApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
