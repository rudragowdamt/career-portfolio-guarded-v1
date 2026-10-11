"""Small, auditable retrieval pipeline. TF-IDF is the zero-cost baseline, not neural embeddings."""
from pathlib import Path
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KNOWLEDGE = Path(__file__).parent / "knowledge"

def chunks():
    result=[]
    for path in sorted(KNOWLEDGE.glob("*.md")):
        text=path.read_text(encoding="utf-8")
        parts=re.split(r"(?=^## )",text,flags=re.M)
        for part in parts:
            part=part.strip()
            if part:
                result.append({"id":path.stem,"title":path.stem.replace("_"," ").title(),"text":part,"url":"/#work" if "intelligence" in path.name or "copilot" in path.name else "/#experience" if "experience" in path.name else "/#about"})
    return result

class Retriever:
    def __init__(self):
        self.docs=chunks()
        self.vectorizer=TfidfVectorizer(stop_words="english",ngram_range=(1,2),sublinear_tf=True)
        self.matrix=self.vectorizer.fit_transform([d["text"] for d in self.docs])
    def search(self,query,k=3):
        scores=cosine_similarity(self.vectorizer.transform([query]),self.matrix)[0]
        indices=sorted(range(len(scores)),key=lambda i:float(scores[i]),reverse=True)[:k]
        return [{**self.docs[i],"score":round(float(scores[i]),3)} for i in indices if scores[i]>=0.055]
