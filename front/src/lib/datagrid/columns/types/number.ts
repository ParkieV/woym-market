import type { ColumnBase } from ".";
import { MyCellEditor } from "../../cell";
import { postfixColumn } from "./util";

export default class NumberColumn implements ColumnBase<number> {
    precision?: number;
    min?: number;
    max?: number;

    constructor(init: { precision?: number; min?: number; max?: number }) {
        this.precision = init.precision;
        this.min = init.min;
        this.max = init.max;
    }

    cellEditor = MyCellEditor;

    formatter(val: number | null | undefined) {
        if (val === null || val === undefined) {
            return "N/A";
        }
        if (this.precision === undefined) {
            return val.toString();
        } else {
            return val.toFixed(this.precision);
        }
    }

    parser(s: string) {
        const regex = /^[\d ]+([.,][\d ]*)?$/;
        if (!regex.test(s)) return new Error();

        let num = Number.parseFloat(s.trim().replaceAll(",", ".").replaceAll(" ", ""));
        if (this.precision) {
            // FIXME: 0.005-ish values are handled incorrectly
            num = Number.parseFloat(num.toFixed(this.precision));
        }
        if (!Number.isFinite(num)) return new Error();
        if (this.min && num <= this.min) return new Error();
        if (this.max && num >= this.max) return new Error();
        return num;
    }

    classes = () => ["ag-right-aligned-cell"];
}

export const intColumn = new NumberColumn({ precision: 0, min: 0 });
export const floatColumn = new NumberColumn({ precision: 3, min: 0 });
export const rubleColumn = postfixColumn(new NumberColumn({ precision: 0, min: 0 }), " ₽", "₽");
export const dollarColumn = postfixColumn(new NumberColumn({ precision: 2, min: 0 }), " $", "$");
export const percentColumn = postfixColumn(new NumberColumn({ precision: 2, min: 0 }), "%");
