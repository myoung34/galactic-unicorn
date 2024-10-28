import time
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
import urequests
from mqtt_as import MQTTClient, config
from secrets import config as secrets_config
import asyncio
import json

# Local configuration
config["ssid"] = secrets_config["ssid"]
config["wifi_pw"] = secrets_config["wifi_pw"]
config["server"] = secrets_config["server"]

gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)
width = 53
height = 11

# constants for controlling scrolling text
PADDING = 5
MESSAGE_COLOUR = (255, 255, 255)
OUTLINE_COLOUR = (0, 0, 0)
BACKGROUND_COLOUR = (10, 0, 96)
HOLD_TIME = 2.0
STEP_TIME = 0.075


class Image:
    # message is a list of lists of RGB integers such as
    # [
    #   [0,0,255],[0,0,255],[0,0,255],
    #   [0,0,255],[255,255,0],[0,0,255],
    #   [0,0,255],[0,0,255],[0,0,255],
    # ]
    def __init__(
        self,
        message,
        blinking=False,
        scrolling=False,
    ):
        self.message = message
        self.blinking = blinking
        self.scrolling = scrolling
        self.max_width = 0
        self.max_height = 0


class Message:
    def __init__(
        self,
        message,
        font="Letters",
        font_color=(230, 210, 250),
        background_color=(20, 20, 120),
        max_width=0,
        max_height=0,
        pre_buffer=0,
        post_buffer=0,
        start_buffer=0,
        end_buffer=True,
        blinking=False,
        scrolling=False,
    ):
        self.message = message
        self.font = font
        self.font_color = font_color
        self.background_color = background_color
        self.max_width = max_width
        self.max_height = max_height
        self.pre_buffer = pre_buffer
        self.post_buffer = post_buffer
        self.start_buffer = start_buffer
        self.end_buffer = end_buffer
        self.blinking = blinking
        self.scrolling = scrolling

        if len(message) == 0:
            self.ascii = [""]
        else:
            self.ascii = self.get_ascii()

    def get_ascii(self):
        response = urequests.get(
            f"https://asciified.thelicato.io/api/v2/ascii?text={self.message}&font={self.font}"
        )
        self.max_width = 0
        self.max_height = height - self.pre_buffer - self.post_buffer
        lines = response.text.splitlines()

        for i in range(len(lines)):
            if len(lines[i]) > self.max_width:
                self.max_width = len(lines[i])
            for x in range(0, self.start_buffer):
                lines[i] = " " + lines[i]

            if self.blinking:
                lines[i] += "XXXXXX"
            # for x in range(0, end_buffer):
            if self.end_buffer:
                lines[i] += " " * (width - len(lines[i]))
                if len(lines[i]) > self.max_width:
                    self.max_width = len(lines[i])
            print(lines[i])

        for x in range(0, self.pre_buffer):
            # lines.insert(0, [[" ", " ", " ",]])
            lines[0:0] = [" " * width]
        for x in range(0, self.post_buffer):
            # lines.insert(0, [[" ", " ", " ",]])
            lines.extend([" " * width])
            # lines[-1:-1] = ["              "]

        return [line for line in lines]


@micropython.native  # noqa: F821
def draw_image(image, time_ms, scrolling=False, blinking=False):
    # image is a list of lists of RGB integers such as
    # [
    #   [[0,0,255],[0,0,255],[0,0,255]],
    #   [[0,0,255],[255,255,0],[0,0,255]],
    #   [[0,0,255],[0,0,255],[0,0,255]],
    # ]
    for y, row in enumerate(image):
        for x, (r, g, b) in enumerate(row):
            graphics.set_pen(graphics.create_pen(r, g, b))
            graphics.pixel(x, y)
    gu.update(graphics)


