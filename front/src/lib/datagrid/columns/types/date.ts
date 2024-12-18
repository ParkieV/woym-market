import type { DateString } from "$lib/util";
import type { ColumnBase } from ".";

export default class DateColumn<T extends DateString | Date> implements ColumnBase<T> {
    formatter(val: T | null | undefined) {
        if (val === null || val === undefined) return "N/A";

        let date = val instanceof Date ? val : new Date(val);
        return date.toLocaleDateString("en-GB");
    }
}
