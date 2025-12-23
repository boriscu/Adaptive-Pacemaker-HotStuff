const EventLog = {
    maxEvents: 100,
    
    init() {
        this.container = document.getElementById('event-log');
    },
    
    addEvent(event) {
        const entry = this.createEntry(event);
        this.container.appendChild(entry);
        
        while (this.container.children.length > this.maxEvents) {
            this.container.removeChild(this.container.firstChild);
        }
        
        this.container.scrollTop = this.container.scrollHeight;
    },
    
    createEntry(event) {
        const entry = document.createElement('div');
        entry.className = 'event-entry';
        
        const time = event.timestamp || 0;
        const type = event.type || 'UNKNOWN';
        const details = this.formatDetails(event);
        
        const typeClass = this.getTypeClass(type);
        
        entry.innerHTML = `
            <span class="event-time">${time}ms</span>
            <span class="event-type ${typeClass}">${type}</span>
            <span class="event-details">${details}</span>
        `;
        
        return entry;
    },
    
    formatDetails(event) {
        switch (event.type) {
            case 'MESSAGE_RECEIVE':
                return `R${event.sender_id} → R${event.recipient_id}: ${event.message_type}`;
            case 'VOTE_SEND':
                return `R${event.replica_id} voted ${event.vote_type}`;
            case 'QC_FORMATION':
                return `R${event.replica_id} formed ${event.qc_type} QC`;
            case 'COMMIT':
                return `R${event.replica_id} committed block at height ${event.height}`;
            case 'TIMEOUT':
                return `R${event.replica_id} timeout in view ${event.view}`;
            case 'VIEW_CHANGE':
                return `R${event.replica_id} → view ${event.new_view}`;
            case 'PROPOSAL':
                return `R${event.replica_id} proposed block in view ${event.view}`;
            case 'LOCK_UPDATE':
                return `R${event.replica_id} locked at view ${event.locked_view}`;
            case 'BYZANTINE_ACTION':
                return `⚠ R${event.replica_id} [FAULTY]: ${event.action}`;
            default:
                return JSON.stringify(event);
        }
    },
    
    getTypeClass(type) {
        const typeMap = {
            'MESSAGE_RECEIVE': 'message-receive',
            'VOTE_SEND': 'vote-send',
            'QC_FORMATION': 'qc-formation',
            'COMMIT': 'commit',
            'TIMEOUT': 'timeout',
            'VIEW_CHANGE': 'view-change',
            'PROPOSAL': 'proposal',
            'BYZANTINE_ACTION': 'byzantine-action'
        };
        return typeMap[type] || '';
    },
    
    clear() {
        this.container.innerHTML = '';
    }
};
