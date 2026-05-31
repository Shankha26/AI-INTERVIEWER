import random
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from models.database import db
from models.question import Question
from models.aptitude import AptitudeResult
from sqlalchemy.sql.expression import func

aptitude_bp = Blueprint('aptitude', __name__, url_prefix='/aptitude')

# Hardcoded fallback questions in case database seeding is pending or failed
FALLBACK_QUESTIONS = {
    'Quantitative Aptitude': [
        {
            'id': 9901,
            'question_text': "A train 120 m long passes a telegraph post in 6 seconds. Find the speed of the train in km/hr.",
            'option_a': "60 km/hr", 'option_b': "72 km/hr", 'option_c': "80 km/hr", 'option_d': "90 km/hr",
            'correct_option': "B",
            'explanation': "Speed = Distance / Time = 120m / 6s = 20 m/s. To convert m/s to km/hr, multiply by 18/5: 20 * 18/5 = 72 km/hr."
        },
        {
            'id': 9902,
            'question_text': "If 15 men can complete a project in 20 days, how many days will 10 men take to complete the same work?",
            'option_a': "30 days", 'option_b': "25 days", 'option_c': "40 days", 'option_d': "35 days",
            'correct_option': "A",
            'explanation': "Work is constant. Men * Days = Work. 15 * 20 = 300 man-days. Days for 10 men = 300 / 10 = 30 days."
        },
        {
            'id': 9903,
            'question_text': "What is the average of first five prime numbers?",
            'option_a': "5.0", 'option_b': "5.6", 'option_c': "6.2", 'option_d': "5.4",
            'correct_option': "B",
            'explanation': "First five prime numbers are 2, 3, 5, 7, 11. Sum = 2 + 3 + 5 + 7 + 11 = 28. Average = 28 / 5 = 5.6."
        }
    ],
    'Logical Reasoning': [
        {
            'id': 9911,
            'question_text': "Look at the series: 2, 1, (1/2), (1/4), ... What number should come next?",
            'option_a': "(1/3)", 'option_b': "(1/8)", 'option_c': "(2/8)", 'option_d': "(1/16)",
            'correct_option': "B",
            'explanation': "This is a geometric division series. Each number is half of the previous number: 1/4 * 1/2 = 1/8."
        },
        {
            'id': 9912,
            'question_text': "Pointing to a photograph, Vicky said, 'He is the son of the only daughter of my father.' How is Vicky related to the man in the photograph?",
            'option_a': "Father", 'option_b': "Brother", 'option_c': "Maternal Uncle", 'option_d': "Nephew",
            'correct_option': "C",
            'explanation': "'Only daughter of my father' is Vicky's sister. Her son is Vicky's nephew, making Vicky the maternal uncle of the man."
        }
    ],
    'Verbal Ability': [
        {
            'id': 9921,
            'question_text': "Choose the word which is most nearly SYNONYMOUS to 'ABANDON'.",
            'option_a': "Adopt", 'option_b': "Forsake", 'option_c': "Keep", 'option_d': "Cherish",
            'correct_option': "B",
            'explanation': "Abandon means to leave completely or desert. Forsake is its closest synonym."
        },
        {
            'id': 9922,
            'question_text': "Identify the grammatical error in the following: 'She has been working here since three years.'",
            'option_a': "She has", 'option_b': "been working", 'option_c': "here since", 'option_d': "three years",
            'correct_option': "C",
            'explanation': "'Since' is used for a specific point in time (e.g. 2020), while 'for' is used for a duration (e.g. three years). It should be 'for three years'."
        }
    ]
}

@aptitude_bp.route('/setup')
@login_required
def setup():
    categories = ['Quantitative Aptitude', 'Logical Reasoning', 'Verbal Ability']
    return render_template('aptitude/setup.html', categories=categories)

@aptitude_bp.route('/start', methods=['POST'])
@login_required
def start():
    category = request.form.get('category')
    if not category:
        flash('Please select a valid aptitude category.', 'danger')
        return redirect(url_for('aptitude.setup'))
        
    # Attempt to retrieve questions from DB
    db_questions = Question.query.filter_by(subject=category, category='aptitude').order_by(func.random()).limit(10).all()
    
    questions_list = []
    if len(db_questions) >= 3:
        for q in db_questions:
            questions_list.append({
                'id': q.id,
                'question_text': q.question_text,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_option': q.correct_option,
                'explanation': q.explanation
            })
    else:
        # Fall back to hardcoded checklist if database is empty or unseeded
        questions_list = FALLBACK_QUESTIONS.get(category, [])
        
    # Store questions and quiz details in session
    session['apt_category'] = category
    session['apt_questions'] = questions_list
    session['apt_start_time'] = datetime.utcnow().isoformat()
    
    return redirect(url_for('aptitude.quiz'))

@aptitude_bp.route('/quiz')
@login_required
def quiz():
    if 'apt_questions' not in session:
        flash('No active aptitude test found.', 'danger')
        return redirect(url_for('aptitude.setup'))
        
    category = session['apt_category']
    questions = session['apt_questions']
    
    # 10 minutes limit (600 seconds)
    time_limit = 600
    
    return render_template('aptitude/quiz.html', category=category, questions=questions, time_limit=time_limit)

@aptitude_bp.route('/evaluate', methods=['POST'])
@login_required
def evaluate():
    if 'apt_questions' not in session:
        return jsonify({'error': 'No active aptitude quiz session found.'}), 400
        
    user_answers = request.json.get('answers', {})
    category = session['apt_category']
    questions = session['apt_questions']
    
    score = 0
    total_questions = len(questions)
    results = []
    
    for q in questions:
        q_id_str = str(q['id'])
        user_ans = user_answers.get(q_id_str, '')
        correct_ans = q['correct_option']
        
        is_correct = (user_ans.upper() == correct_ans.upper())
        if is_correct:
            score += 1
            
        results.append({
            'question_text': q['question_text'],
            'option_a': q['option_a'],
            'option_b': q['option_b'],
            'option_c': q['option_c'],
            'option_d': q['option_d'],
            'user_answer': user_ans,
            'correct_answer': correct_ans,
            'is_correct': is_correct,
            'explanation': q['explanation']
        })
        
    try:
        # Log to Database
        new_result = AptitudeResult(
            user_id=current_user.id,
            category=category,
            score=score,
            total_questions=total_questions
        )
        db.session.add(new_result)
        db.session.commit()
        
        # Clear session
        session.pop('apt_category', None)
        session.pop('apt_questions', None)
        session.pop('apt_start_time', None)
        
        return jsonify({
            'status': 'success',
            'redirect_url': url_for('aptitude.result', result_id=new_result.id),
            'results': results,
            'score': score,
            'total': total_questions
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save quiz results: {e}'}), 500

@aptitude_bp.route('/result/<int:result_id>')
@login_required
def result(result_id):
    res = AptitudeResult.query.filter_by(id=result_id, user_id=current_user.id).first_or_404()
    percentage = round((res.score / res.total_questions) * 100) if res.total_questions > 0 else 0
    return render_template('aptitude/result.html', result=res, percentage=percentage)

@aptitude_bp.route('/history')
@login_required
def history():
    results = AptitudeResult.query.filter_by(user_id=current_user.id).order_by(AptitudeResult.created_at.desc()).all()
    return render_template('aptitude/history.html', results=results)
