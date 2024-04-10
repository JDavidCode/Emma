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
        self.subthreads = []

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

    def create_subthread(self, parent_thread_name, subthread):
        """
        Create and add a subthread to the specified parent thread.

        Args:
            parent_thread_name (str): The name of the parent thread.
            subthread (Thread): The subthread to be added.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        for _, parent_thread in self.threads.items():
            if str(parent_thread.name) == parent_thread_name:
                parent_thread_id = id(parent_thread)

                # Check if the parent thread ID is already in the subthreads dictionary
                if parent_thread_id in self.subthreads:
                    # Check if the subthread is already associated with the parent thread
                    if id(subthread) not in [sub['id'] for sub in self.subthreads[parent_thread_id]]:
                        self.subthreads[parent_thread_id].append(
                            {'id': id(subthread), 'name': subthread.name})
                        return True, f"Subthread '{subthread.name}' has been added to '{parent_thread.name}'."
                    else:
                        return True, f"Subthread '{subthread.name}' is already associated with '{parent_thread.name}'."
                else:
                    # If the parent thread ID is not in the dictionary, create a new list with the first subthread
                    self.subthreads[parent_thread_id] = [
                        {'id': id(subthread), 'name': subthread.name}]
                    return True, f"Subthread '{subthread.name}' has been created and added to '{parent_thread.name}'."

        return False, f"Parent thread '{parent_thread_name}' not found."

    def get_subthreads_dict(self, thread):
        """
        Get the dictionary mapping parent thread IDs to their subthreads.

        Returns:
            dict: A dictionary containing parent thread IDs as keys and lists of subthread names as values.
        """
        return self.subthreads_dict[id(thread)]

    def subthread_target(self):
        """
        The target function for the subthread.
        Implement the logic for the subthread here.
        """
        # Add your subthread logic here.
        pass

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
                    Config.app.system.admin.agents.system.sys.module_reloader(
                        thread_name, True)
                    self.start_thread(thread_name)
                    return True, f"{thread_name} has been restarted."
                else:
                    return True, f"Thread '{thread_name}' is not running"
        return True, f"Thread '{thread_name}' not found"

    def stop_thread(self, thread_name):
        """
        Stop a thread by its name and its associated child threads.

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

                    # Check if the thread has associated child threads
                    thread_id = id(thread)
                    if thread_id in self.subthreads:
                        for subthread_info in self.subthreads[thread_id]:
                            subthread_id = subthread_info['id']
                            subthread_instance = self.get_thread_instance(
                                subthread_id)
                            if subthread_instance and subthread_instance.is_alive():
                                subthread_instance.__stop()

                    # Stop the main thread
                    thread_instance.__stop()

                    return True, f"\n{thread_name} and its associated child threads have been stopped."
                else:
                    return True, f"\n{thread_name} not found."
        return True, f"\nThread '{thread_name}' not found."

    def get_thread_instance(self, thread_id):
        """
        Get the thread instance based on its ID.

        Args:
            thread_id (int): The ID of the thread.

        Returns:
            Thread: The thread instance, or None if not found.
        """
        for _, thread in self.threads.items():
            if id(thread) == thread_id:
                return thread
        return None

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
                        thread_instance.__stop()
                        Config.app.thread_instances.pop(thread_name)
                        return f"\n{thread_name} has been killed."
                else:
                    return f"\n{thread_name} is unknown."
        return True, f"\nThread '{thread_name}' not found."
