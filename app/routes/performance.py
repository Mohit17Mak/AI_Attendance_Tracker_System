from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from app import db
from app.models import Student, Performance
from app.services.ai_engine import AIEngine

bp = Blueprint('performance', __name__, url_prefix='/performance')

class PerformanceForm(FlaskForm):
    """Form for entering/editing performance/marks"""
    student_id = SelectField('Select Student', coerce=int, validators=[DataRequired()])
    subject_name = StringField('Subject Name', validators=[DataRequired()], default='General')
    marks = DecimalField('Marks (out of 100)', validators=[
        DataRequired(message='Marks are required'),
        NumberRange(min=0, max=100, message='Marks must be between 0 and 100')
    ])
    submit = SubmitField('Save Marks')

@bp.route('/view')
def view_performance():
    """View all performance records (READ)"""
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
    
    # Prepare performance data
    performance_data = []
    for student in students.items:
        perf_records = student.performance_records.all()
        avg_marks = student.average_marks
        
        performance_data.append({
            'student': student,
            'records': perf_records,
            'average': avg_marks,
            'remark': AIEngine.generate_performance_remark(avg_marks) if perf_records else 'N/A'
        })
    
    return render_template('performance_view.html',
                         performance_data=performance_data,
                         pagination=students,
                         search=search)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_performance():
    """Add new performance record (CREATE)"""
    form = PerformanceForm()
    
    # Populate student choices
    students = Student.query.order_by(Student.roll_no).all()
    form.student_id.choices = [(s.id, f'{s.roll_no} - {s.name}') for s in students]
    
    if form.validate_on_submit():
        student_id = form.student_id.data
        student = Student.query.get_or_404(student_id)
        
        # Generate AI remark
        remark = AIEngine.generate_performance_remark(float(form.marks.data))
        
        # Create new performance record
        performance = Performance(
            student_id=student_id,
            subject_name=form.subject_name.data,
            marks=form.marks.data,
            remark=remark
        )
        
        try:
            db.session.add(performance)
            db.session.commit()
            
            flash(f'Marks added for {student.name} in {form.subject_name.data}: '
                  f'{form.marks.data}/100 - {remark}', 'success')
            
            # Provide AI suggestions based on performance
            if float(form.marks.data) < 50:
                flash('AI Suggestion: Student may benefit from additional tutoring or study support', 'info')
            elif float(form.marks.data) >= 90:
                flash('AI Suggestion: Excellent performance! Consider advanced learning opportunities', 'info')
            
            return redirect(url_for('performance.view_performance'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding marks: {str(e)}', 'danger')
    
    return render_template('performance_add.html', form=form)

@bp.route('/enter', methods=['GET', 'POST'])
@login_required
def enter_performance():
    """Enter or update performance marks (CREATE/UPDATE)"""
    form = PerformanceForm()
    
    # Populate student choices
    students = Student.query.order_by(Student.roll_no).all()
    form.student_id.choices = [(s.id, f'{s.roll_no} - {s.name}') for s in students]
    
    if form.validate_on_submit():
        student_id = form.student_id.data
        student = Student.query.get_or_404(student_id)
        
        # Generate AI remark
        remark = AIEngine.generate_performance_remark(float(form.marks.data))
        
        # Check if performance record exists for this subject
        performance = Performance.query.filter_by(
            student_id=student_id,
            subject_name=form.subject_name.data
        ).first()
        
        if performance is None:
            performance = Performance(
                student_id=student_id,
                subject_name=form.subject_name.data
            )
            db.session.add(performance)
            action = 'added'
        else:
            action = 'updated'
        
        performance.marks = form.marks.data
        performance.remark = remark
        
        try:
            db.session.commit()
            flash(f'Marks {action} for {student.name} in {form.subject_name.data}: '
                  f'{form.marks.data}/100 - {remark}', 'success')
            
            # Provide AI suggestions based on performance
            if float(form.marks.data) < 50:
                flash('AI Suggestion: Student may benefit from additional tutoring or study support', 'info')
            elif float(form.marks.data) >= 90:
                flash('AI Suggestion: Excellent performance! Consider advanced learning opportunities', 'info')
            
            return redirect(url_for('performance.view_performance'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving marks: {str(e)}', 'danger')
    
    return render_template('performance_enter.html', form=form)

@bp.route('/detail/<int:id>')
def view_performance_detail(id):
    """View single performance record detail (READ)"""
    performance = Performance.query.get_or_404(id)
    student = performance.student
    
    return render_template('performance_detail.html',
                         performance=performance,
                         student=student)

@bp.route('/student/<int:student_id>')
def view_student_performance(student_id):
    """View all performance records for a specific student (READ)"""
    student = Student.query.get_or_404(student_id)
    performances = student.performance_records.order_by(Performance.subject_name).all()
    
    avg_marks = student.average_marks
    overall_remark = AIEngine.generate_performance_remark(avg_marks) if performances else 'N/A'
    
    return render_template('student_performance.html',
                         student=student,
                         performances=performances,
                         average_marks=avg_marks,
                         overall_remark=overall_remark)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_performance(id):
    """Edit performance record (UPDATE)"""
    performance = Performance.query.get_or_404(id)
    student = performance.student
    
    form = PerformanceForm(obj=performance)
    
    # Populate student choices
    students = Student.query.order_by(Student.roll_no).all()
    form.student_id.choices = [(s.id, f'{s.roll_no} - {s.name}') for s in students]
    
    if request.method == 'GET':
        form.student_id.data = student.id
        form.subject_name.data = performance.subject_name
        form.marks.data = float(performance.marks)
    
    if form.validate_on_submit():
        # Generate AI remark
        remark = AIEngine.generate_performance_remark(float(form.marks.data))
        
        performance.subject_name = form.subject_name.data
        performance.marks = form.marks.data
        performance.remark = remark
        
        try:
            db.session.commit()
            
            flash(f'Marks updated for {student.name} in {form.subject_name.data}: '
                  f'{form.marks.data}/100 - {remark}', 'success')
            
            # Provide AI suggestions
            if float(form.marks.data) < 50:
                flash('AI Suggestion: Student may benefit from additional support', 'info')
            elif float(form.marks.data) >= 90:
                flash('AI Suggestion: Excellent! Encourage advanced topics', 'info')
            
            return redirect(url_for('performance.view_performance'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating marks: {str(e)}', 'danger')
    
    return render_template('performance_edit.html', 
                         form=form, 
                         performance=performance, 
                         student=student)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_performance(id):
    """Delete performance record (DELETE)"""
    performance = Performance.query.get_or_404(id)
    student_name = performance.student.name
    subject_name = performance.subject_name
    
    try:
        db.session.delete(performance)
        db.session.commit()
        flash(f'Performance record deleted: {student_name} - {subject_name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting performance record: {str(e)}', 'danger')
    
    return redirect(url_for('performance.view_performance'))

@bp.route('/delete-all/<int:student_id>', methods=['POST'])
@login_required
def delete_all_student_performance(student_id):
    """Delete all performance records for a student (DELETE)"""
    student = Student.query.get_or_404(student_id)
    
    try:
        count = student.performance_records.count()
        student.performance_records.delete()
        db.session.commit()
        flash(f'Deleted {count} performance record(s) for {student.name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting performance records: {str(e)}', 'danger')
    
    return redirect(url_for('performance.view_performance'))
