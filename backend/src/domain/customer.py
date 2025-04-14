from sqlalchemy.ext.asyncio import AsyncSession



async def set_target_price(session: AsyncSession, vendor_code_list: dict[int, tuple[str, int]]):
    for vendor_code in vendor_code_list:
        pass

