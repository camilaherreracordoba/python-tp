import random
import threading
import time
import logging


logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

semaforo = threading.Semaphore()

latasEnEspera = 1
botellasEnEspera = 1

class Heladera(threading.Thread):
    def __init__(self):    
        super().__init__()
        self.botellas = 0
        self.latas = 0
        self.MAXBotellas = 10
        self.MAXLatas = 15
        self.estaPrendida = False

    def cargarLatas(self):
        global latasEnEspera
        if (self.estaPrendida):
            if(self.latas + latasEnEspera <= self.MAXLatas):
                self.latas += latasEnEspera
                latasEnEspera -= latasEnEspera
                logging.info('%i latas guardadas' %self.latas)
            else:
                aux = self.MAXLatas - self.latas
                self.latas += aux
                latasEnEspera -= aux

    def cargarBotellas(self):
        global botellasEnEspera
        if (self.estaPrendida):
            if(self.botellas + botellasEnEspera <= self.MAXBotellas):
                self.botellas += botellasEnEspera
                botellasEnEspera -= botellasEnEspera
                logging.info('%i botellas guardadas' %self.botellas)
            else:
                aux = self.MAXBotellas - self.botellas
                self.botellas += aux
                botellasEnEspera -= aux 

    def llenar(self):
        while(True):
            if(latasEnEspera > 0):
                self.cargarLatas()
            if(botellasEnEspera > 0):
                self.cargarBotellas()
            if(self.botellas == 10 and self.latas == 15):
                logging.info('esta completa %i botellas y %i latas' %(self.botellas, self.latas))
                logging.info('%i botellas y %i latas restantes' % (botellasEnEspera, latasEnEspera))
                break

    def enchufar(self):
        logging.info('enchufando %s ...' % self.name)
        time.sleep(random.randint(1, 10))
        self.estaPrendida = True
        logging.info('prendida')

    def activarEnfriado(self):
        logging.info('activando enfriado rápido')
        time.sleep(random.random())
    
    def run(self):
        self.llenar()
        

class Proveedor(threading.Thread):
    def __init__(self):
        super().__init__()
        self.botellas = random.randint(0, 10)
        self.latas = random.randint(0, 15)

    def run(self):
        global latasEnEspera
        global botellasEnEspera
        time.sleep(random.randint(0, 20)) # los proveedores van a tardar una cantidad de tiempo indeterminada para hacer la entrega 
        logging.info('entregando cervezas...')
        latasEnEspera += self.latas
        botellasEnEspera += self.botellas
        logging.info('%i botellas y %i latas entregadas' % (self.botellas, self.latas))

def organizador(heladeras):
    for i in heladeras:
        semaforo.acquire()
        i.enchufar()
        i.start()
        if(i.latas == 15 and i.botellas == 10):
            i.activarEnfriado()
            semaforo.release()

latasEnEspera = 0
botellasEnEspera = 0
heladeras = []

for i in range(15):
    h = Heladera()
    h.name = 'Heladera'+str(i)
    heladeras.append(h)
heladeras.reverse()
orga = threading.Thread(target= organizador,  name= 'Organizador', args= (heladeras, ))
orga.start()

for i in range(5):
    p = Proveedor()
    p.name = 'Proveedor' + str(i)
    p.start()

