import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 画面設定
st.set_page_config(page_title="LapGraph-App", layout="centered")

# --- 日本語フォントの設定 ---
FONT_PATH = 'font.ttf' 

if os.path.exists(FONT_PATH):
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = font_prop.get_name()
    pdfmetrics.registerFont(TTFont('JapaneseFont', FONT_PATH))
    font_name = 'JapaneseFont'
else:
    st.warning("フォントファイルが見つかりません。")
    font_name = 'Helvetica'

st.title("LapGraph-App")

EVENT_CONFIG = {
    "1500m": [400, 800, 1200, 1500],
    "3000m": [400, 800, 1200, 1600, 2000, 2400, 2800],
    "5000m": [400, 800, 1200, 1600, 2000, 2400, 2800, 3200, 3600, 4000, 4400, 4800],
    "10000m": [i for i in range(400, 10001, 400)]
}

event_type = st.selectbox("種目を選択してください", list(EVENT_CONFIG.keys()))
title = st.text_input("グラフのタイトル（大会名など）を入力", value="")

distances = EVENT_CONFIG[event_type]
laps = []

st.subheader("ラップタイム入力 (秒)")
cols = st.columns(2)
for i, dist in enumerate(distances):
    with cols[i % 2]:
        val = st.text_input(f"{dist}m", key=f"lap_{dist}", placeholder="00.0")
        if val:
            try: laps.append(float(val))
            except: st.error("数字を入れてください")

if st.button("グラフとPDFを作成"):
    if len(laps) == len(distances):
        avg_val = sum(laps) / len(laps)
        
        # --- 描画開始 ---
        fig = plt.figure(figsize=(11, 8.5), facecolor='white')
        
        # ① 表（上半分）の文字化け対策
        ax_table = fig.add_axes([0.1, 0.55, 0.8, 0.3]) 
        ax_table.axis('off')
        table_data = [["距離 (m)", "通過タイム (s)"]]
        for d, l in zip(distances, laps):
            table_data.append([f"{d}", f"{l}"])
            
        table = ax_table.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.2, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.8)
        
        # 【重要】表の中の文字すべてにフォントを適用
        if os.path.exists(FONT_PATH):
            for (row, col), cell in table.get_celld().items():
                cell.set_fontproperties(font_prop)
            ax_table.set_title(f"通過タイム表: {event_type}", fontsize=15, pad=10, fontproperties=font_prop)
        
        # ② グラフ（下半分）の軸調整
        ax_graph = fig.add_axes([0.1, 0.12, 0.8, 0.32]) 
        ax_graph.plot(distances, laps, color='red', linestyle='-', marker="o", label='タイム')
        
        # 縦軸を40〜90に固定
        ax_graph.set_ylim(40, 90)
        
        if os.path.exists(FONT_PATH):
            ax_graph.set_title(title if title else "通過タイムグラフ", fontsize=16, fontproperties=font_prop)
            ax_graph.set_xlabel('距離 (m)', fontsize=12, fontproperties=font_prop)
            ax_graph.set_ylabel('時間 (s)', fontsize=12, fontproperties=font_prop)
            ax_graph.legend(prop=font_prop)
        
        ax_graph.set_xticks(distances)
        ax_graph.grid(True, linestyle='--', linewidth=0.5)

        # 平均表示
        avg_text = f"平均ラップ: {avg_val:.2f}秒"
        fig.text(0.1, 0.05, avg_text, fontsize=12, fontproperties=font_prop if os.path.exists(FONT_PATH) else None)

        # 画像化
        img_io = io.BytesIO()
        fig.savefig(img_io, format='png', dpi=300, bbox_inches='tight')
        img_io.seek(0)
        
        st.pyplot(fig)
        plt.close(fig)

        # --- PDF生成 ---
        pdf_io = io.BytesIO()
        c = canvas.Canvas(pdf_io, pagesize=landscape(A4))
        width, height = landscape(A4)
        c.setFillColorRGB(0.31, 0.50, 0.74) 
        c.rect(0, height - 15*mm, width, 15*mm, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont(font_name, 16)
        pdf_title = title if title else "通過タイムグラフ"
        c.drawString(10*mm, height - 10*mm, f"{pdf_title} ({event_type})")
        c.drawImage(ImageReader(img_io), 5*mm, 5*mm, width=width-10*mm, height=height-25*mm, preserveAspectRatio=True)
        c.showPage()
        c.save()
        
        st.download_button(label="PDFを保存する", data=pdf_io.getvalue(), file_name=f"{title if title else 'LapGraph'}.pdf", mime="application/pdf")
    else:
        st.warning("すべてのラップを入力してください。")
