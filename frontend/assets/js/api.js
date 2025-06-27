/**
 * DataFair API Client
 * JavaScript SDK für die Kommunikation mit dem DataFair Backend
 * ERWEITERT MIT DASHBOARD FUNKTIONEN
 */

class DataFairAPI {
    constructor() {
        this.baseURL = window.location.origin; // Verwendet die aktuelle Domain
        this.headers = {
            'Content-Type': 'application/json',
        };
    }
    
    /**
     * Generische API-Anfrage Methode
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: this.headers,
            credentials: 'include', // Wichtig für Session-Cookies
            ...options
        };
        
        try {
            console.log(`🔄 API Request: ${config.method || 'GET'} ${endpoint}`);
            
            const response = await fetch(url, config);
            
            console.log(`📡 API Response: ${response.status} ${response.statusText}`);
            
            // Handle different response types
            const contentType = response.headers.get('content-type');
            let data;
            
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }
            
            if (!response.ok) {
                // Handle different error types
                let errorMessage = 'API request failed';
                
                if (response.status === 401) {
                    errorMessage = 'Unauthorized - please login';
                    // Optional: redirect to login
                    // window.location.href = '/login.html';
                } else if (response.status === 403) {
                    errorMessage = 'Forbidden - insufficient permissions';
                } else if (response.status === 404) {
                    errorMessage = 'Not found';
                } else if (response.status === 500) {
                    errorMessage = 'Server error';
                } else if (data && typeof data === 'object' && data.error) {
                    errorMessage = data.error;
                } else if (data && typeof data === 'string') {
                    errorMessage = data;
                }
                
                throw new Error(errorMessage);
            }
            
            return data;
        } catch (error) {
            console.error('❌ API Error:', error);
            throw error;
        }
    }
    
    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
    
    // ===== AUTHENTICATION METHODS =====
    
    /**
     * User Login
     */
    async login(email, password) {
        const data = await this.post('/auth/login', { email, password });
        console.log('✅ Login successful:', data);
        return data;
    }
    
    /**
     * User Logout
     */
    async logout() {
        const data = await this.post('/auth/logout', {});
        console.log('✅ Logout successful');
        return data;
    }
    
    /**
     * User Registration
     */
    async register(userData) {
        const data = await this.post('/auth/register', userData);
        console.log('✅ Registration successful:', data);
        return data;
    }
    
    /**
     * Check Authentication Status
     */
    async checkAuth() {
        try {
            const data = await this.get('/auth/check');
            return data;
        } catch (error) {
            console.log('ℹ️ Not authenticated');
            return { authenticated: false };
        }
    }
    
    // ===== USER PROFILE METHODS =====
    
    /**
     * Get User Profile
     */
    async getProfile() {
        const data = await this.get('/auth/profile');
        return data.user || data;
    }
    
    /**
     * Update User Profile
     */
    async updateProfile(profileData) {
        const data = await this.put('/auth/profile', profileData);
        return data;
    }
    
    // ===== DASHBOARD METHODS (NEU!) =====
    
    /**
     * Get complete dashboard overview in one call
     * @returns {Promise<Object>} Complete dashboard data
     */
    async getDashboardOverview() {
        const response = await this.get('/api/dashboard/overview');
        return response.dashboard;
    }
    
    /**
     * Handle quick actions from dashboard
     * @param {string} action - Action type
     * @param {Object} data - Action data
     * @returns {Promise<Object>} Action result
     */
    async handleQuickAction(action, data = {}) {
        return await this.post('/api/dashboard/quick-actions', {
            action: action,
            ...data
        });
    }
    
    /**
     * Generate test earnings for demo
     * @returns {Promise<Object>} Generated earnings info
     */
    async generateTestEarnings() {
        return await this.handleQuickAction('generate_test_earnings');
    }
    
    /**
     * Quick toggle data type permission
     * @param {number} dataTypeId - Data type ID
     * @param {boolean} enabled - Enable/disable
     * @returns {Promise<Object>} Update result
     */
    async quickToggleDataType(dataTypeId, enabled) {
        return await this.handleQuickAction('toggle_data_type', {
            dataTypeId: dataTypeId,
            enabled: enabled
        });
    }
    
    /**
     * Quick payout request
     * @param {number} amount - Payout amount
     * @param {string} method - Payout method
     * @returns {Promise<Object>} Payout result
     */
    async quickPayoutRequest(amount, method = 'paypal') {
        return await this.handleQuickAction('request_payout', {
            amount: amount,
            method: method
        });
    }
    
    // ===== DATA METHODS =====
    
