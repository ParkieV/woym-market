import type { ICellEditorComp, ICellRendererComp, ICellRendererFunc } from "ag-grid-enterprise";
import { ImageCellRenderer, MyCellEditor } from "./cell";
import type { DateString } from "$lib/util";

export interface ColumnBase<T> {
    parser?: (s: string) => T | Error;
    formatter?: (val: T | null | undefined) => string;
    cellRenderer?: string | ICellRendererFunc<T> | ICellRendererComp<T>;
    cellEditor?: string | (() => ICellEditorComp<any, T>);
    cellEditorParams?: any | (() => any);
}

export const stringColumn: ColumnBase<string> = { formatter: val => val ?? "", parser: s => s };
export const imageColumn: ColumnBase<string> = {
    ...stringColumn,
    cellRenderer: ImageCellRenderer
};

export class BooleanColumn implements ColumnBase<boolean> {
    cellRenderer = "agCheckboxCellRenderer";
    cellEditor = "agCheckboxCellEditor";
    formatter(val: boolean | null | undefined) {
        if (val === true) return "true";
        if (val === false) return "false";
        return "";
    }
    parser = (s: string) => {
        s = s.trim().toLowerCase();
        if (s === "true" || s === "да" || s === "+" || s === "1") {
            return true;
        }
        if (s === "false" || s === "нет" || s === "-" || s === "0") {
            return false;
        }
        return new Error();
    };
}

export class NumberColumn implements ColumnBase<number> {
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
        if (this.min && num >= this.min) return new Error();
        if (this.max && num <= this.max) return new Error();
        return num;
    }
}

export const intColumn = new NumberColumn({ precision: 0, min: 0 });
export const floatColumn = new NumberColumn({ precision: 2, min: 0 });
export const rubleColumn = postfixColumn(new NumberColumn({ precision: 0, min: 0 }), " ₽", "₽");
export const dollarColumn = postfixColumn(new NumberColumn({ precision: 2, min: 0 }), " $", "$");
export const percentColumn = postfixColumn(new NumberColumn({ precision: 2, min: 0 }), "%");

export function postfixColumn<T extends Object>(
    col: ColumnBase<T>,
    postfix: string,
    ...alts: string[]
): ColumnBase<T> {
    const { parser, formatter } = col;

    let _formatter = formatter
        ? (val: T | null | undefined) => {
              if (val === null || val === undefined) {
                  return formatter.bind(col)(val);
              } else {
                  return `${formatter.bind(col)(val)}${postfix}`;
              }
          }
        : undefined;
    let _parser = parser
        ? (s: string) => {
              s = s.trimEnd();
              const postfixes = [postfix, ...alts].sort((a, b) => b.length - a.length);
              for (const postfix of postfixes) {
                  if (s.endsWith(postfix)) {
                      s = s.substring(0, s.length - postfix.length);
                      break;
                  }
              }
              return parser.bind(col)(s);
          }
        : undefined;

    // Used to keep original prototype, and so not to break `instanceof`
    col.formatter = _formatter;
    col.parser = _parser;

    return col;
}

export class ComboboxColumn<V extends string | number> implements ColumnBase<V> {
    options: { name: string; value: V }[];

    cellEditor: string;
    cellEditorParams: any;

    formatter(val: V | null | undefined) {
        if (val === null || val === undefined) return "N/A";
        return this.options.find(x => x.value === val)?.name ?? "???";
    }

    parser(s: string) {
        s = s.trim();
        if (!this.options.map(x => x.value).includes(s as V)) {
            return new Error();
        }

        const type = typeof this.options[0].value;
        if (type === "number") {
            return Number(s) as V;
        } else if (type === "string") {
            return s as V;
        } else {
            return new Error();
        }
    }

    constructor(options: { name: string; value: V }[]) {
        this.options = options;
        this.cellEditor = "agSelectCellEditor";
        this.cellEditorParams = { values: this.options.map(x => x.value) };
    }
}

export class GroupColumn<T extends Object> implements ColumnBase<T> {
    cellRenderer = "agGroupCellRenderer";
}

export class DateColumn<T extends DateString | Date> implements ColumnBase<T> {
    formatter(val: T | null | undefined) {
        if (val === null || val === undefined) return "N/A";

        let date = val instanceof Date ? val : new Date(val);
        return date.toLocaleDateString("en-GB");
    }
}
