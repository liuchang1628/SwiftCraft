from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Polygon


ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "images" / "dashboard"
PDF_DIR = ROOT / "exports" / "pdf"
IMG_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

BG = "#F3F6F9"
NAV = "#0B2A55"
CARD = "#FFFFFF"
TEXT = "#1D2129"
SUB = "#4E5969"
BLUE = "#165DFF"
RED = "#F53F3F"
GREEN = "#00B42A"
ORANGE = "#FF7D00"
GRID = "#E5E6EB"


def pct(v, d=2):
    return f"{v * 100:.{d}f}%"


def signed_pct(v, d=2):
    return f"{v * 100:+.{d}f}%"


def load_csv(name):
    return pd.read_csv(ROOT / name)


def setup_page(title, subtitle):
    fig = plt.figure(figsize=(16, 10), dpi=160, facecolor=BG)
    fig.subplots_adjust(0, 0, 1, 1)
    nav = fig.add_axes([0.015, 0.03, 0.12, 0.94])
    nav.set_facecolor(NAV)
    nav.set_xticks([])
    nav.set_yticks([])
    for s in nav.spines.values():
        s.set_visible(False)
    nav.text(0.14, 0.94, "SwiftCart", color="white", fontsize=18, weight="bold", transform=nav.transAxes)
    nav.text(0.14, 0.90, "Growth BI", color="#BFD7FF", fontsize=9, transform=nav.transAxes)

    ax = fig.add_axes([0.16, 0.90, 0.82, 0.08])
    ax.axis("off")
    ax.text(0, 0.72, title, fontsize=24, weight="bold", color=TEXT, transform=ax.transAxes)
    ax.text(0, 0.22, subtitle, fontsize=11, color=SUB, transform=ax.transAxes)
    return fig


def card(fig, rect, title=None):
    ax = fig.add_axes(rect)
    ax.set_facecolor(CARD)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    patch = FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.012,rounding_size=0.03",
        linewidth=0,
        facecolor=CARD,
        transform=ax.transAxes,
        zorder=-1,
    )
    ax.add_patch(patch)
    if title:
        ax.text(0.04, 0.93, title, fontsize=13, weight="bold", color=TEXT, transform=ax.transAxes)
    return ax


