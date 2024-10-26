import '../css/FilterPanel.css';

const FilterPanel = ({ filters, setFilters, shopMarketOptions, handleResetFilters }) => {

    const handleFilterChange = (name_of_shop, market) => {
        setFilters((prev) => {
            const pairExists = prev.shopMarketPairs.some(
                (pair) => pair.shop === name_of_shop && pair.market === market
            );

            return {
                ...prev,
                shopMarketPairs: pairExists
                    ? prev.shopMarketPairs.filter(
                        (pair) => !(pair.shop === name_of_shop && pair.market === market)
                    )
                    : [...prev.shopMarketPairs, { shop: name_of_shop, market }]
            };
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
                            className={`filter-button ${filters.shopMarketPairs.some(
                                (pair) => pair.shop === item.name && pair.market === item.type
                            )
                                    ? 'active'
                                    : ''
                                }`}
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
