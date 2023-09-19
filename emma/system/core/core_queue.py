import queue
import traceback


class QueueHandler:
    def __init__(self, name, queue_name):
        self.name = name
        self.queue_name = queue_name
        self.queues = {}
        self.secure_queues = {}  # New dictionary to store secure queues
        self.coutdown = 150

    def create_queue(self, name, size=None):
        if name in self.queues:
            raise ValueError(f"Queue with name {name} already exists")
        elif size is not None:
            self.queues[name] = queue.Queue(maxsize=size)
        else:
            self.queues[name] = queue.Queue()

    def create_secure_queue(self, name, size=None):
        if name in self.secure_queues:
            raise ValueError(
                f"Secure queue with name {name} already exists")
        elif size is not None:
            self.secure_queues[name] = {}
        else:
            self.secure_queues[name] = {}

    def add_to_queue(self, name, command):
        if name not in self.queues:
            if self.coutdown >= 150:
                print(f"No queue found with name {name}")
                self.coutdown = 0
            else:
                self.coutdown += 1
            return
        if self.queues[name].maxsize == 1:
            if not self.queues[name].empty():
                _ = self.get_queue(name)
            self.queues[name].put(command)
        else:
            self.queues[name].put(command)

    def add_to_secure_queue(self, name, special_id, command):
        if name not in self.secure_queues:
            raise ValueError(f"No secure queue found with name {name}")
        if special_id in self.secure_queues[name]:
            self.secure_queues[name][special_id].put(command)
        else:
            self.secure_queues[name][special_id] = queue.Queue()
            self.secure_queues[name][special_id].put(command)

    def get_queue(self, name, out=None, default=None):
        try:
            if out is not None:
                return self.queues[name].get(timeout=out)
            else:
                return self.queues[name].get()
        except queue.Empty:
            # Handle the empty queue exception here (if needed)
            if default is not None:
                return default
        except Exception as e:
            # Print the error message for other non-empty queue-related exceptions
            traceback_str = traceback.format_exc()
            self.add_to_queue("LOGGING", (self.name, (e, traceback_str)))
            if default is not None:
                return default

    def get_queue_lenght(self, name):
        return self.queues[name].qsize()

    def get_secure_queue_item(self, name, special_id, out=None):
        if name not in self.secure_queues or special_id not in self.secure_queues[name]:
            return None
        if out is not None:
            try:
                return self.secure_queues[name][special_id].get(timeout=out)
            except Exception as e:
                traceback_str = traceback.format_exc()
                self.add_to_queue("LOGGING", (self.name, (e, traceback_str)))
                return None
        else:
            try:
                return self.secure_queues[name][special_id].get()
            except Exception as e:
                traceback_str = traceback.format_exc()
                self.add_to_queue("LOGGING", (self.name, (e, traceback_str)))
                return None

    def queue_exists(self, name):
        """
        Check if a regular queue with the given name exists.
        :param name: The name of the regular queue.
        :return: True if the queue exists, False otherwise.
        """
        return name in self.queues

    def remove_queue(self, name):
        if name not in self.queues:
            raise ValueError(f"No queue found with name {name}")
        del self.queues[name]

    def remove_secure_queue(self, name):
        if name not in self.secure_queues:
            raise ValueError(f"No secure queue found with name {name}")
        del self.secure_queues[name]

    def remove_secure_queue_item(self, name, special_id):
        if name not in self.secure_queues or special_id not in self.secure_queues[name]:
            raise ValueError(
                f"No secure queue item found with name {name} and special_id {special_id}")
        del self.secure_queues[name][special_id]
