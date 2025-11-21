import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import sys
st.title("🕵️‍♂️ Debug Mode")
current_dir = os.getcwd()
st.write(f"📂 Thư mục hiện tại: `{current_dir}`")
files = os.listdir(current_dir)
st.write("📄 Danh sách file thực tế trên server:")
st.code(files)
if "agent.py" in files:
    st.success("✅ TÌM THẤY file agent.py trên đĩa cứng!")
else:
    st.error("❌ KHÔNG TÌM THẤY file agent.py trên đĩa cứng! (Lỗi Git rồi)")
    st.stop()
st.write("🔄 Đang thử import agent...")
st.success("✅ Import agent thành công! Code agent ngon lành.")


load_dotenv()
try:
    from agent import analyze_cv_jd
except ImportError:
    st.error("⚠️ Không tìm thấy file 'agent.py'. Hãy đảm bảo file này nằm cùng thư mục với main.py")
    st.stop()
st.set_page_config(page_title="AI Resume Analyzer", page_icon="🕵️‍♂️", layout="wide")
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    h1 { color: #2e86c1; }
    .stButton>button {
        width: 100%; background-color: #2e86c1; color: white; font-weight: bold; padding: 10px;
    }
    .stButton>button:hover { background-color: #1a5276; color: white; }
    .error-box {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

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

st.title("🕵️‍♂️ AI Resume & Career Analyzer")
st.caption("Phát triển bởi Võ Phước Thịnh, Liên Phúc Thịnh và Gemini - Powered by LangChain & OpenAI & Streamlit")
st.markdown("---")
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ Chưa tìm thấy OPENAI_API_KEY trong file .env.")
    st.stop()
with st.expander("⚠️ Lưu ý quan trọng về upload ảnh"):
    st.markdown("""
    <div class="warning-box">
    <strong>Nếu bạn upload CV/JD dưới dạng ảnh (.png, .jpg):</strong>
    <ul>
        <li>Cần cài đặt Tesseract OCR trước</li>
        <li>Windows: <a href="https://github.com/UB-Mannheim/tesseract/wiki" target="_blank">Tải tại đây</a></li>
        <li>Nếu chưa cài, vui lòng chọn "Nhập văn bản (Text)" thay vì upload ảnh</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.header("📄 Thông tin Ứng viên (CV)")
    cv_option = st.radio("Nguồn CV:", ["Nhập văn bản (Text)", "Upload File (PDF/Ảnh)"], key="cv_opt")
    cv_input = None
    cv_type = "text"
    
    if cv_option == "Upload File (PDF/Ảnh)":
        cv_type = "file"
        uploaded_cv = st.file_uploader("Tải lên CV", type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_cv:
            cv_input = save_uploaded_file(uploaded_cv)
            st.success(f"✅ Đã tải: {uploaded_cv.name}")
            if uploaded_cv.type.startswith('image'):
                st.image(uploaded_cv, caption="Preview CV", use_column_width=True)
                st.warning("⚠️ Đang sử dụng ảnh - cần Tesseract OCR")
    else:
        cv_input = st.text_area("Nội dung CV:", height=300, 
                                placeholder="Ví dụ:\nNguyễn Văn A\nPython Developer\n- 3 năm kinh nghiệm...",
                                help="Nhập hoặc paste nội dung CV vào đây")
with col2:
    st.header("💼 Mô tả Công việc (JD)")
    jd_option = st.radio("Nguồn JD:", ["Nhập văn bản (Text)", "Upload File (PDF/Ảnh)"], key="jd_opt")
    jd_input = None
    jd_type = "text"
    
    if jd_option == "Upload File (PDF/Ảnh)":
        jd_type = "file"
        uploaded_jd = st.file_uploader("Tải lên JD", type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_jd:
            jd_input = save_uploaded_file(uploaded_jd)
            st.success(f"✅ Đã tải: {uploaded_jd.name}")
            if uploaded_jd.type.startswith('image'):
                st.image(uploaded_jd, caption="Preview JD", use_column_width=True)
                st.warning("⚠️ Đang sử dụng ảnh - cần Tesseract OCR")
    else:
        jd_input = st.text_area("Nội dung JD:", height=300,
                                placeholder="Ví dụ:\nTuyển dụng Python Developer\nYêu cầu: Python, FastAPI, Docker...",
                                help="Nhập hoặc paste nội dung JD vào đây")
st.markdown("---")
analyze_btn = st.button("🚀 PHÂN TÍCH NGAY", type="primary")

if analyze_btn:
    if not cv_input or not jd_input:
        st.error("⚠️ Vui lòng cung cấp đầy đủ thông tin CV và JD!")
    else:
        try:
            with st.spinner("🤖 AI đang phân tích... Vui lòng đợi..."):
                result = analyze_cv_jd(
                    cv_input=cv_input, 
                    jd_input=jd_input, 
                    cv_type=cv_type, 
                    jd_type=jd_type
                )
                if "ERROR:" in result or "Không thể đọc" in result:
                    st.markdown("""
                    <div class="error-box">
                    <h3>❌ Lỗi khi xử lý file</h3>
                    <p>{}</p>
                    <p><strong>Giải pháp:</strong></p>
                    <ul>
                        <li>Nếu đang dùng ảnh: Cài đặt Tesseract OCR hoặc chuyển sang nhập text</li>
                        <li>Nếu đang dùng PDF: Kiểm tra file có hợp lệ không</li>
                        <li>Khuyên dùng: Chọn "Nhập văn bản (Text)" để tránh lỗi</li>
                    </ul>
                    </div>
                    """.format(result), unsafe_allow_html=True)
                else:
                    st.success("✅ Phân tích hoàn tất!")
                    st.markdown("## 📊 Kết Quả Phân Tích")
                    st.markdown("---")
                    st.markdown(result)
                    
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
            <h3>❌ Đã xảy ra lỗi</h3>
            <p><strong>Chi tiết:</strong> {str(e)}</p>
            <p><strong>Khuyến nghị:</strong></p>
            <ul>
                <li>Thử lại với định dạng "Nhập văn bản (Text)"</li>
                <li>Kiểm tra OPENAI_API_KEY trong file .env</li>
                <li>Restart ứng dụng Streamlit</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        finally:
            if cv_type == "file" and cv_input and os.path.exists(cv_input): 
                try:
                    os.unlink(cv_input)
                except:
                    pass
            if jd_type == "file" and jd_input and os.path.exists(jd_input): 
                try:
                    os.unlink(jd_input)
                except:
                    pass

st.markdown("---")
st.caption("Phát triển bởi Võ Phước Thịnh, Liên Phúc Thịnh và Gemini - Powered by LangChain & OpenAI & Streamlit")