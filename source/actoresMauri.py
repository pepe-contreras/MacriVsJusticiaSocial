'''
Created on 8 de feb. de 2016

@author: Martin
'''
import pilasengine
import math
from time import *
from time import sleep
from numpy.f2py.auxfuncs import throw_error


class Macri(pilasengine.actores.Actor):
    '''
    classdocs
    '''
    maurisEnJuego = []
    def __mul__(self,cant):
        return pilasengine.actores.Actor.__mul__(self,cant)
    
    def __init__(self,pilas,*k,**kw):
        '''
        Constructor
        '''
        Macri.maurisEnJuego.append(self)
        self.golpeado = False
        self.pilas = pilas
        pilasengine.actores.Actor.__init__(self,pilas)
        self.imagen = pilas.imagenes.cargar('macri.png')
        self.radio_de_colision = 50
        self.naveEnemiga = None
        self.escala= 0.75
        self.agregar_habilidad(self.pilas.habilidades.SeMantieneEnPantalla)
        self.agregar_habilidad(SeAlejadeOtrosMauirs)
        self.x = self.y = 0
        
    def agregarNave(self,nave):
        self.naveEnemiga = nave
        
    def eliminar(self):
        self.naveEnemiga.puntaje = self.naveEnemiga.puntaje + 1
        if self.golpeado:
            pilasengine.actores.Actor.eliminar(self)
        else:
            angulo = self.pilas.azar(0,360)
            vel = self.pilas.azar(1,5)
            if self.x > self.naveEnemiga.x:
                vel = -vel
            
            if (not self.naveEnemiga is None):
                angulo = definir_angulo(self,self.naveEnemiga)                       
            self.imagen = self.pilas.imagenes.cargar('macribobo.png')
            self.hacer(self.pilas.comportamientos.Proyectil,
                   velocidad_maxima=vel,
                   aceleracion=5,
                   angulo_de_movimiento = angulo,                       
                   gravedad=0)
            self.golpeado = True
            self.agregar_habilidad(self.pilas.habilidades.PuedeExplotarConHumo)
            

def definir_angulo(actorOrigen,actorDestino):
    dx = distancia(actorOrigen.x,actorDestino.x)
    dy = distancia(actorOrigen.y,actorDestino.y)
    if dx <> 0:
        return math.degrees(math.atan(dy/dx))
    return 90

def distancia(numero1,numero2):
    return numero2 - numero1
    
            
