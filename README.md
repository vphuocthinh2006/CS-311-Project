# CS-311-Project
---

# 🧩 Project Plan: Smart Resume Analyzer + Company Fit Finder

## 🎯 Mục tiêu chính

1. **CV Analyzer**

   * Phân tích bố cục CV (layout).
   * Đưa feedback chi tiết (thiếu skill, thiếu section, keyword chưa match).

2. **Company Fit Finder**

   * So khớp CV với Job Description (JD).
   * Gợi ý công ty/position phù hợp nhất.
   * Đưa ra lý do (match/thiếu skill nào).

3. **App Desktop**

   * Giao diện kéo-thả CV PDF.
   * Hiển thị feedback + danh sách công ty gợi ý.

---

## 🗂️ Công nghệ & Toolchain

* **CV Layout & Text Extraction**:

  * `PyMuPDF` hoặc `pdfplumber` (trích xuất text).
  * `LayoutLM` hoặc `DocFormer` (hiểu bố cục CV).

* **NLP (Feedback + Skill Extraction)**:

  * `spaCy` (NER cho skill, experience).
  * `sentence-transformers` (SBERT) hoặc OpenAI embeddings.
  * Fine-tuned BERT/GPT cho **feedback tự động**.

* **Matching & Ranking**:

  * `FAISS` (similarity search).
  * Cosine similarity trên embeddings.

* **App Desktop**:

  * **PyQt5/PySide6** (Python GUI).
  * Hoặc **Electron + FastAPI backend** (nếu muốn UI đẹp kiểu web).

---

## 📅 Roadmap chi tiết (6 tuần)

### 🔹 Tuần 1: Foundation

* Thu thập CV mẫu (PDF) và vài JD thật từ LinkedIn/VietnamWorks.
* Xây pipeline đọc CV PDF → trích xuất text + layout cơ bản.
* Làm giao diện desktop đơn giản (drag & drop CV).

**Deliverable**: App mở được CV, hiển thị text.

---

### 🔹 Tuần 2: CV Analyzer MVP

* Dùng NLP (spaCy + keyword matching) để phát hiện:

  * Skills, Education, Experience, Certificates.
* Sinh feedback cơ bản: thiếu skill, thiếu section.
* Hiển thị feedback trên GUI.

**Deliverable**: Người dùng thả CV vào → feedback text hiển thị.

---

### 🔹 Tuần 3: Job Description Parser

* Xây parser cho JD (text hoặc JSON mẫu).
* Trích xuất skill, yêu cầu từ JD.
* Chuẩn hóa skill thành embedding (SBERT / OpenAI).

**Deliverable**: Hệ thống đọc được JD, liệt kê skill yêu cầu.

---

### 🔹 Tuần 4: Matching System

* Chuyển CV + JD thành embedding vector.
* Tính cosine similarity → match score.
* Bổ sung “gap analysis” (skill thiếu, kinh nghiệm chưa đủ).

**Deliverable**: Output dạng:

```
JD: AI Engineer @ FPT
Match: 82%
Missing: Docker, TensorFlow
Feedback: Nên bổ sung dự án ML có Docker.
```

---

### 🔹 Tuần 5: Company Fit Finder

* Tạo danh sách JD (crawl hoặc nhập tay 5–10 JD).
* So khớp CV → gợi ý top 3 công ty phù hợp.
* Hiển thị lý do match/mismatch.

**Deliverable**:

```
Top companies for you:
1. FPT AI Lab – match 85% (thiếu Docker).
2. VNG – match 78% (thiếu GoLang).
3. LINE Vietnam – match 70% (thiếu NLP).
```

---

### 🔹 Tuần 6: UI/UX + Polish

* Làm UI gọn gàng (tab “CV Feedback” + tab “Company Fit”).
* Cho phép tải lại CV đã chỉnh sửa → hệ thống so sánh trước/sau.
* (Optional) Tích hợp API LinkedIn để lấy JD tự động.
* Đóng gói app thành `.exe` (PyInstaller) hoặc desktop app (Electron).

**Deliverable**: App desktop hoàn chỉnh, chạy offline.

---

## 📊 Tổng kết giá trị

