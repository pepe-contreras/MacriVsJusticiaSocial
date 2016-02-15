'''
Created on 8 de feb. de 2016

@author: Martin
'''
import pilasengine
from source.actoresMauri import *


pilas = pilasengine.iniciar(1024,768)
pilas.actores.vincular(Macri)
macris = pilas.actores.Macri() * pilas.azar(20, 50)
nave = pilas.actores.Nave()
macris.escala = 0.5
nave.definir_enemigos(macris)

pilas.fisica.gravedad_y = 0

macris.agregar_habilidad(pilas.habilidades.RebotarComoCaja)
pilas.fondos.Espacio()
nave.escala = 1.5
musica = pilas.musica.cargar('marcha.mp3')
musica.reproducir(True)
#nave._imagen= pilas.imagenes.cargar('pj.png')
pilas.ejecutar()
pilas.terminar()
