import json
from urllib.parse import urlparse
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import nltk

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class AIIndexer:
    def __init__(self, input_file='./final_results.json', output_file='alexandrya_ai.json', model_path='./classifier'):
        self.input_file = input_file
        self.output_file = output_file
        self.model_path = model_path
        self.indexed_data = []

        # Load AI model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.labels = [
            "Analyst Update", "Fed | Central Banks", "Company | Product News",
            "Treasuries | Corporate Debt", "Dividend", "Earnings", "Energy | Oil",
            "Financials", "Currencies", "General News | Opinion", "Gold | Metals | Materials",
            "IPO", "Legal | Regulation", "M&A | Investments", "Macro", "Markets",
            "Politics", "Personnel Change", "Stock Commentary", "Stock Movement"
        ]

    def classify_text(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        logits = outputs.logits
        scores = torch.softmax(logits, dim=1).squeeze().tolist()
        
        results = [{"label": label, "score": score} for label, score in zip(self.labels, scores)]
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        return results

    def score_url(self, url):
        score = 0
        parsed_url = urlparse(url)
        
        # HTTPS
        if parsed_url.scheme == 'https':
            score += 5
        
        # URL length
        score += min(len(url) // 10, 5)  # Max 5 points for length
        
        # Domain
        domain = parsed_url.netloc
        if domain.endswith('.com'):
            score += 3
        elif domain.endswith('.br'):
            score += 4
        elif domain.endswith('.gov'):
            score += 5
        elif domain.endswith('.edu'):
            score += 5
        
        return score

    def index(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        for item in results:
            classification_results = self.classify_text(item['text'])
            url_score = self.score_url(item['url'])
            
            indexed_item = {
                'url': item['url'],
                'title': item['title'],
                'text': item['text'],
                'links': item['links'],  # Adicionando o campo 'links'
                'classification_results': classification_results,
                'url_score': url_score
            }
            self.indexed_data.append(indexed_item)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.indexed_data, f, ensure_ascii=False, indent=4)

        print(f"Indexing complete. Results saved to {self.output_file}")

    def search(self, query, top_n=5):
        query_classification = self.classify_text(query)
        top_query_label = query_classification[0]['label']
        
        results = []
        for item in self.indexed_data:
            item_top_label = item['classification_results'][0]['label']
            if item_top_label == top_query_label:
                results.append(item)
        
        # Sort results by the score of the matching label
        results.sort(key=lambda x: next(r['score'] for r in x['classification_results'] if r['label'] == top_query_label), reverse=True)
        
        return results[:top_n]

if __name__ == "__main__":
    indexer = AIIndexer()
    indexer.index()