/**
 * Sail Analysis Heatmap JavaScript Module
 * Handles data processing and visualization for Fleet 22 sail analysis
 */

class SailAnalysisHeatmap {
    constructor(containerId, dataPath) {
        this.containerId = containerId;
        this.dataPath = dataPath;
        this.sailData = [];
        this.currentHull = null;
        this.tooltip = null;
        this.init();
    }

    async init() {
        try {
            await this.loadData();
            this.setupTooltip();
            this.populateHullDropdown();
            this.hideLoading();
        } catch (error) {
            this.showError('Error loading data: ' + error.message);
        }
    }

    async loadData() {
        const response = await fetch(this.dataPath);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        this.sailData = await response.json();
    }

    setupTooltip() {
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
    }

    populateHullDropdown() {
        const hullSelect = document.getElementById('hullSelect');
        const hulls = [...new Set(this.sailData.map(item => item.Hull))]
            .sort((a, b) => parseInt(a) - parseInt(b));
        
        hullSelect.innerHTML = '<option value="">Select a hull...</option>';
        hulls.forEach(hull => {
            const option = document.createElement('option');
            option.value = hull;
            option.textContent = `Hull ${hull}`;
            hullSelect.appendChild(option);
        });

        hullSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                this.currentHull = e.target.value;
                this.updateVisualization(e.target.value);
            } else {
                this.clearVisualization();
            }
        });
    }

    updateVisualization(hull) {
        const hullData = this.sailData.filter(item => item.Hull === hull);
        
        if (hullData.length === 0) {
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

        statsDiv.innerHTML = `
            <strong>Hull ${hull} Statistics:</strong><br>
            Total Sails: ${totalSails}<br>
            Sailmakers: ${sailmakers.join(', ')}<br>
            Sail Types: ${sailTypes.join(', ')}<br>
            Years: ${Math.min(...years)} - ${Math.max(...years)}
        `;
    }

    clearVisualization() {
        d3.select('#heatmap').selectAll('*').remove();
        this.hideNoData();
        document.querySelector('.legend').style.display = 'none';
        document.getElementById('hullStats').innerHTML = 'Select a hull to see statistics';
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
        document.getElementById('loading').innerHTML = `<p class="text-danger">${message}</p>`;
    }

    // Public method to handle window resize
    handleResize() {
        if (this.currentHull) {
            this.updateVisualization(this.currentHull);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SailAnalysisHeatmap;
}