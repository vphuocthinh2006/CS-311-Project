import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain import hub
from dotenv import load_dotenv
import base64
import fitz  # pymupdf - để convert PDF sang images
import io
# Load environment variables
load_dotenv(".env")

# Import tools
try:
    from tools_ocr import process_raw_text
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
def tool_extract_text_from_file(file_path: str) -> str:
    """
    Trích xuất văn bản từ file (PDF hoặc ảnh) bằng GPT-4o Vision.
    Agent tự động xử lý mọi loại file.
    
    Input: đường dẫn file (PDF/PNG/JPG/JPEG)
    Output: nội dung văn bản được trích xuất
    """
    try:
        ext = file_path.lower().split('.')[-1]
        vision_llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        # Xử lý PDF: convert từng trang sang image rồi OCR
        if ext == 'pdf':
            pdf_doc = fitz.open(file_path)
            all_text = []
            
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                # Render page thành image với độ phân giải cao
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_bytes = pix.tobytes("png")
                base64_data = base64.b64encode(img_bytes).decode('utf-8')
                
                message = HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": f"Trích xuất TOÀN BỘ văn bản trong trang {page_num + 1} này. Giữ nguyên format và cấu trúc. Chỉ trả về text, không thêm giải thích."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_data}"}
                        }
                    ]
                )
                response = vision_llm.invoke([message])
                all_text.append(f"--- Trang {page_num + 1} ---\n{response.content}")
            
            pdf_doc.close()
            return "\n\n".join(all_text)
        
        # Xử lý ảnh: OCR trực tiếp
        else:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
                base64_data = base64.b64encode(file_bytes).decode('utf-8')
            
            mime_type = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Trích xuất TOÀN BỘ văn bản trong file này. Giữ nguyên format và cấu trúc. Chỉ trả về text, không thêm giải thích."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}
                    }
                ]
            )
            response = vision_llm.invoke([message])
            return response.content
            
    except Exception as e:
        return f"ERROR: Không thể đọc file - {str(e)}"



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
@tool
def tool_suggest_jobs(dummy: str = "run") -> str:
    """
    Gợi ý các vị trí việc làm phù hợp dựa trên CV đã lưu.
    Sử dụng kiến thức của agent để đề xuất (KHÔNG dùng tool khác).
    
    Input: bất kỳ (dummy parameter)
    Output: danh sách 5-7 vị trí việc làm phù hợp
    
    Agent hãy tự phân tích CV và đưa ra gợi ý dựa trên:
    - Kỹ năng hiện tại
    - Kinh nghiệm làm việc
    - Ngành nghề
    - Mức độ seniority
    
    Format output:
    1. [Tên vị trí] - [Lý do phù hợp ngắn gọn]
    2. ...
    """
    global CV_TEXT_STORAGE
    
    if not CV_TEXT_STORAGE:
        return "ERROR: Chưa có CV. Vui lòng phân tích CV trước."
    
    # Trả về CV để agent tự phân tích
    return f"CV_CONTENT_FOR_ANALYSIS:\n{CV_TEXT_STORAGE[:2000]}"

def initialize_agent():
    """Khởi tạo Agent."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    tools = [
        tool_extract_text_from_file,
        tool_process_text_input,
        tool_store_cv_text,
        tool_store_jd_text,
        tool_calculate_match_score,
        tool_analyze_skills,
        tool_suggest_jobs
    ]
    system_message = """Bạn là AI Recruitment Expert chuyên nghiệp.

NHIỆM VỤ:
- Phân tích CV và JD
- Tính điểm phù hợp
- So sánh kỹ năng
- Đề xuất khóa học
- Gợi ý việc làm phù hợp

QUAN TRỌNG:
- Với file (PDF/ảnh): Dùng tool_extract_text_from_file để OCR
- Với text: Dùng tool_process_text_input để làm sạch
- Luôn lưu CV/JD sau khi trích xuất
- Khi gợi ý việc làm: Phân tích CV và tự đưa ra gợi ý dựa trên kiến thức của bạn
- Khi gợi ý khóa học: Tự nghĩ ra các khóa học phù hợp từ Coursera, Udemy, edX
- Trả lời bằng tiếng Việt, chuyên nghiệp, thân thiện"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
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
  - Gọi tool_extract_text_from_file("{cv_input}") để OCR file PDF/ảnh
Nếu cv_type == 'text':
  - Gọi tool_process_text_input với nội dung CV

SAU ĐÓ: Gọi tool_store_cv_text với kết quả vừa nhận

══════════════════════════════════════════════
BƯỚC 2: TRÍCH XUẤT JD TEXT
══════════════════════════════════════════════
Nếu jd_type == 'file':
  - Gọi tool_extract_text_from_file("{jd_input}") để OCR file PDF/ảnh
Nếu jd_type == 'text':
  - Gọi tool_process_text_input với nội dung JD
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
    
