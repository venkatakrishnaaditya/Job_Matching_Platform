"""
Test script for hybrid resume parser (Regex + spaCy)
"""
import sys
sys.path.append('.')

from app.utils.resume_parser import ResumeParser

# Sample resume text for testing
SAMPLE_RESUME = """
John Michael Smith
Email: john.smith@email.com
Phone: +1 (555) 123-4567

PROFESSIONAL SUMMARY
Senior Software Engineer with 8+ years of experience in full-stack development

EXPERIENCE
Senior Software Engineer | Tech Corp Inc. | 2020-2024
- Developed scalable microservices using Python and FastAPI
- Led a team of 5 developers in building cloud-native applications
- Implemented CI/CD pipelines using Docker and Kubernetes

Software Engineer | StartupXYZ | 2017-2020  
- Built REST APIs using Node.js and Express
- Worked with MongoDB, PostgreSQL, and Redis databases
- Developed frontend applications using React and TypeScript

Junior Developer | WebSolutions Ltd. | 2016-2017
- Created responsive web applications
- Used JavaScript, HTML, CSS, and jQuery

EDUCATION
Bachelor of Science in Computer Science | MIT | 2016

SKILLS
Python, FastAPI, Node.js, React, TypeScript, MongoDB, PostgreSQL, Docker, 
Kubernetes, AWS, Azure, Git, CI/CD, Microservices, REST APIs

CERTIFICATIONS
- AWS Certified Solutions Architect
- Google Cloud Professional
"""

def test_hybrid_parser():
    print("🧪 Testing Hybrid Parser (Regex + spaCy)...\n")
    
    parser = ResumeParser()
    
    # Test spaCy model loading
    if parser.nlp:
        print("✅ spaCy model loaded successfully")
    else:
        print("⚠️  spaCy model not loaded (will use regex fallback)")
    
    print("\n" + "="*60)
    print("PARSING SAMPLE RESUME")
    print("="*60 + "\n")
    
    # Parse the sample resume (treating as text)
    result = parser.parse(SAMPLE_RESUME.encode('utf-8'), 'txt')
    
    print("📊 PARSING RESULTS:\n")
    
    # New spaCy-extracted fields
    print("🆕 HYBRID FIELDS (spaCy):")
    print(f"  • Candidate Name: {result.get('candidateName')}")
    print(f"  • Total Experience: {result.get('totalExperienceYears')} years")
    print(f"  • Current Job Title: {result.get('currentJobTitle')}")
    
    print("\n📋 REGEX FIELDS (Traditional):")
    print(f"  • Email: {result.get('email')}")
    print(f"  • Phone: {result.get('phone')}")
    print(f"  • Skills Found: {len(result.get('skills', []))} skills")
    print(f"    → {', '.join(result.get('skills', [])[:10])}")
    print(f"  • Experience Entries: {len(result.get('experience', []))}")
    print(f"  • Education Entries: {len(result.get('education', []))}")
    print(f"  • Projects: {len(result.get('projects', []))}")
    print(f"  • Certifications: {len(result.get('certifications', []))}")
    
    print(f"\n✅ Parsing Status: {result.get('parsing_status')}")
    
    print("\n" + "="*60)
    print("EXPERIENCE DETAILS:")
    print("="*60 + "\n")
    
    for i, exp in enumerate(result.get('experience', []), 1):
        print(f"{i}. {exp.get('description')[:80]}...")
        print(f"   Years: {exp.get('years')}")
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")
    
    # Validation checks
    checks = {
        "Candidate Name Extracted": result.get('candidateName') is not None,
        "Experience Years Calculated": result.get('totalExperienceYears') is not None,
        "Job Title Extracted": result.get('currentJobTitle') is not None,
        "Email Found": result.get('email') is not None,
        "Phone Found": result.get('phone') is not None,
        "Skills Found": len(result.get('skills', [])) > 0,
        "Experience Parsed": len(result.get('experience', [])) > 0,
        "Education Parsed": len(result.get('education', [])) > 0,
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, status in checks.items():
        print(f"  {'✅' if status else '❌'} {check}")
    
    print(f"\n📈 Score: {passed}/{total} checks passed")
    print(f"   Accuracy: {(passed/total)*100:.1f}%\n")
    
    if passed == total:
        print("🎉 All tests passed! Hybrid parser is working perfectly!")
    elif passed >= total * 0.75:
        print("✅ Hybrid parser is working well!")
    else:
        print("⚠️  Some issues detected. Check the results above.")

if __name__ == "__main__":
    test_hybrid_parser()
