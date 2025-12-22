const ReplicaPanel = {
    init() {
        document.getElementById('replica-list').addEventListener('click', (e) => {
            const card = e.target.closest('.replica-card');
            if (card) {
                card.classList.toggle('expanded');
            }
        });
    },
    
    update(replicas) {
        const container = document.getElementById('replica-list');
        container.innerHTML = '';
        
        for (const replica of replicas) {
            const card = this.createCard(replica);
            container.appendChild(card);
        }
    },
    
    createCard(replica) {
        const card = document.createElement('div');
        card.className = 'replica-card';
        
        if (replica.is_leader) {
            card.classList.add('leader');
        }
        if (replica.is_faulty) {
            card.classList.add('faulty');
        }
        
        const roleText = replica.is_leader ? 'Leader' : 'Replica';
        const roleClass = replica.is_leader ? 'leader' : '';
        
        card.innerHTML = `
            <div class="replica-header">
                <span class="replica-id">Replica ${replica.replica_id}</span>
                <span class="replica-role ${roleClass}">${roleText}</span>
            </div>
            <div class="replica-details">
                <div>
                    <span>View:</span>
                    <span>${replica.current_view}</span>
                </div>
                <div>
                    <span>Phase:</span>
                    <span>${replica.current_phase}</span>
                </div>
                <div>
                    <span>Locked QC:</span>
                    <span>${replica.locked_qc ? `v${replica.locked_qc.view}` : 'None'}</span>
                </div>
                <div>
                    <span>Prepare QC:</span>
                    <span>${replica.prepare_qc ? `v${replica.prepare_qc.view}` : 'None'}</span>
                </div>
                <div>
                    <span>Commits:</span>
                    <span>${replica.committed_count}</span>
                </div>
                <div>
                    <span>Last Vote:</span>
                    <span>${replica.last_voted_view ?? 'None'}</span>
                </div>
                ${replica.is_faulty ? `
                <div>
                    <span>Fault:</span>
                    <span style="color: #dc3545">${replica.fault_type}</span>
                </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }
};
