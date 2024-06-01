import type { ICellEditorComp, ICellRendererComp, ICellRendererFunc } from "ag-grid-enterprise";

import ImageColumn from "./image";
import StringColumn from "./string";
import NumberColumn, {
    dollarColumn,
    floatColumn,
    intColumn,
    percentColumn,
    rubleColumn
} from "./number";
import BooleanColumn from "./boolean";
import ComboboxColumn from "./combobox";
import DateColumn from "./date";
import GroupColumn from "./group";

export {
    StringColumn,
    ImageColumn,
    NumberColumn,
    BooleanColumn,
    ComboboxColumn,
    DateColumn,
    GroupColumn,
    dollarColumn,
    floatColumn,
    intColumn,
    percentColumn,
    rubleColumn
};

/** Interface that is implemented by any column type. */
export interface ColumnBase<T> {
    parser?: (s: string) => T | Error;
    formatter?: (val: T | null | undefined) => string;

    cellRenderer?: string | ICellRendererFunc<T> | ICellRendererComp<T>;
    cellEditor?: string | (() => ICellEditorComp<any, T>);
    cellEditorParams?: any | (() => any);

    /** Gets list of classes that should be added to the column of that type. */
    classes?: () => string[];
}
