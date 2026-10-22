/** Pure helpers for shareable sail analysis views and portable record exports. */
const SailAnalysisUtils = {
    normalizeHull(value) {
        const hull = String(value ?? '').trim().replace(/^0+(?=\d)/, '');
        return /^\d{1,6}$/.test(hull) ? hull : null;
    },

    parseView(url, currentYear = new Date().getFullYear()) {
        const params = new URL(url, 'https://fleet22.us').searchParams;
        const year = name => /^\d{4}$/.test(params.get(name) || '') &&
            Number(params.get(name)) >= 1900 && Number(params.get(name)) <= currentYear + 1
            ? Number(params.get(name)) : null;
        const hull = this.normalizeHull(params.get('hull'));
        const startYear = year('from'), endYear = year('to');
        const cellYear = year('cellYear');
        const text = name => (params.get(name) || '').slice(0, 200);
        return {
            hull,
            startYear: startYear && endYear ? Math.min(startYear, endYear) : null,
            endYear: startYear && endYear ? Math.max(startYear, endYear) : null,
            sailType: text('type'), sailmaker: text('maker'),
            includeUndated: params.get('undated') !== '0', query: text('q'),
            cell: cellYear && text('cellType') && text('cellMaker') ? {
                year: cellYear, sailType: text('cellType'), sailmaker: text('cellMaker'),
                key: JSON.stringify([text('cellType'), text('cellMaker')])
            } : null
        };
    },

    viewUrl(base, view) {
        const url = new URL(base);
        url.search = '';
        url.hash = '';
        if (!view.hull) return url.href;
        const values = {
            hull: view.hull, from: view.startYear, to: view.endYear,
            type: view.sailType, maker: view.sailmaker, undated: view.includeUndated ? '1' : '0',
            q: view.query,
            cellYear: view.cell?.year, cellType: view.cell?.sailType, cellMaker: view.cell?.sailmaker
        };
        for (const [key, value] of Object.entries(values)) {
            if (value !== null && value !== undefined && value !== '') url.searchParams.set(key, value);
        }
        return url.href;
    },

    latestDeliveries(records) {
        const types = [...new Set(records.map(record => record.sailType))].sort();
        return types.map(sailType => {
            const dated = records.filter(record => record.sailType === sailType && record.year !== null);
            const latestDate = dated.map(record => record.source['Delivery Date']).sort().at(-1) || null;
            return {sailType, date: latestDate,
                records: dated.filter(record => record.source['Delivery Date'] === latestDate)};
        });
    },

    recordsCsv(records, lookup = new Map()) {
        // Quote every cell for commas/newlines and neutralize spreadsheet formula prefixes.
        const cell = value => {
            let text = String(value ?? '');
            if (/^[\s\u0000-\u001f]*[=+\-@]/.test(text) || /^[\t\r\n]/.test(text)) text = "'" + text;
            return '"' + text.replace(/"/g, '""') + '"';
        };
        const rows = [['Hull', 'Current boat name', 'Current owner', 'Certificate', 'Delivery date',
            'Sail type', 'Sailmaker', 'Purchaser at registration', 'Notes', 'Record flags']];
        for (const record of records) {
            const details = lookup.get(record.hull);
            rows.push([record.hull, details?.boatName, details?.owner, record.certificate,
                record.source['Delivery Date'], record.sailType, record.sailmaker,
                record.source.Purchaser, record.source.Notes, record.flags.join('; ')]);
        }
        return '\uFEFF' + rows.map(row => row.map(cell).join(',')).join('\r\n') + '\r\n';
    }
};
if (typeof module !== 'undefined' && module.exports) module.exports = SailAnalysisUtils;
if (typeof window !== 'undefined') window.SailAnalysisUtils = SailAnalysisUtils;