* **Sinh viên dùng**: chỉnh CV, tìm JD phù hợp → tăng cơ hội xin việc.
* **Nhà tuyển dụng dùng**: so khớp nhanh ứng viên.
* **Bạn**: có một project **NLP + CV real-world** để showcase trên GitHub + portfolio, cực kỳ ấn tượng khi apply việc.

---

Tuyệt — dưới đây là **lộ trình cực kỳ chi tiết** (MVP → production-ready) để bạn phát triển **Smart Resume Analyzer + Company Fit Finder + CV Booster**. Mình chia nhỏ thành milestones, tasks từng bước, nội dung kỹ thuật rõ ràng, file/schema mẫu, test plan, deployment và stretch-goals — để bạn có thể copy — paste làm theo ngay.

# Tổng quan ngắn

Mục tiêu: từ **CV (PDF)** tạo profile cấu trúc → phân tích, gợi ý chỉnh sửa (rewrite/ATS/keyword), sinh CV tùy chỉnh cho từng JD → match với JD từ nguồn (crawl/upload) → gợi ý công ty phù hợp + learning path.
MVP focus: chính xác trích xuất (skills/exp), feedback cụ thể, company ranking.

---

# MVP (phải có)

1. Drag & drop PDF CV → extract text + layout.
2. Trích xuất structured profile (skills, experiences, education, projects, certs).
3. So khớp 1 JD → skill gap + suggestions + AI rewrite cho vài bullet points.
4. Company Fit: so sánh CV với 5–10 JD mẫu → top-3 companies + lý do.
5. Desktop GUI đơn giản (PyQt/Electron) với export PDF/Word của CV đã rewrite.

---

# Kiến trúc hệ thống (tóm tắt)

* Frontend: Electron (React) hoặc PyQt5 (Python).
* Backend: FastAPI (Python) local (chạy cùng máy người dùng).
* Components: PDF reader → Layout parser → NLP extractor → Embedding store + FAISS → LLM prompt module (rewrite/cover letter) → UI.
* Storage: local JSON files per user; optional SQLite để index JD/companies.
* Models/libs: PyMuPDF/pdfplumber, Tesseract/EasyOCR, LayoutLM/Donut/DocTR, spaCy, sentence-transformers, FAISS, HuggingFace transformers or OpenAI for LLM.

---

# Schema dữ liệu mẫu (parsed\_cv.json)

```json
{
  "meta": {"filename":"cv.pdf","parsed_at":"2025-09-14T12:00:00+07:00"},
  "personal": {"name":"Vo Phuoc Thinh","email":"thinh@example.com","phone":"+84...","location":"Ho Chi Minh"},
  "summary":"Short professional summary...",
  "skills":[{"name":"Python","level":"advanced"},{"name":"Computer Vision","level":"intermediate"}],
  "projects":[{"title":"Image Classifier","desc":"Used PyTorch...","github":"https://github.com/...","start":"2024-05","end":"2024-08"}],
  "experience":[{"role":"Intern","company":"ABC","start":"2023-06","end":"2023-09","desc":"..."}],
  "education":[{"degree":"BSc Computer Science","school":"UIT","year":"2024"}],
  "certificates":["AWS Certified Cloud Practitioner"],
  "embeddings":{"skills_vector":[0.00123, ...], "full_cv_vector":[...]}
}
```

---

# Lộ trình cực kỳ chi tiết (6 giai đoạn, mỗi giai đoạn chia tasks nhỏ)

## Giai đoạn 0 — Chuẩn bị (1–2 ngày)

* Mục tiêu: chuẩn bị dataset, môi trường dev.
* Tasks:

  * Tạo repo GitHub (branch: `main`, `dev`).
  * Chuẩn dev env: Python 3.10+, virtualenv, nodejs nếu dùng Electron.
  * Cài libs cơ bản: `pip install fastapi uvicorn sentence-transformers spaCy pymupdf pdfplumber faiss-cpu transformers torch`.
  * Thu thập dữ liệu: ít nhất 50 CV PDF (ẩn danh) + 50 JD (các vị trí mục tiêu).
  * Tạo notebook `explore.ipynb` để thử extract text từ PDF.

## Giai đoạn 1 — PDF extraction + layout (MVP core)

