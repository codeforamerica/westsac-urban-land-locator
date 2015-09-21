from apscheduler.schedulers.blocking import BlockingScheduler
from farmsList.imports import every_night_at_1am
from rq import Queue
from worker import conn
import logging

logging.basicConfig()
q = Queue(connection=conn)
sched = BlockingScheduler()

@sched.scheduled_job('cron', hour=18, minute=41) # hour=8, minute=15)  # This is UTC and translates to 1:15 AM PDT (12:15 AM PST)
def scheduled_job():
	q.enqueue(every_night_at_1am)

sched.start()
