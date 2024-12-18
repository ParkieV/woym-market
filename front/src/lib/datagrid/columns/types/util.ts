import type { ColumnBase } from ".";

/**
 * Wraps column to handle postfixes and prefixes in parser and formatter.
 *
 * @param col Column to wrap
 * @param postfix Primary postfix that will be added in formatter.
 * @param alts Alternative postfixes that will be recognized during parsing.
 * */
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
