const {test} = require('node:test');
const assert = require('node:assert/strict');
const {SailDeclarationManager} = require('../tools/documents/sail_declaration.js');

const owner = (name, status = 'Member 2026', role = 'OW') => ({
    Hull: '493', 'Boat Name': 'Rapscallion', 'Owners/Helmsmen': name,
    Status: role, 'Class Membership': status
});

function manager() {
    const form = new SailDeclarationManager();
    for (const id of ['hullNumber', 'owner', 'boatName', 'email', 'mobile',
                      'spinnaker1Color', 'spinnaker2Color']) form.elements[id] = {value: ''};
    form.elements.boatLookupStatus = {textContent: ''};
    form.elements.useRegistryDetails = {disabled: true};
    form.elements.hullNumber.value = '493';
    form.state.boatLookupLoaded = true;
    form.state.boatLookup = SailDeclarationManager.buildBoatLookup([owner('Current owner')], [], 2026);
    return form;
}

test('current owner beats old purchaser/owner and current crew in either row order', () => {
    const rows = [owner('Old owner', 'Member 2010'), owner('Crew', 'Member 2026', 'CO'), owner('Current owner')];
    for (const records of [rows, [...rows].reverse()]) {
        assert.equal(SailDeclarationManager.buildBoatLookup(records, [], 2026).get('493').owner, 'Current owner');
    }
});

test('equally current co-owners are included once; fleet boat name takes precedence', () => {
    const lookup = SailDeclarationManager.buildBoatLookup([owner('Ann'), owner('Gary'), owner('Ann')],
        [{'Hull Number': '493', 'Boat Name': 'Local boat name'}], 2026);
    assert.deepEqual(lookup.get('493'), {owner: 'Ann / Gary', boatName: 'Local boat name'});
});

test('crew and historical sail buyers are never substituted for missing owner records', () => {
    const lookup = SailDeclarationManager.buildBoatLookup([owner('Crew', 'Member 2026', 'CO')], [], 2026);
    assert.equal(lookup.get('493').owner, '');
});

test('lookup fills boat name and owner, normalizing leading zeros', () => {
    const form = manager();
    form.elements.hullNumber.value = ' 0493 ';
    form.applyBoatDetails();
    assert.equal(form.elements.owner.value, 'Current owner');
    assert.equal(form.elements.boatName.value, 'Rapscallion');
    assert.equal(form.elements.useRegistryDetails.disabled, false);
});

test('late lookup preserves manual edits and only fills untouched fields', () => {
    const form = manager();
    form.elements.owner.value = 'Charterer';
    form.state.identityOverrides.add('owner');
    form.applyBoatDetails();
    assert.equal(form.elements.owner.value, 'Charterer');
    assert.equal(form.elements.boatName.value, 'Rapscallion');
    form.state.identityOverrides.clear();
    form.applyBoatDetails();
    assert.equal(form.elements.owner.value, 'Current owner');
});

test('saved overrides, including intentionally blank boat names, survive another lookup', () => {
    const form = manager();
    form.applyBoatDetails();
    form.restoreFormData({owner: 'Manual owner', boatName: ''});
    form.applyBoatDetails();
    assert.equal(form.elements.owner.value, 'Manual owner');
    assert.equal(form.elements.boatName.value, '');
    assert.match(form.elements.boatLookupStatus.textContent, /Manual details/);
});

test('unknown hull clears previous identity and leaves manual entry available', () => {
    const form = manager();
    form.applyBoatDetails();
    form.elements.hullNumber.value = '999999';
    form.applyBoatDetails();
    assert.equal(form.elements.owner.value, '');
    assert.equal(form.elements.boatName.value, '');
    assert.equal(form.elements.useRegistryDetails.disabled, true);
    assert.match(form.elements.boatLookupStatus.textContent, /Enter the details manually/);
});

test('a matched boat with no sails still receives its identity', () => {
    const form = manager();
    form.initializeSailDropdowns = () => {};
    form.handleHullNumberChange();
    assert.equal(form.elements.owner.value, 'Current owner');
    assert.equal(form.elements.boatName.value, 'Rapscallion');
});

test('changing hull clears overrides and contact/color details from the previous boat', () => {
    const form = manager();
    form.initializeSailDropdowns = () => {};
    form.handleHullNumberChange();
    form.elements.email.value = 'old@example.com';
    form.elements.spinnaker1Color.value = 'Red';
    form.elements.owner.value = 'Override';
    form.state.identityOverrides.add('owner');
    form.elements.hullNumber.value = '999999';
    form.handleHullNumberChange();
    assert.equal(form.elements.owner.value, '');
    assert.equal(form.elements.email.value, '');
    assert.equal(form.elements.spinnaker1Color.value, '');
    assert.equal(form.state.identityOverrides.size, 0);
});