def save(fig, name):
    png = IMG_DIR / f"{name}.png"
    pdf = PDF_DIR / f"{name}.pdf"
    fig.savefig(png, facecolor=BG, bbox_inches="tight", pad_inches=0.05)
    with PdfPages(pdf) as pp:
        pp.savefig(fig, facecolor=BG, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def draw_kpi(ax, title, value, note, color=BLUE):
    ax.axis("off")
    ax.text(0.06, 0.72, title, fontsize=10, color=SUB, transform=ax.transAxes)
    ax.text(0.06, 0.38, value, fontsize=20, color=color, weight="bold", transform=ax.transAxes)
    ax.text(0.06, 0.15, note, fontsize=9, color=SUB, transform=ax.transAxes)


def page_overview():
    exec_df = load_csv("mart_01_executive_summary.csv")
    exec_df["mock_date"] = pd.to_datetime(exec_df["mock_date"])
    fig = setup_page("SwiftCart 增长诊断系统", "总览识别：流量基本稳定，但异常期首单支付率与 D1 留存率同步下探")

    kpis = [
        ("新用户总数", "479,680", "规模整体稳定", BLUE),
        ("首单支付率", "4.85%", "异常明显下探", RED),
        ("结算→支付转化率", "67.21%", "后段核心断点", BLUE),
        ("首单客单价", "¥99.84", "价格侧平稳", TEXT),
        ("首单GMV", "¥16,474,526", "受转化波动影响", TEXT),
        ("D1留存率", "16.60%", "用户质量承压", RED),
        ("AB首单绝对提升", "+15.43%", "ALL全量口径", GREEN),
    ]
    for i, item in enumerate(kpis):
        x = 0.16 + i * 0.118
        ax = card(fig, [x, 0.76, 0.105, 0.12])
        draw_kpi(ax, *item)

    ax1 = card(fig, [0.16, 0.39, 0.40, 0.32], "每日新用户与首单支付率")
    ax1b = ax1.twinx()
    ax1.bar(exec_df["mock_date"], exec_df["daily_new_users"], color="#8DBBFF", width=0.72, label="新用户数")
    ax1b.plot(exec_df["mock_date"], exec_df["first_order_pay_rate"], color=TEXT, lw=2.4, marker="o", ms=3, label="首单支付率")
    ax1.axvspan(pd.Timestamp("2026-04-21"), pd.Timestamp("2026-04-26"), color=RED, alpha=0.12)
    ax1.grid(axis="y", color=GRID, lw=0.6)
    ax1.tick_params(axis="x", rotation=30, labelsize=8)
    ax1.tick_params(axis="y", labelsize=8, colors=SUB)
    ax1b.tick_params(axis="y", labelsize=8, colors=SUB)
    ax1b.yaxis.set_major_formatter(lambda x, pos: f"{x*100:.0f}%")
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))

    ax2 = card(fig, [0.58, 0.39, 0.40, 0.32], "每日 D1 留存率趋势")
    ax2.plot(exec_df["mock_date"], exec_df["d1_retention_rate"], color=BLUE, lw=2.5, marker="o", ms=3)
    ax2.axvspan(pd.Timestamp("2026-04-21"), pd.Timestamp("2026-04-26"), color=RED, alpha=0.12)
    ax2.grid(axis="y", color=GRID, lw=0.6)
    ax2.tick_params(axis="x", rotation=30, labelsize=8)
    ax2.tick_params(axis="y", labelsize=8, colors=SUB)
    ax2.yaxis.set_major_formatter(lambda x, pos: f"{x*100:.0f}%")
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=5))

    funnel = load_csv("mart_02_overall_funnel.csv")
    anomaly = funnel[funnel["period"].str.startswith("2")].iloc[0]
    vals = [anomaly[c] for c in ["exposure_uv", "click_uv", "cart_uv", "checkout_uv", "paid_uv"]]
    names = ["曝光", "点击", "加购", "结算", "支付"]
    ax3 = card(fig, [0.16, 0.08, 0.38, 0.25], "整体转化漏斗")
    maxv = max(vals)
    for i, (name, val) in enumerate(zip(names, vals)):
        width = val / maxv * 0.84
        y = 0.82 - i * 0.16
        ax3.add_patch(FancyBboxPatch((0.08, y - 0.05), width, 0.09, boxstyle="round,pad=0.01", facecolor=BLUE, alpha=0.88 - i * 0.1, edgecolor="none", transform=ax3.transAxes))
        ax3.text(0.10, y - 0.005, name, color="white", weight="bold", transform=ax3.transAxes)
        ax3.text(0.94, y - 0.005, f"{int(val):,}", ha="right", color=TEXT, transform=ax3.transAxes)

    ax4 = card(fig, [0.57, 0.08, 0.41, 0.25], "关键发现")
    ax4.axis("off")
    findings = [
        "异常期流量未同步断崖，问题更偏向转化质量。",
        "信息流渠道A是后段支付率下降的主要贡献渠道。",
        "结算→支付是最直接的交易断点。",
        "Top20 缺货和北京/杭州城市风险共同构成供给解释链。"
    ]
    for i, text in enumerate(findings):
        ax4.text(0.06, 0.78 - i * 0.18, f"• {text}", fontsize=12, color=TEXT, transform=ax4.transAxes)
    save(fig, "01_overview")


