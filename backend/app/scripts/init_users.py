"""
Script para inicializar usuarios y roles por defecto
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import Permission, Role, User
from sqlalchemy import select


async def init_roles_and_permissions():
    """
    Crea roles y permisos por defecto
    """
    async with AsyncSessionLocal() as db:
        # Verificar si ya existen roles
        result = await db.execute(select(Role))
        existing_roles = result.scalars().all()

        if existing_roles:
            print("⚠️  Los roles ya existen. Saltando inicialización de roles.")
            return

        print("📋 Creando roles por defecto...")

        # Definir páginas disponibles
        pages = ["catalogo", "importers", "configuracion"]

        # Rol: Super Admin (acceso total + permisos especiales)
        super_admin_role = Role(
            name="Super Admin",
            description="Acceso total al sistema con privilegios especiales",
            is_active=True,
        )
        db.add(super_admin_role)
        await db.flush()

        for page in pages:
            permission = Permission(
                role_id=super_admin_role.id, page_name=page, can_access=True
            )
            db.add(permission)

        print("  ✅ Rol 'Super Admin' creado con permisos completos")

        # Rol: Admin (acceso total)
        admin_role = Role(
            name="Admin",
            description="Acceso completo a todas las funcionalidades",
            is_active=True,
        )
        db.add(admin_role)
        await db.flush()

        for page in pages:
            permission = Permission(
                role_id=admin_role.id, page_name=page, can_access=True
            )
            db.add(permission)

        print("  ✅ Rol 'Admin' creado con permisos completos")

        # Rol: Viewer (solo visualización de catálogo)
        viewer_role = Role(
            name="Viewer",
            description="Acceso solo para visualizar el catálogo de productos",
            is_active=True,
        )
        db.add(viewer_role)
        await db.flush()

        permission = Permission(
            role_id=viewer_role.id, page_name="catalogo", can_access=True
        )
        db.add(permission)

        print("  ✅ Rol 'Viewer' creado")

        await db.commit()
        print("✅ Roles y permisos creados exitosamente\n")


async def init_admin_user():
    """
    Crea un usuario administrador por defecto
    """
    async with AsyncSessionLocal() as db:
        # Verificar si existe el usuario admin
        result = await db.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("⚠️  El usuario 'admin' ya existe. Saltando creación de admin.")
            return

        # Obtener el rol de Super Admin
        role_result = await db.execute(select(Role).where(Role.name == "Super Admin"))
        super_admin_role = role_result.scalar_one_or_none()

        print("👤 Creando usuario super administrador...")

        admin_user = User(
            username="admin",
            email="admin@syncar.cl",
            full_name="Super Administrador del Sistema",
            hashed_password=get_password_hash("admin123"),  # 🔐 Cambiar en producción
            is_active=True,
            is_superuser=True,
            role_id=super_admin_role.id if super_admin_role else None,
        )

        db.add(admin_user)
        await db.commit()

        print("  ✅ Usuario 'admin' creado con rol Super Admin")
        print("     📧 Email: admin@syncar.cl")
        print("     🔑 Password: admin123")
        print("     🔒 Tipo: Superusuario")
        print("     ⚠️  IMPORTANTE: Cambiar la contraseña en producción\n")


async def main():
    """
    Función principal
    """
    print("=" * 60)
    print("🚀 Inicializando sistema de usuarios y permisos")
    print("=" * 60)
    print()

    await init_roles_and_permissions()
    await init_admin_user()

    print("=" * 60)
    print("✅ Inicialización completada exitosamente")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
