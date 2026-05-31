import os
import json
import re
import google.generativeai as genai
from config import Config

class GeminiService:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("Gemini API initialized successfully!")
            except Exception as e:
                print(f"Failed to initialize Gemini API: {e}. Running in Mock Mode.")
                self.enabled = False
        else:
            print("Gemini API key not found. Running in Mock Mode.")

    def _clean_json_response(self, text):
        """Cleans and extracts JSON content from Gemini markdown blocks."""
        # Find anything between ```json and ``` or ``` and ```
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            clean_text = match.group(1).strip()
        else:
            clean_text = text.strip()
            
        # Clean potential single trailing commas or unmatched braces
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # Try to fix basic JSON syntax errors or return as is for manual repair
            try:
                # Remove JS style comments
                clean_text = re.sub(r'//.*?\n', '', clean_text)
                return json.loads(clean_text)
            except Exception:
                raise ValueError(f"Could not parse Gemini JSON response: {text[:200]}...")

    def analyze_resume_ats(self, resume_text):
        """
        Extracts skills, measures ATS score (0-100), analyzes layout, formatting,
        education, and outputs strengths, weaknesses, missing keywords, and suggestions.
        """
        if not self.enabled:
            return self._get_mock_resume_analysis(resume_text)
            
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) recruiter and resume coach. 
        Analyze the following resume text and provide a comprehensive feedback report.
        You MUST respond in EXACT JSON format with the following keys. Do not include any text before or after the JSON:
        {{
            "ats_score": 82, // An integer between 0 and 100 representing the compatibility score.
            "strengths": ["strength 1", "strength 2"], // Array of strings detailing resume strengths.
            "weaknesses": ["weakness 1", "weakness 2"], // Array of strings detailing resume weaknesses.
            "suggestions": ["suggestion 1", "suggestion 2"], // Array of strings with improvements.
            "skills": ["Skill 1", "Skill 2"], // Array of identified skills.
            "missing_keywords": ["keyword 1", "keyword 2"], // Array of keywords that are missing but recommended for placement.
            "formatting_feedback": "A short paragraph describing layout, structure, and text formatting."
        }}

        Resume Content to Analyze:
        {resume_text}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._clean_json_response(response.text)
        except Exception as e:
            print(f"Gemini API Error in analyze_resume_ats: {e}. Falling back to simulation.")
            return self._get_mock_resume_analysis(resume_text)

    def generate_interview_questions(self, domain, count=5):
        """
        Generates structured technical or HR mock interview questions based on domain.
        """
        if not self.enabled:
            return self._get_mock_interview_questions(domain, count)
            
        prompt = f"""
        You are a senior technical interviewer for the domain: {domain}.
        Generate {count} distinct and highly relevant interview questions.
        You MUST respond in EXACT JSON format containing an array of objects. Do not include any text before or after the JSON:
        [
            {{
                "question_number": 1,
                "question_text": "The full text of question 1..."
            }},
            {{
                "question_number": 2,
                "question_text": "The full text of question 2..."
            }}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._clean_json_response(response.text)
        except Exception as e:
            print(f"Gemini API Error in generate_interview_questions: {e}. Falling back to simulation.")
            return self._get_mock_interview_questions(domain, count)

    def evaluate_interview_answers(self, domain, questions_and_answers):
        """
        Evaluates a set of user interview answers against questions.
        Expected format of questions_and_answers list of dicts: [{'question': '...', 'answer': '...'}]
        """
        if not self.enabled:
            return self._get_mock_interview_evaluation(domain, questions_and_answers)
            
        qa_text = ""
        for idx, item in enumerate(questions_and_answers):
            qa_text += f"\nQ{idx+1}: {item['question']}\nA{idx+1}: {item['answer']}\n"
            
        prompt = f"""
        You are a senior interviewer evaluating a candidate's responses for a {domain} interview.
        Read the following question-and-answer transcript. Rate the candidate's average score (0 to 100) and provide a detailed analysis.
        You MUST respond in EXACT JSON format with the following keys. Do not include any text before or after the JSON:
        {{
            "score": 75, // Integer between 0 and 100
            "feedback": "Overall executive summary paragraph explaining candidate's performance, technical depth, and communication.",
            "detailed_evaluation": [
                {{
                    "question": "question text",
                    "answer": "answer text",
                    "score": 80, // Integer score for this specific answer out of 100
                    "critique": "Feedback on this answer: what was good, what was missing, and the ideal key points."
                }}
            ]
        }}
        
        Transcript:
        {qa_text}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._clean_json_response(response.text)
        except Exception as e:
            print(f"Gemini API Error in evaluate_interview_answers: {e}. Falling back to simulation.")
            return self._get_mock_interview_evaluation(domain, questions_and_answers)

    def evaluate_voice_response(self, question, transcript):
        """
        Evaluates voice transcripts across parameters: fluency, confidence,
        technical accuracy, grammar, and relevance.
        """
        if not self.enabled:
            return self._get_mock_voice_evaluation(question, transcript)
            
        prompt = f"""
        You are a communications specialist and technical reviewer evaluating a spoken mock interview response.
        Review the question and the transcript of the candidate's answer. Assess performance on 5 pillars, each scored out of 100.
        You MUST respond in EXACT JSON format. Do not include any text before or after the JSON:
        {{
            "fluency_score": 80, // Assess speech smooth flow, pauses, fillers
            "confidence_score": 85, // Assess assertiveness and vocabulary choice
            "technical_accuracy_score": 75, // Verify exact factual correctness
            "grammar_score": 90, // Assess grammar structure and sentence construction
            "relevance_score": 88, // Assess whether the answer directly solves the prompt
            "feedback": "A summary paragraph reviewing their verbal communication style, tone, and logical structuring."
        }}
        
        Question: {question}
        Answer Transcript: {transcript}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._clean_json_response(response.text)
        except Exception as e:
            print(f"Gemini API Error in evaluate_voice_response: {e}. Falling back to simulation.")
            return self._get_mock_voice_evaluation(question, transcript)

    def generate_career_guidance(self, skills, interests, preferred_domain):
        """
        Generates a structured career guidance roadmap.
        """
        if not self.enabled:
            return self._get_mock_career_guidance(skills, interests, preferred_domain)
            
        prompt = f"""
        You are an elite career counselor aligned with SDG 4 (Quality Education).
        Provide custom recommendations for a student with:
        - Skills: {skills}
        - Interests: {interests}
        - Preferred Domain: {preferred_domain}

        You MUST respond in EXACT JSON format. Do not include any text before or after the JSON:
        {{
            "career_paths": "### Suggested Career Paths\\n1. **Path A**\\nDescription...\\n\\n2. **Path B**\\nDescription...",
            "required_skills": "### Essential Skills to Acquire\\n- **Skill A**: Why and how...\\n- **Skill B**: Why and how...",
            "roadmap": "### Learning Roadmap\\n#### Month 1-2: Fundamentals\\n- Task 1...\\n#### Month 3-4: Projects\\n- Task 2...",
            "certifications": "### Recommended Certifications\\n- **Cert A** (Provider): Description\\n- **Cert B** (Provider): Description"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._clean_json_response(response.text)
        except Exception as e:
            print(f"Gemini API Error in generate_career_guidance: {e}. Falling back to simulation.")
            return self._get_mock_career_guidance(skills, interests, preferred_domain)

    def generate_study_plan(self, plan_type, interview_scores, aptitude_scores, weak_topics):
        """
        Generates a custom daily roadmap (7, 15, or 30 days) to help the student level up.
        """
        if not self.enabled:
            return self._get_mock_study_plan(plan_type, interview_scores, aptitude_scores, weak_topics)
            
        prompt = f"""
        You are an academic mentor. Design a highly detailed day-by-day {plan_type} study plan for a student.
        Academic Context:
        - Mock Interview Average: {interview_scores}%
        - Aptitude Scores: {aptitude_scores}%
        - Weak Areas: {weak_topics}

        You MUST respond in EXACT JSON format. Do not include any text before or after the JSON:
        {{
            "plan_type": "{plan_type}",
            "plan_content": "# Personalized {plan_type} Preparation Blueprint\\n\\n## Analysis Overview\\nBased on your average interview score of {interview_scores}% and weak areas, here is your path to placement readiness.\\n\\n## Day-by-Day Roadmap\\n- **Day 1**: [Focus Area] details...\\n- **Day 2**: [Focus Area] details..."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._clean_json_response(response.text)
        except Exception as e:
            print(f"Gemini API Error in generate_study_plan: {e}. Falling back to simulation.")
            return self._get_mock_study_plan(plan_type, interview_scores, aptitude_scores, weak_topics)

    # ------------------ MOCK GENERATORS FOR OFFLINE / KEYLESS USE ------------------
    
    def _get_mock_resume_analysis(self, resume_text):
        # Basic parsing of resume_text for realistic mock behavior
        found_skills = []
        for word in ["python", "javascript", "c++", "java", "sql", "html", "css", "django", "flask", "react"]:
            if word in resume_text.lower():
                found_skills.append(word.capitalize())
        if not found_skills:
            found_skills = ["Software Engineering", "Problem Solving", "Object-Oriented Programming"]
            
        missing_kw = ["Docker", "CI/CD", "AWS Cloud", "Git Version Control", "Data Structures", "Algorithms"]
        
        return {
            "ats_score": 74,
            "strengths": [
                "Good descriptive project structures",
                "Clear educational credentials",
                "Incorporation of modern programming frameworks"
            ],
            "weaknesses": [
                "Lack of quantifiable metrics (e.g. 'Improved efficiency by X%')",
                "Missing industry-standard DevOps terminology",
                "Summary section is too generic"
            ],
            "suggestions": [
                "Add performance metrics to project bullet points",
                "Incorporate cloud deployment tools (e.g. Docker, AWS)",
                "Shorten descriptions to focus on active verbs"
            ],
            "skills": found_skills,
            "missing_keywords": missing_kw,
            "formatting_feedback": "The document has high parseability. Recommended to keep the layout single-column to satisfy all older ATS engines."
        }

    def _get_mock_interview_questions(self, domain, count):
        questions_pool = {
            "Python": [
                "Explain the difference between deep copy and shallow copy in Python.",
                "What are decorators in Python and how do you write one?",
                "How does memory management work in Python (garbage collection and GIL)?",
                "Explain list comprehensions and generator expressions.",
                "What is the difference between *args and **kwargs in Python function definitions?"
            ],
            "Java": [
                "What is JVM, JRE, and JDK? How do they differ?",
                "Explain Object-Oriented Programming (OOP) concepts in Java.",
                "What is the difference between Interface and Abstract class in Java?",
                "Explain garbage collection and memory segments in Java.",
                "What are Java Collections? Differentiate between List, Set, and Map."
            ],
            "DBMS": [
                "What is normalization? Differentiate between 1NF, 2NF, and 3NF.",
                "Explain ACID properties in database transaction management.",
                "What is the difference between primary key, unique key, and foreign key?",
                "Explain SQL joins with code structures (Inner, Left, Right, Full).",
                "What are indexes and how do they speed up database queries?"
            ],
            "DSA": [
                "Explain the difference between Array and Linked List data structures.",
                "How does binary search work? What is its time complexity?",
                "What is a hash collision? How are collisions handled?",
                "Explain the Quick Sort algorithm and its average vs worst-case complexities.",
                "Differentiate between Depth-First Search (DFS) and Breadth-First Search (BFS)."
            ]
        }
        
        selected_questions = questions_pool.get(domain, [
            f"Explain a core challenge you faced in a {domain} project and how you solved it.",
            f"What are the best practices in code optimization and design patterns for {domain}?",
            f"How do you handle error handling and exceptions in {domain}?",
            f"Explain memory layout and processing models in {domain}.",
            f"Describe the difference between synchronous and asynchronous operations in {domain}."
        ])
        
        return [{"question_number": i + 1, "question_text": q} for i, q in enumerate(selected_questions[:count])]

    def _get_mock_interview_evaluation(self, domain, qas):
        score = 80
        details = []
        for idx, qa in enumerate(qas):
            ans_len = len(qa['answer'])
            ans_score = 65 if ans_len < 30 else (85 if ans_len > 120 else 75)
            
            details.append({
                "question": qa['question'],
                "answer": qa['answer'],
                "score": ans_score,
                "critique": f"Good concise answer. {'However, adding code syntax or specific technical terminology would improve depth.' if ans_len < 80 else 'Nice structure and depth.'}"
            })
            
        return {
            "score": round(sum(d['score'] for d in details) / len(details)) if details else 0,
            "feedback": f"Strong general demonstration of {domain} syntax and foundations. Practice explaining edge-cases and runtime trade-offs.",
            "detailed_evaluation": details
        }

    def _get_mock_voice_evaluation(self, question, transcript):
        word_count = len(transcript.split())
        fluency = min(60 + word_count // 3, 92)
        confidence = min(65 + word_count // 4, 95)
        accuracy = 82 if word_count > 30 else 60
        grammar = 85
        relevance = 88
        
        return {
            "fluency_score": fluency,
            "confidence_score": confidence,
            "technical_accuracy_score": accuracy,
            "grammar_score": grammar,
            "relevance_score": relevance,
            "feedback": "The speaker displayed good steady delivery. Speed was appropriate, and response was relevant. Recommend reducing filler words and pacing more deliberately."
        }

    def _get_mock_career_guidance(self, skills, interests, preferred_domain):
        return {
            "career_paths": f"### Suggested Career Paths\n1. **{preferred_domain or 'Cloud Engineer'}**\nUsing your interests in {interests}, this role fits your background.\n\n2. **Full-Stack Developer**\nLeveraging skills in {skills} to develop client-server web apps.",
            "required_skills": f"### Essential Skills to Acquire\n- **Backend Frameworks**: Mastery of Flask/Django or Node.js\n- **DevOps Foundations**: Docker, Git, CI/CD setups",
            "roadmap": "### Learning Roadmap\n#### Weeks 1-4: Advanced Programming\n- Practice data structures and algorithms in Python/Java.\n#### Weeks 5-8: Capstone Project\n- Design and host a modern web app on GitHub.",
            "certifications": "### Recommended Certifications\n- **AWS Certified Developer** (Amazon)\n- **Google Professional Cloud Architect** (Google Cloud)"
        }

    def _get_mock_study_plan(self, plan_type, interview_scores, aptitude_scores, weak_topics):
        return {
            "plan_type": plan_type,
            "plan_content": f"# Personalized {plan_type} Prep Blueprint\n\n## Performance Analysis\n- **Interview Base**: {interview_scores}%\n- **Aptitude Base**: {aptitude_scores}%\n- **Identified Focus**: {weak_topics}\n\n## Day-by-Day Breakdown\n- **Day 1**: Solve 10 Easy-to-Medium problems in {weak_topics}.\n- **Day 2**: Conduct a full mock interview and focus on speaking confidence.\n- **Day 3**: Focus on {weak_topics} edge cases and review core formulas.\n- **Day 4-7**: Complete full-length practice exams and track timing."
        }
