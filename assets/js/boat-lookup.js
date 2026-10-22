/** Shared current-owner lookup and accessible name suggestions for J/105 tools.
 * Hosts provide state/elements, config URLs, applyBoatDetails(), and selectBoatSuggestion().
 */
class BoatLookupController {
    /** Build hull lookups from owner records, never from historical sail purchases. */
    static buildBoatLookup(members, boats, year = new Date().getFullYear()) {
        const lookup = new Map();
        const grouped = new Map();
        const normalizeHull = value => String(value ?? '').trim().replace(/^0+(?=\d)/, '');
        const rank = record => {
            const match = /^(Member|Associate) (\d{4})$/.exec(record['Class Membership'] || '');
            const memberYear = match ? Number(match[2]) : 0;
            return [Number(match?.[1] === 'Member' && memberYear === year), memberYear,
                    Number(match?.[1] === 'Member')];
        };
        const compare = (a, b) => {
            const left = rank(a), right = rank(b);
            for (let i = 0; i < left.length; i++) {
                if (left[i] !== right[i]) return right[i] - left[i];
            }
            return 0;
        };
        for (const member of members) {
            const hull = normalizeHull(member.Hull);
            if (!/^\d+$/.test(hull) || hull === '0') continue;
            if (!grouped.has(hull)) grouped.set(hull, []);
            grouped.get(hull).push(member);
        }
        for (const [hull, records] of grouped) {
            const owners = records.filter(record => record.Status === 'OW').sort(compare);
            const primary = owners[0] || [...records].sort(compare)[0];
            // Equally recent owner records may be co-owners; keep their names together.
            const currentOwners = owners.filter(record => compare(record, owners[0]) === 0);
            const names = [...new Set(currentOwners.map(record => record['Owners/Helmsmen']?.trim()).filter(Boolean))].sort();
            lookup.set(hull, {boatName: primary['Boat Name'] || '', owner: names.join(' / ')});
        }
        for (const boat of boats) {
            const hull = normalizeHull(boat['Hull Number']);
            if (!/^\d+$/.test(hull) || hull === '0') continue;
            const details = lookup.get(hull) || {boatName: '', owner: ''};
            if (boat['Boat Name']) details.boatName = boat['Boat Name'];
            lookup.set(hull, details);
        }
        return lookup;
    }

    /** Load identity sources independently of sail availability. */
    async loadBoatData() {
        const fetchRecords = async url => {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const records = await response.json();
            if (!Array.isArray(records) || !records.every(record => record && typeof record === 'object')) {
                throw new Error('Invalid boat lookup data');
            }
            return records;
        };
        const [members, boats] = await Promise.allSettled([
            fetchRecords(this.config.membersUrl), fetchRecords(this.config.boatsUrl)
        ]);
        this.state.ownerLookupUnavailable = members.status !== 'fulfilled';
        this.state.boatLookup = BoatLookupController.buildBoatLookup(
            members.status === 'fulfilled' ? members.value : [],
            boats.status === 'fulfilled' ? boats.value : []
        );
        this.state.boatLookupLoaded = true;
        this.applyBoatDetails();
        if (typeof document !== 'undefined') {
            const field = ['owner', 'boatName'].find(id => document.activeElement === this.elements[id]);
            if (field) this.showIdentitySuggestions(field);
        }
    }

