# to do list:
# -wprowadzic topiki w PUB, aby zmienial sie indeks klientowi od obserwowanej elektrowni
# -elektrownie wiedza ile jest klientow
# -zrobic na przykladzie warszawy - liczba elektrowni,moce, osiedla klientami itd
# -jak najkrotszy main - żądania na secondary powinny pojsc z metody w agencie
# -losowanie zapotrzebowania wg rozkladu normalnego
# -prawdopodobnie trzeba zmienic pub na push z żądaniem odpowiedzi - duzo łatwiejszy system zmiany elektrowni

import random
from typing import Any, Union, List
from osbrain import Agent
from osbrain import run_agent
from osbrain import run_nameserver

# Watts

class Consumer(Agent): #osiedle

    def on_init(self):
        #number = 2 ################################### maksymalna liczba dostawcow do jednego klienta
        self.bind('PUSH', alias='main')
        self.bind('PUSH', alias='secondary')
        self.network = [0,1,2,3]
        self.PPindex = 0
        self.consumption = 0
        #lista = list(range(number))

#        for i in range(number): # losowanie polaczen z elektrownia - losowa struktura sieci
#            self.network.append(random.choice(lista))
#            lista.remove(self.network[i])

    def getConsumption(self):
        if(self.consumption == 0):
            self.consumption = random.randint(1500000, 80000000)
        return str(self.consumption)

    def getConnections(self):
        return self.network

    def getIndex(self):
        return self.PPindex

    def clientNewDay(self):
        self.consumption = 0
        self.PPindex = 0

class PowerPlant(Agent): ############ wprowadzic topic'i do 'PUB'a. Jesli elektrownia jest pelna to klient ktory nie wyslal(?) demand'a zmienia temat oraz wysyla gdzie indziej(łączy z sencondary)
    def on_init(self):
        self.maxpower = 150 * 1000000
        self.minpower = 100 * 1000000
        self.demand = 0
        self.bind('PUB', alias='alert')

    def checkDemand(self):
        #if self.demand < self.minpower:
        #    self.send('alert', 'OFF')
        #    self.log_info('OFF')
        if self.demand > self.maxpower:
            self.send('alert', 'MAX',topic='0') ################## co dalej
            self.log_info('MAX')
        else:
            self.send('alert', 'OK')


def summariseDemand(self, message):
    self.demand = self.demand + int(message)
    self.log_info(self.demand)
    self.log_info('Received: %s' % message)
    self.checkDemand()
    #if self.demand >= self.maxpower:
    #    self.send('alert', 'MAX')
    #    print("max")

def changePowerPlant(self, message):
    if message == 'OFF':
        self.send('secondary', self.demand)
        self.log_info('Received OFF')
    elif message == 'MAX':
        self.PPindex = self.PPindex + 1
        self.log_info('Received MAX')


################################################## MAIN ##########################################################

if __name__ == '__main__':
    # System deployment
    numberOfClients = 15
    numberOfPowerPlants = 5
    clientNames = []
    powerplantNames = []
    clients = []  # type: List[object]
    powerplants = []
    ns = run_nameserver()
    topic = []

    for i in range(numberOfClients):
        clientNames.append('Client' + str(i + 1))
        clients.append(run_agent(clientNames[i], base=Consumer))  # type: object

    for i in range(numberOfPowerPlants):
        powerplantNames.append('PP' + str(i + 1))
        powerplants.append(run_agent(powerplantNames[i], base=PowerPlant))
        topic.append(str(i))

    # System configuration

    for i in clients:
        powerplants[i.getConnections()[i.getIndex()]].connect(i.addr('main'), handler=summariseDemand) #polacenie z pierwsza elektrownia
        i.connect( powerplants[ i.getConnections()[ i.getIndex() ]  ].addr('alert'), handler={ topic[i.getConnections()[i.getIndex()]]: changePowerPlant}) #subskrypcja wiadomosci wysylanych przez elektrownie z indeksem 1
        powerplants[i.getConnections()[i.getIndex()]+1].connect(i.addr('secondary'), handler=summariseDemand) #polaczenie  z drugą elektrownią
        i.connect( powerplants[ i.getConnections()[ i.getIndex()+1 ]  ].addr('alert'), handler={ topic[i.getConnections()[i.getIndex()+1]]: changePowerPlant}) #subskrypcja wiadomosci wysylanych przez elektrownie z indeksem 2

    # Send messagges - energy demand
    for i in clients:
        if i.getIndex() == 0:
            i.send('main', i.getConsumption())
            print(i.getIndex())
        elif i.getIndex() == 1:
            i.send('secondary', i.getConsumption())
            print("secondary")
            print(i.getIndex())

    # Checking whole demand by power plants: is it enough?

    ns.shutdown()


