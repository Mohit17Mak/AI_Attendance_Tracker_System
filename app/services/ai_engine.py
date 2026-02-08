"""
AI Engine Service Module

This module contains AI-assisted logic for the attendance and performance tracker.
Currently implements rule-based logic, but designed to be easily replaceable
with actual LLM integration in the future.

Future Enhancement: Replace rule-based methods with OpenAI/Anthropic API calls
"""

from app.config import Config

class AIEngine:
    """
    AI-powered analytics and recommendation engine
    
    This class is designed as a service layer that can be upgraded
    to use real AI/LLM APIs without modifying the rest of the application.
    """
    
    @staticmethod
    def generate_performance_remark(marks: float) -> str:
        """
        Generate performance remark based on marks
        
        Args:
            marks: Student's marks (0-100)
            
        Returns:
            str: Performance remark
            
        Future: Replace with LLM prompt:
            "Generate a constructive remark for a student who scored {marks}/100"
        """
        if marks >= Config.PERFORMANCE_GOOD_THRESHOLD:
            return "Good"
        elif marks >= Config.PERFORMANCE_AVERAGE_THRESHOLD:
            return "Average"
        else:
            return "Needs Improvement"
    
    @staticmethod
    def generate_attendance_warning(attendance_percentage: float) -> dict:
        """
        Generate attendance warning and suggestions
        
        Args:
            attendance_percentage: Current attendance percentage
            
        Returns:
            dict: Warning information with message and severity
            
        Future: Replace with LLM analysis for personalized suggestions
        """
        if attendance_percentage < Config.ATTENDANCE_WARNING_THRESHOLD:
            shortage = Config.ATTENDANCE_WARNING_THRESHOLD - attendance_percentage
            return {
                'has_warning': True,
                'severity': 'high' if shortage > 10 else 'medium',
                'message': f'⚠ Attendance Shortage: {attendance_percentage:.2f}%',
                'suggestion': AIEngine._get_attendance_suggestion(shortage)
            }
        return {
            'has_warning': False,
            'severity': 'none',
            'message': 'Attendance is satisfactory',
            'suggestion': 'Keep up the good work!'
        }
    
    @staticmethod
    def _get_attendance_suggestion(shortage: float) -> str:
        """
        Generate attendance improvement suggestion
        
        Future: Use LLM to generate personalized, encouraging suggestions
        """
        if shortage > 15:
            return "Critical shortage! Attend all upcoming lectures to improve."
        elif shortage > 10:
            return "Significant shortage. Try to maintain 100% attendance going forward."
        else:
            return "Minor shortage. A few more attended lectures will help."
    
    @staticmethod
    def validate_student_data(roll_no: str, name: str, semester: int) -> dict:
        """
        AI-assisted validation of student data
        
        Args:
            roll_no: Student roll number
            name: Student name
            semester: Student semester
            
        Returns:
            dict: Validation results with suggestions
            
        Future: Use LLM to detect format issues, suggest corrections
        """
        errors = []
        suggestions = []
        
        # Roll number validation
        if not roll_no or len(roll_no.strip()) == 0:
            errors.append("Roll number is required")
        elif len(roll_no) < 3:
            suggestions.append("Roll number seems short. Typical format: ABC123")
        
        # Name validation
        if not name or len(name.strip()) == 0:
            errors.append("Name is required")
        elif len(name.strip()) < 3:
            suggestions.append("Name seems very short. Please verify.")
        elif not any(char.isalpha() for char in name):
            errors.append("Name must contain alphabetic characters")
        
        # Semester validation
        if semester < 1 or semester > 8:
            errors.append("Semester must be between 1 and 8")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions
        }
    
    @staticmethod
    def calculate_required_attendance(current_total: int, current_attended: int, 
                                     target_percentage: float = 75.0) -> dict:
        """
        Calculate lectures needed to reach target attendance
        
        Args:
            current_total: Total lectures conducted so far
            current_attended: Lectures attended so far
            target_percentage: Target attendance percentage (default 75%)
            
        Returns:
            dict: Analysis with required lectures
            
        Future: Use LLM to provide motivational messaging
        """
        if current_total == 0:
            return {
                'achievable': True,
                'lectures_needed': 0,
                'message': 'No lectures conducted yet'
            }
        
        current_percentage = (current_attended * 100.0) / current_total
        
        if current_percentage >= target_percentage:
            return {
                'achievable': True,
                'lectures_needed': 0,
                'current_percentage': current_percentage,
                'message': f'Already at {current_percentage:.2f}%. Great job!'
            }
        
        # Calculate lectures needed
        # Formula: (attended + x) / (total + x) = target/100
        # Solving: x = (target * total - 100 * attended) / (100 - target)
        
        numerator = (target_percentage * current_total) - (100 * current_attended)
        denominator = 100 - target_percentage
        
        if denominator == 0:
            lectures_needed = float('inf')
            achievable = False
        else:
            lectures_needed = max(0, int(numerator / denominator) + 1)
            achievable = lectures_needed < 100  # Reasonable threshold
        
        return {
            'achievable': achievable,
            'lectures_needed': lectures_needed,
            'current_percentage': current_percentage,
            'target_percentage': target_percentage,
            'message': f'Attend next {lectures_needed} lectures continuously to reach {target_percentage}%'
        }
    
    @staticmethod
    def generate_student_insights(student) -> dict:
        """
        Generate comprehensive insights about a student
        
        Args:
            student: Student model instance
            
        Returns:
            dict: Comprehensive insights
            
        Future: Use LLM to generate natural language report
        """
        insights = {
            'attendance_status': 'Unknown',
            'performance_status': 'Unknown',
            'overall_status': 'Unknown',
            'recommendations': []
        }
        
        # Attendance insights
        if student.attendance:
            att_pct = student.attendance.attendance_percentage
            if att_pct >= 90:
                insights['attendance_status'] = 'Excellent'
            elif att_pct >= 75:
                insights['attendance_status'] = 'Good'
            elif att_pct >= 60:
                insights['attendance_status'] = 'Fair'
            else:
                insights['attendance_status'] = 'Poor'
                insights['recommendations'].append('Improve attendance immediately')
        
        # Performance insights
        avg_marks = student.average_marks
        if avg_marks >= 75:
            insights['performance_status'] = 'Excellent'
        elif avg_marks >= 50:
            insights['performance_status'] = 'Average'
            insights['recommendations'].append('Focus on improving performance')
        else:
            insights['performance_status'] = 'Needs Attention'
            insights['recommendations'].append('Requires academic support')
        
        # Overall status
        if insights['attendance_status'] in ['Excellent', 'Good'] and \
           insights['performance_status'] in ['Excellent']:
            insights['overall_status'] = 'Outstanding'
        elif insights['attendance_status'] in ['Poor'] or \
             insights['performance_status'] == 'Needs Attention':
            insights['overall_status'] = 'Requires Intervention'
        else:
            insights['overall_status'] = 'Satisfactory'
        
        return insights
