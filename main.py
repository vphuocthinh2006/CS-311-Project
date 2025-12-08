import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()
from agent import analyze_cv_jd, find_suitable_jobs, find_hiring_companies, chat_with_agent

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🕵️‍♂️", layout="wide")

# ==================== CUSTOM CSS - MODERN DARK THEME ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Main background với gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.5)); }
        to { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.8)); }
    }
    
    .sub-header {
        text-align: center;
        color: #a0aec0;
        font-size: 1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Cards styling */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* Section headers */
    .section-title {
        color: #e2e8f0;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #a0aec0;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #e2e8f0;
        font-family: 'Poppins', sans-serif;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.03);
        border: 2px dashed rgba(102, 126, 234, 0.5);
        border-radius: 15px;
        padding: 1rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    /* Alert boxes */
    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.1) 100%);
        border-left: 4px solid #ef4444;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: #fecaca;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(245, 158, 11, 0.1) 100%);
        border-left: 4px solid #f59e0b;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: #fde68a;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.1) 100%);
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: #bfdbfe;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(22, 163, 74, 0.1) 100%);
        border-left: 4px solid #22c55e;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: #bbf7d0;
        margin: 1rem 0;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 0.5rem 0;
    }
    
    /* Chat input */
    [data-testid="stChatInput"] input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        color: #e2e8f0;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
        margin: 2rem 0;
    }
    
    /* Caption */
    .stCaption {
        color: #64748b;
        text-align: center;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        color: #e2e8f0;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
    }
    
    /* Feature card */
    .feature-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: scale(1.02);
        border-color: #667eea;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #94a3b8;
        font-size: 0.9rem;
    }
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

# ==================== HEADER ====================
st.markdown('<h1 class="main-header">🕵️‍♂️ AI Resume & Career Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Powered by GPT-4o Vision • LangChain Agent • Smart OCR</p>', unsafe_allow_html=True)

