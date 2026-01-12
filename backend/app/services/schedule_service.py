"""Schedule service for calculating next run times."""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class ScheduleService:
    """Service for calculating scheduled report run times."""

    @staticmethod
    def calculate_next_run(
        schedule_config: Dict[str, Any],
        from_time: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate the next run time based on schedule configuration.

        Args:
            schedule_config: Schedule configuration dict with:
                - type: 'daily' | 'weekly' | 'monthly'
                - time: 'HH:MM' (24-hour format)
                - day_of_week: 0-6 (for weekly, 0=Monday)
                - day_of_month: 1-31 (for monthly)
            from_time: Calculate from this time (default: now)

        Returns:
            Next scheduled run time as datetime

        Raises:
            ValueError: If schedule_config is invalid
        """
        if from_time is None:
            from_time = datetime.utcnow()

        schedule_type = schedule_config.get('type')
        time_str = schedule_config.get('time', '00:00')

        # Parse time
        try:
            hour, minute = map(int, time_str.split(':'))
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid time format: {time_str}. Expected 'HH:MM'")

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Invalid time: {time_str}. Hour must be 0-23, minute 0-59")

        if schedule_type == 'daily':
            return ScheduleService._calculate_daily(from_time, hour, minute)
        elif schedule_type == 'weekly':
            day_of_week = schedule_config.get('day_of_week')
            if day_of_week is None or not (0 <= day_of_week <= 6):
                raise ValueError(f"Invalid day_of_week: {day_of_week}. Must be 0-6")
            return ScheduleService._calculate_weekly(from_time, hour, minute, day_of_week)
        elif schedule_type == 'monthly':
            day_of_month = schedule_config.get('day_of_month')
            if day_of_month is None or not (1 <= day_of_month <= 31):
                raise ValueError(f"Invalid day_of_month: {day_of_month}. Must be 1-31")
            return ScheduleService._calculate_monthly(from_time, hour, minute, day_of_month)
        else:
            raise ValueError(f"Invalid schedule type: {schedule_type}. Must be 'daily', 'weekly', or 'monthly'")

    @staticmethod
    def _calculate_daily(from_time: datetime, hour: int, minute: int) -> datetime:
        """Calculate next daily run time."""
        # Create target time today
        next_run = from_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If target time already passed today, schedule for tomorrow
        if next_run <= from_time:
            next_run += timedelta(days=1)

        return next_run

    @staticmethod
    def _calculate_weekly(
        from_time: datetime,
        hour: int,
        minute: int,
        day_of_week: int
    ) -> datetime:
        """
        Calculate next weekly run time.

        Args:
            from_time: Current time
            hour: Target hour (0-23)
            minute: Target minute (0-59)
            day_of_week: Target day (0=Monday, 6=Sunday)
        """
        # Current day of week (0=Monday)
        current_day = from_time.weekday()

        # Days until target day
        days_ahead = day_of_week - current_day

        # If target day is today, check if time has passed
        if days_ahead == 0:
            next_run = from_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= from_time:
                # Time passed, schedule for next week
                days_ahead = 7
        elif days_ahead < 0:
            # Target day already passed this week, schedule for next week
            days_ahead += 7

        next_run = from_time + timedelta(days=days_ahead)
        next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

        return next_run

    @staticmethod
    def _calculate_monthly(
        from_time: datetime,
        hour: int,
        minute: int,
        day_of_month: int
    ) -> datetime:
        """
        Calculate next monthly run time.

        Args:
            from_time: Current time
            hour: Target hour (0-23)
            minute: Target minute (0-59)
            day_of_month: Target day of month (1-31)
        """
        # Try this month first
        year = from_time.year
        month = from_time.month

        # Create target datetime for this month
        try:
            next_run = datetime(year, month, day_of_month, hour, minute, 0, 0)
        except ValueError:
            # Day doesn't exist in this month (e.g., Feb 30)
            # Skip to next month
            next_run = None

        # If target time in this month has passed or doesn't exist, try next month
        if next_run is None or next_run <= from_time:
            # Move to next month
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1

            # Try creating datetime for next month
            try:
                next_run = datetime(year, month, day_of_month, hour, minute, 0, 0)
            except ValueError:
                # Day doesn't exist in next month either
                # Use last day of next month instead
                if month == 12:
                    # Get last day of December
                    next_run = datetime(year, month, 31, hour, minute, 0, 0)
                else:
                    # Get last day of month by going to first day of next month - 1 day
                    first_of_next_month = datetime(year, month + 1, 1, hour, minute, 0, 0)
                    next_run = first_of_next_month - timedelta(days=1)
                    next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

        return next_run

    @staticmethod
    def should_run_now(
        next_run_at: datetime,
        tolerance_minutes: int = 5
    ) -> bool:
        """
        Check if a scheduled report should run now.

        Args:
            next_run_at: Scheduled next run time
            tolerance_minutes: Tolerance window in minutes (default: 5)

        Returns:
            True if report should run now
        """
        now = datetime.utcnow()
        return now >= next_run_at and (now - next_run_at).total_seconds() <= (tolerance_minutes * 60)

    @staticmethod
    def format_schedule_description(schedule_config: Dict[str, Any]) -> str:
        """
        Generate human-readable schedule description.

        Args:
            schedule_config: Schedule configuration dict

        Returns:
            Human-readable description (e.g., "Daily at 09:00", "Weekly on Monday at 14:30")
        """
        schedule_type = schedule_config.get('type')
        time_str = schedule_config.get('time', '00:00')

        if schedule_type == 'daily':
            return f"Daily at {time_str}"
        elif schedule_type == 'weekly':
            day_of_week = schedule_config.get('day_of_week', 0)
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_name = days[day_of_week] if 0 <= day_of_week <= 6 else 'Unknown'
            return f"Weekly on {day_name} at {time_str}"
        elif schedule_type == 'monthly':
            day_of_month = schedule_config.get('day_of_month', 1)
            return f"Monthly on day {day_of_month} at {time_str}"
        else:
            return "Unknown schedule"
