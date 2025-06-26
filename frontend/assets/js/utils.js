// Utility functions
const utils = {
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    },
    
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('de-DE');
    }
};