""" Paradigmas de Programación - Curso 2024/25
    Solución de la primera práctica

    Autor: César Vaca Rodríguez
"""

from random import seed, randrange, choice

AZAR = 75
DADOS = "⚀⚁⚂⚃⚄⚅"
ORDA = ord('A')


class JugPtos(object):
    """ Clase auxiliar para almacenar una jugada y su puntuación
        La jugada se almacena como una lista de enteros (los índices de columnas)
        y como un string (str_jugada)
    """
    def __init__(self, jugada: [int], ptos: int):
        self.jugada = jugada
        self.str_jugada = "".join(chr(ORDA+i) for i in self.jugada)
        self.ptos = ptos

    def __repr__(self):
        return f"{self.ptos}|{self.str_jugada}"

    # Comparación entre jugadas basada en puntuación

    def __eq__(self, other):
        return self.ptos == other.ptos

    def __lt__(self, other):
        return self.ptos < other.ptos

    def __gt__(self, other):
        return self.ptos > other.ptos

    def __le__(self, other):
        return self.ptos <= other.ptos

    def __ge__(self, other):
        return self.ptos >= other.ptos


class Columna(object):
    """ Clase auxiliar para representar una columna.
        Almacena su índice, numero de fichas y el indice del jugador (-1 si está vacía)
        Implementamos callbacks para que pueda "avisar" a otras
        entidades de cualquier cambio en el número de fichas.
        El callback debe ser una función o método con el siguiente esquema:
        - func(columna: Columna)
        Usamos getters y setters para el número de fichas y el jugador (el índice se
        supone que es invariable)
    """

    def __init__(self, ind, num=0, jug=-1, callback=None):
        self.ind = ind
        self.jug = jug
        self._num = num
        self.callback = callback
        self.callback_activos = True

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, value):
        self._num = value
        if self.callback_activos and self.callback is not None:
            self.callback(self)

    def decrementa(self):
        """ Elimina una ficha de la columna """
        if self.num == 0:
            raise Exception("Error: Quitar de columna vacía.")
        self.num -= 1
        if self.num == 0:
            self.jug = -1

    @property
    def valor(self):
        """ Devuelve el valor de puntuación de la columna """
        return self.ind+1 if self._num == 1 else 2*(self.ind+1)*self._num


class Pargammon(object):
    """ Implementación de todos los bloques, con cualquier número de jugadores.
        Para representar el tablero se utiliza una lista de objetos de clase columna,
        que almacenan el número de fichas y el indice (0-based) del jugador (-1 si no hay fichas en esa columna)
        La información de deshacer consiste en tuplas, una por cada modificación (asignación) realizada a alguna
        columna. Cada tupla tiene la información del índice de la columna y su número de fichas e índice del
        jugador anterior. Como pueden existir varias modificaciones por movimiento, se introducen tuplas especiales
        para marcar el principio de una jugada y el principio de un movimiento.
    """

    # Constantes para identificar acciones para deshacer
    U_MARCA_JUG = -2  # Marca de principio de jugada. La tupla incluye los dados.
    U_MARCA_MOV = -1  # Marca de principio de movimiento
    U_ASIGNAR = 0     # La tupla incluye la columna y su número y jugador anterior

    def __init__(self, n=18, m=6, d=3, fichas="\u263a\u263b"):
        self.N = n              # Número de columnas
        self.M = m              # Número inicial de fichas
        self.D = d              # Número de dados
        self.FICHAS = fichas
        self.J = len(fichas)    # Número de jugadores
        # Callbacks de movimientos
        
        self.on_mover = None
        self.on_capturar = None
        self.on_sacar = None
        self.callbacks_activos = True

        # Tablero (lista de Columna)
        self.tab = [self.crea_columna(i, m, i) for i in range(self.J)] + \
                   [self.crea_columna(i) for i in range(self.J, n)]
        self.numj = 0     # Número de jugadas realizadas
        self.fin = False  # Marca de final de partida
        self.turno = -1   # Indice [0..J-1] del jugador que tiene el turno
        self.dados = []   # Tirada del turno actual
        self.jugs = []    # Jugadas posibles para el turno actual
        self.undo = []    # Pila de tuplas con los datos para deshacer movimientos

        # String con las letras de las columnas
        # También se podría haber calculado asi (pero entonces se entendería mejor):
        # self.cols = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:n+1]
        self.cols = ''.join(chr(ORDA - 1 + i) for i in range(n+1))
        self.inicializar()

    def inicializar(self):
        """ Para dar la oportunidad de añadir acciones post-creación en clases que hereden """
        self.cambiar_turno()

    def crea_columna(self, *args, **kwargs) -> Columna:
        """ Para dar la oportunidad de usar clases que deriven de Columna """
        return Columna(*args, **kwargs)

    def __getitem__(self, key: int) -> Columna:
        """ Para acceder a la columna i-esima """
        return self.tab[key]

    def __iter__(self):
        """ Para recorrer las columnas - Usamos un generador (corutina) """
        for col in self.tab:
            yield col

    def _ficha(self, fil: int, col: int) -> str:
        """ Caracter a mostrar en la fila y columna del rectángulo de dibujo del tablero """
        c = self.tab[col]
        return ' ' if c.jug == -1 or c.num < fil else self.FICHAS[c.jug]

    def __repr__(self):
        max_alt = max(map(lambda c: c.num, self.tab))
        return f'\nJUGADA #{self.numj}\n' + \
            '\n'.join('│'.join(self._ficha(f, c) for c in range(self.N)) for f in range(max_alt, 0, -1)) + \
            '\n' + ' '.join(self.cols[1:]) + f"\nTurno de {self.FICHAS[self.turno]}: " + \
            ' '.join(DADOS[i - 1] for i in self.dados)  # + \
