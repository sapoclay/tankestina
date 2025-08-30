
import pygame
import sys
import random
from graficos import (
    ANCHO, ALTO, BLANCO, NEGRO, ROJO, VERDE, GRIS_OSCURO,
    dibujar_tanque, dibujar_muro, dibujar_fondo, dibujar_ui_jugador, dibujar_controles, dibujar_titulo,
    dibujar_menu_principal, dibujar_pantalla_puntuaciones, dibujar_pantalla_configuracion,
    dibujar_input_nombre
)
from animaciones import animar_disparo, animar_destruccion_tanque, crear_particulas_tierra, actualizar_particulas_tierra
from utils import nueva_posicion_enemigo, nueva_posicion_muro
from puntuaciones import SistemaPuntuaciones

# Configuración global del juego
NIVEL_DIFICULTAD = 2  # 1=Fácil, 2=Medio, 3=Difícil, 4=Experto, 5=Maestro
# Modo debug para simular turnos ide la IA y recoger trazas en la terminal
# Poner True sólo para pruebas automáticas; en ejecución normal dejamos False
DEBUG_IA = False
DEBUG_IA_TURNS = 8
# Parámetros de movimiento/heurística (ajustados para que la IA se acerque más y con pasos útiles)
# UMBRAL_FORZADO: distancia a partir de la cual la IA fuerza el acercamiento
UMBRAL_FORZADO = 80  # más agresiva: forzar acercamiento cuando la distancia sea >= 80
# PASO_MOVIMIENTO_DEFAULT/FORZADO: cuánto se mueve la IA cuando decide acercarse
PASO_MOVIMIENTO_DEFAULT = 30
PASO_MOVIMIENTO_FORZADO = 44
ROTACION_PASO = 3  # grados por frame que la IA puede girar el cañón para ser visible (más lento)



def mostrar_menu_principal(pantalla, sistema_puntuaciones):
    """Muestra el menú principal y maneja la navegación"""
    opcion_seleccionada = 0
    opciones_total = 4

    while True:
        # Dibujar menú
        dibujar_menu_principal(pantalla, opcion_seleccionada)
        pygame.display.flip()

        # Manejar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % opciones_total
                elif evento.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % opciones_total
                elif evento.key == pygame.K_RETURN:
                    if opcion_seleccionada == 0:  # Iniciar juego
                        return "juego"
                    elif opcion_seleccionada == 1:  # Configuración
                        mostrar_configuracion(pantalla)
                    elif opcion_seleccionada == 2:  # Ver puntuaciones
                        mostrar_puntuaciones(pantalla, sistema_puntuaciones)
                    elif opcion_seleccionada == 3:  # Salir
                        pygame.quit()
                        sys.exit()

def mostrar_puntuaciones(pantalla, sistema_puntuaciones):
    """Muestra la pantalla de puntuaciones"""
    while True:
        puntuaciones = sistema_puntuaciones.obtener_top_puntuaciones()
        dibujar_pantalla_puntuaciones(pantalla, puntuaciones)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return

def mostrar_configuracion(pantalla):
    """Muestra la pantalla de configuración y permite cambiar el nivel de dificultad"""
    global NIVEL_DIFICULTAD
    opcion_seleccionada = NIVEL_DIFICULTAD - 1  # Convertir a índice (0-4)
    opciones_total = 5

    while True:
        # Dibujar configuración
        dibujar_pantalla_configuracion(pantalla, opcion_seleccionada)
        pygame.display.flip()

        # Manejar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % opciones_total
                elif evento.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % opciones_total
                elif evento.key == pygame.K_RETURN:
                    NIVEL_DIFICULTAD = opcion_seleccionada + 1  # Convertir de vuelta (1-5)
                    return
                elif evento.key == pygame.K_ESCAPE:
                    return

def guardar_puntuacion_ganador(pantalla, vida_restante, sistema_puntuaciones):
    """Permite al jugador ingresar su nombre para guardar la puntuación"""
    nombre = ""
    fuente_input = pygame.font.SysFont(None, 36)

    while True:
        dibujar_input_nombre(pantalla, nombre, vida_restante)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN and nombre.strip():
                    # Guardar puntuación
                    sistema_puntuaciones.agregar_puntuacion(nombre.strip(), vida_restante)
                    return
                elif evento.key == pygame.K_ESCAPE:
                    return
                elif evento.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                else:
                    # Agregar carácter si es alfanumérico y no excede el límite
                    if len(nombre) < 15 and evento.unicode.isalnum() or evento.unicode in " ñÑáéíóúÁÉÍÓÚ":
                        nombre += evento.unicode

