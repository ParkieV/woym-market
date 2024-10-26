import React, { useEffect, useState, useRef } from 'react';
import '../css/ModalEditor.css';

const ModalEditor = ({ isOpen, onClose, value, onSave, inputType }) => {
    const [inputValue, setInputValue] = useState(value);
    const textareaRef = useRef(null);
    

    useEffect(() => {
        setInputValue(value);
    }, [value]);

    useEffect(() => {
        if (!isOpen) {
            setInputValue('');
        } else if (textareaRef.current) {
            textareaRef.current.focus();
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleSave = () => {
        let formattedValue;

        if (inputType === 'number') {
            formattedValue = parseFloat(inputValue).toFixed(2);
        } else if (inputType === 'integer') {
            formattedValue = parseInt(inputValue, 10);
        } else {
            formattedValue = inputValue;
        }

        onSave(formattedValue);
        onClose();
    }

    const handleChange = (e) => {
        const { value } = e.target;

        if (inputType === 'number') {
            const regex = /^\d*[,\.]?\d{0,2}$/;
            if (regex.test(value) || value === '') {
                setInputValue(value.replace(',', '.'));
            }
        } else if (inputType === 'integer') {
            const regex = /^\d*$/;
            if (regex.test(value) || value === '') {
                setInputValue(value);
            }
        } else {
            setInputValue(value);
        }
    }

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2 className="modal-title">Редактировать значение</h2>
                <textarea
                    ref={textareaRef}
                    className="modal-input"
                    value={inputValue}
                    onChange={handleChange}
                    rows={4}
                />
                <div className="modal-actions">
                    <button className="modal-button" onClick={handleSave}>Сохранить</button>
                    <button className="modal-button cancel-button" onClick={onClose}>Отмена</button>
                </div>
            </div>
        </div>
    );
};

export default ModalEditor;
