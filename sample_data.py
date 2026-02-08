"""
Sample Data Generator
This script generates fake student data for testing the application
"""

import sys
import os
from faker import Faker
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Student, Attendance, Performance
from app.services.ai_engine import AIEngine

fake = Faker()

def generate_sample_students(num_students=20):
    """Generate sample students with attendance and performance data"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Performance.query.delete()
        Attendance.query.delete()
        Student.query.delete()
        db.session.commit()
        
        print(f"Generating {num_students} sample students...")
        
        for i in range(num_students):
            # Generate student
            roll_no = f"CS2024{str(i+1).zfill(3)}"
            name = fake.name()
            semester = random.randint(1, 8)
            
            student = Student(roll_no=roll_no, name=name, semester=semester)
            db.session.add(student)
            db.session.flush()
            
            # Generate attendance
            total_lectures = random.randint(30, 60)
            if random.random() < 0.3:
                attended = random.randint(int(total_lectures * 0.5), int(total_lectures * 0.7))
            else:
                attended = random.randint(int(total_lectures * 0.8), total_lectures)
            
            attendance = Attendance(student_id=student.id, total_lectures=total_lectures, attended_lectures=attended)
            db.session.add(attendance)
            
            # Generate performance
            subjects = ['Mathematics', 'Physics', 'Chemistry']
            for subject in random.sample(subjects, random.randint(1, 3)):
                marks = random.uniform(40, 100)
                remark = AIEngine.generate_performance_remark(marks)
                
                performance = Performance(student_id=student.id, subject_name=subject, marks=round(marks, 2), remark=remark)
                db.session.add(performance)
        
        db.session.commit()
        
        print(f"\n✓ Successfully created {num_students} students!")
        print("\nYou can now:")
        print("1. Run the application: python run.py")
        print("2. Login with: admin / admin123")
        print("3. View students at: http://localhost:5000/students")

if __name__ == '__main__':
    num = 20
    if len(sys.argv) > 1:
        try:
            num = int(sys.argv[1])
        except ValueError:
            print("Usage: python sample_data.py [number_of_students]")
            sys.exit(1)
    
    generate_sample_students(num)
