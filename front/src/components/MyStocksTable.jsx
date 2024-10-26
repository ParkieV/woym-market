import React, { useState, useMemo, useEffect, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import '../css/CatalogTable.css';
import ModalEditor from './ModalEditor';


const MyStocksTable = ({ data, setStocks, storagges, shops, editedRowsCancel, editedRows1, setEditedStorages }) => {

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
    const [selectedImage, setSelectedImage] = useState(null);


    useEffect(() => {
        setRowData(data);
    }, [data]);

    useEffect(() => {
        setEditedRows(editedRowsCancel);
    }, [editedRowsCancel]);

    useEffect(() => {
        editedRows1(new Set(editedRows));
    }, [editedRows]);


    const handleChange = (event, field, rowIndex) => {
        const { value } = event.target;
    
        setStocks((prevData) => {
            const updatedData = [...prevData];
            const row = updatedData[rowIndex];
    
            if (field.startsWith('storage_')) {
                const storageIndex = parseInt(field.split('_')[1], 10);
                const storage = row.storages.find(s => s.storage_place_id === storagges[storageIndex].id);
    
                if (storage) {
                    storage.value = parseInt(value, 10); 
                    const editedKey = `${row.offer.sku}_${storage.id}`; 
    
                    setEditedStorages((prevEdited) => {
                        const newEdited = new Map(prevEdited);
                        newEdited.set(editedKey, { id: storage.id, value: storage.value, storage_place_id: storage.storage_place_id });
                        return newEdited;
                    });
                } else {
                    console.error(`Storage with id ${storagges[storageIndex].id} not found`);
                }
            } else {
                updatedData[rowIndex][field] = value;
            }
    
            return updatedData;
        });
    
        setEditedRows(prev => new Set(prev).add(rowIndex));
    };


    const handleImageClick = (imgSrc) => {
        setSelectedImage(imgSrc);
    };


    const closeModal = () => {
        setSelectedImage(null);
    };

    const columns = useMemo(() => [
        {
            headerName: 'SKU',
            field: 'offer.sku',
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
                    field: 'offer.photo',
                    editable: false,
                    cellRenderer: (params) => (
                        <img src={params.value[0]} alt="Фото" className="table-img" onClick={() => handleImageClick(params.value[0])} />
                    ),
                    width: 300,
                },
                {
                    headerName: 'Название',
                    field: 'offer.name',
                    editable: false,
                    cellEditor: 'agLargeTextCellEditor',
                    width: 300,
                },
            ],
        },
        {
            headerName: 'Склады',
            children: [
                {
                    headerName: storagges[0].name,
                    field: 'storage_0',
                    editable: true,
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 150,
                    valueGetter: (params) => {
                        const storages = params.data.storages;
                        const storage = storages ? storages.find(s => s.storage_place_id === storagges[0].id) : null;
                        return storage ? storage.value : 'N/A'
                    },
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'storage_0', params.node.rowIndex);
                    },
                },
                {
                    headerName: storagges[1].name,
                    field: 'storage_1',
                    editable: true,
                    cellStyle: { backgroundColor: '#d4edda' },
                    width: 150,
                    valueGetter: (params) => {
                        const storages = params.data.storages;
                        const storage = storages ? storages.find(s => s.storage_place_id === storagges[1].id) : null;
                        return storage ? storage.value : 'N/A'
                    },
                    onCellValueChanged: (params) => {
                        handleChange({ target: { value: params.newValue } }, 'storage_1', params.node.rowIndex);
                    },
                },
            ],
        },
        {
            headerName: 'Магазины',
            children: shops.map(shop => ({
                headerName: `${shop.name} (${shop.type})`,
                editable: false,
                valueGetter: (params) => {
                    const stock = params.data.stocks.find(s => s.name_of_shop === shop.name && s.market === shop.type);
                    return stock ? stock.stock : 'N/A';
                },
                width: 150,
            })),
        },
    ], [editedRows]);

    const onCellClicked = (params) => {

        if (params.colDef.editable) {
            setCurrentRowIndex(params.rowIndex);
            setCurrentField(params.colDef.field);
            setCurrentEditValue(params.value);

            if (params.colDef.field === 'storages') {
                setInputType('number');
            }

            setScrollToRowIndex(params.rowIndex);
            setModalOpen(true);
        }
    };

    const handleSave = (value) => {
      
        setRowData((prevData) => {
            const updatedData = [...prevData];
            const row = updatedData[currentRowIndex];

            if (currentField.startsWith('storage_')) {

                const storageIndex = parseInt(currentField.split('_')[1], 10);

                const storage = row.storages.find(s => s.storage_place_id === storagges[storageIndex].id);

                if (storage) {
                    storage.value = parseInt(value, 10); 
                    const editedKey = `${row.offer.sku}_${storage.id}`; 
    
                    setEditedStorages((prevEdited) => {
                        const newEdited = new Map(prevEdited);
                        newEdited.set(editedKey, { id: storage.id, value: storage.value, storage_place_id: storage.storage_place_id });
                        return newEdited;
                    });
                } else {
                    console.error(`Storage with id ${storagges[storageIndex].id} not found`);
                }
            } else {
                updatedData[currentRowIndex][currentField] = value;
            }

            return updatedData;
        });

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
                    rowHeight={90}
                    onCellClicked={onCellClicked}
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
            {selectedImage && (
                <div className="modal show" onClick={closeModal}>
                    <img src={selectedImage} alt="Увеличенное фото" />
                </div>
            )}
        </>
    );
};

export default MyStocksTable;
