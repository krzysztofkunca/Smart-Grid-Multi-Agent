import random
from typing import Any, Union, List

from osbrain import Agent
from osbrain import run_agent
from osbrain import run_nameserver

# Watts

class Consumer(Agent):

    def on_init(self):
        number = 2 ################################### maksymalna liczba dostawcow do jednego klienta
        self.bind('PUSH', alias='main')
        self.bind('PUSH', alias='secondary')
        lista = list(range(number))
        self.network = []
        self.PPindex = 0
        for i in range(number): # losowanie polaczen z elektrownia - losowa struktura sieci
            self.network.append(random.choice(lista))
            lista.remove(self.network[i])

    def getConsumption(self):
        return str(random.randint(100, 1000))

    def getConnections(self):
        return self.network

    def getIndex(self):
        return self.PPindex

class PowerPlant(Agent): ############ wprowadzic topic'i do 'PUB'a. Jesli elektrownia jest pelna to klient ktory nie wyslal(?) demand'a zmienia temat oraz wysyla gdzie indziej(łączy z sencondary)
    def on_init(self):
        self.maxpower = 200 * 1000000
        self.minpower = 100 * 1000000
        self.demand = 0
        self.bind('PUB', alias='alert')

    def checkDemand(self):
        if self.demand < self.minpower:
            self.send('alert', 'OFF')
        elif self.demand > self.maxpower:
            self.send('alert', 'HELP') ################## co dalej
        else:
            self.send('alert', 'OK')