#            '\nJugadas: ' + ','.join(map(repr, self.jugs))

    def fin_partida(self) -> bool:
        """ Por si se quiere comprobar fin de partida tras cada movimiento """
        return all(col.jug != self.turno for col in self.tab)

    def cambiar_turno(self) -> bool:
        """ Cambia de turno, hace una nueva tirada de dados y comprueba final de partida """
        if self.fin_partida():
            # Jugador actual se ha quedado sin fichas -> fin de partida
            return True
        self.numj += 1
        self.turno = (self.turno + 1) % self.J
        self.dados = [randrange(6) + 1 for _ in range(self.D)]
        self.analizar()
        return False

    def haz_movim(self, col1: int, desp: int) -> None | str:
        """ Intenta mover una ficha desde la columna col1 a la columna col1 + desp.  col1 == -1 omite el movimiento.
        :return: None si el movimiento es válido, mensaje de error si no lo es.
        """
        # Comprobar caso de omitir uso de dado
        if col1 == -1:
            self.undo.append((self.U_MARCA_MOV, None, None, None))
            return None
        c1 = self.tab[col1]
        # Comprobar que la columna tiene fichas del jugador
        if c1.jug != self.turno:
            return f"ERROR J2-M2: Columna de origen {chr(col1+ORDA)} no tiene fichas del jugador."
        col2 = col1 + desp
        # Comprobar que la columna destino está en el rango
        # Presciencia: Poner las condiciones más generales posibles (col2 < 0)
        if col2 > self.N or col2 < 0:
            return f"ERROR J2-M3: Movimiento {chr(col1+ORDA)} -> {chr(col2+ORDA)}, columna destino fuera de rango."
        if col2 == self.N:
            # Sacar ficha
            if self.callbacks_activos and self.on_sacar is not None:
                self.on_sacar(c1.ind)
            self.undo.append((self.U_MARCA_MOV, None, None, None))
            self.undo.append((self.U_ASIGNAR, c1, c1.num, c1.jug))
            c1.decrementa()
            return None
        c2 = self.tab[col2]
        if c2.jug == -1 or c2.jug == self.turno:
            # Mover a columna vacía o con fichas del jugador
            if self.callbacks_activos and self.on_mover is not None:
                self.on_mover(c1.ind, c2.ind)
            self.undo.append((self.U_MARCA_MOV, None, None, None))
            self.undo.append((self.U_ASIGNAR, c1, c1.num, c1.jug))
            c1.decrementa()
            self.undo.append((self.U_ASIGNAR, c2, c2.num, c2.jug))
            c2.num += 1
            c2.jug = self.turno
            return None
        if c2.num == 1:
            # Capturar ficha de otro jugador
            otro = c2.jug
            # Buscar primera columna compatible
            c3 = next(c for c in self.tab if c != c2 and (c.jug == -1 or c.jug == otro or (c == c1 and c1.num == 1)))
            if self.callbacks_activos and self.on_capturar is not None:
                self.on_capturar(c1.ind, c2.ind, c3.ind)
            self.undo.append((self.U_MARCA_MOV, None, None, None))
            self.undo.append((self.U_ASIGNAR, c1, c1.num, c1.jug))
            c1.decrementa()
            self.undo.append((self.U_ASIGNAR, c2, c2.num, c2.jug))
            c2.num = 1
            c2.jug = self.turno
            self.undo.append((self.U_ASIGNAR, c3, c3.num, c3.jug))
            c3.num += 1
            c3.jug = otro
            return None
        # Movimiento a columna con más de una ficha contraria
        return f"ERROR J2-M4: Movimiento {chr(col1+ORDA)} -> {chr(col2+ORDA)}, columna destino tiene más de una " \
               f"ficha contraria."

    def haz_jugada(self, jugada: [int]) -> None | str:
        """ Intenta realizar una jugada completa, especificada como lista de índices de columnas (o -1 para omitir)
        :return: None si la jugada es válida o el mensaje de error del primer movimiento no válido
        """
        res = None
        self.undo.append((self.U_MARCA_JUG, self.dados[:], None, None))
        for col, dado in zip(jugada, self.dados):
            res = self.haz_movim(col, dado)
            if res is not None:
                self.deshaz_jugada()
                break
        return res

    def jugar(self, txt_jugada: str) -> None | str:
        """ Intenta realizar la jugada indicada en el string txt_jugada
        :return: None si la jugada es válida, mensaje de error si no lo es
        """
        # Comprobar longitud jugada
        if len(txt_jugada) != self.D:
            return f"ERROR J1: Debe indicar exactamente {self.D} movimientos."
        cjug = set(txt_jugada)
        # Comprobación de jugada vacía
        if cjug == {'@'} and not (len(self.jugs) == 1 and self.jugs[0].jugada == [-1]*self.D):
            return f"ERROR J3: No puede perder turno, existen otras jugadas válidas."
        # Comprobación de columnas correctas
        col_err = cjug - set(self.cols)
        if col_err:
            return f"ERROR J2-M1: No existen columna(s) con estas letras: {', '.join(col_err)}."
        # Intentar realizar la jugada (la traducimos a índices)
        return self.haz_jugada([ord(ch)-ORDA for ch in txt_jugada])

    def deshaz_movim(self):
        """ Deshace un movimiento (necesario en generación recursiva de jugadas) """
        tipo, col, num, jug = self.undo.pop()
        while tipo != self.U_MARCA_MOV:
            if tipo == self.U_ASIGNAR:
                col.num = num
                col.jug = jug
            else:
                raise Exception("Fallo en deshaz_movim")
            tipo, col, num, jug = self.undo.pop()

    def deshaz_jugada(self):
        """ Deshace una jugada (solo actualiza el tablero, no el número de jugadas y turno) """
        # Cuidado: Pueden no existir D movimientos, si alguno era no válido
        tipo, col, num, jug = self.undo.pop()
        while tipo != self.U_MARCA_JUG:
            if tipo == self.U_ASIGNAR:
                col.num = num
                col.jug = jug
            tipo, col, num, jug = self.undo.pop()
        self.dados = col

    def deshacer(self, n: int):
        """ Deshace n jugadas, actualizando número de jugadas y turno """
        for _ in range(n):
            self.deshaz_jugada()
            self.numj -= 1
            self.turno -= 1
            if self.turno < 0:
                self.turno += self.J
        self.analizar()

    def info_jugadores(self) -> [(int, int)]:
        """ Devuelve una lista de tuplas (una por cada jugador), cada tupla tiene dos enteros:
            El número de fichas sacadas y la puntuación del jugador """
        # Número de fichas sacadas de cada jugador
        nums = [self.M - sum(c.num for c in self.tab if c.jug == j) for j in range(self.J)]
        # Puntos basados en posición para cada jugador
        ppos = (sum(c.valor for c in self.tab if c.jug == j) for j in range(self.J))
        # Puntos de cada jugador (añadimos puntuación fichas sacadas)
        return list(zip(nums, [p + 3*(self.N+1)*s for s, p in zip(nums, ppos)]))

    def valor_tablero(self) -> int:
        """ Devuelve el valor del tablero para el jugador actual """
        ptos = [p for _, p in self.info_jugadores()]
        return 2*ptos[self.turno] - sum(ptos)

    def cols_jugador(self, jugador: int):
        """ Generador que devuelve los índices de las columnas con fichas del jugador """
        yield -1  # Representa movimiento vacío (omitir el dado)
        for col in self.tab:
            if col.jug == jugador:
                yield col.ind

    def analizar_rec(self, jugada: [int], i: int):
        """ Añade a la lista jugadas aquellas jugadas válidas que se obtienen
            de examinar todos los valores posibles para el movimiento i-esimo
        """
        if i >= self.D:
            # Fin de recursividad, añadir jugada y puntuación a la lista (ojo, solo si la jugada no es vacía)
            if any(map(lambda m: m != -1, jugada)):
                # Se debe almacenar un clon de jugada: jugada[:]
                self.jugs.append(JugPtos(jugada[:], self.valor_tablero()))
            return
        # Recorrer los posibles valores de jug[i] (columnas que contengan fichas del jugador actual)
        for c in self.cols_jugador(self.turno):
            jugada[i] = c
            # Comprobar si es jugada válida
            if self.haz_movim(jugada[i], self.dados[i]) is None:
                # Explorar mas movimientos recursivamente
                self.analizar_rec(jugada, i+1)
                # Deshacer movimiento
                self.deshaz_movim()

    def analizar(self):
        """ Rellena self.jugs con los objetos JugPtos (jugada y puntuación) de las
            jugadas disponibles para el jugador actual
        """
        # Desactivamos los callbacks de las columnas y de los movimientos
        for col in self:
            col.callback_activos = False
        self.callbacks_activos = False
        # Llamada a función recursiva auxiliar
        self.jugs = []
        self.analizar_rec([-1]*self.D, 0)
        # Si no hay jugadas disponibles, añadir la jugada vacía
        if not self.jugs:
            self.jugs.append(JugPtos([-1]*self.D, self.valor_tablero()))
        # Ordenar de mejor a peor
        self.jugs.sort(reverse=True)
        # Reactivamos los callbacks de las columnas y de los movimientos
        for col in self:
            col.callback_activos = True
        self.callbacks_activos = True

    def jugada_azar(self) -> JugPtos:
        """ Devuelve una jugada al azar entre las posible jugadas válidas """
        return choice(self.jugs)

    def jugada_mejor(self) -> JugPtos:
        """ Devuelve la mejor jugada entre las posibles jugadas válidas"""
        # Podría devolverse self.jugs[0] pero es mejor no asumir que la lista está ordenada
        return max(self.jugs)