* Mục tiêu: đọc PDF, tách block (header, skill, exp).
* Tasks chi tiết:

  1. Dùng PyMuPDF/pdfplumber để lấy text + vị trí bounding boxes. Lưu raw text + bbox.

     * Code gợi ý: đọc page → `page.get_text("dict")` để lấy blocks.
  2. (Optional) OCR cho ảnh trong PDF: Tesseract/EasyOCR. Chỉ bật khi text missing.
  3. Heuristic rule-based layout parser: rules for headings (all caps, bold, keywords: "Experience", "Education", "Skills").

     * Viết rules sequence: detect headings → assign blocks to sections by proximity.
  4. (Advanced) Thử LayoutLM/DocTR cho chính xác hơn: fine-tune nhỏ nếu cần.
* Deliverable: `parsed_cv.json` generation function.

## Giai đoạn 2 — Skill & entity extraction (NLP)

* Mục tiêu: tự động nhận diện skills, role, dates, company, project.
* Tasks:

  1. Install spaCy + custom NER model or use rule-based + keyword list (fast).

     * Build canonical skill dictionary (normalize synonyms: "CV" → "Computer Vision").
  2. Extract experiences: parse date ranges (regex), company names (heuristic + NER).
  3. Normalize skills: map raw tokens to canonical names using fuzzy matching (fuzzywuzzy/rapidfuzz).
  4. Test on sample set; compute extraction accuracy (precision/recall).
* Deliverable: structured profile with canonicalized skills.

## Giai đoạn 3 — Embeddings & Matching core

* Mục tiêu: chuyển CV + JD → vectors; xây similarity pipeline.
* Tasks:

  1. Choose embedding model: `sentence-transformers/all-mpnet-base-v2` (good default offline) OR OpenAI embeddings (if cloud).
  2. Compute embeddings:

     * `full_cv_vector` = embed(concat(summary + top N bullet points))
     * `skills_vector` = embed("Python, Docker, TensorFlow")
     * For each JD: compute `jd_vector` and `jd_skill_vector`.
  3. Index JD vectors in FAISS (flat index for MVP).
  4. Implement similarity scoring:

     * score\_full = cosine(full\_cv\_vector, jd\_vector)
     * skill\_overlap = jaccard(skills\_cv, skills\_jd) normalized
     * final\_score = weighted(sum)
     * Expose factors for explainability (show breakdown).
* Deliverable: ranking API `POST /match` returning top-K JD with breakdown.

## Giai đoạn 4 — Feedback generator & AI rewrite

* Mục tiêu: feedback chi tiết + rewrite bullets, cover letter.
* Tasks:

  1. Build rule-based suggestions (ATS warnings, missing sections).
  2. Integrate LLM for high-quality rewrite:

     * If offline: use local LLM (Llama-like) or HF `gpt-neo` small; for quality, use OpenAI API (GPT-4/4o) if permitted.
     * Prompt templates:

       * Input: original bullet, role, skills. Output: rewritten bullet (concise, action/result).
  3. Create `rewrite_batch` endpoint: take top 5 bullets → return rewrites with variations.
  4. Add cover letter generator (prompted with company JD + CV summary).
* Deliverable: `rewrite_preview` modal in UI; download rewritten CV.

## Giai đoạn 5 — Company Fit Finder + UI polish

* Mục tiêu: crawl/import JD pool, rank companies, improve UI/UX.
* Tasks:

  1. Data source: manual JD upload / scrape LinkedIn/VietnamWorks (scraper optional).

     * Note: scraping LinkedIn may violate TOS; prefer manual upload or public job boards with API.
  2. Implement company profile metadata: `industry, size, remote, required_skills`.
  3. Ranking view: top 10 companies with reasons and action items (what to add to CV to bump score).
  4. UI polish: tabs — CV Feedback / Rewrites / Company Fit / Apply Actions.
  5. Export: allow user to save new CV as PDF or DOCX (python-docx / reportlab).
* Deliverable: finished desktop app with full workflow.

## Giai đoạn 6 — Testing, evaluation, deploy & optional extras

