import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import csv
from datetime import datetime

# ─── 颜色常量 ───
BG          = "#0f1117"
CARD_BG     = "#1a1d27"
CARD_BORDER = "#2a2d3a"
ACCENT      = "#5b8af5"
ACCENT2     = "#7c4dff"
GREEN       = "#4ade80"
ORANGE      = "#fb923c"
RED         = "#f87171"
YELLOW      = "#fbbf24"
WHITE       = "#e2e8f0"
GRAY        = "#64748b"
DARK_GRAY   = "#1e2130"
ENTRY_BG    = "#252836"


class RoundedButton(tk.Canvas):
    """圆角按钮（用Canvas绘制）"""
    def __init__(self, parent, text, command=None, color=ACCENT,
                 hover_color="#7aa4f8", width=180, height=42, radius=12,
                 font_size=13, text_color="#ffffff", **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=CARD_BG, **kwargs)
        self.color = color
        self.hover_color = hover_color
        self.radius = radius
        self.text = text
        self.text_color = text_color
        self.font = ("Microsoft YaHei", font_size, "bold")
        self.command = command
        self._state = "normal"
        self._draw(0, 0, width, height)
        self.bind("<Button-1>", lambda e: self._pressed())
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))

    def _draw(self, x, y, w, h):
        self.delete("all")
        r = self.radius
        color = self.hover_color if self._state == "hover" else self.color
        if self._state == "disabled":
            color = "#44475a"
        self.create_polygon(
            x+r, y, x+w-r, y, x+w, y, x+w, y+r,
            x+w, y+h-r, x+w, y+h, x+w-r, y+h,
            x+r, y+h, x, y+h, x, y+h-r,
            x, y+r, x, y, x+r, y,
            fill=color, outline=""
        )
        cx, cy = x + w/2, y + h/2
        self.create_text(cx, cy, text=self.text, fill=self.text_color,
                         font=self.font)

    def _hover(self, inside):
        self._state = "hover" if inside else "normal"
        self._draw(0, 0, int(self.cget("width")), int(self.cget("height")))

    def _pressed(self):
        if self.command and self._state != "disabled":
            self.command()


