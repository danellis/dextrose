from __future__ import absolute_import
from postmark import PMMail
from celery.task import task

@task(ignore_result=True)
def send_mail_task(api_key, sender, recipients, subject, body):
    mail = PMMail(
        api_key=api_key,
        to=recipients,
        subject=subject,
        text_body=body,
        sender=sender
    )
    mail.send()