# Feature cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Phân Tích Thông Minh</div>
        <div class="feature-desc">So khớp CV-JD với AI</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎯</div>
        <div class="feature-title">Gợi Ý Việc Làm</div>
        <div class="feature-desc">Tìm công việc phù hợp</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💬</div>
        <div class="feature-title">AI Assistant</div>
        <div class="feature-desc">Tư vấn nghề nghiệp 24/7</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if not os.getenv("OPENAI_API_KEY"):
    st.markdown("""
    <div class="error-box">
        <h4>⚠️ Thiếu API Key</h4>
        <p>Chưa tìm thấy OPENAI_API_KEY trong file .env</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# TABS
tab1, tab2, tab3 = st.tabs(["📊 Phân Tích CV-JD", "💼 Tìm Việc Làm", "💬 Chat với AI"])

with tab1:
    st.markdown('<div class="section-title">📊 Phân Tích CV và JD</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📄 CV của bạn")
        cv_option = st.radio("Nguồn CV:", ["✏️ Nhập văn bản", "📁 Upload File"], key="cv_opt", horizontal=True)
        cv_input = None
        cv_type = "text"
        
        if cv_option == "📁 Upload File":
            cv_type = "file"
            uploaded_cv = st.file_uploader("Tải lên CV (PDF/PNG/JPG)", type=["pdf", "png", "jpg", "jpeg"], key="cv_file")
            if uploaded_cv:
                cv_input = save_uploaded_file(uploaded_cv)
                st.success(f"✅ Đã tải: {uploaded_cv.name}")
                if uploaded_cv.type.startswith('image'):
                    st.image(uploaded_cv, caption="Preview CV", use_container_width=True)
                elif uploaded_cv.type == "application/pdf":
                    st.markdown("""
                    <div class="info-box">
                        <strong>📄 File PDF đã sẵn sàng!</strong><br>
                        AI sẽ sử dụng OCR để trích xuất nội dung
                    </div>
                    """, unsafe_allow_html=True)
        else:
            cv_input = st.text_area("Nội dung CV:", height=280, 
                                    placeholder="Paste nội dung CV vào đây...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 💼 Job Description")
        jd_option = st.radio("Nguồn JD:", ["✏️ Nhập văn bản", "📁 Upload File"], key="jd_opt", horizontal=True)
        jd_input = None
        jd_type = "text"
        
        if jd_option == "📁 Upload File":
            jd_type = "file"
            uploaded_jd = st.file_uploader("Tải lên JD (PDF/PNG/JPG)", type=["pdf", "png", "jpg", "jpeg"], key="jd_file")
            if uploaded_jd:
                jd_input = save_uploaded_file(uploaded_jd)
                st.success(f"✅ Đã tải: {uploaded_jd.name}")
                if uploaded_jd.type.startswith('image'):
                    st.image(uploaded_jd, caption="Preview JD", use_container_width=True)
                elif uploaded_jd.type == "application/pdf":
                    st.markdown("""
                    <div class="info-box">
                        <strong>📄 File PDF đã sẵn sàng!</strong><br>
                        AI sẽ sử dụng OCR để trích xuất nội dung
                    </div>
                    """, unsafe_allow_html=True)
        else:
            jd_input = st.text_area("Nội dung JD:", height=280,
                                    placeholder="Paste nội dung JD vào đây...")
        st.markdown('</div>', unsafe_allow_html=True)
    
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
    st.markdown('<div class="section-title">💼 Tìm Việc Làm Phù Hợp</div>', unsafe_allow_html=True)
    
    # Sub-tabs cho Vị trí và Công ty
    job_tab1, job_tab2 = st.tabs(["🎯 Vị Trí Việc Làm", "🏢 Công Ty Đang Tuyển"])
    
    # ========== SUB-TAB 1: VỊ TRÍ VIỆC LÀM ==========
    with job_tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("""
            **🚀 Cách hoạt động:**
            
            AI sẽ phân tích CV của bạn và đề xuất các **vị trí việc làm** phù hợp nhất dựa trên:
            - Kỹ năng hiện có
            - Kinh nghiệm làm việc
            - Ngành nghề & chuyên môn
            """)
            
            if st.button("🔍 TÌM VỊ TRÍ PHÙ HỢP", type="primary", use_container_width=True, key="find_jobs"):
                with st.spinner("🤖 AI đang phân tích CV và tìm vị trí phù hợp..."):
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
                            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                            st.markdown(result)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="success-box">
            <strong>📋 Hướng dẫn:</strong><br><br>
            <strong>1.</strong> Phân tích CV (Tab 1)<br>
            <strong>2.</strong> Tìm vị trí việc làm<br>
            <strong>3.</strong> Xem công ty tuyển dụng
            </div>
            """, unsafe_allow_html=True)
    
    # ========== SUB-TAB 2: CÔNG TY ĐANG TUYỂN ==========
    with job_tab2:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("""
            **🏢 Tìm Công Ty Đang Tuyển:**
            
            AI sẽ gợi ý các **công ty thật** đang tuyển dụng phù hợp với profile của bạn:
            - Công ty Việt Nam & Quốc tế
            - Link career page trực tiếp
            - Link tìm kiếm trên LinkedIn, Indeed, TopDev...
            """)
            
            if st.button("🏢 TÌM CÔNG TY ĐANG TUYỂN", type="primary", use_container_width=True, key="find_companies"):
                with st.spinner("🤖 AI đang tìm các công ty phù hợp..."):
                    try:
                        result = find_hiring_companies()
                        
                        if "❌" in result:
                            st.markdown(f"""
                            <div class="warning-box">
                            <h4>⚠️ Chưa thể tìm công ty</h4>
                            <p>{result}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.info("💡 **Hướng dẫn:** Hãy chuyển sang tab 'Phân Tích CV-JD' và phân tích CV trước!")
                        else:
                            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                            st.markdown(result)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
            <strong>🔗 Nền tảng tuyển dụng:</strong><br><br>
            • <a href="https://www.linkedin.com/jobs/" target="_blank" style="color: #bfdbfe;">LinkedIn Jobs</a><br>
            • <a href="https://itviec.com" target="_blank" style="color: #bfdbfe;">ITviec</a><br>
            • <a href="https://topdev.vn" target="_blank" style="color: #bfdbfe;">TopDev</a><br>
            • <a href="https://vn.indeed.com" target="_blank" style="color: #bfdbfe;">Indeed VN</a><br>
            • <a href="https://www.vietnamworks.com" target="_blank" style="color: #bfdbfe;">VietnamWorks</a>
            </div>
            """, unsafe_allow_html=True)
    
    # Thêm section tips
    st.markdown("---")
    st.markdown("### 💡 Mẹo Tìm Việc Hiệu Quả")
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("""
        **🎯 Chuẩn bị CV tốt:**
        - Liệt kê đầy đủ kỹ năng kỹ thuật
        - Ghi rõ số năm kinh nghiệm
        - Mô tả dự án cụ thể
        - Cập nhật công nghệ mới nhất
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tips_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("""
        **🚀 Sau khi có gợi ý:**
        - Tìm hiểu chi tiết về vị trí
        - Chuẩn bị kỹ năng còn thiếu
        - Networking trên LinkedIn
        - Cập nhật CV theo xu hướng
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 3: CHATBOX ====================
with tab3:
    st.markdown('<div class="section-title">💬 Chat với AI Assistant</div>', unsafe_allow_html=True)
    
    # Initialize pending question state
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    
    # Quick actions - Đặt lên trên
    st.markdown("#### 🎯 Câu Hỏi Gợi Ý")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Phân tích CV", use_container_width=True, key="q1"):
            question = "Hãy phân tích CV của tôi một cách chi tiết"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            st.session_state.pending_question = question
            st.rerun()
    
    with col2:
        if st.button("📚 Gợi ý học tập", use_container_width=True, key="q2"):
            question = "Đề xuất lộ trình học tập và khóa học phù hợp"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            st.session_state.pending_question = question
            st.rerun()
    
    with col3:
        if st.button("💼 Tư vấn nghề nghiệp", use_container_width=True, key="q3"):
            question = "Cho tôi lời khuyên về sự nghiệp và phát triển"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            st.session_state.pending_question = question
            st.rerun()
    
    with col4:
        if st.button("🗑️ Xóa chat", type="secondary", use_container_width=True, key="clear"):
            st.session_state.chat_messages = []
            st.session_state.pending_question = None
            st.rerun()
    
    st.markdown("---")
    
    # Hiển thị lịch sử chat
    chat_container = st.container(height=450)
    
    with chat_container:
        if not st.session_state.chat_messages:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #64748b;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
                <h3 style="color: #94a3b8;">Xin chào! Tôi là AI Assistant</h3>
                <p>Hãy hỏi tôi bất cứ điều gì về CV, nghề nghiệp, hoặc phát triển kỹ năng của bạn!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
    
    # Xử lý pending question từ nút gợi ý
    if st.session_state.pending_question:
        pending_q = st.session_state.pending_question
        st.session_state.pending_question = None  # Clear ngay để tránh loop
        
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🤔 Đang suy nghĩ..."):
                    try:
                        response = chat_with_agent(pending_q)
                        st.markdown(response)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"❌ Lỗi: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        st.rerun()
    
    # Chat input
    user_input = st.chat_input("💭 Nhập câu hỏi của bạn...")
    
    if user_input:
        # Thêm tin nhắn người dùng
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        # Hiển thị tin nhắn người dùng
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Gọi agent
        with st.chat_message("assistant"):
            with st.spinner("🤔 Đang suy nghĩ..."):
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

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0; color: #64748b;">
    <p style="margin-bottom: 0.5rem;">
        <strong style="color: #94a3b8;">👨‍💻 Phát triển bởi</strong> 
        <span style="background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600;">
            Võ Phước Thịnh, Liên Phúc Thịnh & Nguyễn Tấn Phúc Thịnh
        </span>
    </p>
    <p style="font-size: 0.85rem; color: #475569;">
        🚀 Version 2.0 • GPT-4o Vision OCR • LangChain Agent • Smart Job Matching
    </p>
</div>
""", unsafe_allow_html=True)