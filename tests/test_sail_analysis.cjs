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
