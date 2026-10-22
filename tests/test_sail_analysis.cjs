const {test} = require('node:test');
const assert = require('node:assert/strict');
const SailAnalysisHeatmap = require('../analysis/sail-analysis.js');

function analysis() {
    const app = new SailAnalysisHeatmap('heatmap', 'sails.json', {autoInit: false});
    app.elements = {
        hullSelect: {value: ''}, owner: {value: ''}, boatName: {value: ''},
        selectedBoat: {textContent: ''}, lookupStatus: {textContent: ''}
    };
    app.state.boatLookup = new Map([
        ['493', {boatName: 'Rapscallion', owner: 'Current owner'}],
        ['72', {boatName: 'Highlander', owner: 'Another owner'}],
        ['999', {boatName: 'No sails boat', owner: 'Third owner'}]
    ]);
    app.state.boatLookupLoaded = true;
    app.sailData = [
        {Hull: '493', Purchaser: 'Historical buyer', 'Sail Type': 'M', Sailmaker: 'North', 'Delivery Date': '2026-01-01'},
        {Hull: '72', 'Sail Type': 'J', Sailmaker: 'Quantum', 'Delivery Date': '2025-01-01'}
    ];
    app.dataLoaded = true;
    app.view = {hull: null, clearCount: 0, noData: false};
    app.populateHullDropdown = () => { app.elements.hullSelect.value = app.currentHull || ''; };
    app.updateStats = hull => { app.view.hull = hull; };
    app.createHeatmap = (_, hull) => { app.view.hull = hull; };
    app.clearVisualization = () => { app.view.hull = null; app.view.clearCount++; app.view.noData = false; };
    app.hideNoData = () => { app.view.noData = false; };
    app.showNoData = () => { app.view.noData = true; };
    return app;
}

test('choosing a name suggestion updates hull, identity and chart together', () => {
    const app = analysis();
    app.selectBoatSuggestion(app.findBoatSuggestions('boatName', 'rap')[0]);
    assert.equal(app.currentHull, '493');
    assert.equal(app.elements.hullSelect.value, '493');
    assert.equal(app.elements.boatName.value, 'Rapscallion');
    assert.equal(app.elements.owner.value, 'Current owner');
    assert.equal(app.view.hull, '493');
    assert.match(app.elements.selectedBoat.textContent, /Hull 493.*Rapscallion.*Current owner/);
});

test('typing/searching alone never changes the selected hull or analysis identity', () => {
    const app = analysis();
    app.selectHull('493');
    app.elements.owner.value = 'Another';
    app.state.identityOverrides.add('owner');
    const matches = app.findBoatSuggestions('owner', 'Another');
    assert.equal(matches[0].hull, '72');
    assert.equal(app.currentHull, '493');
    assert.equal(app.view.hull, '493');
    assert.match(app.elements.selectedBoat.textContent, /Rapscallion/);
    app.selectBoatSuggestion(matches[0]);
    assert.equal(app.currentHull, '72');
    assert.equal(app.elements.owner.value, 'Another owner');
});

test('direct hull selection clears search edits and refreshes both names', () => {
    const app = analysis();
    app.selectHull('493');
    app.elements.boatName.value = 'Search text';
    app.state.identityOverrides.add('boatName');
    app.selectHull(' 0072 ');
    assert.equal(app.currentHull, '72');
    assert.equal(app.elements.boatName.value, 'Highlander');
    assert.equal(app.elements.owner.value, 'Another owner');
    assert.equal(app.state.identityOverrides.size, 0);
});

test('clearing selection removes names, chart and resize target', () => {
    const app = analysis();
    app.selectHull('493');
    app.selectHull('');
    app.handleResize();
    assert.equal(app.currentHull, null);
    assert.equal(app.elements.owner.value, '');
    assert.equal(app.elements.boatName.value, '');
    assert.equal(app.elements.hullSelect.value, '');
    assert.equal(app.view.hull, null);
    assert.equal(app.elements.selectedBoat.textContent, 'No boat selected.');
});