@micropython.native  # noqa: F821
def draw(image, sx, sy, fg, bg, time_ms, scrolling=False, blinking=False):
    fg_pen = graphics.create_pen(fg[0], fg[1], fg[2])
    bg_pen = graphics.create_pen(bg[0], bg[1], bg[2])
    for y in range(len(image)):
        row = image[y]
        for x in range(len(row)):
            pixel = row[x]
            if blinking:
                if not pixel.isspace() and pixel != "X":
                    graphics.set_pen(fg_pen)
                # draw blinking
                elif pixel == "X" and (time_ms // 300) % 2:
                    graphics.set_pen(fg_pen)
                else:
                    graphics.set_pen(bg_pen)
                if scrolling:
                    graphics.pixel(x + sx, y + sy)
                else:
                    graphics.pixel(x, y)
            else:
                if not pixel.isspace():
                    graphics.set_pen(fg_pen)
                else:
                    graphics.set_pen(bg_pen)
                if scrolling:
                    graphics.pixel(x + sx, y + sy)
                else:
                    graphics.pixel(x, y)

    gu.update(graphics)


def callback(topic, msg, retained):
    message = {}
    global _message
    try:
        message["data"] = json.loads(json.loads(msg)["data"])
    except Exception:
        message = json.loads(msg)

    if message.get("type", "") == "image":
        _message = Image(message["data"]["message"])
        print(_message.message[0])
    else:
        _message = Message(
            message["data"]["message"],
            font=message["data"].get("font", "Letters"),
            font_color=message["data"].get("font_color", (230, 210, 250)),
            background_color=message["data"].get("background_color", (20, 20, 120)),
            max_width=message["data"].get("max_width", 0),
            max_height=message["data"].get("max_height", 0),
            pre_buffer=message["data"].get("pre_buffer", 0),
            post_buffer=message["data"].get("post_buffer", 0),
            start_buffer=message["data"].get("start_buffer", 0),
            end_buffer=message["data"].get("end_buffer", True),
            scrolling=message["data"].get("scrolling", False),
            blinking=message["data"].get("blinking", False),
        )


async def conn_han(client):
    await client.subscribe("foo", 1)


_message = Message("")


async def main(client):
    await client.connect()

    global _message
    smiley = __import__("test")
    _message = Image(smiley.get_image())

    gu.set_brightness(0.5)

    # state constants
    STATE_PRE_SCROLL = 0
    STATE_SCROLLING = 1
    STATE_POST_SCROLL = 2

    shift = 0
    state = STATE_PRE_SCROLL

    last_time = time.ticks_ms()

    while True:
        time_ms = time.ticks_ms()

        if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
            gu.adjust_brightness(+0.01)

        if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
            gu.adjust_brightness(-0.01)

        if state == STATE_PRE_SCROLL and time_ms - last_time > HOLD_TIME * 1000:
            if _message.max_width + PADDING * 2 >= width:
                state = STATE_SCROLLING
            last_time = time_ms

        if state == STATE_SCROLLING and time_ms - last_time > STEP_TIME * 1000:
            shift += 1
            if shift >= (_message.max_width + PADDING * 2) - width - 1:
                state = STATE_POST_SCROLL
            last_time = time_ms

        if state == STATE_POST_SCROLL and time_ms - last_time > HOLD_TIME * 1000:
            state = STATE_PRE_SCROLL
            shift = 0
            last_time = time_ms

        graphics.set_pen(
            graphics.create_pen(
                int(BACKGROUND_COLOUR[0]),
                int(BACKGROUND_COLOUR[1]),
                int(BACKGROUND_COLOUR[2]),
            )
        )
        graphics.clear()
        if isinstance(_message, Image):
            draw_image(
                _message.message,
                time_ms=time_ms,
            )
        else:
            if _message.scrolling:
                draw(
                    _message.ascii,
                    sx=PADDING - shift,
                    sy=2,
                    fg=_message.font_color,
                    bg=_message.background_color,
                    time_ms=time_ms,
                    scrolling=True,
                    blinking=True,
                )
            else:
                draw(
                    _message.ascii,
                    sx=0,
                    sy=2,
                    fg=_message.font_color,
                    bg=_message.background_color,
                    time_ms=time_ms,
                    scrolling=False,
                    blinking=True,
                )

            # update the display
        gu.update(graphics)

        # pause for a moment (important or the USB serial device will fail)
        await asyncio.sleep(0.001)


config["subs_cb"] = callback
config["connect_coro"] = conn_han

# Example call:
# curl -XPOST https://... -d \
#   '{"topic":"foo","data":{"font":"USA+Flag","message":"THIS+IS+FINE","scrolling":true,"pre_buffer":1,"start_buffer":0,"font_color":[255,255,0],"background_color":[0,0,255]}}
MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
