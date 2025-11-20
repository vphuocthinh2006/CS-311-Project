import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Import hàm phân tích từ agent
try:
    from agent import analyze_cv_jd
except ImportError:
    st.error("⚠️ Không tìm thấy file 'agent.py'. Hãy đảm bảo file này nằm cùng thư mục với main.py")
    st.stop()

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="AI Resume Analyzer", page_icon="🕵️‍♂️", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    h1 { color: #2e86c1; }
    .stButton>button {
        width: 100%; background-color: #2e86c1; color: white; font-weight: bold; padding: 10px;
    }
    .stButton>button:hover { background-color: #1a5276; color: white; }
</style>
""", unsafe_allow_html=True)

# --- HÀM HỖ TRỢ ---
def save_uploaded_file(uploaded_file):
    """Lưu file upload vào thư mục tạm"""
    try:
        suffix = "." + uploaded_file.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Lỗi khi lưu file: {e}")
        return None

# --- HEADER ---
st.title("🕵️‍♂️ AI Resume & Career Analyzer")
st.caption("Phát triển bởi Võ Phước Thịnh, Liên Phúc Thịnh và Gemini")
st.markdown("---")

# Kiểm tra API Key
if not os.getenv("OPENAI_API_KEY"):
    st.warning("⚠️ Chưa tìm thấy OPENAI_API_KEY trong file .env.")
    st.stop()

col1, col2 = st.columns(2)

# --- CỘT 1: CV ---
with col1:
    st.header("📄 Thông tin Ứng viên (CV)")
    cv_option = st.radio("Nguồn CV:", ["Upload File (PDF/Ảnh)", "Nhập văn bản (Text)"], key="cv_opt")
    cv_input = None
    cv_type = "file"
    
    if cv_option == "Upload File (PDF/Ảnh)":
        uploaded_cv = st.file_uploader("Tải lên CV", type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_cv:
            cv_input = save_uploaded_file(uploaded_cv)
            st.success(f"Đã tải: {uploaded_cv.name}")
            if uploaded_cv.type.startswith('image'):
                st.image(uploaded_cv, caption="Preview CV", use_column_width=True)
    else:
        cv_type = "text"
        cv_input = st.text_area("Nội dung CV:", height=300, placeholder="Nguyễn Văn A - Kinh nghiệm...")

# --- CỘT 2: JD ---
with col2:
    st.header("💼 Mô tả Công việc (JD)")
    jd_option = st.radio("Nguồn JD:", ["Upload File (PDF/Ảnh)", "Nhập văn bản (Text)"], key="jd_opt")
    jd_input = None
    jd_type = "file"
    
    if jd_option == "Upload File (PDF/Ảnh)":
        uploaded_jd = st.file_uploader("Tải lên JD", type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_jd:
            jd_input = save_uploaded_file(uploaded_jd)
            st.success(f"Đã tải: {uploaded_jd.name}")
            if uploaded_jd.type.startswith('image'):
                st.image(uploaded_jd, caption="Preview JD", use_column_width=True)
    else:
        jd_type = "text"
        jd_input = st.text_area("Nội dung JD:", height=300, placeholder="Tuyển dụng Python Developer...")

# --- NÚT PHÂN TÍCH ---
st.markdown("---")
analyze_btn = st.button("🚀 PHÂN TÍCH NGAY")

if analyze_btn:
    if not cv_input or not jd_input:
        st.error("⚠️ Vui lòng cung cấp đầy đủ thông tin CV và JD!")
    else:
        try:
            with st.spinner("🤖 AI đang phân tích... Vui lòng đợi..."):
                result = analyze_cv_jd(cv_input=cv_input, jd_input=jd_input, cv_type=cv_type, jd_type=jd_type)
                st.success("✅ Phân tích hoàn tất!")
                st.markdown("## 📊 Kết Quả Phân Tích")
                st.markdown("---")
                st.markdown(result)
        except Exception as e:
            st.error(f"❌ Lỗi: {e}")
        finally:
            # Dọn dẹp file tạm
            if cv_type == "file" and cv_input and os.path.exists(cv_input): os.unlink(cv_input)
            if jd_type == "file" and jd_input and os.path.exists(jd_input): os.unlink(jd_input)
# %%
st.markdown("---")
st.caption("Phát triển bởi Võ Phước Thịnh, Liên Phúc Thịnh và Gemini - Powered by LangChain & OpenAI & Streamlit")
# %%