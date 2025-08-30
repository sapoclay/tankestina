import pygame
import math
import os
import random

ANCHO = 800
ALTO = 600
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
ROJO_OSCURO = (139, 0, 0)  # Rojo oscuro para opción seleccionada
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
GRIS_CLARO = (200, 200, 200)
GRIS_OSCURO = (100, 100, 100)
AZUL_CIELO = (135, 206, 235)
VERDE_TIERRA = (34, 139, 34)
NARANJA = (255, 165, 0)
TAM_TANQUE = 40

_tanque1_img = None
_tanque2_img = None

def dibujar_fondo(pantalla):
    """Dibuja un fondo con gradiente cielo-tierra"""
    for y in range(ALTO):
        if y < ALTO // 2:
            # Cielo con gradiente
            factor = y / (ALTO // 2)
            color = (
                int(AZUL_CIELO[0] * (1 - factor * 0.3)),
                int(AZUL_CIELO[1] * (1 - factor * 0.3)),
                int(AZUL_CIELO[2] * (1 - factor * 0.1))
            )
        else:
            # Tierra
            color = VERDE_TIERRA
        pygame.draw.line(pantalla, color, (0, y), (ANCHO, y))

def dibujar_tanque(pantalla, x, y, color, angulo_canon=0, tipo=1):
    global _tanque1_img, _tanque2_img
    if tipo == 1:
        if _tanque1_img is None:
            try:
                _tanque1_img = pygame.image.load(os.path.join('img', 'tanque1.png')).convert_alpha()
                _tanque1_img = pygame.transform.scale(_tanque1_img, (TAM_TANQUE, TAM_TANQUE))
                # Asegurar que la imagen tenga fondo transparente
                _tanque1_img.set_colorkey((255, 255, 255))  # Blanco como transparente
                _tanque1_img.set_colorkey((0, 0, 0))  # Negro como transparente (por si acaso)
            except:
                # Fallback si no hay imagen - dibujar solo el contorno sin relleno
                pygame.draw.rect(pantalla, NEGRO, (x, y - TAM_TANQUE, TAM_TANQUE, TAM_TANQUE), 2)
                return
        img = _tanque1_img
    else:
        if _tanque2_img is None:
            try:
                _tanque2_img = pygame.image.load(os.path.join('img', 'tanque2.png')).convert_alpha()
                _tanque2_img = pygame.transform.scale(_tanque2_img, (TAM_TANQUE, TAM_TANQUE))
                # Asegurar que la imagen tenga fondo transparente
                _tanque2_img.set_colorkey((255, 255, 255))  # Blanco como transparente
                _tanque2_img.set_colorkey((0, 0, 0))  # Negro como transparente (por si acaso)
            except:
                # Fallback si no hay imagen - dibujar solo el contorno sin relleno
                pygame.draw.rect(pantalla, NEGRO, (x, y - TAM_TANQUE, TAM_TANQUE, TAM_TANQUE), 2)
                return
        img = _tanque2_img

    # Dibujar sombra del tanque (más sutil)
    sombra = pygame.Surface((TAM_TANQUE, TAM_TANQUE), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 30))  # Más transparente
    pantalla.blit(sombra, (x + 1, y - TAM_TANQUE + 1))

    # Dibujar imagen del tanque
    pantalla.blit(img, (x, y - TAM_TANQUE))

    # Dibujar cañón con mejor apariencia y indicador visual
    largo_canon = 35
    rad = math.radians(angulo_canon)
    x_canon = x + TAM_TANQUE//2 + largo_canon * math.cos(rad)
    y_canon = (y - TAM_TANQUE) - largo_canon * math.sin(rad)  # Desde la parte superior del tanque

    # Cañón principal con mejor visibilidad
    pygame.draw.line(pantalla, NEGRO, (x + TAM_TANQUE//2, y - TAM_TANQUE), (x_canon, y_canon), 8)
    # Borde del cañón
    pygame.draw.line(pantalla, GRIS_CLARO, (x + TAM_TANQUE//2, y - TAM_TANQUE), (x_canon, y_canon), 6)
    # Punta del cañón (más visible)
    pygame.draw.circle(pantalla, NEGRO, (int(x_canon), int(y_canon)), 4)
    pygame.draw.circle(pantalla, NARANJA, (int(x_canon), int(y_canon)), 2)

def dibujar_muro(pantalla, x, altura):
    """Dibuja un muro con textura y sombra"""
    # Sombra del muro
    pygame.draw.rect(pantalla, (0, 0, 0, 100), (x + 3, ALTO - altura + 3, 30, altura))

    # Muro principal con gradiente
    for i in range(altura):
        factor = i / altura
        color = (
            int(GRIS_OSCURO[0] * (1 - factor * 0.3)),
            int(GRIS_OSCURO[1] * (1 - factor * 0.3)),
            int(GRIS_OSCURO[2] * (1 - factor * 0.3))
        )
        pygame.draw.line(pantalla, color, (x, ALTO - altura + i), (x + 30, ALTO - altura + i))

    # Borde superior
    pygame.draw.line(pantalla, NEGRO, (x, ALTO - altura), (x + 30, ALTO - altura), 2)

def dibujar_barra_potencia(pantalla, x, y, potencia, max_potencia=100, color=NARANJA):
    """Dibuja una barra de potencia visual"""
    ancho_barra = 200
    alto_barra = 20

    # Fondo de la barra
    pygame.draw.rect(pantalla, GRIS_OSCURO, (x, y, ancho_barra, alto_barra))
    pygame.draw.rect(pantalla, NEGRO, (x, y, ancho_barra, alto_barra), 2)

    # Barra de potencia
    ancho_actual = int((potencia / max_potencia) * ancho_barra)
    pygame.draw.rect(pantalla, color, (x, y, ancho_actual, alto_barra))

    # Texto de potencia
    fuente = pygame.font.SysFont(None, 24)
    texto = fuente.render(f'{potencia}%', True, BLANCO)
    pantalla.blit(texto, (x + ancho_barra + 10, y))

def dibujar_ui_jugador(pantalla, x, y, angulo, potencia, puntos, color_texto, es_jugador1=True):
    """Dibuja la interfaz de usuario para un jugador"""
    fuente_titulo = pygame.font.SysFont(None, 28, bold=True)
    fuente_info = pygame.font.SysFont(None, 24)

    # Título del jugador
    titulo = "JUGADOR 1" if es_jugador1 else "JUGADOR 2"
    texto_titulo = fuente_titulo.render(titulo, True, color_texto)
    pantalla.blit(texto_titulo, (x, y))

    # Vida
    texto_puntos = fuente_info.render(f'Vida: {puntos}', True, color_texto)
    pantalla.blit(texto_puntos, (x, y + 35))

    # Ángulo con indicador visual
    texto_angulo = fuente_info.render(f'Ángulo: {angulo}°', True, color_texto)
    pantalla.blit(texto_angulo, (x, y + 60))

    # Indicador visual del ángulo (pequeña flecha)
    centro_x = x + 100
    centro_y = y + 75
    angulo_rad = math.radians(angulo)
    flecha_largo = 15
    flecha_x = centro_x + flecha_largo * math.cos(angulo_rad)
    flecha_y = centro_y - flecha_largo * math.sin(angulo_rad)

    pygame.draw.line(pantalla, color_texto, (centro_x, centro_y), (flecha_x, flecha_y), 3)
    # Punta de la flecha
    pygame.draw.circle(pantalla, color_texto, (int(flecha_x), int(flecha_y)), 2)

    # Barra de potencia
    dibujar_barra_potencia(pantalla, x, y + 85, potencia, color=color_texto)

def dibujar_titulo(pantalla):
    """Dibuja el título del juego"""
    fuente_titulo = pygame.font.SysFont(None, 48, bold=True)
    fuente_subtitulo = pygame.font.SysFont(None, 24)

    titulo = fuente_titulo.render("TANKESTINA", True, NEGRO)
    subtitulo = fuente_subtitulo.render("Batalla Artillera", True, GRIS_OSCURO)

    # Centro de la pantalla
    titulo_rect = titulo.get_rect(center=(ANCHO // 2, 40))
    subtitulo_rect = subtitulo.get_rect(center=(ANCHO // 2, 70))

    pantalla.blit(titulo, titulo_rect)
    pantalla.blit(subtitulo, subtitulo_rect)

def dibujar_controles(pantalla):
    """Dibuja las instrucciones de control"""
    fuente = pygame.font.SysFont(None, 20)
    controles = [
        "CONTROLES:",
        "<- -> : Angulo canon",
        "A D : Mover tanque",
        "ESPACIO : Disparar (mantén pulsado para más potencia)"
    ]

    y = ALTO - 80
    for linea in controles:
        texto = fuente.render(linea, True, NEGRO)
        pantalla.blit(texto, (10, y))
        y += 20

def dibujar_menu_principal(pantalla, opcion_seleccionada=0):
    """Dibuja el menú principal del juego"""
    # Dibujar imagen de fondo
    try:
        imagen_fondo = pygame.image.load(os.path.join('img', 'splash.png')).convert()
        # Escalar la imagen para que quepa en la pantalla
        imagen_fondo = pygame.transform.scale(imagen_fondo, (ANCHO, ALTO))
        pantalla.blit(imagen_fondo, (0, 0))
    except (pygame.error, FileNotFoundError):
        # Si no se puede cargar la imagen, usar el fondo gradiente normal
        dibujar_fondo(pantalla)

    # Título del juego con fondo
    fuente_titulo = pygame.font.SysFont(None, 64, bold=True)
    fuente_subtitulo = pygame.font.SysFont(None, 32)
    fuente_opciones = pygame.font.SysFont(None, 36)

    titulo = fuente_titulo.render("TANKESTINA", True, NEGRO)
    subtitulo = fuente_subtitulo.render("Batalla Artillera", True, NEGRO)

    titulo_rect = titulo.get_rect(center=(ANCHO // 2, 100))
    subtitulo_rect = subtitulo.get_rect(center=(ANCHO // 2, 140))

    # Fondo semi-transparente para el título
    fondo_titulo = pygame.Surface((titulo_rect.width + 40, titulo_rect.height + subtitulo_rect.height + 60))
    fondo_titulo.set_alpha(180)  # Semi-transparente
    fondo_titulo.fill((255, 255, 255))  # Blanco suave
    fondo_titulo_rect = fondo_titulo.get_rect(center=(ANCHO // 2, 120))
    pantalla.blit(fondo_titulo, fondo_titulo_rect)

    pantalla.blit(titulo, titulo_rect)
    pantalla.blit(subtitulo, subtitulo_rect)

    # Opciones del menú
    opciones = ["INICIAR JUEGO", "CONFIGURACIÓN", "MÁXIMAS PUNTUACIONES", "SALIR"]
    y_opcion = 250

    for i, opcion in enumerate(opciones):
        color = ROJO_OSCURO if i == opcion_seleccionada else NEGRO
        if i == opcion_seleccionada:
            # Resaltar opción seleccionada con indicador visual
            texto_opcion = fuente_opciones.render(f">> {opcion}", True, color)
        else:
            texto_opcion = fuente_opciones.render(f"   {opcion}", True, color)

        opcion_rect = texto_opcion.get_rect(center=(ANCHO // 2, y_opcion))

        # Fondo para cada opción
        if i == opcion_seleccionada:
            # Fondo más visible para la opción seleccionada
            fondo_opcion = pygame.Surface((opcion_rect.width + 40, opcion_rect.height + 20))
            fondo_opcion.set_alpha(200)  # Más opaco para la opción seleccionada
            fondo_opcion.fill((255, 200, 200))  # Rojo claro
        else:
            # Fondo sutil para opciones no seleccionadas
            fondo_opcion = pygame.Surface((opcion_rect.width + 40, opcion_rect.height + 20))
            fondo_opcion.set_alpha(150)  # Más transparente
            fondo_opcion.fill((255, 255, 255))  # Blanco suave

        fondo_opcion_rect = fondo_opcion.get_rect(center=(ANCHO // 2, y_opcion))
        pantalla.blit(fondo_opcion, fondo_opcion_rect)
        pantalla.blit(texto_opcion, opcion_rect)
        y_opcion += 60

    # Instrucciones
    fuente_instrucciones = pygame.font.SysFont(None, 24)
    instrucciones = fuente_instrucciones.render("Usa flechas ARRIBA/ABAJO para navegar, ENTER para seleccionar", True, NEGRO)
    inst_rect = instrucciones.get_rect(center=(ANCHO // 2, ALTO - 50))

    # Fondo para las instrucciones
    fondo_instrucciones = pygame.Surface((inst_rect.width + 40, inst_rect.height + 20))
    fondo_instrucciones.set_alpha(160)  # Semi-transparente
    fondo_instrucciones.fill((255, 255, 255))  # Blanco suave
    fondo_inst_rect = fondo_instrucciones.get_rect(center=(ANCHO // 2, ALTO - 50))
    pantalla.blit(fondo_instrucciones, fondo_inst_rect)

    pantalla.blit(instrucciones, inst_rect)

def dibujar_pantalla_puntuaciones(pantalla, puntuaciones):
    """Dibuja la pantalla de máximas puntuaciones"""
    # Dibujar fondo
    dibujar_fondo(pantalla)

    # Título
    fuente_titulo = pygame.font.SysFont(None, 48, bold=True)
    fuente_puntuacion = pygame.font.SysFont(None, 28)
    fuente_fecha = pygame.font.SysFont(None, 20)

    titulo = fuente_titulo.render("MÁXIMAS PUNTUACIONES", True, NEGRO)
    titulo_rect = titulo.get_rect(center=(ANCHO // 2, 50))
    pantalla.blit(titulo, titulo_rect)

    if not puntuaciones:
        # No hay puntuaciones
        fuente_vacio = pygame.font.SysFont(None, 32)
        texto_vacio = fuente_vacio.render("No hay puntuaciones guardadas", True, GRIS_OSCURO)
        vacio_rect = texto_vacio.get_rect(center=(ANCHO // 2, ALTO // 2))
        pantalla.blit(texto_vacio, vacio_rect)
    else:
        # Mostrar puntuaciones
        y = 120
        for i, puntuacion in enumerate(puntuaciones[:10], 1):
            # Posición
            if i == 1:
                color_pos = (255, 215, 0)  # Oro
            elif i == 2:
                color_pos = (192, 192, 192)  # Plata
            elif i == 3:
                color_pos = (205, 127, 50)  # Bronce
            else:
                color_pos = NEGRO

            # Número de posición
            texto_pos = fuente_puntuacion.render(f"{i}.", True, color_pos)
            pantalla.blit(texto_pos, (50, y))

            # Nombre
            texto_nombre = fuente_puntuacion.render(puntuacion["nombre"], True, NEGRO)
            pantalla.blit(texto_nombre, (100, y))

            # Vida restante
            texto_vida = fuente_puntuacion.render(f"Vida: {puntuacion['vida_restante']}", True, VERDE)
            pantalla.blit(texto_vida, (300, y))

            # Fecha
            texto_fecha = fuente_fecha.render(puntuacion["fecha"], True, GRIS_OSCURO)
            pantalla.blit(texto_fecha, (500, y))

            y += 40

    # Instrucción para volver
    fuente_volver = pygame.font.SysFont(None, 24)
    texto_volver = fuente_volver.render("Presiona ESC para volver al menu", True, GRIS_OSCURO)
    volver_rect = texto_volver.get_rect(center=(ANCHO // 2, ALTO - 30))
    pantalla.blit(texto_volver, volver_rect)

def dibujar_pantalla_configuracion(pantalla, opcion_seleccionada=0):
    """Dibuja la pantalla de configuración del juego"""
    # Dibujar fondo
    dibujar_fondo(pantalla)

    # Título
    fuente_titulo = pygame.font.SysFont(None, 48, bold=True)
    fuente_opciones = pygame.font.SysFont(None, 32)
    fuente_descripcion = pygame.font.SysFont(None, 24)

    titulo = fuente_titulo.render("CONFIGURACIÓN", True, NEGRO)
    titulo_rect = titulo.get_rect(center=(ANCHO // 2, 50))
    pantalla.blit(titulo, titulo_rect)

    # Subtítulo
    fuente_subtitulo = pygame.font.SysFont(None, 28)
    subtitulo = fuente_subtitulo.render("Selecciona el nivel de dificultad de la IA:", True, NEGRO)
    subtitulo_rect = subtitulo.get_rect(center=(ANCHO // 2, 100))
    pantalla.blit(subtitulo, subtitulo_rect)

    # Mostrar nivel actual
    fuente_actual = pygame.font.SysFont(None, 24)
    niveles = ["Fácil", "Medio", "Difícil", "Experto", "Maestro"]
    nivel_actual = niveles[opcion_seleccionada] if opcion_seleccionada < len(niveles) else "Maestro"
    texto_actual = fuente_actual.render(f"Nivel actual: {nivel_actual}", True, VERDE)
    actual_rect = texto_actual.get_rect(center=(ANCHO // 2, 130))
    pantalla.blit(texto_actual, actual_rect)

    # Opciones de dificultad
    dificultades = [
        ("FÁCIL", "La IA tiene mucha variabilidad (±20°) y comete muchos errores"),
        ("MEDIO", "La IA tiene variabilidad moderada (±12°) y algunos errores"),
        ("DIFÍCIL", "La IA es muy precisa (±5°) pero puede fallar en situaciones complejas"),
        ("EXPERTO", "La IA tiene precisión quirúrgica (±2°), rara vez falla"),
        ("MAESTRO", "La IA tiene precisión absoluta (±1°), casi infalible")
    ]

    y_opcion = 150
    for i, (nivel, descripcion) in enumerate(dificultades):
        # Color de la opción
        color = ROJO_OSCURO if i == opcion_seleccionada else NEGRO

        # Nombre del nivel
        if i == opcion_seleccionada:
            texto_nivel = fuente_opciones.render(f">> {nivel}", True, color)
        else:
            texto_nivel = fuente_opciones.render(f"   {nivel}", True, color)

        nivel_rect = texto_nivel.get_rect(center=(ANCHO // 2, y_opcion))
        pantalla.blit(texto_nivel, nivel_rect)

        # Descripción
        texto_desc = fuente_descripcion.render(descripcion, True, GRIS_OSCURO)
        desc_rect = texto_desc.get_rect(center=(ANCHO // 2, y_opcion + 30))
        pantalla.blit(texto_desc, desc_rect)

        y_opcion += 80

    # Instrucciones
    fuente_instrucciones = pygame.font.SysFont(None, 24)
    instrucciones = fuente_instrucciones.render("Usa flechas ARRIBA/ABAJO para seleccionar, ENTER para confirmar, ESC para cancelar", True, NEGRO)
    inst_rect = instrucciones.get_rect(center=(ANCHO // 2, ALTO - 50))
    pantalla.blit(instrucciones, inst_rect)

def dibujar_input_nombre(pantalla, nombre, vida_restante):
    """Dibuja la pantalla para ingresar el nombre del jugador"""
    # Dibujar fondo
    dibujar_fondo(pantalla)

    # Título
    fuente_titulo = pygame.font.SysFont(None, 48, bold=True)
    fuente_input = pygame.font.SysFont(None, 36)
    fuente_info = pygame.font.SysFont(None, 24)

    titulo = fuente_titulo.render("¡VICTORIA!", True, VERDE)
    titulo_rect = titulo.get_rect(center=(ANCHO // 2, 100))
    pantalla.blit(titulo, titulo_rect)

    # Información de la victoria
    info_vida = fuente_info.render(f"Vida restante: {vida_restante}", True, NEGRO)
    info_rect = info_vida.get_rect(center=(ANCHO // 2, 150))
    pantalla.blit(info_vida, info_rect)

    # Instrucción para ingresar nombre
    instruccion = fuente_info.render("Ingresa tu nombre para guardar la puntuación:", True, NEGRO)
    inst_rect = instruccion.get_rect(center=(ANCHO // 2, 200))
    pantalla.blit(instruccion, inst_rect)

    # Campo de entrada
    rect_input = pygame.Rect(ANCHO // 2 - 150, 230, 300, 50)
    pygame.draw.rect(pantalla, BLANCO, rect_input)
    pygame.draw.rect(pantalla, NEGRO, rect_input, 2)

    # Texto del nombre
    texto_nombre = fuente_input.render(nombre, True, NEGRO)
    nombre_rect = texto_nombre.get_rect(center=(ANCHO // 2, 255))
    pantalla.blit(texto_nombre, nombre_rect)

    # Cursor parpadeante
    if pygame.time.get_ticks() % 1000 < 500:
        cursor_x = nombre_rect.right + 5
        pygame.draw.line(pantalla, NEGRO, (cursor_x, 240), (cursor_x, 270), 2)

    # Instrucciones
    instrucciones = fuente_info.render("ENTER para guardar, ESC para cancelar", True, GRIS_OSCURO)
    inst_final_rect = instrucciones.get_rect(center=(ANCHO // 2, 320))
    pantalla.blit(instrucciones, inst_final_rect)
