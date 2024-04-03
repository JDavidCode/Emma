import time
import traceback
from app.config.config import Config


class EventHandler:
    def __init__(self, name, queue_name, queue_handler):
        """
        Initialize the EventHandler.

        Args:
            name (str): The name of the event handler.
            queue_name (str): The name of the queue to listen for messages.
            queue_handler: The queue handler for message retrieval.
        """
        self.name = name
        self.queue_name = queue_name
        self.subscribers = []
        self.queue_handler = queue_handler
        self.shutdown_flag = []

    def subscribe(self, subscriber):
        """
        Subscribe a component to the event handler.

        Args:
            subscriber: The component to subscribe.
        """
        self.subscribers.append(subscriber)

    def subscribers_shutdown_flag(self, subscriber=None, start=False):
        """
        Handle shutdown flags for subscribers.

        Args:
            subscriber: The subscriber component.
            start (bool): Whether to start the shutdown flag for a subscriber.

        Returns:
            bool: True if all subscribers have been shut down, False otherwise.
        """
        if not start and subscriber is not None:
            self.shutdown_flag.append(subscriber)
        else:
            for subscriber_to_remove in self.shutdown_flag:
                if subscriber_to_remove in self.subscribers:
                    self.subscribers.remove(subscriber_to_remove)
            return len(self.subscribers) == 0

    def unsubscribe(self, subscriber):
        """
        Unsubscribe a component from the event handler.

        Args:
            subscriber: The component to unsubscribe.
        """
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    def notify_shutdown(self):
        """
        Notify subscribers of a shutdown event.
        """
        for subscriber in self.subscribers:
            try:
                subscriber.handle_shutdown()
                self.queue_handler.add_to_queue(
                    "CONSOLE", (self.name, f"{subscriber} HAS BEEN NOTIFIED OF SHUTDOWN"))
            except Exception as e:
                self.queue_handler.add_to_queue(
                    "CONSOLE", (self.name, f"ERROR WHEN NOTIFYING {subscriber} OF SHUTDOWN: {e}"))
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, (e, traceback_str)))
                continue
        time.sleep(3)
        self.subscribers = []

    def notify_overload(self):
        """
        Notify of an overload event.
        """
        pass

    def notify_worker_overload(self, thread_name):
        """
        Notify of a worker overload event.

        Args:
            thread_name (str): The name of the overloaded worker thread.
        """
        Config.app.system.admin.agents.sys.create_new_worker(thread_name)

    def notify_connection(self):
        """
        Notify of a connection event.
        """
        pass

    def notify_disconnection(self):
        """
        Notify of a disconnection event.
        """
        pass

    def notify_progress(self, progress_percentage):
        """
        Notify of a progress event.

        Args:
            progress_percentage (float): The percentage of progress.
        """
        pass
