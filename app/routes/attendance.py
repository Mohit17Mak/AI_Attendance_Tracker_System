from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from app import db
from app.models import Student, Attendance
from app.services.ai_engine import AIEngine

bp = Blueprint('attendance', __name__, url_prefix='/attendance')

class AttendanceForm(FlaskForm):
    """Form for marking/editing attendance"""
    student_id = SelectField('Select Student', coerce=int, validators=[DataRequired()])
    total_lectures = IntegerField('Total Lectures Conducted', validators=[
        DataRequired(message='Total lectures is required'),
        NumberRange(min=0, message='Total lectures cannot be negative')
    ])
    attended_lectures = IntegerField('Lectures Attended', validators=[
        DataRequired(message='Attended lectures is required'),
        NumberRange(min=0, message='Attended lectures cannot be negative')
    ])
    submit = SubmitField('Save Attendance')
    
    def validate_attended_lectures(self, field):
        """Validate that attended lectures don't exceed total"""
        if field.data > self.total_lectures.data:
            raise ValidationError('Attended lectures cannot exceed total lectures')

@bp.route('/view')
def view_attendance():
    """View all attendance records (READ)"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    # Base query
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
    students = query.order_by(Student.roll_no).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    # Prepare data with warnings
    attendance_data = []
    for student in students.items:
        att = student.attendance
        if att:
            warning = AIEngine.generate_attendance_warning(att.attendance_percentage)
            attendance_data.append({
                'student': student,
                'attendance': att,
                'warning': warning
            })
        else:
            attendance_data.append({
                'student': student,
                'attendance': None,
                'warning': {'has_warning': False}
            })
    
    return render_template('attendance_view.html',
                         attendance_data=attendance_data,
                         pagination=students,
                         search=search)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_attendance():
    """Add/Mark attendance for a student (CREATE)"""
    form = AttendanceForm()
    
    # Populate student choices
    students = Student.query.order_by(Student.roll_no).all()
    form.student_id.choices = [(s.id, f'{s.roll_no} - {s.name}') for s in students]
    
    if form.validate_on_submit():
        student_id = form.student_id.data
        student = Student.query.get_or_404(student_id)
        
        # Check if attendance record already exists
        existing_attendance = Attendance.query.filter_by(student_id=student_id).first()
        
        if existing_attendance:
            flash(f'Attendance record already exists for {student.name}. Use Edit to update.', 'warning')
            return redirect(url_for('attendance.edit_attendance', id=existing_attendance.id))
        
        # Create new attendance record
        attendance = Attendance(
            student_id=student_id,
            total_lectures=form.total_lectures.data,
            attended_lectures=form.attended_lectures.data
        )
        
        try:
            db.session.add(attendance)
            db.session.commit()
            
            # Generate AI warning if needed
            warning = AIEngine.generate_attendance_warning(attendance.attendance_percentage)
            
            flash(f'Attendance created for {student.name}: {attendance.attendance_percentage:.2f}%', 'success')
            
            if warning['has_warning']:
                flash(warning['message'], 'warning')
                flash(f'Suggestion: {warning["suggestion"]}', 'info')
            
            return redirect(url_for('attendance.view_attendance'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating attendance: {str(e)}', 'danger')
    
    return render_template('attendance_add.html', form=form)

@bp.route('/mark', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    """Mark or update attendance for a student (CREATE/UPDATE)"""
    form = AttendanceForm()
    
    # Populate student choices
    students = Student.query.order_by(Student.roll_no).all()
    form.student_id.choices = [(s.id, f'{s.roll_no} - {s.name}') for s in students]
    
    if form.validate_on_submit():
        student_id = form.student_id.data
        student = Student.query.get_or_404(student_id)
        
        # Get or create attendance record
        attendance = Attendance.query.filter_by(student_id=student_id).first()
        
        if attendance is None:
            attendance = Attendance(student_id=student_id)
            db.session.add(attendance)
            action = 'created'
        else:
            action = 'updated'
        
        attendance.total_lectures = form.total_lectures.data
        attendance.attended_lectures = form.attended_lectures.data
        
        try:
            db.session.commit()
            
            # Generate AI warning if needed
            warning = AIEngine.generate_attendance_warning(attendance.attendance_percentage)
            
            flash(f'Attendance {action} for {student.name}: {attendance.attendance_percentage:.2f}%', 'success')
            
            if warning['has_warning']:
                flash(warning['message'], 'warning')
                flash(f'Suggestion: {warning["suggestion"]}', 'info')
            
            return redirect(url_for('attendance.view_attendance'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error marking attendance: {str(e)}', 'danger')
    
    return render_template('attendance_mark.html', form=form)

@bp.route('/detail/<int:id>')
def view_attendance_detail(id):
    """View single attendance record detail (READ)"""
    attendance = Attendance.query.get_or_404(id)
    student = attendance.student
    
    # Get AI warning
    warning = AIEngine.generate_attendance_warning(attendance.attendance_percentage)
    
    # Calculate required attendance
    required_info = AIEngine.calculate_required_attendance(
        attendance.total_lectures,
        attendance.attended_lectures
    )
    
    return render_template('attendance_detail.html',
                         attendance=attendance,
                         student=student,
                         warning=warning,
                         required_info=required_info)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_attendance(id):
    """Edit attendance record (UPDATE)"""
    attendance = Attendance.query.get_or_404(id)
    student = attendance.student
    
    form = AttendanceForm(obj=attendance)
    
    # Populate student choices and set current student as default
    students = Student.query.order_by(Student.roll_no).all()
    form.student_id.choices = [(s.id, f'{s.roll_no} - {s.name}') for s in students]
    
    if request.method == 'GET':
        form.student_id.data = student.id
    
    if form.validate_on_submit():
        # Note: Typically we don't allow changing which student this attendance belongs to
        # But keeping the flexibility here
        
        attendance.total_lectures = form.total_lectures.data
        attendance.attended_lectures = form.attended_lectures.data
        
        try:
            db.session.commit()
            
            # Generate AI warning
            warning = AIEngine.generate_attendance_warning(attendance.attendance_percentage)
            
            flash(f'Attendance updated for {student.name}: {attendance.attendance_percentage:.2f}%', 'success')
            
            if warning['has_warning']:
                flash(warning['message'], 'warning')
                flash(f'Suggestion: {warning["suggestion"]}', 'info')
            
            return redirect(url_for('attendance.view_attendance'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating attendance: {str(e)}', 'danger')
    
    return render_template('attendance_edit.html', form=form, attendance=attendance, student=student)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_attendance(id):
    """Delete attendance record (DELETE)"""
    attendance = Attendance.query.get_or_404(id)
    student_name = attendance.student.name
    
    try:
        db.session.delete(attendance)
        db.session.commit()
        flash(f'Attendance record for {student_name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting attendance: {str(e)}', 'danger')
    
    return redirect(url_for('attendance.view_attendance'))

@bp.route('/reset/<int:id>', methods=['POST'])
@login_required
def reset_attendance(id):
    """Reset attendance record to zero (UPDATE)"""
    attendance = Attendance.query.get_or_404(id)
    student_name = attendance.student.name
    
    try:
        attendance.total_lectures = 0
        attendance.attended_lectures = 0
        db.session.commit()
        flash(f'Attendance reset to 0/0 for {student_name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting attendance: {str(e)}', 'danger')
    
    return redirect(url_for('attendance.view_attendance'))
