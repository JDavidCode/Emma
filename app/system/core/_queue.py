import queue
import traceback

class QueueHandler:
    def __init__(self, name, queue_name):
        """
        Initialize the QueueHandler instance.

        Args:
            name (str): The name of the queue handler.
            queue_name (str): The name of the queue.
        """
        self.name = name
        self.queue_name = queue_name
        self.queues = {}
        self.secure_queues = {}
        self.coutdown = 150

    def create_queue(self, name, size=None):
        """
        Create a new queue.

        Args:
            name (str): The name of the queue.
            size (int, optional): The maximum size of the queue. Defaults to None.
        """
        if name in self.queues:
            raise ValueError(f"Queue with name {name} already exists")
        self.queues[name] = queue.Queue(maxsize=size)

    def create_secure_queue(self, name, size=None):
        """
        Create a new secure queue.

        Args:
            name (str): The name of the secure queue.
            size (int, optional): The maximum size of the secure queue. Defaults to None.
        """
        if name in self.secure_queues:
            raise ValueError(f"Secure queue with name {name} already exists")
        self.secure_queues[name] = {}

    def add_to_queue(self, name, command):
        """
        Add a command to a queue.

        Args:
            name (str): The name of the queue.
            command (any): The command to be added to the queue.
        """
        if name not in self.queues:
            if self.coutdown >= 150:
                print(f"No queue found with name {name}")
                self.coutdown = 0
            else:
                self.coutdown += 1
            return
        if self.queues[name].maxsize == 1 and not self.queues[name].empty():
            _ = self.get_queue(name)
        self.queues[name].put(command)

    def add_to_secure_queue(self, name, special_id, command):
        """
        Add a command to a secure queue.

        Args:
            name (str): The name of the secure queue.
            special_id (str): An identifier for the secure queue.
            command (any): The command to be added to the secure queue.
        """
        if name not in self.secure_queues:
            raise ValueError(f"No secure queue found with name {name}")
        if special_id not in self.secure_queues[name]:
            self.secure_queues[name][special_id] = queue.Queue()
        self.secure_queues[name][special_id].put(command)

    def get_queue(self, name, timeout=None, default=None):
        """
        Get a command from a queue.

        Args:
            name (str): The name of the queue.
            out (float, optional): The maximum time to wait for an item in the queue (in seconds).
            default (any, optional): The default value to return if the queue is empty. Defaults to None.

        Returns:
            any: The command from the queue or the default value.
        """
        try:
            if timeout is not None:
                return self.queues[name].get(timeout=timeout)
            return self.queues[name].get()
        except queue.Empty:
            if default is not None:
                return default
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.add_to_queue("LOGGING", (self.name, (e, traceback_str)))
            if default is not None:
                return default

    def get_queue_length(self, name):
        """
        Get the length of a queue.

        Args:
            name (str): The name of the queue.

        Returns:
            int: The length of the queue.
        """
        return self.queues[name].qsize()

    def get_secure_queue_item(self, name, special_id, out=None):
        """
        Get a command from a secure queue.

        Args:
            name (str): The name of the secure queue.
            special_id (str): An identifier for the secure queue.
            out (float, optional): The maximum time to wait for an item in the queue (in seconds).

        Returns:
            any: The command from the secure queue or None.
        """
        if name not in self.secure_queues or special_id not in self.secure_queues[name]:
            return None
        try:
            if out is not None:
                return self.secure_queues[name][special_id].get(timeout=out)
            return self.secure_queues[name][special_id].get()
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.add_to_queue("LOGGING", (self.name, (e, traceback_str)))
            return None

    def queue_exists(self, name):
        """
        Check if a regular queue with the given name exists.

        Args:
            name (str): The name of the regular queue.

        Returns:
            bool: True if the queue exists, False otherwise.
        """
        return name in self.queues

    def remove_queue(self, name):
        """
        Remove a queue by name.

        Args:
            name (str): The name of the queue to remove.
        """
        if name not in self.queues:
            raise ValueError(f"No queue found with name {name}")
        del self.queues[name]

    def remove_secure_queue(self, name):
        """
        Remove a secure queue by name.

        Args:
            name (str): The name of the secure queue to remove.
        """
        if name not in self.secure_queues:
            raise ValueError(f"No secure queue found with name {name}")
        del self.secure_queues[name]

    def remove_secure_queue_item(self, name, special_id):
        """
        Remove an item from a secure queue.

        Args:
            name (str): The name of the secure queue.
            special_id (str): An identifier for the secure queue item.
        """
        if name not in self.secure_queues or special_id not in self.secure_queues[name]:
            raise ValueError(f"No secure queue item found with name {name} and special_id {special_id}")
        del self.secure_queues[name][special_id]
