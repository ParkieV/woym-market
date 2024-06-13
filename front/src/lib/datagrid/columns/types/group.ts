import type { ColumnBase } from ".";

export default class GroupColumn<T extends Object> implements ColumnBase<T> {
    cellRenderer = "agGroupCellRenderer";
}
