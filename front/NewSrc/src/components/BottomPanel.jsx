import React from 'react';

const BottomPanel = ({ lastUpdated, isSidebarOpen, onCancel, onSave }) => {
    const formattedDate = new Date(lastUpdated).toLocaleString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    });

    return (
        <div style={{
            ...styles.panel,
            left: isSidebarOpen ? '250px' : '70px'
        }}>
            <span style={styles.updateText}>Последнее обновление: {formattedDate}</span>
            <div style={styles.rightSection}>
                <button style={styles.button} onClick={onCancel}>Отмена</button>
                <button style={styles.button} onClick={onSave}>Сохранить</button>
            </div>
        </div>
    );
};

const styles = {
    panel: {
        position: 'fixed',
        bottom: 0,
        left: '70px',
        right: 0,
        height: '80px',
        backgroundColor: '#34495E',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 20px',
        boxSizing: 'border-box',
        zIndex: 1000,
        transition: 'left 0.3s ease',
    },
    rightSection: {
        display: 'flex',
        alignItems: 'center',
        marginRight: '50px',
    },
    button: {
        background: 'none',
        border: '1px solid white',
        color: 'white',
        padding: '10px 20px', 
        cursor: 'pointer',
        marginLeft: '20px',
        fontSize: '16px', 
        borderRadius: '8px', 
        transition: 'background-color 0.3s ease', 
    },
    buttonHover: {
        backgroundColor: '#2C3E50', 
    },
    updateText: {
        fontSize: '14px',
    },
};

export default BottomPanel;
