import pandas as pd


async def get_seller_discount_from_page(offers: pd.DataFrame) -> dict[str, float]:
    discounts = {}
    for offer in offers:
        if offer['auto_price_control__api']:
            if offer['seller_discount__api'] != offer['old_discount']:
                discounts[offer['id']] = offer['seller_discount__api']
            elif offer['seller_discount'] != offer['old_discount']:
                discounts[offer['id']] = offer['seller_discount']
        else:
            discounts[offer['id']] = offer['seller_discount']
    return discounts