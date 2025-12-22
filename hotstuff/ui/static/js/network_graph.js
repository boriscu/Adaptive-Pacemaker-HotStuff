const NetworkGraph = {
    cy: null,
    
    init() {
        this.cy = cytoscape({
            container: document.getElementById('network-graph'),
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#4a90d9',
                        'label': 'data(label)',
                        'color': '#fff',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '14px',
                        'font-weight': 'bold',
                        'width': 50,
                        'height': 50,
                        'border-width': 3,
                        'border-color': '#2a70b9'
                    }
                },
                {
                    selector: 'node.leader',
                    style: {
                        'background-color': '#ffd700',
                        'border-color': '#b8860b',
                        'color': '#000'
                    }
                },
                {
                    selector: 'node.faulty',
                    style: {
                        'background-color': '#dc3545',
                        'border-color': '#a71d2a',
                        'opacity': 0.6
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#3a3a5e',
                        'curve-style': 'bezier',
                        'opacity': 0.5
                    }
                },
                {
                    selector: 'edge.active',
                    style: {
                        'line-color': '#ff6b35',
                        'width': 4,
                        'opacity': 1,
                        'target-arrow-color': '#ff6b35',
                        'target-arrow-shape': 'triangle'
                    }
                }
            ],
            layout: {
                name: 'circle',
                padding: 50
            },
            userZoomingEnabled: false,
            userPanningEnabled: false,
            boxSelectionEnabled: false
        });
        
        this.createInitialNodes();
    },
    
    createInitialNodes() {
        const numReplicas = App.config?.num_replicas || 4;
        const elements = [];
        
        for (let i = 0; i < numReplicas; i++) {
            elements.push({
                data: { id: `r${i}`, label: `R${i}` }
            });
        }
        
        for (let i = 0; i < numReplicas; i++) {
            for (let j = i + 1; j < numReplicas; j++) {
                elements.push({
                    data: { 
                        id: `e${i}-${j}`, 
                        source: `r${i}`, 
                        target: `r${j}` 
                    }
                });
            }
        }
        
        this.cy.add(elements);
        this.cy.layout({ name: 'circle', padding: 50 }).run();
    },
    
    updateNodes(replicas) {
        for (const replica of replicas) {
            const node = this.cy.getElementById(`r${replica.replica_id}`);
            if (node) {
                node.removeClass('leader faulty');
                if (replica.is_leader) {
                    node.addClass('leader');
                }
                if (replica.is_faulty) {
                    node.addClass('faulty');
                }
            }
        }
    },
    
    highlightMessage(event) {
        if (event.type === 'MESSAGE_RECEIVE') {
            const senderId = event.sender_id;
            const recipientId = event.recipient_id;
            
            const edgeId1 = `e${Math.min(senderId, recipientId)}-${Math.max(senderId, recipientId)}`;
            const edge = this.cy.getElementById(edgeId1);
            
            if (edge) {
                edge.addClass('active');
                setTimeout(() => {
                    edge.removeClass('active');
                }, 500);
            }
        }
    }
};
