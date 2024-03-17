import type { ICellEditorComp, ICellRendererFunc } from "ag-grid-enterprise";
import Editor from "./Editor.svelte";

export const ImageCellRenderer: ICellRendererFunc<string> = ({ value }) =>
    value != null ? `<img src="${value}" />` : "";

export function MyCellEditor<T>(): ICellEditorComp<any, T, any> {
    let container: HTMLDivElement;
    let editor: Editor;

    return {
        init(params) {
            container = document.createElement("div");
            container.style.display = "contents";

            editor = new Editor({ target: container, props: { params } });
        },
        destroy() {
            editor.$destroy();
        },

        getGui: () => container,
        afterGuiAttached: () => editor.afterGuiAttached(),

        getValue: () => editor.getValue(),
        isCancelAfterEnd: () => editor.isCancelAfterEnd()
    };
}
