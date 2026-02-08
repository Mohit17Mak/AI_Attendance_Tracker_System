from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """Admin user model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    performance_records = db.relationship('Performance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.roll_no}: {self.name}>'
    
    @property
    def attendance(self):
        """Get the student's attendance record"""
        return self.attendance_records.first()
    
    @property
    def performance(self):
        """Get the student's latest performance record"""
        return self.performance_records.order_by(Performance.created_at.desc()).first()
    
    @property
    def average_marks(self):
        """Calculate average marks across all subjects"""
        records = self.performance_records.all()
        if not records:
            return 0.0
        return sum(r.marks for r in records) / len(records)

class Attendance(db.Model):
    """Attendance model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    total_lectures = db.Column(db.Integer, default=0, nullable=False)
    attended_lectures = db.Column(db.Integer, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attendance Student:{self.student_id} {self.attendance_percentage:.2f}%>'
    
    @property
    def attendance_percentage(self):
        """Calculate attendance percentage"""
        if self.total_lectures == 0:
            return 0.0
        return (self.attended_lectures * 100.0) / self.total_lectures
    
    @property
    def has_shortage(self):
        """Check if attendance is below threshold"""
        from app.config import Config
        return self.attendance_percentage < Config.ATTENDANCE_WARNING_THRESHOLD

class Performance(db.Model):
    """Performance/Marks model"""
    __tablename__ = 'performance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    subject_name = db.Column(db.String(100), default='General', nullable=False)
    marks = db.Column(db.Numeric(5, 2), nullable=False)
    remark = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Performance Student:{self.student_id} {self.subject_name}: {self.marks}>'
    
    def __init__(self, **kwargs):
        super(Performance, self).__init__(**kwargs)
        # Auto-generate remark if not provided
        if not self.remark and self.marks is not None:
            from app.services.ai_engine import AIEngine
            self.remark = AIEngine.generate_performance_remark(float(self.marks))
