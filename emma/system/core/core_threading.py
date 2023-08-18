import queue
import emma.globals as EMMA_GLOBALS
import time
import traceback


class ThreadHandler:
    def __init__(self, name, queue_name):
        self.name = name
        self.queue_name = queue_name
        self.threads = {}

    def add_thread(self, thread):
        thread_id = id(thread)
        self.threads[thread_id] = thread

    def start_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if not thread.is_alive():
                    thread.start()
                    return True, f"{thread_name} has been started."
                else:
                    return True, f"{thread_name} is current active."
        return True, f"{thread_name} not found."

    def get_thread_status(self):
        status_list = []
        for _, thread in self.threads.items():
            status = thread.is_alive()
            status_list.append((thread, status))
        return True, status_list

    def get_thread_info(self, thread_name):
        thread_info= {}
        for _, thread in self.threads.items():
            if thread.name == thread_name:  # Check if the current thread matches the provided name
                thread_info = {
                    "name": thread.name,
                    "is_alive": thread.is_alive(),
                    "is_daemon": thread.daemon,
                    "thread_id": id(thread),
                }
        return thread_info

    def restart_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    self.stop_thread(thread_name)
                    EMMA_GLOBALS.sys_v.module_reloader(thread_name, True)
                    self.start_thread(thread_name)
                    return True, f"{thread_name} has been restarted."
                else:
                    return True, f"Thread '{thread_name}' is not running"
            else:
                return True, f"Thread '{thread_name}' not found"

    def stop_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    thread_instance = EMMA_GLOBALS.thread_instances.get(
                        thread_name)
                    thread_instance.stop()
                    return True, f"\n{thread_name} has been stopped."
                else:
                    return True, f"\n{thread_name} not found."

    def remove_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    self.stop_thread(thread_name)
                    del EMMA_GLOBALS.thread_instances[thread_name]
                    return True, f"\n{thread_name} has been removed."
                else:
                    del EMMA_GLOBALS.thread_instances[thread_name]
                    return True, f"\n{thread_name} has been removed."

        else:
            return True, f"\nThread '{thread_name}' not found."

    def kill_thread(self):
        threads = EMMA_GLOBALS.thread_instances
        for thread_name in threads:
            for _, thread in self.threads.items():
                if str(thread.name) == thread_name:
                    if thread.is_alive():
                        thread_instance = EMMA_GLOBALS.thread_instances.get(
                            thread_name)
                        thread_instance.stop()
                        EMMA_GLOBALS.thread_instances.pop(thread_name)
                        return f"\n{thread_name} has been killed."
                else:
                    return f"\n{thread_name} is unk."
            else:
                return True, f"\nThread '{thread_name}' not found."
