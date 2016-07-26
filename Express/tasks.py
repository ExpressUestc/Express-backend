from celery.task import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task(name="testCelery")
def testCelery(self,email, message):
    """sends an email when feedback form is filled successfully"""
    print 'hello world'
