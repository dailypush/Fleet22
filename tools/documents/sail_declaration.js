/**
 * Sail Declaration Form Manager
 * 
 * This module manages the J/105 North American Championship Sail Declaration form.
 * It handles fetching sail data, form validation, sail selection, and local storage persistence.
 * 
 * @module SailDeclarationManager
 * @version 2.0.0
 * @author Fleet22
 */

/**
 * Main class for managing the Sail Declaration form
 */
class SailDeclarationManager {
    /**
     * Initialize the Sail Declaration Manager
     */
    constructor() {
        // Configuration
        this.config = {
            dataUrl: 'https://raw.githubusercontent.com/dailypush/Fleet22/main/data/sails/sail_tags.json',
            storagePrefix: 'sailDeclaration_',
            autoSaveDelay: 2000, // milliseconds
            sailTypes: {
                jib: 'J',
                spinnaker: 'S89',
                main: 'M'
            }
        };

        // State management
        this.state = {
            sailsData: [],
            isLoading: false,
            hasError: false,
            errorMessage: '',
            selectedTags: new Set(),
            isDirty: false,
            autoSaveTimer: null
        };

        // DOM element references (will be initialized after DOM loads)
        this.elements = {};
    }

    /**
     * Initialize the application
     * Sets up event listeners and loads initial data
     */
    async init() {
        try {
            console.log('Initializing Sail Declaration Manager...');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // Cache DOM element references
            this.cacheElements();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load sail data
            await this.loadSailData();
            
            // Try to restore last saved state if hull number exists
            this.checkForAutoRestore();
            
            console.log('Sail Declaration Manager initialized successfully');
        } catch (error) {
            this.handleError('Initialization failed', error);
        }
    }

