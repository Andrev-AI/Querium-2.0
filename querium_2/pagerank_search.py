import json
import math
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class SearchEngine:
    def __init__(self, indexed_file='alexandrya_ai.json'):
        with open(indexed_file, 'r', encoding='utf-8') as f:
            self.indexed_data = json.load(f)
        
        self.stop_words = set(stopwords.words('english'))
        self.avg_doc_length = self.calculate_avg_doc_length()
        self.pagerank_scores = self.calculate_pagerank()

    def calculate_pagerank(self, damping_factor=0.85, num_iterations=100):
        num_pages = len(self.indexed_data)
        initial_value = 1.0 / num_pages
        pagerank = {item['url']: initial_value for item in self.indexed_data}

        url_to_index = {item['url']: i for i, item in enumerate(self.indexed_data)}

        for _ in range(num_iterations):
            new_pagerank = {}
            for item in self.indexed_data:
                url = item['url']
                incoming_pr = 0
                for other_item in self.indexed_data:
                    if 'links' in other_item and url in other_item['links']:
                        incoming_pr += pagerank[other_item['url']] / len(other_item['links'])
                new_pagerank[url] = (1 - damping_factor) / num_pages + damping_factor * incoming_pr

            pagerank = new_pagerank

        return pagerank

    def calculate_avg_doc_length(self):
        total_length = sum(len(self.tokenize(item['text'])) for item in self.indexed_data)
        return total_length / len(self.indexed_data)

    def tokenize(self, text):
        tokens = word_tokenize(text.lower())
        return [token for token in tokens if token.isalnum() and token not in self.stop_words]

    def compute_bm25_score(self, query, document, k1=1.5, b=0.75):
        query_terms = self.tokenize(query)
        doc_terms = self.tokenize(document)
        doc_length = len(doc_terms)
        term_freqs = Counter(doc_terms)
        
        score = 0
        for term in query_terms:
            if term in term_freqs:
                idf = math.log((len(self.indexed_data) - len([d for d in self.indexed_data if term in self.tokenize(d['text'])])) + 0.5) - \
                      math.log(len([d for d in self.indexed_data if term in self.tokenize(d['text'])]) + 0.5)
                tf = term_freqs[term]
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * doc_length / self.avg_doc_length)
                score += idf * numerator / denominator
        
        return score

    def get_snippet(self, text, query, snippet_length=200):
        query_terms = set(self.tokenize(query))
        words = text.split()
        best_start = 0
        max_matches = 0

        for i in range(len(words) - snippet_length):
            snippet = ' '.join(words[i:i+snippet_length])
            matches = sum(1 for term in query_terms if term in self.tokenize(snippet))
            if matches > max_matches:
                max_matches = matches
                best_start = i

        return ' '.join(words[best_start:best_start+snippet_length]) + '...'

    def search(self, query, top_n=5):
        results = []
        for item in self.indexed_data:
            bm25_score = self.compute_bm25_score(query, item['text'])
            url_score = item.get('url_score', 0)
            pagerank_score = self.pagerank_scores.get(item['url'], 0)
            
            if 'classification_results' in item and item['classification_results']:
                classification_score = item['classification_results'][0]['score']
            else:
                classification_score = 0
            
            total_score = (bm25_score * 0.4 + url_score * 0.1 + pagerank_score * 0.3 + classification_score * 0.2)
            
            snippet = self.get_snippet(item['text'], query)
            
            results.append({
                'url': item['url'],
                'title': item['title'],
                'score': total_score,
                'snippet': snippet
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_n]

if __name__ == "__main__":
    search_engine = SearchEngine()
    query = ""
    search_results = search_engine.search(query)
    for result in search_results:
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Score: {result['score']}")
        print(f"Snippet: {result['snippet']}")
        print("---")