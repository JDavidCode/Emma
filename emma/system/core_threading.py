import datetime
import queue
import threading
import emma.globals as EMMA_GLOBALS
import time
import traceback

class ThreadHandler:
    def __init__(self):
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

    def restart_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    self.stop_thread(thread_name)
                    EMMA_GLOBALS.sys_v.module_reloader(thread_name, True)
                    self.start_thread(thread_name)
                    return f"{thread_name} has been restarted."
                else:
                    return f"Thread '{thread_name}' is not running"
            else:
                return True, f"Thread '{thread_name}' not found"

    def stop_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    thread_instance = EMMA_GLOBALS.thread_instances.get(
                        thread_name)
                    thread_instance.stop()
                    return f"\n{thread_name} has been stopped."
                else:
                    return f"\n{thread_name} not found."

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

class EventHandler:
    def __init__(self, console_handler):
            self.subscribers = []
            self.console_handler = console_handler
            self.shutdown_flag = []
            self.tag = "Event Handler"

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
                self.console_handler.write(self.tag, f"{subscriber} HAS BEEN NOTIFY THE SHUTDOWN")
            except Exception as e:
                self.console_handler.write(self.tag, f"ERROR WHEN NOTIFY {subscriber} SHUTDOWN {e}")
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))
                continue
        time.sleep(3)
        self.subscribers = []
    
    def notify_overload(self):
            pass

    def notify_connection(self):
            pass

    def notify_disconnection(self):
            pass

    def notify_progress(self, progress_percentage):
            pass

class QueueHandler:
    def __init__(self):
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
            self.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))
            if default is not None:
                return default

    def get_secure_queue_item(self, name, special_id, out=None):
            if name not in self.secure_queues or special_id not in self.secure_queues[name]:
                return None
            if out is not None:
                try:
                    return self.secure_queues[name][special_id].get(timeout=out)
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))
                    return None
            else:
                try:
                    return self.secure_queues[name][special_id].get()
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))
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

class ConsoleHandler:
    def __init__(self, queue_handler):
            self.queue = queue_handler
            dateTime = datetime.datetime.now()
            clock = dateTime.time()
            self.clock = clock.strftime("%H:%M:%S")
            self.output_queue = queue.Queue()
            self.console_thread = threading.Thread(
                target=self._output_console, daemon=True
            )
            self.console_thread.start()

    def _output_console(self):
            while True:
                output = self.output_queue.get()
                print(f"[{self.clock}] | {output}")

    def write(self, remitent, output):
            self.queue.add_to_queue("LOGGING", [remitent, output])
            self.output_queue.put(f"{remitent}: {output}")