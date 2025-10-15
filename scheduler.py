"""Scheduler for automated daily digest generation"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DigestScheduler:
    """Schedules automatic digest generation"""

    def __init__(self, digest_function, hour=8, minute=0):
        """
        Initialize the scheduler

        Args:
            digest_function: Function to call for generating the digest
            hour: Hour of day to run (0-23), default 8 AM
            minute: Minute of hour to run (0-59), default 0
        """
        self.scheduler = BackgroundScheduler()
        self.digest_function = digest_function
        self.hour = hour
        self.minute = minute

    def start(self):
        """Start the scheduler"""
        # Schedule daily digest generation
        trigger = CronTrigger(hour=self.hour, minute=self.minute)
        self.scheduler.add_job(
            self._run_digest,
            trigger,
            id='daily_digest',
            name='Daily Threat Intelligence Digest',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info(f"Scheduler started. Daily digest will run at {self.hour:02d}:{self.minute:02d}")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def _run_digest(self):
        """Internal method to run the digest generation"""
        logger.info("Starting scheduled digest generation...")
        try:
            result = self.digest_function()
            logger.info(f"Digest generation completed at {datetime.now()}")
            return result
        except Exception as e:
            logger.error(f"Error during scheduled digest generation: {str(e)}")

    def run_now(self):
        """Manually trigger a digest generation immediately"""
        logger.info("Manual digest generation triggered")
        return self._run_digest()

    def get_next_run_time(self):
        """Get the next scheduled run time"""
        job = self.scheduler.get_job('daily_digest')
        if job:
            return job.next_run_time
        return None
