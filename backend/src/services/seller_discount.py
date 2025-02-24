from collections.abc import Mapping

import numpy as np
import pandas as pd


def get_seller_discount_from_page(offers: pd.DataFrame) -> dict[str, float]:
    discounts = {}
    for offer in offers.itertuples():
        if offer.auto_participation_in_promotions:
            if offer.seller_discount__api != offer.old_discount:
                discounts[offer.id] = offer.seller_discount__api
            elif offer.seller_discount != offer.old_discount:
                discounts[offer.id] = offer.seller_discount
        else:
            discounts[offer.id] = offer.seller_discount
    return discounts

def update_discounts(discounts: Mapping[str, float], offers: pd.DataFrame):
    """ Обновления данных о скидках в offers """
    mask = offers['id'].isin(discounts) & (offers['market'] == 'wildberries')
    new_values = offers.loc[mask, 'id'].map(discounts)

    old_seller = offers.loc[mask, 'seller_discount']
    updated_seller = new_values.fillna(old_seller)
    offers.loc[mask, 'seller_discount'] = updated_seller
    offers.loc[mask, 'seller_discount_changed'] = np.where(
        (old_seller == updated_seller) | (old_seller.isna() & updated_seller.isna()),
        False,
        True
    )

    old_old = offers.loc[mask, 'old_discount']
    updated_old = new_values.fillna(old_old)
    offers.loc[mask, 'old_discount'] = updated_old
    offers.loc[mask, 'old_discount_changed'] = np.where(
        (old_old == updated_old) | (old_old.isna() & updated_old.isna()),
        False,
        True
    )
