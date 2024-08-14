import type { Market } from "$lib/data/markets";
import { writable, type Writable } from "svelte/store";
import type { ShopOption } from "./ShopsFilter.svelte";
import type { MultiFilterEntry } from "./MultiFilter.svelte";

export default class Filter {
    constructor() {
        this.state = writable(this.createState());
        this.set = this.state.set;
        this.update = this.state.update;
        this.subscribe = this.state.subscribe;
    }

    private state: Writable<FilterState>;
    private markets: Market[] = [];

    public readonly set;
    public readonly update;
    public readonly subscribe;

    public init(markets: Market[]) {
        this.markets = markets;
        this.set(this.createState());
    }

    public reset() {
        this.set(this.createState());
    }

    private createState(): FilterState {
        return {
            search: "",
            shops: this.markets.map(x => ({
                id: x.id,
                name: x.name,
                market: x.type,
                selected: true
            })),
            showHidden: false,
            supplierAvailable: null,
            hideUnmarkedWarehouses: false,
            attentionMarks: {
                targetPrice: {
                    name: "Целевая цена",
                    tooltip: "«Текущая цена» не равна «Целевая цена» (жёлтый)",
                    enabled: false
                },
                stopPrice: {
                    name: "Стоп цена",
                    tooltip:
                        "«Ваша цена по акции» / «Целевая цена» / «Текущая цена» ниже «Стоп цена» (красный)",
                    enabled: false
                }
            }
        };
    }
}

type FilterState = {
    search: string;
    shops: ShopOption[];
    showHidden: boolean;
    supplierAvailable: boolean | null;
    hideUnmarkedWarehouses: boolean;
    attentionMarks: AttentionMarks;
};

type AttentionMarks = {
    targetPrice: MultiFilterEntry;
    stopPrice: MultiFilterEntry;
};
