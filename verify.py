import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import sys

def verify_system():
    print("==================================================")
    print("       PrepAI Pro System Diagnostics Tool         ")
    print("==================================================")
    
    errors = 0
    warnings = 0
    
    # 1. Check folder dependencies
    folders = [
        "uploads",
        "uploads/resumes",
        "uploads/videos",
        "uploads/audio",
        "uploads/profiles"
    ]
    
    print("\n[+] Checking file directory assets:")
    for f in folders:
        if not os.path.exists(f):
            try:
                os.makedirs(f, exist_ok=True)
                print(f"  - Created directory: {f}")
            except Exception as e:
                print(f"  - ERROR: Failed creating directory {f}: {e}")
                errors += 1
        else:
            print(f"  - Verified directory: {f}")
            
    # 2. Check Python packages
    print("\n[+] Checking critical library dependencies:")
    critical_packages = [
        ("flask", "Flask"),
        ("flask_sqlalchemy", "Flask-SQLAlchemy"),
        ("flask_login", "Flask-Login"),
        ("flask_bcrypt", "Flask-Bcrypt"),
        ("PyPDF2", "PyPDF2"),
        ("pdfplumber", "pdfplumber"),
        ("google.generativeai", "google-generativeai")
    ]
    
    for pkg_import, pkg_name in critical_packages:
        try:
            __import__(pkg_import)
            print(f"  - Checked: {pkg_name} is installed.")
        except ImportError:
            print(f"  - ERROR: {pkg_name} is NOT installed. Run 'pip install -r requirements.txt'")
            errors += 1
            
    # 3. Check Gemini API configuration
    print("\n[+] Validating environment configurations:")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        print("  - WARNING: GEMINI_API_KEY is not set. Platform will operate in SIMULATED/MOCK mode.")
        print("    To activate complete AI generation, please set 'GEMINI_API_KEY' in your .env file.")
        warnings += 1
    else:
        print("  - Checked: GEMINI_API_KEY is defined in system environment.")
        
    print("\n==================================================")
    print(f"Diagnostics complete: {errors} Errors, {warnings} Warnings.")
    print("==================================================")
    
    if errors > 0:
        print("\n[!] Please resolve the errors above before launching the application.")
        sys.exit(1)
    else:
        print("\n[PASS] System is ready! You can now run the app:")
        print("    1. Run database seeder: 'python seed.py'")
        print("    2. Start development server: 'python app.py'")
        sys.exit(0)

if __name__ == "__main__":
    verify_system()