def find_suitable_jobs():
    """
    Tìm việc làm phù hợp với CV đã lưu.
    
    Returns:
        str: Danh sách việc làm gợi ý
    """
    global CV_TEXT_STORAGE
    
    if not CV_TEXT_STORAGE:
        return "❌ Chưa có CV. Vui lòng phân tích CV ở tab 'Phân Tích CV-JD' trước!"
    
    print("\n🔍 TÌM VIỆC LÀM PHÙ HỢP...\n")
    
    agent = initialize_agent()
    
    query = f"""
Dựa vào CV đã lưu, hãy gợi ý 5-7 vị trí việc làm PHÙ HỢP NHẤT.

CV:
{CV_TEXT_STORAGE[:2000]}

YÊU CẦU:
- Phân tích kỹ năng, kinh nghiệm, ngành nghề từ CV
- Đề xuất TÊN VỊ TRÍ/VAI TRÒ cụ thể (VD: "Senior Python Developer", "AI Engineer")
- KHÔNG đề xuất tên công ty
- Xếp theo độ phù hợp từ cao → thấp
- Giải thích ngắn gọn (1-2 câu) tại sao phù hợp

FORMAT:

# 💼 GỢI Ý VIỆC LÀM PHÙ HỢP

## 🎯 Phân Tích Hồ Sơ
[Tóm tắt ngắn: kỹ năng chính, kinh nghiệm, level]

## 📋 Danh Sách Vị Trí Đề Xuất

### 1. [Tên vị trí 1]
**Độ phù hợp:** ⭐⭐⭐⭐⭐ (Rất cao)
**Lý do:** [Giải thích ngắn]

### 2. [Tên vị trí 2]
**Độ phù hợp:** ⭐⭐⭐⭐ (Cao)
**Lý do:** [Giải thích ngắn]

[... tiếp tục cho đến vị trí 5-7]

## 💡 Lời Khuyên
[Gợi ý về hướng phát triển sự nghiệp]
"""
    
    try:
        result = agent.invoke({"input": query})
        return result['output']
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"

def find_hiring_companies():
    """
    Tìm các công ty đang tuyển dụng phù hợp với CV.
    
    Returns:
        str: Danh sách công ty và link tuyển dụng
    """
    global CV_TEXT_STORAGE
    
    if not CV_TEXT_STORAGE:
        return "❌ Chưa có CV. Vui lòng phân tích CV ở tab 'Phân Tích CV-JD' trước!"
    
    print("\n🏢 TÌM CÔNG TY ĐANG TUYỂN DỤNG...\n")
    
    agent = initialize_agent()
    
    query = f"""
Dựa vào CV đã lưu, hãy gợi ý 8-10 CÔNG TY đang tuyển dụng phù hợp nhất.

CV:
{CV_TEXT_STORAGE[:2000]}

YÊU CẦU:
1. Phân tích kỹ năng và ngành nghề từ CV
2. Đề xuất CÁC CÔNG TY THẬT (có tên, có thương hiệu) ở Việt Nam và quốc tế
3. Ưu tiên công ty lớn, có uy tín, đang tuyển nhiều
4. Với mỗi công ty, cung cấp:
   - Tên công ty
   - Ngành nghề/Lĩnh vực
   - Tại sao phù hợp (1 câu)
   - Link tuyển dụng THẬT (career page hoặc LinkedIn)

QUAN TRỌNG: Chỉ đề xuất CÔNG TY THẬT, KHÔNG bịa tên công ty!

FORMAT:

# 🏢 CÔNG TY ĐANG TUYỂN DỤNG

## 🎯 Ngành Nghề Phù Hợp
[Liệt kê 2-3 ngành nghề chính dựa trên CV]

## 📋 Danh Sách Công Ty

### 🇻🇳 Công Ty Tại Việt Nam

#### 1. [Tên Công Ty]
- **Ngành:** [Ngành nghề]
- **Phù hợp vì:** [Lý do ngắn]
- **🔗 Tuyển dụng:** [Link career page thật, ví dụ: https://careers.fpt.com.vn]

#### 2. [Tên Công Ty]
...

### 🌍 Công Ty Quốc Tế (Remote/Hybrid)

#### 1. [Tên Công Ty]
- **Ngành:** [Ngành nghề]
- **Phù hợp vì:** [Lý do ngắn]
- **🔗 Tuyển dụng:** [Link career page thật]

...

## 🔍 Link Tìm Việc Nhanh

Dựa vào kỹ năng trong CV, tạo các link tìm kiếm sẵn:

| Nền tảng | Link tìm kiếm |
|----------|---------------|
| LinkedIn | https://www.linkedin.com/jobs/search/?keywords=[keyword từ CV] |
| Indeed VN | https://vn.indeed.com/jobs?q=[keyword] |
| TopDev | https://topdev.vn/viec-lam-it/[keyword] |
| ITviec | https://itviec.com/it-jobs/[keyword] |

## 💡 Mẹo Ứng Tuyển
[2-3 tips ngắn gọn về cách ứng tuyển hiệu quả]
"""
    
    try:
        result = agent.invoke({"input": query})
        return result['output']
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"

def chat_with_agent(user_message: str):
    """
    Chat tự do với agent (không lưu history).
    
    Args:
        user_message: Câu hỏi của người dùng
    
    Returns:
        str: Phản hồi của agent
    """
    agent = initialize_agent()
    global CV_TEXT_STORAGE, JD_TEXT_STORAGE
    context = ""
    if CV_TEXT_STORAGE:
        context += f"\n[CV đã lưu: {len(CV_TEXT_STORAGE)} ký tự]"
    if JD_TEXT_STORAGE:
        context += f"\n[JD đã lưu: {len(JD_TEXT_STORAGE)} ký tự]"
    
    full_query = f"{context}\n\nCÂU HỎI: {user_message}\n\nHãy trả lời dựa trên thông tin đã lưu (nếu có) và kiến thức của bạn."
    try:
        result = agent.invoke({"input": full_query})
        return result['output']
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"