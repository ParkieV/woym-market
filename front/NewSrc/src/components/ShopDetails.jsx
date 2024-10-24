import React, { useEffect, useState } from 'react';

const ShopDetails = ({ shopData, setShopData }) => {

    const [localData, setLocalData] = useState(shopData);

    useEffect(() => {
        setLocalData(shopData);
    }, [shopData]);

    const handleChange = (e, field) => {
        const { type, checked, value } = e.target;
        const newValue = type === 'checkbox' ? checked : value
        setShopData((prevData) => ({
            ...prevData,
            [field]: newValue,
        }));
    };

    return (
        <>
            <div style={styles.gridContainer}>
                <div style={styles.container}>
                    <h2 style={styles.heading}>Основное</h2>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Курс (долларов за рубль):</label>
                        <input
                            type="number"
                            value={localData.rate || ''}
                            onChange={(e) => handleChange(e, 'rate')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Налог (%):</label>
                        <input
                            type="number"
                            value={localData.tax || ''}
                            onChange={(e) => handleChange(e, 'tax')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Комиссия за продажу в FBO (%):</label>
                        <input
                            type="number"
                            value={localData.fbo_sales_commission || ''}
                            onChange={(e) => handleChange(e, 'fbo_sales_commission')}
                            style={styles.input}
                        />
                    </div>
                </div>
                <div style={styles.container}>
                    <h2 style={styles.heading}>Логистика</h2>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Цена длительного хранения (₽ / литр):</label>
                        <input
                            type="number"
                            value={localData.long_term_storage_cost || ''}
                            onChange={(e) => handleChange(e, 'long_term_storage_cost')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Порог для доп. логистики за 1 литр (л):</label>
                        <input
                            type="number"
                            value={localData.volume_threshold_for_additional_logistics || ''}
                            onChange={(e) => handleChange(e, 'volume_threshold_for_additional_logistics')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Цена доп. логистики за 1 литр (₽):</label>
                        <input
                            type="number"
                            value={localData.cost_of_additional_logistics_per_liter || ''}
                            onChange={(e) => handleChange(e, 'cost_of_additional_logistics_per_liter')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>
                            Учитывать в целевой цене товара стоимость дополнительной логистики
                            <input
                                type="checkbox"
                                checked={localData.consider_logistic_cost || false}
                                onChange={(e) => handleChange(e, 'consider_logistic_cost')}
                                style={{ marginLeft: '30px' }}
                            />
                        </label>
                    </div>
                </div>
                <div style={styles.container}>
                    <h2 style={styles.heading}>Рекомендованная розничная цена (РРЦ)</h2>
                    <h3 style={styles.subHeading}>X (₽) + «ОПТ» (₽) + «ОПТ» (₽) * Y%</h3>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>X (₽):</label>
                        <input
                            type="number"
                            value={localData.first_variable_for_recommended_retail_price || ''}
                            onChange={(e) => handleChange(e, 'first_variable_for_recommended_retail_price')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Y (%):</label>
                        <input
                            type="number"
                            value={localData.second_variable_for_recommended_retail_price || ''}
                            onChange={(e) => handleChange(e, 'second_variable_for_recommended_retail_price')}
                            style={styles.input}
                        />
                    </div>
                </div>
                <div style={styles.container}>
                    <h2 style={styles.heading}>Стоп-цена</h2>
                    <h3 style={styles.subHeading}>X (₽) + «ОПТ» (₽) + «ОПТ» (₽) * Y%</h3>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>X (₽):</label>
                        <input
                            type="number"
                            value={localData.first_variable_for_stop_price || ''}
                            onChange={(e) => handleChange(e, 'first_variable_for_stop_price')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Y (%):</label>
                        <input
                            type="number"
                            value={localData.second_variable_for_stop_price || ''}
                            onChange={(e) => handleChange(e, 'second_variable_for_stop_price')}
                            style={styles.input}
                        />
                    </div>
                </div>
                <div style={styles.container}>
                    <h2 style={styles.heading}>Акции</h2>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Скидка на товары (%):</label>
                        <input
                            type="number"
                            value={localData.discount_purchase || ''}
                            onChange={(e) => handleChange(e, 'discount_purchase')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Цена до скидки (%):</label>
                        <input
                            type="number"
                            value={localData.price_before_discount || ''}
                            onChange={(e) => handleChange(e, 'price_before_discount')}
                            style={styles.input}
                        />
                    </div>
                    {localData.name === "CALMAR.SHOP" && localData.type === "yandex" ? (
                        <h2 style={styles.subHeading}>Ограничение на разницу между "целевая цена" и "цена до скидки": 5% &lt;= Разница &gt;= 99%</h2>
                    ) : (
                        ''
                    )}
                    {(localData.name === "CALMARSHOP" && localData.type === "ozon") ||
                        (localData.name === "SkrabPlus" && localData.type === "ozon") ? (
                        <>
                            <h2 style={{ ...styles.subHeading, textAlign: 'left' }}>
                                Ограничение на разницу между "целевая цена" и "цена до скидки":
                            </h2>
                            <ul style={{ listStyleType: 'none', paddingLeft: '0', textAlign: 'left', color: 'black' }}>
                                <li>- Если цена &lt;= 400 рублей, то разница &gt;= 20 рублей</li>
                                <li>- Если цена от 400 до 10000 рублей, то разница &gt;= 5%</li>
                                <li>- Если цена &gt; 10000 рублей, то разница &gt;= 500</li>
                            </ul>
                        </>
                    ) : (
                        ''
                    )}

                </div>
                <div style={styles.container}>
                    <h2 style={styles.heading}>Умная поставка</h2>
                    <h3 style={styles.subHeading}>«заказы за 7 дней» * A + «заказы за 14 дней» * B + «заказы за 28 дней» * C + «заказы за 60 дней» * D + «заказы за 120 дней» * E</h3>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>A (Заказы за 7 дней):</label>
                        <input
                            type="number"
                            value={localData.a_variable_for_smart_delivery || ''}
                            onChange={(e) => handleChange(e, 'a_variable_for_smart_delivery')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>B (Заказы за 14 дней):</label>
                        <input
                            type="number"
                            value={localData.b_variable_for_smart_delivery || ''}
                            onChange={(e) => handleChange(e, 'b_variable_for_smart_delivery')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>C (Заказы за 28 дней):</label>
                        <input
                            type="number"
                            value={localData.c_variable_for_smart_delivery || ''}
                            onChange={(e) => handleChange(e, 'c_variable_for_smart_delivery')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>D (Заказы за 60 дней):</label>
                        <input
                            type="number"
                            value={localData.d_variable_for_smart_delivery || ''}
                            onChange={(e) => handleChange(e, 'd_variable_for_smart_delivery')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>E (Заказы за 120 дней):</label>
                        <input
                            type="number"
                            value={localData.e_variable_for_smart_delivery || ''}
                            onChange={(e) => handleChange(e, 'e_variable_for_smart_delivery')}
                            style={styles.input}
                        />
                    </div>
                </div>
                <div style={styles.container}>
                    <h2 style={styles.heading}>Значения по умолчанию</h2>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Схема ценообразования:</label>
                        <select
                            value={localData.default_pricing_scheme || ''}
                            onChange={(e) => handleChange(e, 'default_pricing_scheme')}
                            style={styles.input}
                        >
                            <option></option>
                            <option value="O0">O0</option>
                            <option value="W0">W0</option>
                            <option value="Y0">Y0</option>
                            <option value="Y1">Y1</option>
                        </select>
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Авто мин цена %:</label>
                        <input
                            type="number"
                            value={localData.default_auto_min_price || ''}
                            onChange={(e) => handleChange(e, 'default_auto_min_price')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>
                            Авто контроль цен
                            <input
                                type="checkbox"
                                checked={localData.default_auto_price_control || false}
                                onChange={(e) => handleChange(e, 'default_auto_price_control')}
                                style={{ marginLeft: '30px' }}
                            />
                        </label>
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Коэффициент расчётной цены:</label>
                        <input
                            type="number"
                            value={localData.default_total_price_coeff || ''}
                            onChange={(e) => handleChange(e, 'default_total_price_coeff')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>Минимальная наценка расчётной цены:</label>
                        <input
                            type="number"
                            value={localData.default_total_price_min_additional || ''}
                            onChange={(e) => handleChange(e, 'default_total_price_min_additional')}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.fieldGroup}>
                        <label style={styles.label}>
                            Автоучастие в акциях
                            <input
                                type="checkbox"
                                checked={localData.default_auto_participation_in_promotions || false}
                                onChange={(e) => handleChange(e, 'default_auto_participation_in_promotions')}
                                style={{ marginLeft: '30px' }}
                            />
                        </label>
                    </div>
                </div>
            </div>
        </>
    );
};

const styles = {
    gridContainer: {
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '50px',
        padding: '20px',
        maxWidth: '1500px',
        margin: '50px auto 100px auto',
        width: '100%',
    },
    container: {
        display: 'flex',
        flexDirection: 'column',
        padding: '20px',
        backgroundColor: '#f7f7f7',
        borderRadius: '10px',
        width: '700px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    },
    fieldGroup: {
        marginBottom: '15px',
        display: 'flex',
        flexDirection: 'column',
    },
    label: {
        marginBottom: '5px',
        fontWeight: 'bold',
        fontSize: '14px',
        color: '#333',
    },
    input: {
        padding: '10px',
        fontSize: '14px',
        borderRadius: '5px',
        width: '100%',
        boxSizing: 'border-box',
        border: '1px solid #ccc',
    },
    heading: {
        textAlign: 'center',
        color: '#000',
        marginBottom: '20px',
    },
    subHeading: {
        color: '#333',
        fontSize: '16px',
        textAlign: 'center',
        fontWeight: 'normal',
        marginTop: '5px'
    },
};

export default ShopDetails;