def calcular_disparo_ia(x_enemigo, y_enemigo, x_jugador, y_jugador, muro_x, muro_altura):
    """
    Calcula el ángulo y potencia óptimos para que la IA acierte al jugador
    teniendo en cuenta el muro como obstáculo y el nivel de dificultad
    """
    global NIVEL_DIFICULTAD
    import math

    # Calcular distancia y altura entre tanques
    dx = abs(x_jugador - x_enemigo)
    dy = y_enemigo - y_jugador  # Diferencia de altura (positiva si enemigo está más alto)

    # Si el enemigo está a la izquierda del muro y el jugador a la derecha (o viceversa)
    # necesitamos disparar por encima del muro
    if (x_enemigo < muro_x and x_jugador > muro_x) or (x_enemigo > muro_x and x_jugador < muro_x):
        # Calcular la altura efectiva considerando el muro
        altura_muro = muro_altura
        distancia_muro = min(abs(muro_x - x_enemigo), abs(muro_x - x_jugador))

        # Si el muro es un obstáculo significativo, calcular trayectoria por encima
        if altura_muro > 50:  # Muro alto
            # Usar trayectoria parabólica más alta, ajustar según distancia para pasar por encima
            if dx < 150:  # Distancia corta con muro alto
                angulo_base = 75
            elif dx > 300:  # Distancia muy larga
                angulo_base = 60
            elif dx > 200:  # Distancia larga
                angulo_base = 65
            else:  # Distancia media
                angulo_base = 68
        else:
            # Muro bajo
            # Para muro bajo favorecer ángulos moderadamente altos si la distancia lo requiere
            if dx < 150:  # Distancia corta con muro bajo
                angulo_base = 60
            else:  # Distancia normal
                angulo_base = 50
    else:
        # Sin muro entre medio, trayectoria directa
        if dx < 150:  # Distancia corta - ángulo más alto para mejor trayectoria
            angulo_base = 50
        elif dx < 250:  # Distancia media
            angulo_base = 45
        else:  # Distancia larga
            angulo_base = 40

    # Añadir variabilidad controlada según el nivel de dificultad
    # Cuanto mayor el nivel, menor la variabilidad (más precisión)
    if NIVEL_DIFICULTAD == 1:  # Fácil - mucha variabilidad
        variabilidad = random.randint(-20, 20)
    elif NIVEL_DIFICULTAD == 2:  # Medio - variabilidad moderada
        variabilidad = random.randint(-12, 12)
    elif NIVEL_DIFICULTAD == 3:  # Difícil - poca variabilidad
        variabilidad = random.randint(-5, 5)
    elif NIVEL_DIFICULTAD == 4:  # Experto - mínima variabilidad
        variabilidad = random.randint(-2, 2)
    else:  # Maestro - precisión quirúrgica
        variabilidad = random.randint(-1, 1)

    angulo_canon_maquina = max(30, min(85, angulo_base + variabilidad))

    # Calcular potencia basada en física real
    g = 9.8
    ang_rad = math.radians(180 - angulo_canon_maquina)

    # Estimar la distancia efectiva (considerando el muro si existe)
    distancia_efectiva = dx
    if muro_altura > 30:
        # Si hay muro alto, ajustar ligeramente la distancia efectiva según dificultad
        # Niveles más altos tienen cálculos más precisos
        if NIVEL_DIFICULTAD >= 4:  # Experto y Maestro - máxima precisión
            distancia_efectiva *= 0.99  # Ajuste mínimo
        elif NIVEL_DIFICULTAD == 3:  # Difícil - buena precisión
            distancia_efectiva *= 0.97  # Ajuste moderado
        else:  # Fácil y Medio - precisión básica
            distancia_efectiva *= 0.94  # Ajuste mayor

    # Calcular velocidad inicial necesaria
    try:
        # Fórmula de física: v = sqrt((g * d^2) / (2 * cos^2(θ) * (h + d * tan(θ))))
        tan_theta = math.tan(ang_rad)
        cos_theta = math.cos(ang_rad)

        # Altura máxima aproximada
        altura_max = (distancia_efectiva * tan_theta) - (g * distancia_efectiva**2) / (2 * cos_theta**2)

        if altura_max < 0:
            altura_max = 0

        # Calcular velocidad inicial
        velocidad_inicial = math.sqrt((g * distancia_efectiva**2) / (2 * cos_theta**2 * (altura_max + 1)))
        # Convertir a potencia del juego (escala 10-100)
        # Usar factor de conversión fijo; la dificultad NO debe cambiar la escala de potencia,
        # solo la precisión (variabilidad).
        factor_conversion = 15.0
        potencia_base = int((velocidad_inicial / factor_conversion) * 10)

        # Ajuste especial: usar la misma mínima que el jugador (10) para que la IA
        # utilice el mismo rango de potencia que el jugador 1
        potencia_minima = 10

        # Añadir variabilidad controlada según dificultad: afecta sólo a la dispersión (precision)
        if NIVEL_DIFICULTAD == 1:  # Fácil - amplia variabilidad
            variabilidad_potencia = random.randint(-6, 8)
        elif NIVEL_DIFICULTAD == 2:  # Medio
            variabilidad_potencia = random.randint(-4, 6)
        elif NIVEL_DIFICULTAD == 3:  # Difícil
            variabilidad_potencia = random.randint(-2, 4)
        elif NIVEL_DIFICULTAD == 4:  # Experto
            variabilidad_potencia = random.randint(-1, 3)
        else:  # Maestro
            variabilidad_potencia = random.randint(-1, 2)

        # La potencia final respeta límites pero la dificultad NO la incrementa artificialmente
        potencia_maquina = max(potencia_minima, min(100, potencia_base + variabilidad_potencia))

        # Mapear la potencia al mismo formato/granularidad que el jugador 1
        potencia_maquina = int(max(10, min(100, round(potencia_maquina))))

        # Si existe un muro entre los tanques y es considerable, limitar la potencia
        # para evitar impactos sistemáticos contra el muro y favorecer que la IA mueva
        if (x_enemigo < muro_x < x_jugador) or (x_jugador < muro_x < x_enemigo):
                    if muro_altura > 30:
                        # Capar potencia máxima cuando hay muro en medio
                        # Reducido para incentivar movimiento en lugar de disparos inútiles
                        potencia_maquina = min(potencia_maquina, 45)
                        if 'DEBUG_IA' in globals() and DEBUG_IA:
                            print(f"[DEBUG_IA][calcular_disparo_ia] Muro detectado entre tanques. Potencia capada a {potencia_maquina}")

    except (ValueError, ZeroDivisionError):
        # Fallback si hay error en el cálculo - usar valores más razonables
        if dx < 150:
            potencia_maquina = random.randint(25, 45)  # Valores más bajos
        elif dx < 250:
            potencia_maquina = random.randint(20, 40)  # Valores más bajos
        else:
            potencia_maquina = random.randint(15, 35)  # Valores más bajos

    return angulo_canon_maquina, potencia_maquina

