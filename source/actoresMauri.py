'''
Created on 8 de feb. de 2016

@author: Martin
'''
import pilasengine
from pilasengine.actores import * 
from pilasengine.comportamientos import proyectil
from pilasengine.habilidades import seguir_a_otro_actor, puede_explotar_con_humo
import math
import sys
from time import *

class Macri(actor.Actor):
    '''
    classdocs
    '''
    maurisEnJuego = []
        
    def __mul__(self,cant):
        res = pilasengine.actores.Actor.__mul__(self,cant)
        for macri in res:
            macri._cir.x,macri._cir.y = macri.x ,macri.y
        return res
    
    def __init__(self,pilas,*k,**kw):
        '''
        Constructor
        '''
        self._cir = pilas.fisica.Circulo(0,0,60)
        Macri.maurisEnJuego.append(self)
        self.golpeado = False
        self.pilas = pilas
        pilasengine.actores.Actor.__init__(self,pilas)
        self.imagen = pilas.imagenes.cargar('macri.png')
        self.radio_de_colision = 40
        self._cir.radio = self.radio_de_colision
        self._cir.set_radius(self.radio_de_colision)
        self.naveEnemiga = None
        self.escala= 0.75
        self.agregar_habilidad(self.pilas.habilidades.SeMantieneEnPantalla)
#        self.agregar_habilidad(SeAlejadeOtrosMauirs)
        self.imitar(self._cir)
    
       
    def agregarNave(self,nave):
        self.naveEnemiga = nave
  
    def eliminar(self):
        self.naveEnemiga.puntaje = self.naveEnemiga.puntaje + 1
        if self.golpeado:
            super.eliminar(self)
        else:
            sonido = self.pilas.sonidos.cargar('audio/basta.wav')
            sonido.reproducir()
            angulo = self.pilas.azar(0,360)
            vel = self.pilas.azar(1,5)
            if self.x > self.naveEnemiga.x:
                vel = -vel
            
            if (not self.naveEnemiga is None):
                angulo = definir_angulo(self,self.naveEnemiga)
            self.imagen = self.pilas.imagenes.cargar('macribobo.png')
            self.aprender(pilasengine.habilidades.seguir_a_otro_actor.SeguirAOtroActor,NaveJusticialista.NAVE,velocidad=0.5,inteligencia=0)
            # self.hacer(self.pilas.comportamientos.Proyectil,
                   # velocidad_maxima=vel,
                   # aceleracion=5,
                   # angulo_de_movimiento = angulo,                        
                   # gravedad=0)
            self.golpeado = True
            self.agregar_habilidad(PuedeExplotarConHumoySonido)
            
def definir_angulo(actorOrigen,actorDestino):
    dx = distancia(actorOrigen.x,actorDestino.x)
    dy = distancia(actorOrigen.y,actorDestino.y)
    if dx != 0:
        return math.degrees(math.atan(dy/dx))
    return 90

def distancia(numero1,numero2):
    return numero2 - numero1

            
class NaveJusticialista(pilasengine.actores.Nave):
    '''
    classdocs
    '''
    MAX_POWER = 5
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
        self.chocadoTick = 100
   
        pilasengine.actores.Nave.__init__(self,pilas)
       
