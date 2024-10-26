import React, { useState } from 'react';
import '../css/Sidebar.css';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { ReactComponent as UserIcon } from '../icons/user.svg';
import { ReactComponent as CardsIcon } from '../icons/cards.svg';
import { ReactComponent as CatalogIcon } from '../icons/catalog.svg';
import { ReactComponent as StockIcon } from '../icons/stock.svg';
import { ReactComponent as FboStockIcon } from '../icons/fbo.svg';
import { ReactComponent as PriceIcon } from '../icons/price.svg';
import { ReactComponent as ShopsIcon } from '../icons/shops.svg';
import { ReactComponent as LogoutIcon } from '../icons/logout.svg';
import { ReactComponent as ArrowIcon } from '../icons/arrow.svg';

const Sidebar = ({ username, isOpen, toggleSidebar, handleViewChange, fetchCatalog, fetchStock }) => {

    const navigate = useNavigate();

    const handleLogout = () => {
        Cookies.remove('token');
        navigate('/login');
    };

    return (
        <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>

            <div className="sidebar-header">
                {isOpen && <UserIcon className="icon" />}
                {isOpen && <span className="username">{username}</span>}
                <button className="toggle-btn" onClick={toggleSidebar}>
                    <ArrowIcon className="icon" style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }} />
                </button>
            </div>

            <ul className="menu-items">
                <li>
                    <CardsIcon className="icon" />
                    {isOpen && <span>Карточки</span>}
                </li>
                <li onClick={() => {
                    handleViewChange('catalog');
                    fetchCatalog();
                }}>
                    <CatalogIcon className="icon" />
                    {isOpen && <span>Каталог</span>}
                </li>
                <li onClick={() => {
                    handleViewChange('stocks');
                    fetchStock();
                }}>
                    <StockIcon className="icon" />
                    {isOpen && <span>Мои остатки</span>}
                </li>
                <li>
                    <FboStockIcon className="icon" />
                    {isOpen && <span>FBO остатки</span>}
                </li>
            </ul>

            <div style={{ flex: 1 }}></div>


            <ul className="bottom-items">
                <li>
                    <PriceIcon className="icon" />
                    {isOpen && <span>Шаблоны цен</span>}
                </li>
                <li onClick={() => handleViewChange('shops')}>
                    <ShopsIcon className="icon" />
                    {isOpen && <span>Магазины</span>}
                </li>
                <li onClick={handleLogout}>
                    <LogoutIcon className="icon" />
                    {isOpen && <span>Выход</span>}
                </li>
            </ul>
        </div>
    );
};

export default Sidebar;