    /**
     * Get Available Data Types
     */
    async getDataTypes() {
        const data = await this.get('/api/data-types');
        return data.data_types || [];
    }
    
    /**
     * Update Data Permission
     */
    async updateDataPermission(dataTypeId, enabled) {
        const permissions = await this.get('/api/data-permissions');
        
        // Update the specific permission
        const updatedPermissions = permissions.permissions.map(p => 
            p.data_type === dataTypeId ? { ...p, enabled } : p
        );
        
        const data = await this.post('/api/data-permissions', {
            permissions: updatedPermissions
        });
        return data;
    }
    
    // ===== EARNINGS METHODS =====
    
    /**
     * Get User Earnings
     */
    async getEarnings() {
        const data = await this.get('/api/earnings');
        return data;
    }
    
    /**
     * Request Payout
     */
    async requestPayout(amount, method) {
        const data = await this.post('/api/payout', { amount, method });
        return data;
    }
    
    /**
     * Get Payout History
     */
    async getPayouts() {
        const data = await this.get('/api/payouts');
        return data.payouts || [];
    }
    
    // ===== SURVEY METHODS =====
    
    /**
     * Get Available Surveys
     */
    async getSurveys() {
        const data = await this.get('/api/surveys/available');
        return data;
    }
    
    /**
     * Get Survey Details
     */
    async getSurveyDetails(surveyId) {
        const data = await this.get(`/api/surveys/${surveyId}`);
        return data;
    }
    
    /**
     * Start Survey
     */
    async startSurvey(surveyId) {
        const data = await this.post(`/api/surveys/${surveyId}/start`, {});
        return data;
    }
    
    /**
     * Submit Survey
     */
    async submitSurvey(surveyId, responses) {
        const data = await this.post(`/api/surveys/${surveyId}/submit`, { responses });
        return data;
    }
    
    /**
     * Get My Survey Responses
     */
    async getMySurveyResponses() {
        const data = await this.get('/api/surveys/my-responses');
        return data.responses || [];
    }
    
    // ===== DEVELOPMENT / TEST METHODS =====
    
    /**
     * Generate Test Monthly Earnings (for development)
     */
    async generateMonthlyEarnings() {
        // This would be a custom endpoint for generating test data
        const data = await this.post('/api/test/generate-earnings', {});
        return data;
    }
    
    /**
     * Get Activities
     */
    async getActivities() {
        // Mock data for now - replace with real endpoint later
        return [
            {
                id: 1,
                type: 'data_usage',
                title: 'Daten wurden abgerufen',
                description: 'Shopping-Verhalten wurde für Marktforschung verwendet',
                timestamp: '2025-06-27T10:30:00Z',
                earning: 2.50
            },
            {
                id: 2,
                type: 'survey_completed',
                title: 'Umfrage abgeschlossen',
                description: 'Technologie-Nutzung im Alltag',
                timestamp: '2025-06-26T15:45:00Z',
                earning: 12.00
            }
        ];
    }
}

// ===== UTILITY FUNCTIONS =====

/**
 * Check if user is authenticated and redirect if not
 */
async function requireAuthentication() {
    try {
        const authStatus = await window.DataFairAPI.checkAuth();
        if (!authStatus.authenticated) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/login.html';
        return false;
    }
}

/**
 * Redirect to dashboard if already authenticated
 */
async function redirectIfAuthenticated() {
    try {
        const authStatus = await window.DataFairAPI.checkAuth();
        if (authStatus.authenticated) {
            window.location.href = '/dashboard.html';
        }
    } catch (error) {
        // User is not authenticated, continue normally
        console.log('User not authenticated, staying on current page');
    }
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'EUR') {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format relative time
 */
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffMinutes < 1) return 'Gerade eben';
    if (diffMinutes < 60) return `vor ${diffMinutes} Minuten`;
    if (diffHours < 24) return `vor ${diffHours} Stunden`;
    if (diffDays < 7) return `vor ${diffDays} Tagen`;
    return formatDate(dateString);
}

/**
 * Show notification (simple version)
 */
function showNotification(message, type = 'info', duration = 3000) {
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 z-50 p-4 rounded-lg text-white max-w-sm ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 
        type === 'warning' ? 'bg-yellow-500' :
        'bg-blue-500'
    }`;
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white opacity-70 hover:opacity-100">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

// ===== GLOBAL INITIALIZATION =====

// Create global API instance
window.DataFairAPI = new DataFairAPI();

// Export for modules (if using ES6 modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DataFairAPI, requireAuthentication, redirectIfAuthenticated };
}

console.log('✅ DataFair API Client loaded successfully (with Dashboard support)');