import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool, StructuredTool
from langchain import hub
from dotenv import load_dotenv
import json

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
    from tools_courses import get_course_recommendations
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    print("MAKE SURE THAT THEY EXIST IN THE data/ DIRECTORY")
    exit()


# ===== SIMPLE TOOLS =====
@tool
def tool_read_image(image_path: str) -> str:
    """
    Đọc văn bản từ file ảnh (jpg, png, jpeg).
    Input: đường dẫn file ảnh (string)
    Output: nội dung văn bản (string)
    """
    return extract_text_from_image(image_path)


@tool
def tool_process_text_input(raw_text: str) -> str:
    """
    Làm sạch văn bản thô do người dùng nhập.
    Input: văn bản thô (string)
    Output: văn bản đã làm sạch (string)
    """
    return process_raw_text(raw_text)


@tool
def tool_read_pdf(file_path: str) -> str:
    """
    Đọc văn bản từ file PDF.
    Input: đường dẫn file PDF (string)
    Output: nội dung văn bản (string)
    """
    return extract_text_hybrid_fixed(file_path)


@tool
def tool_calculate_match_score(texts_json: str) -> str:
    """
    Tính điểm phù hợp giữa CV và JD.
    Input: JSON string chứa cv_text và jd_text
    Ví dụ: '{"cv_text": "...", "jd_text": "..."}'
    Output: điểm phù hợp dạng string (ví dụ: "0.75")
    """
    try:
        data = json.loads(texts_json)
        cv_text = data.get('cv_text', '')
        jd_text = data.get('jd_text', '')
        score = calculate_similarity(cv_text, jd_text)
        return str(score)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def tool_analyze_skills(texts_json: str) -> str:
    """
    Phân tích kỹ năng trong CV so với JD.
    Input: JSON string chứa cv_text và jd_text
    Ví dụ: '{"cv_text": "...", "jd_text": "..."}'
    Output: JSON string chứa cv_skills và missing_skills
    """
    try:
        data = json.loads(texts_json)
        cv_text = data.get('cv_text', '')
        jd_text = data.get('jd_text', '')
        result = compare_skills_tool(cv_text, jd_text)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def tool_suggest_courses(skills_csv: str) -> str:
    """
    Gợi ý khóa học cho các kỹ năng thiếu.
    Input: danh sách kỹ năng phân cách bởi dấu phẩy (string)
    Ví dụ: "Python, Docker, AWS"
    Output: JSON string chứa danh sách khóa học
    """
    try:
        skills_list = [s.strip() for s in skills_csv.split(',') if s.strip()]
        courses = get_course_recommendations(skills_list)
        return json.dumps(courses, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def initialize_agent():
    """Khởi tạo LangChain Agent."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    tools = [
        tool_read_pdf,
        tool_read_image,
        tool_process_text_input,
        tool_calculate_match_score,
        tool_analyze_skills,
        tool_suggest_courses
    ]
    
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=25,
        early_stopping_method="generate"
    )
    
    return agent_executor


def analyze_cv_jd(cv_input: str, jd_input: str, cv_type: str = "text", jd_type: str = "text"):
    """
    Phân tích CV và JD.
    
    Args:
        cv_input: Đường dẫn file hoặc nội dung text của CV
        jd_input: Đường dẫn file hoặc nội dung text của JD
        cv_type: 'file' hoặc 'text'
        jd_type: 'file' hoặc 'text'
    
    Returns:
        str: Kết quả phân tích
    """
    
    print("\n" + "="*70)
    print("🚀 KHỞI ĐỘNG PHÂN TÍCH CV-JD")
    print("="*70 + "\n")
    
    agent = initialize_agent()
    
    user_query = f"""
Bạn là chuyên gia phân tích CV. Thực hiện phân tích theo 5 BƯỚC sau:

═══════════════════════════════════════════════════════════
📥 THÔNG TIN ĐẦU VÀO
═══════════════════════════════════════════════════════════
• CV: type={cv_type}, data={cv_input[:200] if len(cv_input) > 200 else cv_input}
• JD: type={jd_type}, data={jd_input[:200] if len(jd_input) > 200 else jd_input}

═══════════════════════════════════════════════════════════
📝 BƯỚC 1: TRÍCH XUẤT VĂN BẢN
═══════════════════════════════════════════════════════════

XỬ LÝ CV:
• Nếu cv_type=='file' và cv_input kết thúc bằng '.pdf':
  → Gọi: tool_read_pdf với input là "{cv_input}"
  
• Nếu cv_type=='file' và cv_input kết thúc bằng '.png'/'.jpg'/'.jpeg':
  → Gọi: tool_read_image với input là "{cv_input}"
  
• Nếu cv_type=='text':
  → Gọi: tool_process_text_input với input là nội dung CV

→ LƯU KẾT QUẢ vào biến: CV_TEXT

XỬ LÝ JD (tương tự):
• Áp dụng logic như trên với JD
→ LƯU KẾT QUẢ vào biến: JD_TEXT

═══════════════════════════════════════════════════════════
🎯 BƯỚC 2: TÍNH ĐIỂM PHÙ HỢP
═══════════════════════════════════════════════════════════

Tạo JSON string từ CV_TEXT và JD_TEXT:
json_input = '{{"cv_text": "' + CV_TEXT + '", "jd_text": "' + JD_TEXT + '"}}'

Gọi: tool_calculate_match_score với input là json_input

→ LƯU KẾT QUẢ vào biến: MATCH_SCORE (dạng số)

═══════════════════════════════════════════════════════════
✅ BƯỚC 3: PHÂN TÍCH KỸ NĂNG
═══════════════════════════════════════════════════════════

Tạo JSON string tương tự bước 2:
json_input = '{{"cv_text": "' + CV_TEXT + '", "jd_text": "' + JD_TEXT + '"}}'

Gọi: tool_analyze_skills với input là json_input

Kết quả trả về là JSON string, parse nó để lấy:
→ CV_SKILLS (danh sách kỹ năng có)
→ MISSING_SKILLS (danh sách kỹ năng thiếu)

═══════════════════════════════════════════════════════════
📚 BƯỚC 4: GỢI Ý KHÓA HỌC
═══════════════════════════════════════════════════════════

Chuyển MISSING_SKILLS thành chuỗi phân cách dấu phẩy:
Ví dụ: ["Python", "Docker"] → "Python, Docker"

Gọi: tool_suggest_courses với input là chuỗi này

→ LƯU KẾT QUẢ vào biến: COURSES (parse JSON để lấy danh sách)

═══════════════════════════════════════════════════════════
📊 BƯỚC 5: VIẾT BÁO CÁO CUỐI CÙNG
═══════════════════════════════════════════════════════════

Tổng hợp tất cả thông tin theo format:

---
# 📊 KẾT QUẢ PHÂN TÍCH CV-JD

## 🎯 Điểm Phù Hợp: [MATCH_SCORE × 100]%

**Đánh giá:** 
- ≥ 80%: ⭐⭐⭐ Xuất sắc - Hồ sơ rất phù hợp
- 60-79%: ⭐⭐ Tốt - Hồ sơ khá phù hợp  
- 40-59%: ⭐ Trung bình - Cần cải thiện
- < 40%: ⚠️ Thấp - Cần bổ sung nhiều

---

## ✅ Kỹ Năng Ứng Viên Đã Có

[Liệt kê từng kỹ năng trong CV_SKILLS, mỗi kỹ năng 1 dòng với bullet point]

---

## ⚠️ Kỹ Năng Cần Bổ Sung

[Liệt kê từng kỹ năng trong MISSING_SKILLS với giải thích ngắn tại sao quan trọng]

---

## 📚 Khóa Học Đề Xuất

[Với mỗi khóa học trong COURSES, hiển thị:
- Tên khóa học
- Link đăng ký
- Mô tả ngắn (nếu có)]

---

## 💡 Lời Khuyên

[Đưa ra 3-5 gợi ý cụ thể dựa trên kết quả phân tích để giúp ứng viên cải thiện CV]

---

⚠️ CHÚ Ý:
- Thực hiện TUẦN TỰ từ bước 1 → 5
- Kiểm tra output mỗi bước trước khi chuyển bước tiếp
- Nếu gặp lỗi, báo cáo ngay và DỪNG

HÃY BẮT ĐẦU TỪ BƯỚC 1!
"""
    
    try:
        result = agent.invoke({"input": user_query})
        return result['output']
    except Exception as e:
        error_msg = f"❌ Lỗi: {str(e)}"
        print(error_msg)
        return error_msg