import threading
import emma.config.globals as EMMA_GLOBALS


class InputRouter:
    def __init__(self, console_handler, queue_handler) -> None:
        self.tag = "ROUTER IO"
        self.console_handler = console_handler
        self.queue_handler = queue_handler
        self.stop_flag = False
        self.event = threading.Event()

    def main(self):
        self.event.wait()
        while not self.stop_flag:
            # Here suppose that have many io queues than only 1
            a_input = self.queue_handler.get_queue("API_INPUT")

            self.queue_handler.add_to_queue(
                'GPT_INPUT', a_input)
            key, data = self.queue_handler.get_queue("RESPONSE")

            if key == 's0offline':
                self.command_indexer(keyword=data, off_key=True)

            elif key == 'funcall':
                result = self.command_indexer(
                    keyword=data[0])
                if result is not False:
                    result.append(data[1])
                    self.queue_handler.add_to_queue('COMMAND', result)
            elif key == 'answer':
                self.queue_handler.add_to_queue('API_RESPONSE', data)

    def command_indexer(self, keyword, off_key=False):
        diccionary = EMMA_GLOBALS.tools_da.json_loader(
            EMMA_GLOBALS.stcpath_command_dir,
            keyword,
            "command",
            self.console_handler,
        )

        if off_key:
            first_key = next(iter(diccionary))
            args = keyword.replace(first_key, '')

        if diccionary != None:
            return [diccionary]
        else:
            return False

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    pass
