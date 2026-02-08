from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from app import db
from app.models import Student, Attendance, Performance
from app.services.ai_engine import AIEngine
from app.config import Config

bp = Blueprint('students', __name__)

class StudentForm(FlaskForm):
    """Form for adding/editing students"""
    roll_no = StringField('Roll Number', validators=[
        DataRequired(message='Roll number is required'),
        Length(min=3, max=20, message='Roll number must be 3-20 characters')
    ])
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=3, max=100, message='Name must be 3-100 characters')
    ])
    semester = IntegerField('Semester', validators=[
        DataRequired(message='Semester is required'),
        NumberRange(min=1, max=8, message='Semester must be between 1 and 8')
    ])
    submit = SubmitField('Save Student')
    
    def __init__(self, original_roll_no=None, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.original_roll_no = original_roll_no
    
    def validate_roll_no(self, field):
        """Custom validator for roll number uniqueness"""
        if field.data != self.original_roll_no:
            student = Student.query.filter_by(roll_no=field.data).first()
            if student:
                raise ValidationError('Roll number already exists')

@bp.route('/dashboard')
def dashboard():
    """Dashboard with statistics"""
    total_students = Student.query.count()
    
    # Students with attendance shortage
    students_with_shortage = 0
    all_students = Student.query.all()
    for student in all_students:
        if student.attendance and student.attendance.has_shortage:
            students_with_shortage += 1
    
    # Students with poor performance
    students_poor_performance = 0
    for student in all_students:
        if student.average_marks < Config.PERFORMANCE_AVERAGE_THRESHOLD:
            students_poor_performance += 1
    
    return render_template('dashboard.html',
                         total_students=total_students,
                         students_with_shortage=students_with_shortage,
                         students_poor_performance=students_poor_performance)

@bp.route('/students')
def list_students():
    """List all students with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Student.query
    
    # Search functionality
    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            db.or_(
                Student.roll_no.like(search_filter),
                Student.name.like(search_filter)
            )
        )
    
    # Pagination
    pagination = query.order_by(Student.roll_no).paginate(
        page=page,
        per_page=Config.STUDENTS_PER_PAGE,
        error_out=False
    )
    
    students = pagination.items
    
    return render_template('students_list.html',
                         students=students,
                         pagination=pagination,
                         search=search)

@bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add new student (CREATE)"""
    form = StudentForm()
    
    if form.validate_on_submit():
        # AI-assisted validation
        validation = AIEngine.validate_student_data(
            form.roll_no.data,
            form.name.data,
            form.semester.data
        )
        
        # Show AI suggestions
        for suggestion in validation['suggestions']:
            flash(f'AI Suggestion: {suggestion}', 'info')
        
        if validation['is_valid']:
            student = Student(
                roll_no=form.roll_no.data.strip(),
                name=form.name.data.strip(),
                semester=form.semester.data
            )
            
            try:
                db.session.add(student)
                db.session.commit()
                
                # Initialize attendance record
                attendance = Attendance(student_id=student.id)
                db.session.add(attendance)
                db.session.commit()
                
                flash(f'Student {student.name} added successfully!', 'success')
                return redirect(url_for('students.list_students'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding student: {str(e)}', 'danger')
        else:
            for error in validation['errors']:
                flash(error, 'danger')
    
    return render_template('student_add.html', form=form)

@bp.route('/students/view/<int:id>')
def view_student(id):
    """View single student details (READ)"""
    student = Student.query.get_or_404(id)
    
    # Get AI-generated insights
    insights = AIEngine.generate_student_insights(student)
    
    # Get attendance warning if applicable
    attendance_warning = None
    if student.attendance:
        attendance_warning = AIEngine.generate_attendance_warning(
            student.attendance.attendance_percentage
        )
    
    return render_template('student_view.html',
                         student=student,
                         insights=insights,
                         attendance_warning=attendance_warning)

@bp.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    """Edit existing student (UPDATE)"""
    student = Student.query.get_or_404(id)
    form = StudentForm(original_roll_no=student.roll_no, obj=student)
    
    if form.validate_on_submit():
        # AI-assisted validation
        validation = AIEngine.validate_student_data(
            form.roll_no.data,
            form.name.data,
            form.semester.data
        )
        
        for suggestion in validation['suggestions']:
            flash(f'AI Suggestion: {suggestion}', 'info')
        
        if validation['is_valid']:
            student.roll_no = form.roll_no.data.strip()
            student.name = form.name.data.strip()
            student.semester = form.semester.data
            
            try:
                db.session.commit()
                flash(f'Student {student.name} updated successfully!', 'success')
                return redirect(url_for('students.list_students'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating student: {str(e)}', 'danger')
        else:
            for error in validation['errors']:
                flash(error, 'danger')
    
    return render_template('student_edit.html', form=form, student=student)

@bp.route('/students/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    """Delete student (DELETE) - Cascades to attendance and performance"""
    student = Student.query.get_or_404(id)
    
    try:
        name = student.name
        roll_no = student.roll_no
        
        # Get counts for confirmation message
        attendance_count = student.attendance_records.count()
        performance_count = student.performance_records.count()
        
        db.session.delete(student)
        db.session.commit()
        
        flash(f'Student {name} ({roll_no}) deleted successfully! '
              f'Also removed {attendance_count} attendance record(s) and '
              f'{performance_count} performance record(s).', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'danger')
    
    return redirect(url_for('students.list_students'))

@bp.route('/students/report/<int:id>')
def student_report(id):
    """Detailed student report"""
    student = Student.query.get_or_404(id)
    
    # Get AI-generated insights
    insights = AIEngine.generate_student_insights(student)
    
    # Get attendance warning if applicable
    attendance_warning = None
    if student.attendance:
        attendance_warning = AIEngine.generate_attendance_warning(
            student.attendance.attendance_percentage
        )
    
    # Calculate required attendance
    required_info = None
    if student.attendance:
        required_info = AIEngine.calculate_required_attendance(
            student.attendance.total_lectures,
            student.attendance.attended_lectures
        )
    
    return render_template('student_report.html',
                         student=student,
                         insights=insights,
                         attendance_warning=attendance_warning,
                         required_info=required_info)

@bp.route('/students/export')
def export_students():
    """Export students data to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    students = Student.query.order_by(Student.roll_no).all()
    
    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow([
        'Roll No', 'Name', 'Semester',
        'Total Lectures', 'Attended Lectures', 'Attendance %',
        'Average Marks', 'Performance Remark'
    ])
    
    # Write data
    for student in students:
        att = student.attendance
        perf = student.performance
        
        writer.writerow([
            student.roll_no,
            student.name,
            student.semester,
            att.total_lectures if att else 0,
            att.attended_lectures if att else 0,
            f'{att.attendance_percentage:.2f}' if att else '0.00',
            f'{student.average_marks:.2f}',
            perf.remark if perf else 'N/A'
        ])
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=students_report.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output
