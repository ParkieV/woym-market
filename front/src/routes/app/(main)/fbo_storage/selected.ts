import type { FboStocks, FboStorage } from "$lib/data/fbo_storage";
import type { ChangeList } from "$lib/datagrid/plugins/changes";
import { num_word } from "$lib/util";
import type { MenuItemDef } from "ag-grid-enterprise";
import { openModal } from "svelte-modals";
import { derived, get, writable } from "svelte/store";
import SetSelectedWindow from "./SetSelectedWindow.svelte";
import { fboOffersSelection, fboStorageSelection } from "../state";

export function selectedContextMenuItems(
    changes: ChangeList<FboStocks, "id">,
    innerChanges: ChangeList<FboStorage, "id">
): MenuItemDef[] {
    return [
        {
            name: "Мин. остаток",
            icon: icon("/arrow-line-down.svg"),
            tooltip: "Установить минимальный остаток у выделенных складов и товаров.",
            disabled:
                get(fboOffersSelection.filtered).size === 0 ||
                get(fboStorageSelection.filtered).size === 0,
            action: ({ api }) => {
                openModal(SetSelectedWindow, {
                    grid: api,
                    selectedStocks: fboOffersSelection.filtered,
                    selectedStorage: fboStorageSelection.filtered,
                    changes,
                    innerChanges
                });
            }
        }
    ];
}

const icon = (src: string) => `<img src="${src}" style="width: 16px; margin-bottom: -3px;" />`;

export let selectedDisplayInfo = derived(
    [fboOffersSelection.filtered, fboStorageSelection.filtered],
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
