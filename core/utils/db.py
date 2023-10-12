import os

import aiopg


async def async_db_session():
    return await aiopg.connect(
        database=os.getenv('POSTGRES_DB', 'autoria'),
        user=os.getenv('POSTGRES_USER', 'AutoRia'),
        password=os.getenv('POSTGRES_PASSWORD', 'AutoRia'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', 5431)
    )


async def create_car_table(session):
    async with session.cursor() as cur:
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS car (
                id SERIAL PRIMARY KEY,
                url VARCHAR,
                title VARCHAR,
                price_usd INT,
                odometer INT,
                username VARCHAR,
                phone_number BIGINT,
                image_url VARCHAR,
                images_count INT,
                car_number VARCHAR,
                car_vin VARCHAR,
                datetime_found TIMESTAMPTZ DEFAULT current_timestamp
            );
        """)


async def table_exists(session):
    async with session.cursor() as cur:
        await cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'car'
            )
        """)
        result = await cur.fetchone()
        return result[0]
