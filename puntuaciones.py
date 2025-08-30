import json
import os
from datetime import datetime

class SistemaPuntuaciones:
    def __init__(self, archivo_puntuaciones="puntuaciones.json"):
        self.archivo_puntuaciones = archivo_puntuaciones
        self.puntuaciones = []
        self.cargar_puntuaciones()

    def cargar_puntuaciones(self):
        """Carga las puntuaciones desde el archivo"""
        try:
            if os.path.exists(self.archivo_puntuaciones):
                with open(self.archivo_puntuaciones, 'r', encoding='utf-8') as f:
                    self.puntuaciones = json.load(f)
            else:
                self.puntuaciones = []
        except (json.JSONDecodeError, FileNotFoundError):
            self.puntuaciones = []

    def guardar_puntuaciones(self):
        """Guarda las puntuaciones en el archivo"""
        try:
            with open(self.archivo_puntuaciones, 'w', encoding='utf-8') as f:
                json.dump(self.puntuaciones, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar puntuaciones: {e}")

    def agregar_puntuacion(self, nombre, vida_restante):
        """Agrega una nueva puntuación"""
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        nueva_puntuacion = {
            "nombre": nombre,
            "vida_restante": vida_restante,
            "fecha": fecha
        }

        self.puntuaciones.append(nueva_puntuacion)
        # Ordenar por vida restante (mayor a menor)
        self.puntuaciones.sort(key=lambda x: x["vida_restante"], reverse=True)
        # Mantener solo las top 10
        self.puntuaciones = self.puntuaciones[:10]
        self.guardar_puntuaciones()

    def obtener_top_puntuaciones(self, limite=10):
        """Obtiene las mejores puntuaciones"""
        return self.puntuaciones[:limite]

    def obtener_mejor_puntuacion(self):
        """Obtiene la mejor puntuación"""
        if self.puntuaciones:
            return self.puntuaciones[0]
        return None
