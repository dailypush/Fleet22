/* One deployment-local data loader for member and dues tables. */
(() => {
    const dataRoot = new URL('../../data/', document.currentScript.src);
    const table = document.querySelector('[data-boats-table]');
    if (!table) return;
    const body = table.tBodies[0];
    const showDues = table.hasAttribute('data-dues');
    const fields = ['Hull Number', 'Boat Name', 'Yacht Club'];
    if (showDues) fields.push('Fleet Dues', 'Class Dues');

    function showMessage(message, error = false) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = fields.length;
        cell.textContent = message;
        cell.className = error ? 'text-danger' : 'text-muted';
        cell.setAttribute('role', 'status');
        row.appendChild(cell);
        body.replaceChildren(row);
    }

    async function load() {
        showMessage('Loading boats…');
        try {
            const response = await fetch(new URL('boats/boats_fleet22.json', dataRoot));
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const boats = await response.json();
            if (!Array.isArray(boats) || !boats.length) throw new Error('Empty or invalid fleet data');
            const rows = boats.map(boat => {
                const row = document.createElement('tr');
                for (const field of fields) {
                    const cell = document.createElement('td');
                    cell.textContent = boat[field] || '';
                    if (field.endsWith('Dues')) cell.className = boat[field] === 'Paid' ? 'paid' : 'not-paid';
                    row.appendChild(cell);
                }
                return row;
            });
            body.replaceChildren(...rows);
        } catch (error) {
            showMessage('Unable to load fleet data. Please try reloading this page.', true);
            console.error('Fleet data:', error);
        }
        const updated = document.getElementById('lastUpdatedDate');
        if (updated) {
            try {
                const response = await fetch(new URL('metadata.json', dataRoot));
                if (!response.ok) throw new Error('Freshness metadata unavailable');
                const metadata = await response.json();
                const checked = new Date(metadata.checked_at);
                if (Number.isNaN(checked.getTime())) throw new Error('Invalid freshness date');
                updated.textContent = `Data last checked: ${checked.toLocaleString()}`;
            } catch {
                updated.textContent = 'Data refresh date unavailable.';
            }
        }
    }
    load();
})();