test('registry failure does not block manual identity fields or available fleet boat names', async () => {
    const form = manager();
    const original = global.fetch;
    global.fetch = async url => url.includes('members') ? {ok: false, status: 503} : {
        ok: true, json: async () => [{'Hull Number': '493', 'Boat Name': 'Fleet boat'}]
    };
    try {
        await form.loadBoatData();
        assert.equal(form.elements.boatName.value, 'Fleet boat');
        assert.equal(form.elements.owner.value, '');
        assert.match(form.elements.boatLookupStatus.textContent, /unavailable/);
    } finally {
        global.fetch = original;
    }
});

test('print output preserves override text without interpreting HTML', () => {
    const form = manager();
    const html = form.generatePrintContent({hullNumber: '493', owner: 'A & B', boatName: '<New name>'}, {});
    assert.match(html, /A &amp; B/);
    assert.match(html, /&lt;New name&gt;/);
    assert.ok(!html.includes('<New name>'));
});

test('boat and owner suggestions match partial names regardless of case and accents', () => {
    const form = manager();
    form.state.boatLookup.set('72', {boatName: 'Highlander', owner: 'José Butcher'});
    assert.equal(form.findBoatSuggestions('boatName', 'RAPS')[0].hull, '493');
    assert.equal(form.findBoatSuggestions('owner', '  JOSE ')[0].hull, '72');
    assert.equal(form.findBoatSuggestions('owner', 'Butch')[0].hull, '72');
    assert.deepEqual(form.findBoatSuggestions('boatName', 'R'), []);
});

test('ambiguous suggestions keep separate hulls and prefer prefix matches', () => {
    const form = manager();
    form.state.boatLookup = new Map([
        ['72', {boatName: 'Magic', owner: 'Owner A'}],
        ['493', {boatName: 'Blue Magic', owner: 'Owner B'}],
        ['194', {boatName: 'Magic', owner: 'Owner C'}]
    ]);
    assert.deepEqual(form.findBoatSuggestions('boatName', 'magic').map(match => match.hull), ['72', '194', '493']);
    assert.equal(form.findBoatSuggestions('boatName', 'magic', 2).length, 2);
});

test('typing an exact suggestion never changes the hull until a suggestion is selected', () => {
    const form = manager();
    form.elements.boatName.value = 'Rapscallion';
    form.elements.hullNumber.value = '';
    form.findBoatSuggestions('boatName', 'Rapscallion');
    assert.equal(form.elements.hullNumber.value, '');
    assert.equal(form.elements.boatName.value, 'Rapscallion');
});

test('selecting a suggestion fills the hull and related fields and clears stale boat details', () => {
    const form = manager();
    form.initializeSailDropdowns = () => {};
    form.state.activeHull = '72';
    form.elements.hullNumber.value = '72';
    form.elements.email.value = 'old@example.com';
    form.state.identityOverrides.add('boatName');
    form.selectBoatSuggestion(form.findBoatSuggestions('boatName', 'rap')[0]);
    assert.equal(form.elements.hullNumber.value, '493');
    assert.equal(form.elements.boatName.value, 'Rapscallion');
    assert.equal(form.elements.owner.value, 'Current owner');
    assert.equal(form.elements.email.value, '');
    assert.equal(form.state.identityOverrides.size, 0);
    assert.equal(form.state.isDirty, true);
});

test('choosing a suggestion for the same hull preserves contact information', () => {
    const form = manager();
    form.initializeSailDropdowns = () => {};
    form.state.activeHull = '493';
    form.elements.email.value = 'current@example.com';
    form.selectBoatSuggestion(form.findBoatSuggestions('owner', 'current')[0]);
    assert.equal(form.elements.email.value, 'current@example.com');
});

test('Enter without a highlighted suggestion keeps manual text and does not submit', () => {
    const form = manager();
    form.elements.owner.value = 'Manual owner';
    form.state.suggestions = {field: 'owner', matches: form.findBoatSuggestions('owner', 'current'), activeIndex: -1};
    let prevented = false;
    form.handleSuggestionKeydown({key: 'Enter', preventDefault: () => { prevented = true; }}, 'owner');
    assert.equal(form.elements.owner.value, 'Manual owner');
    assert.equal(form.elements.hullNumber.value, '493');
    assert.equal(prevented, true);
});

test('Enter selects a highlighted suggestion and Escape preserves manual input', () => {
    const form = manager();
    form.initializeSailDropdowns = () => {};
    form.state.suggestions = {field: 'owner', matches: form.findBoatSuggestions('owner', 'current'), activeIndex: 0};
    form.handleSuggestionKeydown({key: 'Enter', preventDefault() {}}, 'owner');
    assert.equal(form.elements.owner.value, 'Current owner');
    form.elements.owner.value = 'Charterer';
    form.handleSuggestionKeydown({key: 'Escape'}, 'owner');
    assert.equal(form.elements.owner.value, 'Charterer');
    assert.equal(form.state.suggestions.field, null);
});
