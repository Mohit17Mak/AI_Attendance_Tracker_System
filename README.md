# AI-Assisted Smart Attendance & Performance Tracker

A complete, production-ready web application for managing student attendance and performance with AI-powered insights.

## 🌟 Features

### Core Features
- ✅ **Student Management**: Add, edit, delete, and view students
- ✅ **Attendance Tracking**: Mark attendance with automatic percentage calculation
- ✅ **Performance Management**: Enter marks with auto-generated remarks
- ✅ **AI-Powered Insights**: Auto-remarks, warnings, validation, calculations

### Bonus Features
- ✅ **CSV Export**: Export complete student reports
- ✅ **Dark/Light Mode**: Theme toggle with persistence
- ✅ **Pagination**: 10 records per page
- ✅ **Search**: Search by roll number or name
- ✅ **Dashboard**: Overview statistics

### Security
- ✅ CSRF protection on all forms
- ✅ Server-side validation
- ✅ Flask-Login authentication
- ✅ Password hashing
- ✅ SQLAlchemy ORM only

## 🏗️ Tech Stack

- **Backend**: Python Flask 3.0
- **Database**: MySQL 8.0+
- **ORM**: Flask-SQLAlchemy
- **Forms**: Flask-WTF (CSRF enabled)
- **Auth**: Flask-Login
- **Frontend**: Jinja2 + HTML + CSS + JavaScript

## 📁 Project Structure

```
AI_Attendance_Tracker/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── services/
│   │   └── ai_engine.py
│   ├── routes/
│   │   ├── students.py
│   │   ├── attendance.py
│   │   ├── performance.py
│   │   └── auth.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── students_list.html
│   │   ├── attendance_view.html
│   │   ├── performance_view.html
│   │   ├── 404.html
│   │   └── 500.html
│   └── static/
│       ├── styles.css
│       └── theme.js
├── sample_data.py
├── db_setup.sql
├── requirements.txt
├── .env.example
├── README.md
└── run.py
```

## 🚀 Setup Instructions

### Step 1: Extract the ZIP File
```bash
unzip AI_Attendance_Tracker.zip
cd AI_Attendance_Tracker
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup MySQL Database
```bash
# Login to MySQL
mysql -u root -p

# Run the setup script
source db_setup.sql

# Or from command line:
mysql -u root -p < db_setup.sql
```

### Step 5: Configure Environment
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env file (use notepad, nano, vim, etc.)
# Update these values:
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=attendance_tracker
SECRET_KEY=your-secret-key-here
```

### Step 6: Generate Sample Data (Optional)
```bash
# Generate 20 sample students
python sample_data.py

# Or specify custom number:
python sample_data.py 50
```

### Step 7: Run the Application
```bash
python run.py
```

**Application URL**: http://localhost:5000

## 🔐 Default Login Credentials

```
Username: admin
Password: admin123
```

⚠️ **Important**: Change the password in production!

## 📝 Complete Testing Guide

### Test 1: System Login
1. Open browser and go to: http://localhost:5000
2. You'll be redirected to login page
3. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
4. Click "Login"
5. ✅ You should see the Dashboard

### Test 2: View Dashboard Statistics
1. After login, you're on the Dashboard
2. Observe three stat cards:
   - Total Students
   - Attendance Shortage
   - Poor Performance
3. ✅ Statistics should display correctly

### Test 3: View Students List
1. Click "Students" in navigation
2. You should see paginated list of students
3. Try the search box:
   - Search by roll number: `CS2024001`
   - Search by name: `John`
4. ✅ Search should filter results

### Test 4: Add New Student (Login Required)
1. Go to Students page
2. Click "Add Student" button
3. Fill in the form:
   - Roll No: `TEST001`
   - Name: `Test Student`
   - Semester: `5`
4. Click "Save Student"
5. ✅ Student should be added and you see success message
6. ✅ AI validation suggestions may appear

### Test 5: Edit Student (Login Required)
1. In Students list, click "Edit" button for any student
2. Change the name or semester
3. Click "Save Student"
4. ✅ Student should be updated with success message

### Test 6: View Attendance Records
1. Click "Attendance" in navigation
2. View list of all students with their attendance
3. ✅ Attendance percentages should be displayed
4. ✅ Students with <75% should show warnings

### Test 7: Mark Attendance (Login Required)
1. Go to Attendance → Mark Attendance
2. Select a student from dropdown
3. Enter:
   - Total Lectures: `50`
   - Attended Lectures: `35`
4. Click "Mark Attendance"
5. ✅ Attendance should be saved
6. ✅ Warning should appear (35/50 = 70% < 75%)
7. ✅ AI suggestion should be displayed

### Test 8: View Performance Records
1. Click "Performance" in navigation
2. View list of students with their marks
3. ✅ Average marks should be calculated
4. ✅ Performance remarks should be displayed

### Test 9: Enter Performance Marks (Login Required)
1. Go to Performance → Enter Marks
2. Select a student
3. Enter:
   - Subject: `Mathematics`
   - Marks: `85`
4. Click "Save Marks"
5. ✅ Marks should be saved
6. ✅ Remark "Good" should be auto-generated (85 >= 75)
7. Try again with marks < 50:
   - Marks: `45`
8. ✅ Remark "Needs Improvement" should appear

### Test 10: View Student Report
1. Go to Students list
2. Click the "📄" (Report) icon for any student
3. ✅ Comprehensive report should display:
   - Student details
   - Attendance with percentage and warnings
   - Performance marks and remarks
   - AI insights and recommendations

