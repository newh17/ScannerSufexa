"""
Servicio para operaciones seguras del sistema de archivos.
"""

import shutil
from pathlib import Path
from typing import Optional


class FileSystemService:
    """
    Servicio que gestiona operaciones del sistema de archivos.

    Responsabilidades:
    - Mover archivos de forma segura
    - Renombrar archivos
    - Crear carpetas de clientes
    - Mover archivos con error a carpeta de errores
    - Prevenir sobrescrituras accidentales
    """

    def __init__(
        self,
        carpeta_salida_base: str,
        carpeta_errores: str
    ):
        """
        Inicializa el servicio de sistema de archivos.

        Args:
            carpeta_salida_base: Carpeta base donde se guardan los albaranes
                                (ej: C:\\albaranes)
            carpeta_errores: Carpeta donde se mueven los archivos con error
                           (ej: C:\\albaranes\\errores)
        """
        self.carpeta_salida_base = Path(carpeta_salida_base)
        self.carpeta_errores = Path(carpeta_errores)

        # Crear carpetas si no existen
        self._asegurar_carpetas()

    def _asegurar_carpetas(self):
        """Crea las carpetas base si no existen."""
        self.carpeta_salida_base.mkdir(parents=True, exist_ok=True)
        self.carpeta_errores.mkdir(parents=True, exist_ok=True)

    def mover_a_carpeta_cliente(
        self,
        archivo_origen: str,
        nombre_cliente: str,
        nuevo_nombre: str
    ) -> str:
        """
        Mueve un archivo a la carpeta del cliente con el nuevo nombre.

        Pasos:
        1. Crear carpeta del cliente si no existe
        2. Generar ruta destino
        3. Verificar que no exista (prevenir sobrescritura)
        4. Mover archivo

        Args:
            archivo_origen: Ruta del archivo original
            nombre_cliente: Nombre del cliente (usado como carpeta)
            nuevo_nombre: Nuevo nombre del archivo (ej: CLIENTE_FECHA_NUM.pdf)

        Returns:
            str: Ruta del archivo movido

        Raises:
            FileNotFoundError: Si el archivo origen no existe
            FileExistsError: Si ya existe un archivo con ese nombre
            IOError: Si hay un error al mover
        """
        origen = Path(archivo_origen)

        if not origen.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {archivo_origen}")

        # Crear carpeta del cliente
        carpeta_cliente = self.carpeta_salida_base / nombre_cliente
        carpeta_cliente.mkdir(parents=True, exist_ok=True)

        # Ruta destino
        destino = carpeta_cliente / nuevo_nombre

        # Verificar que no exista
        if destino.exists():
            raise FileExistsError(
                f"Ya existe un archivo en: {destino}\n"
                "Este albarán probablemente es un duplicado."
            )

        # Mover archivo
        try:
            shutil.move(str(origen), str(destino))
            return str(destino)
        except Exception as e:
            raise IOError(f"Error al mover archivo: {e}")

    def mover_a_errores(
        self,
        archivo_origen: str,
        razon: Optional[str] = None
    ) -> str:
        """
        Mueve un archivo a la carpeta de errores.

        Si hay conflicto de nombres, añade un sufijo.

        Args:
            archivo_origen: Ruta del archivo original
            razon: Razón del error (opcional, se añade al nombre)

        Returns:
            str: Ruta del archivo en carpeta de errores

        Raises:
            FileNotFoundError: Si el archivo origen no existe
            IOError: Si hay un error al mover
        """
        origen = Path(archivo_origen)

        if not origen.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {archivo_origen}")

        # Generar nombre con prefijo de error
        nombre_base = origen.stem
        extension = origen.suffix

        if razon:
            # Sanitizar razón para nombre de archivo
            razon_limpia = razon.replace(' ', '_')[:30]
            nuevo_nombre = f"ERROR_{razon_limpia}_{nombre_base}{extension}"
        else:
            nuevo_nombre = f"ERROR_{nombre_base}{extension}"

        destino = self.carpeta_errores / nuevo_nombre

        # Si existe, añadir sufijo numérico
        destino = self._obtener_nombre_unico(destino)

        # Mover archivo
        try:
            shutil.move(str(origen), str(destino))
            return str(destino)
        except Exception as e:
            raise IOError(f"Error al mover archivo a errores: {e}")

    def _obtener_nombre_unico(self, ruta: Path) -> Path:
        """
        Genera un nombre único si el archivo ya existe.

        Si archivo.pdf existe, genera archivo_1.pdf, archivo_2.pdf, etc.

        Args:
            ruta: Ruta propuesta

        Returns:
            Path: Ruta con nombre único
        """
        if not ruta.exists():
            return ruta

        nombre_base = ruta.stem
        extension = ruta.suffix
        carpeta = ruta.parent
        contador = 1

        while True:
            nuevo_nombre = f"{nombre_base}_{contador}{extension}"
            nueva_ruta = carpeta / nuevo_nombre

            if not nueva_ruta.exists():
                return nueva_ruta

            contador += 1

            # Límite de seguridad
            if contador > 1000:
                raise RuntimeError(
                    "No se pudo generar un nombre único después de 1000 intentos"
                )

    def renombrar_archivo(
        self,
        archivo: str,
        nuevo_nombre: str
    ) -> str:
        """
        Renombra un archivo en su misma carpeta.

        Args:
            archivo: Ruta del archivo actual
            nuevo_nombre: Nuevo nombre (solo el nombre, no la ruta completa)

        Returns:
            str: Nueva ruta del archivo

        Raises:
            FileNotFoundError: Si el archivo no existe
            FileExistsError: Si ya existe un archivo con el nuevo nombre
        """
        origen = Path(archivo)

        if not origen.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {archivo}")

        destino = origen.parent / nuevo_nombre

        if destino.exists():
            raise FileExistsError(f"Ya existe: {destino}")

        origen.rename(destino)
        return str(destino)

    def copiar_archivo(
        self,
        archivo_origen: str,
        carpeta_destino: str,
        nuevo_nombre: Optional[str] = None
    ) -> str:
        """
        Copia un archivo a una carpeta destino.

        Args:
            archivo_origen: Ruta del archivo a copiar
            carpeta_destino: Carpeta donde copiar
            nuevo_nombre: Nuevo nombre (opcional, usa el original si es None)

        Returns:
            str: Ruta del archivo copiado

        Raises:
            FileNotFoundError: Si el archivo origen no existe
        """
        origen = Path(archivo_origen)

        if not origen.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {archivo_origen}")

        carpeta_dest = Path(carpeta_destino)
        carpeta_dest.mkdir(parents=True, exist_ok=True)

        nombre = nuevo_nombre if nuevo_nombre else origen.name
        destino = carpeta_dest / nombre

        shutil.copy2(str(origen), str(destino))
        return str(destino)

    def eliminar_archivo(self, archivo: str) -> bool:
        """
        Elimina un archivo.

        Args:
            archivo: Ruta del archivo a eliminar

        Returns:
            bool: True si se eliminó, False si no existía
        """
        archivo_path = Path(archivo)

        if not archivo_path.exists():
            return False

        archivo_path.unlink()
        return True

    def obtener_tamano(self, archivo: str) -> int:
        """
        Obtiene el tamaño de un archivo en bytes.

        Args:
            archivo: Ruta del archivo

        Returns:
            int: Tamaño en bytes

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        archivo_path = Path(archivo)

        if not archivo_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {archivo}")

        return archivo_path.stat().st_size

    def existe_archivo(self, archivo: str) -> bool:
        """
        Verifica si un archivo existe.

        Args:
            archivo: Ruta del archivo

        Returns:
            bool: True si existe, False en caso contrario
        """
        return Path(archivo).exists()