#        self.aprender(pilas.habilidades.SeMantieneEnPantalla)
        self._habilidades[1].cuando_dispara = self.disparar
        
        self.aprender(pilas.habilidades.SiempreEnElCentro)
        self.figura_de_colision = pilas.fisica.Rectangulo(0, 0, 80, 120, sensor=True, dinamica=False)
    
    def sumarPuntos(self):
        self.puntaje = self.puntaje + 1
        
    def disparar(self):
        if self.poder > 0:
            self.poder = self.poder - 1
            
    def hacer_explotar_al_enemigo(self, mi_disparo, el_enemigo):
        if mi_disparo.transparencia == 0:
            pilasengine.actores.Nave.hacer_explotar_al_enemigo(self, mi_disparo, el_enemigo)
                     
    def definir_enemigos(self, grupo, cuando_elimina_enemigo=None):
        self.cipayos = grupo
        for cipayo in grupo:
            self.pilas.colisiones.agregar(self, cipayo, cuando_colisiona)
        pilasengine.actores.Nave.definir_enemigos(self, grupo, cuando_elimina_enemigo=cuando_elimina_enemigo)

    def quitar_vida(self):
        self.vida = self.vida - 1
        self.chocadoTick = 0
        self.imagen = self.pilas.imagenes.cargar_grilla("naveEnllamas.png",2)
        if self.vida <= 0:
            musica = self.pilas.musica.cargar('audio//gameover.mp3')
            musica.reproducir()
            for cipayo in self.cipayos:
                cipayo.eliminar()
                
            self.texto.texto = "GAME OVER, NEOLIBERALISM WINS!"
            self.texto.x=0
            self.texto.y=0
            self.texto.rotacion = [0,365]
            self.eliminar()
    
    def actualizar(self):
        self.texto.texto = "Vida: " + self.vida.__str__()  + " Poder: " +  self.poder.__str__() + " Puntaje: "    + self.puntaje.__str__()
           
        if self.chocadoTick < 100:
            self.chocadoTick+=1
            if self.chocado == 98:
                self.imagen = self.pilas.imagenes.cargar_grilla("nave.png",2)
            
        self.chocado = False
        if    time() - self.tiempoUltimoChori > 5:
            self.pilas.colisiones.agregar(self, Chori.dameElChori(self.pilas), agarrar_chori)      
            self.tiempoUltimoChori = time()
                
        if self.poder > 0:
            self.municion = pilasengine.actores.Misil
            try:
                self._habilidades[1]._municion = pilasengine.actores.Misil
            except:
                pass
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
        
    def eliminar(self):
        musica = self.pilas.musica.cargar('audio/gameover.mp3')
        musica.reproducir()
        super.eliminar()

        

class MisilInvisible(pilasengine.actores.Misil):
    def __init__(self, pilas):
        pilasengine.actores.Misil.__init__(self,pilas)
        self.transparencia = 100    
        
def cuando_colisiona(nave, macri):
    if macri.golpeado:
        nave.quitar_vida()
        
def agarrar_chori(nave, chori):
    nave.poder = NaveJusticialista.RECHARG_CHORIPAN + nave.poder
    sonido = nave.pilas.sonidos.cargar('audio/evita.wav')
    sonido.reproducir()
    chori.eliminar()
class PuedeExplotarConHumoySonido(pilasengine.habilidades.puede_explotar_con_humo.PuedeExplotarConHumo):
    def eliminar_y_explotar(self):
        self.pilas.sonidos.cargar('audio/merindo.wav').reproducir()
        explosion = self.crear_explosion()
        explosion.x = self.receptor.x
        explosion.y = self.receptor.y
        pilasengine.actores.Actor.eliminar(self.receptor)

class Chori(pilasengine.actores.Actor):
    CHORI = None
    
    def __init__(self,pilas):
        pilasengine.actores.Actor.__init__(self, pilas)
        self.imagen = "chori.png"
        self.escala = 0.5
      
        self.radio_de_colision = 50
        self.x = - self.pilas.widget.width()/2 
        fin=self.pilas.widget.height()/2 - 50
        inicio = - self.pilas.widget.height()/2 + 50
        self.y = pilas.azar(inicio,fin)
                        
        self.hacer(pilasengine.comportamientos.proyectil.Proyectil,
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
        self.tiempo= time()
    
    def iniciar(self, receptor):
        pilasengine.habilidades.Habilidad.iniciar(self, receptor)
        self.receptor = receptor
    
    def actualizar(self):
        pilasengine.habilidades.Habilidad.actualizar(self)
