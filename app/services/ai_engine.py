"""
AI Engine Service Module

Hybrid AI-powered analytics and recommendation engine combining Google Gemini
(`google-genai` Interactions API) for personalized student coaching insights with
deterministic rule-based analytics and algebraic attendance projections as a
guaranteed, zero-downtime fallback.
"""

from app.config import Config

_gemini_client = None
_gemini_checked = False


def _get_gemini_client():
    """Lazily initialize the Google GenAI client when GEMINI_API_KEY is configured."""
    global _gemini_client, _gemini_checked
    if _gemini_checked:
        return _gemini_client

    _gemini_checked = True
    if not Config.GEMINI_API_KEY:
        return None

    try:
        from google import genai

        _gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY)
    except Exception:
        _gemini_client = None

    return _gemini_client


def _generate_gemini_advice(system_instruction: str, prompt: str) -> str | None:
    """Call Gemini Interactions API for concise academic coaching feedback."""
    client = _get_gemini_client()
    if client is None:
        return None

    try:
        interaction = client.interactions.create(
            model=Config.GEMINI_MODEL,
            system_instruction=system_instruction,
            input=prompt,
            store=False,
        )
        text = (interaction.output_text or "").strip()
        return text if text else None
    except Exception:
        return None


class AIEngine:
    """
    Hybrid AI-powered analytics and recommendation engine.

    Combines deterministic threshold classifications and exact attendance recovery
    math with Google Gemini (`gemini-4-hydrogen`) natural-language coaching
    suggestions whenever `GEMINI_API_KEY` is provided.
    """

    @staticmethod
    def generate_performance_remark(marks: float) -> str:
        """Classify subject marks (0-100) into standardized academic remarks."""
        if marks >= Config.PERFORMANCE_GOOD_THRESHOLD:
            return "Good"
        elif marks >= Config.PERFORMANCE_AVERAGE_THRESHOLD:
            return "Average"
        else:
            return "Needs Improvement"

    @staticmethod
    def generate_attendance_warning(attendance_percentage: float) -> dict:
        """Generate attendance shortage alert and actionable guidance."""
        if attendance_percentage < Config.ATTENDANCE_WARNING_THRESHOLD:
            shortage = Config.ATTENDANCE_WARNING_THRESHOLD - attendance_percentage
            return {
                'has_warning': True,
                'severity': 'high' if shortage > 10 else 'medium',
                'message': f'⚠ Attendance Shortage: {attendance_percentage:.2f}%',
                'suggestion': AIEngine._get_attendance_suggestion(shortage, attendance_percentage),
            }
        return {
            'has_warning': False,
            'severity': 'none',
            'message': 'Attendance is satisfactory',
            'suggestion': 'Keep up the good work!',
        }

    @staticmethod
    def _get_attendance_suggestion(shortage: float, attendance_percentage: float | None = None) -> str:
        """Generate personalized attendance guidance via Gemini with rule-based fallback."""
        pct_str = f"{attendance_percentage:.2f}%" if attendance_percentage is not None else f"{75.0 - shortage:.2f}%"
        llm_tip = _generate_gemini_advice(
            system_instruction=(
                "You are an academic advisor. Write ONE concise, encouraging sentence "
                "(under 22 words) advising a college student whose attendance fell below 75%."
            ),
            prompt=f"Current attendance: {pct_str} ({shortage:.2f}% below the 75% requirement).",
        )
        if llm_tip:
            return llm_tip

        if shortage > 15:
            return "Critical shortage! Attend all upcoming lectures to improve."
        elif shortage > 10:
            return "Significant shortage. Try to maintain 100% attendance going forward."
        else:
            return "Minor shortage. A few more attended lectures will help."

    @staticmethod
    def validate_student_data(roll_no: str, name: str, semester: int) -> dict:
        """Validate student enrollment fields and surface formatting suggestions."""
        errors = []
        suggestions = []

        if not roll_no or len(roll_no.strip()) == 0:
            errors.append("Roll number is required")
        elif len(roll_no) < 3:
            suggestions.append("Roll number seems short. Typical format: ABC123")

        if not name or len(name.strip()) == 0:
            errors.append("Name is required")
        elif len(name.strip()) < 3:
            suggestions.append("Name seems very short. Please verify.")
        elif not any(char.isalpha() for char in name):
            errors.append("Name must contain alphabetic characters")

        if semester < 1 or semester > 8:
            errors.append("Semester must be between 1 and 8")

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions,
        }

    @staticmethod
    def calculate_required_attendance(
        current_total: int,
        current_attended: int,
        target_percentage: float = 75.0,
    ) -> dict:
        """
        Calculate continuous lectures required to reach `target_percentage`:
        (attended + x) / (total + x) = target / 100
        """
        if current_total == 0:
            return {
                'achievable': True,
                'lectures_needed': 0,
                'message': 'No lectures conducted yet',
            }

        current_percentage = (current_attended * 100.0) / current_total

        if current_percentage >= target_percentage:
            return {
                'achievable': True,
                'lectures_needed': 0,
                'current_percentage': current_percentage,
                'message': f'Already at {current_percentage:.2f}%. Great job!',
            }

        numerator = (target_percentage * current_total) - (100 * current_attended)
        denominator = 100 - target_percentage

        if denominator == 0:
            lectures_needed = float('inf')
            achievable = False
        else:
            lectures_needed = max(0, int(numerator / denominator) + 1)
            achievable = lectures_needed < 100

        return {
            'achievable': achievable,
            'lectures_needed': lectures_needed,
            'current_percentage': current_percentage,
            'target_percentage': target_percentage,
            'message': f'Attend next {lectures_needed} lectures continuously to reach {target_percentage}%',
        }

    @staticmethod
    def generate_student_insights(student) -> dict:
        """
        Generate comprehensive academic insights combining deterministic risk
        classification with Gemini-generated coaching recommendations when configured.
        """
        insights = {
            'attendance_status': 'Unknown',
            'performance_status': 'Unknown',
            'overall_status': 'Unknown',
            'recommendations': [],
        }

        att_pct = None
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

        avg_marks = student.average_marks
        if avg_marks >= 75:
            insights['performance_status'] = 'Excellent'
        elif avg_marks >= 50:
            insights['performance_status'] = 'Average'
            insights['recommendations'].append('Focus on improving performance')
        else:
            insights['performance_status'] = 'Needs Attention'
            insights['recommendations'].append('Requires academic support')

        if insights['attendance_status'] in ['Excellent', 'Good'] and insights['performance_status'] == 'Excellent':
            insights['overall_status'] = 'Outstanding'
        elif insights['attendance_status'] == 'Poor' or insights['performance_status'] == 'Needs Attention':
            insights['overall_status'] = 'Requires Intervention'
        else:
            insights['overall_status'] = 'Satisfactory'

        llm_recommendation = _generate_gemini_advice(
            system_instruction=(
                "You are an academic mentor. Provide ONE actionable, specific study & attendance "
                "recommendation in 1-2 sentences based on the student's metrics."
            ),
            prompt=(
                f"Student: {getattr(student, 'name', 'Student')}, Semester {getattr(student, 'semester', 'N/A')}. "
                f"Attendance: {f'{att_pct:.2f}%' if att_pct is not None else 'N/A'} ({insights['attendance_status']}). "
                f"Average Marks: {avg_marks:.2f}% ({insights['performance_status']}). "
                f"Overall Status: {insights['overall_status']}."
            ),
        )
        if llm_recommendation:
            insights['recommendations'].insert(0, llm_recommendation)

        return insights
