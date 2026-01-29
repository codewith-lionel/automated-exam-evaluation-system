"""NLP evaluator for analyzing and scoring exam answers."""

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string
import re
import numpy as np

# Download required NLTK data (will be done in app initialization)
def download_nltk_data():
    """Download required NLTK data packages."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)

class NLPEvaluator:
    """NLP-based answer evaluation system."""
    
    def __init__(self):
        """Initialize the evaluator with NLTK components."""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def preprocess_text(self, text):
        """
        Preprocess text for NLP analysis.
        
        Steps:
        1. Lowercase conversion
        2. Remove punctuation
        3. Tokenization
        4. Remove stop words
        5. Lemmatization
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 2
        ]
        
        return ' '.join(processed_tokens)
    
    def extract_keywords(self, text, top_n=10):
        """
        Extract important keywords using TF-IDF.
        
        Args:
            text: Input text
            top_n: Number of top keywords to extract
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        try:
            # Preprocess
            processed_text = self.preprocess_text(text)
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(max_features=top_n)
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform([processed_text])
            
            # Get feature names (keywords)
            keywords = vectorizer.get_feature_names_out()
            
            return list(keywords)
        
        except Exception as e:
            print(f"Error extracting keywords: {str(e)}")
            # Fallback: return most common words
            words = processed_text.split()
            return list(set(words[:top_n]))
    
    def calculate_similarity(self, text1, text2):
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text (model answer)
            text2: Second text (student answer)
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Preprocess both texts
            processed_text1 = self.preprocess_text(text1)
            processed_text2 = self.preprocess_text(text2)
            
            if not processed_text1 or not processed_text2:
                return 0.0
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def evaluate_answer(self, model_answer, student_answer, max_marks=10):
        """
        Evaluate a single answer against model answer.
        
        Args:
            model_answer: Correct answer
            student_answer: Student's answer
            max_marks: Maximum marks for this question
            
        Returns:
            Dictionary with score and analysis
        """
        # Calculate similarity score
        similarity = self.calculate_similarity(model_answer, student_answer)
        
        # Calculate marks based on similarity
        obtained_marks = round(similarity * max_marks, 2)
        
        # Extract keywords from both answers
        model_keywords = set(self.extract_keywords(model_answer, top_n=15))
        student_keywords = set(self.extract_keywords(student_answer, top_n=15))
        
        # Find matched and missed keywords
        keywords_matched = list(model_keywords.intersection(student_keywords))
        keywords_missed = list(model_keywords.difference(student_keywords))
        
        return {
            'obtained_marks': obtained_marks,
            'max_marks': max_marks,
            'similarity': round(similarity * 100, 2),
            'keywords_matched': keywords_matched,
            'keywords_missed': keywords_missed
        }
    
    def evaluate_multiple_answers(self, questions_data):
        """
        Evaluate multiple questions.
        
        Args:
            questions_data: List of dicts with 'question', 'model_answer', 'student_answer', 'max_marks'
            
        Returns:
            Dictionary with overall results and question-wise breakdown
        """
        results = {
            'questions': [],
            'total_marks': 0,
            'obtained_marks': 0,
            'percentage': 0
        }
        
        for i, q_data in enumerate(questions_data):
            evaluation = self.evaluate_answer(
                q_data.get('model_answer', ''),
                q_data.get('student_answer', ''),
                q_data.get('max_marks', 10)
            )
            
            evaluation['question_number'] = i + 1
            evaluation['question_text'] = q_data.get('question', f'Question {i + 1}')
            evaluation['model_answer'] = q_data.get('model_answer', '')
            evaluation['student_answer'] = q_data.get('student_answer', '')
            
            results['questions'].append(evaluation)
            results['total_marks'] += evaluation['max_marks']
            results['obtained_marks'] += evaluation['obtained_marks']
        
        # Calculate percentage
        if results['total_marks'] > 0:
            results['percentage'] = round((results['obtained_marks'] / results['total_marks']) * 100, 2)
        
        return results
    
    def generate_feedback(self, evaluation_results):
        """
        Generate detailed feedback based on evaluation results.
        
        Args:
            evaluation_results: Results from evaluate_multiple_answers
            
        Returns:
            Dictionary with categorized feedback
        """
        feedback = {
            'good_answers': [],
            'areas_to_improve': [],
            'suggestions': []
        }
        
        for question in evaluation_results['questions']:
            q_num = question['question_number']
            similarity = question['similarity']
            
            # Good answers (similarity > 70%)
            if similarity >= 70:
                feedback['good_answers'].append(
                    f"Question {q_num}: Excellent understanding! Score: {question['obtained_marks']}/{question['max_marks']}"
                )
            
            # Areas to improve (similarity < 70%)
            else:
                feedback['areas_to_improve'].append(
                    f"Question {q_num}: Needs improvement. Score: {question['obtained_marks']}/{question['max_marks']}"
                )
                
                # Add specific suggestions based on missed keywords
                if question['keywords_missed']:
                    missed_kw = ', '.join(question['keywords_missed'][:5])
                    feedback['suggestions'].append(
                        f"Question {q_num}: Include key concepts like: {missed_kw}"
                    )
        
        # Add general suggestions
        if evaluation_results['percentage'] < 50:
            feedback['suggestions'].append(
                "Review the fundamental concepts and practice more examples."
            )
        elif evaluation_results['percentage'] < 75:
            feedback['suggestions'].append(
                "Good progress! Focus on elaborating answers with more details and examples."
            )
        else:
            feedback['suggestions'].append(
                "Great work! Continue practicing to maintain your performance."
            )
        
        return feedback
