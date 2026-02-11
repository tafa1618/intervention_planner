
import asyncio
from database import AsyncSessionLocal
from services.ingestion import ingest_programmes_data

async def main():
    async with AsyncSessionLocal() as session:
        print("Starting ingestion...")
        await ingest_programmes_data("data/Programmes.xlsx", session)
        await session.commit()
        print("Ingestion complete.")

if __name__ == "__main__":
    asyncio.run(main())
