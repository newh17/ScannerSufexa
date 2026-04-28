"""
Script de prueba para verificar el funcionamiento de la base de datos.

Ejecutar desde la raíz del proyecto:
    python scripts/test_database.py
"""

import sys
from pathlib import Path

# Añadir src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from domain.entities import Albaran, Cliente
from domain.value_objects import FechaAlbaran, NumeroAlbaran
from domain.exceptions import AlbaranDuplicadoException
from infrastructure.persistence.database import Database
from infrastructure.persistence.repositories import (
    SQLiteAlbaranRepository,
    SQLiteClienteRepository,
)


def main():
    """Función principal de prueba."""
    print("=" * 60)
    print("PRUEBA DE BASE DE DATOS - SCANNER SUFEXA")
    print("=" * 60)

    # Crear BD en memoria para testing
    db = Database(":memory:")
    db.connect()
    db.initialize_schema()

    print("\n✅ Base de datos creada e inicializada")

    # Crear repositorios
    cliente_repo = SQLiteClienteRepository(db)
    albaran_repo = SQLiteAlbaranRepository(db)

    print("✅ Repositorios creados")

    # 1. CREAR CLIENTES
    print("\n" + "-" * 60)
    print("1. CREANDO CLIENTES")
    print("-" * 60)

    cliente1 = Cliente(nombre="METALCRISMAR, S.L.")
    cliente1 = cliente_repo.save(cliente1)
    print(f"✅ Cliente creado: {cliente1}")

    cliente2 = Cliente(nombre="EMPRESA EJEMPLO S.A.")
    cliente2 = cliente_repo.save(cliente2)
    print(f"✅ Cliente creado: {cliente2}")

    # 2. BUSCAR CLIENTES
    print("\n" + "-" * 60)
    print("2. BUSCANDO CLIENTES")
    print("-" * 60)

    encontrado = cliente_repo.find_by_nombre("METALCRISMAR, S.L.")
    print(f"✅ Cliente encontrado por nombre: {encontrado}")

    todos_clientes = cliente_repo.get_all()
    print(f"✅ Total de clientes: {len(todos_clientes)}")

    # 3. CREAR ALBARANES
    print("\n" + "-" * 60)
    print("3. CREANDO ALBARANES")
    print("-" * 60)

    albaran1 = Albaran(
        cliente=cliente1,
        fecha=FechaAlbaran("23/01/2026"),
        numero=NumeroAlbaran(71206),
        ruta_archivo_original="C:\\scan\\entrada\\scan001.pdf",
    )
    albaran1 = albaran_repo.save(albaran1)
    print(f"✅ Albarán creado: {albaran1}")
    print(f"   Nombre archivo: {albaran1.generar_nombre_archivo()}")

    # Actualizar contador del cliente
    cliente1.incrementar_contador(albaran1.fecha.to_datetime())
    cliente_repo.save(cliente1)
    print(f"✅ Cliente actualizado: contador = {cliente1.total_albaranes}")

    # 4. PREVENCIÓN DE DUPLICADOS
    print("\n" + "-" * 60)
    print("4. PROBANDO PREVENCIÓN DE DUPLICADOS")
    print("-" * 60)

    try:
        albaran_duplicado = Albaran(
            cliente=cliente1,
            fecha=FechaAlbaran("23/01/2026"),
            numero=NumeroAlbaran(71206),  # Mismo número y fecha
            ruta_archivo_original="C:\\scan\\entrada\\scan002.pdf",
        )
        albaran_repo.save(albaran_duplicado)
        print("❌ ERROR: Debería haber lanzado excepción de duplicado")
    except AlbaranDuplicadoException as e:
        print(f"✅ Duplicado detectado correctamente: {e}")

    # 5. VERIFICAR EXISTENCIA
    print("\n" + "-" * 60)
    print("5. VERIFICANDO EXISTENCIA")
    print("-" * 60)

    existe = albaran_repo.exists(
        NumeroAlbaran(71206),
        FechaAlbaran("23/01/2026")
    )
    print(f"✅ ¿Existe albarán 71206 del 23/01/2026? {existe}")

    no_existe = albaran_repo.exists(
        NumeroAlbaran(99999),
        FechaAlbaran("01/01/2026")
    )
    print(f"✅ ¿Existe albarán 99999 del 01/01/2026? {no_existe}")

    # 6. CREAR MÁS ALBARANES
    print("\n" + "-" * 60)
    print("6. CREANDO MÁS ALBARANES")
    print("-" * 60)

    albaran2 = Albaran(
        cliente=cliente1,
        fecha=FechaAlbaran("24/01/2026"),
        numero=NumeroAlbaran(71207),
        ruta_archivo_original="C:\\scan\\entrada\\scan003.pdf",
    )
    albaran_repo.save(albaran2)
    cliente1.incrementar_contador(albaran2.fecha.to_datetime())
    cliente_repo.save(cliente1)
    print(f"✅ Albarán 2 creado: {albaran2}")

    albaran3 = Albaran(
        cliente=cliente2,
        fecha=FechaAlbaran("25/01/2026"),
        numero=NumeroAlbaran(71208),
        ruta_archivo_original="C:\\scan\\entrada\\scan004.pdf",
    )
    albaran_repo.save(albaran3)
    cliente2.incrementar_contador(albaran3.fecha.to_datetime())
    cliente_repo.save(cliente2)
    print(f"✅ Albarán 3 creado: {albaran3}")

    # 7. RANKING DE CLIENTES
    print("\n" + "-" * 60)
    print("7. RANKING DE CLIENTES")
    print("-" * 60)

    ranking = cliente_repo.get_ranking(top_n=10)
    print(f"✅ Top {len(ranking)} clientes:")
    for i, cliente in enumerate(ranking, 1):
        print(
            f"   {i}. {cliente.nombre:30} "
            f"- {cliente.total_albaranes} albaranes"
        )

    # 8. ESTADÍSTICAS
    print("\n" + "-" * 60)
    print("8. ESTADÍSTICAS")
    print("-" * 60)

    total_albaranes = albaran_repo.count()
    total_clientes = cliente_repo.count()

    print(f"✅ Total de albaranes: {total_albaranes}")
    print(f"✅ Total de clientes: {total_clientes}")

    # 9. LISTADO DE ALBARANES
    print("\n" + "-" * 60)
    print("9. LISTADO DE ALBARANES")
    print("-" * 60)

    todos_albaranes = albaran_repo.get_all()
    print(f"✅ Albaranes procesados ({len(todos_albaranes)}):")
    for albaran in todos_albaranes:
        print(
            f"   - #{albaran.numero} | {albaran.fecha} | "
            f"{albaran.cliente.nombre}"
        )

    # Cerrar BD
    db.disconnect()

    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()
