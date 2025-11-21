# %%
import re

# %%
COMMON_SKILLS_DB = {
    # Programming Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "php", "ruby", "swift", "kotlin", "go", "rust", "html", "css", "sql", "r", "matlab",
    # Frameworks & Libraries
    "react", "angular", "vue", "django", "flask", "spring boot", "node.js", "express", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "keras", "jquery", "bootstrap", ".net",
    # Tools & Platforms
    "git", "github", "gitlab", "docker", "kubernetes", "aws", "azure", "google cloud", "gcp", "jenkins", "jira", "linux", "unix", "postman",
    # Databases
    "mysql", "postgresql", "mongodb", "oracle", "redis", "elasticsearch", "sql server",
    # Concepts / Soft Skills
    "machine learning", "deep learning", "data analysis", "data science", "artificial intelligence", "nlp", "computer vision", "agile", "scrum", "communication", "leadership", "problem solving", "teamwork", "project management"
}

# %%
def extract_skills_from_text(text: str) -> list:
    """
    Phiên bản 'nhẹ': Quét text và tìm từ khóa có trong danh sách skill.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = set()
    
    # Cách 1: Tìm chính xác từ (đơn giản)
    for skill in COMMON_SKILLS_DB:
        # Dùng regex để đảm bảo bắt đúng từ (ví dụ không bắt 'java' trong 'javascript')
        # \b là ranh giới từ
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
            
    return list(found_skills)

# %%
def compare_skills_tool(cv_text: str, jd_text: str) -> dict:
    """
    Tool so sánh kỹ năng, trả về skills khớp và skills thiếu.
    """
    # 1. Trích xuất skill từ CV
    cv_skills = set(extract_skills_from_text(cv_text))
    
    # 2. Trích xuất skill từ JD
    jd_skills = set(extract_skills_from_text(jd_text))
    
    # 3. So sánh
    matched = list(cv_skills.intersection(jd_skills))
    missing = list(jd_skills.difference(cv_skills))
    
    return {
        "cv_skills": list(cv_skills),
        "jd_skills": list(jd_skills),
        "matched_skills": matched,
        "missing_skills": missing
    }

# %%



