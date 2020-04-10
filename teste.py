from mic     import Mic
from speaker import Speaker
from modem   import Modem


mic = Mic()
speaker = Speaker()
modem = Modem()

while True:
	entrada = mic.read()

	# modulado   =  modem.modAm(entrada)
	# demodulado = modem.demodAm(modulado)

	modulado   =  modem.modAmsc(entrada)
	demodulado = modem.demodAmsc(modulado)

	# modulado   = modem.modFm(entrada)
	# demodulado = modem.demodFm(modulado)

	speaker.play(demodulado)
