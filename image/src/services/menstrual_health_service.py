from datetime import datetime, timedelta
from models.menstrual_health import MenstrualPhase, PhaseResponse
from models.user import User, QAPair
from typing import Optional, Tuple


class MenstrualHealthService:
    @staticmethod
    def check_required_data(qa_pairs: list[QAPair]) -> Tuple[bool, Optional[str]]:
        """
        Check if required QA pairs are present and valid
        """
        if not qa_pairs:
            return False, "No menstrual health data available"

        last_period_date = None
        period_duration = None

        for qa in qa_pairs:
            if qa.question == "When was the first day of your last period?":
                last_period_date = qa.answer
            elif qa.question == "How long does your period typically last?":
                period_duration = qa.answer

        if not last_period_date:
            return False, "Last period date not provided"
        if not period_duration:
            return False, "Period duration not provided"

        return True, None

    @staticmethod
    def calculate_phase(qa_pairs: list[QAPair]) -> PhaseResponse:
        """
        Calculate the current menstrual phase based on the user's QA pairs
        """
        # Check if we have required data
        has_data, message = MenstrualHealthService.check_required_data(qa_pairs)
        if not has_data:
            return PhaseResponse(phase=None, has_data=False, message=message)

        # Find last period date from QA pairs
        last_period_date = None
        period_duration = None

        for qa in qa_pairs:
            if qa.question == "When was the first day of your last period?":
                try:
                    last_period_date = datetime.strptime(qa.answer, "%Y-%m-%d")
                except ValueError:
                    return PhaseResponse(
                        phase=None,
                        has_data=False,
                        message="Invalid date format for last period",
                    )
            elif qa.question == "How long does your period typically last?":
                period_duration = qa.answer

        # Calculate days since last period
        days_since_period = (datetime.now() - last_period_date).days

        # Approximate phase lengths
        period_length = {"3-5": 4, "5-7": 6, "7-10": 8, "10+": 10}.get(
            period_duration, 5
        )

        follicular_length = 14 - period_length
        ovulation_length = 3
        luteal_length = 11

        # Determine current phase
        if days_since_period < period_length:
            phase = MenstrualPhase.MENSTRUAL
        elif days_since_period < (period_length + follicular_length):
            phase = MenstrualPhase.FOLLICULAR
        elif days_since_period < (period_length + follicular_length + ovulation_length):
            phase = MenstrualPhase.OVULATION
        elif days_since_period < 28:
            phase = MenstrualPhase.LUTEAL
        else:
            # If more than 28 days, calculate the phase within the current cycle
            current_cycle_day = days_since_period % 28
            return MenstrualHealthService.calculate_phase(
                [
                    QAPair(
                        question="When was the first day of your last period?",
                        answer=(
                            datetime.now() - timedelta(days=current_cycle_day)
                        ).strftime("%Y-%m-%d"),
                    ),
                    QAPair(
                        question="How long does your period typically last?",
                        answer=period_duration,
                    ),
                ]
            )

        return PhaseResponse(phase=phase, has_data=True, message=None)
