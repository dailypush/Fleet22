/**
 * Sail Analysis Heatmap JavaScript Module
 * Handles data processing and visualization for Fleet 22 sail analysis
 */

const AnalysisBoatLookup = typeof module !== 'undefined' && module.exports
    ? require('../assets/js/boat-lookup.js') : window.FleetBoatLookup;
const AnalysisUtils = typeof module !== 'undefined' && module.exports
    ? require('./sail-analysis-utils.js') : window.SailAnalysisUtils;

class SailAnalysisHeatmap extends AnalysisBoatLookup {
    constructor(containerId, dataPath, {autoInit = true} = {}) {
        super();
        this.containerId = containerId;
        this.dataPath = dataPath;
        this.sailData = [];
        this.dataLoaded = false;
        this.currentHull = null;
        this.restoringUrl = false;
        this.tooltip = null;
        this.records = [];
        this.filters = {startYear: null, endYear: null, sailType: '', sailmaker: '', includeUndated: true};
        this.selectedCell = null;
        this.tableQuery = '';
        this.tablePage = 0;
        this.pageSize = 25;
        this.config = {
            membersUrl: '../data/members/j105_members_status.json',
            boatsUrl: '../data/boats/boats_fleet22.json'
        };
        this.state = {
            boatLookup: new Map(), boatLookupLoaded: false, ownerLookupUnavailable: false,
            identityOverrides: new Set(), suggestions: {field: null, matches: [], activeIndex: -1}
        };
        this.elements = {};
        this.ready = autoInit ? this.init() : Promise.resolve();
    }

    async init() {
        for (const id of ['hullSelect', 'boatName', 'owner', 'ownerSuggestions',
                          'boatNameSuggestions', 'suggestionStatus', 'lookupStatus', 'selectedBoat',
                          'startYear', 'endYear', 'sailTypeFilter', 'sailmakerFilter', 'includeUndated',
                          'filterControls', 'filterStatus', 'tableSearch', 'recordDetails', 'detailsHeading',
                          'detailsSummary', 'recordRows', 'clearCell', 'previousPage', 'nextPage', 'tablePage',
                          'dataQuality', 'latestSection', 'latestDeliveries', 'copyLink', 'shareStatus',
                          'shareFallback', 'shareUrl', 'exportCsv', 'dataFreshness']) {
            this.elements[id] = document.getElementById(id);
        }
        this.elements.hullSelect.addEventListener('change', event => this.selectHull(event.target.value));
        for (const field of ['owner', 'boatName']) {
            const input = this.elements[field];
            input.addEventListener('input', () => {
                this.state.identityOverrides.add(field);
                this.showIdentitySuggestions(field);
            });
            input.addEventListener('focus', () => this.showIdentitySuggestions(field));
            input.addEventListener('blur', () => this.closeIdentitySuggestions());
            input.addEventListener('keydown', event => this.handleSuggestionKeydown(event, field));
        }
        this.setupFilters();
        this.setupActions();
        // Registry lookup is optional and does not block direct hull analysis.
        const registry = this.loadBoatData();
        const freshness = this.loadFreshness();
        try {
            await this.loadData();
            this.dataLoaded = true;
            this.setupTooltip();
            this.populateHullDropdown();
            this.hideLoading();
            if (this.currentHull) {
                this.resetFilters();
                this.updateVisualization(this.currentHull);
            } else this.restoreView(window.location.href);
        } catch (error) {
            this.showError('Error loading sail data: ' + error.message);
        }
        await Promise.all([registry, freshness]);
    }

    async loadData() {
        const response = await fetch(this.dataPath);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        if (!Array.isArray(data)) throw new Error('Expected a sail record list');
        this.sailData = data;
        this.indexRecords();
    }

    async loadBoatData() {
        await super.loadBoatData();
        this.populateHullDropdown();
    }

