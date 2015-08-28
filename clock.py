from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
import logging

logging.basicConfig()
q = Queue(connection=conn)
sched = BlockingScheduler()

def every_three_minutes():
	print('This job is run every three minutes.')

def every_weekday_at_5pm():
    print('This job is run every weekday at 5pm.')

@sched.scheduled_job('interval', minutes=3)
def timed_job():
	q.enqueue(every_three_minutes)

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
	q.enqueue(every_weekday_at_5pm)

sched.start()
