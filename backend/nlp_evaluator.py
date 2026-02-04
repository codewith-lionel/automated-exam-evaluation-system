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
from collections import Counter

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
    """Enhanced NLP-based answer evaluation system with improved reliability."""
    
    def __init__(self):
        """Initialize the evaluator with NLTK components."""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def preprocess_text(self, text):
        """
        Preprocess text for NLP analysis.
        
        Steps:
        1. Lowercase conversion
        2. Remove extra whitespace
        3. Remove punctuation
        4. Tokenization
        5. Remove stop words
        6. Lemmatization
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 2 and token.isalnum()
        ]
        
        return ' '.join(processed_tokens)
    
    def extract_keywords(self, text, top_n=15):
        """
        Extract important keywords using TF-IDF with improved accuracy.
        
        Args:
            text: Input text
            top_n: Number of top keywords to extract
            
        Returns:
            List of (keyword, score) tuples
        """
        if not text:
            return []
        
        try:
            # Preprocess
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                return []
            
            # Create TF-IDF vectorizer with bigrams for better context
            vectorizer = TfidfVectorizer(
                max_features=top_n,
                ngram_range=(1, 2),  # Include single words and pairs
                min_df=1
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform([processed_text])
            
            # Get feature names and scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Sort by score
            keyword_scores = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
            
            return [kw for kw, score in keyword_scores if score > 0]
        
        except Exception as e:
            print(f"Error extracting keywords: {str(e)}")
            # Fallback: return most common words
            words = processed_text.split()
            word_freq = Counter(words)
            return [word for word, count in word_freq.most_common(top_n)]
    
    def calculate_semantic_similarity(self, text1, text2):
        """
        Calculate enhanced semantic similarity using multiple metrics.
        
        Args:
            text1: First text (model answer)
            text2: Second text (student answer)
            
        Returns:
            Similarity score (0-1) with improved accuracy
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Preprocess both texts
            processed_text1 = self.preprocess_text(text1)
            processed_text2 = self.preprocess_text(text2)
            
            if not processed_text1 or not processed_text2:
                return 0.0
            
            # 1. TF-IDF Cosine Similarity (primary metric)
            vectorizer = TfidfVectorizer(ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # 2. Jaccard Similarity (word overlap)
            words1 = set(processed_text1.split())
            words2 = set(processed_text2.split())
            jaccard_sim = len(words1.intersection(words2)) / len(words1.union(words2)) if words1.union(words2) else 0
            
            # 3. Length ratio penalty (if answer is too short)
            len_ratio = min(len(processed_text2.split()), len(processed_text1.split())) / max(len(processed_text1.split()), 1)
            length_penalty = 1.0 if len_ratio > 0.5 else len_ratio * 2
            
            # Weighted combination (70% cosine, 20% jaccard, 10% length consideration)
            final_similarity = (cosine_sim * 0.7 + jaccard_sim * 0.2 + length_penalty * 0.1)
            
            return float(min(final_similarity, 1.0))
        
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def calculate_keyword_coverage(self, model_keywords, student_keywords):
        """
        Calculate keyword coverage score with weighting.
        
        Args:
            model_keywords: Keywords from model answer
            student_keywords: Keywords from student answer
            
        Returns:
            Coverage score (0-1)
        """
        if not model_keywords:
            return 0.0
        
        model_set = set(model_keywords)
        student_set = set(student_keywords)
        
        matched = model_set.intersection(student_set)
        coverage = len(matched) / len(model_set) if model_set else 0
        
        return coverage
    
    def evaluate_answer(self, model_answer, student_answer, max_marks=10):
        """
        Evaluate a single answer with enhanced accuracy and reliability.
        
        Args:
            model_answer: Correct answer
            student_answer: Student's answer
            max_marks: Maximum marks for this question
            
        Returns:
            Dictionary with detailed score and analysis
        """
        # Handle empty answers
        if not student_answer or len(student_answer.strip()) < 5:
            return {
                'obtained_marks': 0,
                'max_marks': max_marks,
                'similarity': 0,
                'keyword_coverage': 0,
                'keywords_matched': [],
                'keywords_missed': self.extract_keywords(model_answer, top_n=10),
                'quality_score': 0
            }
        
        # Calculate semantic similarity
        similarity = self.calculate_semantic_similarity(model_answer, student_answer)
        
        # Extract keywords from both answers
        model_keywords = self.extract_keywords(model_answer, top_n=15)
        student_keywords = self.extract_keywords(student_answer, top_n=15)
        
        # Find matched and missed keywords
        keywords_matched = list(set(model_keywords).intersection(set(student_keywords)))
        keywords_missed = list(set(model_keywords).difference(set(student_keywords)))
        
        # Calculate keyword coverage
        keyword_coverage = self.calculate_keyword_coverage(model_keywords, student_keywords)
        
        # Calculate quality score (combination of similarity and keyword coverage)
        quality_score = (similarity * 0.6) + (keyword_coverage * 0.4)
        
        # Calculate final marks with bonus for comprehensive answers
        base_marks = quality_score * max_marks
        
        # Bonus: if student includes extra relevant information (more keywords)
        extra_keywords = len(set(student_keywords).difference(set(model_keywords)))
        bonus = min(extra_keywords * 0.1, max_marks * 0.1)  # Max 10% bonus
        
        obtained_marks = min(round(base_marks + bonus, 2), max_marks)
        
        return {
            'obtained_marks': obtained_marks,
            'max_marks': max_marks,
            'similarity': round(similarity * 100, 2),
            'keyword_coverage': round(keyword_coverage * 100, 2),
            'quality_score': round(quality_score * 100, 2),
            'keywords_matched': keywords_matched[:10],  # Limit for display
            'keywords_missed': keywords_missed[:10]
        }
    
    def evaluate_multiple_answers(self, questions_data):
        """
        Evaluate multiple questions with enhanced accuracy.
        
        Args:
            questions_data: List of dicts with 'question', 'model_answer', 'student_answer', 'max_marks'
            
        Returns:
            Dictionary with comprehensive results and analytics
        """
        results = {
            'questions': [],
            'total_marks': 0,
            'obtained_marks': 0,
            'percentage': 0,
            'analytics': {
                'avg_similarity': 0,
                'avg_keyword_coverage': 0,
                'questions_above_70': 0,
                'questions_below_50': 0
            }
        }
        
        total_similarity = 0
        total_coverage = 0
        
        for i, q_data in enumerate(questions_data):
            evaluation = self.evaluate_answer(
                q_data.get('model_answer', ''),
                q_data.get('student_answer', ''),
                q_data.get('max_marks', 10)
            )
            
            evaluation['question_number'] = q_data.get('question_number', i + 1)
            evaluation['question_text'] = q_data.get('question', f'Question {i + 1}')
            evaluation['model_answer'] = q_data.get('model_answer', '')
            evaluation['student_answer'] = q_data.get('student_answer', '')
            
            results['questions'].append(evaluation)
            results['total_marks'] += evaluation['max_marks']
            results['obtained_marks'] += evaluation['obtained_marks']
            
            # Track analytics
            total_similarity += evaluation['similarity']
            total_coverage += evaluation.get('keyword_coverage', 0)
            
            percentage = (evaluation['obtained_marks'] / evaluation['max_marks']) * 100
            if percentage >= 70:
                results['analytics']['questions_above_70'] += 1
            if percentage < 50:
                results['analytics']['questions_below_50'] += 1
        
        # Calculate overall percentage
        if results['total_marks'] > 0:
            results['percentage'] = round((results['obtained_marks'] / results['total_marks']) * 100, 2)
        
        # Calculate average analytics
        num_questions = len(questions_data)
        if num_questions > 0:
            results['analytics']['avg_similarity'] = round(total_similarity / num_questions, 2)
            results['analytics']['avg_keyword_coverage'] = round(total_coverage / num_questions, 2)
        
        return results
    
    def generate_feedback(self, evaluation_results):
        """
        Generate detailed, actionable feedback based on evaluation results.
        
        Args:
            evaluation_results: Results from evaluate_multiple_answers
            
        Returns:
            Dictionary with categorized, specific feedback
        """
        feedback = {
            'good_answers': [],
            'areas_to_improve': [],
            'suggestions': []
        }
        
        for question in evaluation_results['questions']:
            q_num = question['question_number']
            similarity = question['similarity']
            quality = question.get('quality_score', similarity)
            percentage = (question['obtained_marks'] / question['max_marks']) * 100
            
            # Excellent answers (quality >= 80%)
            if quality >= 80:
                feedback['good_answers'].append(
                    f"Question {q_num}: Outstanding! ({question['obtained_marks']}/{question['max_marks']} marks) - "
                    f"You demonstrated excellent understanding with {len(question['keywords_matched'])} key concepts covered."
                )
            
            # Good answers (quality >= 70%)
            elif quality >= 70:
                feedback['good_answers'].append(
                    f"Question {q_num}: Well done! ({question['obtained_marks']}/{question['max_marks']} marks) - "
                    f"Good grasp of the topic. Consider adding more detail."
                )
            
            # Moderate answers (quality >= 50%)
            elif quality >= 50:
                feedback['areas_to_improve'].append(
                    f"Question {q_num}: Satisfactory ({question['obtained_marks']}/{question['max_marks']} marks) - "
                    f"You understood the basics but missed some important points."
                )
                
                if question['keywords_missed']:
                    top_missed = ', '.join(question['keywords_missed'][:3])
                    feedback['suggestions'].append(
                        f"Q{q_num}: Try to include key concepts like: {top_missed}"
                    )
            
            # Weak answers (quality < 50%)
            else:
                feedback['areas_to_improve'].append(
                    f"Question {q_num}: Needs significant improvement ({question['obtained_marks']}/{question['max_marks']} marks) - "
                    f"The answer lacks depth and key concepts."
                )
                
                if question['keywords_missed']:
                    top_missed = ', '.join(question['keywords_missed'][:4])
                    feedback['suggestions'].append(
                        f"Q{q_num}: Essential topics to study: {top_missed}"
                    )
        
        # Overall performance feedback
        percentage = evaluation_results['percentage']
        analytics = evaluation_results.get('analytics', {})
        
        if percentage >= 85:
            feedback['suggestions'].append(
                "🎉 Excellent performance overall! You have a strong grasp of the material. "
                "Keep up the great work and focus on maintaining this level."
            )
        elif percentage >= 70:
            feedback['suggestions'].append(
                "👍 Good job! You're performing well. To improve further: "
                "1) Elaborate your answers with more examples, "
                "2) Cover all key concepts mentioned in the question, "
                "3) Structure your answers clearly with main points first."
            )
        elif percentage >= 50:
            feedback['suggestions'].append(
                "📚 You're on the right track but need more practice. Focus on: "
                "1) Understanding core concepts thoroughly, "
                "2) Reading questions carefully and addressing all parts, "
                "3) Using relevant terminology in your answers."
            )
        else:
            feedback['suggestions'].append(
                "⚠️ This topic needs significant attention. Recommended steps: "
                "1) Review the fundamental concepts from your notes/textbook, "
                "2) Practice writing structured answers, "
                "3) Focus on understanding rather than memorization, "
                "4) Consider discussing challenging topics with your instructor."
            )
        
        # Add specific analytics-based suggestions
        if analytics.get('avg_keyword_coverage', 0) < 50:
            feedback['suggestions'].append(
                "💡 Tip: Your answers often miss important keywords. Make sure to include "
                "all key terms and concepts related to the question. Review your study material "
                "to identify the most important terminology for each topic."
            )
        
        return feedback
