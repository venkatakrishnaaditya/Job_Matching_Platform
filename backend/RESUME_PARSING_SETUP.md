# Resume Parsing Setup Guide

## Installation Steps

### 1. Install Required Packages

```bash
cd backend
pip install -r requirements.txt
```

### 2. Download spaCy Language Model (Optional - for advanced NLP)

If you want to use spaCy for more advanced parsing:

```bash
python -m spacy download en_core_web_sm
```

### 3. Test the Installation

Run the backend server:

```bash
uvicorn app.main:app --reload
```

## How It Works

### PDF/DOCX Text Extraction
- Uses `PyPDF2` for PDF files
- Uses `python-docx` for Word documents
- Extracts raw text from uploaded resumes

### Information Extraction
The parser automatically extracts:

1. **Contact Information**
   - Email addresses
   - Phone numbers

2. **Skills**
   - Technical skills matching from predefined list
   - 50+ common technologies covered

3. **Experience**
   - Work history sections
   - Job descriptions with dates

4. **Education**
   - Degrees and qualifications
   - Universities and colleges

5. **Projects**
   - Personal or academic projects

6. **Certifications**
   - Professional certifications and licenses

### API Endpoints

#### Upload Resume (with parsing)
```
POST /resumes/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Response:
{
  "message": "Resume uploaded and parsed successfully",
  "parsed": {
    "skills_found": 12,
    "experience_entries": 3,
    "education_entries": 2,
    "parsing_status": "SUCCESS"
  }
}
```

#### Get Parsed Data
```
GET /resumes/parsed-data
Authorization: Bearer <token>

Response:
{
  "message": "Parsed data retrieved",
  "data": {
    "email": "user@example.com",
    "phone": "+91 9876543210",
    "skills": ["Python", "React", "MongoDB"],
    "experience": [...],
    "education": [...],
    "projects": [...],
    "certifications": [...]
  }
}
```

## Extending the Parser

### Adding More Skills

Edit `backend/app/utils/resume_parser.py`:

```python
self.tech_skills = [
    'python', 'java', 'javascript',
    # Add your skills here
    'new_skill_1', 'new_skill_2'
]
```

### Customizing Section Detection

Modify regex patterns in `section_patterns`:

```python
self.section_patterns = {
    'experience': r'(?i)(experience|work history|employment)',
    'custom_section': r'(?i)(your custom pattern)'
}
```

## Troubleshooting

### Issue: PDF extraction returns empty text
- **Solution**: Some PDFs are image-based. Consider adding OCR (pytesseract) for scanned documents

### Issue: Skills not being detected
- **Solution**: Add more keywords to `self.tech_skills` list

### Issue: Section headers not recognized
- **Solution**: Update regex patterns in `self.section_patterns`

## Next Steps

1. **AI Matching Algorithm**: Use extracted skills to match with job requirements
2. **Resume Scoring**: Calculate compatibility scores based on parsed data
3. **Advanced NLP**: Integrate spaCy for entity recognition
4. **OCR Support**: Add pytesseract for image-based PDFs
