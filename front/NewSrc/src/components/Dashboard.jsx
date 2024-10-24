import React, { useEffect, useState, useMemo } from 'react';
import Sidebar from '../components/Sidebar';
import CatalogTable from '../components/CatalogTable'
import StokcsTable from '../components/MyStocksTable'
import BottomPanel from '../components/BottomPanel';
import ShopDetails from '../components/ShopDetails';
import FilterPanel from '../components/FilterPanel';
import '../css/ShopsView.css';
import Cookies from 'js-cookie';
import YandexIcon from '../icons/yandex.svg';
import OzonIcon from '../icons/ozon.svg';
import wildberriesIcon from '../icons/wildberries.jpeg';

const Dashboard = () => {
    const [lastUpdated, setLastUpdated] = useState('');
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [username, setUserName] = useState('');
    const [shops, setShops] = useState([]);
    const [catalog, setCatalog] = useState([]);
    const [selectedShop, setSelectedShop] = useState(null);
    const [currentView, setCurrentView] = useState('shops');
    const [isLoading, setIsLoading] = useState(false);
    const [editedRows, setEditedRows] = useState(new Set());
    const [editedRows1, setEditedRows1] = useState(new Set());
    const [shopData, setShopData] = useState(null);
    const [originalCatalogData, setOriginalCatalogData] = useState([]);
    const [stocks, setStocks] = useState([]);
    const [originalStocks, setOriginalStocks] = useState([]);
    const [storages, setStorages] = useState([]);
    const [editedStorages, setEditedStorages] = useState(new Map());

    const [filters, setFilters] = useState({
        shop: [],
        market: [],
        search: ''
    });

    const handleResetFilters = () => {
        setFilters({
            shop: [],
            market: [],
            search: ''
        });
    };
    const applyCatalogFilters = (catalogData, filters) => {

        if (!Array.isArray(catalogData)) {
            console.error("catalogData is not an array:", catalogData);
            return [];
        }

        return catalogData.filter(item => {
            const searchValue = filters.search ? filters.search.toLowerCase() : '';

            const matchesSearch = (item.name && item.name.toLowerCase().includes(searchValue)) ||
                (item.search_words && item.search_words.toLowerCase().includes(searchValue));

            const matchesShopAndMarket = item.synchronization.some(sync =>
                filters.shop.includes(sync.name_of_shop) && filters.market.includes(sync.market)
            );

            return matchesSearch && (!filters.shop.length || matchesShopAndMarket);
        });
    };



    const applyStocksFilters = (stocksData, filters) => {
        return stocksData.filter(item => {
            const searchValue = filters.search ? filters.search.toLowerCase() : '';

            const matchesSearch = item.offer.name && item.offer.name.some(name => name.toLowerCase().includes(searchValue));

            const matchesShop = filters.shop.length
                ? item.offer.name_of_shop && item.offer.name_of_shop.some(shop => filters.shop.includes(shop))
                : true;

            const matchesMarket = filters.market.length
                ? item.offer.market && item.offer.market.some(market => filters.market.includes(market))
                : true

            return matchesSearch && matchesShop && matchesMarket;
        });
    };




    useEffect(() => {
        const fetchDataLogs = async () => {
            const token = Cookies.get('token');

            const response = await fetch('https://dev.oy-pro.ru/backend/settings/logs', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                console.error('Ошибка:', response.status, response.statusText);
                return;
            }

            const data = await response.json();
            setLastUpdated(data.updated_at);
        };

        const fetchDataGetMe = async () => {
            const token = Cookies.get('token');

            const response = await fetch('https://dev.oy-pro.ru/backend/users/me', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                console.error('Ошибка:', response.status, response.statusText);
                return;
            }

            const data = await response.json();
            setUserName(data.login);
        };

        fetchShops();
        fetchStorages();
        fetchDataLogs();
        fetchDataGetMe();
    }, []);

    const fetchShops = async () => {
        const token = Cookies.get('token');

        const response = await fetch('https://dev.oy-pro.ru/backend/settings/markets', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Ошибка:', response.status, response.statusText);
            return;
        }

        const data = await response.json();
        setShops(data);
    };

    const fetchCatalog = async () => {
        const token = Cookies.get('token');
        const response = await fetch('https://dev.oy-pro.ru/backend/catalog', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        setCatalog(result);
        setOriginalCatalogData(JSON.parse(JSON.stringify(result)));

    };

    const fetchStock = async () => {
        const token = Cookies.get('token');
        const response = await fetch('https://dev.oy-pro.ru/backend/stocks/own-storage', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        setStocks(result);
        setOriginalStocks(JSON.parse(JSON.stringify(result)));

    };

    const fetchStorages = async () => {
        const token = Cookies.get('token');
        const response = await fetch('https://dev.oy-pro.ru/backend/stocks/own-storage/places', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        setStorages(result);

    };

    const handleCancel = () => {
        if (currentView === 'shops') {
            setShopData(selectedShop);
        } else if (currentView === 'catalog') {
            setEditedRows(new Set());
            setCatalog(JSON.parse(JSON.stringify(originalCatalogData)));
        } else if (currentView === 'stocks') {
            setEditedRows(new Set());
            setStocks(JSON.parse(JSON.stringify(originalStocks)));
        }

    };

    const filteredCatalog = useMemo(() => applyCatalogFilters(catalog, filters), [catalog, filters]);
    const filteredStocks = useMemo(() => applyStocksFilters(stocks, filters), [stocks, filters]);

    const handleSave = async () => {
        const token = Cookies.get('token');

        setIsLoading(true);

        try {
            if (currentView === 'shops') {
                const response = await fetch(`https://dev.oy-pro.ru/backend/settings/markets/${selectedShop.id}`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(shopData),
                });

                if (response.ok) {
                    alert('Данные магазина успешно сохранены!');
                } else {
                    console.error('Ошибка при сохранении данных магазина');
                }
            } else if (currentView === 'catalog') {
                const changedRows = Array.from(editedRows1).map((rowIndex) => catalog[rowIndex]);
                const response = await fetch('https://dev.oy-pro.ru/backend/catalog', {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(changedRows),
                });

                if (response.ok) {
                    setEditedRows(new Set());
                    setEditedRows1(new Set());
                    alert('Данные каталога успешно сохранены!');
                } else {
                    console.error('Ошибка при сохранении данных каталога');
                }
            } else if (currentView === 'stocks') {
                const changedStorages = Array.from(editedStorages.values());
                const response = await fetch('https://dev.oy-pro.ru/backend/stocks/own-storage', {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(changedStorages),
                });

                if (response.ok) {
                    setEditedRows(new Set());
                    setEditedRows1(new Set());
                    alert('Данные остатков успешно сохранены!');
                } else {
                    console.error('Ошибка при сохранении данных каталога');
                }
            }
        } catch (error) {
            console.error('Ошибка при выполнении запроса:', error);
        } finally {
            if (currentView === 'shops') {
                setIsLoading(false);
                fetchShops();
            } else if (currentView === 'catalog') {
                setIsLoading(false);
                fetchCatalog();
            } else if (currentView === 'stocks') {
                setIsLoading(false);
                fetchStock();
            }
        }
    };


    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const handleShopSelect = (shop) => {
        setSelectedShop(shop);
        setShopData(shop);
    };

    const handleViewChange = (view) => {
        setCurrentView(view);
        setSelectedShop(null);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <div style={{ display: 'flex', flex: 1 }}>
                <Sidebar username={username} isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} handleViewChange={handleViewChange} fetchCatalog={fetchCatalog} fetchStock={fetchStock} />
                <div style={{ flex: 1, marginLeft: isSidebarOpen ? '250px' : '70px', display: 'flex', flexDirection: 'column' }}>
                    {currentView !== 'shops' && (
                        <FilterPanel
                            filters={filters}
                            setFilters={setFilters}
                            shopMarketOptions={shops}
                            handleResetFilters={handleResetFilters}
                        />
                    )}

                    <div style={{ flex: 1, padding: '0px', backgroundColor: '#f0f0f0', color: 'white', overflow: 'hidden' }}>
                        {currentView === 'shops' && (
                            <>
                                {isLoading && (
                                    <div className="loading-overlay">
                                        <div className="loading-spinner"></div>
                                    </div>
                                )}
                                <div className="shop-list-container">
                                    <h2 className="shop-heading">Список магазинов</h2>
                                    <div className="button-container">
                                        {shops.map(shop => (
                                            <button
                                                key={shop.id}
                                                onClick={() => handleShopSelect(shop)}
                                                className={`shop-button ${selectedShop && selectedShop.id === shop.id ? 'selected' : ''}`}
                                            >
                                                {shop.type === 'yandex' && <img src={YandexIcon} alt="Yandex" className="icon" />}
                                                {shop.type === 'ozon' && <img src={OzonIcon} alt="Ozon" className="icon" />}
                                                {shop.type === 'wildberries' && <img src={wildberriesIcon} alt="wildberries" className="icon" />}
                                                {shop.name}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                {selectedShop ? (
                                    <ShopDetails shopData={shopData} setShopData={setShopData} />
                                ) : (
                                    <h2 className="select-shop-message">Выберите магазин в списке</h2>
                                )}
                            </>
                        )}

                        {currentView === 'catalog' && catalog.length !== 0 && (
                            <>
                                {isLoading && (
                                    <div className="loading-overlay">
                                        <div className="loading-spinner"></div>
                                    </div>
                                )}
                                <CatalogTable data={filteredCatalog} setCatalog={setCatalog} editedRowsCancel={editedRows} editedRows1={setEditedRows1} />
                            </>
                        )}

                        {currentView === 'stocks' && stocks.length !== 0 && (
                            <>
                                {isLoading && (
                                    <div className="loading-overlay">
                                        <div className="loading-spinner"></div>
                                    </div>
                                )}
                                <StokcsTable data={filteredStocks} setStocks={setStocks} storagges={storages} shops={shops} editedRowsCancel={editedRows} editedRows1={setEditedRows1} setEditedStorages={setEditedStorages} />
                            </>
                        )}
                    </div>
                </div>
            </div>

            <BottomPanel lastUpdated={lastUpdated} isSidebarOpen={isSidebarOpen} onCancel={handleCancel} onSave={handleSave} />
        </div>
    );
};

export default Dashboard;
