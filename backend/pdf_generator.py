"""
PDF Resume Generator - Creates full-page A4 resumes with 5 different formats
Uses fpdf2 library
"""
import os
from fpdf import FPDF


class ResumeGenerator(FPDF):
    def __init__(self, fmt="A"):
        super().__init__()
        self.fmt = fmt
        self.set_auto_page_break(auto=False)

    def _section_header(self, title):
        if self.fmt == "A":
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 7, title.upper(), ln=True)
            self.set_draw_color(0, 0, 0)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(2)
        elif self.fmt == "B":
            alt = {"EXPERIENCE": "Work History", "EDUCATION": "Academic Background",
                   "SKILLS": "Technical Skills", "PROJECTS": "Projects",
                   "CERTIFICATIONS": "Certifications & Training",
                   "PROFESSIONAL SUMMARY": "Profile Summary", "OBJECTIVE": "Career Objective"}
            display = alt.get(title.upper(), title.title())
            self.set_font("Helvetica", "BI", 11)
            self.cell(0, 7, display, ln=True)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(2)
        elif self.fmt == "C":
            alt = {"EXPERIENCE": "Professional Experience:", "EDUCATION": "Qualifications:",
                   "SKILLS": "Expertise:", "PROJECTS": "Key Projects:",
                   "CERTIFICATIONS": "Certifications:", "PROFESSIONAL SUMMARY": "About Me:",
                   "OBJECTIVE": "Career Objective:"}
            display = alt.get(title.upper(), title.title() + ":")
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 7, display, ln=True)
            self.ln(1)
        elif self.fmt == "D":
            self.set_font("Helvetica", "B", 10)
            self.set_fill_color(230, 230, 230)
            self.cell(0, 6, "  " + title.upper(), ln=True, fill=True)
            self.ln(2)
        elif self.fmt == "E":
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 7, title.upper(), ln=True)
            self.set_draw_color(100, 100, 100)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(2)

    def _bullet(self, text):
        self.set_font("Helvetica", "", 9)
        x = self.get_x()
        self.cell(5, 4, "-", ln=False)
        self.multi_cell(175, 4, text)
        self.ln(0.5)


def generate_resume_pdf(candidate, output_dir):
    fmt = candidate.get("format", "A")
    pdf = ResumeGenerator(fmt)
    pdf.add_page()
    margin = 10
    pdf.set_left_margin(margin)
    pdf.set_right_margin(margin)

    # === NAME ===
    pdf.set_font("Helvetica", "B", 16 if fmt != "D" else 14)
    pdf.cell(0, 8, candidate["name"], ln=True, align="C" if fmt in ("A", "E") else "L")

    # === CONTACT ===
    pdf.set_font("Helvetica", "", 9)
    contact = f"{candidate['email']}  |  {candidate['phone']}"
    if fmt in ("A", "E"):
        contact += "  |  linkedin.com/in/" + candidate["name"].lower().replace(" ", "-")
        contact += "  |  github.com/" + candidate["name"].split()[0].lower()
    pdf.cell(0, 5, contact, ln=True, align="C" if fmt in ("A", "E") else "L")
    pdf.ln(3)

    # For format D: Skills at TOP
    if fmt == "D":
        _add_skills_section(pdf, candidate)

    # === SUMMARY / OBJECTIVE ===
    header = "OBJECTIVE" if not candidate.get("exp") else "PROFESSIONAL SUMMARY"
    pdf._section_header(header)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 4, candidate.get("summary", ""))
    pdf.ln(3)

    # For format D: skip skills later
    if fmt != "D":
        _add_skills_section(pdf, candidate)

    # === EXPERIENCE ===
    if candidate.get("exp"):
        pdf._section_header("EXPERIENCE")
        for job in candidate["exp"]:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 5, f"{job['title']}  |  {job['company']}", ln=True)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 4, job["dates"], ln=True)
            pdf.ln(1)
            for bullet in job.get("bullets", []):
                pdf._bullet(bullet)
            pdf.ln(2)
    elif fmt == "E" and candidate.get("projects"):
        # Freshers: projects come before education
        _add_projects_section(pdf, candidate)

    # === PROJECTS (non-freshers or if not already added) ===
    if candidate.get("projects") and fmt != "E":
        _add_projects_section(pdf, candidate)

    # === EDUCATION ===
    pdf._section_header("EDUCATION")
    edu = candidate["edu"]
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, edu["degree"], ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 4, f"{edu['univ']}  |  {edu['year']}  |  CGPA: {edu['cgpa']}", ln=True)
    if fmt == "E":
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 4, "Relevant Coursework: Data Structures, Algorithms, Database Management, Software Engineering, Computer Networks", ln=True)
    pdf.ln(3)

    # === PROJECTS for freshers (if experience was present, projects come after education) ===
    if fmt == "E" and candidate.get("exp") and candidate.get("projects"):
        _add_projects_section(pdf, candidate)

    # === CERTIFICATIONS ===
    if candidate.get("certs"):
        pdf._section_header("CERTIFICATIONS")
        for cert in candidate["certs"]:
            pdf._bullet(cert)
        pdf.ln(2)

    # === FILL remaining space for freshers with extra content ===
    if fmt == "E" and pdf.get_y() < 250:
        pdf._section_header("EXTRA-CURRICULAR ACTIVITIES")
        extras = [
            "Active member of college Coding Club, organized 3 hackathons",
            "Participated in Smart India Hackathon 2023, reached finals",
            "Volunteer at local NGO teaching basic computer skills",
            "Won 2nd prize in inter-college technical paper presentation",
        ]
        for e in extras:
            pdf._bullet(e)

    # Save
    os.makedirs(output_dir, exist_ok=True)
    filename = candidate["name"].replace(" ", "_") + "_Resume.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath


def _add_skills_section(pdf, candidate):
    pdf._section_header("SKILLS")
    skills = candidate.get("skills", [])
    pdf.set_font("Helvetica", "", 9)
    if candidate.get("format") == "D":
        # Inline comma-separated
        pdf.multi_cell(0, 4, ", ".join(skills))
    else:
        # Categorized display
        langs = [s for s in skills if s.lower() in ("python", "java", "javascript", "typescript", "go", "r", "c++", "c#", "kotlin", "swift")]
        frameworks = [s for s in skills if s.lower() in ("react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi", "spring boot", "next.js", "redux", "rxjs", "vuex")]
        dbs = [s for s in skills if s.lower() in ("sql", "mysql", "postgresql", "mongodb", "redis", "dynamodb", "sqlite", "nosql")]
        tools_list = [s for s in skills if s not in langs + frameworks + dbs]

        if langs:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(30, 4, "Languages: ", ln=False)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 4, ", ".join(langs), ln=True)
        if frameworks:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(30, 4, "Frameworks: ", ln=False)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 4, ", ".join(frameworks), ln=True)
        if dbs:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(30, 4, "Databases: ", ln=False)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 4, ", ".join(dbs), ln=True)
        if tools_list:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(30, 4, "Tools: ", ln=False)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 4, ", ".join(tools_list), ln=True)
    pdf.ln(3)


def _add_projects_section(pdf, candidate):
    pdf._section_header("PROJECTS")
    for proj in candidate.get("projects", []):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, proj["name"], ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4, proj["desc"])
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 4, f"Tech Stack: {proj['tech']}", ln=True)
        pdf.ln(2)
