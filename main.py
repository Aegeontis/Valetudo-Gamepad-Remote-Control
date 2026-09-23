import os

import pygame

import vale

DRY_RUN = False

VERT_AXIS = 1
HORZ_AXIS = 0

VERT_AXIS_DIR = -1
HORZ_AXIS_DIR = 1

DEADZONE = 0.15
SEND_INTERVAL_MS = 150

BUTTON_X = 2
BUTTON_Y = 3

rc = vale.RemoteControl(os.environ.get("VALE_URL"))

if not DRY_RUN:
    rc.enter()

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
RED = pygame.Color('red')

JS_PREVIEW_RADIUS = 150
JS_PREVIEW_CENTER = [300 + JS_PREVIEW_RADIUS, 300 + JS_PREVIEW_RADIUS]


class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


def normalize_axis(value):
    if abs(value) < DEADZONE:
        return 0.0
    sign = 1.0 if value > 0 else -1.0
    return sign * ((abs(value) - DEADZONE) / (1.0 - DEADZONE))


def calculate_movement(x, y):
    if abs(x) < DEADZONE and abs(y) < DEADZONE:
        return 0.0, 0.0

    velocity = normalize_axis(y) if abs(y) > DEADZONE else 0.0
    angle = x * 90.0

    return max(-1.0, min(1.0, velocity)), angle


try:
    pygame.init()
    screen = pygame.display.set_mode((650, 650))
    pygame.display.set_caption("Whack a Robot")

    done = False
    clock = pygame.time.Clock()

    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    textPrint = TextPrint()

    last_send_time = 0
    last_velocity = None
    last_angle = None

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == BUTTON_Y:
                    print("Y -> home")
                    rc.home()
                elif event.button == BUTTON_X:
                    print("X -> stop")
                    rc.basic_stop()

        screen.fill(WHITE)
        textPrint.reset()

        joystick_count = pygame.joystick.get_count()
        textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
        textPrint.indent()

        try:
            jid = joystick.get_instance_id()
        except AttributeError:
            jid = joystick.get_id()
        textPrint.tprint(screen, "Joystick {}".format(jid))
        textPrint.indent()

        name = joystick.get_name()
        textPrint.tprint(screen, "Joystick name: {}".format(name))

        try:
            guid = joystick.get_guid()
        except AttributeError:
            pass
        else:
            textPrint.tprint(screen, "GUID: {}".format(guid))

        axes = joystick.get_numaxes()
        textPrint.tprint(screen, "Number of axes: {}".format(axes))
        textPrint.indent()

        for i in range(axes):
            axis = joystick.get_axis(i)
            textPrint.tprint(screen, "Axis {} value: {:>6.3f}".format(i, axis))
        textPrint.unindent()

        buttons = joystick.get_numbuttons()
        textPrint.tprint(screen, "Number of buttons: {}".format(buttons))
        textPrint.indent()

        for i in range(buttons):
            button = joystick.get_button(i)
            textPrint.tprint(screen, "Button {:>2} value: {}".format(i, button))
        textPrint.unindent()

        hats = joystick.get_numhats()
        textPrint.tprint(screen, "Number of hats: {}".format(hats))
        textPrint.indent()

        for i in range(hats):
            hat = joystick.get_hat(i)
            textPrint.tprint(screen, "Hat {} value: {}".format(i, str(hat)))
        textPrint.unindent()

        textPrint.unindent()

        x = joystick.get_axis(HORZ_AXIS) * HORZ_AXIS_DIR
        y = joystick.get_axis(VERT_AXIS) * VERT_AXIS_DIR

        velocity, angle = calculate_movement(x, y)

        pygame.draw.circle(screen, BLACK, JS_PREVIEW_CENTER, JS_PREVIEW_RADIUS, 1)
        pygame.draw.line(screen, BLACK,
                         [JS_PREVIEW_CENTER[0], JS_PREVIEW_CENTER[1] - JS_PREVIEW_RADIUS],
                         [JS_PREVIEW_CENTER[0], JS_PREVIEW_CENTER[1] + JS_PREVIEW_RADIUS])
        pygame.draw.line(screen, BLACK,
                         [JS_PREVIEW_CENTER[0] - JS_PREVIEW_RADIUS, JS_PREVIEW_CENTER[1]],
                         [JS_PREVIEW_CENTER[0] + JS_PREVIEW_RADIUS, JS_PREVIEW_CENTER[1]])

        pygame.draw.line(screen, RED, JS_PREVIEW_CENTER,
                         [JS_PREVIEW_CENTER[0] + JS_PREVIEW_RADIUS * x,
                          JS_PREVIEW_CENTER[1] - JS_PREVIEW_RADIUS * y], 2)

        if not DRY_RUN:
            now = pygame.time.get_ticks()
            is_moving = velocity != 0.0 or angle != 0.0
            velocity_changed = last_velocity is None or abs(velocity - last_velocity) > 0.03
            angle_changed = last_angle is None or abs(angle - last_angle) > 3.0
            due = now - last_send_time > SEND_INTERVAL_MS

            if velocity_changed or angle_changed or (is_moving and due):
                rc.move(round(velocity, 3), round(angle, 1))
                last_velocity = velocity
                last_angle = angle
                last_send_time = now

        pygame.display.flip()
        clock.tick(60)

finally:
    if not DRY_RUN:
        rc.exit()

pygame.quit()
