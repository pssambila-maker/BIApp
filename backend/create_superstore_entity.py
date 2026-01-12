"""
Create Superstore semantic entity with dimensions and measures
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models import User
from app.models.semantic import SemanticEntity, SemanticDimension, SemanticMeasure

async def create_superstore_entity():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get testuser
        result = await session.execute(
            select(User).where(User.username == 'testuser')
        )
        user = result.scalar_one_or_none()

        if not user:
            print("Error: testuser not found")
            return

        print(f"Creating Superstore entity for user: {user.username}")

        # Create Superstore entity
        entity = SemanticEntity(
            owner_id=user.id,
            name='Superstore',
            plural_name='Superstore Orders',
            description='Complete Superstore dataset with orders, customers, products, and financial metrics',
            primary_table='superstore',
            is_certified=True,
            tags=['sales', 'orders', 'retail', 'analytics']
        )
        session.add(entity)
        await session.flush()

        print(f"Created entity: {entity.name} (ID: {entity.id})")

        # Create Dimensions
        dimensions = [
            # Date dimensions
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Order Date',
                sql_column='order_date',
                data_type='date',
                display_format='%Y-%m-%d',
                is_hidden=False,
                display_order=1
            ),
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Ship Date',
                sql_column='ship_date',
                data_type='date',
                display_format='%Y-%m-%d',
                is_hidden=False,
                display_order=2
            ),

            # Customer dimensions
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Customer Name',
                sql_column='customer_name',
                data_type='string',
                is_hidden=False,
                display_order=3
            ),
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Customer Segment',
                sql_column='segment',
                data_type='string',
                is_hidden=False,
                display_order=4
            ),

            # Product dimensions
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Product Name',
                sql_column='product_name',
                data_type='string',
                is_hidden=False,
                display_order=5
            ),
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Category',
                sql_column='category',
                data_type='string',
                is_hidden=False,
                display_order=6
            ),
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Sub-Category',
                sql_column='sub_category',
                data_type='string',
                is_hidden=False,
                display_order=7
            ),

            # Location dimensions
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Region',
                sql_column='region',
                data_type='string',
                is_hidden=False,
                display_order=8
            ),
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='State',
                sql_column='state',
                data_type='string',
                is_hidden=False,
                display_order=9
            ),
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='City',
                sql_column='city',
                data_type='string',
                is_hidden=False,
                display_order=10
            ),

            # Other dimensions
            SemanticDimension(
                semantic_entity_id=entity.id,
                name='Ship Mode',
                sql_column='ship_mode',
                data_type='string',
                is_hidden=False,
                display_order=11
            ),
        ]

        session.add_all(dimensions)
        print(f"Added {len(dimensions)} dimensions")

        # Create Measures
        measures = [
            SemanticMeasure(
                semantic_entity_id=entity.id,
                name='Total Sales',
                aggregation_function='SUM',
                base_column='sales',
                format='currency',
                default_format_pattern='$#,##0.00',
                is_hidden=False
            ),
            SemanticMeasure(
                semantic_entity_id=entity.id,
                name='Total Profit',
                aggregation_function='SUM',
                base_column='profit',
                format='currency',
                default_format_pattern='$#,##0.00',
                is_hidden=False
            ),
            SemanticMeasure(
                semantic_entity_id=entity.id,
                name='Total Quantity',
                aggregation_function='SUM',
                base_column='quantity',
                format='number',
                default_format_pattern='#,##0',
                is_hidden=False
            ),
            SemanticMeasure(
                semantic_entity_id=entity.id,
                name='Average Discount',
                aggregation_function='AVG',
                base_column='discount',
                format='percent',
                default_format_pattern='0.0%',
                is_hidden=False
            ),
            SemanticMeasure(
                semantic_entity_id=entity.id,
                name='Number of Orders',
                aggregation_function='COUNT',
                base_column='order_id',
                format='number',
                default_format_pattern='#,##0',
                is_hidden=False
            ),
        ]

        session.add_all(measures)
        print(f"Added {len(measures)} measures")

        await session.commit()

        print("\n✓ Superstore entity created successfully!")
        print(f"  Entity: {entity.name}")
        print(f"  Dimensions: {len(dimensions)}")
        print(f"  Measures: {len(measures)}")
        print(f"\nYou can now use this entity in the Query Builder at:")
        print(f"  http://localhost:3000/query-builder")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_superstore_entity())