test('a named boat without sails clears previous results and shows no-data state', () => {
    const app = analysis();
    app.selectHull('493');
    const original = global.document;
    const statistics = {textContent: ''};
    global.document = {getElementById: () => statistics};
    try {
        app.selectBoatSuggestion(app.findBoatSuggestions('boatName', 'No sails')[0]);
        assert.equal(app.currentHull, '999');
        assert.equal(app.elements.owner.value, 'Third owner');
        assert.equal(app.view.hull, null);
        assert.equal(app.view.noData, true);
        assert.equal(statistics.textContent, 'No sail records for this hull.');
    } finally {
        global.document = original;
    }
});

test('hulls without registry matches retain direct analysis with no old owner fallback', () => {
    const app = analysis();
    app.state.boatLookup.delete('493');
    app.selectHull('72');
    app.selectHull('493');
    assert.equal(app.elements.owner.value, '');
    assert.equal(app.elements.boatName.value, '');
    assert.equal(app.view.hull, '493');
    assert.match(app.elements.selectedBoat.textContent, /Owner: Unavailable/);
});

test('late registry loading preserves search text and the selected chart', async () => {
    const app = analysis();
    app.selectHull('493');
    app.elements.owner.value = 'Typed while loading';
    app.state.identityOverrides.add('owner');
    const original = global.fetch;
    global.fetch = async url => ({ok: true, json: async () => url.includes('members') ? [{
        Hull: '493', Status: 'OW', 'Boat Name': 'Registry boat',
        'Owners/Helmsmen': 'Registry owner', 'Class Membership': `Member ${new Date().getFullYear()}`
    }] : []});
    try {
        await app.loadBoatData();
        assert.equal(app.elements.owner.value, 'Typed while loading');
        assert.equal(app.elements.boatName.value, 'Registry boat');
        assert.equal(app.currentHull, '493');
        assert.equal(app.view.hull, '493');
    } finally {
        global.fetch = original;
    }
});

test('owner lookup failure preserves fleet-name search and direct hull analysis', async () => {
    const app = analysis();
    const original = global.fetch;
    global.fetch = async url => url.includes('members') ? {ok: false, status: 503} : {
        ok: true, json: async () => [{'Hull Number': '493', 'Boat Name': 'Fleet boat'}]
    };
    try {
        await app.loadBoatData();
        app.selectHull('493');
        assert.equal(app.state.ownerLookupUnavailable, true);
        assert.equal(app.elements.owner.value, '');
        assert.equal(app.findBoatSuggestions('boatName', 'Fleet')[0].hull, '493');
        assert.equal(app.view.hull, '493');
        assert.match(app.elements.lookupStatus.textContent, /unavailable/);
    } finally {
        global.fetch = original;
    }
});

const sail = (certificate, date, extra = {}) => ({
    Hull: '493', 'Certificate No.': certificate, 'Delivery Date': date,
    'Sail Type': 'M', Sailmaker: 'North', Purchaser: 'Historical purchaser', Notes: '', ...extra
});

function dataAnalysis(records) {
    const app = new SailAnalysisHeatmap('heatmap', 'sails.json', {autoInit: false});
    app.sailData = records;
    app.indexRecords();
    app.filters = {startYear: 2020, endYear: 2026, sailType: '', sailmaker: '', includeUndated: true};
    return app;
}

test('delivery years reject invalid calendar dates without timezone shifts', () => {
    for (const value of ['', null, '0000-00-00', '2025-02-29', '2026-04-31', '2026-13-01', '2026-00-01', 'not a date']) {
        assert.equal(SailAnalysisHeatmap.deliveryYear(value), null, String(value));
    }
    assert.equal(SailAnalysisHeatmap.deliveryYear('2024-02-29'), 2024);
    assert.equal(SailAnalysisHeatmap.deliveryYear('2026-01-01'), 2026);
    assert.equal(SailAnalysisHeatmap.deliveryYear('2025-12-31'), 2025);
});

test('transfers and repeated certificates are flagged without discarding history', () => {
    const source = [sail('A', '2026-01-01'), sail('A', '2026-02-01'),
        sail('B', '2025-01-01'), sail('B', '2025-01-01', {Hull: '72'}),
        sail('', '2025-01-01'), sail('', '2025-01-01')];
    const before = JSON.stringify(source);
    const records = SailAnalysisHeatmap.prepareRecords(source);
    assert.equal(records.length, 6);
    assert.match(records[0].flags.join(' '), /repeated on this hull/);
    assert.match(records[2].flags.join(' '), /also recorded on hull 72/);
    assert.match(records[3].flags.join(' '), /also recorded on hull 493/);
    assert.equal(records[4].repeatedCertificate, false);
    assert.equal(JSON.stringify(source), before);
});

