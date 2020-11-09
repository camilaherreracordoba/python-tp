import random
import threading
import time
import logging


logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

#semaforoHeladeras = threading.Semaphore()

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
        # --- DEL BONUS 1 ---
        self.semaforoInterno = threading.Semaphore(0) # los asistentes de la fiesta esperan a que se completen las heladeras

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

    def estaVacia(self):
        return self.botellas == 0 == self.latas

    def llenar(self):
        while(True):
            if(latasEnEspera > 0):
                self.cargarLatas()
            if(botellasEnEspera > 0):
                self.cargarBotellas()
            if(self.botellas == 10 and self.latas == 15):
                self.semaforoInterno.release()
                logging.info('%s esta completa' %(self.name))
                logging.info('%i botellas y %i latas restantes' % (botellasEnEspera, latasEnEspera))
                break
    # --- DEL BONUS 1 ---
    def sacarUnaLata(self):
        with (self.semaforoInterno):
            if(self.latas != 0):
                self.latas -= 1
    # --- DEL BONUS 1 ---
    def sacarUnaBotella(self):
        with (self.semaforoInterno):
            if(self.botellas != 0):
                self.botellas -= 1
    # hay que usar un monitor para prevenir que saquen las cervezas antes de que se llene la heladera
    def enchufar(self):
        logging.info('enchufando %s ...' % self.name)
        time.sleep(random.randint(1, 10))
        self.estaPrendida = True
        logging.info('prendida')

    def activarEnfriado(self):
        logging.info('activando enfriado rápido')
        time.sleep(random.random())
    # --- DEL BONUS 2 ---
    def detectarLataPinchada(self):
        time.sleep(random.randint(10, 100))
        if(not self.estaVacia()):
            logging.info('hay que quitar una lata pinchada')
            self.sacarUnaLata()
            logging.info('ya sacamos la lata pinchada, quedan %i latas' % self.latas)
       
    def run(self):
        self.llenar()
        while(True):
            self.detectarLataPinchada()

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

class Beode(threading.Thread):
    def __init__(self, heladeras):
        super().__init__()
        self.limite = random.randint(7, 15)
        self.tomadas = 0
        self.heladera = heladeras[random.randint(0, len(heladeras)-1)]
        self.bebeEnBotellas = False
        self.bebeEnLatas = False
        # esto es asumiendo que las cervezas tienen la misma cantidad
        r = random.randint(0, 3)
        if (r == 0):
            self.bebeEnLatas = True
        elif (r == 1):
            self.bebeEnBotellas = True
        elif (r == 2):
            self.bebeEnLatas = True
            self.bebeEnBotellas = True
    # tiene que elegir de que heladera tomar antes, pasando la lista con el constructor
    def tomarBotella(self):
        while(True):
            if(self.heladera.botellas != 0):
                time.sleep(1)
                self.heladera.sacarUnaBotella()
                self.tomadas += 1
                logging.info('tomando botella')
                break
    def tomarLata(self):
        while(True):
            if(self.heladera.latas != 0):
                time.sleep(1)
                self.heladera.sacarUnaLata()
                self.tomadas += 1
                logging.info('tomando lata')
                break

    def tomarCualquiera(self):
        i = random.randint(0, 2)
        if (i == 0):
            self.tomarBotella()
        elif(i == 1):
            self.tomarLata()
    def tomar(self):
        logging.info('voy a tomar de la %s' % self.heladera.name)
        while(self.limite != self.tomadas):
            time.sleep(random.randint(2, 20)) # para simular que se toma un tiempo entre cervezas
            if(self.bebeEnBotellas):
                self.tomarBotella()
            elif(self.bebeEnLatas):
                self.tomarLata()
            else:
                self.tomarCualquiera()
            if(self.limite == self.tomadas):
                logging.info('ya no puede seguir tomando, quebró (%i cervezas tomadas)' % self.tomadas)
                logging.info('botellas: %i' % self.heladera.botellas)
                logging.info('latas: %i' % self.heladera.latas)
                break

    def run(self):
        time.sleep(random.randint(0, 10))
        self.tomar()

class Organizador(threading.Thread):
    def __init__(self, heladeras):
        super().__init__()
        self.heladeras = heladeras
        self.semaforoCompletas = threading.Semaphore(0)
        self.completo = False
        self.monitor = threading.Condition()

    # BONUS PARTE 3
    def reponer(self):
        with self.semaforoCompletas:
            self.heladeras.sort(key = lambda h: h.latas + h.botellas)
            for i in self.heladeras:
                i.semaforoInterno.acquire()
                i.llenar()
    def organizar(self):
        for i in heladeras:
            i.enchufar()
            i.start()
            if(i.latas == 15 and i.botellas == 10):
                i.activarEnfriado()
        logging.info('se completaron todas las heladeras')
        self.completo = True
        self.semaforoCompletas.release()
    def run(self):
        self.organizar()
        while(True):
            with self.monitor:
                self.monitor.wait()
                self.reponer()
 
latasEnEspera = 0
botellasEnEspera = 0
heladeras = []

for i in range(2):
    h = Heladera()
    h.name = 'Heladera'+str(i)
    heladeras.append(h)

orga = Organizador(heladeras)
orga.name = 'Organizador'
orga.start()

    # --- DEL BONUS 1 ---
for i in range(30):
    b = Beode(heladeras)
    b.name = 'Borrachín'+str(i)
    b.start()

for i in range(15):
    p = Proveedor()
    p.name = 'Proveedor' + str(i)
    p.start()
    # --- DEL BONUS 3 ---
    if (orga.completo):
        with orga.monitor:
            orga.monitor.notify()
    time.sleep(random.randint(5, 30))