    showIdentitySuggestions(field) {
        super.showIdentitySuggestions(field);
        if (!this.elements.lookupStatus) return;
        const query = this.elements[field]?.value?.trim() || '';
        let message = 'Choose a hull, or type at least two characters of a boat or owner name.';
        if (!this.state.boatLookupLoaded) {
            message = 'Name suggestions are loading. You can still choose a hull directly.';
        } else if (field === 'owner' && this.state.ownerLookupUnavailable) {
            message = 'Owner lookup is unavailable. Choose a hull or search by boat name.';
        } else if (query.length >= 2) {
            message = this.state.suggestions.matches.length
                ? 'Choose a suggestion to update the analysis. Typing alone keeps the current selection.'
                : 'No matching suggestions. Try another name or choose a hull directly.';
        }
        this.elements.lookupStatus.textContent = message;
    }

    getHullNumber() {
        return this.currentHull || '';
    }

    populateHullDropdown() {
        const select = this.elements.hullSelect;
        if (!select) return;
        const hulls = new Set([...this.sailData.map(item => String(item.Hull)), ...this.state.boatLookup.keys()]);
        if (this.currentHull) hulls.add(this.currentHull);
        select.replaceChildren();
        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = 'Select a hull…';
        select.appendChild(placeholder);
        [...hulls].filter(hull => /^\d+$/.test(hull)).sort((a, b) => Number(a) - Number(b)).forEach(hull => {
            const option = document.createElement('option');
            option.value = hull;
            option.textContent = `Hull ${hull}`;
            select.appendChild(option);
        });
        select.value = this.currentHull || '';
    }

    selectBoatSuggestion(match) {
        if (match && this.state.boatLookup.has(match.hull)) this.selectHull(match.hull);
    }

    selectHull(value) {
        this.currentHull = AnalysisUtils.normalizeHull(value);
        this.selectedCell = null;
        this.tableQuery = '';
        this.tablePage = 0;
        if (this.elements.tableSearch) this.elements.tableSearch.value = '';
        this.resetFilters();
        this.state.identityOverrides.clear();
        this.closeIdentitySuggestions();
        this.populateHullDropdown();
        this.applyBoatDetails();
        if (!this.currentHull) this.clearVisualization();
        else if (this.dataLoaded) this.updateVisualization(this.currentHull);
        this.syncUrl();
    }

    applyBoatDetails() {
        const details = this.state.boatLookup.get(this.currentHull);
        for (const field of ['owner', 'boatName']) {
            if (this.elements[field] && !this.state.identityOverrides.has(field)) {
                this.elements[field].value = details?.[field] || '';
            }
        }
        if (this.elements.selectedBoat) {
            this.elements.selectedBoat.textContent = this.currentHull
                ? `Hull ${this.currentHull} · ${details?.boatName || 'Boat name unavailable'} · Owner: ${details?.owner || 'Unavailable'}`
                : 'No boat selected.';
        }
        if (this.elements.lookupStatus) {
            this.elements.lookupStatus.textContent = this.currentHull
                ? 'Showing the selected hull. Choose another hull or name suggestion to switch boats.'
                : 'Choose a hull, or type at least two characters of a boat or owner name.';
            if (this.state.ownerLookupUnavailable) {
                this.elements.lookupStatus.textContent += ' Owner lookup is unavailable; hull analysis still works.';
            }
        }
    }

    setupActions() {
        this.elements.copyLink.addEventListener('click', () => this.copyAnalysisLink());
        this.elements.exportCsv.addEventListener('click', () => this.exportRecords());
        window.addEventListener('popstate', () => {
            if (this.dataLoaded) this.restoreView(window.location.href);
        });
    }

    updateActions() {
        if (this.elements.copyLink) this.elements.copyLink.disabled = !this.currentHull || !this.dataLoaded;
    }

    async loadFreshness() {
        if (!this.elements.dataFreshness) return;
        try {
            const response = await fetch('../data/metadata.json');
            if (!response.ok) throw new Error('Metadata unavailable');
            const metadata = await response.json();
            const date = typeof metadata.checked_at === 'string' ? new Date(metadata.checked_at) : new Date(NaN);
            if (!Number.isFinite(date.getTime()) || !metadata.files?.['sails/sail_tags.json']) throw new Error('Invalid metadata');
            this.elements.dataFreshness.textContent = `Data last checked: ${date.toLocaleString()}`;
        } catch {
            this.elements.dataFreshness.textContent = 'Data refresh date unavailable.';
        }
    }

