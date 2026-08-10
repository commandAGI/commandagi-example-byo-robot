# CommandAGI · Bring your own robot

A complete, hardware-free example of **registering your own robot** on
[CommandAGI](https://commandagi.com): it streams a robot's camera into a CommandAGI session and
applies the drive actions it receives. Anyone with the session link — a person in the web UI, an AI
agent, or another developer's SDK client — can then watch the camera and drive the robot in real time.

This runs a _virtual_ rover so you can try it with no hardware. Swap `VirtualRobot` for your real
robot — a `camera()` that returns JPEG bytes and an `on_action(action, payload)` that moves it — and
you've put a physical robot on the platform.

## Run it

```bash
pip install -r requirements.txt
export COMMANDAGI_API_KEY=cagi_...        # create one in your CommandAGI dashboard (operator scope)
python virtual_robot.py
```

It prints a session URL — open it to watch your robot's camera and drive it (move / turn / stop /
reset). Press Ctrl-C to take the robot offline.

## How it works

```python
from commandagi import CommandAGI

cagi = CommandAGI()                         # COMMANDAGI_API_KEY from the environment
bridge = cagi.register_robot("virtual-rover")   # registers a robot device, returns a bridge
print("watch + drive at:", bridge.session_url)

bridge.run(
    camera=robot.camera,                    # () -> JPEG/PNG bytes  (your robot's observation)
    on_action=robot.on_action,              # (action, payload) -> None  (drive your robot)
    fps=10,
)
```

- `register_robot()` creates an agentless **machine** with a bring-your-own robot device and returns a
  `RobotBridge`.
- `bridge.run()` connects to the session's realtime channel, publishes each `camera()` frame, and calls
  `on_action()` for every control message the platform routes to your robot.

The control vocabulary for a mobile robot: `move {speed}`, `back {speed}`, `turn {dir, rate}`, `stop`,
`reset`.

## Learn more

- Robot developer API + Python SDK: <https://commandagi.com/docs/robots>
- Full HTTP + WebSocket reference (what the SDK wraps): the `ROBOT_DEVELOPER_API` doc.

MIT licensed.
