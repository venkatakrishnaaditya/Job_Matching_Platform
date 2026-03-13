"""
Skill Matching using TF-IDF + Cosine Similarity
Compares resume skills vs job skills to produce a similarity score (0-1)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Set


# ============================================================
# SKILL SYNONYMS DICTIONARY
# Maps variations/aliases to canonical skill names
# ============================================================
SKILL_SYNONYMS: Dict[str, List[str]] = {
    # Programming Languages
    "javascript": ["js", "ecmascript", "es6", "es2015", "es2016", "es2017", "es2018", "es2019", "es2020", "ecma"],
    "typescript": ["ts"],
    "python": ["py", "python3", "python2"],
    "c++": ["cpp", "cplusplus", "c plus plus"],
    "c#": ["csharp", "c sharp", "dotnet c#"],
    "golang": ["go", "go lang", "go language"],
    "ruby": ["rb"],
    "kotlin": ["kt"],
    "scala": ["sc"],
    
    # Frontend Frameworks
    "react": ["reactjs", "react.js", "react js", "reactdom"],
    "vue": ["vuejs", "vue.js", "vue js", "vue3", "vue2"],
    "angular": ["angularjs", "angular.js", "angular js", "angular2", "angular4"],
    "next.js": ["nextjs", "next js", "next"],
    "nuxt.js": ["nuxtjs", "nuxt js", "nuxt"],
    "svelte": ["sveltejs", "svelte.js"],
    
    # Backend Frameworks  
    "node.js": ["nodejs", "node js", "node", "expressjs", "express.js"],
    "express": ["expressjs", "express.js", "express js"],
    "django": ["dj", "python django"],
    "flask": ["python flask"],
    "fastapi": ["fast api", "fast-api", "python fastapi"],
    "spring": ["spring boot", "springboot", "spring framework"],
    "rails": ["ruby on rails", "ror", "ruby rails"],
    ".net": ["dotnet", "dot net", "asp.net", "aspnet"],
    
    # Databases
    "postgresql": ["postgres", "psql", "pgsql"],
    "mysql": ["my sql", "mariadb"],
    "mongodb": ["mongo", "mongo db"],
    "sql server": ["mssql", "microsoft sql", "ms sql"],
    "dynamodb": ["dynamo db", "aws dynamodb"],
    "cassandra": ["apache cassandra"],
    "elasticsearch": ["elastic search", "elastic", "es"],
    "redis": ["redis cache"],
    
    # Cloud Platforms
    "aws": ["amazon web services", "amazon aws", "amazon cloud"],
    "gcp": ["google cloud", "google cloud platform", "google cloud services"],
    "azure": ["microsoft azure", "ms azure", "azure cloud"],
    "heroku": ["heroku cloud"],
    
    # AWS Services
    "ec2": ["amazon ec2", "elastic compute cloud"],
    "s3": ["amazon s3", "simple storage service"],
    "lambda": ["aws lambda", "amazon lambda"],
    "rds": ["amazon rds", "relational database service"],
    
    # DevOps & Tools
    "kubernetes": ["k8s", "kube"],
    "docker": ["docker container", "containerization"],
    "jenkins": ["jenkins ci", "jenkins cd"],
    "terraform": ["hashicorp terraform", "tf"],
    "ansible": ["ansible automation"],
    "ci/cd": ["cicd", "ci cd", "continuous integration", "continuous deployment"],
    "github actions": ["gh actions", "github ci"],
    "gitlab ci": ["gitlab cicd", "gitlab ci/cd"],
    
    # Data Science / ML
    "machine learning": ["ml", "machine-learning"],
    "deep learning": ["dl", "deep-learning"],
    "artificial intelligence": ["ai", "a.i."],
    "natural language processing": ["nlp", "natural-language-processing"],
    "computer vision": ["cv", "image recognition"],
    "tensorflow": ["tf", "tensor flow"],
    "pytorch": ["py torch", "torch"],
    "scikit-learn": ["sklearn", "scikit learn", "sk-learn"],
    "pandas": ["pd", "python pandas"],
    "numpy": ["np", "num py", "numerical python"],
    
    # Other Technologies
    "rest api": ["restful", "restful api", "rest", "restful apis", "rest apis"],
    "graphql": ["graph ql", "gql"],
    "websocket": ["web socket", "websockets", "ws"],
    "oauth": ["oauth2", "oauth 2.0", "oauth2.0"],
    "jwt": ["json web token", "json web tokens"],
    "html": ["html5", "hypertext markup language"],
    "css": ["css3", "cascading style sheets"],
    "sass": ["scss"],
    "tailwind": ["tailwindcss", "tailwind css"],
    "bootstrap": ["bootstrap css", "twitter bootstrap"],
    
    # Testing
    "jest": ["jestjs"],
    "pytest": ["py test", "python pytest"],
    "selenium": ["selenium webdriver"],
    "cypress": ["cypress.io", "cypress testing"],
    
    # Agile/Project Management
    "agile": ["agile methodology", "agile development"],
    "scrum": ["scrum methodology", "scrum master"],
    "jira": ["atlassian jira"],
    "confluence": ["atlassian confluence"],
    
    # Version Control
    "git": ["github", "gitlab", "bitbucket", "version control"],
    
    # Business Intelligence
    "power bi": ["powerbi", "microsoft power bi"],
    "tableau": ["tableau desktop", "tableau server"],
    
    # Big Data
    "apache spark": ["spark", "pyspark"],
    "hadoop": ["apache hadoop", "hdfs"],
    "kafka": ["apache kafka"],
    "airflow": ["apache airflow"],
}


def _build_reverse_synonym_map() -> Dict[str, str]:
    """
    Build a reverse lookup: alias -> canonical form
    """
    reverse_map = {}
    for canonical, aliases in SKILL_SYNONYMS.items():
        # Map all aliases to canonical
        for alias in aliases:
            reverse_map[alias.lower().strip()] = canonical.lower()
        # Also map canonical to itself
        reverse_map[canonical.lower().strip()] = canonical.lower()
    return reverse_map


# Pre-build reverse map for O(1) lookups
REVERSE_SYNONYM_MAP = _build_reverse_synonym_map()


class SkillMatcher:
    """
    Matches skills using TF-IDF vectorization and cosine similarity
    with skill synonym support for intelligent matching
    """
    
    def __init__(self):
        # Configure TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            token_pattern=r'\b[a-zA-Z][a-zA-Z+#.]{1,}\b',  # Handles C++, C#, .NET
            max_features=500,  # Limit vocabulary size
            ngram_range=(1, 2),  # Unigrams and bigrams (e.g., "machine learning")
            stop_words='english'  # Remove common words
        )
    
    def normalize_skill(self, skill: str) -> str:
        """
        Normalize a skill to its canonical form using synonym mapping.
        
        Examples:
            "JS" -> "javascript"
            "React.js" -> "react"
            "Amazon Web Services" -> "aws"
        """
        normalized = skill.lower().strip()
        
        # Check if it's a known alias
        if normalized in REVERSE_SYNONYM_MAP:
            return REVERSE_SYNONYM_MAP[normalized]
        
        # Return as-is if not found
        return normalized
    
    def normalize_skill_set(self, skills: List[str]) -> Set[str]:
        """
        Normalize a list of skills to their canonical forms.
        Returns a set of unique canonical skill names.
        """
        return {self.normalize_skill(skill) for skill in skills}
    
    def calculate_similarity(
        self, 
        resume_skills: List[str], 
        job_required_skills: List[str], 
        job_preferred_skills: List[str] = None
    ) -> float:
        """
        MATCHING LOGIC:
        - Required skills: Pure set-based (HARD constraint)
        - Preferred skills: TF-IDF bonus (SOFT, max 20%)
        
        Formula: final = min(1.0, required_score + preferred_bonus)
        
        TF-IDF is ONLY used for preferred skills bonus.
        Required skill matching is 100% set-based - no TF-IDF penalty possible.
        
        Args:
            resume_skills: List of candidate's skills
            job_required_skills: List of required skills for job
            job_preferred_skills: List of preferred/nice-to-have skills
        
        Returns:
            float: Similarity score (0.0 to 1.0)
        """
        
        # Handle empty inputs
        if not resume_skills:
            return 0.0
        
        if not job_required_skills:
            return 0.0
        
        # Normalize all skills using synonym mapping
        resume_set = self.normalize_skill_set(resume_skills)
        required_set = self.normalize_skill_set(job_required_skills)
        
        # ====== REQUIRED SKILLS: Set-based exact match (with synonyms) ======
        matched_required = resume_set & required_set
        required_score = len(matched_required) / len(required_set)
        
        # ====== PREFERRED SKILLS: TF-IDF bonus (max 20%) ======
        preferred_bonus = 0.0
        
        if job_preferred_skills and len(job_preferred_skills) > 0:
            try:
                # Calculate TF-IDF similarity for preferred skills
                resume_text = " ".join(resume_skills)
                preferred_text = " ".join(job_preferred_skills)
                
                texts = [resume_text, preferred_text]
                self.vectorizer.fit(texts)
                vectors = self.vectorizer.transform(texts)
                
                tfidf_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
                
                # Bonus capped at 20%
                preferred_bonus = tfidf_sim * 0.2
            except Exception as e:
                print(f"Error calculating preferred bonus: {e}")
                preferred_bonus = 0.0
        
        # ====== FINAL SCORE ======
        final_score = min(1.0, required_score + preferred_bonus)
        
        return max(0.0, final_score)
    
    def get_matching_skills(
        self, 
        resume_skills: List[str], 
        job_skills: List[str]
    ) -> List[str]:
        """
        Find which skills overlap between resume and job (with synonym support)
        
        Args:
            resume_skills: Candidate's skills
            job_skills: Job's required/preferred skills
        
        Returns:
            List of matching skills (original case from resume)
        """
        # Normalize using synonyms
        resume_normalized = self.normalize_skill_set(resume_skills)
        job_normalized = self.normalize_skill_set(job_skills)
        
        # Find intersection of canonical forms
        matching_canonical = resume_normalized & job_normalized
        
        # Return original-cased skills from resume that match
        result = []
        for skill in resume_skills:
            if self.normalize_skill(skill) in matching_canonical:
                result.append(skill)
        
        return result
    
    def get_missing_skills(
        self, 
        resume_skills: List[str], 
        job_skills: List[str]
    ) -> List[str]:
        """
        Find which job skills the candidate is missing (with synonym support)
        
        Args:
            resume_skills: Candidate's skills
            job_skills: Job's required/preferred skills
        
        Returns:
            List of missing skills (original case from job)
        """
        # Normalize using synonyms
        resume_normalized = self.normalize_skill_set(resume_skills)
        job_normalized = self.normalize_skill_set(job_skills)
        
        # Find what's in job but not in resume (using canonical forms)
        missing_canonical = job_normalized - resume_normalized
        
        # Return original-cased skills from job that are missing
        result = []
        for skill in job_skills:
            if self.normalize_skill(skill) in missing_canonical:
                result.append(skill)
        
        return result
