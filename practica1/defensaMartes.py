# Practica 1- Paradigmas de Programaccion 2025. Pargammon
# Practica realizada por:
# Mario San José de Prado, grupo T2 teoria y subgrupo X6 practicas
# Rodrigo Gil Hernáiz, grupo T2 teoria y subgrupo X6 practicas

from random import seed, randrange,choice

AZAR = 123  # Semilla del generador de números aleatorios

class Pargammon(object):
    def __init__(self, n=18, m=6, d=3, fichas=('\u263a', '\u263b')):
        
        self.N = n  # Número de columnas
        self.M = m  # Número de fichas por jugador
        self.D = d  # Número de dados
        self.FICHAS = fichas  # Caracteres de las fichas de cada jugador
        self.dados_str = {1: '\u2680', 2: '\u2681', 3: '\u2682', 4: '\u2683', 5: '\u2684', 6: '\u2685'} # Diccionario con la representacion de los dados
        self.jugadas = 1  # Contador de jugadas del tablero
        self.turnos = 0  # Turnos (jugador 1: 0, jugador 2: 1, jugador N: N-1)
        self.tablero = {}  # Tablero: {clave: letra de la columna, valor: lista de fichas}
        self.fichas_sacadas = {} #Diccionario que almacena el numero de fichas sacadas (clave: caracter de cada jugador, valor: numero de fichas)
        self.tipo_jugador =[] # Lista que almacena los tipos de jugadores, de cada jugador (Humano,maquina[T],maquina[L])
        self.seleccionar_jugadores() #Llamamos a seleccionar jugadores
        self.turbos = {}
        self.inicializar_tablero() #Llamamos a incializar tablero al instanciar la clase para que se genere el tablero 
        self.guardar_tablero=[] #Lista que almacena el estado de los tableros en cada jugada
        self.guardar_fichas_sacadas=[] #Lista que almacena el estado de las fichas sacadas en cada jugada
        self.guardar_dados=[] #Lista que almacena los dados de cada jugada
        self.guardar_turno=[] #Lista que almacena el turno del jugador en cada jugada
        self.deshacer = False #Bandera para verificar si se quiere deshacer la jugada
        self.uso_turbo = False

    def inicializar_tablero(self):
        """Inicializa el tablero con las fichas de cada jugador en sus columnas iniciales."""
        
        self.tablero = {chr(65 + i): [] for i in range(self.N + 1)} #Columna N+1 para fichas sacadas
        for i in range(len(self.FICHAS)):  
            self.tablero[chr(65 + i)] = [self.FICHAS[i]] * self.M
        
        
        self.fichas_sacadas = {ficha: 0 for ficha in self.FICHAS} #Contador de fichas sacadas por jugador
        self.turbos = {ficha: 2 for ficha in self.FICHAS}
        
    def __repr__(self)->str:    
        """Devuelve una representación visual del tablero y el estado de la partida.
            :return: La representacion visual"""
        
        # Calculamos la altura dinámica: el número máximo de fichas en columnas A..(A+N-1) (excluimos la columna N+1, que es donde se guardan las fichas sacadas).
        altura = max((len(self.tablero[chr(65 + i)]) for i in range(self.N)), default=1) # default =1, para que si la lista esta vacia imprimar por lo menos 1 fila
    
        tablero_str = f"JUGADA #{self.jugadas}\n"
        for fila in range(altura):  # Recorremos cada fila desde la superior (fila=0) hasta la inferior (fila=altura-1)
            for col in range(self.N): # No mostrar la columna N+1
                letra = chr(65 + col)
                fichas = self.tablero.get(letra, [])
                numero_fichas = len(fichas)
            
                # Calculamos el índice de ficha para mostrar en esta fila
                #    Cuando fila=altura-1 (abajo)
                #    indice = fila - (altura - numero_fichas)
                #    Si es negativo, significa que no hay ficha en esa fila.
                indice = fila - (altura - numero_fichas)
            
                if 0 <= indice < numero_fichas:
                    tablero_str += fichas[indice]+"|"
                else:
                    tablero_str += " |"
            tablero_str += "\n"
        tablero_str += " ".join([chr(65 + i) for i in range(self.N)]) + "\n"
        tablero_str += f"Turno de {self.FICHAS[self.turnos]}: "
        for dado in self.dados:
            tablero_str += f"{self.dados_str[dado]} "
        #tablero_str += f"\nFichas sacadas: {self.fichas_sacadas}" #Para ver las fichas que se van sacando por jugador
    
        return tablero_str
    
        #Tablero con una altura estatica (exactamente una altura de self.M fichas por si falla el de altura dinamica)
               
        #tablero = f"JUGADA #{self.jugadas}\n"
        #for fila in range(self.M):
        #    for col in range(self.N):  # No mostrar la columna N+1
        #        letra = chr(65 + col)
        #        fichas = self.tablero.get(letra, [])
        #        numero_fichas = len(fichas)
        #        if self.M - fila <= numero_fichas:
        #            tablero += fichas[fila - (self.M - numero_fichas)] + "|"
        #        else:
        #            tablero += " |"
        #    tablero += "\n"
        #tablero += " ".join([chr(65 + i) for i in range(self.N)]) + "\n"
        #tablero += f"Turno de {self.FICHAS[self.turnos]}: "
        #for dado in self.dados:
        #    tablero += f"{self.dados_str[dado]} "
        #tablero += f"\nFichas sacadas: {self.fichas_sacadas}" #Para ver las fichas que se van sacando por jugador
        #return tablero
        
    def cambiar_turno(self)->bool:
        """Cambia de turno y realiza una tirada de dados.
            :return: True si es fin de partida o False si no lo es"""
        
        fin = False # bandera para verificar el fin de partida
        if self.verificar_fin_partida(): # si hay fin de partida : fin = True
            fin = True
            
        if self.deshacer == False: # si no se ha deshecho la jugada,  lanzamos los dados y cambiamos turno
            self.dados = [randrange(6) + 1 for _ in range(self.D)] # lanzamos los dados
         
            if self.jugadas > 1: # si el numero de jugadas es >1 pasamos al siguiente jugador
                self.turnos = (self.turnos +1) % len(self.FICHAS)

        self.guardar_estado() #Guardamos el estado despues de la tirada de dados y del turno
        self.deshacer = False #Marcamos deshacer como False si era True
        self.uso_turbo = False
        
        
        return fin #Retornamos la bandera que verifica el fin de partida
    
    def guardar_estado(self):
        """Metodo que guarda el estado actual de la partida. 
            Este incluye el tablero, el turno actual, el numero de fichas sacadas y los dados"""
            
        self.guardar_tablero.append(self.copiar_tablero(self.tablero)) #Guardamos el tablero en la lista de tableros
        self.guardar_turno.append(self.turnos) #Guardamos el turno en la lista de turnos
        self.guardar_fichas_sacadas.append(self.guardar_sacadas()) #Guardamos las fichas sacadas en la lista de fichas sacadas
        self.guardar_dados.append(self.dados) #Guardamos los dados en la lista de dados
        
    def deshacer_jugada(self,num_jugadas):
        """Metodo que deshace el numero de jugadas dadas por parametro"""
        
        for i in range (num_jugadas): #Dado el numero de jugadas a deshacer, eliminamos las N ultimas posiciones de las listas
                self.guardar_fichas_sacadas.pop()
                self.guardar_tablero.pop()
                self.guardar_dados.pop()
                self.guardar_turno.pop()

        self.tablero=self.guardar_tablero[-1] #Retornamos el tablero actual
        self.dados=self.guardar_dados[-1] #Retornamos los dados actuales
        self.fichas_sacadas=self.guardar_fichas_sacadas[-1] #Retornamos las fichas sacadas actuales          
        self.turnos=self.guardar_turno[-1] #Retornamos el turno actual
        self.jugadas-=num_jugadas #Decrementamos el numero de jugadas al actual
         
    def guardar_sacadas(self)->dict:
        """Metodo que guarda el estado de las fichas sacadas de cada jugador"""
        
        fichas_sacadas = {} #Incializo una copia del diccionario
        
        for i in range(len(self.FICHAS)): #Copio en el diccionario copia cada una de sus claves con su correspondiente valor
            fichas_sacadas[self.FICHAS[i]] = self.fichas_sacadas[self.FICHAS[i]]
            
        return fichas_sacadas #Retornamos una copia del diccionario de las fichas sacadas 
    
    def jugar(self, txt_jugada: str)-> str |None:
        """Intenta realizar la jugada indicada.
            :return: None si la jugada es valida, o un str con el error"""
            
        if txt_jugada[0]=='*':
          # Si la jugada comienza por * se deshace la jugada
            num_jugada = len(txt_jugada)
            if num_jugada>=self.jugadas:
                return "No se pueden deshacer mas jugadas"
            
            self.deshacer_jugada(num_jugada)
            self.deshacer = True # Marcamos deshacer como True si se ha deshecho
        
            return None
        
        turbo = False
        if txt_jugada[-1] == '!':
            turbo = True
            txt_jugada = txt_jugada[:-1]

            jugador = self.FICHAS[self.turnos]
            if self.turbos[jugador] <= 0:
                return "No tiene turbo"

            self.uso_turbo = True
            if len(txt_jugada) != self.D:
                return f"ERROR J1: Debe indicar exactamente {self.D} movimientos."
                
        letras_no_aparece = []
        for letra in txt_jugada: #Almacenamos en una lista las letras que no aparecen en el tablero excepto la @
            if letra not in self.tablero and letra != '@':
                if letra not in letras_no_aparece:
                    letras_no_aparece.append(letra)
        
        if len(letras_no_aparece) >0: #Si existen letras que no aparecen en el tablero en la jugada introducida ERROR J2-M1 
            texto = ", ".join(letras_no_aparece[::-1]) #Imprimimos la lista de las letras que no aparecen desde el final
            return f"ERROR J2-M1: No existen columna(s) con estas letras: {texto}."
        
        
        jugadas_posibles = self.obtener_posibles() #Obtnemos una lista con las jugadas posibles
        if txt_jugada == '@'*self.D: #Si la jugada introducida es la jugada vacia (@@@) y hay alguna otra jugada posible ERROR J3
            if txt_jugada not in jugadas_posibles:
                return "ERROR J3: No puede perder turno, existen otras jugadas válidas." 
        
        # Copiamos el estado del tablero por si hay un error
        copia_tablero = self.copiar_tablero(self.tablero)
        
        for i, letra in enumerate(txt_jugada):
            if letra != '@': # si la letra no es @ pasamos al siguiente dado
                dado = self.dados[i]
                if turbo:
                    dado = dado*2
                error = self.mover_ficha(letra, dado)
                if error: # si el error no es None retornamos el mensaje de error y restauramos el tablero
                    self.tablero = copia_tablero
                    return error
                
        self.jugadas += 1 #Aumentamos el numero de jugadas
        if turbo:
            self.turbos[self.FICHAS[self.turnos]] -=1
            
        return None #Si la jugada ha sido valida retornamos None

    def mover_ficha(self, origen, dado) -> str |None:
        """Mueve una ficha de la columna de origen a la columna de destino.
            :return : un mensaje de error si la ficha no se ha podido mover
            especificando el porque o None si la ficha se movio exitosamente"""
            
        error = self.verificar_movimiento_valido(origen, dado) # Comprobamos primero si el movimiento es valido
        if error: #Si no es valido retornamos el error
            return error
        
        destino = chr(ord(origen) + dado)#Calculamos la letra de destino
            
        if ord(destino) == 65 + self.N: #Si la letra de destino es la N+1 sacamos la ficha
            self.sacar_ficha(origen)
            return None

        columna_origen = self.tablero.get(origen,[]) #Obtenemos la columna de origen 
        columna_destino = self.tablero.get(destino, []) #Obtenemos la columna de destino

        if columna_destino and columna_destino[-1] != self.FICHAS[self.turnos]: 
        #si la columna de destino no esta vacia y el ultimo elemento de la lista es distinto del jugador actual
            if len(columna_destino) > 1: #si tiene mas de una ficha ERROR J2-M4
                return f"ERROR J2-M4: Movimiento {origen} -> {destino}, columna destino tiene más de una ficha contraria."
            else: # Si solo tiene 1 ficha se captura
                # Captura la ficha contraria
                ficha_contraria = columna_destino.pop() # se obtiene la ultima ficha y se captura
                ficha = columna_origen.pop()
                self.mover_ficha_capturada(ficha_contraria)
                self.tablero[destino].append(ficha)
                return None

        # Movemos la ficha del jugador actual asegurando que la columna de destino o esta vacia o pertenece al jugador
        ficha = columna_origen.pop() #Sacamos la ficha del jugador de la columna de origen
        self.tablero[destino].append(ficha) #Almacenamos la ficha del jugador en la columna de destino 
        return None #Retornamos None cuando la jugada es valida

    def verificar_movimiento_valido(self, origen, dado) -> str |None:
        """Verifica si el movimiento es válido.
            :return : Retorna un mensaje de error o None si el movimiento es valido"""
        
        columna_origen = self.tablero[origen] #sacamos la columna de origen
        if not columna_origen or columna_origen[-1] != self.FICHAS[self.turnos]: 
            #si la columna de origen no tiene fichas o la ultima ficha de la columna no es la del jugador ERROR J2-M2
            return f"ERROR J2-M2: Columna de origen {origen} no tiene fichas del jugador."
        
        destino = ord(origen) + dado #sacamos el valor ascii de la letra de destino
            
        if destino > 65 + self.N: # si el valor numerico es mayor que el de la letra N+1, ERROR J2-M3
            return f"ERROR J2-M3: Movimiento {origen} -> {chr(destino)}, columna de destino fuera de rango."

        return None #Si no hay error retornamos None

    def sacar_ficha(self, origen):
        """Saca una ficha del tablero. Y aumenta el contador de fichas sacadas de cada jugador"""
        
        ficha = self.tablero[origen].pop() #sacamos la ultima ficha de la columna
        self.tablero[chr(65+self.N)].append(ficha) #Almacenamos la ficha en la columna N+1
        self.fichas_sacadas[self.FICHAS[self.turnos]] += 1 # aumentamos el contador de fichas sacadas del jugador

    def verificar_fin_partida(self) ->bool:
        """Verifica si el jugador actual ha ganado la partida (sacado todas sus fichas).
            :return : si la partida ha finalizado"""
            
        #si el numero de fichas sacadas del jugador actual es igual al numero de fichas de la partida, se acaba la partida
        return self.fichas_sacadas[self.FICHAS[self.turnos]] == self.M 

    def mover_ficha_capturada(self, ficha):
        """Mueve una ficha capturada a la primera columna vacía o que contenga fichas del mismo jugador."""
        
        for col in range(self.N): # recorre cada columna del tablero y obtiene su columna
            letra = chr(65 + col) 
            columna = self.tablero[letra]
            if not columna or columna[-1] == ficha: #si la columna esta vacia o la primera columna tiene una ficha del mismo jugador
                self.tablero[letra].append(ficha) # almacenamos la ficha y salimos
                break
            
    def copiar_tablero(self,tablero)->dict:
        """Metodo que copia el tablero que se pase por argumento
            :return: Una copia del tablero"""
            
        copia = {} #Incializamos un diccionario copia
        for i in range(len(tablero)): # recorremos el tablero
            letra = chr(65+i) #sacamos la letra de cada columna e incializamos una lista vacia por columna
            lista = []
            
            for ficha in tablero[letra]: # metemos cada ficha de cada columna en la lista
                lista.append(ficha)
            
            copia[letra] = lista # asignamos cada lista a cada letra, para conseguir una copia del tablero
            
        return copia #Devolvemos una copia del tablero
    
    def jugadas_posibles(self, tablero, dados, jugada_actual='')->list:
        """
        Devuelve una lista con todas las jugadas posibles dado un tablero y los dados.
        Las jugadas se generan de manera secuencial:
            1. Primero todas las jugadas que comienzan con '@'.
            2. Luego todas las jugadas que comienzan con un movimiento válido.
        :return: Una lista con las jugadas posibles
        """
    
        #Caso base: Si ya hemos usado todos los dados (la longitud de la jugada es igual a self.D)
        if len(jugada_actual) == self.D:
            return [jugada_actual]  # Almacenamos la jugada en una lista

        posibles = []  # Lista para almacenar las jugadas posibles

        # 1: No mover una ficha con el dado actual (usar '@')
        nuevas_jugadas = self.jugadas_posibles(tablero, dados[1:], jugada_actual + '@') # sumamos un @ para obtener todos las combinaciones 
        posibles.extend(nuevas_jugadas) #Almacenamos la jugada completada en la lista de posibles
                                                                                                                                                                                                                                                    
        # 2: Mover una ficha con el dado actual (si es posible)
        for letra in tablero: 
            columna = tablero[letra] # para cada letra del tablero obtenemos su columna de fichas
            if columna and columna[-1] == self.FICHAS[self.turnos]:  # Si la columna tiene una ficha del jugador actual
                dado = dados[0] #Obtenemos el primer dado
                
                destino = chr(ord(letra) + dado) #Obtenemos la casilla de destino  

                if destino <= chr(65 + self.N):  # Si el movimiento está dentro del tablero (es menor 65+self.N)
                    
                    #comprobamos que se cumplan las reglas al mover
                    #1- la columna de destino esta vacia
                    #2- la columna de destino tiene solo una unica ficha de un jugador rival
                    #3- la columna de destino tiene fichas del jugador actual
                    #4- la columna de destino es exactamente la ultima(N+1) ya que la ultima almacena todo tipo de fichas sin restricciones
                    
                    columna_destino = tablero.get(destino,[]) # Sacamos la columna de fichas de destino
                    if len(columna_destino) == 0 or \
                        (len(columna_destino) == 1 and columna_destino[-1] != self.FICHAS[self.turnos]) or \
                        (columna_destino[-1] == self.FICHAS[self.turnos])or \
                        (destino == chr(65+self.N)): 
                        
                            
                        # Copiamos el tablero para simular el movimiento
                        nuevo_tablero = self.copiar_tablero(tablero)
                        # Realizamos el movimiento de la ficha 
                    
                        nueva_ficha = nuevo_tablero[letra].pop()  # Sacamos la ficha del tablero
                        nuevo_tablero[destino].append(nueva_ficha)  # Ponemos la ficha en la nueva columna

                        # Llamamos recursivamente para hacer la siguiente jugada con los dados restantes
                        nuevas_jugadas = self.jugadas_posibles(nuevo_tablero, dados[1:], jugada_actual + letra)
                        posibles.extend(nuevas_jugadas) #Almacenamos la jugada completada en la lista de posibles
            
        if len(posibles) > 1:
            #Si la longitud de la lista de jugadas posibles es >1, quitamos la jugada vacia @@@
            posibles = [jugada for jugada in posibles if jugada != '@' * self.D]
        
        # Si no hay ninguna jugada posible, permitimos la jugada de todo '@'
        if not posibles and len(jugada_actual) == 0:
            return ['@' * self.D]

        return posibles  # Devolvemos la lista de jugadas posibles
    
    def obtener_posibles(self):
        normales = self.jugadas_posibles(self.tablero,self.dados)
        resultado = list(normales)
        
        if self.turbos[self.FICHAS[self.turnos]] >0:
            turbo_dados = [d*2 for d in self.dados]
            turbo_jugadas = self.jugadas_posibles(self.tablero,turbo_dados)
            
            resultado.extend(jugada +'!' for jugada in turbo_jugadas)
    
        return resultado
    
    def seleccionar_jugadores(self):
        """Metodo que permite seleccionar a los jugadores que van a comenzar la partida"""
        
        jugadores = ['H','T','L'] #Lista con los posibles jugadores
        for i in range(len(self.FICHAS)):
           while True: #Para cada jugador solicitamos el tipo de jugador
                jugador = input(f"Jugador {self.FICHAS[i]} es [H]umano, Máquina [T]onta o Máquina [L]ista: ").strip().upper()
                if(jugador in jugadores): #Si es correcto se almacena en la lista de tipo_jugador y se pasa al siguiente
                    self.tipo_jugador.append(jugador)
                    break

    def jugada_maquina_tonta(self)->str:
        """Método que elige una jugada aleatoria para la máquina tonta
            :return: Una jugada aleatoria de las posibles"""
            
        lista_jugadas = self.obtener_posibles() #Carga la lista de jugadas posibles del jugador actual
        mejores_jugadas = self.mejor_jugada() #Obtenemos los valores de cada jugada
        
        #ordenamos las listas de jugadas y sus valores de mayor a menor puntuacion
        lista_jugadas,mejores_jugadas = self.ordenar_jugadas(lista_jugadas,mejores_jugadas)
        
        jugada = choice(lista_jugadas)
        return jugada # Elige una jugada aleatoria con choice
    
    def jugada_maquina_lista(self)->str:
        """Método que elige la mejor jugada posible para la máquina lista
            :return: La mejor jugada de las posibles"""
        
        jugadas_posibles = self.obtener_posibles() #Carga la lista de jugadas posibles del jugador actual
        mejores_jugadas = self.mejor_jugada() #Carga la lista con los valores de cada jugada posible
        
        #ordenamos las listas de jugadas y sus valores de mayor a menor puntuacion
        jugadas_posibles, mejores_jugadas = self.ordenar_jugadas(jugadas_posibles,mejores_jugadas)
             
        return jugadas_posibles[0] #Devolvemos la mejor jugada (la primera)
               
    def calcular_puntuacion(self, jugador,tablero)->int:
        """Calcula la puntuación de un jugador en el estado actual del tablero, dado el jugador y el tablero.
            :return: La puntuacion del jugador"""
        
        puntuacion = 0
        for columna in tablero: #Recorre todas las columnas del tablero
            columna_fichas = tablero[columna]
            for i, ficha in enumerate(columna_fichas):
                if ficha == jugador: #Para cada ficha de la columna comprueba que sea del jugador 
                    # Si está apilada, factor 2, si está sola, factor 1, si está fuera del tablero, factor 3
                    factor = 1 if len(columna_fichas) == 1 else 2
                    # Si la ficha está fuera del tablero
                    if columna == chr(65 + self.N):  # Si está fuera del tablero
                        factor = 3
                        posicion = self.N + 1  # Fichas fuera del tablero tienen posición N+1
                    else:
                        # La posición se calcula usando el índice 1-based (A =1, B =2) de la columna
                        posicion = ord(columna) - 64  # Sacamos el valor de la columna y le restamos 64 (uno menos que el valor de 'A')
                    # La puntuación es: factor * posición de la columna
                    puntuacion += factor * posicion
        return puntuacion #Devolvemos la puntuacion 

    def mejor_jugada(self)->list:
        """Calcula la mejor jugada según la diferencia de puntuación entre el jugador actual y los demás jugadores.
            :return: Una lista con los valores de cada jugada posible segun el algoritmo de la practica """
            
        mejores_jugadas = [] #Utilizamos una lista para almacenar los valores de cada jugada 

        # Listamos las jugadas posibles
        lista_jugadas = self.obtener_posibles()

        for jugada in lista_jugadas: #Para cada jugada de la lista de jugadas posibles
            turbo = False
            if jugada[-1] == '!':
                turbo = True
                jugada = jugada[:-1]
            # Simulamos la jugada en el tablero
            nuevo_tablero = self.copiar_tablero(self.tablero) #Para simular se copia el tablero para que no afecte al del juego en cuestión
            for i, letra in enumerate(jugada):
                if letra != '@':  # Solo movemos si no es '@'
                    if turbo:
                        dado = self.dados[i]*2
                    else:
                        dado = self.dados[i]
                         
                    columna_origen = nuevo_tablero.get(letra,[]) #A partir de aqui es la funcionalidad del metodo mover_ficha pero aplicada a la simulacion
                    destino = chr(ord(letra)+dado)
                    columna_destino = nuevo_tablero.get(destino,[])
                    if columna_destino and columna_destino[-1] != self.FICHAS[self.turnos]: 
                    #si la columna de destino no esta vacia y el ultimo elemento de la lista es distinto
                        if len(columna_destino) == 1: #si tiene mas de una ficha error M4
                            # Captura la ficha contraria
                            ficha_contraria = columna_destino.pop() # se obtiene la ultima ficha y se captura
                            for col in range(self.N): # lo mismo que para capturar una ficha pero aplicado a la simulacion del tablero
                                pos = chr(65+col)
                                columna = nuevo_tablero[pos]
                                if not columna or columna[-1] == ficha_contraria:
                                    nuevo_tablero[pos].append(ficha_contraria)
                                    break

                    if len(columna_origen)>0:# Movemos la ficha del jugador actual
                        ficha = columna_origen.pop()
                        nuevo_tablero[destino].append(ficha)   
            
            # Calculamos la puntuación del jugador actual y de los otros jugadores después de la jugada
            puntuacion_jugador_actual = self.calcular_puntuacion(self.FICHAS[self.turnos],nuevo_tablero)
            puntuacion_otros_jugadores = 0
            for i, jugador in enumerate(self.FICHAS):
                if jugador != self.FICHAS[self.turnos]:
                    puntuacion_otros_jugadores += self.calcular_puntuacion(jugador,nuevo_tablero)
            
            # Calculamos la diferencia de puntuación (la mayor, mejor jugada)
            diferencia = puntuacion_jugador_actual - puntuacion_otros_jugadores
            
            #Esto es para depurar y mostrar por pantalla los valores de cada jugada 
            #print(f"Jugada: {jugada} | Diferencia: {diferencia} | Puntuación jugador actual: {puntuacion_jugador_actual} | Puntuación otros jugadores: {puntuacion_otros_jugadores}")
            
            mejores_jugadas.append(diferencia) #Almacenamos el valor en la lista de mejores jugadas
            
        return mejores_jugadas  # Devolvemos las mejores jugadas
    
    def ordenar_jugadas(self,jugadas,valores):
        """ Metodo que ordena las jugadas y sus respectivos valores de mayor a menor utilizando 
            el alogoritmo de ordenacion por burbuja (bubble sort)
            :return: lista de jugadas y lista de valores ordenadas"""
            
        n = len(jugadas)#obtenemos el numero de elementos de la lista
        for i in range(n): #iteramos sobre ellos
            for j in range(0,(n-1)-i):
                if(valores[j] < valores[j+1]): #si el valor actual es menor que el siguiente se intercambian
                    temp_valores= valores[j]
                    temp_jugadas = jugadas[j]
                    jugadas[j] = jugadas[j+1]
                    valores[j] = valores[j+1]
                    valores[j+1] = temp_valores
                    jugadas[j+1] = temp_jugadas
        
        #para imprimir valor y jugada ordenados     
        #for i,jugada in enumerate(jugadas):
        #    print(f"{valores[i]}|{jugada}")
            
        #retornamos la lista de jugadas y la lista de los valores de las jugadas
        return jugadas,valores
                
                          
