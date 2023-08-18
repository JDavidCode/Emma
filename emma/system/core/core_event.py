import time
import traceback
import emma.globals as EMMA_GLOBALS


class EventHandler:
    def __init__(self, name, queue_name, queue_handler):
        self.name = name
        self.queue_name = queue_name
        self.subscribers = []
        self.queue_handler = queue_handler
        self.shutdown_flag = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def subscribers_shutdown_flag(self, subscriber=None, start=False):
        if not start and subscriber != None:
            self.shutdown_flag.append(subscriber)
        else:
            for subscriber_to_remove in self.shutdown_flag:
                if subscriber_to_remove in self.subscribers:
                    self.subscribers.remove(subscriber_to_remove)
                return len(self.subscribers) == 0

    def unsubscribe(self, subscriber):
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    def notify_shutdown(self):
        for subscriber in self.subscribers:
            try:
                subscriber.handle_shutdown()
                self.queue_handler.add_to_queue("CONSOLE",
                                                (self.name, f"{subscriber} HAS BEEN NOTIFY THE SHUTDOWN"))
            except Exception as e:
                self.queue_handler.add_to_queue("CONSOLE",
                                                (self.name, f"ERROR WHEN NOTIFY {subscriber} SHUTDOWN {e}"))
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, (e, traceback_str)))
                continue
        time.sleep(3)
        self.subscribers = []

    def notify_overload(self):
        pass

    def notify_worker_overload(self, thread_name):
        EMMA_GLOBALS.sys_v.create_new_worker(thread_name)

    def notify_connection(self):
        pass

    def notify_disconnection(self):
        pass

    def notify_progress(self, progress_percentage):
        pass
