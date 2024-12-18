import type { ICellRendererParams } from "ag-grid-enterprise";
import StringColumn from "./string";
import type { ColumnBase } from ".";

export default class ImageColumn extends StringColumn implements ColumnBase<string> {
    cellRenderer({ value }: ICellRendererParams) {
        return value != null ? `<img src="${value}" />` : "";
    }

    classes = () => ["image"];
}
