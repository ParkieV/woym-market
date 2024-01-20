/**
 * Converts a numeric value to a corresponding word form.
 * @param value - The numeric value to be converted.
 * @param words - An array of three strings representing the word forms for singular, plural, and special cases.
 * @returns The word corresponding to the numeric value based on the provided rules.
 */
export function num_word(value: number, words: [string, string, string]) {
    value = Math.abs(value) % 100;
    var num = value % 10;
    if (value > 10 && value < 20) return words[2];
    if (num > 1 && num < 5) return words[1];
    if (num == 1) return words[0];
    return words[2];
}

/** Loads user-selected file as a Blob. */
export async function uploadFile(): Promise<Blob> {
    const input = document.createElement("input");
    input.type = "file";

    let promise = new Promise<Blob>(resolve => {
        input.onchange = async e => {
            let target = e.target as HTMLInputElement;
            let file = target.files![0];
            resolve(file);
        };
    });
    input.click();

    return promise;
}

/** Downloads blob as a file. */
export function downloadFile(blob: Blob, defaultFilename: string) {
    let url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = defaultFilename;
    link.click();
}