test('unknown dates and blank sail metadata remain inspectable records', () => {
    const app = dataAnalysis([sail('A', '0000-00-00', {'Sail Type': '', Sailmaker: ''})]);
    const record = app.records[0];
    assert.equal(record.year, null);
    assert.equal(record.sailType, 'Unknown type');
    assert.equal(record.sailmaker, 'Unknown sailmaker');
    assert.match(record.flags.join(' '), /Unknown delivery date/);
    assert.equal(app.processDataForHeatmap(app.records).length, 0);
    app.filteredRecords = app.filterRecords(app.records);
    assert.equal(app.getTableRecords().length, 1);
});

test('notes flags preserve original notes without deciding exemptions', () => {
    const app = dataAnalysis([sail('A', '2026-01-01', {Notes: 'Purchased used; warranty replacement mentioned.'})]);
    assert.match(app.records[0].flags.join('; '), /Replacement.*Used sail/);
    assert.equal(app.records[0].source.Notes, 'Purchased used; warranty replacement mentioned.');
});

test('date, type and sailmaker filters combine and handle undated records explicitly', () => {
    const app = dataAnalysis([
        sail('A', '2019-12-31'), sail('B', '2020-01-01'), sail('C', '2026-12-31'),
        sail('D', '2026-01-01', {'Sail Type': 'J'}), sail('E', '2026-01-01', {Sailmaker: 'Quantum'}),
        sail('F', '0000-00-00')
    ]);
    app.filters.sailType = 'M';
    app.filters.sailmaker = 'North';
    assert.deepEqual(app.filterRecords(app.records).map(record => record.certificate), ['B', 'C', 'F']);
    app.filters.includeUndated = false;
    assert.deepEqual(app.filterRecords(app.records).map(record => record.certificate), ['B', 'C']);
});

test('aggregation safely handles maker parentheses and counts records, not unique certificates', () => {
    const app = dataAnalysis([
        sail('A', '2026-01-01', {Sailmaker: 'Maker (Loft)'}),
        sail('A', '2026-02-01', {Sailmaker: 'Maker (Loft)'}),
        sail('B', '0000-00-00', {Sailmaker: 'Maker (Loft)'})
    ]);
    const cells = app.processDataForHeatmap(app.records);
    assert.equal(cells.length, 1);
    assert.equal(cells[0].sailmaker, 'Maker (Loft)');
    assert.equal(cells[0].count, 2);
    assert.equal(cells[0].year, 2026);
});

test('layout includes zero-record years and height depends only on unique rows', () => {
    const app = dataAnalysis([sail('A', '2020-01-01'), sail('B', '2026-01-01')]);
    const layout = app.getChartLayout(app.processDataForHeatmap(app.records));
    assert.deepEqual(layout.years, [2020, 2021, 2022, 2023, 2024, 2025, 2026]);
    assert.equal(layout.rows.length, 1);
    assert.equal(layout.height, 32);
});

test('recent year presets use calendar years and exclude unknown dates until opted in', () => {
    const app = dataAnalysis([sail('A', '2000-01-01')]);
    app.currentHull = '493';
    app.resetFilters();
    app.refreshFilters = () => {};
    const year = new Date().getFullYear();
    app.applyYearPreset('3');
    assert.equal(app.filters.startYear, year - 2);
    assert.equal(app.filters.endYear, year);
    assert.equal(app.filters.includeUndated, false);
    app.applyYearPreset('5');
    assert.equal(app.filters.startYear, year - 4);
    app.applyYearPreset('all');
    assert.equal(app.filters.startYear, 2000);
    assert.equal(app.filters.includeUndated, true);
});

