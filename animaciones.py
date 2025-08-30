import pygame
import math
import random
from graficos import ANCHO, ALTO, ROJO, AZUL

def animar_destruccion_tanque(pantalla, x, y, color_tanque, muro_x=None, muro_altura=None, x_otro_tanque=None, y_otro_tanque=None, angulo_canon=0,
                              angulo_jugador=None, potencia_jugador=None, vida_jugador=None, vida_enemigo=None,
                              angulo_maquina=None, potencia_maquina=None, es_turno_jugador=True):
    """Animación de destrucción de tanque con pedazos volando"""
    # Crear pedazos del tanque
    pedazos = []
    num_pedazos = 8

    for i in range(num_pedazos):
        # Crear pedazos de diferentes tamaños y formas
        tamano = random.randint(8, 20)
        angulo = random.uniform(0, 2 * math.pi)
        velocidad = random.uniform(4, 14)  # Aumentado de 3-12 a 4-14
        rotacion = random.uniform(-5, 5)

        pedazo = {
            'x': x + random.randint(-15, 15),
            'y': y + random.randint(-15, 15),
            'vx': velocidad * math.cos(angulo),
            'vy': velocidad * math.sin(angulo) - random.uniform(3, 8),  # Aumentado de 2-6 a 3-8
            'rotacion': 0,
            'vel_rotacion': rotacion,
            'tamano': tamano,
            'vida': 60,
            'color': color_tanque,
            'forma': random.choice(['rect', 'circle', 'triangle'])
        }
        pedazos.append(pedazo)

    # Animar la destrucción
    for frame in range(60):
        # Dibujar fondo y elementos del juego
        from graficos import dibujar_fondo, dibujar_tanque, dibujar_muro, dibujar_ui_jugador, dibujar_controles, dibujar_titulo
        dibujar_fondo(pantalla)
        dibujar_titulo(pantalla)

        # Dibujar el otro tanque si existe
        if x_otro_tanque is not None and y_otro_tanque is not None:
            color_otro = (0, 255, 0) if color_tanque == (255, 0, 0) else (255, 0, 0)
            dibujar_tanque(pantalla, x_otro_tanque, y_otro_tanque, color_otro, angulo_canon, tipo=1 if color_tanque == (255, 0, 0) else 2)

        # Dibujar muro si existe
        if muro_x is not None and muro_altura is not None:
            dibujar_muro(pantalla, muro_x, muro_altura)

        # Dibujar UI del jugador (fija): Jugador 1 siempre a la izquierda, Jugador 2 siempre a la derecha
        if angulo_jugador is not None and potencia_jugador is not None and vida_jugador is not None and vida_enemigo is not None:
            ang_ui = angulo_jugador if angulo_jugador is not None else angulo_canon
            pot_ui = potencia_jugador if potencia_jugador is not None else 50
            ang_enemigo_ui = angulo_maquina if angulo_maquina is not None else 0
            pot_enemigo_ui = potencia_maquina if potencia_maquina is not None else 50
            # Jugador 1: izquierda (fija)
            dibujar_ui_jugador(pantalla, 10, 10, ang_ui, pot_ui, vida_jugador, (0,255,0), True)
            # Jugador 2: derecha (fija)
            dibujar_ui_jugador(pantalla, ANCHO - 250, 10, ang_enemigo_ui, pot_enemigo_ui, vida_enemigo, (255,0,0), False)

        # Dibujar controles
        dibujar_controles(pantalla)

        # Actualizar y dibujar pedazos
        for pedazo in pedazos[:]:
            # Aplicar física
            pedazo['x'] += pedazo['vx']
            pedazo['y'] += pedazo['vy']
            pedazo['vy'] += 0.3  # Gravedad
            pedazo['rotacion'] += pedazo['vel_rotacion']
            pedazo['vida'] -= 1

            if pedazo['vida'] <= 0:
                pedazos.remove(pedazo)
                continue

            # Dibujar pedazo con rotación
            alpha = int(255 * (pedazo['vida'] / 60))
            superficie = pygame.Surface((pedazo['tamano'] * 2, pedazo['tamano'] * 2), pygame.SRCALPHA)

            # Dibujar forma del pedazo
            if pedazo['forma'] == 'rect':
                pygame.draw.rect(superficie, (*pedazo['color'], alpha), (0, 0, pedazo['tamano'], pedazo['tamano']))
            elif pedazo['forma'] == 'circle':
                pygame.draw.circle(superficie, (*pedazo['color'], alpha), (pedazo['tamano'], pedazo['tamano']), pedazo['tamano'])
            else:  # triangle
                points = [(pedazo['tamano'], 0), (0, pedazo['tamano']*2), (pedazo['tamano']*2, pedazo['tamano']*2)]
                pygame.draw.polygon(superficie, (*pedazo['color'], alpha), points)

            # Rotar superficie
            superficie_rotada = pygame.transform.rotate(superficie, pedazo['rotacion'])
            rect_rotado = superficie_rotada.get_rect(center=(int(pedazo['x']), int(pedazo['y'])))
            pantalla.blit(superficie_rotada, rect_rotado)

        pygame.display.flip()
        pygame.time.delay(25)

