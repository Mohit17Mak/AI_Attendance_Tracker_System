"""
Application entry point
"""

from app import create_app, db
from app.models import User, Student, Attendance, Performance

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Student': Student,
        'Attendance': Attendance,
        'Performance': Performance
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
