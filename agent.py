import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool
from langchain import hub
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")
if not os.getenv("OPENAI_API_KEY"):
    print("NOT FOUND THE API KEY!")
else:
    print("KEY FOUND!")

# Import tools
try:
    from tools_ocr import extract_text_hybrid_fixed, extract_text_from_image, process_raw_text
    from tools_similarity import calculate_similarity
    from tools_skills import compare_skills_tool
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    print("MAKE SURE THAT THEY EXIST IN THE data/ DIRECTORY")
    exit()


# Global variables to store extracted texts
CV_TEXT_STORAGE = ""
JD_TEXT_STORAGE = ""


# ===== SIMPLE TOOLS - NO JSON =====
@tool
def tool_read_image(image_path: str) -> str:
    """
    Đọc văn bản từ file ảnh.
    Input: đường dẫn file ảnh
    Output: nội dung văn bản
    """
    try:
        result = extract_text_from_image(image_path)
        if not result or "error" in result.lower():
            return "ERROR_OCR: Tesseract chưa được cài đặt. Vui lòng dùng text input."
        return result
    except Exception as e:
        return f"ERROR_OCR: {str(e)}"


@tool
def tool_process_text_input(raw_text: str) -> str:
    """
    Làm sạch văn bản.
    Input: văn bản thô
    Output: văn bản đã làm sạch
    """
    try:
        return process_raw_text(raw_text)
    except Exception as e:
        return f"ERROR: {str(e)}"


@tool
def tool_read_pdf(file_path: str) -> str:
    """
    Đọc văn bản từ file PDF.
    Input: đường dẫn file PDF
    Output: nội dung văn bản
    """
    try:
        result = extract_text_hybrid_fixed(file_path)
        if not result or len(result.strip()) < 10:
            return "ERROR_PDF: File PDF trống hoặc không đọc được."
        return result
    except Exception as e:
        return f"ERROR_PDF: {str(e)}"


@tool
def tool_store_cv_text(cv_text: str) -> str:
    """
    Lưu CV text đã trích xuất vào bộ nhớ.
    Input: nội dung CV text
    Output: xác nhận đã lưu
    """
    global CV_TEXT_STORAGE
    CV_TEXT_STORAGE = cv_text
    return f"SUCCESS: Đã lưu CV text ({len(cv_text)} ký tự)"


@tool
def tool_store_jd_text(jd_text: str) -> str:
    """
    Lưu JD text đã trích xuất vào bộ nhớ.
    Input: nội dung JD text
    Output: xác nhận đã lưu
    """
    global JD_TEXT_STORAGE
    JD_TEXT_STORAGE = jd_text
    return f"SUCCESS: Đã lưu JD text ({len(jd_text)} ký tự)"


@tool
def tool_calculate_match_score(dummy: str = "run") -> str:
    """
    Tính điểm phù hợp giữa CV và JD đã lưu trong bộ nhớ.
    Input: bất kỳ string nào (không quan trọng)
    Output: điểm phù hợp dạng số
    """
    global CV_TEXT_STORAGE, JD_TEXT_STORAGE
    try:
        if not CV_TEXT_STORAGE or not JD_TEXT_STORAGE:
            return "ERROR: Chưa có CV hoặc JD text. Hãy lưu chúng trước."
        score = calculate_similarity(CV_TEXT_STORAGE, JD_TEXT_STORAGE)
        return str(score)
    except Exception as e:
        return f"ERROR: {str(e)}"


