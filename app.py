from time import sleep
from enum import Enum

from ctrl9000 import Pigeon, State
from gpiozero import Button, LED
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008 as MCP3008

GPIO_MODE_BUTTON = 17
GPIO_POWER_BUTTON = 24

SPI_PORT = 0
SPI_DEVICE = 0

MAX_SLIDE_VALUE = 1023

SLIDE_MODIFIER = 400

MAX_CYCLE_LENGTH = 100


class Color(Enum):
	RED = 1
	GREEN = 2


class RGLED:
	def __init__(self, red, green):
		self.red_led = red
		self.green_led = green
		self.color = None


	def toggle(self):
		if self.color is Color.RED:
			self.green()
		elif self.color is Color.GREEN:
			self.red()
		elif self.color is None:
			self.red()


	def green(self):
		self.red_led.off()
		self.green_led.on()
		self.color = Color.GREEN


	def red(self):
		self.green_led.off()
		self.red_led.on()
		self.color = Color.RED


pigeon = Pigeon()
state = State()

mcp = MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

power_button = Button(GPIO_POWER_BUTTON)
switch_mode_button = Button(GPIO_MODE_BUTTON)

rgled = RGLED(LED(22), LED(27))
rgled.red()


def calc_cycle_time(slide_state):
	return ((MAX_CYCLE_LENGTH / MAX_SLIDE_VALUE) * slide_state) + 30


def calc_operating_ratio(slide_state):
	# Calculate slide state in percent
	return (100 - (100 / (MAX_SLIDE_VALUE + (SLIDE_MODIFIER * 2))) * \
		(slide_state + SLIDE_MODIFIER)) * 0.01



def switch_power():
	state.power = not state.power
	rgled.toggle()
	pigeon.push(state)

power_button.when_pressed = switch_power

try:
	while True:
		cycle_slide_state = mcp.read_adc(0)
		ratio_slide_state = mcp.read_adc(1)

		state.cycle_time = calc_cycle_time(cycle_slide_state)
		state.operating_ratio = calc_operating_ratio(ratio_slide_state)
		
		pigeon.push(state)

		sleep(0.5)

except KeyboardInterrupt:
	state.power = False
	pigeon.push(state)