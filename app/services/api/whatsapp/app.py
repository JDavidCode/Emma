import os
import threading
import traceback
import requests


class App:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.response_thread = None
        self.token = os.getenv("WHATSAPP_BUSINESS_TOKEN")
        self.phone_id = os.getenv("WHATSAPP_PHONE_ID")

    def send_whatsapp_message(self, recipient, text):
        url = f"https://graph.facebook.com/v18.0/{self.phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"body": text}
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Error sending message: {response.text}")
        
    def process_responses(self):
        try:
            while not self.stop_flag:
                ids, data = self.queue_handler.get_queue(
                    "WHATSAPP_API_RESPONSE", 0.1, (None, None))
                if ids is None:
                    continue
                else:
                    pass
        except Exception as e:
            self.handle_error(e)

    def main(self):
        self.event.wait()
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Is Started"])
        try:
            while not self.stop_flag:
                data = self.queue_handler.get_queue(
                    "WHATSAPP_WEBHOOK", 0.1, (None))
                if data is None:
                    continue
                else:
                    update_json = data.get('update')
                    
        except Exception as e:
            self.handle_error(e)

    def run(self):
        self.event.set()

    def _handle_system_ready(self):
        self.response_thread = threading.Thread(
            target=self.process_responses, name=f"{self.name}_RESPONSES")
        self.response_thread.start()
        self.run()
        return True

    def stop(self):
        self.stop_flag = True

    def handle_error(self, error, message=None):
        error_message = f"Error in {self.name}: {error}"
        if message:
            error_message += f" - {message}"
        traceback_str = traceback.format_exc()
        self.queue_handler.add_to_queue("LOGGING", (self.name, traceback_str))

    def _handle_shutdown(self):
        try:
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)
        except Exception as e:
            self.handle_error(e)


if __name__ == "__main__":
    pass
