import streamlit as st
import matplotlib.pyplot as plt
import japanize_kame
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

# 画面設定：ブラウザのタブ名
st.set_page_config(page_title="LapGraph-App", layout="centered")

# --- UIデザイン（自動テーマ対応） ---
# 特定の色を固定せず、Streamlitの標準変数を使うことでライト/ダークに自動追従させる
st.markdown("""
    <style>
    /* ボタンなどのアクセントカラーだけ指定 */
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
        
        # --- PDF/プレビュー用画像作成（印刷用なので背景は白固定） ---
        fig = plt.figure(figsize=(11, 8.5), facecolor='white')
        
        # ① 表の作成（上部）
        ax_table = fig.add_axes([0.1, 0.60, 0.8, 0.25]) 
        ax_table.axis('off')
        
        table_data = [["距離 (m)", "通過タイム (s)"]]
        for d, l in zip(distances, laps):
            table_data.append([f"{d}", f"{l}"])
            
        table = ax_table.table(
            cellText=table_data,
            loc='center',
            cellLoc='center',
            colWidths=[0.3, 0.3]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(12) 
        table.scale(1.2, 2.2)
        ax_table.set_title(f"通過タイム表_{event_type}", fontsize=16, pad=20)

        # ② グラフの作成（下部）
        ax_graph = fig.add_axes([0.1, 0.18, 0.8, 0.35]) 
        ax_graph.plot(distances, laps, color='red', linestyle='-', marker="o", label='タイム')
        ax_graph.set_title(title, fontsize=18, pad=15)
        ax_graph.set_xlabel('距離 (m)', fontsize=14)
        ax_graph.set_ylabel('時間 (s)', fontsize=14)
        ax_graph.set_xticks(distances)
        ax_graph.set_ylim(40, 95)
        ax_graph.grid(True, linestyle='--', linewidth=0.5)
        ax_graph.legend()

        # ③ 平均値表示
        avg_text = f"全区間の平均タイム： {avg_val:.2f} 秒"
        fig.text(0.1, 0.08, avg_text, fontsize=14, weight='bold')

        img_io = io.BytesIO()
        fig.savefig(img_io, format='png', dpi=300, bbox_inches='tight')
        img_io.seek(0)
        
        # 画面プレビュー（ここは白背景のまま表示されるのが、PDFの確認になって良い）
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
        
        save_name = f"{title}.pdf" if title else f"LapResult_{event_type}.pdf"
        
        st.download_button(
            label="PDFを保存する",
            data=pdf_io.getvalue(),
            file_name=save_name,
            mime="application/pdf"
        )
    else:
        st.warning("すべてのラップを入力してください。")
