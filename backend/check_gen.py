import os
import sys
from seed_data import CANDIDATES
from seed_data2 import CANDIDATES_PART2
from pdf_generator import generate_resume_pdf

ALL_CANDIDATES = CANDIDATES + CANDIDATES_PART2
OUTPUT_DIR = "generated_resumes"

def check_gen():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    success = 0
    for i, c in enumerate(ALL_CANDIDATES, 1):
        try:
            path = generate_resume_pdf(c, OUTPUT_DIR)
            if os.path.exists(path):
                print(f"[{i:2d}/25] OK: {c['name']}")
                success += 1
            else:
                print(f"[{i:2d}/25] MISSED: {c['name']} (Path not found)")
        except Exception as e:
            print(f"[{i:2d}/25] FAIL: {c['name']} - {str(e)}")
    
    print(f"\nTotal Success: {success}/25")

if __name__ == "__main__":
    check_gen()
