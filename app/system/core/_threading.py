from app.config.config import Config


class ThreadHandler:
    def __init__(self, name, queue_name):
        """
        Initialize the ThreadHandler instance.

        Args:
            name (str): The name of the thread handler.
            queue_name (str): The name of the queue.
        """
        self.name = name
        self.queue_name = queue_name
        self.threads = {}

    def add_thread(self, thread):
        """
        Add a thread to the thread handler.

        Args:
            thread (Thread): The thread instance to be added.
        """
        thread_id = id(thread)
        self.threads[thread_id] = thread

    def start_thread(self, thread_name):
        """
        Start a thread by its name.

        Args:
            thread_name (str): The name of the thread to start.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if not thread.is_alive():
                    thread.start()
                    return True, f"{thread_name} has been started."
                else:
                    return True, f"{thread_name} is currently active."
        return True, f"{thread_name} not found."

    def get_thread_status(self):
        """
        Get the status of all threads.

        Returns:
            tuple: A tuple containing a boolean indicating success and a list of thread statuses.
        """
        status_list = []
        for _, thread in self.threads.items():
            status = thread.is_alive()
            status_list.append((thread, status))
        return True, status_list

    def get_thread_info(self, thread_name):
        """
        Get information about a specific thread.

        Args:
            thread_name (str): The name of the thread to get information about.

        Returns:
            dict: A dictionary containing thread information.
        """
        thread_info = {}
        for _, thread in self.threads.items():
            if thread.name == thread_name:
                thread_info = {
                    "name": thread.name,
                    "is_alive": thread.is_alive(),
                    "is_daemon": thread.daemon,
                    "thread_id": id(thread),
                }
        return thread_info

    def restart_thread(self, thread_name):
        """
        Restart a thread by its name.

        Args:
            thread_name (str): The name of the thread to restart.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    self.stop_thread(thread_name)
                    Config.app.system.agents._sys.module_reloader(
                        thread_name, True)
                    self.start_thread(thread_name)
                    return True, f"{thread_name} has been restarted."
                else:
                    return True, f"Thread '{thread_name}' is not running"
        return True, f"Thread '{thread_name}' not found"

    def stop_thread(self, thread_name):
        """
        Stop a thread by its name.

        Args:
            thread_name (str): The name of the thread to stop.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    thread_instance = Config.app.thread_instances.get(
                        thread_name)
                    thread_instance.stop()
                    return True, f"\n{thread_name} has been stopped."
                else:
                    return True, f"\n{thread_name} not found."
        return True, f"\nThread '{thread_name}' not found."

    def remove_thread(self, thread_name):
        """
        Remove a thread by its name.

        Args:
            thread_name (str): The name of the thread to remove.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    self.stop_thread(thread_name)
                    del Config.app.thread_instances[thread_name]
                    return True, f"\n{thread_name} has been removed."
                else:
                    del Config.app.thread_instances[thread_name]
                    return True, f"\n{thread_name} has been removed."
        return True, f"\nThread '{thread_name}' not found."

    def kill_thread(self):
        """
        Kill all threads.

        Returns:
            str: A message indicating the threads that have been killed.
        """
        threads = Config.app.thread_instances
        for thread_name in threads:
            for _, thread in self.threads.items():
                if str(thread.name) == thread_name:
                    if thread.is_alive():
                        thread_instance = Config.app.thread_instances.get(
                            thread_name)
                        thread_instance.stop()
                        Config.app.thread_instances.pop(thread_name)
                        return f"\n{thread_name} has been killed."
                else:
                    return f"\n{thread_name} is unknown."
        return True, f"\nThread '{thread_name}' not found."
