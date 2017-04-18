from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from recommendation import extract_keywords
from scraper_utils import update_songs_table
from datetime import datetime


def update_after_insert(engine):
    extract_keywords(engine)
    update_songs_table(engine)


class DropmuseScheduler():
    def __init__(self, engine):
        self.engine = engine
        self.scheduler = BackgroundScheduler(timezone=utc)
        self.job = self.scheduler.add_job(update_after_insert,
                                          'interval',
                                          id='after_insert',
                                          args=(self.engine,),
                                          days=7,
                                          max_instances=1,
                                          next_run_time=None)
        self.scheduler.start()

    def schedule_update(self):
        self.scheduler.remove_job('after_insert')
        self.job = self.scheduler.add_job(update_after_insert,
                                          'interval',
                                          id='after_insert',
                                          args=(self.engine,),
                                          days=7,
                                          max_instances=1,
                                          next_run_time=datetime.utcnow())
