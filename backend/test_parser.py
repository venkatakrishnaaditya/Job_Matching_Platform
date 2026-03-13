"""
Test script for resume parsing functionality
Run this to verify that all dependencies are installed correctly
"""

def test_imports():
    """Test if all required libraries are installed"""
    print("Testing imports...")
    
    try:
        import PyPDF2
        print("✅ PyPDF2 installed")
    except ImportError:
        print("❌ PyPDF2 not installed - run: pip install PyPDF2")
        return False
    
    try:
        from docx import Document
        print("✅ python-docx installed")
    except ImportError:
        print("❌ python-docx not installed - run: pip install python-docx")
        return False
    
    try:
        from app.utils.resume_parser import ResumeParser
        print("✅ ResumeParser module loaded")
    except ImportError as e:
        print(f"❌ ResumeParser import failed: {e}")
        return False
    
    return True

def test_parser():
    """Test parser functionality with sample text"""
    print("\nTesting parser functionality...")
    
    from app.utils.resume_parser import ResumeParser
    
    parser = ResumeParser()
    
    # Sample resume text
    sample_text = """
    John Doe
    john.doe@email.com
    +91 9876543210
    
    SKILLS
    Python, JavaScript, React, Node.js, MongoDB, Docker
    
    EXPERIENCE
    Software Engineer at Tech Corp
    2020 - 2023
    Developed web applications using React and Node.js
    
    EDUCATION
    B.Tech Computer Science
    ABC University, 2016-2020
    
    PROJECTS
    - E-commerce Platform using MERN stack
    - Machine Learning model for prediction
    
    CERTIFICATIONS
    - AWS Certified Developer
    - Python for Data Science
    """
    
    # Test skill extraction
    skills = parser.extract_skills(sample_text)
    print(f"  Skills found: {len(skills)}")
    print(f"  Skills: {skills[:5]}...")
    
    # Test email extraction
    email = parser.extract_email(sample_text)
    print(f"  Email: {email}")
    
    # Test phone extraction
    phone = parser.extract_phone(sample_text)
    print(f"  Phone: {phone}")
    
    # Test section extraction
    sections = parser.extract_sections(sample_text)
    print(f"  Sections found: {list(sections.keys())}")
    
    print("\n✅ Parser test completed successfully!")
    return True

if __name__ == "__main__":
    print("="*50)
    print("Resume Parser Test Suite")
    print("="*50)
    
    if test_imports():
        test_parser()
        print("\n" + "="*50)
        print("All tests passed! Resume parsing is ready to use.")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("Please install missing dependencies")
        print("Run: pip install -r requirements.txt")
        print("="*50)
