import type { FboStocks } from "$lib/data/fbo_stocks";
import type { FboStorage } from "$lib/data/fbo_storage";
import { Selection } from "$lib/selection";
import { fboStocksFilter, fboStorageFilter } from "./fbo_storage/filter";

export const fboStorageSelection = new Selection<FboStorage, number>(fboStorageFilter);
export const fboStocksSelection = new Selection<FboStocks, number>(fboStocksFilter);
