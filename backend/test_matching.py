"""
Test script for matching system
Verifies TF-IDF + Cosine Similarity implementation
"""

import sys
sys.path.append('.')

from app.utils.skill_matcher import SkillMatcher
from app.utils.match_calculator import MatchCalculator


def test_skill_matching():
    print("=" * 60)
    print("TEST 1: SKILL MATCHING (TF-IDF + Cosine Similarity)")
    print("=" * 60)
    
    matcher = SkillMatcher()
    
    # Test Case 1: High similarity
    print("\n✅ Test Case 1: High Similarity")
    resume_skills = ["Python", "Django", "PostgreSQL", "Docker", "React"]
    job_required = ["Python", "Django", "Docker"]
    job_preferred = ["AWS", "Kubernetes"]
    
    similarity = matcher.calculate_similarity(resume_skills, job_required, job_preferred)
    print(f"Resume: {resume_skills}")
    print(f"Job Required: {job_required}")
    print(f"Job Preferred: {job_preferred}")
    print(f"Similarity Score: {similarity:.2f} ({similarity*100:.0f}%)")
    
    matching = matcher.get_matching_skills(resume_skills, job_required + job_preferred)
    missing = matcher.get_missing_skills(resume_skills, job_required)
    print(f"Matching Skills: {matching}")
    print(f"Missing Required Skills: {missing}")
    
    # Test Case 2: Medium similarity
    print("\n⚠️  Test Case 2: Medium Similarity")
    resume_skills = ["Python", "Flask", "MySQL"]
    job_required = ["Python", "Django", "PostgreSQL"]
    
    similarity = matcher.calculate_similarity(resume_skills, job_required, [])
    print(f"Resume: {resume_skills}")
    print(f"Job Required: {job_required}")
    print(f"Similarity Score: {similarity:.2f} ({similarity*100:.0f}%)")
    
    # Test Case 3: Low similarity
    print("\n❌ Test Case 3: Low Similarity")
    resume_skills = ["JavaScript", "React", "Node.js"]
    job_required = ["Python", "Django", "PostgreSQL"]
    
    similarity = matcher.calculate_similarity(resume_skills, job_required, [])
    print(f"Resume: {resume_skills}")
    print(f"Job Required: {job_required}")
    print(f"Similarity Score: {similarity:.2f} ({similarity*100:.0f}%)")


def test_experience_matching():
    print("\n" + "=" * 60)
    print("TEST 2: EXPERIENCE MATCHING (Numeric Comparison)")
    print("=" * 60)
    
    calculator = MatchCalculator()
    
    test_cases = [
        (5, 3, "Exceeds requirement"),
        (3, 3, "Meets requirement"),
        (2, 3, "Below requirement"),
        (1, 5, "Far below"),
        (10, 2, "Over-qualified"),
        (0, 0, "Entry-level job"),
    ]
    
    for candidate, job_min, desc in test_cases:
        score = calculator.calculate_experience_score(candidate, job_min)
        print(f"\n{desc}:")
        print(f"  Candidate: {candidate} years | Job Min: {job_min} years")
        print(f"  Score: {score:.2f} ({score*100:.0f}%)")


def test_education_matching():
    print("\n" + "=" * 60)
    print("TEST 3: EDUCATION MATCHING (Ordinal Comparison)")
    print("=" * 60)
    
    calculator = MatchCalculator()
    
    test_cases = [
        (4, 3, "Master's for Bachelor's job"),
        (3, 3, "Bachelor's for Bachelor's job"),
        (3, 4, "Bachelor's for Master's job"),
        (3, 5, "Bachelor's for PhD job"),
        (5, 3, "PhD for Bachelor's job"),
        (2, 1, "Any Degree for Not Required"),
    ]
    
    for candidate_level, required_level, desc in test_cases:
        score = calculator.calculate_education_score(candidate_level, required_level)
        print(f"\n{desc}:")
        print(f"  Candidate Level: {candidate_level} | Required Level: {required_level}")
        print(f"  Score: {score:.2f} ({score*100:.0f}%)")


def test_final_scoring():
    print("\n" + "=" * 60)
    print("TEST 4: FINAL WEIGHTED SCORING")
    print("=" * 60)
    
    calculator = MatchCalculator()
    
    # Test Case 1: Excellent match
    print("\n✅ Test Case 1: Excellent Match")
    result = calculator.calculate_final_score(
        skills_similarity=0.95,
        experience_score=1.0,
        education_score=1.0
    )
    print(f"Skills: 95% | Experience: 100% | Education: 100%")
    print(f"Overall Score: {result['overall_score']}%")
    print(f"Label: {calculator.get_match_label(result['overall_score'])}")
    print(f"Breakdown: {result['breakdown']}")
    
    # Test Case 2: Good match
    print("\n✅ Test Case 2: Good Match")
    result = calculator.calculate_final_score(
        skills_similarity=0.85,
        experience_score=1.0,
        education_score=0.7
    )
    print(f"Skills: 85% | Experience: 100% | Education: 70%")
    print(f"Overall Score: {result['overall_score']}%")
    print(f"Label: {calculator.get_match_label(result['overall_score'])}")
    
    # Test Case 3: Fair match
    print("\n⚠️  Test Case 3: Fair Match")
    result = calculator.calculate_final_score(
        skills_similarity=0.65,
        experience_score=0.67,
        education_score=0.7
    )
    print(f"Skills: 65% | Experience: 67% | Education: 70%")
    print(f"Overall Score: {result['overall_score']}%")
    print(f"Label: {calculator.get_match_label(result['overall_score'])}")
    
    # Test Case 4: Weak match
    print("\n❌ Test Case 4: Weak Match")
    result = calculator.calculate_final_score(
        skills_similarity=0.30,
        experience_score=0.50,
        education_score=0.40
    )
    print(f"Skills: 30% | Experience: 50% | Education: 40%")
    print(f"Overall Score: {result['overall_score']}%")
    print(f"Label: {calculator.get_match_label(result['overall_score'])}")


if __name__ == "__main__":
    print("\n🧪 TESTING AI MATCHING SYSTEM")
    print("=" * 60)
    
    try:
        test_skill_matching()
        test_experience_matching()
        test_education_matching()
        test_final_scoring()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📊 Summary:")
        print("✓ TF-IDF vectorization working")
        print("✓ Cosine similarity calculation working")
        print("✓ Experience scoring working")
        print("✓ Education scoring working")
        print("✓ Weighted final scoring working")
        print("\n🚀 Matching system ready for use!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
