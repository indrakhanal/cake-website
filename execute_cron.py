from apscheduler.schedulers.background import BackgroundScheduler
from job_scheduler import CronJobScheduler


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(CronJobScheduler, 'interval', minutes=60)
    scheduler.start()