    /** Match names locally; typing never selects a boat or changes the hull. */
    findBoatSuggestions(field, query, limit = 8) {
        if (!['owner', 'boatName'].includes(field)) return [];
        const normalize = value => String(value || '').normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '').toLowerCase().trim().replace(/\s+/g, ' ');
        const search = normalize(query);
        if (search.length < 2) return [];
        return [...this.state.boatLookup].map(([hull, details]) => ({hull, ...details}))
            .filter(match => normalize(match[field]).includes(search))
            .sort((a, b) => Number(normalize(b[field]).startsWith(search)) - Number(normalize(a[field]).startsWith(search))
                || a[field].localeCompare(b[field]) || Number(a.hull) - Number(b.hull))
            .slice(0, limit);
    }

    showIdentitySuggestions(field) {
        const input = this.elements[field];
        const list = this.elements[`${field}Suggestions`];
        if (!input || !list) return;
        this.closeIdentitySuggestions();
        const matches = this.findBoatSuggestions(field, input.value);
        this.state.suggestions = {field, matches, activeIndex: -1};
        if (!matches.length) {
            if (this.elements.suggestionStatus && input.value.trim().length >= 2) {
                this.elements.suggestionStatus.textContent = this.state.boatLookupLoaded
                    ? 'No matching suggestions. You can keep your entry.' : 'Suggestions are loading. You can keep typing.';
            }
            return;
        }
        matches.forEach((match, index) => {
            const option = document.createElement('div');
            option.id = `${field}-suggestion-${index}`;
            option.className = 'identity-option';
            option.setAttribute('role', 'option');
            option.setAttribute('aria-selected', 'false');
            const name = document.createElement('strong');
            name.textContent = match[field];
            const context = document.createElement('small');
            context.textContent = `Hull ${match.hull} · ${field === 'owner' ? match.boatName || 'Boat name unavailable' : match.owner || 'Owner unavailable'}`;
            option.append(name, context);
            // Keep input focus so touch and mouse selections don't race its blur handler.
            option.addEventListener('pointerdown', event => event.preventDefault());
            option.addEventListener('click', () => this.selectBoatSuggestion(match));
            list.appendChild(option);
        });
        list.hidden = false;
        input.setAttribute('aria-expanded', 'true');
        if (this.elements.suggestionStatus) {
            this.elements.suggestionStatus.textContent = `${matches.length} suggestions. Use the up and down arrow keys and Enter to select, or keep typing your own details.`;
        }
    }

    closeIdentitySuggestions() {
        for (const field of ['owner', 'boatName']) {
            const input = this.elements[field];
            input?.setAttribute?.('aria-expanded', 'false');
            input?.removeAttribute?.('aria-activedescendant');
            const list = this.elements[`${field}Suggestions`];
            if (list) {
                list.hidden = true;
                list.replaceChildren();
            }
        }
        if (this.elements.suggestionStatus) this.elements.suggestionStatus.textContent = '';
        this.state.suggestions = {field: null, matches: [], activeIndex: -1};
    }

    handleSuggestionKeydown(event, field) {
        if (event.key === 'Escape' || event.key === 'Tab') {
            this.closeIdentitySuggestions();
            return;
        }
        if (event.key === 'Enter') {
            // Enter keeps a manual entry unless an option was explicitly highlighted.
            event.preventDefault();
            const {matches, activeIndex, field: activeField} = this.state.suggestions;
            if (activeField === field && activeIndex >= 0) this.selectBoatSuggestion(matches[activeIndex]);
            else this.closeIdentitySuggestions();
            return;
        }
        if (!['ArrowDown', 'ArrowUp'].includes(event.key)) return;
        if (this.state.suggestions.field !== field || !this.state.suggestions.matches.length) {
            this.showIdentitySuggestions(field);
        }
        const suggestions = this.state.suggestions;
        if (!suggestions.matches.length) return;
        event.preventDefault();
        const count = suggestions.matches.length;
        suggestions.activeIndex = event.key === 'ArrowDown'
            ? (suggestions.activeIndex + 1) % count
            : (suggestions.activeIndex < 0 ? count - 1 : (suggestions.activeIndex - 1 + count) % count);
        const list = this.elements[`${field}Suggestions`];
        [...list.children].forEach((option, index) => {
            option.setAttribute('aria-selected', String(index === suggestions.activeIndex));
        });
        const active = list.children[suggestions.activeIndex];
        this.elements[field].setAttribute('aria-activedescendant', active.id);
        active.scrollIntoView({block: 'nearest'});
    }

}

if (typeof module !== 'undefined' && module.exports) module.exports = BoatLookupController;
if (typeof window !== 'undefined') window.FleetBoatLookup = BoatLookupController;