test('cell drill-down and table search combine without changing chart records', () => {
    const app = dataAnalysis([
        sail('A', '2026-01-01', {Notes: 'Blue sail'}), sail('B', '2025-01-01'),
        sail('C', '2026-02-01', {'Sail Type': 'J'}), sail('D', '0000-00-00')
    ]);
    app.filteredRecords = app.filterRecords(app.records);
    app.selectedCell = {year: 2026, sailType: 'M', sailmaker: 'North'};
    assert.deepEqual(app.getTableRecords().map(record => record.certificate), ['A']);
    app.tableQuery = 'BLUE';
    assert.equal(app.getTableRecords().length, 1);
    app.tableQuery = 'not found';
    assert.equal(app.getTableRecords().length, 0);
    assert.equal(app.filteredRecords.length, 4);
    app.selectedCell = null;
    app.tableQuery = 'unknown delivery';
    assert.deepEqual(app.getTableRecords().map(record => record.certificate), ['D']);
});

test('changing filters clears the old cell scope but keeps table search', () => {
    const app = dataAnalysis([]);
    app.currentHull = '493';
    app.selectedCell = {year: 2026};
    app.tableQuery = 'North';
    app.tablePage = 2;
    app.updateVisualization = hull => assert.equal(hull, '493');
    app.refreshFilters();
    assert.equal(app.selectedCell, null);
    assert.equal(app.tablePage, 0);
    assert.equal(app.tableQuery, 'North');
});

test('opening a cell clears old table search and focuses the details heading', () => {
    const app = dataAnalysis([]);
    app.tableQuery = 'old query';
    app.tablePage = 4;
    let focused = false;
    app.elements = {tableSearch: {value: 'old query'}, detailsHeading: {
        focus: () => { focused = true; }, scrollIntoView: () => {}
    }};
    app.markSelectedCell = () => {};
    app.renderRecordTable = () => {};
    app.selectCell({key: 'row', year: 2026, sailType: 'M', sailmaker: 'North'});
    assert.equal(app.tableQuery, '');
    assert.equal(app.elements.tableSearch.value, '');
    assert.equal(app.tablePage, 0);
    assert.equal(focused, true);
});

test('record table paginates, clamps stale pages and renders source text safely', () => {
    const app = dataAnalysis(Array.from({length: 27}, (_, index) => sail(String(index), '2026-01-01', {
        Notes: index === 0 ? '<script>plain source text</script>' : ''
    })));
    app.filteredRecords = app.records;
    class Element {
        constructor() { this.children = []; }
        appendChild(child) { this.children.push(child); }
        replaceChildren() { this.children = []; }
        set innerHTML(_) { throw new Error('Source records must be rendered as text'); }
    }
    for (const id of ['recordDetails', 'detailsHeading', 'detailsSummary', 'clearCell',
                      'recordRows', 'tablePage', 'previousPage', 'nextPage']) app.elements[id] = new Element();
    const original = global.document;
    global.document = {createElement: () => new Element()};
    try {
        app.renderRecordTable();
        assert.equal(app.elements.recordRows.children.length, 25);
        assert.equal(app.elements.recordRows.children[0].children[5].textContent, '<script>plain source text</script>');
        assert.equal(app.elements.previousPage.disabled, true);
        assert.equal(app.elements.nextPage.disabled, false);
        app.tablePage = 1;
        app.renderRecordTable();
        assert.equal(app.elements.recordRows.children.length, 2);
        assert.equal(app.elements.nextPage.disabled, true);
        app.tableQuery = 'plain source text';
        app.renderRecordTable();
        assert.equal(app.tablePage, 0);
        assert.equal(app.elements.recordRows.children.length, 1);
        assert.equal(app.elements.tablePage.textContent, 'Page 1 of 1');
        app.tableQuery = 'no match';
        app.renderRecordTable();
        assert.equal(app.elements.recordRows.children[0].children[0].colSpan, 7);
        assert.match(app.elements.detailsSummary.textContent, /^0 records/);
    } finally {
        global.document = original;
    }
});

test('full source snapshot aggregation accounts for every dated record without NaN years', () => {
    const source = require('../data/sails/sail_tags.json');
    const app = dataAnalysis(source);
    const cells = app.processDataForHeatmap(app.records);
    assert.equal(cells.reduce((sum, cell) => sum + cell.count, 0),
        app.records.filter(record => record.year !== null).length);
    assert.ok(cells.every(cell => Number.isInteger(cell.year)));
    assert.equal(app.records.length, source.length);
});