def decidir_movimiento_ia(x_enemigo, x_jugador, muro_x, ancho_juego=ANCHO):
    """
    Decide si la IA debería moverse y hacia dónde para mejorar su posición
    teniendo en cuenta las restricciones de movimiento reales
    """
    # Límites de movimiento reales para la IA
    limite_izquierdo = muro_x + 40  # Margen junto al muro (no cruzar)
    limite_derecho = ancho_juego - 40  # Límite derecho de la pantalla

    # Si el jugador está a la izquierda de la IA, queremos acercarnos hacia la izquierda
    # Si el jugador está a la derecha de la IA, acercarnos hacia la derecha
    distancia_jugador = x_enemigo - x_jugador

    # Umbral mínimo para evitar pequeños ajustes innecesarios
    umbral_acercamiento = 30

    if abs(distancia_jugador) <= umbral_acercamiento:
        return None

    if x_jugador < x_enemigo:
        # Intentar acercarse hacia la izquierda sin cruzar el muro
        if x_enemigo - 1 <= limite_izquierdo:
            return None
        # Permitir movimiento hacia la izquierda si reduce distancia al jugador
        if x_enemigo > x_jugador + umbral_acercamiento:
            return "izquierda"
    else:
        # Intentar acercarse hacia la derecha sin salirse de la pantalla
        if x_enemigo + 1 >= limite_derecho:
            return None
        if x_enemigo < x_jugador - umbral_acercamiento:
            return "derecha"

    return None

