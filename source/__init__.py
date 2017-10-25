'''
Created on 8 de feb. de 2016

@author: Martin
'''
import pilasengine
from source.actoresMauri import *
from pilasengine.habilidades import *

sys.path.insert(0, "../data")
print(sys.path)
pilas = pilasengine.iniciar(1024,768,'Macri Vs Justicia Social')

pilas.actores.vincular(Macri)
pilas.actores.vincular(NaveJusticialista)
pilas.actores.vincular(Chori)



nave = pilas.actores.NaveJusticialista()
macris = pilas.actores.Macri() * pilas.azar(20,50)
macris.agregarNave(nave)
nave.definir_enemigos(macris)
pilas.fisica.set_gravedad_y(0)


pilas.fondos.Espacio()
musica = pilas.musica.cargar('marcha.mp3')
print(NaveJusticialista.NAVE.imagen.ruta_original)
musica.reproducir(True)

pilas.ejecutar()