class NaveJusticialista(pilasengine.actores.Nave):
    '''
    classdocs
    '''
    MAX_POWER = 20
    RECHARG_CHORIPAN = 5
    NAVE = None
    
    @staticmethod
    def devolverNave():
        return NaveJusticialista.NAVE
    
    def __init__(self,pilas,*k,**kw):
        '''
        Constructor
        '''
        if (not (NaveJusticialista.NAVE is None)):
            raise Exception("No se puede crer mas de una nave Justicialista")
        NaveJusticialista.NAVE = self
        
        self.vida = 10
        self.puntaje = 0
        
        self.poder = NaveJusticialista.MAX_POWER
    
        self.pilas = pilas
        self.cipayos = None
        self.tiempoUltimoChori =0
        self.texto = pilas.actores.Texto()
        self.texto.x= 400
        self.texto.y= 300
        
        
        pilasengine.actores.Nave.__init__(self,pilas)
        self.aprender(pilas.habilidades.SeMantieneEnPantalla)
        self._habilidades[1].cuando_dispara = self.disparar
        self.figura_de_colision = pilas.fisica.Rectangulo(0, 0, 80, 120, sensor=True, dinamica=False)
    
    def sumarPuntos(self):
        self.puntaje = self.puntaje + 1
        
    def disparar(self):
        if self.poder > 0:
            self.poder = self.poder - 1
            
    def hacer_explotar_al_enemigo(self, mi_disparo, el_enemigo):
        if self.poder > 0:
            pilasengine.actores.Nave.hacer_explotar_al_enemigo(self, mi_disparo, el_enemigo)
                     
    def definir_enemigos(self, grupo, cuando_elimina_enemigo=None):
        self.cipayos = grupo
        for cipayo in grupo:
            self.pilas.colisiones.agregar(self, cipayo, cuando_colisiona)
        pilasengine.actores.Nave.definir_enemigos(self, grupo, cuando_elimina_enemigo=cuando_elimina_enemigo)

    def quitar_vida(self):
        self.vida = self.vida - 1
        if self.vida <= 0:
            for cipayo in self.cipayos:
                cipayo.eliminar()
            self.texto.texto = "GAME OVER, NEOLIBERALISM WINS!"
            self.texto.x=0
            self.texto.y=0
            self.texto.rotacion = [0,365]
            self.eliminar()
    
    def actualizar(self):
        self.texto.texto = "Vida: " + self.vida.__str__()  + " Poder: " +  self.poder.__str__() + " Puntaje: "  + self.puntaje.__str__()
           
        if  time() - self.tiempoUltimoChori > 5:
            self.pilas.colisiones.agregar(self, Chori.dameElChori(self.pilas), agarrar_chori)     
            self.tiempoUltimoChori = time()
                
        if self.poder > 0:
            self.municion = pilasengine.actores.Misil
            self._habilidades[1]._municion = pilasengine.actores.Misil
        else:
            self.municion = MisilInvisible
            self._habilidades[1]._municion = MisilInvisible
        
        ganado = True
        for cipayo in self.cipayos:
            if not cipayo.esta_eliminado():
                ganado = False
        if ganado:
            self.texto.texto = "La Victoria Ha triunfado!"
            self.texto.x=0
            self.texto.y=0
            self.texto.rotacion = [0,365]
            
            for cipayo in self.cipayos:
                cipayo.eliminar()
                cipayo.eliminar()
            
        pilasengine.actores.Nave.actualizar(self)
        

class MisilInvisible(pilasengine.actores.Misil):
    def __init__(self, pilas):
        pilasengine.actores.Misil.__init__(self,pilas)
        self.transparencia = 100    
        
def cuando_colisiona(nave, macri):
    if macri.golpeado:
        nave.quitar_vida()
        
def agarrar_chori(nave, chori):
    nave.poder = NaveJusticialista.RECHARG_CHORIPAN + nave.poder
    chori.eliminar()

class Chori(pilasengine.actores.Actor):
    CHORI = None
    
    def __init__(self,pilas):
        pilasengine.actores.Actor.__init__(self, pilas)
        self.imagen = "chori.png"
        self.escala = 0.5
      
        self.radio_de_colision = 50
        self.x = - self.pilas.widget.width()/2 
        altoNave = NaveJusticialista.devolverNave().y + self.pilas.widget.height()/2 - 100

        if(self.pilas.widget.height() - altoNave > altoNave):
            fin = int(altoNave)
            inicio =  100
        else:
            fin = self.pilas.widget.height()
            inicio = int(altoNave)
            
        self.y = pilas.azar(inicio,fin)
                        
        self.hacer(self.pilas.comportamientos.Proyectil,
                   velocidad_maxima=5,
                   aceleracion=5,
                   angulo_de_movimiento = 0,                       
                   gravedad=0)
        self.agregar_habilidad(self.pilas.habilidades.EliminarseSiSaleDePantalla)
    
    @staticmethod
    def dameElChori(pilas):
        if (Chori.CHORI is None or Chori.CHORI._vivo == False):
            Chori.CHORI = Chori(pilas)
            
        return Chori.CHORI
class SeAlejadeOtrosMauirs(pilasengine.habilidades.Habilidad):
    def __init__(self,pilas,*k,**kw):
        pilasengine.habilidades.Habilidad.__init__(self,pilas)
    
    def iniciar(self, receptor):
        pilasengine.habilidades.Habilidad.iniciar(self, receptor)
        self.receptor = receptor
    
    def actualizar(self):
        pilasengine.habilidades.Habilidad.actualizar(self)    
        self.receptor.actuaizar =  Macri.actualizar        
        
        