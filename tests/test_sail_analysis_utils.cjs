const {test} = require('node:test');
const assert = require('node:assert/strict');
const utils = require('../analysis/sail-analysis-utils.js');
const SailAnalysisHeatmap = require('../analysis/sail-analysis.js');

const sail = (certificate, date, extra = {}) => ({Hull: '493', 'Certificate No.': certificate,
    'Delivery Date': date, 'Sail Type': 'M', Sailmaker: 'North', Purchaser: 'Historical purchaser', Notes: '', ...extra});
const prepare = records => SailAnalysisHeatmap.prepareRecords(records);

test('analysis links round-trip hull, filters, search and cell without encoding name edits', () => {
    const view = {hull: '493', startYear: 2024, endYear: 2026, sailType: 'M',
        sailmaker: 'Maker & Loft (East)', includeUndated: false, query: '"special" & José',
        cell: {year: 2026, sailType: 'M', sailmaker: 'Maker & Loft (East)'}};
    const link = utils.viewUrl('https://fleet22.us/analysis/sail_analysis_heatmap.html?old=1#old', view);
    const restored = utils.parseView(link, 2026);
    assert.deepEqual({...restored, cell: {...restored.cell, key: undefined}},
        {...view, cell: {...view.cell, key: undefined}});
    assert.equal(new URL(link).hash, '');
    assert.equal(new URL(link).searchParams.has('old'), false);
});

test('malformed links cannot create invalid hulls or unbounded chart year ranges', () => {
    const view = utils.parseView('/?hull=javascript:alert(1)&from=1900&to=9999&cellYear=NaN&cellType=M&cellMaker=North', 2026);
    assert.equal(view.hull, null);
    assert.equal(view.startYear, null);
    assert.equal(view.endYear, null);
    assert.equal(view.cell, null);
    assert.equal(utils.normalizeHull(' 00493 '), '493');
    assert.equal(utils.normalizeHull('1234567'), null);
    assert.equal(utils.normalizeHull('-1'), null);
});

test('links normalize reversed endpoints, limit query length and ignore removed features', () => {
    const view = utils.parseView('/?hull=493&from=2026&to=2020&compare=72&table=72&q=' + 'x'.repeat(1000), 2026);
    assert.equal(view.startYear, 2020);
    assert.equal(view.endYear, 2026);
    assert.equal(view.query.length, 200);
    const url = new URL(utils.viewUrl('https://fleet22.us/analysis/sail_analysis_heatmap.html', view));
    assert.equal(url.searchParams.has('compare'), false);
    assert.equal(url.searchParams.has('table'), false);
    assert.equal(view.includeUndated, true);
});

test('cleared selection produces a clean analysis URL', () => {
    assert.equal(utils.viewUrl('https://fleet22.us/analysis/sail_analysis_heatmap.html?hull=493&q=North#old', {hull: null}),
        'https://fleet22.us/analysis/sail_analysis_heatmap.html');
});

test('latest delivery summaries ignore undated records and retain all ties', () => {
    const records = prepare([sail('OLD', '2020-01-01'), sail('A', '2026-03-01'),
        sail('B', '2026-03-01', {Sailmaker: 'Quantum'}), sail('UNDATED', '0000-00-00'),
        sail('JIB', '0000-00-00', {'Sail Type': 'J'})]);
    const latest = utils.latestDeliveries(records);
    assert.equal(latest.find(item => item.sailType === 'J').date, null);
    const main = latest.find(item => item.sailType === 'M');
    assert.equal(main.date, '2026-03-01');
    assert.deepEqual(main.records.map(record => record.certificate), ['A', 'B']);
    assert.equal(records.length, 5);
});

test('CSV retains certificates, historical purchaser, notes and repeated/unknown flags', () => {
    const records = prepare([sail('A', '0000-00-00', {Notes: 'Line one,\n"Line two"'}), sail('A', '2026-01-01')]);
    const csv = utils.recordsCsv(records, new Map([['493', {boatName: 'A & B', owner: 'Current owner'}]]));
    assert.ok(csv.startsWith('\uFEFF"Hull","Current boat name","Current owner"'));
    assert.ok(csv.includes('"493","A & B","Current owner","A","0000-00-00"'));
    assert.ok(csv.includes('"Line one,\n""Line two"""'));
    assert.ok(csv.includes('Historical purchaser'));
    assert.ok(csv.includes('Unknown delivery date; Certificate repeated on this hull'));
    assert.ok(csv.endsWith('\r\n'));
});

test('CSV neutralizes formula prefixes in all source and identity fields', () => {
    for (const value of ['=SUM(1,2)', '+FORMULA', '-FORMULA', '@FORMULA', '  =FORMULA', '\tFORMULA', '\rFORMULA', '\nFORMULA']) {
        const record = prepare([sail(value, '2026-01-01', {Purchaser: value, Notes: value})]);
        const csv = utils.recordsCsv(record, new Map([['493', {boatName: value, owner: value}]]));
        const escaped = value.replace(/"/g, '""');
        assert.ok(csv.includes('"\'' + escaped + '"'), value);
        assert.ok(!csv.includes(',"' + escaped + '"'), value);
    }
});

test('CSV exports every matching record, including records beyond the first table page', () => {
    const records = prepare(Array.from({length: 27}, (_, index) => sail(String(index), '2026-01-01')));
    const csv = utils.recordsCsv(records);
    assert.equal(csv.trimEnd().split('\r\n').length, 28);
    assert.ok(csv.includes('"26","2026-01-01"'));
});
