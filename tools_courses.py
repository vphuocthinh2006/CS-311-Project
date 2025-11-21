# %%
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# %%
class SkillGapAnalyzer:
    def __init__(self, coursera_dataset_path):
        self.courses_df = pd.read_csv(coursera_dataset_path)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._preprocess_courses()
        
    def _preprocess_courses(self):
        self.courses_df['skills_clean'] = self.courses_df.iloc[:, 1].fillna('').astype(str) 
        self.course_vectors = self.vectorizer.fit_transform(self.courses_df['skills_clean'])

    def recommend_courses(self, missing_skills, top_n=3):
        if not missing_skills: return []
        query = ' '.join(missing_skills)
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.course_vectors).flatten()
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        results = []
        for idx in top_indices:
            row = self.courses_df.iloc[idx]
            results.append({
                "course_name": row.get('course_name', 'Unknown'),
                "url": row.get('course_url', '#'),
                "score": round(similarities[idx], 2)
            })
        return results


# %%
DATASET_PATH = "D:\CS311 Project\data\coursea_data.csv" 
print("Loading Course Analyzer...")
try:
    course_analyzer = SkillGapAnalyzer(DATASET_PATH)
    print("✅ Course Analyzer loaded.")
except Exception as e:
    print(f"⚠️ Error loading Course Data: {e}")
    course_analyzer = None

# --- MAIN TOOL FUNCTION ---
def get_course_recommendations(missing_skills: list) -> list:
    """Tool gợi ý khóa học dựa trên list kỹ năng thiếu."""
    if course_analyzer is None:
        return []
    return course_analyzer.recommend_courses(missing_skills)


