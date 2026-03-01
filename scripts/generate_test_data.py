"""
Generate sample Excel file with student exam data for testing
"""
import random
from openpyxl import Workbook
from datetime import datetime, timedelta

# Sample data
first_names = [
    'Emma', 'Noah', 'Olivia', 'Liam', 'Sophia', 'Lucas', 'Ava', 'Oliver',
    'Isabella', 'Elias', 'Mia', 'William', 'Ella', 'Jakob', 'Emily',
    'Alexander', 'Sofia', 'Filip', 'Charlotte', 'Henrik', 'Amelia', 'Oskar',
    'Harper', 'Viktor', 'Evelyn', 'Magnus', 'Nora', 'Sebastian', 'Ingrid', 'Jonas',
    'Leah', 'Mathias', 'Eline', 'Kristian', 'Sara', 'Andreas', 'Julie',
    'Martin', 'Maria', 'Benjamin', 'Anna', 'Lars', 'Kaja', 'Erik', 'Sofie',
    'Thomas', 'Emilie', 'Markus', 'Linnea', 'Fredrik'
]

last_names = [
    'Hansen', 'Johansen', 'Olsen', 'Larsen', 'Andersen', 'Pedersen', 'Nilsen',
    'Kristiansen', 'Jensen', 'Karlsen', 'Johnsen', 'Pettersen', 'Eriksen',
    'Berg', 'Haugen', 'Hagen', 'Johannessen', 'Andreassen', 'Jacobsen', 'Dahl',
    'Jørgensen', 'Halvorsen', 'Henriksen', 'Lund', 'Sørensen', 'Bakke', 'Strand',
    'Solberg', 'Moen', 'Eliassen', 'Nguyen', 'Jacobsen', 'Holm', 'Kristoffersen',
    'Iversen', 'Berge', 'Knutsen', 'Martinsen', 'Rasmussen', 'Gundersen'
]

rooms = ['101', '102', '103', '104', '105', '201', '202', '203', '204', '205', 
         '301', '302', '303', 'Gymsal', 'Aula']

# Exam subjects - mix of two-part and one-part exams
subjects = [
    {'fagkode': 'MAT1021', 'fagnavn': 'Matematikk R1'},  # Two-part
    {'fagkode': 'REA3036', 'fagnavn': 'Realfaglig matematikk'},  # Two-part
    {'fagkode': 'NOR1267', 'fagnavn': 'Norsk hovedmål'},  # One-part
    {'fagkode': 'SAM3046', 'fagnavn': 'Samfunnsfag'},  # One-part
    {'fagkode': 'FSP6152', 'fagnavn': 'Fransk nivå II'}  # One-part
]

# Generate 3 exam dates (March 15, 17, 20, 2026)
exam_dates = [
    datetime(2026, 3, 15),
    datetime(2026, 3, 17),
    datetime(2026, 3, 20)
]

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Eksamensliste"

# Add headers
headers = ['Rom', 'Fagkode', 'Fagnavn', 'Fornavn', 'Etternavn', 'Eksamensdato', 'PAS kandidatnummer']
ws.append(headers)

# Generate ~100 students (20 per subject)
kandidat_number = 10000000
students_per_subject = 20

for subject in subjects:
    for i in range(students_per_subject):
        # Randomly select name components
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        room = random.choice(rooms)
        
        # Distribute across 3 dates
        exam_date = exam_dates[i % 3]
        date_str = exam_date.strftime('%d.%m.%Y')
        
        # Create row
        row = [
            room,
            subject['fagkode'],
            subject['fagnavn'],
            first_name,
            last_name,
            date_str,
            kandidat_number
        ]
        
        ws.append(row)
        kandidat_number += 1

# Save file
filename = 'test_exam_data.xlsx'
wb.save(filename)
print(f"✓ Generated {filename} with {len(subjects) * students_per_subject} student records")
print(f"  - {len(subjects)} subjects: {', '.join([s['fagkode'] for s in subjects])}")
print(f"  - {len(exam_dates)} exam dates")
print(f"  - Mix of two-part exams (MAT1021, REA3036) and one-part exams")