def page_channel():
    df = load_csv("mart_03_funnel_channel.csv")
    fig = setup_page("SwiftCart 渠道与异动诊断", "渠道责任：定位首单支付率与 D1 留存下探的主要贡献渠道")
    data = [
        ("信息流渠道A", 194625, 0.03203, 0.15932, -0.0785),
        ("自然搜索", 139318, 0.03450, 0.17099, 0.0047),
        ("达人种草", 137997, 0.03451, 0.17067, -0.0019),
    ]
    for i, (ch, users, pay, d1, delta) in enumerate(data):
        ax = card(fig, [0.16 + i * 0.27, 0.72, 0.24, 0.16])
        color = RED if ch == "信息流渠道A" else BLUE
        draw_kpi(ax, ch, f"{users:,}", f"首单支付率 {pct(pay)} / D1 {pct(d1)}", color)

    ax1 = card(fig, [0.16, 0.36, 0.25, 0.30], "渠道首单支付率")
    chs = [d[0] for d in data][::-1]
    rates = [d[2] for d in data][::-1]
    colors = [RED if c == "信息流渠道A" else BLUE for c in chs]
    ax1.barh(chs, rates, color=colors, height=0.42)
    ax1.xaxis.set_major_formatter(lambda x, pos: f"{x*100:.0f}%")
    ax1.grid(axis="x", color=GRID, lw=0.6)

    ax2 = card(fig, [0.44, 0.36, 0.25, 0.30], "渠道 D1 留存率")
    d1s = [d[3] for d in data][::-1]
    ax2.barh(chs, d1s, color=colors, height=0.42)
    ax2.xaxis.set_major_formatter(lambda x, pos: f"{x*100:.0f}%")
    ax2.grid(axis="x", color=GRID, lw=0.6)

    ax3 = card(fig, [0.72, 0.36, 0.26, 0.30], "结算→支付变化")
    deltas = [d[4] for d in data][::-1]
    ax3.barh(chs, deltas, color=[RED if x < 0 else GREEN for x in deltas], height=0.42)
    ax3.axvline(0, color=GRID, lw=1)
    ax3.xaxis.set_major_formatter(lambda x, pos: f"{x*100:.0f}%")
    ax3.grid(axis="x", color=GRID, lw=0.6)

    ax4 = card(fig, [0.16, 0.08, 0.82, 0.22], "诊断结论")
    ax4.axis("off")
    for i, text in enumerate([
        "信息流渠道A用户规模最大，但首单支付率与 D1 留存表现最差。",
        "后段结算→支付变化为 -7.85%，明显弱于自然搜索与达人种草。",
        "渠道问题不是单纯流量规模问题，而是承接流量的交易质量问题。"
    ]):
        ax4.text(0.04, 0.72 - i * 0.22, f"• {text}", fontsize=13, color=TEXT, transform=ax4.transAxes)
    save(fig, "02_channel")


def page_funnel():
    overall = load_csv("mart_02_overall_funnel.csv")
    normal = overall[overall["period"].str.startswith("1")].iloc[0]
    anomaly = overall[overall["period"].str.startswith("2")].iloc[0]
    fig = setup_page("SwiftCart 漏斗与交易后段诊断", "漏斗下钻：定位异常期最大的转化断点")

    stages = [
        ("曝光→点击", normal["exposure_to_click_rate"], anomaly["exposure_to_click_rate"]),
        ("点击→加购", normal["click_to_cart_rate"], anomaly["click_to_cart_rate"]),
        ("加购→结算", normal["cart_to_checkout_rate"], anomaly["cart_to_checkout_rate"]),
        ("结算→支付", normal["checkout_to_paid_rate"], anomaly["checkout_to_paid_rate"]),
    ]
    for i, (name, pre, ano) in enumerate(stages):
        ax = card(fig, [0.16 + i * 0.205, 0.73, 0.18, 0.15])
        delta = ano - pre
        draw_kpi(ax, name, signed_pct(delta), f"{pct(pre)} → {pct(ano)}", RED if delta < 0 else GREEN)

    ax1 = card(fig, [0.16, 0.34, 0.38, 0.32], "异常期整体 5 步漏斗")
    vals = [anomaly[c] for c in ["exposure_uv", "click_uv", "cart_uv", "checkout_uv", "paid_uv"]]
    names = ["曝光", "点击", "加购", "结算", "支付"]
    maxv = max(vals)
    for i, (name, val) in enumerate(zip(names, vals)):
        top = 0.90 - i * 0.15
        width = val / maxv * 0.82
        poly = Polygon([[0.09, top], [0.09 + width, top], [0.09 + width - 0.04, top - 0.10], [0.13, top - 0.10]], closed=True, transform=ax1.transAxes, color=BLUE, alpha=0.90 - i * 0.10)
        ax1.add_patch(poly)
        ax1.text(0.12, top - 0.07, name, color="white", weight="bold", transform=ax1.transAxes)
        ax1.text(0.95, top - 0.07, f"{int(val):,}", ha="right", color=TEXT, transform=ax1.transAxes)

    ax2 = card(fig, [0.58, 0.34, 0.40, 0.32], "阶段转化率 normal vs anomaly")
    x = range(len(stages))
    ax2.bar([i - 0.18 for i in x], [s[1] for s in stages], width=0.35, color=BLUE, label="正常期")
    ax2.bar([i + 0.18 for i in x], [s[2] for s in stages], width=0.35, color=RED, label="异常期")
    ax2.set_xticks(list(x), [s[0] for s in stages], rotation=15)
    ax2.yaxis.set_major_formatter(lambda y, pos: f"{y*100:.0f}%")
    ax2.grid(axis="y", color=GRID, lw=0.6)
    ax2.legend(frameon=False)

    ax3 = card(fig, [0.16, 0.08, 0.82, 0.20], "结论")
    ax3.axis("off")
    for i, text in enumerate([
        "异常并非均匀发生在所有漏斗层级，最大断点集中在结算→支付。",
        "交易后段下滑与供给缺货页面的 Top20 阻断证据一致。",
        "后续优化不应只看投放，应优先修复结算页缺货提示与替代推荐。"
    ]):
        ax3.text(0.04, 0.70 - i * 0.24, f"• {text}", fontsize=13, color=TEXT, transform=ax3.transAxes)
    save(fig, "03_funnel")


