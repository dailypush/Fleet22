/**
 * Sail Analysis Heatmap JavaScript Module
 * Handles data processing and visualization for Fleet 22 sail analysis
 */

const AnalysisBoatLookup = typeof module !== 'undefined' && module.exports
    ? require('../assets/js/boat-lookup.js') : window.FleetBoatLookup;

class SailAnalysisHeatmap extends AnalysisBoatLookup {
    constructor(containerId, dataPath, {autoInit = true} = {}) {
        super();
        this.containerId = containerId;
        this.dataPath = dataPath;
        this.sailData = [];
        this.dataLoaded = false;
        this.currentHull = null;
        this.tooltip = null;
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
                          'boatNameSuggestions', 'suggestionStatus', 'lookupStatus', 'selectedBoat']) {
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
        // Registry lookup is optional and does not block direct hull analysis.
        const registry = this.loadBoatData();
        try {
            await this.loadData();
            this.dataLoaded = true;
            this.setupTooltip();
            this.populateHullDropdown();
            this.hideLoading();
            if (this.currentHull) this.updateVisualization(this.currentHull);
        } catch (error) {
            this.showError('Error loading sail data: ' + error.message);
        }
        await registry;
    }

    async loadData() {
        const response = await fetch(this.dataPath);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        if (!Array.isArray(data)) throw new Error('Expected a sail record list');
        this.sailData = data;
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
        const hull = String(value || '').trim().replace(/^0+(?=\d)/, '');
        this.currentHull = /^\d+$/.test(hull) ? hull : null;
        this.state.identityOverrides.clear();
        this.closeIdentitySuggestions();
        this.populateHullDropdown();
        this.applyBoatDetails();
        if (!this.currentHull) this.clearVisualization();
        else if (this.dataLoaded) this.updateVisualization(this.currentHull);
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

    setupTooltip() {
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
    }

    updateVisualization(hull) {
        const hullData = this.sailData.filter(item => String(item.Hull) === hull);
        if (hullData.length === 0) {
            this.clearVisualization();
            document.getElementById('hullStats').textContent = 'No sail records for this hull.';
            this.showNoData();
            return;
        }
        this.hideNoData();
        this.updateStats(hull, hullData);
        const processedData = this.processDataForHeatmap(hullData);
        this.createHeatmap(processedData, hull);
    }

    processDataForHeatmap(hullData) {
        const summary = {};
        
        hullData.forEach(({ 'Sail Type': sailType, 'Sailmaker': sailmaker, 'Delivery Date': date }) => {
            if (!date) return;
            
            const year = new Date(date).getFullYear().toString();
            const key = `${sailType} (${sailmaker})`;

            if (!summary[key]) {
                summary[key] = {};
            }

            if (!summary[key][year]) {
                summary[key][year] = 0;
            }

            summary[key][year] += 1;
        });

        return Object.entries(summary).flatMap(([key, years]) => {
            return Object.entries(years).map(([year, count]) => ({
                key, 
                year: parseInt(year), 
                count,
                sailType: key.split(' (')[0],
                sailmaker: key.split(' (')[1].replace(')', '')
            }));
        });
    }

    createHeatmap(data, hull) {
        // Clear previous heatmap
        d3.select('#heatmap').selectAll('*').remove();

        if (data.length === 0) return;

        const containerWidth = document.getElementById('heatmap').offsetWidth;
        const margin = { top: 60, right: 50, bottom: 100, left: 200 };
        const width = containerWidth - margin.left - margin.right;
        const height = Math.max(400, data.length * 30) - margin.top - margin.bottom;

        const svg = d3.select('#heatmap')
            .append('svg')
            .attr('width', containerWidth)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Title
        svg.append('text')
            .attr('class', 'heatmap-title')
            .attr('x', width / 2)
            .attr('y', -30)
            .text(`Hull ${hull} - Sail Purchases by Type & Maker`);

        // Scales
        const years = [...new Set(data.map(d => d.year))].sort();
        const sailTypes = [...new Set(data.map(d => d.key))];

        const xScale = d3.scaleBand()
            .domain(years)
            .range([0, width])
            .padding(0.1);

        const yScale = d3.scaleBand()
            .domain(sailTypes)
            .range([0, height])
            .padding(0.1);

        const maxCount = d3.max(data, d => d.count);
        const colorScale = d3.scaleSequential(d3.interpolateBlues)
            .domain([0, maxCount]);

        // Create heatmap cells
        svg.selectAll('.cell')
            .data(data)
            .enter()
            .append('rect')
            .attr('class', 'cell')
            .attr('x', d => xScale(d.year))
            .attr('y', d => yScale(d.key))
            .attr('width', xScale.bandwidth())
            .attr('height', yScale.bandwidth())
            .attr('fill', d => colorScale(d.count))
            .on('mouseover', (event, d) => {
                this.tooltip
                    .style('opacity', 1)
                    .html(`
                        <strong>${d.sailType}</strong><br>
                        Sailmaker: ${d.sailmaker}<br>
                        Year: ${d.year}<br>
                        Purchases: ${d.count}
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', () => {
                this.tooltip.style('opacity', 0);
            });

        // Add text labels on cells if they're large enough
        svg.selectAll('.cell-text')
            .data(data.filter(d => xScale.bandwidth() > 30 && yScale.bandwidth() > 20))
            .enter()
            .append('text')
            .attr('class', 'cell-text')
            .attr('x', d => xScale(d.year) + xScale.bandwidth() / 2)
            .attr('y', d => yScale(d.key) + yScale.bandwidth() / 2)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('fill', d => d.count > maxCount * 0.6 ? 'white' : 'black')
            .attr('font-size', '12px')
            .text(d => d.count);

        // Axes
        const xAxis = d3.axisBottom(xScale);
        const yAxis = d3.axisLeft(yScale);

        svg.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${height})`)
            .call(xAxis)
            .selectAll('text')
            .style('text-anchor', 'end')
            .attr('dx', '-.8em')
            .attr('dy', '.15em')
            .attr('transform', 'rotate(-45)');

        svg.append('g')
            .attr('class', 'y-axis')
            .call(yAxis);

        // Axis labels
        svg.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('y', 0 - margin.left + 20)
            .attr('x', 0 - (height / 2))
            .style('text-anchor', 'middle')
            .style('font-size', '14px')
            .style('fill', '#666')
            .text('Sail Type (Sailmaker)');

        svg.append('text')
            .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 20})`)
            .style('text-anchor', 'middle')
            .style('font-size', '14px')
            .style('fill', '#666')
            .text('Year');

        // Show legend
        document.querySelector('.legend').style.display = 'flex';
    }

    updateStats(hull, hullData) {
        const statsDiv = document.getElementById('hullStats');
        const totalSails = hullData.length;
        const sailmakers = [...new Set(hullData.map(item => item.Sailmaker))];
        const sailTypes = [...new Set(hullData.map(item => item['Sail Type']))];
        const years = [...new Set(hullData.map(item => new Date(item['Delivery Date']).getFullYear()))];

        const title = document.createElement('strong');
        title.textContent = `Hull ${hull} Statistics:`;
        statsDiv.replaceChildren(title);
        for (const line of [`Total Sails: ${totalSails}`, `Sailmakers: ${sailmakers.join(', ')}`,
                            `Sail Types: ${sailTypes.join(', ')}`,
                            `Years: ${Math.min(...years)} - ${Math.max(...years)}`]) {
            statsDiv.append(document.createElement('br'), document.createTextNode(line));
        }
    }

    clearVisualization() {
        d3.select('#heatmap').selectAll('*').remove();
        this.hideNoData();
        document.querySelector('.legend').style.display = 'none';
        document.getElementById('hullStats').textContent = 'Select a hull to see statistics';
        this.tooltip?.style('opacity', 0);
    }

    showNoData() {
        document.getElementById('noData').style.display = 'block';
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