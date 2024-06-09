import type { Market } from "$lib/data/markets";

export default function marketLogo(market: Market): string | undefined {
    if (market.type === "yandex") {
        return "/yandex-market.svg";
    } else if (market.type === "ozon") {
        return "/ozon.svg";
    } else {
        return undefined;
    }
}
