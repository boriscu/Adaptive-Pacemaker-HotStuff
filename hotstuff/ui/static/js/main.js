const App = {
    config: null,
    isRunning: false,
    isPaused: false,
    autoStepInterval: null,
    
    async init() {
        await this.loadConfig();
        NetworkGraph.init();
        ReplicaPanel.init();
        EventLog.init();
        Controls.init();
        await Controls.loadConfig();
        
        await this.refreshState();
    },
    
    async refreshAll() {
        await this.loadConfig();
        await Controls.loadConfig();
        await this.refreshState();
    },
    
    async loadConfig() {
        try {
            const response = await fetch('/api/simulation/config');
            this.config = await response.json();
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    },
    
    async refreshState() {
        try {
            const [statusRes, replicasRes, metricsRes] = await Promise.all([
                fetch('/api/simulation/status'),
                fetch('/api/state/replicas'),
                fetch('/api/metrics/summary')
            ]);
            
            const status = await statusRes.json();
            const replicas = await replicasRes.json();
            const metrics = await metricsRes.json();
            
            this.updateStatus(status);
            ReplicaPanel.update(replicas.replicas);
            NetworkGraph.updateNodes(replicas.replicas);
            this.updateMetrics(metrics);
        } catch (error) {
            console.error('Failed to refresh state:', error);
        }
    },
    
    updateStatus(status) {
        this.isRunning = status.is_running;
        this.isPaused = status.is_paused;
        
        const indicator = document.getElementById('status-indicator');
        indicator.className = '';
        
        if (!status.is_running) {
            indicator.textContent = 'Stopped';
            indicator.classList.add('status-stopped');
        } else if (status.is_paused) {
            indicator.textContent = 'Paused';
            indicator.classList.add('status-paused');
        } else {
            indicator.textContent = 'Running';
            indicator.classList.add('status-running');
        }
        
        document.getElementById('time-display').textContent = `Time: ${status.current_time}ms`;
        document.getElementById('view-display').textContent = `View: ${status.current_view}`;
    },
    
    updateMetrics(metrics) {
        document.getElementById('metric-commits').textContent = metrics.total_blocks_committed;
        document.getElementById('metric-timeouts').textContent = metrics.total_timeouts;
        document.getElementById('metric-latency').textContent = 
            `${metrics.average_commit_latency_ms.toFixed(1)}ms`;
        document.getElementById('metric-throughput').textContent = 
            `${metrics.throughput_blocks_per_second.toFixed(2)} blk/s`;
    },
    
    async start() {
        try {
            const response = await fetch('/api/simulation/start', { method: 'POST' });
            const result = await response.json();
            
            for (const event of result.events) {
                EventLog.addEvent(event);
            }
            
            await this.refreshState();
        } catch (error) {
            console.error('Failed to start simulation:', error);
        }
    },
    
    async pause() {
        try {
            await fetch('/api/simulation/pause', { method: 'POST' });
            await this.refreshState();
        } catch (error) {
            console.error('Failed to pause simulation:', error);
        }
    },
    
    async step() {
        try {
            const response = await fetch('/api/simulation/step', { method: 'POST' });
            const result = await response.json();
            
            if (result.event) {
                EventLog.addEvent(result.event);
                NetworkGraph.highlightMessage(result.event);
            }
            
            await this.refreshState();
            return result.event !== null;
        } catch (error) {
            console.error('Failed to step simulation:', error);
            return false;
        }
    },
    
    async runSteps(count) {
        try {
            const response = await fetch('/api/simulation/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count })
            });
            const result = await response.json();
            
            for (const event of result.events) {
                EventLog.addEvent(event);
            }
            
            await this.refreshState();
        } catch (error) {
            console.error('Failed to run steps:', error);
        }
    },
    
    async reset() {
        try {
            await fetch('/api/simulation/reset', { method: 'POST' });
            EventLog.clear();
            await this.refreshState();
        } catch (error) {
            console.error('Failed to reset simulation:', error);
        }
    },
    
    startAutoStep(speed) {
        this.stopAutoStep();
        const interval = Math.max(50, 1000 - speed * 10);
        this.autoStepInterval = setInterval(async () => {
            const hasMore = await this.step();
            if (!hasMore) {
                this.stopAutoStep();
            }
        }, interval);
    },
    
    stopAutoStep() {
        if (this.autoStepInterval) {
            clearInterval(this.autoStepInterval);
            this.autoStepInterval = null;
        }
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
