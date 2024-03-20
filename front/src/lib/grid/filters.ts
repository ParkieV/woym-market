import type { OfferBase } from "$lib/data/offers";
import type { OwnStorage } from "$lib/data/own_storage";

/** Creates filter for OfferBase */
export function offerBaseFilter(params: FilterParams): (offer: OfferBase) => boolean {
    const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"] as const;
    const { search, stores, show_hidden } = params;

    return (offer: OfferBase) => {
        if (!show_hidden && offer.hidden) return false;
        if (!passes(offer.name_of_shop, stores)) return false;
        return searchStringInFields(search, SEARCH_FIELDS, offer);
    };

    function passes(value: string, options: { key: string; selected: boolean }[]): boolean {
        for (const option of options) {
            if (option.key == value && !option.selected) {
                return false;
            }
        }
        return true;
    }
}

/** Creates filter for OwnStorage */
export function ownStorageFilter(params: FilterParams): (offer: OwnStorage) => boolean {
    const SEARCH_FIELDS = ["sku", "name", "note_1", "note_2", "note_3"] as const;
    const { search, stores } = params;

    return (storage: OwnStorage) => {
        if (!passes(storage.name_of_shop, stores)) return false;
        return searchStringInFields(search, SEARCH_FIELDS, storage);
    };

    function passes(value: string[], options: { key: string; selected: boolean }[]): boolean {
        if (options.every(x => x.selected)) return true;
        return value.some(val => {
            return options
                .filter(x => x.selected)
                .map(x => x.key)
                .includes(val);
        });
    }
}

/** Parameters used to create a filter. */
export type FilterParams = {
    stores: { key: string; selected: boolean }[];
    search: string;
    show_hidden: boolean;
};

/** Searches provided substring in all keys of an object. */
function searchStringInFields<K extends string>(
    search: string,
    keys: readonly K[],
    obj: Record<K, Object | null | undefined>
): boolean {
    const _search = normalizeString(search);
    for (const key of keys) {
        let val = obj[key];
        if (val === undefined || val === null) continue;
        let s = normalizeString(val.toString());
        if (s.includes(_search)) {
            return true;
        }
    }
    return false;
}

/**
 * Normalizes provided string.
 *
 * Trims whitespace, turns into lowercase and replaces `ё` symbol with `е`.
 * */
function normalizeString(s: string): string {
    return s.trim().toLowerCase().replaceAll("ё", "е");
}
