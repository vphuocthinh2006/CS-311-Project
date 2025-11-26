import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()
from agent import analyze_cv_jd, find_suitable_jobs, chat_with_agent

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🕵️‍♂️", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    h1 { color: #2e86c1; }
    .stButton>button {
        width: 100%; background-color: #2e86c1; color: white; font-weight: bold; padding: 10px;
    }
    .stButton>button:hover { background-color: #1a5276; color: white; }
    .error-box { background-color: #ffebee; border-left: 5px solid #f44336; padding: 15px; margin: 10px 0; border-radius: 5px; }
    .warning-box { background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 15px; margin: 10px 0; border-radius: 5px; }
    .info-box { background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 15px; margin: 10px 0; border-radius: 5px; }
    .success-box { background-color: #e8f5e9; border-left: 5px solid #4caf50; padding: 15px; margin: 10px 0; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

def save_uploaded_file(uploaded_file):
    try:
        suffix = "." + uploaded_file.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Lỗi khi lưu file: {e}")
        return None

# Session state cho chatbox
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

st.title("🕵️‍♂️ AI Resume & Career Analyzer")
st.caption("Phát triển bởi Võ Phước Thịnh, Liên Phúc Thịnh và Nguyễn Tấn Phúc Thịnh - The Unwithering Trio")
st.markdown("---")

if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ Chưa tìm thấy OPENAI_API_KEY trong file .env.")
    st.stop()

# TABS
tab1, tab2, tab3 = st.tabs(["📊 Phân Tích CV-JD", "💼 Tìm Việc Làm", "💬 Chat với AI"])

with tab1:
    st.header("📊 Phân Tích CV và JD")
    
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 CV")
        cv_option = st.radio("Nguồn CV:", ["Nhập văn bản (Text)", "Upload File (PDF/Ảnh)"], key="cv_opt")
        cv_input = None
        cv_type = "text"
        
        if cv_option == "Upload File (PDF/Ảnh)":
            cv_type = "file"
            uploaded_cv = st.file_uploader("Tải lên CV", type=["pdf", "png", "jpg", "jpeg"], key="cv_file")
            if uploaded_cv:
                cv_input = save_uploaded_file(uploaded_cv)
                st.success(f"✅ Đã tải: {uploaded_cv.name}")
                if uploaded_cv.type.startswith('image'):
                    st.image(uploaded_cv, caption="Preview CV", use_column_width=True)
                elif uploaded_cv.type == "application/pdf":
                    st.info("📄 File PDF đã sẵn sàng để phân tích")
        else:
            cv_input = st.text_area("Nội dung CV:", height=300, 
                                    placeholder="Paste nội dung CV vào đây...")
    
    with col2:
        st.subheader("💼 JD")
        jd_option = st.radio("Nguồn JD:", ["Nhập văn bản (Text)", "Upload File (PDF/Ảnh)"], key="jd_opt")
        jd_input = None
        jd_type = "text"
        
        if jd_option == "Upload File (PDF/Ảnh)":
            jd_type = "file"
            uploaded_jd = st.file_uploader("Tải lên JD", type=["pdf", "png", "jpg", "jpeg"], key="jd_file")
            if uploaded_jd:
                jd_input = save_uploaded_file(uploaded_jd)
                st.success(f"✅ Đã tải: {uploaded_jd.name}")
                if uploaded_jd.type.startswith('image'):
                    st.image(uploaded_jd, caption="Preview JD", use_column_width=True)
                elif uploaded_jd.type == "application/pdf":
                    st.info("📄 File PDF đã sẵn sàng")
        else:
            jd_input = st.text_area("Nội dung JD:", height=300,
                                    placeholder="Paste nội dung JD vào đây...")
    
    st.markdown("---")
    analyze_btn = st.button("🚀 PHÂN TÍCH", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not cv_input or not jd_input:
            st.error("⚠️ Vui lòng cung cấp đầy đủ CV và JD!")
        else:
            try:
                with st.spinner("🤖 AI đang phân tích... Vui lòng đợi..."):
                    result = analyze_cv_jd(cv_input=cv_input, jd_input=jd_input, 
                                          cv_type=cv_type, jd_type=jd_type)
                    
                    if "ERROR:" in result or "❌" in result:
                        st.markdown(f"""
                        <div class="error-box">
                        <h3>❌ Lỗi khi xử lý</h3>
                        <p>{result}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("✅ Phân tích hoàn tất!")
                        st.markdown("---")
                        st.markdown(result)
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
            finally:
                if cv_type == "file" and cv_input and os.path.exists(cv_input):
                    try: os.unlink(cv_input)
                    except: pass
                if jd_type == "file" and jd_input and os.path.exists(jd_input):
                    try: os.unlink(jd_input)
                    except: pass

# ==================== TAB 2: TÌM VIỆC ====================
with tab2:
    st.header("💼 Tìm Việc Làm Phù Hợp")
    

    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔍 TÌM VIỆC PHÙ HỢP NGAY", type="primary", use_container_width=True):
            with st.spinner("🤖 AI đang phân tích CV và tìm việc phù hợp..."):
                try:
                    result = find_suitable_jobs()
                    
                    if "❌" in result:
                        st.markdown(f"""
                        <div class="warning-box">
                        <h4>⚠️ Chưa thể tìm việc</h4>
                        <p>{result}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.info("💡 **Hướng dẫn:** Hãy chuyển sang tab 'Phân Tích CV-JD' và phân tích CV trước!")
                    else:
                        st.markdown(result)
                        
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
    
    with col2:
        st.markdown("""
        <div class="success-box" style = "color: black;">
        <strong>📋 Bước thực hiện:</strong><br>
        1. Tab 1: Phân tích CV<br>
        2. Tab 2: Tìm việc<br>
        3. Tab 3: Hỏi đáp
        </div>
        """, unsafe_allow_html=True)
    
    # Thêm section tips
    st.markdown("---")
    st.markdown("### 💡 Mẹo Tìm Việc Hiệu Quả")
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.markdown("""
        **🎯 Chuẩn bị CV tốt:**
        - Liệt kê đầy đủ kỹ năng kỹ thuật
        - Ghi rõ số năm kinh nghiệm
        - Mô tả dự án cụ thể
        - Cập nhật công nghệ mới nhất
        """)
    
    with tips_col2:
        st.markdown("""
        **🚀 Sau khi có gợi ý:**
        - Tìm hiểu chi tiết về vị trí
        - Chuẩn bị kỹ năng còn thiếu
        - Networking trên LinkedIn
        - Cập nhật CV theo xu hướng
        """)

# ==================== TAB 3: CHATBOX ====================
with tab3:
    st.header("💬 Chat với AI Assistant")
    
    
    # Hiển thị lịch sử chat
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Chat input
    user_input = st.chat_input("Nhập câu hỏi của bạn...")
    
    if user_input:
        # Thêm tin nhắn người dùng
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        # Hiển thị tin nhắn người dùng
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Gọi agent
        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                try:
                    response = chat_with_agent(user_input)
                    st.markdown(response)
                    
                    # Lưu phản hồi
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Lỗi: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        
        # Rerun để cập nhật UI
        st.rerun()
    
    # Quick actions
    st.markdown("---")
    st.markdown("#### 🎯 Câu Hỏi Gợi Ý")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Phân tích CV", use_container_width=True):
            user_input = "Hãy phân tích CV của tôi một cách chi tiết"
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            st.rerun()
    
    with col2:
        if st.button("📚 Gợi ý học tập", use_container_width=True):
            user_input = "Đề xuất lộ trình học tập và khóa học phù hợp"
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            st.rerun()
    
    with col3:
        if st.button("💼 Tư vấn nghề nghiệp", use_container_width=True):
            user_input = "Cho tôi lời khuyên về sự nghiệp và phát triển"
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            st.rerun()
    
    with col4:
        if st.button("🔄 Xóa chat", type="secondary", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

st.markdown("---")
st.caption("Phát triển bởi Võ Phước Thịnh, Liên Phúc Thịnh và Nguyễn Tấn Phúc Thịnh - Powered by LangChain & GPT-4o")
st.caption("Version 2.0 - GPT-4o Vision OCR • Job Search • AI Chat Assistant")