
import time
import threading
import schedule
from datetime import datetime
from utils.logger import Logger

class ScheduledTaskManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScheduledTaskManager, cls).__new__(cls)
            cls._instance.logger = Logger().get_logger()
            cls._instance.running = False
            cls._instance.thread = None
        return cls._instance
    
    def start(self):
        """
        Start the scheduled task manager in a separate thread
        """
        if self.running:
            self.logger.warning("Scheduled task manager is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_continuously)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("Scheduled task manager started")
    
    def stop(self):
        """
        Stop the scheduled task manager
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None
        self.logger.info("Scheduled task manager stopped")
    
    def _run_continuously(self):
        """
        Run the scheduled tasks continuously
        """
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def schedule_daily_task(self, task_func, hour=0, minute=0):
        """
        Schedule a task to run daily at the specified time
        """
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self._wrap_task, task_func)
        self.logger.info(f"Scheduled daily task {task_func.__name__} at {hour:02d}:{minute:02d}")
    
    def schedule_hourly_task(self, task_func, minute=0):
        """
        Schedule a task to run hourly at the specified minute
        """
        schedule.every().hour.at(f":{minute:02d}").do(self._wrap_task, task_func)
        self.logger.info(f"Scheduled hourly task {task_func.__name__} at minute {minute}")
    
    def schedule_interval_task(self, task_func, interval_hours=1):
        """
        Schedule a task to run at regular intervals
        """
        schedule.every(interval_hours).hours.do(self._wrap_task, task_func)
        self.logger.info(f"Scheduled task {task_func.__name__} to run every {interval_hours} hours")
    
    def _wrap_task(self, task_func):
        """
        Wrap a task with error handling and logging
        """
        start_time = time.time()
        self.logger.info(f"Starting task {task_func.__name__}")
        try:
            result = task_func()
            execution_time = time.time() - start_time
            self.logger.info(f"Task {task_func.__name__} completed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Task {task_func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
            # Here you could implement retry logic or alerts
            return None
