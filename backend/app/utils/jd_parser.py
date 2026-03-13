"""
JD (Job Description) Parser - Hybrid Approach (Regex + spaCy)
Extracts structured data from job descriptions for AI matching
"""

import re
import spacy
from typing import Dict, List, Optional
from datetime import datetime


class JDParser:
    """
    Hybrid parser for Job Descriptions
    - Uses Regex for structured patterns (fast, reliable)
    - Uses spaCy for location detection and section analysis (intelligent, contextual)
    """
    
    def __init__(self):
        # Reuse same tech skills from resume parser
        self.tech_skills = [
            'Python', 'Java', 'Javascript', 'Typescript', 'C', 'C++', 'C#',
            'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go', 'Rust', 'Scala',
            'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django',
            'Flask', 'Spring', 'Fastapi', 'Laravel', 'Rails',
            'Html', 'Css', 'Sass', 'Bootstrap', 'Tailwind',
            'Sql', 'Mysql', 'Postgresql', 'Mongodb', 'Redis', 'Cassandra',
            'Aws', 'Azure', 'Gcp', 'Docker', 'Kubernetes', 'Jenkins',
            'Git', 'Gitlab', 'Github', 'Terraform',
            'Machine Learning', 'Deep Learning', 'Tensorflow', 'Pytorch',
            'Pandas', 'NumPy', 'Scikit-learn', 'Matplotlib', 'Seaborn',
            'Tableau', 'Power BI', 'Excel', 'Data Analysis', 'Statistics',
            'Data Cleaning', 'Data Warehousing', 'ETL', 'Spark', 'Hadoop',
            'Airflow', 'Kafka', 'Elasticsearch', 'Snowflake', 'Databricks',
            'Rest', 'Api', 'Graphql', 'Microservices'
        ]
        
        # Experience patterns - ordered by priority (most specific first)
        self.experience_patterns = [
            r'minimum\s*(?:of\s*)?(\d+)(?:[-–]\d+)?\s*years?',  # "Minimum 1-3 years" → captures 1
            r'at least\s*(\d+)\s*years?',  # "At least 2 years" → captures 2
            r'(\d+)[-–]\d+\s*years?',  # "1-3 years" (range) → captures 1 (minimum)
            r'(\d+)\+\s*years?',  # "5+ years" → captures 5
            r'(\d+)\s*(?:or more)?\s*years?\s*(?:of\s*)?experience',  # "3 years of experience"
            r'(\d+)\s*years?\s*(?:of\s*)?experience'  # Generic "3 years experience"
        ]
        
        # Salary patterns
        self.salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$?(\d{1,3}(?:,\d{3})*)',  # $120,000-$180,000
            r'\$(\d+)k\s*-\s*\$?(\d+)k',  # $120k-$180k
            r'(\d+)k\s*-\s*(\d+)k',  # 120k-180k
            r'\$(\d{1,3}(?:,\d{3})*)\s*/\s*(?:year|yr)',  # $150,000/year
        ]
        
        # Load spaCy model (same as resume parser)
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model loaded for JD parser")
        except:
            print("⚠️  Warning: spaCy model not loaded for JD parser")
            self.nlp = None
    
    def extract_required_skills(self, text: str) -> List[str]:
        """Extract required skills ONLY from Required Skills section"""
        # Find Required Skills section
        required_section = self._extract_section(
            text,
            start_patterns=[
                r'required\s+skills?[:\s]*',
                r'key\s+skills?[:\s]*',
                r'must\s+have[:\s]*',
                r'technical\s+skills?[:\s]*'
            ],
            end_patterns=[
                r'preferred\s+skills?',
                r'nice[\s-]to[\s-]have',
                r'optional\s+skills?',
                r'experience\s+requirements?',
                r'education\s+requirements?',
                r'qualifications?'
            ]
        )
        
        if not required_section:
            # Fallback: scan entire text but exclude preferred section
            preferred_section = self._extract_section(
                text,
                start_patterns=[
                    r'preferred[^:\n]*[:\s]*',
                    r'nice[\s-]to[\s-]have[^:\n]*[:\s]*',
                    r'optional\s+skills?[:\s]*'
                ],
                end_patterns=[r'experience\s+requirements?', r'education']
            )
            if preferred_section:
                # Remove preferred section from text
                required_section = text.replace(preferred_section, '')
            else:
                required_section = text
        
        # Extract skills from required section only
        skills_found = []
        text_lower = required_section.lower()
        
        for skill in self.tech_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                skills_found.append(skill)
        
        return list(set(skills_found))  # Remove duplicates
    
    def extract_min_experience(self, text: str) -> Optional[int]:
        """Extract minimum years of experience using regex patterns"""
        try:
            for pattern in self.experience_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    years = int(match.group(1))
                    # Sanity check
                    if 0 <= years <= 30:
                        return years
            return None
        except Exception as e:
            print(f"Error extracting experience: {e}")
            return None
    
    def _extract_section(self, text: str, start_patterns: List[str], end_patterns: List[str]) -> str:
        """Helper to extract text between start and end patterns"""
        for start_pattern in start_patterns:
            match = re.search(start_pattern, text, re.IGNORECASE)
            if match:
                start_pos = match.end()
                
                # Find end of section
                end_pos = len(text)
                for end_pattern in end_patterns:
                    end_match = re.search(end_pattern, text[start_pos:], re.IGNORECASE)
                    if end_match:
                        end_pos = start_pos + end_match.start()
                        break
                
                return text[start_pos:end_pos].strip()
        
        return ""
    
    def extract_education_level(self, text: str) -> str:
        """Extract required education level using flexible patterns"""
        text_lower = text.lower()
        
        # Check in order of specificity - very flexible patterns
        if re.search(r'\b(?:phd|ph\.d\.?|doctorate|doctoral)\b', text_lower):
            return 'PhD'
        elif re.search(r"\bmaster.{0,3}degree", text_lower) or re.search(r"\bmaster\s+(?:in|of)\b", text_lower) or re.search(r'\bm\.?\s*s\.?', text_lower):
            return "Master's Degree"
        elif re.search(r"\bbachelor.{0,3}degree", text_lower) or re.search(r"\bbachelor\s+(?:in|of)\b", text_lower) or re.search(r'\bb\.?\s*s\.?', text_lower):
            return "Bachelor's Degree"
        elif re.search(r'\bany\s+(?:graduate|degree)\b', text_lower) or re.search(r'\bany\s+field\b', text_lower):
            return 'Any Degree'
        elif re.search(r'\bnot\s+required\b', text_lower) or re.search(r'\bno\s+degree\b', text_lower) or re.search(r'\bhigh\s+school\b', text_lower) or re.search(r'\bdiploma\b', text_lower) or re.search(r'\bassociate.{0,3}degree', text_lower):
            return 'Not Required'
        else:
            return ''
    
    def extract_optional_skills(self, text: str, exclude_skills: List[str] = None) -> List[str]:
        """Extract optional/nice-to-have skills ONLY from Preferred section, excluding required skills"""
        # Find Preferred/Optional/Nice-to-have Skills section using helper
        preferred_section = self._extract_section(
            text,
            start_patterns=[
                r'preferred[^:\n]*[:\s]*',
                r'nice[\\s-]to[\\s-]have[^:\n]*[:\s]*',
                r'optional\\s+skills?[:\s]*',
                r'bonus\\s+skills?[:\s]*',
                r'plus[:\s]*',
                r'good\\s+to\\s+have[:\s]*',
                r'additional\\s+skills?[:\s]*'
            ],
            end_patterns=[
                r'experience\\s+requirements?',
                r'education\\s+requirements?',
                r'qualifications?',
                r'responsibilities',
                r'benefits',
                r'about\\s+(?:us|the\\s+company)',
                r'how\\s+to\\s+apply'
            ]
        )
        
        if not preferred_section:
            return []
        
        # Extract skills from preferred section only
        optional_skills = []
        exclude_lower = [s.lower() for s in (exclude_skills or [])]
        
        # Parse line-by-line for better accuracy
        lines = preferred_section.split('\n')
        for line in lines:
            line_lower = line.strip().lower()
            if not line_lower:
                continue
            
            for skill in self.tech_skills:
                # Skip if already in required skills
                if skill.lower() in exclude_lower:
                    continue
                    
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, line_lower):
                    optional_skills.append(skill)
        
        return list(set(optional_skills))
    
    def extract_salary_range(self, text: str) -> Optional[Dict]:
        """Extract salary range using regex patterns"""
        try:
            for pattern in self.salary_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    min_sal = match.group(1).replace(',', '')
                    max_sal = match.group(2).replace(',', '') if len(match.groups()) > 1 else None
                    
                    # Convert 'k' notation to thousands
                    if 'k' in pattern:
                        min_sal = int(min_sal) * 1000
                        max_sal = int(max_sal) * 1000 if max_sal else None
                    else:
                        min_sal = int(min_sal)
                        max_sal = int(max_sal) if max_sal else None
                    
                    # Sanity checks
                    if min_sal < 1000 or min_sal > 1000000:
                        continue
                    
                    return {
                        'min': min_sal,
                        'max': max_sal if max_sal else min_sal,
                        'currency': 'USD'
                    }
            
            return None
        except Exception as e:
            print(f"Error extracting salary: {e}")
            return None
    
    def extract_location(self, text: str) -> Optional[str]:
        """Extract location - Hybrid: regex first, spaCy GPE as fallback"""
        # Try regex first (look for "Location:" label)
        location_patterns = [
            r'location[:\s]+(.*?)(?=\n|$)',
            r'based in[:\s]+(.*?)(?=\n|$)',
            r'office[:\s]+(.*?)(?=\n|$)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2 and len(location) < 100:
                    return location
        
        # Fallback to spaCy NER (GPE - Geo-Political Entity)
        if self.nlp:
            try:
                doc = self.nlp(text[:500])  # First 500 chars
                locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
                if locations:
                    return locations[0]
            except Exception as e:
                print(f"spaCy location extraction failed: {e}")
        
        return None
    
    def extract_job_type(self, text: str) -> str:
        """Extract job type using keyword matching"""
        text_lower = text.lower()
        
        if 'full-time' in text_lower or 'full time' in text_lower or 'fulltime' in text_lower:
            return 'Full-time'
        elif 'part-time' in text_lower or 'part time' in text_lower or 'parttime' in text_lower:
            return 'Part-time'
        elif 'contract' in text_lower or 'contractor' in text_lower:
            return 'Contract'
        elif 'internship' in text_lower or 'intern' in text_lower:
            return 'Internship'
        elif 'temporary' in text_lower or 'temp' in text_lower:
            return 'Temporary'
        else:
            return 'Full-time'  # Default assumption
    
    def extract_work_mode(self, text: str) -> str:
        """Extract work mode using keyword matching"""
        text_lower = text.lower()
        
        # Check for remote first (most specific)
        if 'remote' in text_lower or 'work from home' in text_lower or 'wfh' in text_lower:
            if 'hybrid' in text_lower:
                return 'Hybrid'
            return 'Remote'
        elif 'hybrid' in text_lower:
            return 'Hybrid'
        elif 'on-site' in text_lower or 'onsite' in text_lower or 'office' in text_lower:
            return 'Onsite'
        else:
            return 'Onsite'  # Default assumption
    
    def parse(self, jd_text: str) -> Dict:
        """
        Main parsing function - Hybrid: Regex + spaCy
        Extracts ONLY fields that are NOT provided by the form:
        - Skills (required + optional)
        - Experience (min years)
        - Education level
        
        Does NOT extract (form provides these):
        - Location, Job Type, Work Mode, Salary
        """
        if not jd_text or len(jd_text) < 50:
            return {
                'requiredSkills': [],
                'minExperience': None,
                'educationLevel': None,
                'optionalSkills': [],
                'parsing_status': 'FAILED'
            }
        
        try:
            # Extract ONLY fields not provided by form
            required_skills = self.extract_required_skills(jd_text)
            min_experience = self.extract_min_experience(jd_text)
            education_level = self.extract_education_level(jd_text)
            # Pass required_skills to exclude them from optional
            optional_skills = self.extract_optional_skills(jd_text, exclude_skills=required_skills)
            
            return {
                # AI Matching fields (CRITICAL)
                'requiredSkills': required_skills,
                'minExperience': min_experience,
                'educationLevel': education_level,
                
                # Skill-Gap fields
                'optionalSkills': optional_skills,
                
                # Metadata
                'parsing_status': 'SUCCESS',
                'parsed_at': datetime.utcnow()
            }
        
        except Exception as e:
            print(f"Error parsing JD: {e}")
            return {
                'requiredSkills': [],
                'minExperience': None,
                'educationLevel': None,
                'optionalSkills': [],
                'parsing_status': 'FAILED'
            }
