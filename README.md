# Tankestina — Batalla Artillera

Pequeño juego de artillería estilo 'Tank' escrito en Python + pygame.

## Resumen

Tankestina enfrenta a dos tanques separados por un muro: el Jugador (izquierda) y la IA (derecha). El objetivo es apuntar y disparar para destruir al adversario usando ángulo y potencia. La IA usa heurísticas para apuntar, decidir moverse y ajustar la precisión según el nivel de dificultad.

## Archivos principales

- `main.py` — Bucle principal, lógica de juego y decisiones de la IA.
- `graficos.py` — Funciones de dibujo (tanques, muro, UI, menús).
- `animaciones.py` — Animaciones de disparo y destrucción.
- `utils.py` — Funciones auxiliares (posiciones aleatorias, etc.).
- `puntuaciones.py` — Sistema sencillo de puntuaciones.
- `run_app.py` — Launcher opcional para iniciar el juego.
- `requirements.txt` — Dependencias del proyecto.
- `img/` — Recursos gráficos (no tocar si no es necesario).

## Controles

- Flechas izquierda/derecha — Girar el cañón del jugador.
- A / D — Mover el tanque del jugador a izquierda/derecha (limitado por el muro).
- Barra espaciadora — Mantener para cargar potencia; soltar para disparar.
- Esc / Enter — Navegación en menús según la pantalla.

Nota: el juego muestra la UI del Jugador 1 siempre a la izquierda y la IA a la derecha.

## Cómo ejecutar

1. Activar el entorno virtual del proyecto (si existe):

```bash
source .venv/bin/activate
```

2. Instalar dependencias (si no están instaladas):

```bash
pip install -r requirements.txt
```

3. Ejecutar el juego:

```bash
.venv/bin/python run_app.py
# o alternativamente
.venv/bin/python main.py
```

Requisitos: entorno con soporte gráfico (X11/Wayland) si quieres ver la ventana del juego.

## Comprobaciones rápidas

- Para detectar problemas de sintaxis: `python -m py_compile main.py`.
- Para un chequeo estático rápido (en el venv): `python -m pyflakes .` (puede reportar advertencias en dependencias instaladas).

## Cómo funciona la IA (breve)

La IA decide entre disparar o moverse. Sus puntos clave:

- La dificultad (`NIVEL_DIFICULTAD`) afecta la variabilidad (precisión) — no la escala de potencia.
- La IA calcula un ángulo base según distancia y presencia del muro. Luego aplica variabilidad aleatoria menor en niveles altos.
- La potencia se calcula desde una estimación física (velocidad necesaria) y se mapea al rango del jugador (10–100).
- Si hay un muro significativo entre tanques, la IA reduce su potencia máxima para favorecer que se mueva en vez de disparar contra el muro.
- Si la IA falla repetidamente o golpea el muro, prioriza moverse hacia el jugador y consume el turno para hacerlo.
- El cañón de la IA rota visualmente hacia el ángulo objetivo en pasos (`ROTACION_PASO`) para que se vea la animación.

Parámetros relevantes (editar en `main.py`):

- `NIVEL_DIFICULTAD` — 1 (fácil) a 5 (maestro).
- `UMBRAL_FORZADO` — distancia a partir de la cual la IA fuerza acercamiento.
- `PASO_MOVIMIENTO_DEFAULT` / `PASO_MOVIMIENTO_FORZADO` — paso de movimiento de la IA.
- `ROTACION_PASO` — grados por frame para la rotación visual del cañón de la IA.
- `DEBUG_IA` — si `True` imprime trazas de decisión en la consola (útil para ajuste).

## Ajustes y tuning

- Para que la IA se mueva más a menudo, reducir `PASO_MOVIMIENTO_DEFAULT` o `UMBRAL_FORZADO`.
- Para que dispare con menos potencia cuando hay un muro, disminuir el valor de cap en la sección de `calcular_disparo_ia` (actualmente capa a 45 si detecta muro alto).
- Para ver las trazas y entender decisiones, activar `DEBUG_IA = True` temporalmente y ejecutar desde terminal.

## Problemas comunes y soluciones

- Error al iniciar por falta de dependencias: ejecutar `pip install -r requirements.txt` dentro del `.venv`.
- El juego no muestra ventana en servidores sin display: ejecutar en un entorno con X11/Wayland o usar X forwarding.
- Si el linter (pyflakes) muestra muchas advertencias, filtra solo tus archivos: `python -m pyflakes main.py graficos.py animaciones.py utils.py`.

## Créditos

Proyecto educativo — implementaciones y ajustes hechos en Python + pygame.

---

