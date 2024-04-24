from telethon import TelegramClient, events
from inn_parser import GoogleParser
from schedule import repeat, every, run_pending
import schedule
import time
from wrapper import GigachatWrapper
import telegram 
import threading
from threading import Thread
import multiprocessing
import queue
import asyncio
api_id = id
api_hash = 'hash'

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run



channels = [
    -1001440547668,
    -1001868607332,
    -1001102973147,
    -1001223136500,
    -1002053630479]

token = 'bot_token'

def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()


class TelegramCrawler:
    def __init__(self):
        self.gw = GigachatWrapper()
        self.api_id = 27661056
        self.api_hash = '05d76b5fcac4ddddfb991156ce033e1a'
        self.client = TelegramClient('telegram_crawler', api_id, api_hash)
        self.messages = list()
        self.bot = telegram.Bot(token=token)

        @self.client.on(events.NewMessage(chats=channels))
        async def my_event_handler(event):
            self.messages.append(event.text)
            print(event.text)

    async def process_data(self):
        for message in self.messages:
            company = self.gw.condense(message)
            if company == 'Нет':
                continue
            inn = GoogleParser.third_function(company)
            msg=f"whrote message {inn}, {company}, {message}"
            print(f"msg: {msg}")
            await self.bot.sendMessage(chat_id=-1002053630479, text=msg)

    def start(self):
        self.client.start()
        self.client.run_until_disconnected()
        
        


if __name__ == '__main__':
    tc = TelegramCrawler()
    schedule.every().second.do(tc.process_data)
    stop_run_continuously = run_continuously()
    tc.start()