@tool
def tool_analyze_skills(dummy: str = "run") -> str:
    """
    Phân tích kỹ năng trong CV so với JD đã lưu.
    Input: bất kỳ string nào
    Output: kỹ năng có và kỹ năng thiếu, phân cách bởi |||
    Format: cv_skills: skill1, skill2 ||| missing_skills: skill3, skill4
    """
    global CV_TEXT_STORAGE, JD_TEXT_STORAGE
    try:
        if not CV_TEXT_STORAGE or not JD_TEXT_STORAGE:
            return "ERROR: Chưa có CV hoặc JD text."
        
        result = compare_skills_tool(CV_TEXT_STORAGE, JD_TEXT_STORAGE)
        cv_skills = ", ".join(result.get('cv_skills', []))
        missing_skills = ", ".join(result.get('missing_skills', []))
        
        return f"cv_skills: {cv_skills} ||| missing_skills: {missing_skills}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def initialize_agent():
    """Khởi tạo Agent."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    tools = [
        tool_read_pdf,
        tool_read_image,
        tool_process_text_input,
        tool_store_cv_text,
        tool_store_jd_text,
        tool_calculate_match_score,
        tool_analyze_skills,
    ]
    
    prompt = hub.pull("hwchase17/react")    
    agent = create_react_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=15
    )
    
    return agent_executor


def analyze_cv_jd(cv_input: str, jd_input: str, cv_type: str = "text", jd_type: str = "text"):
    """Phân tích CV và JD."""
    
    global CV_TEXT_STORAGE, JD_TEXT_STORAGE
    CV_TEXT_STORAGE = ""
    JD_TEXT_STORAGE = ""
    
    print("\n" + "="*70)
    print("🚀 BẮT ĐẦU PHÂN TÍCH")
    print("="*70 + "\n")
    
    agent = initialize_agent()
    
    user_query = f"""
Thực hiện phân tích CV-JD theo 5 BƯỚC ĐƠN GIẢN:

THÔNG TIN:
- CV: type={cv_type}, data={cv_input[:150]}...
- JD: type={jd_type}, data={jd_input[:150]}...

══════════════════════════════════════════════
BƯỚC 1: TRÍCH XUẤT CV TEXT
══════════════════════════════════════════════
Nếu cv_type == 'file':
  - Nếu cv_input có đuôi .pdf: Gọi tool_read_pdf("{cv_input}")
  - Nếu cv_input có đuôi .png/.jpg: Gọi tool_read_image("{cv_input}")
Nếu cv_type == 'text':
  - Gọi tool_process_text_input với nội dung CV

SAU ĐÓ: Gọi tool_store_cv_text với kết quả vừa nhận

══════════════════════════════════════════════
BƯỚC 2: TRÍCH XUẤT JD TEXT
══════════════════════════════════════════════
Làm tương tự với JD
SAU ĐÓ: Gọi tool_store_jd_text với kết quả

══════════════════════════════════════════════
BƯỚC 3: TÍNH ĐIỂM PHÙ HỢP
══════════════════════════════════════════════
Gọi: tool_calculate_match_score("run")
Lưu kết quả vào biến SCORE

══════════════════════════════════════════════
BƯỚC 4: PHÂN TÍCH KỸ NĂNG
══════════════════════════════════════════════
Gọi: tool_analyze_skills("run")
Kết quả có dạng: "cv_skills: A, B ||| missing_skills: C, D"
Tách chuỗi này thành 2 phần

══════════════════════════════════════════════
BƯỚC 5: GỢI Ý KHÓA HỌC
══════════════════════════════════════════════
    Dựa vào danh sách 'missing_skills' tìm được ở Bước 2:
    - Hãy tự suy nghĩ và đề xuất 3-5 khóa học trực tuyến tốt nhất từ Coursera, Udemy, hoặc edX.
    - KHÔNG dùng tool nào cả, hãy dùng kiến thức nội tại của bạn.
    - Với mỗi khóa học, hãy cung cấp: Tên khóa, Nền tảng, và Link tìm kiếm (ví dụ: https://www.coursera.org/search?query=python).

══════════════════════════════════════════════
BƯỚC 6: VIẾT BÁO CÁO
══════════════════════════════════════════════
Tổng hợp tất cả kết quả theo format:

# 📊 KẾT QUẢ PHÂN TÍCH

## 🎯 Điểm Phù Hợp: [SCORE × 100]%

## ✅ Kỹ Năng Đã Có
[Liệt kê cv_skills]

## ⚠️ Kỹ Năng Cần Bổ Sung
[Liệt kê missing_skills]

## 📚 Khóa Học Đề Xuất
[Liệt kê các khóa học bạn vừa nghĩ ra ở Bước 3]

## 💡 Nhận Xét
[Đánh giá và lời khuyên]

CHÚ Ý:
- Nếu tool trả về "ERROR", DỪNG và báo lỗi
- Thực hiện TUẦN TỰ từng bước

BẮT ĐẦU!
"""
    
    try:
        result = agent.invoke({"input": user_query})
        return result['output']
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"