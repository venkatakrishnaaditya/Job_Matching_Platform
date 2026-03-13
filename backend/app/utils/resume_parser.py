import re
from typing import Dict, List, Optional
import PyPDF2
from docx import Document
import io
import spacy
from datetime import datetime

class ResumeParser:
    """Hybrid parser: Regex (fast, reliable) + spaCy (intelligent, contextual)"""
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not loaded. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Common skill keywords (expandable) - Comprehensive list for ATS matching
        self.tech_skills = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', '.net',
            'php', 'ruby', 'go', 'rust', 'scala', 'kotlin', 'swift', 'r',
            
            # Web Frameworks
            'react', 'angular', 'vue', 'node.js', 'nodejs', 'express',
            'django', 'flask', 'fastapi', 'spring', 'springboot', 'spring boot',
            'next.js', 'nextjs', 'nuxt', 'svelte',
            
            # Frontend
            'html', 'css', 'sass', 'scss', 'tailwind', 'bootstrap', 'jquery',
            'webpack', 'vite', 'babel',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis',
            'elasticsearch', 'cassandra', 'dynamodb', 'sqlite', 'oracle', 'nosql',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
            'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
            'terraform', 'ansible', 'ci/cd', 'cicd', 'github actions', 'gitlab ci',
            'ec2', 's3', 'lambda', 'rds', 'cloudformation',
            
            # APIs & Architecture
            'rest', 'rest api', 'rest apis', 'restful', 'api', 'graphql',
            'microservices', 'soap', 'grpc', 'websocket',
            
            # Data Science & ML
            'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn',
            'scikit-learn', 'sklearn', 'tensorflow', 'pytorch', 'keras',
            'machine learning', 'deep learning', 'nlp', 'natural language processing',
            'opencv', 'xgboost', 'lightgbm', 'data analysis', 'data processing',
            'statistics', 'statistical analysis',
            
            # Big Data
            'spark', 'hadoop', 'hive', 'kafka', 'airflow', 'databricks',
            'data pipelines', 'etl', 'data warehouse',
            
            # BI & Visualization
            'power bi', 'powerbi', 'tableau', 'excel', 'looker', 'metabase',
            
            # Authentication & Security
            'jwt', 'oauth', 'oauth2', 'authentication', 'authorization',
            'role-based access control', 'rbac', 'security',
            
            # Tools
            'linux', 'unix', 'bash', 'shell', 'powershell',
            'postman', 'swagger', 'openapi', 'insomnia',
            'jira', 'confluence', 'trello', 'asana',
            
            # Messaging & Queues
            'rabbitmq', 'celery', 'redis queue', 'sqs', 'sns',
            
            # Mobile
            'android', 'ios', 'flutter', 'react native', 'xamarin',
            
            # Testing
            'testing', 'unit testing', 'junit', 'pytest', 'jest',
            'selenium', 'cypress', 'playwright', 'tdd', 'bdd',
            
            # Methodologies
            'agile', 'scrum', 'kanban', 'devops', 'sre',
            
            # Data Formats
            'json', 'xml', 'yaml', 'csv'
        ]
        
        # Education keywords
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'b.e', 'm.e',
            'bca', 'mca', 'mba', 'bsc', 'msc', 'diploma', 'degree',
            'university', 'college', 'institute', 'school'
        ]
        
        # Section headers
        self.section_patterns = {
            'experience': r'(?i)(experience|work history|employment|professional experience)',
            'education': r'(?i)(education|academic|qualification|degree)',
            'skills': r'(?i)(skills|technical skills|expertise|competencies|technologies)',
            'projects': r'(?i)(projects|personal projects|academic projects)',
            'certifications': r'(?i)(certifications?|certificates?|licenses?)'
        }
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ""
    
    def extract_text(self, file_content: bytes, file_type: str) -> str:
        """Extract text based on file type"""
        if file_type.lower() == 'pdf':
            return self.extract_text_from_pdf(file_content)
        elif file_type.lower() in ['docx', 'doc']:
            return self.extract_text_from_docx(file_content)
        elif file_type.lower() == 'txt':
            # Support plain text for testing
            return file_content.decode('utf-8')
        else:
            return ""
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # Indian phone patterns
        phone_patterns = [
            r'\+91[-.\s]?\d{10}',
            r'\b\d{10}\b',
            r'\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from ENTIRE resume text using keyword dictionary scan.
        Scans: Technical Skills section, Experience bullets, Project descriptions.
        Uses word boundary checking for short skills to avoid false positives.
        """
        # Normalize full text for matching
        text_lower = text.lower()
        
        found_skills = []
        found_skills_lower = set()  # Track lowercase versions to avoid duplicates
        
        for skill in self.tech_skills:
            skill_lower = skill.lower()
            
            # Skip if already found (handles duplicates in skill list)
            if skill_lower in found_skills_lower:
                continue
            
            # Check if skill exists in text
            # Use word boundary check for short skills to avoid false positives
            if len(skill_lower) <= 3:
                # Short skills need word boundaries (e.g., "go", "sql", "api", "r")
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, text_lower):
                    formatted_skill = self._format_skill_for_display(skill)
                    if formatted_skill not in found_skills:
                        found_skills.append(formatted_skill)
                        found_skills_lower.add(skill_lower)
            else:
                # Longer skills can use simple contains
                if skill_lower in text_lower:
                    formatted_skill = self._format_skill_for_display(skill)
                    if formatted_skill not in found_skills:
                        found_skills.append(formatted_skill)
                        found_skills_lower.add(skill_lower)
        
        return found_skills
    
    def _format_skill_for_display(self, skill: str) -> str:
        """Format skill for display with proper casing"""
        # Special cases that should have specific casing
        special_cases = {
            'aws': 'AWS', 'gcp': 'GCP', 'sql': 'SQL', 'mysql': 'MySQL',
            'postgresql': 'PostgreSQL', 'postgres': 'PostgreSQL',
            'mongodb': 'MongoDB', 'nosql': 'NoSQL', 'dynamodb': 'DynamoDB',
            'api': 'API', 'rest': 'REST', 'rest api': 'REST API', 'rest apis': 'REST APIs',
            'restful': 'RESTful', 'graphql': 'GraphQL', 'grpc': 'gRPC',
            'jwt': 'JWT', 'oauth': 'OAuth', 'oauth2': 'OAuth2', 'rbac': 'RBAC',
            'ci/cd': 'CI/CD', 'cicd': 'CI/CD',
            'html': 'HTML', 'css': 'CSS', 'scss': 'SCSS', 'sass': 'SASS',
            'json': 'JSON', 'xml': 'XML', 'yaml': 'YAML', 'csv': 'CSV',
            'ec2': 'EC2', 's3': 'S3', 'rds': 'RDS', 'sqs': 'SQS', 'sns': 'SNS',
            'k8s': 'K8s',
            'numpy': 'NumPy', 'pandas': 'Pandas', 'scipy': 'SciPy',
            'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
            'opencv': 'OpenCV', 'xgboost': 'XGBoost', 'lightgbm': 'LightGBM',
            'sklearn': 'Scikit-learn', 'scikit-learn': 'Scikit-learn',
            'fastapi': 'FastAPI', 'nodejs': 'Node.js', 'node.js': 'Node.js',
            'nextjs': 'Next.js', 'next.js': 'Next.js',
            'vuejs': 'Vue.js', 'vue.js': 'Vue.js',
            'nlp': 'NLP', 'etl': 'ETL', 'sre': 'SRE',
            'power bi': 'Power BI', 'powerbi': 'Power BI',
            'c++': 'C++', 'c#': 'C#', '.net': '.NET',
            'ios': 'iOS', 'macos': 'macOS',
            'devops': 'DevOps', 'github': 'GitHub', 'gitlab': 'GitLab',
            'bitbucket': 'Bitbucket', 'jenkins': 'Jenkins',
            'tdd': 'TDD', 'bdd': 'BDD',
            'r': 'R'
        }
        
        skill_lower = skill.lower()
        if skill_lower in special_cases:
            return special_cases[skill_lower]
        
        # Default: Title Case
        return ' '.join(word.capitalize() for word in skill.split())
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Divide text into sections based on headers"""
        sections = {}
        lines = text.split('\n')
        current_section = 'summary'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            section_found = False
            for section_name, pattern in self.section_patterns.items():
                if re.match(pattern, line):
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience entries"""
        sections = self.extract_sections(text)
        experience_text = sections.get('experience', '')
        
        if not experience_text:
            return []
        
        experiences = []
        
        # Split by lines that look like job titles (usually start with capital)
        lines = experience_text.split('\n')
        current_entry = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this looks like a job title line (has | or year range)
            is_job_line = ('|' in line or re.search(r'\d{4}\s*-\s*\d{4}', line) or 
                          re.search(r'\d{4}\s*-\s*Present', line, re.IGNORECASE))
            
            if is_job_line and current_entry:
                # Save previous entry
                if len(current_entry.strip()) > 20:
                    years = re.findall(r'\b(?:19|20)\d{2}\b', current_entry)
                    experiences.append({
                        'description': current_entry.strip(),
                        'years': list(set(years)) if years else []
                    })
                current_entry = line
            else:
                current_entry += "\n" + line if current_entry else line
        
        # Don't forget the last entry
        if current_entry and len(current_entry.strip()) > 20:
            years = re.findall(r'\b(?:19|20)\d{2}\b', current_entry)
            experiences.append({
                'description': current_entry.strip(),
                'years': list(set(years)) if years else []
            })
        
        return experiences
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education entries"""
        sections = self.extract_sections(text)
        education_text = sections.get('education', '')
        
        if not education_text:
            return []
        
        education_entries = []
        lines = education_text.split('\n')
        
        current_entry = []
        for line in lines:
            line = line.strip()
            if not line:
                if current_entry:
                    education_entries.append({
                        'description': ' '.join(current_entry),
                        'raw': '\n'.join(current_entry)
                    })
                    current_entry = []
            else:
                current_entry.append(line)
        
        if current_entry:
            education_entries.append({
                'description': ' '.join(current_entry),
                'raw': '\n'.join(current_entry)
            })
        
        return education_entries
    
    def extract_projects(self, text: str) -> List[str]:
        """Extract project descriptions"""
        sections = self.extract_sections(text)
        projects_text = sections.get('projects', '')
        
        if not projects_text:
            return []
        
        # Split by bullet points or newlines
        projects = [p.strip() for p in re.split(r'\n\s*[-•]\s*|\n\n', projects_text) if len(p.strip()) > 20]
        
        return projects
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        sections = self.extract_sections(text)
        cert_text = sections.get('certifications', '')
        
        if not cert_text:
            return []
        
        # Split by bullet points or newlines
        certs = [c.strip() for c in re.split(r'\n\s*[-•]\s*|\n', cert_text) if len(c.strip()) > 5]
        
        return certs
    
    def extract_candidate_name(self, text: str) -> Optional[str]:
        """
        Extract candidate name from resume.
        Strategy: First try spaCy NER on first 200 chars (before job title),
        then fall back to first non-empty line.
        """
        try:
            # Get first few lines (name is typically on line 1)
            lines = text.strip().split('\n')
            first_lines = []
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if line and len(line) > 2:
                    first_lines.append(line)
            
            if not first_lines:
                return None
            
            # First line is usually the name
            first_line = first_lines[0]
            
            # If spaCy is available, try to extract PERSON entity from first line only
            if self.nlp:
                doc = self.nlp(first_line)
                persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
                if persons:
                    return persons[0]
            
            # Fallback: Use first line if it looks like a name
            # (2-4 words, no special characters except spaces)
            if re.match(r'^[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3}$', first_line):
                # Looks like a name (e.g., "John Doe" or "John Michael Doe")
                return first_line
            
            # If first line has job title mixed in, try to extract just the name part
            # Names are usually before any title-like words
            name_match = re.match(r'^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})', first_line)
            if name_match:
                potential_name = name_match.group(1)
                # Make sure it's not a title
                title_words = ['senior', 'junior', 'lead', 'software', 'data', 'engineer', 'developer', 'analyst']
                if not any(word.lower() in potential_name.lower() for word in title_words):
                    return potential_name
            
            return first_line if len(first_line) < 50 else None
            
        except Exception as e:
            print(f"Error extracting name: {e}")
            return None
    
    def extract_current_job_title(self, text: str, experience_entries: List[Dict]) -> Optional[str]:
        """Extract current/most recent job title from experience"""
        # Priority 1: Extract from first experience entry (most recent job)
        if experience_entries and len(experience_entries) > 0:
            first_exp = experience_entries[0]['description']
            
            # Split by | or newline to get the job title line
            parts = re.split(r'\||\n', first_exp)
            if parts:
                job_title_line = parts[0].strip()
                
                # Remove years/dates from the title
                job_title_line = re.sub(r'\b(19|20)\d{2}\b', '', job_title_line)
                job_title_line = re.sub(r'\d{4}\s*-\s*\d{4}', '', job_title_line)
                job_title_line = re.sub(r'\d{4}\s*-\s*Present', '', job_title_line, flags=re.IGNORECASE)
                job_title_line = job_title_line.strip()
                
                # If it's reasonable length, return it
                if 5 <= len(job_title_line) <= 60:
                    return job_title_line
        
        # Priority 2: Use regex patterns as fallback
        title_patterns = [
            r'(Senior|Junior|Lead|Principal|Staff|Chief)\s+(Software|Web|Mobile|Full Stack|Backend|Frontend|Data|Machine Learning|DevOps|Cloud)\s+(Engineer|Developer|Architect|Scientist)',
            r'(Senior|Junior|Lead|Principal|Staff)\s+(Engineer|Developer|Architect|Manager|Designer|Analyst|Scientist)',
            r'(Software|Web|Data|Machine Learning|DevOps)\s+(Engineer|Developer|Architect|Scientist)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text[:1000], re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return None
    
    def calculate_total_experience(self, text: str, experience_section: str = None) -> Optional[float]:
        """
        Calculate total experience by:
        1. Extract all date ranges from EXPERIENCE SECTION ONLY (not education)
        2. Merge overlapping ranges
        3. Sum merged ranges
        
        Args:
            text: Full resume text (used as fallback)
            experience_section: Text from experience section only (preferred)
        
        Handles formats like:
        - "Jan 2021 - Present"
        - "Jun 2018 – Dec 2020"
        - "2018 - 2020"
        """
        # Use experience section if provided, otherwise try to extract it
        search_text = experience_section
        
        if not search_text:
            # Try to extract experience section from full text
            sections = self.extract_sections(text)
            search_text = sections.get('experience', '')
        
        if not search_text or len(search_text.strip()) < 20:
            # No experience section found - this is likely a fresher
            return None
        
        current_date = datetime.now()
        
        # Month name to number mapping
        month_map = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
            'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
            'may': 5, 'jun': 6, 'june': 6,
            'jul': 7, 'july': 7, 'aug': 8, 'august': 8,
            'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        # Pattern to match date ranges
        # Matches: "Jan 2021 - Present", "Jun 2018 – Dec 2020", "2018 - 2020"
        date_range_pattern = r'(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)[a-z]*\.?\s+)?(\d{4})\s*[-–—]\s*(Present|Current|Till Date|Ongoing|(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)[a-z]*\.?\s+)?(\d{4}))'
        
        ranges = []
        
        try:
            matches = re.findall(date_range_pattern, search_text, re.IGNORECASE)
            
            for match in matches:
                start_month_str = match[0] if match[0] else ''
                start_year_str = match[1]
                end_part = match[2]
                end_month_str = match[3] if len(match) > 3 and match[3] else ''
                end_year_str = match[4] if len(match) > 4 and match[4] else ''
                
                try:
                    # Parse start date
                    start_month = 1
                    if start_month_str:
                        month_key = start_month_str.lower()[:3]
                        start_month = month_map.get(month_key, 1)
                    start_year = int(start_year_str)
                    
                    # Parse end date
                    if end_part.lower() in ['present', 'current', 'till date', 'ongoing']:
                        end_month = current_date.month
                        end_year = current_date.year
                    else:
                        end_month = 12
                        if end_month_str:
                            month_key = end_month_str.lower()[:3]
                            end_month = month_map.get(month_key, 12)
                        end_year = int(end_year_str) if end_year_str else start_year
                    
                    # Convert to months since epoch for easy comparison
                    start_months = start_year * 12 + start_month
                    end_months = end_year * 12 + end_month
                    
                    # Sanity check: valid range within reasonable bounds
                    if (start_months < end_months and 
                        start_year >= 1980 and 
                        end_year <= current_date.year + 1):
                        ranges.append((start_months, end_months))
                except (ValueError, IndexError):
                    continue
            
            if not ranges:
                return None
            
            # Sort ranges by start date
            ranges.sort(key=lambda x: x[0])
            
            # Merge overlapping ranges
            merged = [ranges[0]]
            for start, end in ranges[1:]:
                last_start, last_end = merged[-1]
                if start <= last_end:  # Overlapping or adjacent
                    merged[-1] = (last_start, max(last_end, end))
                else:
                    merged.append((start, end))
            
            # Sum total months from merged ranges
            total_months = sum(end - start for start, end in merged)
            
            # Convert to years
            total_years = total_months / 12
            
            return round(total_years, 1) if total_years > 0 else None
            
        except Exception as e:
            print(f"Error calculating experience: {e}")
            return None
    
    def parse(self, file_content: bytes, file_type: str) -> Dict:
        """Main parsing function - Hybrid: Regex + spaCy"""
        
        # Extract raw text
        raw_text = self.extract_text(file_content, file_type)
        
        if not raw_text:
            return {
                'rawText': '',
                'email': None,
                'phone': None,
                'skills': [],
                'experience': [],
                'education': [],
                'projects': [],
                'certifications': [],
                'candidateName': None,
                'totalExperienceYears': None,
                'currentJobTitle': None,
                'parsing_status': 'FAILED'
            }
        
        # PHASE 1: Regex extraction (fast, reliable)
        email = self.extract_email(raw_text)
        phone = self.extract_phone(raw_text)
        skills = self.extract_skills(raw_text)
        experience = self.extract_experience(raw_text)
        education = self.extract_education(raw_text)
        projects = self.extract_projects(raw_text)
        certifications = self.extract_certifications(raw_text)
        
        # PHASE 2: spaCy extraction (intelligent, contextual)
        candidate_name = self.extract_candidate_name(raw_text)
        current_job_title = self.extract_current_job_title(raw_text, experience)
        # Calculate experience from experience section only (not education dates)
        sections = self.extract_sections(raw_text)
        experience_section_text = sections.get('experience', '')
        total_experience_years = self.calculate_total_experience(raw_text, experience_section_text)
        
        # Return combined results
        return {
            'rawText': raw_text,
            'email': email,
            'phone': phone,
            'skills': skills,
            'experience': experience,
            'education': education,
            'projects': projects,
            'certifications': certifications,
            'candidateName': candidate_name,
            'totalExperienceYears': total_experience_years,
            'currentJobTitle': current_job_title,
            'parsing_status': 'SUCCESS'
        }
