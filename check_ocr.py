"""Check OCR extraction from recent evaluation."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.database import get_evaluation_questions, get_all_evaluations

# Get most recent evaluation
evals = get_all_evaluations(limit=1)
if not evals:
    print("No evaluations found")
    sys.exit(0)

recent = evals[0]
print(f"Recent Evaluation ID: {recent['id']}")
print(f"Subject: {recent['subject']}")
print(f"Status: {recent['status']}")
print(f"Score: {recent['percentage']}%")
print("\n" + "="*80)

# Get questions
questions = get_evaluation_questions(recent['id'])
print(f"\nTotal Questions: {len(questions)}")

for q in questions:
    print(f"\n{'='*80}")
    print(f"Question {q['question_number']}:")
    print(f"Question Text: {q['question_text'][:100]}...")
    print(f"\nStudent Answer ({len(q['student_answer'])} chars):")
    print(q['student_answer'][:500])
    if len(q['student_answer']) > 500:
        print(f"... (truncated, total {len(q['student_answer'])} characters)")
    print(f"\nMarks: {q['obtained_marks']}/{q['max_marks']}")