    /**
     * Cache frequently accessed DOM elements
     * @private
     */
    cacheElements() {
        const elementIds = [
            'hullNumber', 'owner', 'boatName', 'email', 'mobile',
            'jib1', 'jib2', 'main', 'spinnaker1', 'spinnaker2',
            'spinnaker1Color', 'spinnaker2Color'
        ];

        elementIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                this.elements[id] = element;
            } else {
                console.warn(`Element with id '${id}' not found`);
            }
        });

        // Cache buttons
        this.elements.printBtn = document.querySelector('button[onclick*="printSails"]');
        this.elements.saveBtn = document.querySelector('button[onclick*="saveDeclaration"]');
        this.elements.loadBtn = document.querySelector('button[onclick*="loadDeclaration"]');
    }

    /**
     * Setup all event listeners for form interactions
     * @private
     */
    setupEventListeners() {
        // Hull number input with debouncing
        if (this.elements.hullNumber) {
            this.elements.hullNumber.addEventListener('input', 
                this.debounce(() => this.handleHullNumberChange(), 300)
            );
        }

        // Sail dropdown changes
        ['jib1', 'jib2', 'spinnaker1', 'spinnaker2', 'main'].forEach(dropdownId => {
            if (this.elements[dropdownId]) {
                this.elements[dropdownId].addEventListener('change', 
                    () => this.handleSailSelectionChange(dropdownId)
                );
            }
        });

        // Track form changes for auto-save
        Object.values(this.elements).forEach(element => {
            if (element && element.tagName) {
                element.addEventListener('input', () => this.markAsDirty());
            }
        });

        // Warn before leaving with unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.state.isDirty) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }

    /**
     * Load sail data from remote JSON source
     * @async
     * @returns {Promise<void>}
     * @throws {Error} If data loading fails
     */
    async loadSailData() {
        this.state.isLoading = true;
        this.showLoadingState();

        try {
            console.log(`Fetching sail data from ${this.config.dataUrl}...`);
            
            const response = await fetch(this.config.dataUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                cache: 'default'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (!Array.isArray(data)) {
                throw new Error('Invalid data format: expected an array');
            }

            this.state.sailsData = data;
            console.log(`Successfully loaded ${data.length} sail records`);
            
            this.hideLoadingState();
            this.state.isLoading = false;
            this.state.hasError = false;

        } catch (error) {
            this.state.isLoading = false;
            this.state.hasError = true;
            this.state.errorMessage = error.message;
            this.handleError('Failed to load sail data', error);
            throw error;
        }
    }

    /**
     * Handle hull number input changes
     * Updates form with owner information and populates sail dropdowns
     * @private
     */
    handleHullNumberChange() {
        const hullNumber = this.elements.hullNumber?.value?.trim();
        
        if (!hullNumber) {
            this.clearAllFields();
            return;
        }

        console.log(`Hull number changed: ${hullNumber}`);

        // Filter sails for this hull number
        const filteredSails = this.state.sailsData.filter(
            sail => sail.Hull === hullNumber
        );

        if (filteredSails.length === 0) {
            console.log(`No sails found for hull ${hullNumber}`);
            this.clearAllFields();
            this.showMessage(`No sails found for hull number ${hullNumber}`, 'warning');
            return;
        }

        // Sort by delivery date (most recent first)
        const sortedSails = [...filteredSails].sort((a, b) => 
            new Date(b['Delivery Date']) - new Date(a['Delivery Date'])
        );

        // Auto-fill owner with most recent purchase
        if (this.elements.owner && sortedSails[0].Purchaser) {
            this.elements.owner.value = sortedSails[0].Purchaser;
        }

        // Clear boat name (user should fill this)
        if (this.elements.boatName) {
            this.elements.boatName.value = '';
        }

        // Initialize sail dropdowns
        this.initializeSailDropdowns(sortedSails);
        
        console.log(`Found ${filteredSails.length} sails for hull ${hullNumber}`);
    }

    /**
     * Initialize all sail dropdowns with filtered data
     * @private
     * @param {Array} sails - Filtered sail data for the selected hull
     */
    initializeSailDropdowns(sails) {
        // Reset selected tags
        this.state.selectedTags.clear();

        // Populate each dropdown
        this.populateSailDropdown('jib1', sails, this.config.sailTypes.jib);
        this.populateSailDropdown('jib2', sails, this.config.sailTypes.jib);
        this.populateSailDropdown('spinnaker1', sails, this.config.sailTypes.spinnaker);
        this.populateSailDropdown('spinnaker2', sails, this.config.sailTypes.spinnaker);
        this.populateSailDropdown('main', sails, this.config.sailTypes.main);
    }

    /**
     * Populate a single sail dropdown with options
     * @private
     * @param {string} dropdownId - ID of the dropdown element
     * @param {Array} sails - Available sails
     * @param {string} sailType - Type of sail (J, S89, M)
     */
    populateSailDropdown(dropdownId, sails, sailType) {
        const dropdown = this.elements[dropdownId];
        if (!dropdown) return;

        const currentValue = dropdown.value;
        
        // Reset dropdown
        dropdown.innerHTML = '<option value="">Select</option>';

        // Sort by delivery date (newest first)
        const sortedSails = [...sails]
            .filter(sail => sail['Sail Type'] === sailType)
            .sort((a, b) => new Date(b['Delivery Date']) - new Date(a['Delivery Date']));

        // Add options, excluding already selected tags
        sortedSails.forEach(sail => {
            const certNo = sail['Certificate No.'];
            
            if (certNo && (currentValue === certNo || !this.state.selectedTags.has(certNo))) {
                const option = document.createElement('option');
                option.value = certNo;
                
                // Format option text with sail details
                const sailmaker = sail.Sailmaker || 'Unknown';
                const deliveryDate = sail['Delivery Date'] || 'N/A';
                const year = deliveryDate !== 'N/A' ? new Date(deliveryDate).getFullYear() : 'N/A';
                
                option.textContent = `${certNo} - ${sailmaker} (${year})`;
                option.title = `${sailmaker} - Delivered: ${deliveryDate}`;
                
                dropdown.appendChild(option);
            }
        });

        // Restore previous selection if still valid
        if (currentValue && Array.from(dropdown.options).some(opt => opt.value === currentValue)) {
            dropdown.value = currentValue;
        }
    }

    /**
     * Handle changes to sail dropdown selections
     * @private
     * @param {string} changedDropdownId - ID of the dropdown that changed
     */
    handleSailSelectionChange(changedDropdownId) {
        console.log(`Sail selection changed: ${changedDropdownId}`);
        
        // Update selected tags set
        this.updateSelectedTags();
        
        // Refresh all dropdowns to exclude newly selected tags
        const hullNumber = this.elements.hullNumber?.value?.trim();
        if (hullNumber) {
            const filteredSails = this.state.sailsData.filter(
                sail => sail.Hull === hullNumber
            );
            
            if (filteredSails.length > 0) {
                // Repopulate all dropdowns
                const dropdowns = ['jib1', 'jib2', 'spinnaker1', 'spinnaker2', 'main'];
                dropdowns.forEach(id => {
                    const sailType = this.getSailTypeByDropdownId(id);
                    this.populateSailDropdown(id, filteredSails, sailType);
                });
            }
        }

        this.markAsDirty();
    }

    /**
     * Update the set of currently selected tags
     * @private
     */
    updateSelectedTags() {
        this.state.selectedTags.clear();
        
        const dropdownIds = ['jib1', 'jib2', 'spinnaker1', 'spinnaker2', 'main'];
        dropdownIds.forEach(id => {
            const value = this.elements[id]?.value;
            if (value) {
                this.state.selectedTags.add(value);
            }
        });
    }

    /**
     * Get sail type for a dropdown ID
     * @private
     * @param {string} dropdownId - Dropdown element ID
     * @returns {string} Sail type code (J, S89, or M)
     */
    getSailTypeByDropdownId(dropdownId) {
        if (dropdownId.includes('jib')) return this.config.sailTypes.jib;
        if (dropdownId.includes('spinnaker')) return this.config.sailTypes.spinnaker;
        if (dropdownId === 'main') return this.config.sailTypes.main;
        return '';
    }

    /**
     * Validate the form data
     * @returns {Object} Validation result with isValid boolean and errors array
     */
    validateForm() {
        const errors = [];
        
        const hullNumber = this.elements.hullNumber?.value?.trim();
        const owner = this.elements.owner?.value?.trim();
        
        if (!hullNumber) {
            errors.push('Hull number is required');
        }
        
        if (!owner) {
            errors.push('Owner name is required');
        }
        
        // Check if at least one sail is selected
        const selectedSails = [
            this.elements.jib1?.value,
            this.elements.jib2?.value,
            this.elements.main?.value,
            this.elements.spinnaker1?.value,
            this.elements.spinnaker2?.value
        ].filter(val => val);
        
        if (selectedSails.length === 0) {
            errors.push('At least one sail must be selected');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Print the sail declaration
     * Opens a new window with formatted declaration for printing
     */
    printSails() {
        const validation = this.validateForm();
        
        if (!validation.isValid) {
            alert('Please fix the following errors:\n\n' + validation.errors.join('\n'));
            return;
        }

        try {
            const formData = this.getFormData();
            const sailDetails = this.getSailDetails(formData);
            const printContent = this.generatePrintContent(formData, sailDetails);
            
            this.openPrintWindow(printContent);
            
            console.log('Print dialog opened');
        } catch (error) {
            this.handleError('Failed to generate print content', error);
        }
    }

    /**
     * Get all form data
     * @private
     * @returns {Object} Form data object
     */
    getFormData() {
        return {
            hullNumber: this.elements.hullNumber?.value || '',
            owner: this.elements.owner?.value || '',
            boatName: this.elements.boatName?.value || '',
            email: this.elements.email?.value || '',
            mobile: this.elements.mobile?.value || '',
            jib1Cert: this.elements.jib1?.value || '',
            jib2Cert: this.elements.jib2?.value || '',
            mainCert: this.elements.main?.value || '',
            spinnaker1Cert: this.elements.spinnaker1?.value || '',
            spinnaker2Cert: this.elements.spinnaker2?.value || '',
            spinnaker1Color: this.elements.spinnaker1Color?.value || '',
            spinnaker2Color: this.elements.spinnaker2Color?.value || ''
        };
    }

    /**
     * Get detailed sail information for selected certificates
     * @private
     * @param {Object} formData - Form data containing certificate numbers
     * @returns {Object} Sail details object
     */
    getSailDetails(formData) {
        return {
            jib1: this.getSailByCertificate(formData.jib1Cert),
            jib2: this.getSailByCertificate(formData.jib2Cert),
            main: this.getSailByCertificate(formData.mainCert),
            spinnaker1: this.getSailByCertificate(formData.spinnaker1Cert),
            spinnaker2: this.getSailByCertificate(formData.spinnaker2Cert)
        };
    }

    /**
     * Find sail data by certificate number
     * @private
     * @param {string} certNo - Certificate number
     * @returns {Object|null} Sail data or null if not found
     */
    getSailByCertificate(certNo) {
        if (!certNo) return null;
        return this.state.sailsData.find(sail => sail["Certificate No."] === certNo) || null;
    }

    /**
     * Generate HTML content for printing
     * @private
     * @param {Object} formData - Form data
     * @param {Object} sailDetails - Detailed sail information
     * @returns {string} HTML content for printing
     */
    generatePrintContent(formData, sailDetails) {
        const formatSailRow = (sailType, sail, color = '') => {
            if (!sail) return '';
            
            return `
                <tr>
                    <td>${sailType}</td>
                    <td>${sail['Certificate No.'] || 'N/A'}</td>
                    <td>${sail.Sailmaker || 'N/A'}</td>
                    <td>${sail['Delivery Date'] || 'N/A'}</td>
                    <td>${color || 'N/A'}</td>
                </tr>
            `;
        };

        return `
            <header class="text-center my-2">
                <h1>J/105 North American Championship</h1>
                <h2>Sail Declaration</h2>
                <p class="text-center mb-3">This form lists all the sails to be used for the 2024 J/105 North American Championship.</p>
            </header>
            <h3>Sail List for Hull ${formData.hullNumber}</h3>
            <p><strong>Boat Name:</strong> ${formData.boatName || 'Not Provided'}</p>
            <p><strong>Owner:</strong> ${formData.owner}</p>
            <p><strong>Email:</strong> ${formData.email || 'Not Provided'}</p>
            <p><strong>Mobile:</strong> ${formData.mobile || 'Not Provided'}</p>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Sail Type</th>
                        <th>Certificate No.</th>
                        <th>Sailmaker</th>
                        <th>Delivery Date</th>
                        <th>Color/Description</th>
                    </tr>
                </thead>
                <tbody>
                    ${formatSailRow('Jib 1', sailDetails.jib1)}
                    ${formatSailRow('Jib 2', sailDetails.jib2)}
                    ${formatSailRow('Main', sailDetails.main)}
                    ${formatSailRow('Spinnaker 1', sailDetails.spinnaker1, formData.spinnaker1Color)}
                    ${formatSailRow('Spinnaker 2', sailDetails.spinnaker2, formData.spinnaker2Color)}
                </tbody>
            </table>
            <div class="mt-4">
                <p>By signing this form I declare that my sails will be in compliance with the J/105 Class Rules at all times.</p>
                <table class="table table-borderless mt-3">
                    <tr>
                        <td style="width: 50%;">
                            <p>Owner's Signature: _________________________</p>
                        </td>
                        <td style="width: 50%;">
                            <p>Date: _________________________</p>
                        </td>
                    </tr>
                </table>
                <p class="text-muted small mt-3">Generated: ${new Date().toLocaleString()}</p>
            </div>
        `;
    }

    /**
     * Open print window with formatted content
     * @private
     * @param {string} content - HTML content to print
     */
    openPrintWindow(content) {
        const printWindow = window.open('', '', 'height=600,width=800');
        
        if (!printWindow) {
            throw new Error('Failed to open print window. Please check popup blocker settings.');
        }

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sail Declaration - Print</title>
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
                <style>
                    @media print {
                        .no-print { display: none; }
                    }
                    body { padding: 20px; }
                </style>
            </head>
            <body>
                <div class="container mt-5">
                    ${content}
                </div>
            </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        
        // Wait for content to load, then print
        setTimeout(() => {
            printWindow.print();
        }, 250);
    }

    /**
     * Save declaration to local storage
     */
    saveDeclaration() {
        try {
            const formData = this.getFormData();
            
            if (!formData.hullNumber) {
                alert('Please enter a hull number before saving.');
                return;
            }

            const storageKey = this.config.storagePrefix + formData.hullNumber;
            const dataToSave = {
                ...formData,
                savedAt: new Date().toISOString(),
                version: '2.0'
            };

            localStorage.setItem(storageKey, JSON.stringify(dataToSave));
            
            this.state.isDirty = false;
            this.showMessage(`Declaration for Hull ${formData.hullNumber} saved successfully!`, 'success');
            
            console.log(`Declaration saved for hull ${formData.hullNumber}`);
        } catch (error) {
            this.handleError('Failed to save declaration', error);
        }
    }

    /**
     * Load declaration from local storage
     */
    async loadDeclaration() {
        try {
            const hullNumber = this.elements.hullNumber?.value?.trim();
            
            if (!hullNumber) {
                alert('Please enter a hull number to load data.');
                return;
            }

            const storageKey = this.config.storagePrefix + hullNumber;
            const savedData = localStorage.getItem(storageKey);

            if (!savedData) {
                alert(`No saved declaration found for Hull ${hullNumber}.`);
                return;
            }

            const formData = JSON.parse(savedData);
            
            // Restore form fields
            this.restoreFormData(formData);
            
            // Update form with hull-specific data
            this.handleHullNumberChange();
            
            // Wait for dropdowns to populate, then restore sail selections
            setTimeout(() => {
                this.restoreSailSelections(formData);
                this.state.isDirty = false;
            }, 100);

            const savedDate = formData.savedAt ? new Date(formData.savedAt).toLocaleString() : 'Unknown';
            this.showMessage(`Declaration for Hull ${hullNumber} loaded successfully! (Saved: ${savedDate})`, 'success');
            
            console.log(`Declaration loaded for hull ${hullNumber}`);
        } catch (error) {
            this.handleError('Failed to load declaration', error);
        }
    }

    /**
     * Restore form data from saved object
     * @private
     * @param {Object} formData - Saved form data
     */
    restoreFormData(formData) {
        const fields = ['owner', 'boatName', 'email', 'mobile', 'spinnaker1Color', 'spinnaker2Color'];
        
        fields.forEach(field => {
            if (this.elements[field] && formData[field]) {
                this.elements[field].value = formData[field];
            }
        });
    }

    /**
     * Restore sail selections from saved data
     * @private
     * @param {Object} formData - Saved form data
     */
    restoreSailSelections(formData) {
        const sailFields = {
            jib1: 'jib1Cert',
            jib2: 'jib2Cert',
            main: 'mainCert',
            spinnaker1: 'spinnaker1Cert',
            spinnaker2: 'spinnaker2Cert'
        };

        Object.entries(sailFields).forEach(([elementId, dataKey]) => {
            if (this.elements[elementId] && formData[dataKey]) {
                this.elements[elementId].value = formData[dataKey];
            }
        });

        // Update selected tags after restoration
        this.updateSelectedTags();
        
        // Refresh dropdowns
        const hullNumber = this.elements.hullNumber?.value?.trim();
        if (hullNumber) {
            const filteredSails = this.state.sailsData.filter(sail => sail.Hull === hullNumber);
            if (filteredSails.length > 0) {
                this.initializeSailDropdowns(filteredSails);
                // Restore selections again after refresh
                Object.entries(sailFields).forEach(([elementId, dataKey]) => {
                    if (this.elements[elementId] && formData[dataKey]) {
                        this.elements[elementId].value = formData[dataKey];
                    }
                });
            }
        }
    }

    /**
     * Check if there's a saved declaration and offer to restore
     * @private
     */
    checkForAutoRestore() {
        // This could be enhanced to show a list of saved declarations
        console.log('Auto-restore check complete');
    }

    /**
     * Clear all form fields
     * @private
     */
    clearAllFields() {
        const textFields = ['owner', 'boatName', 'email', 'mobile'];
        textFields.forEach(field => {
            if (this.elements[field]) {
                this.elements[field].value = '';
            }
        });

        const dropdowns = ['jib1', 'jib2', 'spinnaker1', 'spinnaker2', 'main'];
        dropdowns.forEach(field => {
            if (this.elements[field]) {
                this.elements[field].innerHTML = '<option value="">Select</option>';
            }
        });

        this.state.selectedTags.clear();
    }

    /**
     * Mark form as having unsaved changes
     * @private
     */
    markAsDirty() {
        this.state.isDirty = true;
        
        // Auto-save after delay
        if (this.state.autoSaveTimer) {
            clearTimeout(this.state.autoSaveTimer);
        }
        
        // Uncomment to enable auto-save:
        // this.state.autoSaveTimer = setTimeout(() => {
        //     this.saveDeclaration();
        // }, this.config.autoSaveDelay);
    }

    /**
     * Show loading state UI
     * @private
     */
    showLoadingState() {
        console.log('Loading sail data...');
        // Could add a loading spinner here
    }

    /**
     * Hide loading state UI
     * @private
     */
    hideLoadingState() {
        console.log('Loading complete');
        // Could remove loading spinner here
    }

    /**
     * Show message to user
     * @private
     * @param {string} message - Message to display
     * @param {string} type - Message type (success, warning, error)
     */
    showMessage(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        // Could implement toast notifications here
    }

    /**
     * Handle errors with proper logging and user feedback
     * @private
     * @param {string} context - Error context description
     * @param {Error} error - The error object
     */
    handleError(context, error) {
        console.error(`${context}:`, error);
        alert(`${context}\n\n${error.message}\n\nPlease try again or contact support if the problem persists.`);
    }

    /**
     * Debounce function to limit rapid function calls
     * @private
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// ============================================================================
// Global Functions (for backward compatibility with inline onclick handlers)
// ============================================================================

let sailDeclarationManager;

/**
 * Print sails function (global for backward compatibility)
 */
function printSails() {
    if (sailDeclarationManager) {
        sailDeclarationManager.printSails();
    }
}

/**
 * Save declaration function (global for backward compatibility)
 */
function saveDeclaration() {
    if (sailDeclarationManager) {
        sailDeclarationManager.saveDeclaration();
    }
}

/**
 * Load declaration function (global for backward compatibility)
 */
function loadDeclaration() {
    if (sailDeclarationManager) {
        sailDeclarationManager.loadDeclaration();
    }
}

// ============================================================================
// Application Initialization
// ============================================================================

/**
 * Initialize the application when DOM is ready
 */
(async function initializeApp() {
    try {
        sailDeclarationManager = new SailDeclarationManager();
        await sailDeclarationManager.init();
    } catch (error) {
        console.error('Failed to initialize Sail Declaration Manager:', error);
        alert('Failed to initialize the application. Please refresh the page and try again.');
    }
})();
