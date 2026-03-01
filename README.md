# Student Exam Information - Excel to Word Converter

This application reads student exam information from an Excel file and generates individual Word documents for each student with their exam details.

## Features

- Reads Excel files (.xlsx, .xls) containing student exam information
- Extracts: Room number, Subject code, Subject name, First name, Last name, Exam date, PAS candidate number
- Generates a Word document with one A4 page per student
- Clean, professional layout with important information highlighted
- **No installation required** - runs directly in your web browser!

## Usage

### Option 1: Browser Application (Recommended - No Installation!)

1. Simply open `index.html` in any web browser (Chrome, Edge, Firefox, etc.)

2. Click or drag your Excel file into the upload area

3. Select which exam dates you want to export (all are checked by default)

4. Choose your sorting and display preference:
   - **Sort by First Name**: Organizes students alphabetically by first name, displays as "Fornavn Etternavn"
   - **Sort by Last Name**: Organizes students alphabetically by last name, displays as "Etternavn, Fornavn"

5. Click "Generate Word Document"

6. The Word document will be automatically downloaded as `student_exam_cards.docx`

Note: Students are always sorted first by Room Number, then by your chosen name field.

### Option 2: Python Script

1. Install Python 3.8 or higher
2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Run the script:

```bash
python main.py
```

## Required Excel Columns

Your Excel file must contain these columns (exact names):
- **Rom** (Room number)
- **Fagkode** (Subject code)
- **Fagnavn** (Subject name)
- **Fornavn** (First name)
- **Etternavn** (Last name)
- **Eksamensdato** (Exam date)
- **PAS kandidatnummer** (PAS candidate number)

## Output Format

Each student gets an A4 page with:
- Exam date (top, centered)
- Room number (large, bold)
- Student name (first and last, very prominent)
- Subject code (bold)
- Subject name
- PAS candidate number (largest text, most prominent)
