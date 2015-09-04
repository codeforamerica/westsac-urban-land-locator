from apscheduler.schedulers.blocking import BlockingScheduler
from farmsList.imports import every_night_at_1am
from rq import Queue
from worker import conn
import logging

logging.basicConfig()
q = Queue(connection=conn)
sched = BlockingScheduler()

@sched.scheduled_job('cron', hour=18, minute=56)# hour=1)
def scheduled_job():
	q.enqueue(every_night_at_1am)

sched.start()
