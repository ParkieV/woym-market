import React, { useState, useMemo, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import '../css/CatalogTable.css';
import ModalEditor from '../components/ModalEditor';


const CatalogTable = ({ data, setCatalog, editedRowsCancel, editedRows1 }) => {
    const [editedRows, setEditedRows] = useState(new Set());
    const [rowData, setRowData] = useState(data);
    const [isModalOpen, setModalOpen] = useState(false);
    const [scrollToRowIndex, setScrollToRowIndex] = useState(null);
    const gridRef = useRef(null);
    const [gridApi, setGridApi] = useState(null);
    const [currentEditValue, setCurrentEditValue] = useState('');
    const [currentField, setCurrentField] = useState('');
    const [currentRowIndex, setCurrentRowIndex] = useState(null);
    const [inputType, setInputType] = useState('text');


    useEffect(() => {
        setRowData(data);
    }, [data]);

    useEffect(() => {
        setEditedRows(editedRowsCancel); 
    }, [editedRowsCancel]); 

    useEffect(() => {
        editedRows1(new Set(editedRows));
    }, [editedRows]); 


    const handleChange = (e, field, rowIndex) => {
        const { type, checked, value } = e.target;
        const newValue = type === 'checkbox' ? checked : value;
       
        setEditedRows((prev) => new Set(prev).add(rowIndex));
        setCatalog((prevData) => {
            const updatedCatalog = [...prevData];
            updatedCatalog[rowIndex] = {
                ...updatedCatalog[rowIndex],
                [field]: newValue,
            };
            return updatedCatalog;
        });

    }

    const handleCheckboxChange = (rowIndex, market, shopName) => {


        const updatedData = [...rowData];
        console.log(rowIndex);

        if (!updatedData[rowIndex] || !updatedData[rowIndex].synchronization) {
            console.error('synchronization field is undefined for this row.');
            return;
        }

        const shop = updatedData[rowIndex].synchronization.find(shop =>
            shop.market === market && shop.name_of_shop === shopName
        );


        if (shop) {
            const newValue = !shop.synchronization;
            shop.synchronization = newValue;
            const updatedSynchronization = [...updatedData[rowIndex].synchronization];
            const shopIndex = updatedSynchronization.findIndex(s => s.market === market && s.name_of_shop === shopName);
            if (shopIndex !== -1) {
                updatedSynchronization[shopIndex].synchronization = newValue;  
            }
            handleChange(
                { target: { value: updatedSynchronization } }, 
                'synchronization',  
                rowIndex   
            );
        } else {
            console.error(`Shop not found for market: ${market}, shop name: ${shopName}`);
            return;
        }
        setRowData(updatedData);
    };

    const handleSelectChange = (event, rowIndex, rowData, setRowData, setEditedRows) => {
        const updatedValue = event.target.value === "null" ? null : parseInt(event.target.value, 10);
        const updatedData = [...rowData];
        if (!updatedData[rowIndex] || !updatedData[rowIndex].synchronization) {
            console.error('synchronization field is undefined for this row.');
            return;
        }

        updatedData[rowIndex].reverse_sync_offer_id = updatedValue;
        handleChange(
            { target: { value: updatedValue } }, 
            'reverse_sync_offer_id',  
            rowIndex   
        );

        setRowData(updatedData);

    };




    const columns = useMemo(() => [
        {
            headerName: 'SKU',
            field: 'sku',
            editable: false,
            cellStyle: (params) => {
                if (editedRows.has(params.rowIndex)) {
                    return { backgroundColor: '#ffeb3b' };
                } else {
                    return { backgroundColor: 'white' };
                }
            },
            pinned: 'left',
            width: 200,
        },
        {
            headerName: 'Информация',
            children: [
                {
                    headerName: 'Фото',
                    field: 'photo',
                    cellRenderer: (params) => (
                        <img src={params.value} alt="Фото" className="table-img" />
                    ),
                    width: 150,
                },
                {
                    headerName: 'Название',
                    field: 'name',
                    editable: true,
                    cellEditor: 'agLargeTextCellEditor',
                    cellEditorParams: {
                        maxLength: 60,
                    },
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'name', params.node.rowIndex);
                    },
                    cellStyle: (params) => {
                        if (params.value.length > 60) {
                            return { backgroundColor: '#f8d7da' };
                        } else {
                            return { backgroundColor: '#d4edda' };
                        }
                    },
                    width: 300,
                },
                {
                    headerName: 'Штрихкоды',
                    field: 'barcodes',
                    editable: true,
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'barcodes', params.node.rowIndex);
                    },
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 200,
                },
                {
                    headerName: 'Аннотация',
                    field: 'description',
                    editable: true,
                    cellEditor: 'agLargeTextCellEditor',
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'description', params.node.rowIndex);
                    },
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 300,
                },
                {
                    headerName: 'Примечание',
                    field: 'catalog_note',
                    editable: true,
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'catalog_note', params.node.rowIndex);
                    },
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 200,
                },
                {
                    headerName: 'Поисковые слова',
                    field: 'search_words',
                    editable: true,
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'search_words', params.node.rowIndex);
                    },
                    cellEditor: 'agLargeTextCellEditor',
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 300,
                },
            ],
        },
        {
            headerName: 'Габариты',
            children: [
                {
                    headerName: 'Вес, кг',
                    field: 'self_weight',
                    editable: true,
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 150,
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'self_weight', params.node.rowIndex);
                    },
                    valueFormatter: (params) => {
                        const value = params.value;
                        if (value === null || value === undefined) return 'N/A';
                        return parseFloat(value).toFixed(2);
                    },
                },
                {
                    headerName: 'Длина, см',
                    field: 'self_length',
                    editable: true,
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 150,
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'self_length', params.node.rowIndex);
                    },
                    valueFormatter: (params) => {
                        return params.value === null || params.value === undefined ? 'N/A' : params.value;
                    },
                },
                {
                    headerName: 'Ширина, см',
                    field: 'self_width',
                    editable: true,
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 150,
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'self_width', params.node.rowIndex);
                    },
                    valueFormatter: (params) => {
                        return params.value === null || params.value === undefined ? 'N/A' : params.value;
                    },
                },
                {
                    headerName: 'Высота, см',
                    field: 'self_height',
                    editable: true,
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'self_height', params.node.rowIndex);
                    },
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 150,
                    valueFormatter: (params) => {
                        return params.value === null || params.value === undefined ? 'N/A' : params.value;
                    },
                },
                {
                    headerName: 'Объем, л',
                    valueGetter: (params) => {
                        const { self_length, self_width, self_height } = params.data;
                        if (self_length && self_width && self_height) {
                            return (self_length * self_width * self_height) / 1000;
                        }
                        return 'N/A';
                    },
                    editable: false,
                },
            ],
        },
        {
            headerName: 'Ценообразование',
            children: [
                {
                    headerName: 'Дата обновления ОПТ (у.е.)',
                    field: 'dollar_cost_price_updated_at',
                    editable: false,
                    valueFormatter: (params) => {
                        return params.value === null || params.value === undefined ? 'N/A' : params.value;
                    },
                },
                {
                    headerName: 'Акция',
                    field: 'use_promotion_price',
                    cellEditor: 'agCheckboxCellEditor',
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'use_promotion_price', params.node.rowIndex);
                    },
                    editable: true,
                    cellStyle: { backgroundColor: '#d4edda' },
                },
                {
                    headerName: 'ОПТ у.е.',
                    field: 'wholesale_dollar_cost_price',
                    editable: true,
                    cellStyle: { backgroundColor: '#d4edda' },
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'wholesale_dollar_cost_price', params.node.rowIndex);
                    },
                    valueFormatter: (params) => {
                        const value = params.value;
                        if (value === null || value === undefined) return 'N/A';
                        return value !== null ? `${parseFloat(value).toFixed(2)} $` : '';
                    },
                },
                {
                    headerName: 'Наличие у поставщика',
                    field: 'supplier_available',
                    cellEditor: 'agCheckboxCellEditor',
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'supplier_available', params.node.rowIndex);
                    },
                    editable: true,
                    cellStyle: { backgroundColor: '#d4edda' },
                },
            ],
        },
        {
            headerName: 'Синхронизация',
            children: [
                {
                    headerName: 'SkrabPlus(ozon)',
                    field: 'synchronization',
                    editable: false,
                    cellRenderer: (params) => {
                        const shopList = params.data.synchronization || [];
                        const shop = shopList.find(shop =>
                            shop.market === 'ozon' && shop.name_of_shop === 'SkrabPlus'
                        );
                        const checkboxId = `checkbox-${params.node.rowIndex}-${shop ? shop.market : 'unknown'}-${shop ? shop.name_of_shop : 'unknown'}`;
                        return (
                            <div className="synchronization-row">
                                <input
                                    type="checkbox"
                                    id={checkboxId}
                                    checked={shop ? shop.synchronization : false}
                                    disabled={!shop}
                                    onChange={() => handleCheckboxChange(params.node.rowIndex, 'ozon', 'SkrabPlus')}
                                    className="custom-checkbox"
                                />
                                <label htmlFor={checkboxId} className="checkbox-label">
                                    <span className="custom-checkbox-indicator"></span>
                                </label>
                            </div>
                        );
                    },
                    cellStyle: (params) => {
                        const shopList = params.data.synchronization || [];
                        const shop = shopList.find(shop =>
                            shop.market === 'ozon' && shop.name_of_shop === 'SkrabPlus'
                        );
                        const isChecked = shop && shop.synchronization;
                        const isEnabled = !!shop;
                        return {
                            backgroundColor: isChecked || isEnabled ? '#d4edda' : 'transparent',
                        };
                    },
                },
                {
                    headerName: 'SkrabPlus(wildberries)',
                    field: 'synchronization',
                    editable: false,
                    cellRenderer: (params) => {
                        const shop = params.data.synchronization.find(shop =>
                            shop.market === 'wildberries' && shop.name_of_shop === 'SkrabPlus'
                        );
                        const checkboxId = `checkbox-${params.node.rowIndex}-${shop ? shop.market : 'unknown'}-${shop ? shop.name_of_shop : 'unknown'}`;
                        return (
                            <div className="synchronization-row">
                                <input
                                    type="checkbox"
                                    id={checkboxId}
                                    checked={shop ? shop.synchronization : false}
                                    disabled={!shop}
                                    onChange={() => handleCheckboxChange(params.node.rowIndex, 'wildberries', 'SkrabPlus')}
                                    className="custom-checkbox"
                                />
                                <label htmlFor={checkboxId} className="checkbox-label">
                                    <span className="custom-checkbox-indicator"></span>
                                </label>
                            </div>
                        );
                    },
                    cellStyle: (params) => {
                        const shop = params.data.synchronization.find(shop =>
                            shop.market === 'wildberries' && shop.name_of_shop === 'SkrabPlus'
                        );
                        const isChecked = shop && shop.synchronization;
                        const isEnabled = !!shop;
                        return {
                            backgroundColor: isChecked || isEnabled ? '#d4edda' : 'transparent'
                        };
                    },
                },
                {
                    headerName: 'CALMARSHOP(ozon)',
                    field: 'synchronization',
                    editable: false,
                    cellRenderer: (params) => {
                        const shop = params.data.synchronization.find(shop =>
                            shop.market === 'ozon' && shop.name_of_shop === 'CALMARSHOP'
                        );
                        const checkboxId = `checkbox-${params.node.rowIndex}-${shop ? shop.market : 'unknown'}-${shop ? shop.name_of_shop : 'unknown'}`;
                        return (
                            <div className="synchronization-row">
                                <input
                                    type="checkbox"
                                    id={checkboxId}
                                    checked={shop ? shop.synchronization : false}
                                    disabled={!shop}
                                    onChange={() => handleCheckboxChange(params.node.rowIndex, 'ozon', 'CALMARSHOP')}
                                    className="custom-checkbox"
                                />
                                <label htmlFor={checkboxId} className="checkbox-label">
                                    <span className="custom-checkbox-indicator"></span>
                                </label>
                            </div>
                        );
                    },
                    cellStyle: (params) => {
                        const shop = params.data.synchronization.find(shop =>
                            shop.market === 'ozon' && shop.name_of_shop === 'CALMARSHOP'
                        );
                        const isChecked = shop && shop.synchronization;
                        const isEnabled = !!shop;
                        return {
                            backgroundColor: isChecked || isEnabled ? '#d4edda' : 'transparent'
                        };
                    },
                },
                {
                    headerName: 'CALMAR.SHOP(yandex)',
                    field: 'synchronization',
                    editable: false,
                    cellRenderer: (params) => {
                        const shop = params.data.synchronization.find(shop =>
                            shop.market === 'yandex' && shop.name_of_shop === 'CALMAR.SHOP'
                        );
                        const checkboxId = `checkbox-${params.node.rowIndex}-${shop ? shop.market : 'unknown'}-${shop ? shop.name_of_shop : 'unknown'}`;
                        return (
                            <div className="synchronization-row">
                                <input
                                    type="checkbox"
                                    id={checkboxId}
                                    checked={shop ? shop.synchronization : false}
                                    disabled={!shop}
                                    onChange={() => handleCheckboxChange(params.node.rowIndex, 'yandex', 'CALMAR.SHOP')}
                                    className="custom-checkbox"
                                />
                                <label htmlFor={checkboxId} className="checkbox-label">
                                    <span className="custom-checkbox-indicator"></span>
                                </label>
                            </div>
                        );
                    },
                    cellStyle: (params) => {
                        const shop = params.data.synchronization.find(shop =>
                            shop.market === 'yandex' && shop.name_of_shop === 'CALMAR.SHOP'
                        );
                        const isChecked = shop && shop.synchronization;
                        const isEnabled = !!shop;
                        return {
                            backgroundColor: isChecked || isEnabled ? '#d4edda' : 'transparent'
                        };
                    },
                },
                {
                    headerName: 'Обратная синхронизация',
                    field: 'reverse_sync_offer_id',
                    editable: false,
                    cellRenderer: (params) => {
                        const availableShops = params.data.synchronization.filter(shop => shop.sku === params.data.sku);

                        const currentShop = availableShops.find(shop => shop.id === params.value);
                        const currentShopLabel = currentShop ? `${currentShop.name_of_shop} (${currentShop.market})` : 'N/A';

                        const shopOptions = [
                            { value: currentShop ? currentShop.id : '', label: currentShopLabel },
                            ...availableShops
                                .filter(shop => shop.id !== params.value)
                                .map(shop => ({
                                    value: shop.id,
                                    label: `${shop.name_of_shop} (${shop.market})`,
                                })),

                        ];
                        if (!shopOptions.some(option => option.label === 'N/A')) {
                            shopOptions.push({ value: null, label: 'N/A' });
                        }

                        return (
                            <select className="custom-select" value={params.data.reverse_sync_offer_id || ''} onChange={(event) => handleSelectChange(event, params.node.rowIndex, rowData, setRowData, setEditedRows)} >
                                {shopOptions.map(item => (
                                    <option key={item.value} value={item.value}>
                                        {item.label}
                                    </option>
                                ))}
                            </select>
                        );
                    },
                    cellStyle: { backgroundColor: '#d4edda' },
                }
            ],
        }
    ], [editedRows]);

    const onCellClicked = (params) => {

        const isCheckboxSync = params.colDef.field === 'synchronization';
        const isCheckboxPromo = params.colDef.field === 'use_promotion_price';
        const isCheckboxAvail = params.colDef.field === 'supplier_available';
        const isSelect = params.colDef.field === 'reverse_sync_offer_id';

        if (isCheckboxSync || isCheckboxPromo || isCheckboxAvail || isSelect) {
            return;
        }

        if (params.colDef.editable) {
            setCurrentRowIndex(params.rowIndex);
            setCurrentField(params.colDef.field);
            setCurrentEditValue(params.value);


            if (params.colDef.field === 'self_weight' || params.colDef.field === "wholesale_dollar_cost_price") {
                setInputType('number');
            } else if (
                params.colDef.field === 'self_length' ||
                params.colDef.field === 'self_width' ||
                params.colDef.field === 'self_height'
            ) {
                setInputType('integer');
            } else {
                setInputType('text');
            }
            setScrollToRowIndex(params.rowIndex);
            setModalOpen(true);
        }
    };

    const handleSave = (value) => {
        const updatedData = [...rowData];
        updatedData[currentRowIndex][currentField] = value;
        setRowData(updatedData);
        setEditedRows((prev) => new Set(prev).add(currentRowIndex));
        if (gridApi && scrollToRowIndex !== null) {
            gridApi.ensureIndexVisible(scrollToRowIndex, 'middle');
        } else {
            console.error("gridRef or API is not available");
        }

    };

    const onGridReady = (params) => {
        gridRef.current = params.api;
        setGridApi(params.api);
    }

    return (
        <>
            <div className="ag-theme-alpine" style={{ height: 'calc(100vh - 165px)', width: '100%' }}>
                <AgGridReact
                    ref={gridRef}
                    rowData={rowData}
                    columnDefs={columns}
                    onCellClicked={onCellClicked}
                    rowHeight={80}
                    onGridReady={onGridReady} 
                    defaultColDef={{
                        filter: true,
                        resizable: true,
                        editable: true,
                    }}
                />
            </div>
            <ModalEditor
                isOpen={isModalOpen}
                onClose={() => {
                    setModalOpen(false);
                    setInputType('');
                    if (gridRef.current && gridRef.current.api && scrollToRowIndex !== null) {
                        gridRef.current.api.ensureIndexVisible(scrollToRowIndex, 'middle');
                    } else {
                        console.error("gridRef or API is not available");
                    }
                }}
                value={currentEditValue}
                onSave={handleSave}
                inputType={inputType}
            />
        </>
    );
};

export default CatalogTable;
