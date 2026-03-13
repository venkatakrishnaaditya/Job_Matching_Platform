"""
Match Calculator - Combines skills, experience, and education scores
Uses weighted scoring to produce final match percentage
"""

from typing import Dict, Optional


class MatchCalculator:
    """
    Calculates final match score using weighted components:
    - Skills: 55%
    - Experience: 25%
    - Education: 20%
    """
    
    # Fixed weights for MVP
    WEIGHTS = {
        'skills': 0.70,      # 70% - Skills are most important
        'experience': 0.20,  # 20% - Reduced from 25%
        'education': 0.10    # 10% - Reduced from 20%
    }
    
    # Education hierarchy
    EDUCATION_LEVELS = {
        'Not Required': 1,
        'Any Degree': 2,
        "Bachelor's Degree": 3,
        "Master's Degree": 4,
        'PhD': 5,
        '': 1,  # Empty string = Not Required
        None: 1
    }
    
    @staticmethod
    def calculate_experience_score(
        candidate_years: Optional[float], 
        job_min_years: Optional[int]
    ) -> float:
        """
        Calculate experience match score (0.0 to 1.0)
        
        Formula: min(candidate_years / job_min_years, 1.0)
        
        Args:
            candidate_years: Candidate's total experience in years
            job_min_years: Minimum years required by job
        
        Returns:
            float: Experience score (0.0 to 1.0)
        """
        
        # Handle missing data
        if candidate_years is None:
            return 0.5  # Unknown = 50% (neutral)
        
        if job_min_years is None or job_min_years == 0:
            return 1.0  # Entry-level job, everyone qualifies
        
        # Sanity checks
        if candidate_years < 0:
            candidate_years = 0
        
        if job_min_years > 50:  # Likely a data entry error
            job_min_years = 5
        
        # Calculate score
        score = min(candidate_years / job_min_years, 1.0)
        
        return score
    
    @staticmethod
    def extract_education_level(education_array) -> int:
        """
        Extract education level from parsed education data
        
        Args:
            education_array: List of education objects with 'description' field
        
        Returns:
            int: Education level (1-5)
        """
        if not education_array or len(education_array) == 0:
            return 2  # Assume 'Any Degree' if not specified
        
        # Check first entry (highest degree usually listed first)
        first_edu = education_array[0].get('description', '').lower()
        
        if 'phd' in first_edu or 'ph.d' in first_edu or 'doctorate' in first_edu:
            return 5  # PhD
        elif 'master' in first_edu or "master's" in first_edu or 'm.tech' in first_edu or 'msc' in first_edu or 'm.sc' in first_edu:
            return 4  # Master's
        elif 'bachelor' in first_edu or "bachelor's" in first_edu or 'b.tech' in first_edu or 'bsc' in first_edu or 'b.sc' in first_edu or 'b.e' in first_edu:
            return 3  # Bachelor's
        else:
            return 2  # Any Degree
    
    @classmethod
    def calculate_education_score(
        cls,
        candidate_level: Optional[int],
        required_level: Optional[int]
    ) -> float:
        """
        Calculate education match score (0.0 to 1.0)
        
        Uses ordinal comparison with graduated penalty
        
        Args:
            candidate_level: Candidate's education level (1-5)
            required_level: Required education level (1-5)
        
        Returns:
            float: Education score (0.0 to 1.0)
        """
        
        # Handle missing data
        if candidate_level is None:
            if required_level is None or required_level <= 2:
                return 0.8  # Likely OK for Not Required/Any Degree
            else:
                return 0.5  # Unknown for specific requirement
        
        if required_level is None or required_level == 1:
            return 1.0  # Not Required - everyone qualifies
        
        # Meets or exceeds requirement
        if candidate_level >= required_level:
            return 1.0
        
        # Below requirement - graduated penalty
        gap = required_level - candidate_level
        
        if gap == 1:
            return 0.7  # One level below (e.g., Bachelor for Master job)
        elif gap == 2:
            return 0.4  # Two levels below
        else:
            return 0.2  # Three+ levels below
    
    @classmethod
    def calculate_final_score(
        cls,
        skills_similarity: float,
        experience_score: float,
        education_score: float
    ) -> Dict:
        """
        Calculate weighted final match score
        
        Args:
            skills_similarity: Skills match (0.0 to 1.0)
            experience_score: Experience match (0.0 to 1.0)
            education_score: Education match (0.0 to 1.0)
        
        Returns:
            dict: {
                'overall_score': int (0-100),
                'breakdown': {
                    'skills': {'score': float, 'percentage': int},
                    'experience': {'score': float, 'percentage': int},
                    'education': {'score': float, 'percentage': int}
                }
            }
        """
        
        # Calculate weighted contributions
        skills_contribution = skills_similarity * cls.WEIGHTS['skills']
        experience_contribution = experience_score * cls.WEIGHTS['experience']
        education_contribution = education_score * cls.WEIGHTS['education']
        
        # Final score (0-1 scale)
        final_score = (
            skills_contribution +
            experience_contribution +
            education_contribution
        )
        
        # Convert to percentage
        overall_percentage = round(final_score * 100)
        
        # Build breakdown
        breakdown = {
            'skills': {
                'score': round(skills_similarity, 2),
                'percentage': round(skills_similarity * 100),
                'weight': cls.WEIGHTS['skills'],
                'contribution': round(skills_contribution * 100, 1)
            },
            'experience': {
                'score': round(experience_score, 2),
                'percentage': round(experience_score * 100),
                'weight': cls.WEIGHTS['experience'],
                'contribution': round(experience_contribution * 100, 1)
            },
            'education': {
                'score': round(education_score, 2),
                'percentage': round(education_score * 100),
                'weight': cls.WEIGHTS['education'],
                'contribution': round(education_contribution * 100, 1)
            }
        }
        
        return {
            'overall_score': overall_percentage,
            'breakdown': breakdown
        }
    
    @classmethod
    def get_match_label(cls, score: int) -> str:
        """
        Get descriptive label for match score
        
        Args:
            score: Match percentage (0-100)
        
        Returns:
            str: Match label
        """
        if score >= 90:
            return "Excellent Match"
        elif score >= 70:
            return "Good Match"
        elif score >= 50:
            return "Fair Match"
        else:
            return "Weak Match"
    
    @classmethod
    def get_match_color(cls, score: int) -> str:
        """
        Get color indicator for match score
        
        Args:
            score: Match percentage (0-100)
        
        Returns:
            str: Color name
        """
        if score >= 90:
            return "green"
        elif score >= 70:
            return "blue"
        elif score >= 50:
            return "yellow"
        else:
            return "gray"
