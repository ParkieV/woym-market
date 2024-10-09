export class Cache<T, ARGS extends unknown[] = []> {
    public constructor(
        protected readonly getter: Getter<T, ARGS>,
        public labels: string[] = []
    ) {
        caches.push(this);
    }

    private data: T | typeof NOT_LOADED = NOT_LOADED;

    public async get(...args: ARGS): Promise<T> {
        if (this.data === NOT_LOADED) {
            this.data = await this.getter(...args);
        }
        return this.data;
    }

    public get isCached() {
        return this.data !== NOT_LOADED;
    }

    public async invalidate() {
        this.data = NOT_LOADED;
    }

    public static async invalidate(selector: string) {
        await Promise.all(caches.filter(c => c.labels.includes(selector)).map(c => c.invalidate()));
    }

    public static async invalidateAll() {
        await Promise.all(caches.map(c => c.invalidate()));
    }
}
const caches: Cache<any>[] = [];

type Getter<T, U extends unknown[]> = (...args: U) => T | PromiseLike<T>;

const NOT_LOADED: unique symbol = Symbol();
