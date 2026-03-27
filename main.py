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
    # ① Matplotlib（グラフ全体）の基本フォントを設定
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = font_prop.get_name()
    
    # ② PDF用のフォント登録
    pdfmetrics.registerFont(TTFont('JapaneseFont', FONT_PATH))
    font_name = 'JapaneseFont'
else:
    st.warning("フォントファイル(font.ttf)が見つかりません。")
    font_name = 'Helvetica'

# --- UIデザイン ---
st.markdown("""
    <style>
    .stDownloadButton > button { background-color: #00FF7F !important; color: #000000 !important; font-weight: bold !important; width: 100% !important; }
    .stButton > button { background-color: #4B6CFF !important; color: white !important; font-weight: bold !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("LapGraph-App")

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
        
        # グラフ作成（個別にfontpropertiesを指定して確実に化けを防ぐ）
        fig, ax_graph = plt.subplots(figsize=(10, 5))
        
        # グラフ描画
        ax_graph.plot(distances, laps, color='red', linestyle='-', marker="o", label='タイム')
        
        # 各種テキストにフォントを適用
        if os.path.exists(FONT_PATH):
            ax_graph.set_title(title if title else "ラップグラフ", fontsize=16, fontproperties=font_prop)
            ax_graph.set_xlabel('距離 (m)', fontsize=12, fontproperties=font_prop)
            ax_graph.set_ylabel('時間 (s)', fontsize=12, fontproperties=font_prop)
            ax_graph.legend(prop=font_prop)
        else:
            ax_graph.set_title(title if title else "Lap Graph")
            ax_graph.set_xlabel('Distance (m)')
            ax_graph.set_ylabel('Time (s)')
            ax_graph.legend()

        ax_graph.set_xticks(distances)
        ax_graph.grid(True, linestyle='--', linewidth=0.5)

        # 平均タイムの表示
        avg_text = f"平均ラップ: {avg_val:.2f}s"
        st.write(f"### {avg_text}")
        
        # 画像として保存
        img_io = io.BytesIO()
        fig.savefig(img_io, format='png', dpi=300, bbox_inches='tight')
        img_io.seek(0)
        
        st.pyplot(fig)
        plt.close(fig)

        # --- PDF生成 ---
        pdf_io = io.BytesIO()
        c = canvas.Canvas(pdf_io, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # ヘッダー
        c.setFillColorRGB(0.31, 0.50, 0.74) 
        c.rect(0, height - 15*mm, width, 15*mm, fill=1, stroke=0)
        
        c.setFillColorRGB(1, 1, 1)
        c.setFont(font_name, 16)
        c.drawString(10*mm, height - 10*mm, f"通過タイムグラフ: {title if title else event_type}")
        
        # メイン画像（グラフ）を中央に
        c.drawImage(ImageReader(img_io), 10*mm, 10*mm, width=width-20*mm, height=height-35*mm, preserveAspectRatio=True)
        
        c.showPage()
        c.save()
        
        save_name = f"{title}.pdf" if title else "Result.pdf"
        st.download_button(label="PDFを保存する", data=pdf_io.getvalue(), file_name=save_name, mime="application/pdf")
    else:
        st.warning("すべてのラップを入力してください。")
