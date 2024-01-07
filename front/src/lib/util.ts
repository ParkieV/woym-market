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