def page_supply():
    daily = load_csv("mart_04_daily_city_oos.csv")
    daily["mock_date"] = pd.to_datetime(daily["mock_date"])
    daily["period"] = daily["mock_date"].between("2026-04-21", "2026-04-26").map({True: "异常期", False: "正常期"})
    summary = daily.groupby("period").agg({"checkout_uv": "sum", "paid_uv": "sum", "top20_checkout_uv": "sum", "top20_paid_uv": "sum"})
    summary["pay"] = summary["paid_uv"] / summary["checkout_uv"]
    summary["oos"] = 1 - summary["top20_paid_uv"] / summary["top20_checkout_uv"]
    city = daily[daily["period"] == "异常期"].groupby("city").agg({"checkout_uv": "sum", "paid_uv": "sum", "top20_checkout_uv": "sum", "top20_paid_uv": "sum"})
    city["pay"] = city["paid_uv"] / city["checkout_uv"]
    city["oos"] = 1 - city["top20_paid_uv"] / city["top20_checkout_uv"]
    city = city.sort_values("oos", ascending=False)

    fig = setup_page("SwiftCart 库存供给证据链", "供给归因：Top20 缺货、城市集中与客诉反馈是否能解释支付断点")
    ax0 = card(fig, [0.16, 0.72, 0.82, 0.16])
    ax0.axis("off")
    ax0.text(0.03, 0.58, f"Top20缺货率：{pct(summary.loc['正常期','oos'])} → {pct(summary.loc['异常期','oos'])}", fontsize=20, weight="bold", color=RED, transform=ax0.transAxes)
    ax0.text(0.42, 0.58, "北京Top20缺货率：49.44%", fontsize=18, weight="bold", color=RED, transform=ax0.transAxes)
    ax0.text(0.70, 0.58, "杭州Top20缺货率：48.22%", fontsize=18, weight="bold", color=RED, transform=ax0.transAxes)
    ax0.text(0.03, 0.20, "目标切片：信息流渠道A × 北京/杭州 × Top20 商品支付率仅约 16%", fontsize=12, color=SUB, transform=ax0.transAxes)

    ax1 = card(fig, [0.16, 0.36, 0.27, 0.30], "大盘支付率 vs Top20缺货率")
    labels = ["正常期", "异常期"]
    ax1.bar([0, 1], [summary.loc["正常期", "pay"], summary.loc["异常期", "pay"]], color=BLUE, width=0.32, label="支付率")
    ax1.bar([0.36, 1.36], [summary.loc["正常期", "oos"], summary.loc["异常期", "oos"]], color=RED, width=0.32, label="Top20缺货率")
    ax1.set_xticks([0.18, 1.18], labels)
    ax1.yaxis.set_major_formatter(lambda y, pos: f"{y*100:.0f}%")
    ax1.legend(frameon=False)
    ax1.grid(axis="y", color=GRID, lw=0.6)

    ax2 = card(fig, [0.46, 0.36, 0.25, 0.30], "异常期城市 Top20 缺货率")
    ax2.barh(city.index[::-1], city["oos"][::-1], color=[RED if c in ["北京", "杭州"] else BLUE for c in city.index[::-1]])
    ax2.xaxis.set_major_formatter(lambda y, pos: f"{y*100:.0f}%")
    ax2.grid(axis="x", color=GRID, lw=0.6)

    ax3 = card(fig, [0.74, 0.36, 0.24, 0.30], "目标切片支付率")
    ax3.bar(["北京\n非Top20", "北京\nTop20", "杭州\n非Top20", "杭州\nTop20"], [0.6115, 0.1604, 0.5930, 0.1629], color=[BLUE, RED, BLUE, RED])
    ax3.yaxis.set_major_formatter(lambda y, pos: f"{y*100:.0f}%")
    ax3.grid(axis="y", color=GRID, lw=0.6)

    ax4 = card(fig, [0.16, 0.08, 0.82, 0.20], "证据链结论")
    ax4.axis("off")
    for i, text in enumerate([
        "Top20 爆款缺货率异常期明显上升，且北京/杭州最高。",
        "信息流渠道A在北京/杭州 Top20 商品上的支付率断崖，和缺货剧本高度吻合。",
        "缺货反馈率同步抬升，因此供给短缺是当前最完整的候选解释。"
    ]):
        ax4.text(0.04, 0.70 - i * 0.24, f"• {text}", fontsize=13, color=TEXT, transform=ax4.transAxes)
    save(fig, "04_inventory")


