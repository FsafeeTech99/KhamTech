import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. ตั้งค่าหน้าเว็บ (Taste-D Style)
# ==========================================
st.set_page_config(page_title="KhamTech | Price Matching", page_icon="💊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1 { color: #0f172a; font-family: 'Segoe UI', Tahoma, sans-serif; font-weight: 800; }
    .stRadio label p { font-size: 20px !important; font-weight: 700 !important; color: #1e293b !important; }
    div[data-testid="stRadio"] { background-color: white; padding: 20px; border-radius: 12px; border: 2px solid #cbd5e1; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Header & Developer Credit
# ==========================================
st.markdown("<h1 style='text-align: center;'>💻 KhamTech : ระบบตรวจสอบและเทียบราคาขายยา 💊</h1>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; color: #475569; font-size: 16px; margin-top: -10px; line-height: 1.6;'>
        <b>พัฒนาโดย:</b> นายพงษ์ศักดิ์ อาษาเสน<br>
        นักวิชาการสาธารณสุข กลุ่มงานประกันสุขภาพและเทคโนโลยีสารสนเทศ<br>
        รพ.สต.คำสะอาด อ.สว่างแดนดิน จ.สกลนคร
    </p>
""", unsafe_allow_html=True)
st.write("---")

mode = st.radio(
    "📌 เลือกโหมดการทำงาน:",
    ["📦 โหมดที่ 1: ตรวจสอบบัญชีรายชื่อยาภาพรวม", "🔍 โหมดที่ 2: ตรวจสอบการจ่ายยารายบุคคล"]
)
st.write("---")

# ==========================================
# 3. นำเข้าข้อมูล (3 ฐานข้อมูล)
# ==========================================
col1, col2, col3 = st.columns(3)
with col1:
    jhcis_file = st.file_uploader("🏥 1. ไฟล์จาก JHCIS (รพ.สต.)", type=["xlsx", "xls", "csv"], key="jhcis")
with col2:
    nhso_file = st.file_uploader("🌐 2. ไฟล์มาตรฐาน สปสช.", type=["xlsx", "xls", "csv"], key="nhso")
with col3:
    rph_file = st.file_uploader("🏥 3. ไฟล์จาก รพร.แม่ข่าย (ถ้ามี)", type=["xlsx", "xls", "csv"], key="rph")

if jhcis_file and nhso_file:
    try:
        df_jhcis = pd.read_csv(jhcis_file) if jhcis_file.name.endswith('csv') else pd.read_excel(jhcis_file)
        df_nhso = pd.read_csv(nhso_file) if nhso_file.name.endswith('csv') else pd.read_excel(nhso_file)

        # 🔒 ล็อคชื่อคอลัมน์มาตรฐาน (Hardcoded)
        # 1. JHCIS
        col_drug_jhcis = "ชื่อยา"
        col_tmt_jhcis = "รหัส_TMT"
        col_price_jhcis = "ราคาขาย"
        col_pid = "PID"  
        col_date = "วันที่" 
        
        # 2. NHSO (สปสช.)
        col_tmt_nhso = "TMTID"
        col_drug_nhso = "GENERICNAME"
        col_price_nhso = "UNITPRICE"
        col_date_eff_nhso = "DATEEFFECTIVE"
        col_date_app_nhso = "DATE_APPROVED"

        # 3. RPH (รพร.แม่ข่าย)
        col_tmt_rph = "TPU List"
        col_drug_rph = "ชื่อเวชภัณฑ์"   
        col_price_rph = "ราคา (OPD)" 

        st.write("")
        st.success("✅ โหลดไฟล์ระบบหลักสำเร็จ พร้อมประมวลผล (One-Click Auto Run)")
        if rph_file:
            st.info("💡 ตรวจพบไฟล์อ้างอิงจาก รพร.แม่ข่าย ระบบจะดึงราคามาเทียบให้ด้วยครับ")
        
        if st.button("🚀 ประมวลผลเปรียบเทียบราคาอัตโนมัติ", type="primary", use_container_width=True):
            
            # --- 0. ตรวจสอบว่าไฟล์มีคอลัมน์ครบไหม ---
            missing_jhcis = [c for c in [col_drug_jhcis, col_tmt_jhcis, col_price_jhcis] if c not in df_jhcis.columns]
            missing_nhso = [c for c in [col_tmt_nhso, col_drug_nhso, col_price_nhso, col_date_eff_nhso, col_date_app_nhso] if c not in df_nhso.columns]
            
            if missing_jhcis or missing_nhso:
                st.error("⚠️ ไฟล์ที่อัปโหลดมีโครงสร้างไม่ตรงกับมาตรฐาน กรุณาตรวจสอบไฟล์อีกครั้ง")
                if missing_jhcis: st.warning(f"ไฟล์ JHCIS ขาดคอลัมน์: {', '.join(missing_jhcis)}")
                if missing_nhso: st.warning(f"ไฟล์ สปสช. ขาดคอลัมน์: {', '.join(missing_nhso)}")
                st.stop()
                
            if rph_file:
                df_rph = pd.read_csv(rph_file) if rph_file.name.endswith('csv') else pd.read_excel(rph_file)
                missing_rph = [c for c in [col_drug_rph, col_tmt_rph, col_price_rph] if c not in df_rph.columns]
                if missing_rph:
                    st.error(f"⚠️ ไฟล์ รพร. ขาดคอลัมน์: {', '.join(missing_rph)} (กรุณาตรวจสอบชื่อคอลัมน์ให้ตรงกันก่อน)")
                    st.stop()

            # --- 1. ทำความสะอาดรหัส TMT ---
            df_jhcis["_clean_tmt_j"] = df_jhcis[col_tmt_jhcis].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().replace(['nan', 'None', 'none', '', '<na>', 'NaN'], np.nan)
            df_nhso["_clean_tmt_n"] = df_nhso[col_tmt_nhso].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().replace(['nan', 'None', 'none', '', '<na>', 'NaN'], np.nan)
            
            keep_cols = [col_drug_jhcis, col_price_jhcis, "_clean_tmt_j"]
            if "โหมดที่ 2" in mode:
                if col_pid not in df_jhcis.columns: df_jhcis[col_pid] = "-"
                if col_date not in df_jhcis.columns: df_jhcis[col_date] = "-"
                keep_cols = [col_pid, col_date] + keep_cols
                
            # --- 2. ดึงคอลัมน์ สปสช. และตัดยาซ้ำ ---
            nhso_subset = df_nhso[["_clean_tmt_n", col_drug_nhso, col_price_nhso, col_date_eff_nhso, col_date_app_nhso]].dropna(subset=["_clean_tmt_n"])
            nhso_subset = nhso_subset.drop_duplicates(subset=["_clean_tmt_n"], keep="first")
            
            # --- 3. ทำการจับคู่ฐานข้อมูลรอบแรก (JHCIS x NHSO) ---
            mapped_df = pd.merge(df_jhcis[keep_cols], nhso_subset, left_on="_clean_tmt_j", right_on="_clean_tmt_n", how="left")

            # --- 3.5 จับคู่ฐานข้อมูลรอบสอง (JHCIS x รพร.) ถ้ามีไฟล์ ---
            if rph_file:
                df_rph["_clean_tmt_r"] = df_rph[col_tmt_rph].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().replace(['nan', 'None', 'none', '', '<na>', 'NaN'], np.nan)
                rph_subset = df_rph[["_clean_tmt_r", col_drug_rph, col_price_rph]].dropna(subset=["_clean_tmt_r"])
                rph_subset = rph_subset.drop_duplicates(subset=["_clean_tmt_r"], keep="first")
                mapped_df = pd.merge(mapped_df, rph_subset, left_on="_clean_tmt_j", right_on="_clean_tmt_r", how="left")

            # --- 4. Logic เปรียบเทียบราคา (โฟกัส สปสช. เป็นหลัก) ---
            def check_price_logic(row):
                tmt = str(row["_clean_tmt_j"]).strip()
                if tmt.lower() in ["nan", "none", "", "0", "<na>"]:
                    return "🟡 ขาดรหัส TMT", "ให้ไปเติมรหัส TMT ก่อน"
                if pd.isna(row[col_price_nhso]):
                    return "❌ สปสช. ไม่มีรหัสนี้", "ตรวจสอบรหัส TMT ใหม่"
                try:
                    p_jhcis = float(str(row[col_price_jhcis]).replace(',', ''))
                    p_nhso = float(str(row[col_price_nhso]).replace(',', ''))
                    if round(p_jhcis, 2) != round(p_nhso, 2):
                        return "🔴 ราคาไม่ตรง สปสช.", f"ควรพิจารณาปรับราคาให้เป็น {round(p_nhso, 2)} ฿"
                    else:
                        return "✅ ราคาตรงกัน", "ถูกต้อง"
                except Exception:
                    return "⚠️ ราคาผิดรูปแบบ", "ในช่องราคาอาจมีตัวหนังสือปน"

            results = mapped_df.apply(check_price_logic, axis=1)
            mapped_df["📌 สถานะ"] = [res[0] for res in results]
            mapped_df["🛠️ วิธีแก้ไข"] = [res[1] for res in results]

            # --- 5. จัดการชื่อและการแสดงผลคอลัมน์ ---
            rename_dict = {
                col_drug_jhcis: "ชื่อยา (JHCIS)", "_clean_tmt_j": "รหัส TMT",
                col_price_jhcis: "ราคา (JHCIS)", col_drug_nhso: "ชื่อยา (สปสช.)", 
                col_price_nhso: "ราคา (สปสช.)", col_date_eff_nhso: "เริ่มใช้ (สปสช.)",
                col_date_app_nhso: "อนุมัติ (สปสช.)"
            }
            if rph_file:
                rename_dict.update({col_drug_rph: "ชื่อยา (รพร.)", col_price_rph: "ราคาอ้างอิง (รพร.)"})
            if "โหมดที่ 2" in mode:
                rename_dict.update({col_pid: "PID", col_date: "วันที่รับบริการ"})
                
            mapped_df.rename(columns=rename_dict, inplace=True)

            # จัดเรียงคอลัมน์ให้ราคาอยู่ติดกัน
            cols_to_show = ["📌 สถานะ", "🛠️ วิธีแก้ไข", "รหัส TMT", "ชื่อยา (JHCIS)", "ราคา (JHCIS)", "ราคา (สปสช.)"]
            if rph_file: cols_to_show.append("ราคาอ้างอิง (รพร.)")
            cols_to_show.extend(["เริ่มใช้ (สปสช.)", "อนุมัติ (สปสช.)", "ชื่อยา (สปสช.)"])
            if rph_file: cols_to_show.append("ชื่อยา (รพร.)")
            
            if "โหมดที่ 2" in mode:
                cols_to_show.insert(3, "PID"); cols_to_show.insert(4, "วันที่รับบริการ")
            
            display_df = mapped_df[cols_to_show]

            def highlight_row(val):
                if val == "🔴 ราคาไม่ตรง สปสช.": return 'background-color: #ffe6e6; color: #cc0000; font-weight: bold;'
                elif val == "🟡 ขาดรหัส TMT": return 'background-color: #fff4cc; color: #996600; font-weight: bold;'
                elif val == "✅ ราคาตรงกัน": return 'color: #008000;'
                return ''

            # ==========================================
            # 6. แสดงผล Dashboard
            # ==========================================
            st.divider()
            st.markdown("### 📊 ผลการตรวจสอบราคาแบบ Multi-Source (JHCIS x สปสช. x รพร.)")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("🟢 ราคาตรง สปสช.", f"{len(display_df[display_df['📌 สถานะ'] == '✅ ราคาตรงกัน'])}")
            m2.metric("🔴 ต้องประเมินราคาใหม่", f"{len(display_df[display_df['📌 สถานะ'] == '🔴 ราคาไม่ตรง สปสช.'])}")
            m3.metric("🟡 ขาดรหัส TMT", f"{len(display_df[display_df['📌 สถานะ'] == '🟡 ขาดรหัส TMT'])}")
            st.write("---")

            filter_view = st.radio("มุมมอง:", ["🔍 แสดงเฉพาะรายการที่ต้องประเมินใหม่", "📋 แสดงทั้งหมด"], horizontal=True)
            if "แสดงเฉพาะ" in filter_view:
                final_df = display_df[display_df["📌 สถานะ"] != "✅ ราคาตรงกัน"]
            else:
                final_df = display_df

            styled_df = final_df.style.map(highlight_row, subset=['📌 สถานะ'])
            st.dataframe(styled_df, use_container_width=True, height=500)

            csv_data = final_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดรายงานเปรียบเทียบราคา",
                data=csv_data,
                file_name="KhamTech_Price_Comparison_Report.csv",
                mime="text/csv",
                type="primary"
            )
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")