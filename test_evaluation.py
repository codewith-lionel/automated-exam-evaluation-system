"""
Quick test script to evaluate the sample student answers
"""

import json
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.nlp_evaluator import NLPEvaluator, download_nltk_data

# Download NLTK data if needed
print("Ensuring NLTK data is available...")
download_nltk_data()

# Load model answers
with open('sample_data/model_answers_6questions.json', 'r', encoding='utf-8') as f:
    model_data = json.load(f)

# Load student answers
with open('sample_data/sample_student_answer.txt', 'r', encoding='utf-8') as f:
    student_text = f.read()

# Parse student answers by question number
student_answers = {}
lines = student_text.split('\n')
current_q = None
current_answer = ''

for line in lines:
    line = line.strip()
    if not line:
        continue
    
    # Check for Q1:, Q2:, etc.
    if line.startswith('Q') and ':' in line:
        # Save previous answer
        if current_q is not None and current_answer:
            student_answers[current_q] = current_answer.strip()
        
        # Start new question
        parts = line.split(':', 1)
        current_q = int(parts[0][1:])  # Extract number from Q1, Q2, etc.
        current_answer = parts[1].strip() if len(parts) > 1 else ''
    else:
        # Continue current answer
        if current_q is not None:
            current_answer += ' ' + line

# Save last answer
if current_q is not None and current_answer:
    student_answers[current_q] = current_answer.strip()

print(f"\n✓ Parsed {len(student_answers)} student answers")
print(f"✓ Loaded {len(model_data['questions'])} model answers\n")

# Prepare questions for evaluation
questions_data = []
for q in model_data['questions']:
    q_num = q['question_number']
    questions_data.append({
        'question': q['question'],
        'model_answer': q['model_answer'],
        'student_answer': student_answers.get(q_num, ''),
        'max_marks': q['max_marks']
    })

# Initialize evaluator
print("Initializing NLP Evaluator...")
evaluator = NLPEvaluator()

# Evaluate
print("Evaluating answers...\n")
print("=" * 80)
results = evaluator.evaluate_multiple_answers(questions_data)

# Display results
print(f"\n{'EVALUATION RESULTS':^80}")
print("=" * 80)
print(f"\nTotal Marks: {results['obtained_marks']:.2f} / {results['total_marks']}")
print(f"Percentage: {results['percentage']:.2f}%")
print(f"Grade: ", end='')

# Calculate grade
percentage = results['percentage']
if percentage >= 90:
    print("A+ (Excellent)")
elif percentage >= 80:
    print("A (Very Good)")
elif percentage >= 70:
    print("B (Good)")
elif percentage >= 60:
    print("C (Satisfactory)")
elif percentage >= 50:
    print("D (Pass)")
else:
    print("F (Fail)")

print("\n" + "=" * 80)
print(f"{'QUESTION-WISE BREAKDOWN':^80}")
print("=" * 80)

for q in results['questions']:
    print(f"\n{'─' * 80}")
    print(f"Question {q['question_number']}: {q['question_text']}")
    print(f"{'─' * 80}")
    print(f"Marks: {q['obtained_marks']:.2f} / {q['max_marks']}")
    print(f"Similarity: {q['similarity']:.2f}%")
    
    if q['keywords_matched']:
        print(f"✓ Matched Keywords: {', '.join(q['keywords_matched'][:5])}")
    
    if q['keywords_missed']:
        print(f"✗ Missed Keywords: {', '.join(q['keywords_missed'][:5])}")
    
    # Performance indicator
    if q['similarity'] >= 80:
        print("Performance: Excellent ⭐⭐⭐")
    elif q['similarity'] >= 70:
        print("Performance: Good ⭐⭐")
    elif q['similarity'] >= 60:
        print("Performance: Satisfactory ⭐")
    else:
        print("Performance: Needs Improvement")

# Generate feedback
print("\n" + "=" * 80)
print(f"{'FEEDBACK':^80}")
print("=" * 80)

feedback = evaluator.generate_feedback(results)

if feedback['good_answers']:
    print("\n✓ Strengths:")
    for item in feedback['good_answers']:
        print(f"  • {item}")

if feedback['areas_to_improve']:
    print("\n⚠ Areas to Improve:")
    for item in feedback['areas_to_improve']:
        print(f"  • {item}")

if feedback['suggestions']:
    print("\n💡 Suggestions:")
    for item in feedback['suggestions']:
        print(f"  • {item}")

print("\n" + "=" * 80)
print("Evaluation Complete!")
print("=" * 80)