def page_experiment():
    ab = load_csv("mart_08_ab_test_summary.csv")
    all_rows = ab[ab["city"] == "ALL"].set_index("experiment_group")
    control = all_rows.loc["Control", "conversion_rate"]
    treatment = all_rows.loc["Treatment", "conversion_rate"]
    city = ab[ab["city"] != "ALL"].pivot(index="city", columns="experiment_group", values="conversion_rate")
    city["lift"] = city["Treatment"] - city["Control"]
    city = city.sort_values("lift", ascending=False)

    fig = setup_page("SwiftCart 实验验证与行动建议", "AB 验证：智能替代品推荐 + 补偿券是否能挽回首单支付")
    kpis = [
        ("Control转化率", pct(control), "原策略", SUB),
        ("Treatment转化率", pct(treatment), "新策略", GREEN),
        ("首单绝对提升", signed_pct(treatment - control), "ALL全量口径", GREEN),
        ("Z-statistic", "18.63", "Two-Proportion Z-Test", BLUE),
        ("P-value", "< 0.001", "显著正向", GREEN),
    ]
    for i, item in enumerate(kpis):
        ax = card(fig, [0.16 + i * 0.164, 0.73, 0.145, 0.15])
        draw_kpi(ax, *item)

    ax1 = card(fig, [0.16, 0.37, 0.30, 0.30], "实验组 vs 对照组")
    ax1.bar(["Control", "Treatment"], [control, treatment], color=[SUB, GREEN], width=0.45)
    ax1.yaxis.set_major_formatter(lambda y, pos: f"{y*100:.0f}%")
    ax1.grid(axis="y", color=GRID, lw=0.6)

    ax2 = card(fig, [0.50, 0.37, 0.48, 0.30], "城市首单支付率绝对提升")
    ax2.barh(city.index[::-1], city["lift"][::-1], color=[GREEN if c in ["北京", "杭州"] else BLUE for c in city.index[::-1]])
    ax2.xaxis.set_major_formatter(lambda y, pos: f"{y*100:.0f}%")
    ax2.grid(axis="x", color=GRID, lw=0.6)

    ax3 = card(fig, [0.16, 0.08, 0.39, 0.22], "行动优先级")
    ax3.axis("off")
    for i, text in enumerate(["1. 北京/杭州 Top20 安全库存", "2. 结算页替代品推荐", "3. 信息流渠道A库存提示", "4. 缺货阻断用户补偿券"]):
        ax3.text(0.06, 0.76 - i * 0.18, text, fontsize=13, color=TEXT, transform=ax3.transAxes)

    ax4 = card(fig, [0.59, 0.08, 0.39, 0.22], "汇报边界")
    ax4.axis("off")
    for i, text in enumerate(["可以说：方案方向显著为正，建议灰度上线。", "不要说：库存是唯一根因。", "不要说：实验策略可以直接全量上线。"]):
        ax4.text(0.06, 0.72 - i * 0.22, f"• {text}", fontsize=13, color=TEXT, transform=ax4.transAxes)
    save(fig, "05_experiment_action")


def main():
    page_overview()
    page_channel()
    page_funnel()
    page_supply()
    page_experiment()
    print("Static dashboard PNG/PDF exports generated.")


if __name__ == "__main__":
    main()