* Mục tiêu: harden, test, package.
* Tasks:

  1. Unit tests for parser, NER, embeddings, matching logic.
  2. Create evaluation dataset (label skills in 100 CVs) → measure extraction metrics.
  3. UX testing: 5 users run their CVs → collect qualitative feedback.
  4. Packaging:

     * If Python GUI: `pyinstaller --onefile main.py` and bundle.
     * If Electron + backend: build Electron app and include Python backend in installer (or deliver as separate binary).
  5. Optional: small backend cloud for heavy LLM calls (if using OpenAI).
* Deliverable: distributable `.exe` or `.dmg` and README install guide.

---

# Chi tiết kỹ thuật / mẫu code & prompts (để bạn copy luôn)

## 1) Tách text từ PDF (snippet)

```python
import fitz  # PyMuPDF
doc = fitz.open("cv.pdf")
pages = []
for page in doc:
    blocks = page.get_text("dict")["blocks"]
    pages.append(blocks)
# Save pages -> use bbox info for layout
```

## 2) Embedding với sentence-transformers

```python
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("all-mpnet-base-v2")
vec = model.encode("Python, Computer Vision", convert_to_tensor=True)
# cosine:
sim = util.cos_sim(vec1, vec2)
```

## 3) Prompt mẫu cho rewrite (OpenAI/GPT)

```
PROMPT:
You are an expert resume writer. Rewrite the following resume bullet to be professional, result-oriented, and concise. Keep it to one sentence. Include metric or impact if possible.

Original bullet: "built small tool to process images"
Role: "Computer Vision Intern"
Skills: "Python, OpenCV, PyTorch"

OUTPUT: <rewritten bullet>
```

---

# UI / UX Mockup (mô tả nhanh)

1. Left panel: File upload + parsed sections (editable inline).
2. Middle panel: CV preview with highlights (yellow = missing keywords, red = ATS fail).
3. Right panel: Suggestions:

   * Skill Gap (list + priority)
   * Rewrite suggestions (Accept / Reject / Edit)
   * Top Companies (score + why)
4. Top bar: Export (PDF/DOCX), Generate Cover Letter, Customize for Job.

---

# KPI, đánh giá chất lượng & test plan

* **Extraction accuracy**: target precision ≥ 0.85 for skills (on test set).
* **Matching alignment**: A/B test final\_score ranking: recruiter blind test (n=20) → % agreement with human ranking ≥ 0.7.
* **User success metric**: % users who submit revised CV to apply within 2 weeks (collect via optional opt-in).
* **Unit tests**: parser edge cases, dates parsing, normalization.

# Risks & mitigation

* **Poor OCR on images** → mitigation: prompt user to upload original PDF or request clearer scan; fallback OCR.
* **Ambiguous skill names** → use canonical dictionary + fuzzy matching + manual mapping UI.
* **Legal/TOS scraping JD** → avoid scraping LinkedIn; use official APIs or manual uploading.
* **Data privacy** → all processing local by default; if using cloud LLMs, prompt consent and mask PII.

---

# Stretch goals (sẽ khiến app “rất nổi bật”)

* CV A/B testing: track which version got replies (user reports).
* Auto GitHub project summarizer (scan repo, auto-generate project blurb).
* Recruiter simulation: 10-sec scan score + “Why rejected in 10s” heatmap.
* Marketplace: connect to local recruiters / internships.
* SaaS mode: multi-user, analytics dashboard, employer API.

---

# Triển khai & vận hành (ngắn gọn)

* Local-first: tất cả xử lý offline (privacy). Dùng OpenAI/Cloud LLM chỉ khi user bật.
* Packaging: tạo installer cho Windows/macOS + README.
* Release: GitHub repo + demo video (2–3 phút) + sample dataset (anonymized) → giúp tuyển dụng tin tưởng.

---

# Checklist triển khai (từng bước, tick-off)

1. [ ] Repo + env setup.
2. [ ] PDF → parsed\_cv.json pipeline.
3. [ ] Skill extraction + canonicalization.
4. [ ] Embedding & FAISS index.
5. [ ] Single JD match API + explainability.
6. [ ] Rewrite API (LLM prompts).
7. [ ] Company ranking + UI.
8. [ ] Export rewritten CV & cover letter.
9. [ ] Unit tests + evaluation.
10. [ ] Packaging + release.

---

# Ba hành động bạn có thể làm ngay (cực thực tế)

