from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models.user import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    college = StringField('College / University', validators=[Length(max=150)])
    branch = SelectField('Branch / Stream', choices=[
        ('Computer Science & Engineering', 'CS & IT'),
        ('Electronics & Communication', 'Electronics (ECE)'),
        ('Electrical Engineering', 'Electrical (EE)'),
        ('Mechanical Engineering', 'Mechanical'),
        ('Civil Engineering', 'Civil'),
        ('Other', 'Other')
    ])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match!')])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered!')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    college = StringField('College / University', validators=[Length(max=150)])
    branch = SelectField('Branch / Stream', choices=[
        ('Computer Science & Engineering', 'CS & IT'),
        ('Electronics & Communication', 'Electronics (ECE)'),
        ('Electrical Engineering', 'Electrical (EE)'),
        ('Mechanical Engineering', 'Mechanical'),
        ('Civil Engineering', 'Civil'),
        ('Other', 'Other')
    ])
    profile_image = FileField('Upload Profile Photo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    password = PasswordField('New Password', validators=[Length(max=50)])
    submit = SubmitField('Save Changes')


class QuestionForm(FlaskForm):
    subject = SelectField('Subject Name', choices=[
        ('Quantitative Aptitude', 'Quantitative Aptitude'),
        ('Logical Reasoning', 'Logical Reasoning'),
        ('Verbal Ability', 'Verbal Ability'),
        ('C Programming', 'C Programming'),
        ('C++', 'C++'),
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('DBMS', 'DBMS'),
        ('Operating Systems', 'Operating Systems'),
        ('Computer Networks', 'Computer Networks'),
        ('Data Structures and Algorithms', 'Data Structures and Algorithms'),
        ('HR', 'HR')
    ], validators=[DataRequired()])
    
    category = SelectField('Subject Category', choices=[
        ('aptitude', 'Aptitude (MCQ Quiz)'),
        ('tech', 'Technical domain'),
        ('hr', 'Human Resources (HR)')
    ], validators=[DataRequired()])
    
    difficulty = SelectField('Difficulty Level', choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], default='medium')
    
    question_text = TextAreaField('Question Text Prompt', validators=[DataRequired()])
    option_a = StringField('Option A', validators=[DataRequired()])
    option_b = StringField('Option B', validators=[DataRequired()])
    option_c = StringField('Option C', validators=[DataRequired()])
    option_d = StringField('Option D', validators=[DataRequired()])
    
    correct_option = SelectField('Correct Option Key', choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D')
    ], validators=[DataRequired()])
    
    explanation = TextAreaField('Solution Explanation')
    submit = SubmitField('Add to Question Bank')


class CareerCounselorForm(FlaskForm):
    skills = TextAreaField('My Current Skills', validators=[DataRequired()])
    interests = TextAreaField('My Academic Interests', validators=[DataRequired()])
    preferred_domain = StringField('Target Placement Domain')
    submit = SubmitField('Map Career Path')


class StudyPlanForm(FlaskForm):
    plan_type = SelectField('Timeline Length', choices=[
        ('7-Day', '7-Day Fast Track (Immediate placement review)'),
        ('15-Day', '15-Day Sprint (Comprehensive concept training)'),
        ('30-Day', '30-Day Masterclass (Complete placement preparation)')
    ], validators=[DataRequired()])
    weak_topics = TextAreaField('Focus Areas / Weak Topics', validators=[DataRequired()])
    submit = SubmitField('Build Schedule')
