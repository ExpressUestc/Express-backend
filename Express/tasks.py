from celery.task import task
from celery.utils.log import get_task_logger

from Express.sendmessage import lostAlarm

logger = get_task_logger(__name__)


@task(name="testCelery")
def testCelery():
    """this is test"""
    print 'hello world'

@task(name="sendMessage")
def sendMessage(code,city,time,rcvPhone):
    print 'message has been sent!'
    return lostAlarm(code,city,time,rcvPhone)