class OutdoorChecklist:
    """户外出发准备清单 - 精美版"""

    HIKING = {
        "⛺ 露营系统": [
            ("双人帐篷+地钉风绳", 2800, 1, "2人共用"),
            ("睡袋(舒适温标-5℃)", 1200, 2, "1个/人"),
            ("防潮垫-蛋巢垫", 550, 2, "R值≥3"),
            ("充气枕头", 200, 2, "可压缩"),
            ("天幕+额外地钉", 800, 1, "休息区"),
        ],
        "🔥 炊具系统": [
            ("便携炉头+气罐", 350, 1, "分体式更佳"),
            ("套锅(1.5L+0.8L)", 600, 1, "含锅盖"),
            ("折叠餐具套装", 120, 2, "含碗筷杯"),
            ("折叠水桶/水袋", 150, 1, "5-10L"),
            ("净水片/过滤器", 80, 2, "备用净水"),
            ("打火机+防水火柴", 30, 1, "密封保存"),
        ],
        "🥾 鞋服系统": [
            ("登山鞋(已磨合)", 1200, 2, "中高帮防水"),
            ("速干内衣(长袖)", 150, 2, "美利奴羊毛佳"),
            ("速干T恤", 120, 2, "备1件"),
            ("抓绒衣/保暖层", 350, 2, "轻量保暖"),
            ("冲锋衣(硬壳)", 450, 2, "防水透气"),
            ("登山裤", 280, 2, "速干弹力"),
            ("保暖裤/软壳裤", 200, 2, "营地穿"),
            ("袜子(速干)", 80, 6, "2-3双/人"),
            ("遮阳帽", 60, 2, "宽檐"),
            ("保暖帽", 50, 2, "抓绒内里"),
        ],
        "🧭 导航通讯": [
            ("手机+充电宝(20000mAh)", 400, 2, "离线地图"),
            ("手持GPS", 200, 1, "备用导航"),
            ("对讲机(2台)", 180, 2, "长距离通讯"),
            ("北斗卫星信标", 230, 1, "紧急求救"),
            ("口哨", 10, 2, "求生用"),
            ("头灯(200流明+)", 80, 2, "备用电池"),
            ("营地灯", 150, 1, "悬挂式"),
            ("荧光棒/反光条", 20, 4, "安全标识"),
        ],
        "🩹 急救医疗": [
            ("急救包(全面)", 300, 1, "含绷带/碘伏/纱布"),
            ("个人药品(3天量)", 100, 2, "常用药"),
            ("止痛药(布洛芬)", 30, 1, ""),
            ("抗过敏药", 30, 1, ""),
            ("肠胃药", 30, 1, ""),
            ("高反药(红景天)", 50, 1, "高海拔必备"),
            ("蛇虫咬伤喷雾", 80, 1, ""),
            ("弹性绷带", 100, 1, "加压包扎"),
            ("医用胶带+棉签", 60, 1, ""),
            ("求生毯(太空毯)", 50, 1, "保温/反光"),
        ],
        "🔧 工具配件": [
            ("多功能工具刀", 200, 1, "Leatherman类"),
            ("登山杖(碳纤维)", 220, 4, "折叠款"),
            ("伞绳(10米)", 100, 1, "多用"),
            ("扎带+魔术贴", 30, 1, "打包用"),
            ("充电线(三合一)", 30, 2, ""),
            ("防水袋(证件/手机)", 50, 2, "多个规格"),
            ("大号防水袋(衣物)", 80, 2, "装睡袋衣物"),
        ],
        "🌧️ 雨雪防护": [
            ("雨衣(全身款)", 350, 2, "带背包罩"),
            ("防水 gloves", 120, 2, ""),
            ("鞋套/防水套", 80, 2, ""),
            ("一次性暖宝宝", 30, 10, "贴腹/贴背"),
            ("保温毯(急救用)", 60, 1, "额外"),
        ],
        "🍫 饮食系统": [
            ("饮用水(2L/人/天)", 2000, 2, "2天量=8L"),
            ("水袋(2L)", 50, 2, "行进中饮水"),
            ("能量棒/能量胶", 60, 10, "随时补充"),
            ("坚果/果干混合包", 80, 2, ""),
            ("压缩饼干", 500, 1, "备用"),
            ("巧克力", 200, 2, ""),
            ("即食饭/自热餐", 400, 2, "1餐/人"),
            ("盐丸/电解质粉", 30, 4, "防抽筋"),
        ],
        "💼 个人物品": [
            ("身份证/证件复印件", 30, 1, "密封防水袋"),
            ("现金(200元+)", 0, 1, "零钱+整钞"),
            ("保险单复印件", 20, 1, "电子备份"),
            ("紧急联系人卡片", 10, 1, "血型/病史"),
            ("手机防水袋", 50, 1, ""),
            ("纸巾+湿巾", 100, 2, ""),
            ("垃圾袋(多个)", 10, 3, "LNT无痕"),
            ("驱蚊液", 60, 1, ""),
            ("防晒SPF50+", 80, 2, ""),
            ("墨镜(UV400)", 50, 2, ""),
            ("个人洗漱包", 150, 2, "旅行装"),
            ("营地拖鞋/凉鞋", 350, 2, "放松双脚"),
        ],
    }

    DRIVING = {
        "🚗 车辆装备": [
            ("全尺寸备胎+工具", 35000, 1, "检查胎压"),
            ("千斤顶", 8000, 1, ""),
            ("脱困板×2", 4000, 1, "沙地/泥地"),
            ("绞盘(8000磅+)", 25000, 1, "含钢缆"),
            ("拖车绳(10m)", 5000, 1, "弹力款"),
            ("搭电线(过江龙)", 2000, 1, ""),
            ("充气泵+胎压计", 1200, 1, "数显"),
            ("灭火器(车用)", 1000, 2, "干粉"),
            ("三角警示牌", 500, 1, ""),
            ("反光背心×2", 300, 2, ""),
            ("应急电源(启动宝)", 5000, 1, "带气泵"),
        ],
        "🔧 随车工具": [
            ("多功能工具刀", 200, 1, ""),
            ("套筒扳手套装", 3000, 1, ""),
            ("十字/一字螺丝刀", 300, 1, ""),
            ("扎带+绝缘胶带", 100, 1, "多规格"),
            ("保险丝(各型号)×10", 100, 1, ""),
            ("备用机油1L", 1000, 1, ""),
            ("备用皮带/保险丝", 200, 1, ""),
            ("补胎胶片+胶水", 300, 1, ""),
            ("拖车D型环(2个)", 1500, 1, ""),
        ],
        "💧 油液补给": [
            ("玻璃水(额外)", 500, 1, ""),
            ("防冻液(备用)", 1000, 1, ""),
            ("刹车油(小瓶)", 300, 1, ""),
        ],
    }

    FOOD_DRINK = {
        "🍖 饮食系统": [
            ("饮用水", 1000, 3, "人均2-3L/天"),
            ("功能饮料/电解质粉", 200, 3, ""),
            ("能量棒/巧克力", 50, 10, ""),
            ("坚果/果干", 100, 6, ""),
            ("压缩饼干", 200, 2, "应急"),
            ("即食饭/罐头", 400, 2, "1餐/人"),
            ("盐丸", 20, 6, ""),
            ("维生素片", 10, 3, ""),
            ("保温壶(热水)", 300, 1, ""),
        ],
    }

    CLOTHING = {
        "🧥 服装系统": [
            ("冲锋衣(防风防水)", 450, 2, ""),
            ("保暖层-Fleece/羽绒", 350, 2, ""),
            ("速干衣×2", 150, 4, ""),
            ("速干裤×2", 200, 4, ""),
            ("保暖内衣", 120, 2, ""),
            ("保暖裤", 180, 2, ""),
            ("泳衣(过河用)", 80, 1, ""),
            ("遮阳帽×2", 60, 2, ""),
            ("保暖帽", 50, 2, ""),
            ("魔术头巾×4", 40, 4, ""),
            ("手套(防晒/保暖)", 80, 2, ""),
        ],
    }

    def __init__(self, root):
        self.root = root
        self.root.title("🏔️ 户外探险准备清单")
        self.root.geometry("1300x960")
        self.root.minsize(1200, 800)
        self.root.configure(bg=BG)

        self.setup_styles()

        self.current_mode = "hiking"
        self.checklist = []
        self.items_data = []
        self.route_checklist = []  # 行程指南勾选项
        self.route_data = []  # 行程指南数据
        self.risk_items = []  # 风险项
        self.hiking_weight = {"total": 0, "breakdown": {}}

        self.build_header()
        self.build_mode_switcher()
        self.build_input_form()
        self.build_buttons()
        self.build_route_guide()  # 行程指南
        self.build_risk_section()  # 风险提示
        self.build_weight_bar()
        self.build_table()
        self.build_footer()

        self.switch_mode("hiking")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Microsoft YaHei", 24, "bold"),
                        foreground=WHITE, background=BG)
        style.configure("Sub.TLabel", font=("Microsoft YaHei", 11),
                        foreground=GRAY, background=BG)
        style.configure("Card.TLabel", font=("Microsoft YaHei", 11),
                        foreground=WHITE, background=CARD_BG)
        style.configure("Hint.TLabel", font=("Microsoft YaHei", 10),
                        foreground=GRAY, background=BG)
        style.configure("Accent.TLabel", font=("Microsoft YaHei", 11, "bold"),
                        foreground=ACCENT, background=BG)
        style.configure("Green.TLabel", font=("Microsoft YaHei", 11, "bold"),
                        foreground=GREEN, background=BG)
        style.configure("Header.TLabel", font=("Microsoft YaHei", 13, "bold"),
                        foreground=ACCENT, background=CARD_BG)
        style.configure("Status.TLabel", font=("Microsoft YaHei", 12),
                        foreground=WHITE, background=CARD_BG)
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("Main.TFrame", background=BG)

    # ─── 头部 ───
    def build_header(self):
        self.header = tk.Frame(self.root, bg=BG, height=80)
        self.header.pack(fill="x", padx=0, pady=0)
        self.header.pack_propagate(False)

        logo_frame = tk.Frame(self.header, bg=BG)
        logo_frame.pack(side="left", padx=20)

        logo_canvas = tk.Canvas(logo_frame, width=40, height=40,
                                highlightthickness=0, bg=BG)
        logo_canvas.pack(side="left")
        logo_canvas.create_polygon(
            20, 5, 35, 35, 5, 35, fill=ACCENT, outline=""
        )
        logo_canvas.create_text(20, 22, text="⛰", font=("", 18), fill=WHITE)

        tk.Label(logo_frame, text="🏔️ 户外准备清单",
                 font=("Microsoft YaHei", 22, "bold"),
                 fg=WHITE, bg=BG).pack(side="left", padx=12)

        tk.Label(logo_frame, text="出发前的最后检查",
                 font=("Microsoft YaHei", 11),
                 fg=GRAY, bg=BG).pack(side="left")

        right_frame = tk.Frame(self.header, bg=BG)
        right_frame.pack(side="right", padx=20)

        self.status_dot = tk.Canvas(right_frame, width=10, height=10,
                                    highlightthickness=0, bg=BG)
        self.status_dot.pack(side="left", padx=5)
        self.status_dot.create_oval(2, 2, 8, 8, fill=GREEN, outline="")

        self.status_text = tk.Label(right_frame, text="就绪",
                                    font=("Microsoft YaHei", 10),
                                    fg=GREEN, bg=BG)
        self.status_text.pack(side="left", padx=10)

    # ─── 模式切换 ───
    def build_mode_switcher(self):
        sw = tk.Frame(self.root, bg=BG, height=50)
        sw.pack(fill="x", padx=15, pady=(10, 5))

        self.mode_frame = tk.Frame(sw, bg=CARD_BORDER, bd=0, relief="flat")
        self.mode_frame.pack(fill="x")

        labels = [
            ("🥾 徒步模式", "hiking"),
            ("🚗 驾车模式", "driving"),
        ]
        self.mode_btns = []
        for i, (text, mode) in enumerate(labels):
            btn = RoundedButton(
                self.mode_frame, text=text,
                command=lambda m=mode: self.switch_mode(m),
                color="#2a2d3a" if i == 1 else ACCENT,
                width=200, height=38, radius=19, font_size=13
            )
            btn.pack(side="left", padx=2, pady=3)
            self.mode_btns.append((btn, mode))

    # ─── 输入表单 ───
    def build_input_form(self):
        self.form_card = tk.Frame(self.root, bg=CARD_BG, bd=0)
        self.form_card.pack(fill="x", padx=15, pady=5)

        tf = tk.Frame(self.form_card, bg=CARD_BG)
        tf.pack(fill="x", padx=15, pady=(12, 5))
        tk.Label(tf, text="📋 行程信息", font=("Microsoft YaHei", 13, "bold"),
                 fg=ACCENT, bg=CARD_BG).pack(side="left")
        tk.Label(tf, text="填写行程参数，智能生成装备清单",
                 font=("Microsoft YaHei", 9), fg=GRAY, bg=CARD_BG).pack(side="right")

        self.form_inputs = {}
        fields_frame = tk.Frame(self.form_card, bg=CARD_BG)
        fields_frame.pack(fill="x", padx=15, pady=(5, 15))

        def add_field(parent, label, key, values=None, row=0, col=0, entry_w=14):
            lbl = tk.Label(parent, text=label, font=("Microsoft YaHei", 10),
                          fg=GRAY, bg=CARD_BG)
            lbl.grid(row=row, column=col*2, sticky="w", padx=(0,8), pady=5)
            if values:
                var = tk.StringVar(value=values[0])
                cb = ttk.Combobox(parent, textvariable=var, values=values,
                                  width=entry_w, state="readonly")
                cb.grid(row=row, column=col*2+1, sticky="w", pady=5)
                cb.configure(style="Card.TCombobox")
            else:
                var = tk.StringVar(value="")
                ent = tk.Entry(parent, textvariable=var, width=entry_w,
                              bg=ENTRY_BG, fg=WHITE, insertbackground=WHITE,
                              relief="flat", font=("Microsoft YaHei", 10),
                              highlightcolor=ACCENT, highlightthickness=1,
                              highlightbackground=CARD_BORDER)
                ent.grid(row=row, column=col*2+1, sticky="w", pady=5)
            self.form_inputs[key] = var

        add_field(fields_frame, "目的地", "destination", row=0, col=0)
        add_field(fields_frame, "路程(km)", "distance", row=0, col=1)
        add_field(fields_frame, "路面", "terrain",
                  ["铺装公路","碎石/砂石","泥路/土路","岩石/非铺装",
                   "混合路面","沙漠沙地","雪地/冰面","山径/步道"],
                  row=0, col=2)
        add_field(fields_frame, "爬升(m)", "climb", row=0, col=3)

        add_field(fields_frame, "过夜数", "nights",
                  ["0","1","2","3","4+"], row=1, col=0)
        add_field(fields_frame, "白天温(℃)", "temp_high", row=1, col=1,
                  values=[str(i) for i in range(-20,46)])
        add_field(fields_frame, "夜间温(℃)", "temp_low", row=1, col=2,
                  values=[str(i) for i in range(-30,36)])
        add_field(fields_frame, "降雨%", "rain", row=1, col=3,
                  values=[str(i) for i in range(0,101,5)])

        add_field(fields_frame, "人数", "people",
                  [str(i) for i in range(1,11)], row=2, col=0)

        self.veh_fields = {}
        add_field(fields_frame, "车辆数", "cars",
                  [str(i) for i in range(1,6)], row=2, col=1)
        add_field(fields_frame, "难度", "difficulty",
                  ["休闲","中等","硬核"], row=2, col=2)

        # 新增：湿度
        add_field(fields_frame, "湿度%", "humidity", row=2, col=3,
                  values=[str(i) for i in range(0,101,5)])

        # 新增：出发时间
        add_field(fields_frame, "出发时间", "depart_time", row=3, col=0,
                  values=["05:00","05:30","06:00","06:30","07:00","07:30","08:00"])
        # 新增：预计到达时间
        add_field(fields_frame, "预计返回", "return_time", row=3, col=1,
                  values=["当天返回","次日返回","第2天","第3天"])
        # 新增：队伍经验
        add_field(fields_frame, "队伍经验", "experience", row=3, col=2,
                  values=["新手","有一定经验","经验丰富","专业领队"])

        # 设置默认值
        self.set_defaults()

    # ─── 新增：行程指南区域 ───
    def build_route_guide(self):
        self.route_card = tk.Frame(self.root, bg=CARD_BG, bd=0)
        self.route_card.pack(fill="x", padx=15, pady=5)

        tf = tk.Frame(self.route_card, bg=CARD_BG)
        tf.pack(fill="x", padx=15, pady=(12, 5))
        tk.Label(tf, text="🗺️ 行程指南与时间表", font=("Microsoft YaHei", 13, "bold"),
                 fg=YELLOW, bg=CARD_BG).pack(side="left")
        tk.Label(tf, text="填写后点击「生成行程」自动建议",
                 font=("Microsoft YaHei", 9), fg=GRAY, bg=CARD_BG).pack(side="right")

        body_frame = tk.Frame(self.route_card, bg=CARD_BG)
        body_frame.pack(fill="x", padx=15, pady=(5, 15))

        # 左侧输入
        left_frame = tk.Frame(body_frame, bg=CARD_BG)
        left_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.route_inputs = {}

        def add_route_field(parent, label, key, values=None, row=0):
            lbl = tk.Label(parent, text=label, font=("Microsoft YaHei", 9),
                          fg=GRAY, bg=CARD_BG)
            lbl.grid(row=row, column=0, sticky="w", padx=(0,8), pady=3)
            if values:
                var = tk.StringVar(value=values[0])
                cb = ttk.Combobox(parent, textvariable=var, values=values,
                                  width=18, state="readonly")
                cb.grid(row=row, column=1, sticky="w", pady=3)
            else:
                var = tk.StringVar(value="")
                ent = tk.Entry(parent, textvariable=var, width=20,
                              bg=ENTRY_BG, fg=WHITE, insertbackground=WHITE,
                              relief="flat", font=("Microsoft YaHei", 9),
                              highlightcolor=ACCENT, highlightthickness=1,
                              highlightbackground=CARD_BORDER)
                ent.grid(row=row, column=1, sticky="w", pady=3)
            self.route_inputs[key] = var
            return row + 1

        row = 0
        row = add_route_field(left_frame, "🕐 出发时间", "depart_time",
                              ["05:00","05:30","06:00","06:30","07:00","07:30","08:00"], row)
        row = add_route_field(left_frame, "🏕️ 计划宿营地", "camp_location",
                              ["营地A(山脊平台)","营地B(河谷旁)","营地C(草甸区)","营地D(观景平台)",
                               "自选营地(请填写)"], row)
        # 允许自填营地
        row = add_route_field(left_frame, "   └ 营地坐标/描述", "camp_detail", None, row)
        row = add_route_field(left_frame, "📍 折返点", "turnaround", None, row)
        row = add_route_field(left_frame, "⏰ 预计返回时间", "est_return",
                              ["当天日落前","次日08:00","次日10:00","第2天傍晚"], row)
        row = add_route_field(left_frame, "🚗 接应车辆位置", "vehicle_pos", None, row)
        row = add_route_field(left_frame, "📡 紧急撤离路线", "evac_route", None, row)

        # 右侧：生成的行程时间线
        right_frame = tk.Frame(body_frame, bg=DARK_GRAY, bd=0, relief="flat")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(right_frame, text="📅 行程时间线 (生成后显示)",
                 font=("Microsoft YaHei", 10, "bold"), fg=ACCENT,
                 bg=DARK_GRAY).pack(padx=10, pady=(10, 5), anchor="w")

        self.timeline_text = scrolledtext.ScrolledText(
            right_frame, height=10, state="disabled",
            font=("Consolas", 10), bg="#1e2130", fg=WHITE,
            relief="flat", borderwidth=0
        )
        self.timeline_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 生成时间线按钮
        btn_frame = tk.Frame(right_frame, bg=DARK_GRAY)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(btn_frame, text="📅 生成行程时间线", command=self.generate_timeline,
                  bg=YELLOW, fg="#000", font=("Microsoft YaHei", 11, "bold"),
                  relief="flat", padx=10, pady=4, cursor="hand2",
                  activebackground="#fbbf24", activeforeground="#000",
                  bd=0, highlightthickness=0).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑️ 清空", command=self.clear_timeline,
                  bg="#44475a", fg="white", font=("Microsoft YaHei", 10),
                  relief="flat", padx=10, pady=4, cursor="hand2",
                  bd=0, highlightthickness=0).pack(side="left", padx=5)

    # ─── 行程时间线生成 ───
    def generate_timeline(self):
        depart = self.route_inputs.get("depart_time", tk.StringVar()).get()
        camp = self.route_inputs.get("camp_location", tk.StringVar()).get()
        camp_detail = self.route_inputs.get("camp_detail", tk.StringVar()).get()
        turnaround = self.route_inputs.get("turnaround", tk.StringVar()).get()
        est_return = self.route_inputs.get("est_return", tk.StringVar()).get()
        vehicle_pos = self.route_inputs.get("vehicle_pos", tk.StringVar()).get()
        evac_route = self.route_inputs.get("evac_route", tk.StringVar()).get()

        distance = self.sf(self.get_val("distance"))
        climb = self.sf(self.get_val("climb"))
        terrain = self.get_val("terrain", "铺装公路")
        nights = self.si(self.get_val("nights"), 1)
        difficulty = self.get_val("difficulty", "中等")
        mode = self.current_mode

        if not depart:
            messagebox.showwarning("提示", "请先填写出发时间")
            return

        # 解析出发时间
        try:
            depart_dt = datetime.strptime(depart, "%H:%M")
        except:
            depart_dt = datetime.strptime("06:00", "%H:%M")

        lines = []
        lines.append("=" * 50)
        lines.append("🗺️  行程时间线")
        lines.append("=" * 50)

        # 出发
        t = depart_dt
        lines.append(f"\n🌅 {t.strftime('%H:%M')} - 出发")
        lines.append(f"   - 检查车辆/装备（对照清单逐项确认）")
        lines.append(f"   - 确认油量/电量充足")
        lines.append(f"   - 通知紧急联系人行程计划")

        if mode == "driving":
            # 驾车：计算行驶时间
            # 假设越野平均速度15-30km/h（根据路况）
            speeds = {"铺装公路": 60, "碎石/砂石": 35, "泥路/土路": 20,
                      "岩石/非铺装": 12, "混合路面": 30, "沙漠沙地": 25,
                      "雪地/冰面": 15, "山径/步道": 0}
            speed = speeds.get(terrain, 20)
            if speed > 0 and distance > 0:
                travel_hours = distance / speed
                # 分段行程
                if distance > 100:
                    # 第一段：到达登山口
                    arrive_base = (datetime.combine(t.date(), t.time())
                                   + __import__("datetime").timedelta(hours=distance * 0.3 / speed))
                    lines.append(f"\n🚗 {arrive_base.strftime('%H:%M')} - 到达登山口/起点")
                    lines.append(f"   - 停车检查车辆")
                    lines.append(f"   - 装载装备，清点人数")
                    lines.append(f"   - 简短安全会议（路线/信号/撤离计划）")

                    # 第二段：到达营地附近
                    arrive_camp = (datetime.combine(t.date(), t.time())
                                   + __import__("datetime").timedelta(hours=distance * 0.7 / speed))
                    lines.append(f"\n🥾 {arrive_camp.strftime('%H:%M')} - 到达徒步起点/营地附近")
                    lines.append(f"   - 选择营地位置")
                    lines.append(f"   - 开始搭帐篷、生火（如允许）")
                    if camp_detail:
                        lines.append(f"   - 📍 营地: {camp_detail}")
                else:
                    arrive_t = (datetime.combine(t.date(), t.time())
                               + __import__("datetime").timedelta(hours=distance / speed))
                    lines.append(f"\n📍 {arrive_t.strftime('%H:%M')} - 到达目的地")
                    lines.append(f"   - 选择营地/停车")
                    lines.append(f"   - 安营扎寨")
            else:
                lines.append(f"\n🥾 到达徒步起点")
                lines.append(f"   - 整理装备开始徒步")
        else:
            # 徒步
            # 平均徒步速度：平路4km/h，爬升额外+1h/500m
            h_speed = 4  # km/h
            climb_time = (climb / 500) * 1 if climb > 0 else 0  # 每500m爬升额外1小时
            if distance > 0:
                travel_hours = distance / h_speed + climb_time
                mid = distance / 2
                first_half = mid / h_speed

                t1 = (datetime.combine(t.date(), t.time())
                      + __import__("datetime").timedelta(hours=first_half))
                lines.append(f"\n🚶 {t1.strftime('%H:%M')} - 到达前半程休息点")
                lines.append(f"   - 休息15分钟，补充水分和食物")
                lines.append(f"   - 检查脚部状况（预防水泡）")

                arrive_t = (datetime.combine(t.date(), t.time())
                           + __import__("datetime").timedelta(hours=travel_hours))
                lines.append(f"\n🏕️ {arrive_t.strftime('%H:%M')} - 到达营地")
                if camp_detail:
                    lines.append(f"   - 📍 {camp_detail}")
                lines.append(f"   - 搭建营地（帐篷、炉具）")
            else:
                lines.append(f"\n🏕️ 到达营地")
                lines.append(f"   - 搭建营地")

        # 营地活动
        lines.append(f"\n🏠 营地活动")
        lines.append(f"   - 搭建/检查帐篷")
        lines.append(f"   - 做饭/热食")
        lines.append(f"   - 检查装备状态")
        lines.append(f"   - 拍照片记录📸")
        if nights > 1:
            lines.append(f"   - 检查天气变化")
            lines.append(f"   - 规划次日路线")

        # 次日（如果过夜）
        if nights >= 1:
            lines.append(f"\n--- 第2天 ---")
            t2 = depart_dt + __import__("datetime").timedelta(days=1)
            if terrain in ("雪地/冰面",):
                lines.append(f"☀️ {t2.strftime('%H:%M')} - 起床（可稍晚避开低温）")
            else:
                lines.append(f"☀️ {t2.strftime('%H:%M')} - 起床")
            lines.append(f"   - 收拾营地（Leave No Trace原则）")
            lines.append(f"   - 检查天气，决定行程")
            lines.append(f"   - 早餐")
            lines.append(f"🧳 {t2.strftime('%H:%M')} - 下撤/返程")
            lines.append(f"   - 注意体力分配")
            lines.append(f"   - 带走所有垃圾")

        if turnaround:
            lines.append(f"\n🔄 折返点: {turnaround}")
        if vehicle_pos:
            lines.append(f"🚗 接应车辆: {vehicle_pos}")
        if evac_route:
            lines.append(f"🏥 紧急撤离路线: {evac_route}")

        lines.append(f"\n⏰ 计划返回/结束时间: {est_return}")
        lines.append(f"\n{'=' * 50}")

        text = "\n".join(lines)

        self.timeline_text.config(state="normal")
        self.timeline_text.delete("1.0", "end")
        self.timeline_text.insert("end", text)
        self.timeline_text.config(state="disabled")

        self.log(f"✅ 行程时间线已生成")

        # 自动生成风险提示
        self.generate_risks()

    def clear_timeline(self):
        self.timeline_text.config(state="normal")
        self.timeline_text.delete("1.0", "end")
        self.timeline_text.insert("end", "行程时间线已清空，请重新生成。")
        self.timeline_text.config(state="disabled")

    # ─── 风险提示区域 ───
    def build_risk_section(self):
        self.risk_card = tk.Frame(self.root, bg=CARD_BG, bd=0)
        self.risk_card.pack(fill="x", padx=15, pady=5)

        tf = tk.Frame(self.risk_card, bg=CARD_BG)
        tf.pack(fill="x", padx=15, pady=(12, 5))
        tk.Label(tf, text="⚠️ 风险提示与注意事项", font=("Microsoft YaHei", 13, "bold"),
                 fg=RED, bg=CARD_BG).pack(side="left")
        tk.Label(tf, text="基于环境和天气条件自动生成",
                 font=("Microsoft YaHei", 9), fg=GRAY, bg=CARD_BG).pack(side="right")

        self.risk_text = scrolledtext.ScrolledText(
            self.risk_card, height=6, state="disabled",
            font=("Microsoft YaHei", 10), bg=DARK_GRAY, fg=WHITE,
            relief="flat", borderwidth=0, wrap="word"
        )
        self.risk_text.pack(fill="x", padx=15, pady=(5, 15))

        # 注意事项复选框
        notes_frame = tk.Frame(self.risk_card, bg=CARD_BG)
        notes_frame.pack(fill="x", padx=15, pady=(0, 15))

        tk.Label(notes_frame, text="✅ 我已确认:",
                 font=("Microsoft YaHei", 10, "bold"),
                 fg=GREEN, bg=CARD_BG).pack(anchor="w")

        self.safety_checks = {}
        safety_items = [
            "已告知家人行程和预计返回时间",
            "已购买户外运动保险",
            "手机充满电并携带充电宝",
            "了解紧急求救号码（110/119/120）",
            "携带急救包并了解基本急救知识",
            "不会单独行动，保持团队在一起",
            "了解天气情况，必要时取消行程",
        ]
        for item in safety_items:
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(notes_frame, text=item, variable=var,
                               font=("Microsoft YaHei", 9),
                               bg=CARD_BG, fg=WHITE, selectcolor=DARK_GRAY,
                               activebackground=CARD_BG, activeforeground=WHITE)
            cb.pack(anchor="w", padx=20, pady=1)
            self.safety_checks[item] = var

    def generate_risks(self):
        """根据条件自动生成风险提示"""
        try:
            terrain = self.get_val("terrain", "铺装公路")
            temp_hi = self.sf(self.get_val("temp_high"), 20)
            temp_lo = self.sf(self.get_val("temp_low"), 10)
            rain = self.sf(self.get_val("rain"), 0)
            humidity = self.sf(self.get_val("humidity"), 50)
            distance = self.sf(self.get_val("distance"), 0)
            night = self.si(self.get_val("nights"), 0)
            mode = self.current_mode
            difficulty = self.get_val("difficulty", "中等")
            climb = self.sf(self.get_val("climb"), 0)
        except:
            terrain = "铺装公路"
            temp_hi, temp_lo = 20, 10
            rain, humidity, distance = 0, 50, 0
            night = 0
            mode = "hiking"
            difficulty = "中等"
            climb = 0

        risks = []
        precautions = []

        # ── 低温风险 ──
        if temp_lo < 0:
            risks.append(("🔴 极寒风险", f"夜间温度 {temp_lo}℃，存在冻伤风险"))
            precautions.append("穿保暖内衣+羽绒+防风外套，保护四肢末端")
            if mode == "hiking":
                precautions.append("使用温标-15℃以下的睡袋，热水瓶睡前灌满")
        elif temp_lo < 5:
            risks.append(("🟡 低温风险", f"夜间温度 {temp_lo}℃，注意保暖"))
            precautions.append("携带保暖帽、手套、暖宝宝")

        # ── 高温风险 ──
        if temp_hi > 35:
            risks.append(("🔴 高温风险", f"白天温度 {temp_hi}℃，警惕中暑"))
            precautions.append("多带水（人/3L/天），避开正午行进")
            precautions.append("携带藿香正气水、防晒装备")
        elif temp_hi > 30:
            risks.append(("🟡 高温风险", f"白天温度 {temp_hi}℃，注意防暑"))

        # ── 降雨风险 ──
        if rain > 70:
            risks.append(("🔴 暴雨风险", f"降雨概率 {rain}%，注意山洪/滑坡"))
            precautions.append("避开河道、峡谷地带，警惕水位上涨")
            if mode == "hiking":
                precautions.append("装备做好防水保护，穿防水登山鞋")
        elif rain > 40:
            risks.append(("🟡 降雨可能", f"降雨概率 {rain}%，备好雨具"))
            if mode == "hiking":
                precautions.append("雨后山路湿滑，注意脚下，使用登山杖")

        # ── 地形风险 ──
        if "岩石" in terrain or "非铺装" in terrain:
            risks.append(("🟡 复杂地形", "岩石/碎石路面，崴脚/滑倒风险"))
            precautions.append("穿中高帮登山鞋，使用登山杖，注意落石")
        if "泥路" in terrain or "土路" in terrain:
            risks.append(("🟡 泥泞路面", "路面湿滑，可能陷车/滑倒"))
            if mode == "driving":
                precautions.append("低速行驶，保持车距，携带脱困板")
        if "沙漠" in terrain:
            risks.append(("🔴 沙漠环境", "高温缺水，沙尘迷路风险"))
            precautions.append("多带水+2倍量，带GPS+地图，防沙装备")
            precautions.append("注意沙尘暴预警")
        if "雪地" in terrain or "冰面" in terrain:
            risks.append(("🔴 雪地风险", "路面结冰/积雪，滑倒/车辆失控"))
            precautions.append("穿防滑鞋/冰爪，车辆安装防滑链")
            precautions.append("注意雪崩风险（山区）")
        if "山径" in terrain or "步道" in terrain:
            risks.append(("🟡 山地徒步", "山路崎岖，体力消耗大"))
            precautions.append("控制节奏，每小时休息5-10分钟")
            if climb > 500:
                precautions.append(f"爬升 {climb}m 较大，注意高反预防")

        # ── 高海拔 ──
        if climb > 2500:
            risks.append(("🔴 高海拔风险", f"最大爬升 {climb}m，可能出现高原反应"))
            precautions.append("缓慢行进，多喝水，备红景天/高原安")
            precautions.append("出现头痛/恶心立即停止上行并下撤")

        # ── 夜路风险 ──
        if night > 0 and distance > 50:
            risks.append(("🟡 夜间风险", f"需过 {night} 晚，注意夜间安全"))
            precautions.append("营地远离悬崖/河道，睡前检查帐篷固定")
            precautions.append("头灯充满电，备足照明")

        # ── 长途/偏远离 ──
        if distance > 200:
            risks.append(("🟡 长途提醒", f"路程 {distance}km，补给点稀少"))
            precautions.append("多备食物饮水+1天量，告知后方人员行程")

        # ── 难度等级风险 ──
        if difficulty == "硬核" and mode == "driving":
            risks.append(("🔴 硬核越野风险", "路线难度高，车辆/人员安全风险"))
            precautions.append("必须有绞盘和拖车装备，不要独自前往")
            precautions.append("提前了解路线，确认可通行性")

        # ── 湿度相关 ──
        if humidity > 80:
            risks.append(("🟡 高湿度", f"湿度 {humidity}%，装备/衣物易湿"))
            precautions.append("携带防水袋，保持脚部干燥预防水泡")

        # 构建输出
        self.risk_text.config(state="normal")
        self.risk_text.delete("1.0", "end")

        if not risks:
            self.risk_text.insert("end", "✅ 根据当前条件，未发现明显风险。\n继续保持安全意识！")
        else:
            self.risk_text.insert("end", "⚠️ 识别到以下风险，请重点关注：\n\n", "title")
            for level, msg in risks:
                self.risk_text.insert("end", f"{level}: {msg}\n")
            self.risk_text.insert("end", f"\n{'─' * 50}\n", "divider")
            self.risk_text.insert("end", "📌 安全建议：\n\n", "title")
            for i, p in enumerate(precautions, 1):
                self.risk_text.insert("end", f"  {i}. {p}\n")

        # 通用提示
        self.risk_text.insert("end", f"\n{'─' * 50}\n", "divider")
        self.risk_text.insert("end", "📋 通用安全守则：\n\n", "title")
        universal = [
            "1. 出发前将行程告知家人/朋友，包括路线和预计返回时间",
            "2. 至少2人同行，不要单独行动",
            "3. 保持手机电量充足，带上充电宝和充电线",
            "4. 遇到恶劣天气及时调整或取消行程",
            "5. 遵循 Leave No Trace 原则，保护自然环境",
            "6. 尊重当地法规，部分区域可能需许可证",
            "7. 野生动物出没地区，妥善存放食物，保持距离",
            "8. 紧急情况拨打 110（报警）/ 119（消防）/ 120（急救）",
        ]
        for item in universal:
            self.risk_text.insert("end", f"  {item}\n")

        self.risk_text.tag_config("title", foreground=YELLOW, font=("Microsoft YaHei", 10, "bold"))
        self.risk_text.tag_config("divider", foreground=GRAY)
        self.risk_text.config(state="disabled")

        self.log(f"⚠️ 生成 {len(risks)} 条风险提示")

    # ─── 按钮 ───
    def build_buttons(self):
        bar = tk.Frame(self.root, bg=CARD_BG, height=50)
        bar.pack(fill="x", padx=15, pady=5)
        bar.pack_propagate(False)

        def make_btn(text, cmd, color=ACCENT, w=14):
            return tk.Button(bar, text=text, command=cmd,
                            bg=color, fg="white", font=("Microsoft YaHei", 11, "bold"),
                            relief="flat", padx=6, pady=4, cursor="hand2",
                            activebackground="#7aa4f8", activeforeground="white",
                            bd=0, highlightthickness=0, width=w)

        make_btn("🔄 生成清单", self.generate, ACCENT).pack(side="left", padx=4)
        make_btn("📅 时间线", self.generate_timeline, YELLOW, 10).pack(side="left", padx=4)
        make_btn("✅ 全选", self.select_all, "#22c55e", 8).pack(side="left", padx=4)
        make_btn("❌ 全不选", self.deselect_all, "#ef4444", 8).pack(side="left", padx=4)
        make_btn("🧮 算背包", self.calc_weight, "#f59e0b", 10).pack(side="left", padx=4)
        make_btn("📤 导出CSV", self.export_csv, "#8b5cf6", 10).pack(side="left", padx=4)

    # ─── 重量统计 ───
    def build_weight_bar(self):
        self.weight_card = tk.Frame(self.root, bg=CARD_BG, bd=0)
        self.weight_card.pack(fill="x", padx=15, pady=5)

        self.weight_main = tk.Label(self.weight_card,
                                     text="点击「计算背包」查看预估负重",
                                     font=("Microsoft YaHei", 13, "bold"),
                                     fg=WHITE, bg=CARD_BG)
        self.weight_main.pack(padx=15, pady=(12, 2))

        self.weight_detail = scrolledtext.ScrolledText(
            self.weight_card, height=4, state="disabled",
            font=("Consolas", 10), bg=DARK_GRAY, fg=WHITE,
            relief="flat", borderwidth=0
        )
        self.weight_detail.pack(fill="x", padx=15, pady=(0, 12))

    # ─── 表格 ───
    def build_table(self):
        table_card = tk.Frame(self.root, bg=CARD_BG, bd=0)
        table_card.pack(fill="both", expand=True, padx=15, pady=5)

        tf = tk.Frame(table_card, bg=CARD_BG)
        tf.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(tf, text="🎒 装备清单", font=("Microsoft YaHei", 13, "bold"),
                 fg=ACCENT, bg=CARD_BG).pack(side="left")
        tk.Label(tf, text="点击右侧列切换 ✓", font=("Microsoft YaHei", 9),
                 fg=GRAY, bg=CARD_BG).pack(side="right")

        columns = ("类别", "装备", "重量(g)", "数量", "已携带")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
        for col, w in zip(columns, (100, 380, 80, 50, 80)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.column("类别", anchor="center")
        self.tree.column("重量(g)", anchor="center")
        self.tree.column("数量", anchor="center")
        self.tree.column("已携带", anchor="center")

        style = ttk.Style()
        style.configure("Treeview", font=("Microsoft YaHei", 10),
                        rowheight=28, background=DARK_GRAY,
                        fieldbackground=DARK_GRAY, foreground=WHITE)
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 10, "bold"),
                        background=CARD_BG, foreground=ACCENT)
        style.map("Treeview", background=[("selected", ACCENT)])

        sb = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<ButtonRelease-1>", self._toggle_carry)

    # ─── 底部 ───
    def build_footer(self):
        self.footer = tk.Frame(self.root, bg=BG, height=30)
        self.footer.pack(fill="x")
        self.footer.pack_propagate(False)
        tk.Label(self.footer,
                 text="🏕️ 数据仅保存在本地 · 出行安全第一 · 导出CSV分享给队友",
                 font=("Microsoft YaHei", 9), fg=GRAY, bg=BG).pack()

    # ─── 行为 ───
    def set_defaults(self):
        hiking = self.current_mode == "hiking"
        self.form_inputs["destination"].set("武功山" if hiking else "阿拉善")
        self.form_inputs["distance"].set("25" if hiking else "300")
        self.form_inputs["terrain"].set("山径/步道" if hiking else "泥路/土路")
        self.form_inputs["climb"].set("1200" if hiking else "500")
        self.form_inputs["nights"].set("1")
        self.form_inputs["temp_high"].set("22" if hiking else "25")
        self.form_inputs["temp_low"].set("8" if hiking else "5")
        self.form_inputs["rain"].set("30")
        self.form_inputs["humidity"].set("65" if hiking else "30")
        self.form_inputs["people"].set("2" if hiking else "4")
        self.form_inputs["cars"].set("2")
        self.form_inputs["difficulty"].set("中等")
        self.form_inputs["depart_time"].set("06:00")
        self.form_inputs["return_time"].set("当天返回" if hiking else "第2天")
        self.form_inputs["experience"].set("有一定经验")

    def get_val(self, key, default=""):
        v = self.form_inputs.get(key)
        if v is None:
            return default
        try:
            return v.get()
        except:
            return default

    def si(self, s, d=0):
        try:
            return int(s) if s else d
        except:
            return d

    def sf(self, s, d=0.0):
        try:
            return float(s) if s else d
        except:
            return d

    def switch_mode(self, mode):
        self.current_mode = mode
        self.set_defaults()
        for btn, m in self.mode_btns:
            if m == mode:
                btn.color = ACCENT
                btn._state = "normal"
                btn._draw(0, 0, int(btn.cget("width")), int(btn.cget("height")))
            else:
                btn.color = "#2a2d3a"
                btn._state = "normal"
                btn._draw(0, 0, int(btn.cget("width")), int(btn.cget("height")))
        self.log(f"已切换到 {'🥾 徒步模式' if mode == 'hiking' else '🚗 驾车模式'}")

    def log(self, msg):
        self.weight_detail.config(state="normal")
        self.weight_detail.insert("end", msg + "\n")
        self.weight_detail.see("end")
        self.weight_detail.config(state="disabled")

    # ─── 徒步生成 ───
    def _build_hiking(self):
        dist     = self.sf(self.get_val("distance"))
        climb    = self.sf(self.get_val("climb"))
        nights   = self.si(self.get_val("nights"))
        temp_hi  = self.sf(self.get_val("temp_high"))
        temp_lo  = self.sf(self.get_val("temp_low"))
        rain     = self.sf(self.get_val("rain"))
        people   = self.si(self.get_val("people"))
        dest     = self.get_val("destination")
        terrain  = self.get_val("terrain")

        rows = []
        def add(cat, item, weight_g=0, qty=1, note=""):
            rows.append({"cat": cat, "item": item, "w": weight_g, "qty": qty, "note": note, "carried": False})

        # 基础
        for item, w, qty, note in self.HIKING["⛺ 露营系统"]:
            add("⛺ 露营", item, w, max(1, qty if qty > 1 else (people//2 if "共用" in note else people)), note)

        for item, w, qty, note in self.HIKING["🔥 炊具系统"]:
            add("🔥 炊具", item, w, qty, note)

        for item, w, qty, note in self.HIKING["🥾 鞋服系统"]:
            if "共用" in note:
                add("🥾 服装", item, w, qty, note)
            else:
                add("🥾 服装", item, w, qty, f"x{people}" if people > 1 else "")

        for item, w, qty, note in self.HIKING["🧭 导航通讯"]:
            add("🧭 导航", item, w, qty, note)

        for item, w, qty, note in self.HIKING["🩹 急救医疗"]:
            add("🩹 急救", item, w, max(1, people // 2), note)

        for item, w, qty, note in self.HIKING["🔧 工具配件"]:
            add("🔧 工具", item, w, people if "登山杖" in item else qty, note)

        rain_gear = self.HIKING["🌧️ 雨雪防护"]
        add("🌧️ 防护", rain_gear[0][0], rain_gear[0][1], people)
        if rain > 30 or temp_lo < 5:
            for item, w, qty, note in rain_gear[1:]:
                add("🌧️ 防护", item, w, qty, note)

        food = self.HIKING["🍫 饮食系统"]
        for item, w, qty, note in food:
            if "饮用水" in item:
                add("🍫 饮食", item, w * people * max(1, nights + 1), people, f"{nights+1}天量")
            elif w == 0:
                add("🍫 饮食", item, 0, 1, note)
            else:
                add("🍫 饮食", item, w, qty * max(1, people // 2) if qty > 1 else qty, note)

        gear = self.HIKING["💼 个人物品"]
        for item, w, qty, note in gear:
            if qty > 1 and people >= 2:
                q = max(1, people // 2)
            else:
                q = qty
            add("💼 个人", item, w, q, note)

        if "雪" in terrain:
            add("❄️ 雪地特需", "冰爪/钉鞋套", 400, people)
            add("❄️ 雪地特需", "雪套/绑腿", 200, people)
            add("❄️ 雪地特需", "保暖手套(厚)", 180, people)
            add("❄️ 雪地特需", "墨镜(防雪盲)", 60, people)
        if terrain == "沙漠沙地":
            add("🏜️ 沙漠特需", "防沙面罩/眼镜", 150, people)
            add("🏜️ 沙漠特需", "额外饮水", 1500 * people, people)
        if "岩石" in terrain or "非铺装" in terrain:
            add("🪨 技术地形", "头盔(防碎石)", 350, people)
        if climb > 2500:
            add("🏔️ 高海拔", "红景天等高原药品", 50, people, "缓慢行进")
        if dist > 20:
            add("⏫ 长途加强", "备用压缩饼干", 200, max(1, people), "应急")
            add("⏫ 长途加强", "备用袜子(干)", 80, max(2, people), "保持干燥")

        return rows

    # ─── 驾车生成 ───
    def _build_driving(self):
        terrain   = self.get_val("terrain", "铺装公路")
        difficulty = self.get_val("difficulty", "中等")
        nights   = self.si(self.get_val("nights"), 0)
        temp_lo  = self.sf(self.get_val("temp_low"), 10)
        rain     = self.sf(self.get_val("rain"), 0)
        people   = self.si(self.get_val("people"), 4)

        rows = []
        def add(cat, item, qty=1, note=""):
            rows.append({"cat": cat, "item": item, "w": None, "qty": qty, "note": note, "carried": False})

        for item, w, qty, note in self.DRIVING["🚗 车辆装备"]:
            add("🚗 车辆装备", item, qty, note)
        for item, w, qty, note in self.DRIVING["🔧 随车工具"]:
            add("🔧 随车工具", item, qty, note)
        for item, w, qty, note in self.DRIVING["💧 油液补给"]:
            add("💧 油液补给", item, qty, note)

        cloth = self.CLOTHING["🧥 服装系统"]
        for item, w, qty, note in cloth:
            add("🧥 服装", item, qty, note)

        if nights >= 1:
            for item, w, qty, note in self.HIKING["⛺ 露营系统"][:4]:
                add("⛺ 露营", item, qty, note)
            add("⛺ 露营", "便携炉具+气罐", 1, "野外热食")
            if nights >= 2:
                add("⛺ 露营", "折叠桌椅", 1, "休息区")
                add("⛺ 露营", "天幕+地钉", 1, "遮阳挡雨")

        food = self.FOOD_DRINK["🍖 饮食系统"]
        for item, w, qty, note in food:
            if "饮用水" in item:
                add("🍖 饮食", item, max(3, people), f"{nights+1}天量")
            else:
                add("🍖 饮食", item, max(1, people // 2), note)

        nav = self.HIKING["🧭 导航通讯"]
        for item, w, qty, note in nav[:4]:
            add("📡 导航", item, qty, note)
        if nights >= 1:
            add("📡 导航", "卫星通讯器/北斗海聊", 1, "偏远地区必备")

        for item, w, qty, note in self.HIKING["🩹 急救医疗"][:6]:
            add("🩹 急救", item, qty, note)

        for item, w, qty, note in self.HIKING["🔧 工具配件"][:5]:
            add("🔧 工具", item, qty, note)

        for item, w, qty, note in self.HIKING["🧭 导航通讯"][5:]:
            add("🔋 电源", item, qty, note)

        gear = self.HIKING["💼 个人物品"]
        for item, w, qty, note in gear:
            add("👤 个人", item, qty, note)

        if terrain != "铺装公路":
            add("🛠️ 路况额外", "拖车绳(重型)", 2, "主车+被拖")
            add("🛠️ 路况额外", "工兵铲", 1, "挖泥/垫轮")
            add("🛠️ 路况额外", "防滑链", 1, "雨雪必备")

        if difficulty in ("中等", "硬核"):
            add("⚡ 进阶", "绞盘", 1, "必带")
            add("⚡ 进阶", "Hi-Lift千斤顶", 2, "脱困神器")

        add("🏥 安全", "急救毯(太空毯)", 1, f"{people}人")
        add("🏥 安全", "灭火器(额外)", 1, "后备箱")
        if temp_lo < 5:
            add("🧊 低温防护", "防冻液补充", 2, "升浓度")
            add("🧊 低温防护", "-35号柴油", 30, "低温用")
        if rain > 30:
            add("🌧️ 雨天", "防水袋(电子设备)", people, "")
            add("🌧️ 雨天", "新雨刮片", 1, "")

        return rows

    def generate(self):
        try:
            if self.current_mode == "hiking":
                rows = self._build_hiking()
            else:
                rows = self._build_driving()

            dest = self.get_val("destination", "未知")
            mode_label = "🥾 徒步" if self.current_mode == "hiking" else "🚗 驾车"
            terrain = self.get_val("terrain", "")

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.items_data = rows
            self.checklist = [False] * len(rows)

            for i, r in enumerate(rows):
                w_str = str(r["w"]) if r["w"] is not None else "整备"
                self.tree.insert("", "end", iid=str(i), values=(
                    r["cat"], r["item"], w_str, r["qty"], ""
                ))

            cats = {}
            for r in rows:
                c = r["cat"]
                cats[c] = cats.get(c, 0) + 1

            self.log(f"✅ {mode_label}生成「{dest}」清单 | {len(rows)}项")
            for c, n in cats.items():
                self.log(f"   {c} {n}项")
        except Exception as e:
            messagebox.showerror("错误", f"生成清单失败:\n{type(e).__name__}: {e}")

    def _toggle_carry(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = int(self.tree.identify_column(event.x).replace("#", "")) - 1
        if col != 4:
            return
        iid = self.tree.identify_row(event.y)
        if iid == "":
            return
        idx = self.tree.index(iid)
        if 0 <= idx < len(self.checklist):
            self.checklist[idx] = not self.checklist[idx]
            mark = "✅" if self.checklist[idx] else ""
            self.tree.set(iid, "已携带", mark)

    def select_all(self):
        for i in range(len(self.checklist)):
            self.checklist[i] = True
            self.tree.set(str(i), "已携带", "✅")

    def deselect_all(self):
        for i in range(len(self.checklist)):
            self.checklist[i] = False
            self.tree.set(str(i), "已携带", "")

    def calc_weight(self):
        if self.current_mode == "driving":
            messagebox.showinfo("驾车模式", "驾车模式下装备由车辆运输，无需背负计算。\n\n建议检查车辆装载是否均衡，物品固定牢靠。")
            return

        total_weight = 0
        cat_weight = {}
        detail_lines = []

        for i, carried in enumerate(self.checklist):
            if carried and i < len(self.items_data):
                item = self.items_data[i]
                w = item["w"] or 0
                total = w * item["qty"]
                total_weight += total

                cat = item["cat"]
                cat_weight[cat] = cat_weight.get(cat, 0) + total
                detail_lines.append((item["item"], w, item["qty"], total))

        people = self.si(self.get_val("people"), 1)

        self.weight_detail.config(state="normal")
        self.weight_detail.delete("1.0", "end")

        if detail_lines:
            self.weight_detail.insert("end", "📋 已选装备重量明细:\n", "bold")
            for name, w, qty, total in detail_lines:
                unit = "g" if total < 1000 else "kg"
                div = 1 if total < 1000 else 1000
                self.weight_detail.insert("end", f"  {name} ×{qty} = {total/div:.0f}{unit}\n")

            self.weight_detail.insert("end", f"\n✨ 已选总重: {total_weight/1000:.1f} kg\n", "green")
            self.weight_detail.insert("end", f"👤 人均背负: {total_weight/1000/people:.1f} kg/人\n", "green")

            if total_weight / 1000 / people > 15:
                self.weight_detail.insert("end", "\n⚠️ 人均负重超15kg，建议精简装备\n", "warn")
            elif total_weight / 1000 / people > 10:
                self.weight_detail.insert("end", "\n💡 人均10-15kg，注意合理分配\n", "warn")
            else:
                self.weight_detail.insert("end", "\n✅ 负重合理，保持轻松出行\n", "green")

            self.weight_detail.insert("end", "\n📂 分类重量:\n", "bold")
            for cat, w in sorted(cat_weight.items(), key=lambda x: -x[1]):
                pct = w * 100 / total_weight if total_weight else 0
                self.weight_detail.insert("end", f"  {cat}: {w/1000:.1f}kg ({pct:.0f}%)\n")
        else:
            self.weight_detail.insert("end", "请先生成清单并勾选装备")

        self.weight_detail.config(state="disabled")
        self.weight_main.config(text=f"⛰️ 已选装备: {len([c for c in self.checklist if c])}项 | "
                                     f"总重 {total_weight/1000:.1f} kg")

        self.weight_detail.tag_config("bold", font=("", 10, "bold"))
        self.weight_detail.tag_config("green", foreground=GREEN)
        self.weight_detail.tag_config("warn", foreground=YELLOW)

    def export_csv(self):
        if not self.checklist or not any(self.checklist):
            messagebox.showwarning("提示", "请先生成清单并至少勾选一项")
            return

        dest = self.get_val("destination", "户外")
        mode = "徒步" if self.current_mode == "hiking" else "越野"
        filename = f"{mode}_装备清单_{dest}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["模式", "目的地", "日期", "类别", "装备名称", "重量(克)", "数量", "是否携带"])
            today = datetime.now().strftime("%Y-%m-%d")
            for i, carried in enumerate(self.checklist):
                if carried and i < len(self.items_data):
                    item = self.items_data[i]
                    writer.writerow([
                        mode, dest, today,
                        item["cat"], item["item"],
                        item["w"] or "", item["qty"], "✓"
                    ])

        abspath = os.path.abspath(filename)
        self.log(f"📤 已导出 {sum(self.checklist)} 项到 {abspath}")
        messagebox.showinfo("导出成功", f"清单已保存到:\n{abspath}")


if __name__ == "__main__":
    root = tk.Tk()
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"+{(sw-1300)//2}+{(sh-900)//2}")
    app = OutdoorChecklist(root)
    root.mainloop()