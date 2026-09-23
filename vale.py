import queue
import threading
import warnings

import requests

warnings.filterwarnings("ignore", message="Unverified HTTPS request")


class RemoteControl:
    def __init__(self, robot_url: str):
        self.robot_url = robot_url
        self.manual_ctl = '/api/v2/robot/capabilities/HighResolutionManualControlCapability'
        self.basic_ctl = '/api/v2/robot/capabilities/BasicControlCapability'

        self._queue = queue.Queue(maxsize=1)
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _run(self):
        while True:
            path, payload = self._queue.get()
            try:
                r = requests.put(
                    self.robot_url + path,
                    json=payload,
                    verify=False,
                    timeout=5,
                )
                print(payload.get('vector', payload.get('action')), r.status_code)
            except requests.RequestException as e:
                print("error:", e)

    def _send(self, path: str, payload: dict):
        """Enqueue, dropping the previous item if it hasn't been sent yet."""
        try:
            self._queue.get_nowait()
        except queue.Empty:
            pass
        try:
            self._queue.put_nowait((path, payload))
        except queue.Full:
            pass

    def enter(self):
        self._send(self.manual_ctl, {'action': 'enable'})

    def exit(self):
        self._send(self.manual_ctl, {'action': 'disable'})

    def move(self, velocity: float, angle: float):
        self._send(
            self.manual_ctl,
            {'action': 'move', 'vector': {'velocity': velocity, 'angle': angle}},
        )

    def stop(self):
        self.move(0.0, 0.0)

    def home(self):
        self._send(self.basic_ctl, {'action': 'home'})

    def basic_stop(self):
        self._send(self.basic_ctl, {'action': 'stop'})