1. Tạo repo GitHub và commit `README` + `requirements.txt`.
2. Lấy 10 CV PDF (ẩn danh) + 10 JD, chạy thử snippet PyMuPDF để xem cấu trúc.
3. Cài `sentence-transformers` và encode một CV sample + một JD sample, tính cosine similarity — bạn sẽ thấy pipeline cơ bản chạy được.

---
Tuyệt — dưới đây là **lộ trình cực kỳ chi tiết** (MVP → production-ready) để bạn phát triển **Smart Resume Analyzer + Company Fit Finder + CV Booster**. Mình chia nhỏ thành milestones, tasks từng bước, nội dung kỹ thuật rõ ràng, file/schema mẫu, test plan, deployment và stretch-goals — để bạn có thể copy — paste làm theo ngay.

# Tổng quan ngắn

Mục tiêu: từ **CV (PDF)** tạo profile cấu trúc → phân tích, gợi ý chỉnh sửa (rewrite/ATS/keyword), sinh CV tùy chỉnh cho từng JD → match với JD từ nguồn (crawl/upload) → gợi ý công ty phù hợp + learning path.
MVP focus: chính xác trích xuất (skills/exp), feedback cụ thể, company ranking.

---

# MVP (phải có)

1. Drag & drop PDF CV → extract text + layout.
2. Trích xuất structured profile (skills, experiences, education, projects, certs).
3. So khớp 1 JD → skill gap + suggestions + AI rewrite cho vài bullet points.
4. Company Fit: so sánh CV với 5–10 JD mẫu → top-3 companies + lý do.
5. Desktop GUI đơn giản (PyQt/Electron) với export PDF/Word của CV đã rewrite.

---

# Kiến trúc hệ thống (tóm tắt)

* Frontend: Electron (React) hoặc PyQt5 (Python).
* Backend: FastAPI (Python) local (chạy cùng máy người dùng).
* Components: PDF reader → Layout parser → NLP extractor → Embedding store + FAISS → LLM prompt module (rewrite/cover letter) → UI.
* Storage: local JSON files per user; optional SQLite để index JD/companies.
* Models/libs: PyMuPDF/pdfplumber, Tesseract/EasyOCR, LayoutLM/Donut/DocTR, spaCy, sentence-transformers, FAISS, HuggingFace transformers or OpenAI for LLM.

---

# Schema dữ liệu mẫu (parsed\_cv.json)

```json
{
  "meta": {"filename":"cv.pdf","parsed_at":"2025-09-14T12:00:00+07:00"},
  "personal": {"name":"Vo Phuoc Thinh","email":"thinh@example.com","phone":"+84...","location":"Ho Chi Minh"},
  "summary":"Short professional summary...",
  "skills":[{"name":"Python","level":"advanced"},{"name":"Computer Vision","level":"intermediate"}],
  "projects":[{"title":"Image Classifier","desc":"Used PyTorch...","github":"https://github.com/...","start":"2024-05","end":"2024-08"}],
  "experience":[{"role":"Intern","company":"ABC","start":"2023-06","end":"2023-09","desc":"..."}],
  "education":[{"degree":"BSc Computer Science","school":"UIT","year":"2024"}],
  "certificates":["AWS Certified Cloud Practitioner"],
  "embeddings":{"skills_vector":[0.00123, ...], "full_cv_vector":[...]}
}
```

---

# Lộ trình cực kỳ chi tiết (6 giai đoạn, mỗi giai đoạn chia tasks nhỏ)

## Giai đoạn 0 — Chuẩn bị (1–2 ngày)

* Mục tiêu: chuẩn bị dataset, môi trường dev.
* Tasks:

  * Tạo repo GitHub (branch: `main`, `dev`).
  * Chuẩn dev env: Python 3.10+, virtualenv, nodejs nếu dùng Electron.
  * Cài libs cơ bản: `pip install fastapi uvicorn sentence-transformers spaCy pymupdf pdfplumber faiss-cpu transformers torch`.
  * Thu thập dữ liệu: ít nhất 50 CV PDF (ẩn danh) + 50 JD (các vị trí mục tiêu).
  * Tạo notebook `explore.ipynb` để thử extract text từ PDF.

## Giai đoạn 1 — PDF extraction + layout (MVP core)

