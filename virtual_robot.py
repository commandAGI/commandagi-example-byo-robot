"""Register your own robot on CommandAGI — a complete, hardware-free example.

This brings a *virtual* differential-drive rover online: it streams a top-down camera view of the
robot into a CommandAGI session and applies the drive actions it receives (move/turn/stop/reset).
Anyone with the session link — a person in the web UI, an agent, or another developer's SDK client —
then watches the camera and drives the robot in real time. Swap `VirtualRobot` for your real
hardware (a `camera()` that returns JPEG bytes and an `on_action()` that moves the robot) and you've
put a physical robot on the platform.

Run it:

    pip install commandagi pillow
    export COMMANDAGI_API_KEY=cagi_...        # create one in your CommandAGI dashboard
    python virtual_robot.py

Then open the printed session URL to watch and drive your robot.
"""
import io
import math
import os
import threading
import time

from PIL import Image, ImageDraw

from commandagi import CommandAGI

FIELD_W, FIELD_H = 640, 480


class VirtualRobot:
    """A toy differential-drive rover on a 2D field. Replace with your real robot."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.x, self.y, self.heading = FIELD_W / 2, FIELD_H / 2, 0.0
        self.v = 0.0  # linear speed (px/tick)
        self.w = 0.0  # angular speed (rad/tick)

    # Apply a control action received from the platform.
    def on_action(self, action: str, payload: dict) -> None:
        if action == "move":
            self.v = float(payload.get("speed", 0.6)) * 6
        elif action == "back":
            self.v = -float(payload.get("speed", 0.5)) * 6
        elif action == "turn":
            self.w = 0.15 * float(payload.get("rate", 0.6)) * (1 if payload.get("dir", "left") == "left" else -1)
        elif action == "stop":
            self.v = self.w = 0.0
        elif action == "reset":
            self.reset()

    # Advance the physics one step.
    def tick(self) -> None:
        self.heading += self.w
        self.x = min(FIELD_W - 20, max(20, self.x + math.cos(self.heading) * self.v))
        self.y = min(FIELD_H - 20, max(20, self.y + math.sin(self.heading) * self.v))

    # The robot's "camera": a top-down view of the field with the rover. Returns JPEG bytes.
    def camera(self) -> bytes:
        img = Image.new("RGB", (FIELD_W, FIELD_H), (24, 24, 28))
        d = ImageDraw.Draw(img)
        for gx in range(0, FIELD_W, 40):
            d.line([(gx, 0), (gx, FIELD_H)], fill=(40, 40, 46))
        for gy in range(0, FIELD_H, 40):
            d.line([(0, gy), (FIELD_W, gy)], fill=(40, 40, 46))
        hx, hy = math.cos(self.heading), math.sin(self.heading)
        px, py = -hy, hx
        tip = (self.x + hx * 18, self.y + hy * 18)
        left = (self.x - hx * 10 + px * 10, self.y - hy * 10 + py * 10)
        right = (self.x - hx * 10 - px * 10, self.y - hy * 10 - py * 10)
        d.polygon([tip, left, right], fill=(120, 230, 180))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=70)
        return buf.getvalue()


def main() -> None:
    cagi = CommandAGI()  # reads COMMANDAGI_API_KEY (+ optional COMMANDAGI_BASE_URL)
    robot = VirtualRobot()

    # Run the physics in the background so the world keeps moving between frames.
    def physics() -> None:
        while True:
            robot.tick()
            time.sleep(1 / 30)

    threading.Thread(target=physics, daemon=True).start()

    bridge = cagi.register_robot("virtual-rover")
    print("Robot online. Watch + drive it at:", bridge.session_url)
    print("Press Ctrl-C to take it offline.")
    bridge.run(camera=robot.camera, on_action=robot.on_action, fps=10)


if __name__ == "__main__":
    main()
