export function toEntries<T>(arr: T[]) {
    return arr.map((value, index) => [index, value] as const);
}
