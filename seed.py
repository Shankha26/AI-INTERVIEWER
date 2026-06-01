import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from models.database import db
from models.user import User
from models.question import Question

def perform_seeding():
    print("Starting database seeding...")
    
    # 1. Create Default Users if they don't exist
    admin_email = "admin@prepai.pro"
    candidate_email = "candidate@prepai.pro"
    
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            name="System Administrator",
            email=admin_email,
            college="PrepAI Central",
            branch="Computer Science & Engineering"
        )
        admin.is_admin = True
        admin.set_password("adminpassword123")
        db.session.add(admin)
        print(f"Created Admin account: {admin_email} / adminpassword123")
        
    candidate = User.query.filter_by(email=candidate_email).first()
    if not candidate:
        candidate = User(
            name="Alex Candidate",
            email=candidate_email,
            college="SDG 4 University",
            branch="Information Technology"
        )
        candidate.is_admin = False
        candidate.set_password("candidatepassword123")
        db.session.add(candidate)
        print(f"Created Candidate account: {candidate_email} / candidatepassword123")
        
    # 2. Seed Questions
    questions_data = [
        # ----- QUANTITATIVE APTITUDE -----
        {
            'subject': 'Quantitative Aptitude', 'category': 'aptitude', 'difficulty': 'easy',
            'question_text': "A sum of money doubles itself in 8 years at simple interest. What is the rate of interest per annum?",
            'option_a': "10%", 'option_b': "12.5%", 'option_c': "15%", 'option_d': "16.67%",
            'correct_option': "B",
            'explanation': "Let Principal = P. Amount = 2P. SI = Amount - Principal = P. Time = 8 years. SI = (P * R * T) / 100 => P = (P * R * 8) / 100 => 8R = 100 => R = 12.5% per annum."
        },
        {
            'subject': 'Quantitative Aptitude', 'category': 'aptitude', 'difficulty': 'medium',
            'question_text': "A worker is paid Rs. 750 for 5 days of work. How much will he earn if he works for 24 days?",
            'option_a': "Rs. 3200", 'option_b': "Rs. 3400", 'option_c': "Rs. 3600", 'option_d': "Rs. 3800",
            'correct_option': "C",
            'explanation': "Payment per day = 750 / 5 = Rs. 150. Earning for 24 days = 150 * 24 = Rs. 3600."
        },
        
        # ----- LOGICAL REASONING -----
        {
            'subject': 'Logical Reasoning', 'category': 'aptitude', 'difficulty': 'easy',
            'question_text': "If CLOCK is coded as KCOLC, how will STEPS be coded?",
            'option_a': "SPETS", 'option_b': "SPSTE", 'option_c': "PETSS", 'option_d': "STEPS",
            'correct_option': "A",
            'explanation': "The coding reverses the spelling of CLOCK to KCOLC. Reversing STEPS yields SPETS."
        },
        {
            'subject': 'Logical Reasoning', 'category': 'aptitude', 'difficulty': 'medium',
            'question_text': "Find the missing number in the series: 3, 5, 9, 17, 33, ?",
            'option_a': "48", 'option_b': "55", 'option_c': "65", 'option_d': "68",
            'correct_option': "C",
            'explanation': "The pattern is: (+2, +4, +8, +16, +32). The next step is 33 + 32 = 65."
        },
        
        # ----- VERBAL ABILITY -----
        {
            'subject': 'Verbal Ability', 'category': 'aptitude', 'difficulty': 'easy',
            'question_text': "Fill in the blank: The manager was angry _____ his secretary for failing to deliver the file.",
            'option_a': "with", 'option_b': "at", 'option_c': "on", 'option_d': "by",
            'correct_option': "A",
            'explanation': "The standard preposition rule is: Angry 'with' a person, but angry 'at' a situation. Hence, 'angry with his secretary'."
        },
        
        # ----- TECHNICAL SUBJECTS: PYTHON -----
        {
            'subject': 'Python', 'category': 'tech', 'difficulty': 'easy',
            'question_text': "Which of the following data structures in Python is IMMUTABLE?",
            'option_a': "List", 'option_b': "Dictionary", 'option_c': "Tuple", 'option_d': "Set",
            'correct_option': "C",
            'explanation': "Tuples are immutable sequences, meaning their items cannot be modified or re-allocated after definition."
        },
        {
            'subject': 'Python', 'category': 'tech', 'difficulty': 'medium',
            'question_text': "What does the expression 'lambda x: x * 2' represent in Python?",
            'option_a': "A generator function", 'option_b': "An anonymous one-line function", 'option_c': "A recursive loop", 'option_d': "An import alias",
            'correct_option': "B",
            'explanation': "Lambda defines an inline, anonymous function in Python that takes inputs and performs a simple calculation."
        },
        
        # ----- TECHNICAL SUBJECTS: DBMS -----
        {
            'subject': 'DBMS', 'category': 'tech', 'difficulty': 'medium',
            'question_text': "Which ACID property guarantees that all transactions are fully saved or completely rolled back?",
            'option_a': "Atomicity", 'option_b': "Consistency", 'option_c': "Isolation", 'option_d': "Durability",
            'correct_option': "A",
            'explanation': "Atomicity guarantees that a transaction is treated as a single, indivisible 'unit of work' that either succeeds in full or fails in full."
        },
        
        # ----- TECHNICAL SUBJECTS: DSA -----
        {
            'subject': 'Data Structures and Algorithms', 'category': 'tech', 'difficulty': 'hard',
            'question_text': "What is the worst-case time complexity of sorting N elements using Quick Sort?",
            'option_a': "O(N log N)", 'option_b': "O(N)", 'option_c': "O(N^2)", 'option_d': "O(2^N)",
            'correct_option': "C",
            'explanation': "Quick Sort has an average complexity of O(N log N), but if pivots are chosen poorly (e.g. sorted array with first element pivot), it degrades to O(N^2)."
        }
    ]
    
    # Avoid duplicate inserts
    seeded_count = 0
    for q in questions_data:
        exists = Question.query.filter_by(question_text=q['question_text']).first()
        if not exists:
            new_q = Question(
                subject=q['subject'],
                category=q['category'],
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_option=q['correct_option'],
                difficulty=q['difficulty'],
                explanation=q['explanation']
            )
            db.session.add(new_q)
            seeded_count += 1
            
    db.session.commit()
    print(f"Database seeding completed! Seeded {seeded_count} new questions.")

def seed_database():
    from app import create_app
    app = create_app()
    with app.app_context():
        perform_seeding()

if __name__ == "__main__":
    seed_database()