* Mục tiêu: đọc PDF, tách block (header, skill, exp).
* Tasks chi tiết:

  1. Dùng PyMuPDF/pdfplumber để lấy text + vị trí bounding boxes. Lưu raw text + bbox.

     * Code gợi ý: đọc page → `page.get_text("dict")` để lấy blocks.
  2. (Optional) OCR cho ảnh trong PDF: Tesseract/EasyOCR. Chỉ bật khi text missing.
  3. Heuristic rule-based layout parser: rules for headings (all caps, bold, keywords: "Experience", "Education", "Skills").

     * Viết rules sequence: detect headings → assign blocks to sections by proximity.
  4. (Advanced) Thử LayoutLM/DocTR cho chính xác hơn: fine-tune nhỏ nếu cần.
* Deliverable: `parsed_cv.json` generation function.

## Giai đoạn 2 — Skill & entity extraction (NLP)

* Mục tiêu: tự động nhận diện skills, role, dates, company, project.
* Tasks:

  1. Install spaCy + custom NER model or use rule-based + keyword list (fast).

     * Build canonical skill dictionary (normalize synonyms: "CV" → "Computer Vision").
  2. Extract experiences: parse date ranges (regex), company names (heuristic + NER).
  3. Normalize skills: map raw tokens to canonical names using fuzzy matching (fuzzywuzzy/rapidfuzz).
  4. Test on sample set; compute extraction accuracy (precision/recall).
* Deliverable: structured profile with canonicalized skills.

## Giai đoạn 3 — Embeddings & Matching core

* Mục tiêu: chuyển CV + JD → vectors; xây similarity pipeline.
* Tasks:

  1. Choose embedding model: `sentence-transformers/all-mpnet-base-v2` (good default offline) OR OpenAI embeddings (if cloud).
  2. Compute embeddings:

     * `full_cv_vector` = embed(concat(summary + top N bullet points))
     * `skills_vector` = embed("Python, Docker, TensorFlow")
     * For each JD: compute `jd_vector` and `jd_skill_vector`.
  3. Index JD vectors in FAISS (flat index for MVP).
  4. Implement similarity scoring:

     * score\_full = cosine(full\_cv\_vector, jd\_vector)
     * skill\_overlap = jaccard(skills\_cv, skills\_jd) normalized
     * final\_score = weighted(sum)
     * Expose factors for explainability (show breakdown).
* Deliverable: ranking API `POST /match` returning top-K JD with breakdown.

## Giai đoạn 4 — Feedback generator & AI rewrite

* Mục tiêu: feedback chi tiết + rewrite bullets, cover letter.
* Tasks:

  1. Build rule-based suggestions (ATS warnings, missing sections).
  2. Integrate LLM for high-quality rewrite:

     * If offline: use local LLM (Llama-like) or HF `gpt-neo` small; for quality, use OpenAI API (GPT-4/4o) if permitted.
     * Prompt templates:

       * Input: original bullet, role, skills. Output: rewritten bullet (concise, action/result).
  3. Create `rewrite_batch` endpoint: take top 5 bullets → return rewrites with variations.
  4. Add cover letter generator (prompted with company JD + CV summary).
* Deliverable: `rewrite_preview` modal in UI; download rewritten CV.

## Giai đoạn 5 — Company Fit Finder + UI polish

* Mục tiêu: crawl/import JD pool, rank companies, improve UI/UX.
* Tasks:

  1. Data source: manual JD upload / scrape LinkedIn/VietnamWorks (scraper optional).

     * Note: scraping LinkedIn may violate TOS; prefer manual upload or public job boards with API.
  2. Implement company profile metadata: `industry, size, remote, required_skills`.
  3. Ranking view: top 10 companies with reasons and action items (what to add to CV to bump score).
  4. UI polish: tabs — CV Feedback / Rewrites / Company Fit / Apply Actions.
  5. Export: allow user to save new CV as PDF or DOCX (python-docx / reportlab).
* Deliverable: finished desktop app with full workflow.

## Giai đoạn 6 — Testing, evaluation, deploy & optional extras

