import '../css/FilterPanel.css';

const FilterPanel = ({ filters, setFilters, shopMarketOptions, handleResetFilters }) => {

    const handleFilterChange = (name_of_shop, market) => {
        setFilters((prev) => {
            const combinationExists = prev.shop.some((shop, index) => 
                shop === name_of_shop && prev.market[index] === market
            );
    
            if (combinationExists) {
                const updatedShops = prev.shop.filter((shop, index) => 
                    !(shop === name_of_shop && prev.market[index] === market)
                );
                const updatedMarkets = prev.market.filter((mkt, index) => 
                    !(prev.shop[index] === name_of_shop && mkt === market)
                );
    
                return {
                    ...prev,
                    shop: updatedShops,
                    market: updatedMarkets
                };
            } else {
                return {
                    ...prev,
                    shop: [...prev.shop, name_of_shop],
                    market: [...prev.market, market]
                };
            }
        });
    };

    const handleSearchChange = (e) => {
        setFilters((prev) => ({
            ...prev,
            search: e.target.value,
        }));
    };

    return (
        <div className="filter-panel">
            <div className="filter-left">
                <label>Фильтр по магазину и маркету:</label>
                <div className="filter-buttons">
                    {shopMarketOptions.map((item) => (
                        <button
                            key={`${item.name}-${item.type}`}
                            onClick={() => handleFilterChange(item.name, item.type)}
                            className={`filter-button ${filters.shop.includes(item.name) && filters.market.includes(item.type) ? 'active' : ''}`}
                        >
                            {`${item.name} (${item.type})`}
                        </button>
                    ))}
                </div>
            </div>

            <div className="filter-right">
                <input
                    type="text"
                    value={filters.search}
                    onChange={handleSearchChange}
                    placeholder="Поиск..."
                    className="search-input"
                />
                <button onClick={handleResetFilters} className="reset-button">Сбросить фильтры</button>
            </div>
        </div>
    );
};

export default FilterPanel;