    viewState() {
        return {hull: this.currentHull, ...this.filters, query: this.tableQuery, cell: this.selectedCell};
    }

    syncUrl() {
        if (typeof window === 'undefined' || !this.dataLoaded || this.restoringUrl) return;
        const url = AnalysisUtils.viewUrl(window.location.href, this.viewState());
        if (url !== window.location.href) {
            window.history.replaceState(null, '', url);
            if (this.elements.shareStatus) this.elements.shareStatus.textContent = '';
            if (this.elements.shareFallback) this.elements.shareFallback.hidden = true;
        }
        if (this.elements.shareUrl) this.elements.shareUrl.value = url;
        this.updateActions();
    }

    restoreView(url) {
        const view = AnalysisUtils.parseView(url);
        this.restoringUrl = true;
        try {
            this.selectHull(view.hull || '');
            if (!view.hull) return;
            if (view.startYear !== null) {
                this.filters.startYear = view.startYear;
                this.filters.endYear = view.endYear;
                const years = [...new Set([...this.availableYears, view.startYear, view.endYear])].sort((a, b) => a - b);
                for (const id of ['startYear', 'endYear']) this.setOptions(this.elements[id], years);
            }
            const records = this.getHullRecords();
            if (records.some(record => record.sailType === view.sailType)) this.filters.sailType = view.sailType;
            if (records.some(record => record.sailmaker === view.sailmaker)) this.filters.sailmaker = view.sailmaker;
            this.filters.includeUndated = view.includeUndated;
            this.syncFilterControls();
            this.tableQuery = view.query;
            if (this.elements.tableSearch) this.elements.tableSearch.value = this.tableQuery;
            const active = this.filterRecords(records);
            this.selectedCell = view.cell && active.some(record => record.year === view.cell.year &&
                record.sailType === view.cell.sailType && record.sailmaker === view.cell.sailmaker) ? view.cell : null;
            this.updateVisualization(this.currentHull);
        } finally {
            this.restoringUrl = false;
            this.syncUrl();
        }
    }

    async copyAnalysisLink() {
        this.syncUrl();
        const url = AnalysisUtils.viewUrl(window.location.href, this.viewState());
        try {
            await navigator.clipboard.writeText(url);
            this.elements.shareStatus.textContent = 'Analysis link copied. It includes the selected boat, filters and table search.';
            this.elements.shareFallback.hidden = true;
        } catch {
            this.elements.shareFallback.hidden = false;
            this.elements.shareUrl.value = url;
            this.elements.shareUrl.focus();
            this.elements.shareUrl.select();
            this.elements.shareStatus.textContent = 'Copy the selected analysis link below.';
        }
    }

