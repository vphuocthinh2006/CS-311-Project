# %%
import torch
from sentence_transformers import SentenceTransformer, util
import re
import unicodedata

# %%
MODEL_PATH = "sentence-transformers/all-MiniLM-L6-v2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"    

# %%
print(f"⏳ Loading Similarity Model on {DEVICE}...")
try:
    sim_model = SentenceTransformer(MODEL_PATH, device=DEVICE)
    print("✅ Similarity Model loaded.")
except Exception as e:
    print(f"⚠️ Error loading Similarity Model: {e}")
    sim_model = None

# %%
def preprocess_text(text):
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"[@#]{2,}", " ", text)
    text = re.sub(r"[^0-9a-zA-ZÀ-ỹ.,!?;:()\-\s]", " ", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

# %%
def calculate_similarity(cv_text: str, jd_text: str) -> float:
    """Tool tính điểm tương đồng giữa CV và JD."""
    if sim_model is None:
        return 0.0
        
    processed_cv = preprocess_text(cv_text)
    processed_jd = preprocess_text(jd_text)
    
    emb1 = sim_model.encode(processed_jd, convert_to_tensor=True)
    emb2 = sim_model.encode(processed_cv, convert_to_tensor=True)
    
    similarity = util.cos_sim(emb1, emb2)
    return round(similarity.item(), 4)

# %%



