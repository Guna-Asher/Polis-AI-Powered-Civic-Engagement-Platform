import nltk
from textblob import TextBlob
import re

class NLPProcessor:
    def __init__(self):
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def summarize_legislation(self, text, max_length=150, min_length=30):
        if len(text.split()) < 50:
            return text[:200] + "..." if len(text) > 200 else text
        try:
            sentences = nltk.sent_tokenize(text)
            if len(sentences) <= 3:
                return text
            return ' '.join(sentences[:3])
        except Exception as e:
            return text[:150] + "..."

    def analyze_sentiment(self, text):
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            return {'label': label, 'score': abs(polarity)}
        except Exception as e:
            return {'label': 'neutral', 'score': 0.5}

    def parse_legislation_structure(self, text):
        clauses = []
        patterns = [
            r'(?:Section|SECTION)\s+(\d+[A-Z]*)\.?\s*(.*?)(?=(?:Section|SECTION)\s+\d+[A-Z]*|$)',
            r'(?:Article|ARTICLE)\s+(\d+[A-Z]*)\.?\s*(.*?)(?=(?:Article|ARTICLE)\s+\d+[A-Z]*|$)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clause_number = match.group(1)
                clause_content = match.group(2).strip()
                if clause_content and len(clause_content) > 10:
                    clauses.append({
                        'number': clause_number,
                        'content': clause_content,
                        'summary': self.summarize_legislation(clause_content, max_length=100, min_length=20)
                    })
        
        if not clauses and len(text) > 100:
            sentences = nltk.sent_tokenize(text)
            for i in range(min(3, len(sentences))):
                clauses.append({
                    'number': str(i + 1),
                    'content': sentences[i],
                    'summary': sentences[i][:100] + "..." if len(sentences[i]) > 100 else sentences[i]
                })
        
        return clauses

nlp_processor = NLPProcessor()