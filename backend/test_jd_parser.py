"""
Test script for JD (Job Description) Parser
"""
import sys
sys.path.append('.')

from app.utils.jd_parser import JDParser

# Sample JD for testing
SAMPLE_JD = """
Senior Software Engineer - Tech Corp

Location: New York, NY
Job Type: Full-time
Work Mode: Remote

About the Role:
We are seeking a talented Senior Software Engineer with 5+ years of experience 
to join our growing engineering team.

Requirements:
- 5+ years of professional software development experience
- Strong proficiency in Python, Django, and PostgreSQL
- Experience with Docker and Kubernetes
- Bachelor's degree in Computer Science or related field required
- Master's degree preferred
- Experience with RESTful APIs and microservices architecture

Nice to Have:
- AWS or Azure cloud experience
- Experience with React or Vue.js
- Knowledge of CI/CD pipelines

Responsibilities:
- Design and develop scalable backend services
- Lead technical discussions and code reviews
- Mentor junior developers
- Collaborate with product and design teams

Benefits:
- Competitive salary ($120,000 - $180,000)
- Health, dental, and vision insurance
- 401(k) with company match
- Flexible work schedule
- Professional development budget

Apply now to join our innovative team!
"""

def test_jd_parser():
    print("🧪 Testing JD Parser (Hybrid: Regex + spaCy)...\n")
    
    parser = JDParser()
    
    # Test spaCy model loading
    if parser.nlp:
        print("✅ spaCy model loaded successfully")
    else:
        print("⚠️  spaCy model not loaded (will use regex fallback)")
    
    print("\n" + "="*60)
    print("PARSING SAMPLE JOB DESCRIPTION")
    print("="*60 + "\n")
    
    # Parse the sample JD
    result = parser.parse(SAMPLE_JD)
    
    print("📊 PARSING RESULTS:\n")
    
    # AI Matching fields (CRITICAL)
    print("🧠 AI MATCHING FIELDS:")
    print(f"  • Required Skills: {len(result.get('requiredSkills', []))} skills")
    print(f"    → {', '.join(result.get('requiredSkills', [])[:10])}")
    print(f"  • Min Experience: {result.get('minExperience')} years")
    print(f"  • Education Level: {result.get('educationLevel')}")
    
    # Skill-Gap fields
    print("\n🎯 SKILL-GAP FIELDS:")
    print(f"  • Optional Skills: {len(result.get('optionalSkills', []))} skills")
    if result.get('optionalSkills'):
        print(f"    → {', '.join(result.get('optionalSkills', []))}")
    
    # Filter fields
    print("\n🎛️  FILTER FIELDS:")
    print(f"  • Salary Range: {result.get('salaryRange')}")
    print(f"  • Location: {result.get('location')}")
    print(f"  • Job Type: {result.get('jobType')}")
    print(f"  • Work Mode: {result.get('workMode')}")
    
    print(f"\n✅ Parsing Status: {result.get('parsing_status')}")
    
    print("\n" + "="*60)
    print("VALIDATION CHECKS")
    print("="*60 + "\n")
    
    # Validation checks
    checks = {
        "Required Skills Extracted": len(result.get('requiredSkills', [])) > 0,
        "Experience Years Found": result.get('minExperience') is not None,
        "Education Level Detected": result.get('educationLevel') != 'Not specified',
        "Optional Skills Found": len(result.get('optionalSkills', [])) > 0,
        "Salary Range Extracted": result.get('salaryRange') is not None,
        "Location Found": result.get('location') is not None,
        "Job Type Detected": result.get('jobType') is not None,
        "Work Mode Detected": result.get('workMode') is not None,
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, status in checks.items():
        print(f"  {'✅' if status else '❌'} {check}")
    
    print(f"\n📈 Score: {passed}/{total} checks passed")
    print(f"   Accuracy: {(passed/total)*100:.1f}%\n")
    
    if passed >= total * 0.75:
        print("🎉 JD Parser is working well!")
    else:
        print("⚠️  Some fields not detected. Check the results above.")
    
    # Detailed results
    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60 + "\n")
    
    print("Required Skills:", result.get('requiredSkills'))
    print("\nOptional Skills:", result.get('optionalSkills'))
    print("\nExperience:", result.get('minExperience'), "years")
    print("Education:", result.get('educationLevel'))
    print("Salary:", result.get('salaryRange'))
    print("Location:", result.get('location'))
    print("Job Type:", result.get('jobType'))
    print("Work Mode:", result.get('workMode'))

if __name__ == "__main__":
    test_jd_parser()
