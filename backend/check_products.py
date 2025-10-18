import asyncio
import sys

sys.path.insert(0, ".")
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://admin:admin123@localhost:5432/syncar"


async def check_products():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        from app.models import Product

        result = await session.execute(
            select(Product)
            .where(Product.importer_id == 4)
            .order_by(Product.updated_at.desc())
            .limit(4)
        )
        products = result.scalars().all()

        print(f"\n📦 Encontrados {len(products)} productos de EMASA:\n")

        for p in products:
            print(f"SKU: {p.sku}")
            print(f"  Nombre: {p.name}")
            print(f"  Marca: {p.brand}")
            print(f"  Imágenes: {len(p.images) if p.images else 0}")
            print(f"  extra_data: {p.extra_data}")

            if p.extra_data:
                print(f"  extra_data keys: {list(p.extra_data.keys())}")

                if "applications" in p.extra_data:
                    apps = p.extra_data["applications"]
                    print(
                        f"  ✅ Applications: {len(apps) if isinstance(apps, list) else 'no es lista'}"
                    )
                    if isinstance(apps, list) and apps:
                        print(
                            f"      Primera app: {json.dumps(apps[0], indent=10, ensure_ascii=False)}"
                        )
                else:
                    print(f'  ❌ NO tiene "applications" en extra_data')
            else:
                print(f"  ❌ extra_data es None o vacío")
            print("-" * 80)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_products())
