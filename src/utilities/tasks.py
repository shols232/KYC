from django.core.management import call_command

from infrastructure.celery import app


@app.task
def clean_duplicate_history() -> None:
    """
    Clean duplicate entries of a model history.

    It checks the last 65 minutes of history, and should be ran once every hour with celery beat (the extra 5 minutes
    are for redundancy).
    """
    call_command('clean_duplicate_history', '-m 65', '--auto')