def main():
    seed(AZAR)
    print("*** PARGAMMON ***")
    params = map(int, input("Numero de columnas, fichas y dados = ").split())
    #fichas='\u263a\u263bx'     #fichas para 3 jugadores (juego = Pargammon(*params,fichas=fichas))
    juego = Pargammon(*params) 
    while (juego.cambiar_turno() == False): #bucle principal del juego
        #print(juego.obtener_posibles())
        print(juego)# imprimimos el tablero
         
        # Jugada de la máquina tonta
        if juego.tipo_jugador[juego.turnos] == 'T':  # Si es la máquina tonta
            jugada = juego.jugada_maquina_tonta() #Obtenemos una jugada al azar 
            print(f"Jugada: {jugada}") #La mostramos por pantalla
            print()
            juego.jugar(jugada) #Llamamos a jugar con esa jugada (si esta bien hecho la jugada será siempre valida)
            
        # Jugada de la maquina lista    
        elif juego.tipo_jugador[juego.turnos] == 'L':  # Si es la máquina lista
            jugada = juego.jugada_maquina_lista() #Obtenemos la mejor jugada
            print(f"Jugada: {jugada}") #La mostramos por pantalla
            print()
            juego.jugar(jugada) #Llamamos a jugar con esa jugada (si esta bien hecho la jugada será siempre valida)
            
        else: #Jugada del humano
            while True:
                jugada = input(f"Jugada: ").strip().upper()  # Pedir jugada
                resultado = juego.jugar(jugada)  # Almacenar el resultado de la jugada
                if resultado is None:  # Si es válida, salimos del bucle
                    print()
                    break
                else:  # Si no es válida, imprimimos el error y seguimos pidiendo una jugada válida
                    print(resultado)
                    
    print(f"Han ganado los {juego.FICHAS[juego.turnos-1]}!")  # Si hemos acabado el juego imprimimos el ganador
    
if __name__ == "__main__":
    main()