def crear_particulas_tierra(pantalla, x, y, cantidad=5):
    """Crea partículas de tierra cuando un tanque se mueve"""
    particulas = []

    for _ in range(cantidad):
        particula = {
            'x': x + random.randint(-10, 10),
            'y': y + random.randint(-5, 5),
            'vx': random.uniform(-3, 3),  # Aumentado de -2,2 a -3,3
            'vy': random.uniform(-4, -1),  # Aumentado de -3,-1 a -4,-1
            'vida': 30,
            'color': (139, 69, 19)  # Color marrón tierra
        }
        particulas.append(particula)

    return particulas

def actualizar_particulas_tierra(pantalla, particulas):
    """Actualiza y dibuja partículas de tierra"""
    for particula in particulas[:]:
        particula['x'] += particula['vx']
        particula['y'] += particula['vy']
        particula['vy'] += 0.1  # Gravedad ligera
        particula['vida'] -= 1

        if particula['vida'] <= 0:
            particulas.remove(particula)
            continue

        alpha = int(255 * (particula['vida'] / 30))
        radio = max(1, particula['vida'] // 10)
        superficie = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        pygame.draw.circle(superficie, (*particula['color'], alpha), (radio, radio), radio)
        pantalla.blit(superficie, (int(particula['x'] - radio), int(particula['y'] - radio)))

def animar_explosion(pantalla, x, y, color=ROJO, muro_x=None, muro_altura=None, x_jugador=None, y_jugador=None, x_enemigo=None, y_enemigo=None, angulo_canon=0,
                     angulo_jugador=None, potencia_jugador=None, vida_jugador=None, vida_enemigo=None,
                     angulo_maquina=None, potencia_maquina=None, es_turno_jugador=True):
    """Animación de explosión mejorada con humo y fuego"""
    # Crear partículas de fuego (explosión inicial)
    particulas_fuego = []
    particulas_humo = []

    # Fuego - explosión inicial intensa
    for _ in range(25):
        angulo = random.uniform(0, 2 * math.pi)
        velocidad = random.uniform(2, 12)  # Aumentado de 1-10 a 2-12
        particulas_fuego.append({
            'x': x,
            'y': y,
            'vx': velocidad * math.cos(angulo),
            'vy': velocidad * math.sin(angulo) - random.uniform(1, 4),
            'vida': 20,
            'color': (255, random.randint(100, 255), 0) if random.random() > 0.5 else (255, 255, 0),
            'tamano': random.randint(3, 8)
        })

    # Humo - más persistente y lento
    for _ in range(15):
        angulo = random.uniform(0, 2 * math.pi)
        velocidad = random.uniform(0.8, 4)  # Aumentado de 0.5-3 a 0.8-4
        particulas_humo.append({
            'x': x + random.randint(-10, 10),
            'y': y + random.randint(-10, 10),
            'vx': velocidad * math.cos(angulo),
            'vy': velocidad * math.sin(angulo) - random.uniform(0.5, 2),
            'vida': 80,
            'color': (100, 100, 100),
            'tamano': random.randint(5, 15)
        })

    # Animar explosión
    for frame in range(80):
        # Dibujar fondo y elementos del juego
        from graficos import dibujar_fondo, dibujar_tanque, dibujar_muro, dibujar_ui_jugador, dibujar_controles, dibujar_titulo
        dibujar_fondo(pantalla)
        dibujar_titulo(pantalla)

        # Dibujar tanques si se proporcionan las coordenadas
        if x_jugador is not None and y_jugador is not None:
            dibujar_tanque(pantalla, x_jugador, y_jugador, (0,255,0), angulo_canon, tipo=1)
        if x_enemigo is not None and y_enemigo is not None:
            dibujar_tanque(pantalla, x_enemigo, y_enemigo, (255,0,0), 0, tipo=2)

        # Dibujar muro si se proporcionan las coordenadas
        if muro_x is not None and muro_altura is not None:
            dibujar_muro(pantalla, muro_x, muro_altura)

        # Dibujar UI fija: Jugador 1 izquierda, Jugador 2 derecha
        if angulo_jugador is not None and potencia_jugador is not None and vida_jugador is not None and vida_enemigo is not None:
            ang_ui = angulo_jugador if angulo_jugador is not None else angulo_canon
            pot_ui = potencia_jugador if potencia_jugador is not None else 50
            ang_enemigo_ui = angulo_maquina if angulo_maquina is not None else 0
            pot_enemigo_ui = potencia_maquina if potencia_maquina is not None else 50
            dibujar_ui_jugador(pantalla, 10, 10, ang_ui, pot_ui, vida_jugador, (0,255,0), True)
            dibujar_ui_jugador(pantalla, ANCHO - 250, 10, ang_enemigo_ui, pot_enemigo_ui, vida_enemigo, (255,0,0), False)

        # Dibujar controles
        dibujar_controles(pantalla)

        # Actualizar y dibujar partículas de fuego
        for particula in particulas_fuego[:]:
            particula['x'] += particula['vx']
            particula['y'] += particula['vy']
            particula['vy'] += 0.15  # Gravedad
            particula['vida'] -= 1

            if particula['vida'] <= 0:
                particulas_fuego.remove(particula)
            else:
                alpha = int(255 * (particula['vida'] / 20))
                radio = max(1, particula['tamano'] * particula['vida'] // 20)
                superficie = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
                pygame.draw.circle(superficie, (*particula['color'], alpha), (radio, radio), radio)
                pantalla.blit(superficie, (int(particula['x'] - radio), int(particula['y'] - radio)))

        # Actualizar y dibujar partículas de humo
        for particula in particulas_humo[:]:
            particula['x'] += particula['vx']
            particula['y'] += particula['vy']
            particula['vy'] += 0.05  # Gravedad ligera
            particula['vida'] -= 1

            if particula['vida'] <= 0:
                particulas_humo.remove(particula)
            else:
                alpha = int(200 * (particula['vida'] / 80))
                radio = max(2, particula['tamano'] * particula['vida'] // 80)
                superficie = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
                pygame.draw.circle(superficie, (*particula['color'], alpha), (radio, radio), radio)
                pantalla.blit(superficie, (int(particula['x'] - radio), int(particula['y'] - radio)))

        pygame.display.flip()
        pygame.time.delay(20)

def animar_disparo(pantalla, x0, y0, angulo, potencia, muro_x, muro_altura, enemigo_x, enemigo_y, angulo_canon,
                   angulo_jugador=None, potencia_jugador=None, vida_jugador=None, vida_enemigo=None,
                   angulo_maquina=None, potencia_maquina=None, es_turno_jugador=True):
    g = 9.8
    ang_rad = math.radians(angulo)
    # Aumentar la velocidad base multiplicando por un factor
    velocidad_base = potencia * 1.5  # Factor de velocidad aumentado
    v0x = velocidad_base * math.cos(ang_rad)
    v0y = -velocidad_base * math.sin(ang_rad)
    t = 0
    dt = 0.08  # Aumentado de 0.05 para mayor velocidad
    x = x0
    y = y0
    resultado = 'fallo'
    impacto = (x0, y0)  # Inicializar con coordenadas de partida

    while 0 <= x <= ANCHO and y <= ALTO + 50:  # Permitir que caiga un poco más abajo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Dibujar fondo y elementos durante la animación
        from graficos import dibujar_fondo, dibujar_tanque, dibujar_muro, dibujar_ui_jugador, dibujar_controles, dibujar_titulo
        dibujar_fondo(pantalla)
        dibujar_titulo(pantalla)

        # Determinar tipo de tanque por posición respecto al muro
        if x0 < muro_x:
            # Jugador 1 a la izquierda
            dibujar_tanque(pantalla, x0, y0, (0,255,0), angulo_canon, tipo=1)
            dibujar_tanque(pantalla, enemigo_x, enemigo_y, (255,0,0), 0, tipo=2)
        else:
            # Jugador 2 a la derecha
            dibujar_tanque(pantalla, enemigo_x, enemigo_y, (0,255,0), 0, tipo=1)
            dibujar_tanque(pantalla, x0, y0, (255,0,0), angulo_canon, tipo=2)

        dibujar_muro(pantalla, muro_x, muro_altura)

        # Dibujar UI fija: Jugador 1 izquierda, Jugador 2 derecha
        if angulo_jugador is not None and potencia_jugador is not None and vida_jugador is not None and vida_enemigo is not None:
            ang_ui = angulo_jugador if angulo_jugador is not None else angulo_canon
            pot_ui = potencia_jugador if potencia_jugador is not None else potencia
            ang_enemigo_ui = angulo_maquina if angulo_maquina is not None else 0
            pot_enemigo_ui = potencia_maquina if potencia_maquina is not None else potencia
            dibujar_ui_jugador(pantalla, 10, 10, ang_ui, pot_ui, vida_jugador, (0,255,0), True)
            dibujar_ui_jugador(pantalla, ANCHO - 250, 10, ang_enemigo_ui, pot_enemigo_ui, vida_enemigo, (255,0,0), False)

        # Dibujar controles
        dibujar_controles(pantalla)

        # Dibujar proyectil con efecto de rastro
        pygame.draw.circle(pantalla, (255,255,0), (int(x), int(y)), 8)  # Núcleo amarillo
        pygame.draw.circle(pantalla, (255,165,0), (int(x), int(y)), 12, 2)  # Aura naranja

        pygame.display.flip()
        pygame.time.delay(6)  # Reducido de 10ms a 6ms para mayor velocidad

        # Verificar colisión con el muro (zona más amplia)
        if muro_x - 5 < x < muro_x + 35 and y > ALTO - muro_altura - 10:
            resultado = 'muro'
            impacto = (x, y)
            break

        # Verificar colisión con el enemigo (zona más amplia y precisa)
        if enemigo_x - 10 < x < enemigo_x + 50 and enemigo_y - 50 < y < enemigo_y + 10:
            resultado = 'enemigo'
            impacto = (x, y)
            break

        # Actualizar posición de la bala
        t += dt
        x_anterior = x
        y_anterior = y
        x = x0 + v0x * t
        y = y0 + v0y * t + 0.5 * g * t * t

        # Verificar si la bala salió completamente de la pantalla
        if x < -20 or x > ANCHO + 20 or y > ALTO + 100:
            resultado = 'fallo'
            # Usar la última posición válida antes de salir de pantalla
            impacto = (x_anterior, y_anterior)
            break

    # Solo mostrar explosión si hubo un impacto real (enemigo o muro)
    # Para fallos, no mostrar explosión o mostrar una muy pequeña
    if resultado == 'enemigo':
        animar_explosion(pantalla, *impacto, color=ROJO,
                         muro_x=muro_x, muro_altura=muro_altura,
                         x_jugador=x0 if x0 < muro_x else enemigo_x,
                         y_jugador=y0 if x0 < muro_x else enemigo_y,
                         x_enemigo=enemigo_x if x0 < muro_x else x0,
                         y_enemigo=enemigo_y if x0 < muro_x else y0,
                         angulo_canon=angulo_canon,
                         angulo_jugador=angulo_jugador, potencia_jugador=potencia_jugador,
                         vida_jugador=vida_jugador, vida_enemigo=vida_enemigo,
                         angulo_maquina=angulo_maquina, potencia_maquina=potencia_maquina,
                         es_turno_jugador=es_turno_jugador)
    elif resultado == 'muro':
        animar_explosion(pantalla, *impacto, color=AZUL,
                         muro_x=muro_x, muro_altura=muro_altura,
                         x_jugador=x0 if x0 < muro_x else enemigo_x,
                         y_jugador=y0 if x0 < muro_x else enemigo_y,
                         x_enemigo=enemigo_x if x0 < muro_x else x0,
                         y_enemigo=enemigo_y if x0 < muro_x else y0,
                         angulo_canon=angulo_canon,
                         angulo_jugador=angulo_jugador, potencia_jugador=potencia_jugador,
                         vida_jugador=vida_jugador, vida_enemigo=vida_enemigo,
                         angulo_maquina=angulo_maquina, potencia_maquina=potencia_maquina,
                         es_turno_jugador=es_turno_jugador)
    elif resultado == 'fallo':
        # Para fallos, mostrar una pequeña explosión en el punto de impacto final
        # pero solo si la bala llegó al suelo (no salió por los lados)
        if ALTO - 50 <= impacto[1] <= ALTO + 50:  # Si llegó cerca del suelo
            # Pequeña explosión de tierra sin fuego intenso
            particulas_tierra = []
            for _ in range(8):
                angulo_particula = random.uniform(0, math.pi)  # Solo hacia arriba
                velocidad = random.uniform(2, 6)  # Aumentado de 1-4 a 2-6
                particulas_tierra.append({
                    'x': impacto[0],
                    'y': impacto[1],
                    'vx': velocidad * math.cos(angulo_particula),
                    'vy': -velocidad * math.sin(angulo_particula),  # Hacia arriba
                    'vida': 25,
                    'color': (139, 69, 19),  # Marrón tierra
                    'tamano': random.randint(2, 5)
                })

            # Animar pequeña explosión de tierra
            for frame in range(25):
                # Dibujar fondo y elementos del juego
                from graficos import dibujar_fondo, dibujar_tanque, dibujar_muro, dibujar_ui_jugador, dibujar_controles, dibujar_titulo
                dibujar_fondo(pantalla)
                dibujar_titulo(pantalla)

                # Dibujar tanques
                if x0 < muro_x:
                    dibujar_tanque(pantalla, x0, y0, (0,255,0), angulo_canon, tipo=1)
                    dibujar_tanque(pantalla, enemigo_x, enemigo_y, (255,0,0), 0, tipo=2)
                else:
                    dibujar_tanque(pantalla, enemigo_x, enemigo_y, (0,255,0), 0, tipo=1)
                    dibujar_tanque(pantalla, x0, y0, (255,0,0), angulo_canon, tipo=2)

                dibujar_muro(pantalla, muro_x, muro_altura)

                # Dibujar UI fija: Jugador 1 izquierda, Jugador 2 derecha
                if angulo_jugador is not None and potencia_jugador is not None and vida_jugador is not None and vida_enemigo is not None:
                    ang_ui = angulo_jugador if angulo_jugador is not None else angulo_canon
                    pot_ui = potencia_jugador if potencia_jugador is not None else potencia
                    ang_enemigo_ui = angulo_maquina if angulo_maquina is not None else angulo_canon
                    pot_enemigo_ui = potencia_maquina if potencia_maquina is not None else potencia
                    dibujar_ui_jugador(pantalla, 10, 10, ang_ui, pot_ui, vida_jugador, (0,255,0), True)
                    dibujar_ui_jugador(pantalla, ANCHO - 250, 10, ang_enemigo_ui, pot_enemigo_ui, vida_enemigo, (255,0,0), False)

                # Dibujar controles
                dibujar_controles(pantalla)

                # Dibujar partículas de tierra
                for particula in particulas_tierra[:]:
                    particula['x'] += particula['vx']
                    particula['y'] += particula['vy']
                    particula['vy'] += 0.2  # Gravedad
                    particula['vida'] -= 1

                    if particula['vida'] <= 0:
                        particulas_tierra.remove(particula)
                    else:
                        alpha = int(255 * (particula['vida'] / 25))
                        radio = max(1, particula['tamano'] * particula['vida'] // 25)
                        superficie = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
                        pygame.draw.circle(superficie, (*particula['color'], alpha), (radio, radio), radio)
                        pantalla.blit(superficie, (int(particula['x'] - radio), int(particula['y'] - radio)))

                pygame.display.flip()
                pygame.time.delay(15)

    return resultado, impacto
