import streamlit as st
import matplotlib.pyplot as plt
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

# 画面設定
st.set_page_config(page_title="LapGraph-App", layout="centered")

# 日本語表示のための設定（部品に頼らず標準フォントを指定）
plt.rcParams['font.family'] = 'sans-serif' # 環境に合わせたフォントを自動選択

# --- UIデザイン ---
st.markdown("""
    <style>
    .stDownloadButton > button {
        background-color: #00FF7F !important; color: #000000 !important;
        font-weight: bold !important; width: 100% !important; border-radius: 8px !important;
    }
    .stButton > button {
        background-color: #4B6CFF !important; color: white !important;
        font-weight: bold !important; width: 100% !important; border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("LapGraph-App")

# 種目設定
EVENT_CONFIG = {
    "1500m": [400, 800, 1200, 1500],
    "3000m": [400, 800, 1200, 1600, 2000, 2400, 2800],
    "5000m": [400, 800, 1200, 1600, 2000, 2400, 2800, 3200, 3600, 4000, 4400, 4800],
    "10000m": [i for i in range(400, 10001, 400)]
}

event_type = st.selectbox("種目を選択してください", list(EVENT_CONFIG.keys()))
title = st.text_input("グラフのタイトルを入力", value="")

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
        
        # --- 画像作成 ---
        fig = plt.figure(figsize=(11, 8.5), facecolor='white')
        
        # ① 表（上部）
        ax_table = fig.add_axes([0.1, 0.60, 0.8, 0.25]) 
        ax_table.axis('off')
        table_data = [["Distance(m)", "Time(s)"]] # 念のため英語併記
        for d, l in zip(distances, laps):
            table_data.append([f"{d}", f"{l}"])
            
        table = ax_table.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(12) 
        table.scale(1.2, 2.2)
        ax_table.set_title(f"Lap Table: {event_type}", fontsize=16, pad=20)

        # ② グラフ（下部）
        ax_graph = fig.add_axes([0.1, 0.18, 0.8, 0.35]) 
        ax_graph.plot(distances, laps, color='red', linestyle='-', marker="o", label='Time')
        ax_graph.set_title(title if title else "Lap Graph", fontsize=18, pad=15)
        ax_graph.set_xlabel('Distance (m)', fontsize=14)
        ax_graph.set_ylabel('Time (s)', fontsize=14)
        ax_graph.set_xticks(distances)
        ax_graph.grid(True, linestyle='--', linewidth=0.5)
        ax_graph.legend()

        # ③ 平均値表示
        avg_text = f"Average Lap: {avg_val:.2f} s"
        fig.text(0.1, 0.08, avg_text, fontsize=14, weight='bold')

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
        c.rect(0, height - 10*mm, width, 10*mm, fill=1, stroke=0)
        c.drawImage(ImageReader(img_io), 5*mm, 5*mm, width=width-10*mm, height=height-20*mm, preserveAspectRatio=True)
        c.showPage()
        c.save()
        
        save_name = f"{title}.pdf" if title else "Result.pdf"
        st.download_button(label="PDFを保存する", data=pdf_io.getvalue(), file_name=save_name, mime="application/pdf")
    else:
        st.warning("すべてのラップを入力してください。")
