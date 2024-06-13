import type { FboStocks, FboStorage } from "$lib/data/fbo_storage";
import type { ChangeList } from "$lib/datagrid/plugins/changes";
import { num_word } from "$lib/util";
import type { MenuItemDef } from "ag-grid-enterprise";
import { openModal } from "svelte-modals";
import { derived, get, writable } from "svelte/store";
import SetSelectedWindow from "./SetSelectedWindow.svelte";

export let selectedStocks = writable(new Map<FboStocks, FboStocks>());
export let selectedStorage = writable(new Map<number, FboStorage>());

export function selectedContextMenuItems(
    changes: ChangeList<FboStocks, "id">,
    innerChanges: ChangeList<FboStorage, "id">
): MenuItemDef[] {
    return [
        {
            name: "Мин. остаток",
            icon: '<img src="/arrow-line-down.svg" style="width: 16px;" />',
            tooltip: "Установить минимальный остаток у выделенных складов и товаров.",
            disabled: get(selectedStocks).size === 0 || get(selectedStorage).size === 0,
            action: ({ api }) => {
                openModal(SetSelectedWindow, {
                    grid: api,
                    selectedStocks,
                    selectedStorage,
                    changes,
                    innerChanges
                });
            }
        }
    ];
}

export let selectedDisplayInfo = derived(
    [selectedStocks, selectedStorage],
    ([selectedStocks, selectedStorage]) => {
        let stocks =
            selectedStocks.size !== 0
                ? `${selectedStocks.size} ${num_word(selectedStocks.size, [
                      "товар",
                      "товара",
                      "товаров"
                  ])}`
                : null;
        let storage =
            selectedStorage.size !== 0
                ? `${selectedStorage.size} ${num_word(selectedStorage.size, [
                      "склад",
                      "склада",
                      "складов"
                  ])}`
                : null;

        if (stocks && storage) {
            let word = num_word(selectedStocks.size, ["Выбран", "Выбрано", "Выбрано"]);
            return `${word} ${stocks} и ${storage}`;
        } else {
            let word = num_word(selectedStocks.size + selectedStorage.size, [
                "Выбран",
                "Выбрано",
                "Выбрано"
            ]);
            return `${word} ${stocks ?? storage}`;
        }
    }
);