### Test 11: Export CSV
1. Go to Students page
2. Click "Export CSV" button
3. ✅ CSV file should download
4. Open in Excel/LibreOffice
5. ✅ All student data should be present

### Test 12: Theme Toggle
1. Click the 🌙 button in navigation bar
2. ✅ Theme should switch to dark mode
3. ✅ Button icon should change to ☀️
4. Click again
5. ✅ Theme should switch back to light mode
6. Refresh page
7. ✅ Theme preference should be remembered

### Test 13: Pagination
1. Go to Students page
2. If you have > 10 students:
   - ✅ "Next" button should appear
   - Click "Next"
   - ✅ Next page of students should load
   - ✅ "Previous" button should appear
3. Navigate through pages

### Test 14: Logout
1. Click "Logout" in navigation
2. ✅ You should be logged out
3. ✅ Redirected to login page
4. ✅ Success message should appear

### Test 15: Protected Routes (Security Test)
1. Logout from the system
2. Try to access: http://localhost:5000/students/add
3. ✅ Should redirect to login page
4. ✅ Warning message should appear

### Test 16: CSRF Protection (Security Test)
1. Login to system
2. Open browser developer tools (F12)
3. Go to Add Student form
4. Inspect the form element
5. ✅ You should see a hidden `csrf_token` field
6. Try submitting without CSRF token (using curl or Postman)
7. ✅ Request should be rejected

### Test 17: Data Validation
1. Try to add student with invalid data:
   - Roll No: (empty)
   - Name: `AB` (too short)
   - Semester: `10` (out of range)
2. ✅ Validation errors should appear
3. ✅ AI suggestions may appear

### Test 18: AI Features Test
1. Add a student with attendance: 40/60 (66.67%)
2. ✅ Warning: "⚠ Attendance Shortage: 66.67%"
3. ✅ Suggestion should appear
4. Add performance marks: 85
5. ✅ Remark: "Good"
6. Add performance marks: 60
7. ✅ Remark: "Average"
8. Add performance marks: 40
9. ✅ Remark: "Needs Improvement"

### Test 19: Error Pages
1. Go to non-existent URL: http://localhost:5000/nonexistent
2. ✅ 404 error page should display
3. ✅ "Go to Dashboard" button should work

### Test 20: Sample Data Generator
1. Run: `python sample_data.py 30`
2. ✅ Script should generate 30 students
3. ✅ Each student should have:
   - Attendance record
   - Performance records (1-3 subjects)
4. Login and verify data is present

## 🎯 Expected Test Results Summary

| Test | Feature | Expected Result |
|------|---------|-----------------|
| 1 | Login | ✅ Successful login with flash message |
| 2 | Dashboard | ✅ Statistics displayed correctly |
| 3 | Student List | ✅ Pagination and search work |
| 4 | Add Student | ✅ Student created with AI validation |
| 5 | Edit Student | ✅ Student updated successfully |
| 6 | View Attendance | ✅ All records displayed with warnings |
| 7 | Mark Attendance | ✅ AI warning for shortage (<75%) |
| 8 | View Performance | ✅ Average marks calculated |
| 9 | Enter Marks | ✅ AI remark auto-generated |
| 10 | Student Report | ✅ Comprehensive report with AI insights |
| 11 | CSV Export | ✅ Complete data exported |
| 12 | Theme Toggle | ✅ Dark/Light mode persists |
| 13 | Pagination | ✅ Navigation works correctly |
| 14 | Logout | ✅ Session cleared |
| 15 | Protected Routes | ✅ Redirects to login |
| 16 | CSRF Protection | ✅ Tokens present and validated |
| 17 | Validation | ✅ Errors shown, AI suggestions given |
| 18 | AI Features | ✅ All AI features working |
| 19 | Error Pages | ✅ Custom 404/500 pages |
| 20 | Sample Data | ✅ Data generated successfully |

## 🐛 Troubleshooting

### Database Connection Error
```
Solution: Check DB_PASSWORD in .env file
          Ensure MySQL is running
```

### Import Error
```
Solution: Activate virtual environment
          Run: pip install -r requirements.txt
```

### Table doesn't exist
```
Solution: Run: mysql -u root -p < db_setup.sql
```

### Sample data fails
```
Solution: Ensure database is created
          Check .env configuration
```

## 📊 AI Features Details

### 1. Performance Remark Generation
- **≥75**: Good
- **50-74**: Average
- **<50**: Needs Improvement

### 2. Attendance Warnings
- Automatic warnings when attendance <75%
- AI-generated suggestions based on shortage

### 3. Data Validation
- Roll number format checking
- Name validation
- Semester range validation
- AI suggestions for improvements

### 4. Student Insights
- Overall status assessment
- Recommendations based on performance and attendance

## 🤖 Hybrid AI Engine Architecture

`app/services/ai_engine.py` combines **Google Gemini (`google-genai` Interactions API)** for personalized natural-language student coaching recommendations with **deterministic rule-based analytics and algebraic attendance recovery projections** as an instant, zero-downtime fallback whenever `GEMINI_API_KEY` is omitted:

```python
from google import genai

client = genai.Client(api_key=Config.GEMINI_API_KEY)
interaction = client.interactions.create(
    model=Config.GEMINI_MODEL,
    system_instruction="You are an academic mentor...",
    input=student_metrics_summary,
    store=False,
)
```

## 📧 Support

For issues:
1. Check troubleshooting section
2. Review test flows
3. Verify all setup steps completed

---

**Built with ❤️ using Flask, MySQL, and AI-powered insights**
