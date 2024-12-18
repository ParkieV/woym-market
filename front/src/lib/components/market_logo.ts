import type { Market } from "$lib/data/markets";

export default function marketLogo(market: string | Market): string | undefined {
    if (typeof market !== "string") market = market.type;
    if (market === "yandex") {
        return "/markets/yandex.svg";
    } else if (market === "ozon") {
        return "/markets/ozon.svg";
    } else if (market === "wildberries") {
        return "/markets/wildberries.jpeg";
    } else {
        return undefined;
    }
}