* Mục tiêu: harden, test, package.
* Tasks:

  1. Unit tests for parser, NER, embeddings, matching logic.
  2. Create evaluation dataset (label skills in 100 CVs) → measure extraction metrics.
  3. UX testing: 5 users run their CVs → collect qualitative feedback.
  4. Packaging:

     * If Python GUI: `pyinstaller --onefile main.py` and bundle.
     * If Electron + backend: build Electron app and include Python backend in installer (or deliver as separate binary).
  5. Optional: small backend cloud for heavy LLM calls (if using OpenAI).
* Deliverable: distributable `.exe` or `.dmg` and README install guide.

---

# Chi tiết kỹ thuật / mẫu code & prompts (để bạn copy luôn)

## 1) Tách text từ PDF (snippet)

```python
import fitz  # PyMuPDF
doc = fitz.open("cv.pdf")
pages = []
for page in doc:
    blocks = page.get_text("dict")["blocks"]
    pages.append(blocks)
# Save pages -> use bbox info for layout
```

## 2) Embedding với sentence-transformers

```python
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("all-mpnet-base-v2")
vec = model.encode("Python, Computer Vision", convert_to_tensor=True)
# cosine:
sim = util.cos_sim(vec1, vec2)
```

## 3) Prompt mẫu cho rewrite (OpenAI/GPT)

```
PROMPT:
You are an expert resume writer. Rewrite the following resume bullet to be professional, result-oriented, and concise. Keep it to one sentence. Include metric or impact if possible.

Original bullet: "built small tool to process images"
Role: "Computer Vision Intern"
Skills: "Python, OpenCV, PyTorch"

OUTPUT: <rewritten bullet>
```

---

# UI / UX Mockup (mô tả nhanh)

1. Left panel: File upload + parsed sections (editable inline).
2. Middle panel: CV preview with highlights (yellow = missing keywords, red = ATS fail).
3. Right panel: Suggestions:

   * Skill Gap (list + priority)
   * Rewrite suggestions (Accept / Reject / Edit)
   * Top Companies (score + why)
4. Top bar: Export (PDF/DOCX), Generate Cover Letter, Customize for Job.

---

# KPI, đánh giá chất lượng & test plan

* **Extraction accuracy**: target precision ≥ 0.85 for skills (on test set).
* **Matching alignment**: A/B test final\_score ranking: recruiter blind test (n=20) → % agreement with human ranking ≥ 0.7.
* **User success metric**: % users who submit revised CV to apply within 2 weeks (collect via optional opt-in).
* **Unit tests**: parser edge cases, dates parsing, normalization.

# Risks & mitigation

* **Poor OCR on images** → mitigation: prompt user to upload original PDF or request clearer scan; fallback OCR.
* **Ambiguous skill names** → use canonical dictionary + fuzzy matching + manual mapping UI.
* **Legal/TOS scraping JD** → avoid scraping LinkedIn; use official APIs or manual uploading.
* **Data privacy** → all processing local by default; if using cloud LLMs, prompt consent and mask PII.

---

# Stretch goals (sẽ khiến app “rất nổi bật”)

* CV A/B testing: track which version got replies (user reports).
* Auto GitHub project summarizer (scan repo, auto-generate project blurb).
* Recruiter simulation: 10-sec scan score + “Why rejected in 10s” heatmap.
* Marketplace: connect to local recruiters / internships.
* SaaS mode: multi-user, analytics dashboard, employer API.

---

# Triển khai & vận hành (ngắn gọn)

* Local-first: tất cả xử lý offline (privacy). Dùng OpenAI/Cloud LLM chỉ khi user bật.
* Packaging: tạo installer cho Windows/macOS + README.
* Release: GitHub repo + demo video (2–3 phút) + sample dataset (anonymized) → giúp tuyển dụng tin tưởng.

---

# Checklist triển khai (từng bước, tick-off)

1. [ ] Repo + env setup.
2. [ ] PDF → parsed\_cv.json pipeline.
3. [ ] Skill extraction + canonicalization.
4. [ ] Embedding & FAISS index.
5. [ ] Single JD match API + explainability.
6. [ ] Rewrite API (LLM prompts).
7. [ ] Company ranking + UI.
8. [ ] Export rewritten CV & cover letter.
9. [ ] Unit tests + evaluation.
10. [ ] Packaging + release.

---