    exportRecords() {
        const records = this.getTableRecords();
        if (!records.length) return;
        const url = URL.createObjectURL(new Blob([AnalysisUtils.recordsCsv(records, this.state.boatLookup)], {type: 'text/csv;charset=utf-8'}));
        const link = document.createElement('a');
        link.href = url;
        link.download = `hull-${this.currentHull}-sail-records.csv`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    renderLatestDeliveries(records) {
        if (!this.elements.latestSection) return;
        this.elements.latestSection.hidden = !records.length;
        this.elements.latestDeliveries.replaceChildren();
        for (const latest of AnalysisUtils.latestDeliveries(records)) {
            const card = document.createElement('div');
            card.className = 'latest-card';
            for (const [value, className] of [
                [latest.sailType, 'fw-bold'], [latest.date || 'No known delivery date', ''],
                [latest.records.map(record => `${record.sailmaker} · ${record.certificate || 'Certificate not recorded'}`).join('; '), 'small text-muted']
            ]) {
                if (!value) continue;
                const line = document.createElement('p');
                line.className = className;
                line.textContent = value;
                card.appendChild(line);
            }
            this.elements.latestDeliveries.appendChild(card);
        }
    }

    // Parse calendar dates without timezone conversion or Date's rollover of invalid days.
    static deliveryYear(value) {
        const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value || '').trim());
        if (!match) return null;
        const [, year, month, day] = match.map(Number);
        if (year < 1900 || month < 1 || month > 12 || day < 1) return null;
        const date = new Date(Date.UTC(year, month - 1, day));
        return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day
            ? year : null;
    }

    static prepareRecords(source) {
        const certificates = new Map();
        source.forEach(record => {
            const certificate = String(record['Certificate No.'] || '').trim();
            if (!certificate) return;
            if (!certificates.has(certificate)) certificates.set(certificate, []);
            certificates.get(certificate).push(String(record.Hull));
        });
        return source.map(record => {
            const certificate = String(record['Certificate No.'] || '').trim();
            const occurrences = certificates.get(certificate) || [];
            const hull = String(record.Hull).trim().replace(/^0+(?=\d)/, '');
            const otherHulls = [...new Set(occurrences.filter(value => value !== String(record.Hull)))];
            const flags = [];
            const year = SailAnalysisHeatmap.deliveryYear(record['Delivery Date']);
            if (year === null) flags.push('Unknown delivery date');
            if (occurrences.length > 1) {
                flags.push(otherHulls.length
                    ? `Certificate also recorded on hull ${otherHulls.join(', ')}`
                    : 'Certificate repeated on this hull');
            }
            const notes = String(record.Notes || '');
            if (/\b(replacement|replaced|defective|destroyed)\b/i.test(notes)) flags.push('Replacement or damage mentioned in notes');
            if (/\b(used|sold|donated|transfer|transferred)\b/i.test(notes)) flags.push('Used sail or transfer mentioned in notes');
            return {
                source: record, hull, certificate, year, flags,
                repeatedCertificate: occurrences.length > 1,
                sailType: String(record['Sail Type'] || '').trim() || 'Unknown type',
                sailmaker: String(record.Sailmaker || '').trim() || 'Unknown sailmaker'
            };
        });
    }

    indexRecords() {
        if (this.indexedSource === this.sailData) return;
        this.records = SailAnalysisHeatmap.prepareRecords(this.sailData);
        this.indexedSource = this.sailData;
    }

    setupFilters() {
        for (const [id, key] of [['startYear', 'startYear'], ['endYear', 'endYear'],
                               ['sailTypeFilter', 'sailType'], ['sailmakerFilter', 'sailmaker']]) {
            this.elements[id].addEventListener('change', event => {
                this.filters[key] = key.endsWith('Year') ? Number(event.target.value) : event.target.value;
                // Moving either endpoint keeps the interval valid.
                if (this.filters.startYear > this.filters.endYear) {
                    const other = key === 'startYear' ? 'endYear' : 'startYear';
                    this.filters[other] = this.filters[key];
                    this.elements[other].value = String(this.filters[key]);
                }
                this.refreshFilters();
            });
        }
        this.elements.includeUndated.addEventListener('change', event => {
            this.filters.includeUndated = event.target.checked;
            this.refreshFilters();
        });
        document.querySelectorAll('[data-year-preset]').forEach(button => {
            button.addEventListener('click', () => this.applyYearPreset(button.dataset.yearPreset));
        });
        this.elements.tableSearch.addEventListener('input', event => {
            this.tableQuery = event.target.value.trim();
            this.tablePage = 0;
            this.renderRecordTable();
        });
        this.elements.clearCell.addEventListener('click', () => {
            this.selectedCell = null;
            this.tablePage = 0;
            this.markSelectedCell();
            this.renderRecordTable();
        });
        for (const [id, direction] of [['previousPage', -1], ['nextPage', 1]]) {
            this.elements[id].addEventListener('click', () => {
                this.tablePage += direction;
                this.renderRecordTable();
            });
        }
    }

    setOptions(element, values, placeholder) {
        if (!element) return;
        element.replaceChildren();
        for (const value of [...(placeholder ? [''] : []), ...values]) {
            const option = document.createElement('option');
            option.value = String(value);
            option.textContent = value === '' ? placeholder : String(value);
            element.appendChild(option);
        }
    }

    getHullRecords(hull = this.currentHull) {
        this.indexRecords();
        return this.records.filter(record => record.hull === hull);
    }

    resetFilters() {
        const records = this.getHullRecords();
        const years = records.map(record => record.year).filter(year => year !== null);
        const currentYear = new Date().getFullYear();
        const minYear = years.length ? Math.min(...years) : currentYear;
        const maxYear = years.length ? Math.max(...years, currentYear) : currentYear;
        this.availableYears = Array.from({length: maxYear - minYear + 1}, (_, index) => minYear + index);
        this.filters = {startYear: minYear, endYear: maxYear, sailType: '', sailmaker: '', includeUndated: true};
        for (const id of ['startYear', 'endYear']) this.setOptions(this.elements[id], this.availableYears);
        this.setOptions(this.elements.sailTypeFilter, [...new Set(records.map(record => record.sailType))].sort(), 'All sail types');
        this.setOptions(this.elements.sailmakerFilter, [...new Set(records.map(record => record.sailmaker))].sort(), 'All sailmakers');
        this.syncFilterControls();
        if (this.elements.filterControls) this.elements.filterControls.disabled = !this.currentHull || !records.length;
    }

    syncFilterControls() {
        for (const [id, key] of [['startYear', 'startYear'], ['endYear', 'endYear'],
                               ['sailTypeFilter', 'sailType'], ['sailmakerFilter', 'sailmaker']]) {
            if (this.elements[id]) this.elements[id].value = String(this.filters[key]);
        }
        if (this.elements.includeUndated) this.elements.includeUndated.checked = this.filters.includeUndated;
    }

    applyYearPreset(preset) {
        const currentYear = new Date().getFullYear();
        const all = preset === 'all';
        this.filters.startYear = all ? this.availableYears[0] : currentYear - Number(preset) + 1;
        this.filters.endYear = all ? this.availableYears.at(-1) : currentYear;
        // Recent presets exclude undated records; the checkbox can include them again.
        this.filters.includeUndated = all;
        const years = [...new Set([...this.availableYears, this.filters.startYear, this.filters.endYear])].sort((a, b) => a - b);
        for (const id of ['startYear', 'endYear']) this.setOptions(this.elements[id], years);
        this.syncFilterControls();
        this.refreshFilters();
    }

    filterRecords(records) {
        return records.filter(record =>
            (!this.filters.sailType || record.sailType === this.filters.sailType) &&
            (!this.filters.sailmaker || record.sailmaker === this.filters.sailmaker) &&
            (record.year === null ? this.filters.includeUndated :
                record.year >= this.filters.startYear && record.year <= this.filters.endYear));
    }

    refreshFilters() {
        this.selectedCell = null;
        this.tablePage = 0;
        if (this.currentHull) this.updateVisualization(this.currentHull);
    }

    setupTooltip() {
        this.tooltip = d3.select('body').append('div').attr('class', 'tooltip').style('opacity', 0);
    }

    updateVisualization(hull) {
        const hullRecords = this.getHullRecords(hull);
        this.renderLatestDeliveries(hullRecords);
        this.updateActions();
        if (hullRecords.length === 0) {
            this.clearVisualization();
            document.getElementById('hullStats').textContent = 'No sail records for this hull.';
            this.showNoData('No sail records available for the selected hull.');
            return;
        }
        this.filteredRecords = this.filterRecords(hullRecords);
        this.hideNoData();
        this.updateStats(hull, hullRecords);
        const processedData = this.processDataForHeatmap(this.filteredRecords);
        this.createHeatmap(processedData, hull);
        if (!processedData.length) this.showNoData(this.filteredRecords.length
            ? 'Matching records have unknown delivery dates. See the records table below.'
            : 'No records match these filters. Adjust the filters or choose All history.');
        this.renderRecordTable();
        this.syncUrl();
    }

    processDataForHeatmap(records) {
        const summary = new Map();
        records.forEach(record => {
            if (record.year === null) return;
            const key = JSON.stringify([record.sailType, record.sailmaker]);
            const cellKey = JSON.stringify([key, record.year]);
            if (!summary.has(cellKey)) summary.set(cellKey, {
                key, year: record.year, count: 0, sailType: record.sailType, sailmaker: record.sailmaker
            });
            summary.get(cellKey).count++;
        });
        return [...summary.values()].sort((a, b) =>
            a.sailType.localeCompare(b.sailType) || a.sailmaker.localeCompare(b.sailmaker) || a.year - b.year);
    }

    getChartLayout(data) {
        const rows = [...new Set(data.map(cell => cell.key))];
        const start = this.filters.startYear;
        const end = this.filters.endYear;
        return {
            rows, height: rows.length * 32,
            years: Array.from({length: end - start + 1}, (_, index) => start + index)
        };
    }

    createHeatmap(data, hull) {
        const chart = d3.select(`#${this.containerId}`);
        chart.selectAll('*').remove();
        this.tooltip?.style('opacity', 0).style('left', '0px').style('top', '0px');
        document.querySelector('.legend').style.display = 'none';
        const heading = document.getElementById('heatmapHeading');
        heading.hidden = !data.length;
        heading.textContent = `Hull ${hull} · Recorded sail registrations`;
        if (data.length === 0) return;

        const {rows, years, height} = this.getChartLayout(data);
        const margin = {top: 15, right: 25, bottom: 75, left: 180};
        const containerWidth = Math.max(document.getElementById(this.containerId).offsetWidth, margin.left + margin.right + years.length * 36);
        const width = containerWidth - margin.left - margin.right;
        const svgRoot = chart.append('svg').attr('width', containerWidth)
            .attr('height', height + margin.top + margin.bottom)
            .attr('role', 'group').attr('aria-labelledby', 'chartTitle chartDescription');
        svgRoot.append('title').attr('id', 'chartTitle').text(`Hull ${hull}: recorded sail registrations`);
        svgRoot.append('desc').attr('id', 'chartDescription')
            .text('Counts of dated records by sail type, sailmaker and delivery year. Empty cells mean zero records. Activate a numbered cell to filter the records table below.');
        const svg = svgRoot.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
        const xScale = d3.scaleBand().domain(years).range([0, width]).padding(0.1);
        const yScale = d3.scaleBand().domain(rows).range([0, height]).padding(0.1);
        const maxCount = d3.max(data, cell => cell.count);
        const colorScale = d3.scaleSequential(d3.interpolateBlues).domain([0, maxCount]);
        const byCell = new Map(data.map(cell => [JSON.stringify([cell.key, cell.year]), cell]));
        const rowDetails = new Map(data.map(cell => [cell.key, cell]));
        const grid = rows.flatMap(key => years.map(year => byCell.get(JSON.stringify([key, year])) || {
            ...rowDetails.get(key), key, year, count: 0
        }));
        const cells = svg.selectAll('.cell').data(grid).enter().append('rect')
            .attr('class', cell => cell.count ? 'cell' : 'cell empty-cell')
            .attr('x', cell => xScale(cell.year)).attr('y', cell => yScale(cell.key))
            .attr('width', xScale.bandwidth()).attr('height', yScale.bandwidth())
            .attr('fill', cell => cell.count ? colorScale(cell.count) : '#f5f5f5');
        cells.filter(cell => cell.count > 0)
            .attr('tabindex', 0).attr('role', 'button')
            .attr('aria-label', cell => `${cell.year}, ${cell.sailType}, ${cell.sailmaker}: ${cell.count} recorded registrations. Show records.`)
            .on('click', (_, cell) => this.selectCell(cell))
            .on('keydown', (event, cell) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    this.selectCell(cell);
                }
            })
            .on('mouseover', (event, cell) => {
                if (window.matchMedia('(hover: none)').matches) return;
                this.tooltip.style('opacity', 1)
                    .text(`${cell.sailType} · ${cell.sailmaker} · ${cell.year}: ${cell.count} recorded registrations`);
                const bounds = this.tooltip.node().getBoundingClientRect();
                this.tooltip.style('left', `${Math.max(12, Math.min(event.clientX + 10, window.innerWidth - bounds.width - 12))}px`)
                    .style('top', `${Math.max(12, Math.min(event.clientY + 10, window.innerHeight - bounds.height - 12))}px`);
            })
            .on('mouseout', () => this.tooltip.style('opacity', 0))
            .on('blur', () => this.tooltip.style('opacity', 0));
        cells.append('title').text(cell => `${cell.sailType} (${cell.sailmaker}), ${cell.year}: ${cell.count} records`);
        svg.selectAll('.cell-text').data(data).enter().append('text')
            .attr('class', 'cell-text').attr('x', cell => xScale(cell.year) + xScale.bandwidth() / 2)
            .attr('y', cell => yScale(cell.key) + yScale.bandwidth() / 2)
            .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
            .attr('fill', cell => cell.count > maxCount * 0.6 ? 'white' : 'black').attr('font-size', '12px')
            .text(cell => cell.count);
        svg.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale)).selectAll('text').style('text-anchor', 'end')
            .attr('dx', '-.8em').attr('dy', '.15em').attr('transform', 'rotate(-45)');
        svg.append('g').attr('class', 'y-axis').call(d3.axisLeft(yScale)
            .tickFormat(key => { const cell = rowDetails.get(key); return `${cell.sailType} (${cell.sailmaker})`; }));
        svg.append('text').attr('x', width / 2).attr('y', height + 65)
            .attr('text-anchor', 'middle').attr('fill', '#666').text('Delivery year');
        const stops = Array.from({length: 11}, (_, index) => d3.interpolateBlues(index / 10));
        document.querySelector('.legend-gradient').style.background = `linear-gradient(to right, ${stops.join(', ')})`;
        document.getElementById('legendMax').textContent = String(maxCount);
        document.querySelector('.legend').style.display = 'flex';
        this.markSelectedCell();
    }

    selectCell(cell) {
        this.selectedCell = {key: cell.key, year: cell.year, sailType: cell.sailType, sailmaker: cell.sailmaker};
        this.tablePage = 0;
        // A cell opens its full record list even if a previous table search was entered.
        this.tableQuery = '';
        this.elements.tableSearch.value = '';
        this.tooltip?.style('opacity', 0);
        this.markSelectedCell();
        this.renderRecordTable();
        this.elements.detailsHeading.focus({preventScroll: true});
        this.elements.detailsHeading.scrollIntoView({block: 'nearest'});
    }

    markSelectedCell() {
        d3.select(`#${this.containerId}`).selectAll('.cell[role="button"]')
            .attr('aria-pressed', cell => String(Boolean(this.selectedCell && cell.key === this.selectedCell.key && cell.year === this.selectedCell.year)));
    }

    getTableRecords() {
        const query = this.tableQuery.toLocaleLowerCase();
        return (this.filteredRecords || []).filter(record => {
            if (this.selectedCell && (record.year !== this.selectedCell.year ||
                record.sailType !== this.selectedCell.sailType || record.sailmaker !== this.selectedCell.sailmaker)) return false;
            return !query || [record.certificate, record.source['Delivery Date'], record.sailType,
                record.sailmaker, record.source.Purchaser, record.source.Notes, ...record.flags]
                .some(value => String(value || '').toLocaleLowerCase().includes(query));
        }).sort((a, b) => (b.year ?? -1) - (a.year ?? -1) ||
            String(b.source['Delivery Date']).localeCompare(String(a.source['Delivery Date'])) || a.certificate.localeCompare(b.certificate));
    }

    renderRecordTable() {
        if (!this.elements.recordDetails) return;
        this.elements.recordDetails.hidden = false;
        const records = this.getTableRecords();
        const pages = Math.max(1, Math.ceil(records.length / this.pageSize));
        this.tablePage = Math.max(0, Math.min(this.tablePage, pages - 1));
        this.elements.detailsHeading.textContent = this.selectedCell
            ? `${this.selectedCell.year} · ${this.selectedCell.sailType} · ${this.selectedCell.sailmaker}` : 'Sail registration records';
        this.elements.clearCell.hidden = !this.selectedCell;
        this.elements.detailsSummary.textContent = `${records.length} record${records.length === 1 ? '' : 's'}${this.selectedCell ? ' in this chart cell' : ' matching the filters'}${this.tableQuery ? ' and table search' : ''}.`;
        this.elements.recordRows.replaceChildren();
        for (const record of records.slice(this.tablePage * this.pageSize, (this.tablePage + 1) * this.pageSize)) {
            const row = document.createElement('tr');
            for (const value of [record.certificate || 'Not recorded', record.year === null ? 'Unknown' : record.source['Delivery Date'],
                                record.sailType, record.sailmaker, record.source.Purchaser || 'Not recorded',
                                record.source.Notes || '—', record.flags.join('; ') || '—']) {
                const cell = document.createElement('td');
                cell.textContent = value;
                row.appendChild(cell);
            }
            this.elements.recordRows.appendChild(row);
        }
        if (!records.length) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 7;
            cell.textContent = 'No records match. Clear the table search or adjust the filters.';
            row.appendChild(cell);
            this.elements.recordRows.appendChild(row);
        }
        this.elements.tablePage.textContent = `Page ${this.tablePage + 1} of ${pages}`;
        this.elements.previousPage.disabled = this.tablePage === 0;
        this.elements.nextPage.disabled = this.tablePage >= pages - 1;
        if (this.elements.exportCsv) this.elements.exportCsv.disabled = !records.length;
        this.syncUrl();
    }

    updateStats(hull, hullRecords) {
        const filtered = this.filteredRecords;
        const undated = filtered.filter(record => record.year === null).length;
        const repeated = hullRecords.filter(record => record.repeatedCertificate).length;
        const allUndated = hullRecords.filter(record => record.year === null).length;
        document.getElementById('hullStats').textContent = `Recorded sail registrations: ${hullRecords.length}. ${filtered.length} match the filters; ${filtered.length - undated} dated records plotted; ${undated} undated records included in the table.`;
        if (this.elements.filterStatus) this.elements.filterStatus.textContent =
            `Delivery years ${this.filters.startYear}–${this.filters.endYear} · ${this.filters.sailType || 'All sail types'} · ${this.filters.sailmaker || 'All sailmakers'}. ${filtered.length} matching records.`;
        if (this.elements.dataQuality) this.elements.dataQuality.textContent = [
            `${allUndated} record${allUndated === 1 ? ' has an' : 's have an'} unknown delivery date.`,
            `${repeated} record${repeated === 1 ? ' has a' : 's have a'} repeated certificate number in the source dataset.`,
            'Repeated entries are retained and flagged; they can represent transfers or multiple entries on one hull. Notes flags are hints, not verified exemptions.'
        ].join(' ');
    }

    clearVisualization() {
        d3.select(`#${this.containerId}`).selectAll('*').remove();
        this.hideNoData();
        document.querySelector('.legend').style.display = 'none';
        document.getElementById('hullStats').textContent = 'Select a hull to see statistics';
        this.tooltip?.style('opacity', 0);
        this.filteredRecords = [];
        this.selectedCell = null;
        const heading = document.getElementById('heatmapHeading');
        if (heading) heading.hidden = true;
        if (this.elements.recordDetails) this.elements.recordDetails.hidden = true;
        if (this.elements.filterStatus) this.elements.filterStatus.textContent = '';
        if (this.elements.dataQuality) this.elements.dataQuality.textContent = '';
        if (this.elements.latestSection) this.elements.latestSection.hidden = true;
        this.updateActions();
    }

    showNoData(message) {
        const element = document.getElementById('noData');
        element.style.display = 'block';
        if (message) element.textContent = message;
        document.querySelector('.legend').style.display = 'none';
    }

    hideNoData() {
        document.getElementById('noData').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showError(message) {
        const error = document.createElement('p');
        error.className = 'text-danger';
        error.textContent = message;
        document.getElementById('loading').replaceChildren(error);
    }

    // Public method to handle window resize
    handleResize() {
        if (this.currentHull && this.dataLoaded) {
            this.updateVisualization(this.currentHull);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SailAnalysisHeatmap;
}