def mostrar_mensaje_derrota(pantalla):
    """Muestra mensaje de derrota"""
    fuente_derrota = pygame.font.SysFont(None, 48)
    fuente_continuar = pygame.font.SysFont(None, 24)

    while True:
        dibujar_fondo(pantalla)

        texto_derrota = fuente_derrota.render('¡DERROTA!', True, ROJO)
        texto_mensaje = fuente_continuar.render('El enemigo te ha destruido', True, NEGRO)
        texto_volver = fuente_continuar.render('Presiona cualquier tecla para continuar', True, GRIS_OSCURO)

        pantalla.blit(texto_derrota, (ANCHO//2 - 150, ALTO//2 - 50))
        pantalla.blit(texto_mensaje, (ANCHO//2 - 200, ALTO//2))
        pantalla.blit(texto_volver, (ANCHO//2 - 180, ALTO//2 + 50))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                return

def jugar_partida(pantalla, sistema_puntuaciones):
    """Ejecuta una partida completa del juego"""
    muro_x, muro_altura = nueva_posicion_muro()
    # El jugador 1 siempre a la izquierda del muro, el jugador 2 a la derecha
    x_jugador = random.randint(0, muro_x - 60)
    y_jugador = ALTO - 40  # Más cerca del suelo
    x_enemigo = random.randint(muro_x + 60, ANCHO - 40)
    y_enemigo = ALTO - 40  # Más cerca del suelo
    vida_jugador = 1000  # Vida máxima del jugador
    vida_enemigo = 1000  # Vida máxima del enemigo
    puntos = 0
    disparos = 0
    angulo_canon = 45
    potencia = 10
    mostrar_dano = False
    dano_valor = 0
    dano_pos = (0, 0)
    fuente = pygame.font.SysFont(None, 36)
    fuente_dano = pygame.font.SysFont(None, 32)
    cargando_potencia = False
    tiempo_inicio_potencia = 0
    turno_jugador = True
    # Si estamos en modo debug, forzamos que la IA juegue continuamente
    if DEBUG_IA:
        turno_jugador = False
    debug_ia_turn = 0
    ultimo_resultado_ia = None
    # Contador de fallos consecutivos para la heurística A
    fallos_consecutivos_ia = 0
    puntos_maquina = 0
    angulo_canon_maquina = 45
    potencia_maquina = 50

    # Variables para movimiento continuo del cañón
    girando_izquierda = False
    girando_derecha = False

    # Variables para efectos visuales
    particulas_tierra_jugador = []
    particulas_tierra_enemigo = []
    x_jugador_anterior = x_jugador
    x_enemigo_anterior = x_enemigo

    while True:
        # Dibujar fondo con gradiente
        dibujar_fondo(pantalla)

        # Dibujar título
        dibujar_titulo(pantalla)

        # Movimiento visual del cañón de la IA: calcular ángulo objetivo y acercarnos gradualmente
        if not turno_jugador:
            try:
                ang_objetivo, _ = calcular_disparo_ia(x_enemigo, y_enemigo, x_jugador, y_jugador, muro_x, muro_altura)
            except Exception:
                ang_objetivo = angulo_canon_maquina
            # Ajustar hacia el objetivo con paso limitado para que sea visible
            diff = ang_objetivo - angulo_canon_maquina
            if abs(diff) <= ROTACION_PASO:
                angulo_canon_maquina = ang_objetivo
            else:
                angulo_canon_maquina += ROTACION_PASO if diff > 0 else -ROTACION_PASO

        # Dibujar elementos del juego
        dibujar_tanque(pantalla, x_jugador, y_jugador, VERDE, angulo_canon, tipo=1)
        dibujar_tanque(pantalla, x_enemigo, y_enemigo, ROJO, angulo_canon_maquina, tipo=2)
        dibujar_muro(pantalla, muro_x, muro_altura)

        # Dibujar UI de los jugadores
        dibujar_ui_jugador(pantalla, 10, 10, angulo_canon, potencia, vida_jugador, VERDE, True)
        dibujar_ui_jugador(pantalla, ANCHO - 250, 10, angulo_canon_maquina, potencia_maquina, vida_enemigo, ROJO, False)

        # Dibujar controles
        dibujar_controles(pantalla)

        # Actualizar y dibujar partículas de tierra
        actualizar_particulas_tierra(pantalla, particulas_tierra_jugador)
        actualizar_particulas_tierra(pantalla, particulas_tierra_enemigo)

        # Mostrar daño si hay
        if mostrar_dano:
            fuente_dano = pygame.font.SysFont(None, 32)
            texto_dano = fuente_dano.render(f'+{dano_valor} daño', True, ROJO)
            pantalla.blit(texto_dano, dano_pos)

        pygame.display.flip()

        if turno_jugador:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_LEFT:
                        girando_izquierda = True
                        angulo_canon = min(angulo_canon + 1, 90)
                    if evento.key == pygame.K_RIGHT:
                        girando_derecha = True
                        angulo_canon = max(angulo_canon - 1, 0)
                    if evento.key == pygame.K_a:
                        x_jugador_anterior = x_jugador
                        x_jugador = max(x_jugador - 10, 0)
                        if x_jugador > muro_x - 60:
                            x_jugador = muro_x - 60
                        # Crear partículas de tierra si el tanque se movió
                        if x_jugador != x_jugador_anterior:
                            nuevas_particulas = crear_particulas_tierra(pantalla, x_jugador + 20, y_jugador + 20, 3)
                            particulas_tierra_jugador.extend(nuevas_particulas)
                    if evento.key == pygame.K_d:
                        x_jugador_anterior = x_jugador
                        x_jugador = min(x_jugador + 10, muro_x - 60)
                        # Crear partículas de tierra si el tanque se movió
                        if x_jugador != x_jugador_anterior:
                            nuevas_particulas = crear_particulas_tierra(pantalla, x_jugador + 20, y_jugador + 20, 3)
                            particulas_tierra_jugador.extend(nuevas_particulas)
                    if evento.key == pygame.K_SPACE and not cargando_potencia:
                        cargando_potencia = True
                        tiempo_inicio_potencia = pygame.time.get_ticks()
                if evento.type == pygame.KEYUP:
                    if evento.key == pygame.K_LEFT:
                        girando_izquierda = False
                    if evento.key == pygame.K_RIGHT:
                        girando_derecha = False
                    if evento.key == pygame.K_SPACE and cargando_potencia:
                        tiempo_fin = pygame.time.get_ticks()
                        duracion = (tiempo_fin - tiempo_inicio_potencia) / 1000.0
                        potencia = min(10 + int(duracion * 60), 100)
                        cargando_potencia = False
                        resultado, impacto = animar_disparo(
                            pantalla,
                            x_jugador + 40, y_jugador,
                            angulo_canon, potencia,
                            muro_x, muro_altura,
                            x_enemigo, y_enemigo,
                            angulo_canon,
                            angulo_jugador=angulo_canon, potencia_jugador=potencia,
                            vida_jugador=vida_jugador, vida_enemigo=vida_enemigo,
                            angulo_maquina=angulo_canon_maquina, potencia_maquina=potencia_maquina,
                            es_turno_jugador=True
                        )
                        disparos += 1
                        mostrar_dano = False
                        if resultado == 'enemigo':
                            dano = random.randint(80, 120)
                            vida_enemigo -= dano
                            mostrar_dano = True
                            dano_valor = dano
                            dano_pos = (int(impacto[0]), int(impacto[1]) - 50)
                            # Verificar si el enemigo fue destruido
                            if vida_enemigo <= 0:
                                vida_enemigo = 0
                                # Animación de destrucción del tanque enemigo
                                animar_destruccion_tanque(
                                    pantalla, x_enemigo + 20, y_enemigo,
                                    ROJO, muro_x, muro_altura,
                                    x_jugador, y_jugador, angulo_canon,
                                    angulo_jugador=angulo_canon, potencia_jugador=potencia,
                                    vida_jugador=vida_jugador, vida_enemigo=vida_enemigo,
                                    angulo_maquina=angulo_canon_maquina, potencia_maquina=potencia_maquina,
                                    es_turno_jugador=True
                                )
                                # Guardar puntuación
                                guardar_puntuacion_ganador(pantalla, vida_jugador, sistema_puntuaciones)
                                return "victoria"
                        elif resultado == 'muro':
                            mostrar_dano = True
                            dano_valor = 0
                            dano_pos = (int(impacto[0]), int(impacto[1]) - 50)
                        if disparos % 2 == 0:
                            x_jugador_anterior = x_jugador
                            x_enemigo_anterior = x_enemigo
                            x_jugador = random.randint(0, muro_x - 60)
                            x_enemigo = random.randint(muro_x + 60, ANCHO - 40)
                            y_jugador = ALTO - 40  # Mantener en el suelo
                            y_enemigo = ALTO - 40  # Mantener en el suelo
                        turno_jugador = False
            # Movimiento continuo del cañón si se mantiene pulsada la tecla
            if girando_izquierda:
                angulo_canon = min(angulo_canon + 1, 90)
            if girando_derecha:
                angulo_canon = max(angulo_canon - 1, 0)
            # Si está cargando potencia, actualizar el valor mostrado
            if cargando_potencia:
                tiempo_actual = pygame.time.get_ticks()
                duracion = (tiempo_actual - tiempo_inicio_potencia) / 1000.0
                potencia = min(10 + int(duracion * 60), 100)
        else:
            pygame.time.delay(700)

            # IA considera moverse para mejorar su posición
            movimiento_ia = decidir_movimiento_ia(x_enemigo, x_jugador, muro_x)

            # --- LOG DEBUG: información de decisión de la IA ---
            dx_actual = abs(x_enemigo - x_jugador)
            forzado = False
            preferir_mover_por_muro = False
            preferir_mover_por_fallos = False
            # Si el último disparo impactó en el muro, preferir moverse en vez de disparar
            if ultimo_resultado_ia == 'muro':
                preferir_mover_por_muro = True
                movimiento_ia = "izquierda" if x_jugador < x_enemigo else "derecha"
                forzado = True
            # Si la IA falló varias veces seguidas, preferir moverse (ahora con 1 fallo)
            if fallos_consecutivos_ia >= 1:
                preferir_mover_por_fallos = True
                movimiento_ia = "izquierda" if x_jugador < x_enemigo else "derecha"
                forzado = True

            # Forzar acercamiento cuando la IA esté lejos del jugador: priorizar movimiento sobre disparo
            if movimiento_ia is None and dx_actual > UMBRAL_FORZADO:
                movimiento_ia = "izquierda" if x_jugador < x_enemigo else "derecha"
                forzado = True

            if 'DEBUG_IA' in globals() and DEBUG_IA:
                print(f"[DEBUG_IA] Turno {debug_ia_turn+1}: dx={dx_actual}, movimiento_sugerido={movimiento_ia}, forzado={forzado}, preferir_mover_por_muro={preferir_mover_por_muro}, preferir_mover_por_fallos={preferir_mover_por_fallos}, fallos_consecutivos={fallos_consecutivos_ia}, x_enemigo={x_enemigo}, x_jugador={x_jugador}")

            # Ejecutar movimiento si hay sugerencia (IA prioriza acercarse)
            if movimiento_ia is not None:
                x_enemigo_anterior = x_enemigo
                # Incrementar paso si estamos moviendo por golpe previo al muro o si es forzado
                paso_movimiento = PASO_MOVIMIENTO_FORZADO if (preferir_mover_por_muro or preferir_mover_por_fallos or forzado) else PASO_MOVIMIENTO_DEFAULT
                if movimiento_ia == "derecha":
                    x_enemigo = min(x_enemigo + paso_movimiento, ANCHO - 40)
                elif movimiento_ia == "izquierda":
                    x_enemigo = max(x_enemigo - paso_movimiento, muro_x + 40)

                if x_enemigo != x_enemigo_anterior:
                    nuevas_particulas = crear_particulas_tierra(pantalla, x_enemigo + 20, y_enemigo + 20, 4)
                    particulas_tierra_enemigo.extend(nuevas_particulas)

                # Pausa corta tras el movimiento para suavizar
                pygame.time.delay(160)

                # Si preferimos mover por haber golpeado el muro anteriormente o por fallos, consumimos el turno moviendo
                if preferir_mover_por_muro or preferir_mover_por_fallos:
                    motivo = 'muro' if preferir_mover_por_muro else 'fallos'
                    if 'DEBUG_IA' in globals() and DEBUG_IA:
                        print(f"[DEBUG_IA] Movimiento forzado por motivo={motivo} ejecutado. x_enemigo {x_enemigo_anterior} -> {x_enemigo}")
                    # Resetear la preferencia/contador para siguientes turnos
                    ultimo_resultado_ia = None
                    fallos_consecutivos_ia = 0
                    turno_jugador = True
                    # Saltar el disparo: la IA usó su turno para moverse
                    continue

            # Calcular disparo inteligente de la IA
            angulo_canon_maquina, potencia_maquina = calcular_disparo_ia(
                x_enemigo, y_enemigo, x_jugador, y_jugador, muro_x, muro_altura
            )
            if 'DEBUG_IA' in globals() and DEBUG_IA:
                print(f"[DEBUG_IA] Potencia calculada: {potencia_maquina}, angulo: {angulo_canon_maquina}")

            resultado, impacto = animar_disparo(
                pantalla,
                x_enemigo, y_enemigo,
                180 - angulo_canon_maquina, potencia_maquina,
                muro_x, muro_altura,
                x_jugador, y_jugador,
                180 - angulo_canon_maquina,
                angulo_jugador=angulo_canon, potencia_jugador=potencia,
                vida_jugador=vida_jugador, vida_enemigo=vida_enemigo,
                angulo_maquina=angulo_canon_maquina, potencia_maquina=potencia_maquina,
                es_turno_jugador=False
            )
            # Registrar resultado del disparo para la heurística de movimiento
            ultimo_resultado_ia = resultado
            if resultado == 'fallo':
                fallos_consecutivos_ia += 1
            else:
                # Resetear contador si acierta o golpea el muro
                fallos_consecutivos_ia = 0
            # Incrementar contador debug y terminar si alcanzamos el límite
            if DEBUG_IA:
                debug_ia_turn += 1
                if 'DEBUG_IA' in globals() and DEBUG_IA:
                    print(f"[DEBUG_IA] Resultado disparo: {resultado}, vida_jugador={vida_jugador}, vida_enemigo={vida_enemigo}\n")
                    if debug_ia_turn >= DEBUG_IA_TURNS:
                        print("[DEBUG_IA] Fin de prueba automática. Saliendo de la partida de prueba.")
                        return "derrota"
            if resultado == 'enemigo':
                dano = random.randint(80, 120)
                vida_jugador -= dano
                mostrar_dano = True
                dano_valor = dano
                dano_pos = (int(impacto[0]), int(impacto[1]) - 50)
                # Verificar si el jugador fue destruido
                if vida_jugador <= 0:
                    vida_jugador = 0
                    # Animación de destrucción del tanque del jugador
                    animar_destruccion_tanque(
                        pantalla, x_jugador + 20, y_jugador,
                        VERDE, muro_x, muro_altura,
                        x_enemigo, y_enemigo, angulo_canon_maquina,
                        angulo_jugador=angulo_canon, potencia_jugador=potencia,
                        vida_jugador=vida_jugador, vida_enemigo=vida_enemigo,
                        angulo_maquina=angulo_canon_maquina, potencia_maquina=potencia_maquina,
                        es_turno_jugador=False
                    )
                    mostrar_mensaje_derrota(pantalla)
                    return "derrota"
            elif resultado == 'muro':
                mostrar_dano = True
                dano_valor = 0
                dano_pos = (int(impacto[0]), int(impacto[1]) - 50)
            turno_jugador = True

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption('Tankestina - Batalla Artillera')

    # Inicializar sistema de puntuaciones
    sistema_puntuaciones = SistemaPuntuaciones()

    while True:
        # Mostrar menú principal
        accion = mostrar_menu_principal(pantalla, sistema_puntuaciones)

        if accion == "juego":
            # Jugar partida
            resultado = jugar_partida(pantalla, sistema_puntuaciones)

            # Después de la partida, volver al menú
            if resultado in ["victoria", "derrota"]:
                continue

if __name__ == '__main__':
    main()