# Esta función no es necesaria para la segunda práctica
def main():
    seed(AZAR)
    print("*** PARGAMMON - PRIMERA PRÁCTICA ***")
    params = map(int, input("Numero de columnas, fichas y dados = ").split())
    # juego = Pargammon4(*params, fichas="☺☻×")
    juego = Pargammon(*params)
    #juego = Pargammon(*params, fichas="OX")
    tipo_jug = []
    for ficha in juego.FICHAS:
        tipo_jug.append(input(f"Jugador {ficha} es [H]umano, Máquina [T]onta o Máquina [L]ista: ").upper())
    fin = False
    while not fin:
        print(juego)
        deshacer = False
        if tipo_jug[juego.turno].startswith('T'):
            jug = juego.jugada_azar().str_jugada
            print(f"Jugada: {jug}")
            res = juego.jugar(jug)
            if res is not None:
                raise Exception(f"ERROR en Máquina Tonta: {res}")
        elif tipo_jug[juego.turno].startswith('L'):
            jug = juego.jugada_mejor().str_jugada
            print(f"Jugada: {jug}")
            res = juego.jugar(jug)
            if res is not None:
                raise Exception(f"ERROR en Máquina Lista: {res}")
        else:
            res = " "
            while res is not None:
                jug = input("Jugada: ").upper()
                if set(jug) == {'*'}:
                    deshacer = True
                    juego.deshacer(len(jug))
                    res = None
                else:
                    res = juego.jugar(jug)
                if res is not None:
                    print(res)
        if not deshacer:
            fin = juego.cambiar_turno()
    print(f"Han ganado los {juego.FICHAS[juego.turno]}!")
    


if __name__ == "__main__":
    main()
