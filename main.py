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
    # ① Matplotlib（グラフ）用の設定
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = font_prop.get_name()
    
    # ② ReportLab（PDF）用の設定 ← ここが化け対策の肝！
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
        
        # グラフ作成（日本語設定済み）
        fig = plt.figure(figsize=(11, 8.5), facecolor='white')
        ax_table = fig.add_axes([0.1, 0.60, 0.8, 0.25]) 
        ax_table.axis('off')
        table_data = [["距離 (m)", "通過タイム (s)"]]
        for d, l in zip(distances, laps):
            table_data.append([f"{d}", f"{l}"])
            
        table = ax_table.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(12) 
        table.scale(1.2, 2.2)
        ax_table.set_title(f"通過タイム表_{event_type}", fontsize=16, pad=20)

        ax_graph = fig.add_axes([0.1, 0.18, 0.8, 0.35]) 
        ax_graph.plot(distances, laps, color='red', linestyle='-', marker="o", label='タイム')
        ax_graph.set_title(title if title else "ラップグラフ", fontsize=18, pad=15)
        ax_graph.set_xlabel('距離 (m)', fontsize=14)
        ax_graph.set_ylabel('時間 (s)', fontsize=14)
        ax_graph.set_xticks(distances)
        ax_graph.grid(True, linestyle='--', linewidth=0.5)
        ax_graph.legend()

        avg_text = f"全区間の平均タイム： {avg_val:.2f} 秒"
        fig.text(0.1, 0.08, avg_text, fontsize=14, weight='bold')

        img_io = io.BytesIO()
        fig.savefig(img_io, format='png', dpi=300, bbox_inches='tight')
        img_io.seek(0)
        
        st.pyplot(fig)
        plt.close(fig)

        # --- PDF生成（文字化け対策版） ---
        pdf_io = io.BytesIO()
        c = canvas.Canvas(pdf_io, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # フォントを指定
        c.setFont(font_name, 12)
        
        # ヘッダー背景
        c.setFillColorRGB(0.31, 0.50, 0.74) 
        c.rect(0, height - 15*mm, width, 15*mm, fill=1, stroke=0)
        
        # タイトル（日本語）
        c.setFillColorRGB(1, 1, 1)
        c.setFont(font_name, 16)
        c.drawString(10*mm, height - 10*mm, f"記録証: {title if title else 'Lap Analysis'}")
        
        # グラフ画像を貼り付け
        c.drawImage(ImageReader(img_io), 5*mm, 10*mm, width=width-10*mm, height=height-30*mm, preserveAspectRatio=True)
        
        c.showPage()
        c.save()
        
        save_name = f"{title}.pdf" if title else "Result.pdf"
        st.download_button(label="PDFを保存する", data=pdf_io.getvalue(), file_name=save_name, mime="application/pdf")
    else:
        st.warning("すべてのラップを入力してください。")import streamlit as st
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
FONT_PATH = 'font.ttf' # GitHubにアップしたフォントファイル名

if os.path.exists(FONT_PATH):
    # Matplotlib用
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = font_prop.get_name()
    # ReportLab用（PDFの文字化け防止）
    pdfmetrics.registerFont(TTFont('JapaneseFont', FONT_PATH))
else:
    st.warning("フォントファイル(font.ttf)が見つかりません。英語表記になります。")

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
        
        fig = plt.figure(figsize=(11, 8.5), facecolor='white')
        
        # ① 表（日本語復活！）
        ax_table = fig.add_axes([0.1, 0.60, 0.8, 0.25]) 
        ax_table.axis('off')
        table_data = [["距離 (m)", "通過タイム (s)"]]
        for d, l in zip(distances, laps):
            table_data.append([f"{d}", f"{l}"])
            
        table = ax_table.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(12) 
        table.scale(1.2, 2.2)
        ax_table.set_title(f"通過タイム表_{event_type}", fontsize=16, pad=20, fontproperties=font_prop if os.path.exists(FONT_PATH) else None)

        # ② グラフ（日本語復活！）
        ax_graph = fig.add_axes([0.1, 0.18, 0.8, 0.35]) 
        ax_graph.plot(distances, laps, color='red', linestyle='-', marker="o", label='タイム')
        ax_graph.set_title(title if title else "ラップグラフ", fontsize=18, pad=15, fontproperties=font_prop if os.path.exists(FONT_PATH) else None)
        ax_graph.set_xlabel('距離 (m)', fontsize=14, fontproperties=font_prop if os.path.exists(FONT_PATH) else None)
        ax_graph.set_ylabel('時間 (s)', fontsize=14, fontproperties=font_prop if os.path.exists(FONT_PATH) else None)
        ax_graph.set_xticks(distances)
        ax_graph.grid(True, linestyle='--', linewidth=0.5)
        ax_graph.legend(prop=font_prop if os.path.exists(FONT_PATH) else None)

        # ③ 平均値
        avg_text = f"全区間の平均タイム： {avg_val:.2f} 秒"
        fig.text(0.1, 0.08, avg_text, fontsize=14, weight='bold', fontproperties=font_prop if os.path.exists(FONT_PATH) else None)

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
