# Sail Declaration Form - Technical Documentation

## Overview

The Sail Declaration Form is a modern, ES6+ JavaScript application for managing J/105 North American Championship sail declarations. The codebase has been refactored to follow best practices with proper separation of concerns, comprehensive error handling, and detailed documentation.

## Architecture

### File Structure

```
tools/documents/
├── Sail_dec_auto.html          # Main HTML page
├── sail_declaration.js          # External JavaScript module (ES6+)
└── SAIL_DECLARATION_README.md   # This documentation file
```

### Design Patterns

- **Class-Based Architecture**: Uses ES6 classes for better organization and encapsulation
- **Separation of Concerns**: HTML structure separate from business logic
- **State Management**: Centralized state object for managing application data
- **Error Boundaries**: Comprehensive try-catch blocks with user-friendly error messages
- **Event-Driven**: Async/await for asynchronous operations

## Code Organization

### Main Class: `SailDeclarationManager`

The application is built around a single class that manages all form functionality.

#### Key Components:

1. **Configuration** (`config`)
   - Data source URLs
   - Storage keys
   - Sail type mappings
   - Auto-save delays

2. **State Management** (`state`)
   - Sail data cache
   - Loading indicators
   - Error states
   - Selected tags tracking
   - Dirty flag for unsaved changes

3. **DOM Element Cache** (`elements`)
   - Pre-cached references to frequently accessed elements
   - Improves performance by avoiding repeated DOM queries

### Main Methods

#### Initialization

```javascript
async init()
```
- Sets up the application on page load
- Caches DOM elements
- Attaches event listeners
- Loads sail data from remote source

#### Data Loading

```javascript
async loadSailData()
```
- Fetches sail tag data from GitHub repository
- Implements error handling for network failures
- Shows loading states during fetch
- Validates data format

#### Form Management

```javascript
handleHullNumberChange()
```
- Responds to hull number input
- Filters sails for the selected hull
- Auto-fills owner information
- Initializes sail dropdowns

```javascript
initializeSailDropdowns(sails)
```
- Populates all sail selection dropdowns
- Sorts sails by delivery date (newest first)
- Excludes already-selected tags
- Formats display text with sail details

#### Selection Handling

```javascript
handleSailSelectionChange(dropdownId)
```
- Updates when a sail is selected
- Prevents duplicate tag selection
- Refreshes all dropdowns dynamically
- Marks form as having unsaved changes

#### Validation

```javascript
validateForm()
```
- Validates required fields
- Ensures at least one sail is selected
- Returns validation result with error messages

#### Persistence

```javascript
saveDeclaration()
```
- Saves form data to localStorage
- Keys by hull number
- Includes version and timestamp

```javascript
loadDeclaration()
```
- Restores previously saved declarations
- Validates hull number exists
- Repopulates all form fields
- Restores sail selections

#### Printing

```javascript
printSails()
```
- Validates form before printing
- Generates formatted HTML for print
- Opens print window with proper styling
- Includes signature lines and compliance statement

## Modern JavaScript Features

### ES6+ Features Used

1. **Classes and Constructors**
   ```javascript
   class SailDeclarationManager {
       constructor() { ... }
   }
   ```

2. **Async/Await**
   ```javascript
   async loadSailData() {
       const response = await fetch(url);
       const data = await response.json();
   }
   ```

3. **Arrow Functions**
   ```javascript
   const sortedSails = [...sails].sort((a, b) => 
       new Date(b['Delivery Date']) - new Date(a['Delivery Date'])
   );
   ```

4. **Template Literals**
   ```javascript
   option.textContent = `${certNo} - ${sailmaker} (${year})`;
   ```

5. **Destructuring**
   ```javascript
   const { isValid, errors } = this.validateForm();
   ```

6. **Spread Operator**
   ```javascript
   const sortedSails = [...sails].sort(...);
   ```

7. **Set Data Structure**
   ```javascript
   this.state.selectedTags = new Set();
   ```

8. **Default Parameters**
   ```javascript
   showMessage(message, type = 'info') { ... }
   ```

## Error Handling

### Error Boundaries

All major operations are wrapped in try-catch blocks:

```javascript
try {
    // Operation that might fail
    await this.loadSailData();
} catch (error) {
    this.handleError('Failed to load sail data', error);
}
```

### User-Friendly Error Messages

The `handleError()` method provides:
- Console logging for developers
- Alert messages for users
- Context-specific error descriptions
- Suggestions for resolution

### Network Error Handling

```javascript
if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
}
```

## JSDoc Documentation

Every method includes comprehensive JSDoc comments:

```javascript
/**
 * Load sail data from remote JSON source
 * @async
 * @returns {Promise<void>}
 * @throws {Error} If data loading fails
 */
async loadSailData() { ... }
```

### JSDoc Tags Used:
- `@module` - Module identification
- `@class` - Class description
- `@async` - Async method indicator
- `@returns` - Return type and description
- `@param` - Parameter documentation
- `@throws` - Exception documentation
- `@private` - Internal method indicator

## State Management

### State Object Structure

```javascript
this.state = {
    sailsData: [],           // Array of all sail records
    isLoading: false,        // Loading indicator flag
    hasError: false,         // Error state flag
    errorMessage: '',        // Current error message
    selectedTags: new Set(), // Set of selected certificate numbers
    isDirty: false,          // Unsaved changes flag
    autoSaveTimer: null      // Auto-save timeout handle
}
```

### State Updates

State is modified through dedicated methods:
- `markAsDirty()` - Sets isDirty flag
- `updateSelectedTags()` - Updates tag selection set
- `showLoadingState()` / `hideLoadingState()` - Toggle loading indicators

## Event Handling

