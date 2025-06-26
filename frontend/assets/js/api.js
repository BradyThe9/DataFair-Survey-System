// DataFair API Client
class DataFairAPI {
    static baseURL = 'http://localhost:5000/api';
    
    // Helper method for making requests
    static async request(url, options = {}) {
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Include cookies for session
            ...options
        };
        
        try {
            const response = await fetch(`${this.baseURL}${url}`, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }
    
    // Authentication APIs
    static async register(userData) {
        return await this.request('/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
    
    static async login(email, password) {
        return await this.request('/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }
    
    static async logout() {
        return await this.request('/logout', {
            method: 'POST'
        });
    }
    
    // ===== NEW: User Profile APIs =====
    
    /**
     * Get current user's profile
     * @returns {Promise<Object>} User profile data
     */
    static async getProfile() {
        const response = await this.request('/profile');
        return response.user;
    }
    
    /**
     * Update current user's profile
     * @param {Object} profileData - Profile data to update
     * @returns {Promise<Object>} Updated user profile
     */
    static async updateProfile(profileData) {
        const response = await this.request('/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
        return response.user;
    }
    
    /**
     * Change user's password
     * @param {string} currentPassword - Current password
     * @param {string} newPassword - New password
     * @returns {Promise<Object>} Success response
     */
    static async changePassword(currentPassword, newPassword) {
        return await this.request('/profile/password', {
            method: 'PUT',
            body: JSON.stringify({
                currentPassword,
                newPassword
            })
        });
    }
    
    /**
     * Delete user account
     * @param {string} password - Password for confirmation
     * @returns {Promise<Object>} Success response
     */
    static async deleteAccount(password) {
        return await this.request('/profile/delete', {
            method: 'DELETE',
            body: JSON.stringify({ password })
        });
    }
    
    // ===== PLACEHOLDER: Future APIs =====
    
    // ===== Data Management APIs =====
    
    /**
     * Get all data types with user's permission status
     * @returns {Promise<Array>} Array of data types with permission info
     */
    static async getDataTypes() {
        const response = await this.request('/data-types');
        return response.dataTypes;
    }
    
    /**
     * Get user's current data permissions
     * @returns {Promise<Array>} Array of user's permissions
     */
    static async getDataPermissions() {
        const response = await this.request('/data-permissions');
        return response.permissions;
    }
    
    /**
     * Update or create a data permission
     * @param {number} dataTypeId - ID of the data type
     * @param {boolean} enabled - Whether to enable or disable
     * @returns {Promise<Object>} Updated permission
     */
    static async updateDataPermission(dataTypeId, enabled) {
        const response = await this.request('/data-permissions', {
            method: 'POST',
            body: JSON.stringify({ 
                dataTypeId: dataTypeId, 
                enabled: enabled 
            })
        });
        return response.permission;
    }
    
    /**
     * Delete a data permission completely
     * @param {number} permissionId - ID of the permission to delete
     * @returns {Promise<Object>} Success response
     */
    static async deleteDataPermission(permissionId) {
        return await this.request(`/data-permissions/${permissionId}`, {
            method: 'DELETE'
        });
    }
    
    /**
     * Get data usage statistics
     * @returns {Promise<Object>} Usage statistics
     */
    static async getDataUsage() {
        const response = await this.request('/data-usage');
        return response.usage;
    }
    
    // ===== Earnings APIs =====
    
    /**
     * Get user's earnings overview
     * @returns {Promise<Object>} Earnings data with monthly stats
     */
    static async getEarnings() {
        const response = await this.request('/earnings');
        return response.earnings;
    }
    
    /**
     * Generate monthly earnings for enabled data types
     * @returns {Promise<Object>} Generated earnings info
     */
    static async generateMonthlyEarnings() {
        return await this.request('/earnings/generate', {
            method: 'POST'
        });
    }
    
    /**
     * Request a payout
     * @param {number} amount - Amount to payout
     * @param {string} method - Payout method ('paypal', 'bank', 'crypto')
     * @returns {Promise<Object>} Payout request result
     */
    static async requestPayout(amount, method) {
        const response = await this.request('/payout', {
            method: 'POST',
            body: JSON.stringify({
                amount: amount,
                method: method
            })
        });
        return response.payout;
    }
    
    /**
     * Get user's payout history
     * @returns {Promise<Array>} Array of payouts
     */
    static async getPayouts() {
        const response = await this.request('/payouts');
        return response.payouts;
    }
    
    /**
     * Add a bonus earning (special promotions)
     * @param {number} amount - Bonus amount
     * @param {string} description - Bonus description
     * @returns {Promise<Object>} Bonus earning result
     */
    static async addBonusEarning(amount, description) {
        const response = await this.request('/earnings/bonus', {
            method: 'POST',
            body: JSON.stringify({
                amount: amount,
                description: description
            })
        });
        return response.earning;
    }
    
    // Survey APIs (TODO: Implement in survey_routes.py)
    static async getSurveys() {
        // return await this.request('/surveys');
        throw new Error('Not implemented yet');
    }
    
    static async getSurveyDetails(surveyId) {
        // return await this.request(`/surveys/${surveyId}`);
        throw new Error('Not implemented yet');
    }
    
    static async startSurvey(surveyId) {
        // return await this.request(`/surveys/${surveyId}/start`, {
        //     method: 'POST'
        // });
        throw new Error('Not implemented yet');
    }
    
    static async submitSurvey(surveyId, responseId, answers) {
        // return await this.request(`/surveys/${surveyId}/submit`, {
        //     method: 'POST',
        //     body: JSON.stringify({ responseId, answers })
        // });
        throw new Error('Not implemented yet');
    }
    
    // ===== Activity APIs =====
    
    /**
     * Get user's activity feed
     * @param {number} limit - Number of activities to fetch
     * @param {number} offset - Offset for pagination
     * @param {string} type - Filter by activity type
     * @returns {Promise<Array>} Array of activities
     */
    static async getActivities(limit = 20, offset = 0, type = null) {
        let url = `/activities?limit=${limit}&offset=${offset}`;
        if (type) {
            url += `&type=${type}`;
        }
        const response = await this.request(url);
        return response.activities;
    }
    
    /**
     * Get activity statistics
     * @returns {Promise<Object>} Activity stats
     */
    static async getActivityStats() {
        const response = await this.request('/activities/stats');
        return response.stats;
    }
    
    /**
     * Create a new activity (for testing)
     * @param {Object} activityData - Activity data
     * @returns {Promise<Object>} Created activity
     */
    static async createActivity(activityData) {
        const response = await this.request('/activities', {
            method: 'POST',
            body: JSON.stringify(activityData)
        });
        return response.activity;
    }
}

// Helper function for authentication check
function redirectIfAuthenticated() {
    // Check if user is already logged in
    DataFairAPI.getProfile()
        .then(() => {
            // User is logged in, redirect to dashboard
            window.location.href = 'dashboard.html';
        })
        .catch(() => {
            // User is not logged in, stay on current page
        });
}

// Helper function to redirect if NOT authenticated
function requireAuthentication() {
    DataFairAPI.getProfile()
        .then(() => {
            // User is authenticated, continue
        })
        .catch(() => {
            // User is not authenticated, redirect to login
            window.location.href = 'login.html';
        });
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataFairAPI;
}