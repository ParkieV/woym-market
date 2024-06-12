import { fetchPlain } from "$lib/fetch";
import { showFetchModals } from "$lib/modal";
import { uploadFile } from "$lib/util";
import type { SimpleImportKind } from "./simple";
import type { WarehouseImportKind } from "./warehouse";

export default abstract class Import {
    public abstract kind: ImportKind;

    public async import(): Promise<{ ok: boolean }> {
        try {
            let blob = await uploadFile();
            let formData = new FormData();
            formData.append("data", blob);

            let url = this.url;
            let promise = fetchPlain(url, {
                method: "POST",
                body: formData
            });
            showFetchModals(promise, "Отправка файла...", "Ошибка импорта");
            await promise;
            return { ok: true };
        } catch {
            return { ok: false };
        }
    }

    protected abstract get url(): string;
    public abstract get valid(): boolean;
}

export type ImportKind = SimpleImportKind | WarehouseImportKind;
