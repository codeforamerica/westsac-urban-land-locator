from apscheduler.schedulers.blocking import BlockingScheduler
import farmsList.imports
from rq import Queue
from worker import conn
import logging

logging.basicConfig()
q = Queue(connection=conn)
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=3)
def timed_job():
	q.enqueue(every_three_minutes)

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
	q.enqueue(every_weekday_at_5pm)

sched.start()