### Event Listeners

1. **Input Events with Debouncing**
   ```javascript
   this.elements.hullNumber.addEventListener('input', 
       this.debounce(() => this.handleHullNumberChange(), 300)
   );
   ```

2. **Change Events**
   ```javascript
   this.elements.jib1.addEventListener('change', 
       () => this.handleSailSelectionChange('jib1')
   );
   ```

3. **Before Unload Warning**
   ```javascript
   window.addEventListener('beforeunload', (e) => {
       if (this.state.isDirty) {
           e.preventDefault();
           e.returnValue = 'You have unsaved changes...';
       }
   });
   ```

## Performance Optimizations

### DOM Element Caching

```javascript
cacheElements() {
    const elementIds = ['hullNumber', 'owner', ...];
    elementIds.forEach(id => {
        this.elements[id] = document.getElementById(id);
    });
}
```

### Debouncing

```javascript
debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}
```

### Efficient Filtering

Uses Set for O(1) lookup when checking selected tags:
```javascript
this.state.selectedTags = new Set();
// Later...
if (!this.state.selectedTags.has(certNo)) { ... }
```

## Data Flow

```
1. Page Load
   ↓
2. Initialize Manager
   ↓
3. Cache DOM Elements
   ↓
4. Setup Event Listeners
   ↓
5. Load Sail Data (async)
   ↓
6. User Enters Hull Number
   ↓
7. Filter & Sort Sails
   ↓
8. Populate Dropdowns
   ↓
9. User Selects Sails
   ↓
10. Update State & Refresh Dropdowns
    ↓
11. Save/Print Declaration
```

## Local Storage

### Storage Keys

Format: `sailDeclaration_{hullNumber}`

Example: `sailDeclaration_123`

### Stored Data Structure

```javascript
{
    hullNumber: "123",
    owner: "John Doe",
    boatName: "Fast Boat",
    email: "john@example.com",
    mobile: "555-1234",
    jib1Cert: "J12345",
    jib2Cert: "J12346",
    mainCert: "M12347",
    spinnaker1Cert: "S8912348",
    spinnaker2Cert: "S8912349",
    spinnaker1Color: "Red/White",
    spinnaker2Color: "Blue",
    savedAt: "2025-10-11T12:00:00.000Z",
    version: "2.0"
}
```

## Browser Compatibility

### Requirements

- Modern browser with ES6+ support (Chrome 51+, Firefox 54+, Safari 10+, Edge 15+)
- localStorage API support
- Fetch API support
- Promise support

### Polyfills

For older browsers, consider adding polyfills for:
- `fetch()`
- `Promise`
- `Array.prototype.find()`
- `Array.prototype.includes()`

## Testing

### Manual Testing Checklist

- [ ] Page loads without errors
- [ ] Sail data fetches successfully
- [ ] Hull number input filters sails correctly
- [ ] Dropdowns populate with correct sails
- [ ] Duplicate tag selection is prevented
- [ ] Save functionality works
- [ ] Load functionality restores data
- [ ] Print generates correct output
- [ ] Form validation works
- [ ] Error messages display properly
- [ ] Unsaved changes warning appears

### Error Scenarios to Test

1. Network failure during data load
2. Invalid hull number
3. No sails found for hull
4. Saving without hull number
5. Loading non-existent declaration
6. Print with incomplete form

## Future Enhancements

### Planned Features (Commented Out)

1. **Auto-save** - Currently commented out, can be enabled:
   ```javascript
   // Uncomment to enable auto-save:
   // this.state.autoSaveTimer = setTimeout(() => {
   //     this.saveDeclaration();
   // }, this.config.autoSaveDelay);
   ```

2. **Loading Indicators** - Placeholder methods exist:
   ```javascript
   showLoadingState() {
       // Could add a loading spinner here
   }
   ```

3. **Toast Notifications** - Prepared for implementation:
   ```javascript
   showMessage(message, type = 'info') {
       // Could implement toast notifications here
   }
   ```

### Potential Improvements

- Add TypeScript for type safety
- Implement unit tests with Jest
- Add E2E tests with Cypress
- Create a build process with webpack
- Add CSS preprocessing with SASS
- Implement progressive web app features
- Add offline support with service workers

## Troubleshooting

### Common Issues

**Issue: Page loads but no sails appear**
- Check browser console for errors
- Verify network connectivity
- Confirm data URL is accessible

**Issue: Dropdown doesn't update after selection**
- Check for JavaScript errors
- Verify event listeners are attached
- Check that `handleSailSelectionChange()` is being called

**Issue: Save/Load not working**
- Check if localStorage is enabled
- Verify browser doesn't block localStorage
- Check storage quota hasn't been exceeded

**Issue: Print window is blank**
- Check popup blocker settings
- Verify print content generation
- Check browser console for errors

## Development

### Local Development

1. Clone the repository
2. Navigate to `tools/documents/`
3. Open `Sail_dec_auto.html` in a modern browser
4. Open browser DevTools to view console logs

### Debugging

Enable verbose logging by checking browser console. The application logs:
- Initialization steps
- Data loading progress
- User interactions
- Error details
- State changes

### Code Style

- Use 4 spaces for indentation
- Use camelCase for variables and methods
- Use PascalCase for classes
- Add JSDoc comments for all public methods
- Keep methods focused and single-purpose
- Use descriptive variable names

## Credits

- **Version**: 2.0.0
- **Author**: Fleet22
- **License**: MIT
- **Repository**: https://github.com/dailypush/Fleet22

## Support

For issues or questions:
1. Check this documentation
2. Review browser console for errors
3. Check GitHub repository issues
4. Contact Fleet22 support

---

Last Updated: October 11, 2025
