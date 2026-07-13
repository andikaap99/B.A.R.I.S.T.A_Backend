import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.dss_engine import run_dss_engine

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        run_dss_engine,
        CronTrigger(day_of_week="sun", hour=23, minute=0, timezone="Asia/Jakarta"),
        id="dss_engine_weekly",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started: DSS Engine setiap Minggu 23:00 WIB")


def trigger_dss_engine():
    logger.info("Manual trigger DSS Engine")
    run_dss_engine()


def get_scheduler_status():
    jobs = scheduler.get_jobs()
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            }
            for job in jobs
        ],
    }
