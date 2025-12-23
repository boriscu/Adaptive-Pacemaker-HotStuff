const Controls = {
    init() {
        this.initConfigControls();
        this.initSimulationControls();
    },
    
    initConfigControls() {
        const replicasInput = document.getElementById('config-replicas');
        const faultyInput = document.getElementById('config-faulty');
        const pacemakerSelect = document.getElementById('config-pacemaker');
        const timeoutInput = document.getElementById('config-timeout');
        const applyBtn = document.getElementById('btn-apply-config');
        
        const updateQuorumInfo = () => {
            const n = parseInt(replicasInput.value) || 4;
            const f = parseInt(faultyInput.value) || 0;
            const quorum = n - f;
            const maxF = Math.floor((n - 1) / 3);
            
            document.getElementById('quorum-size').textContent = quorum;
            document.getElementById('max-faulty').textContent = maxF;
            
            faultyInput.max = n - 1;
        };
        
        replicasInput.addEventListener('input', updateQuorumInfo);
        faultyInput.addEventListener('input', updateQuorumInfo);
        
        applyBtn.addEventListener('click', async () => {
            if (App.isRunning) {
                alert('Please reset the simulation before changing configuration');
                return;
            }
            
            const config = {
                num_replicas: parseInt(replicasInput.value),
                num_faulty: parseInt(faultyInput.value),
                fault_type: document.getElementById('config-fault-type').value,
                pacemaker_type: pacemakerSelect.value,
                base_timeout_ms: parseInt(timeoutInput.value)
            };
            
            try {
                const response = await fetch('/api/simulation/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    applyBtn.textContent = '✓ Applied';
                    applyBtn.classList.add('btn-success');
                    
                    setTimeout(() => {
                        applyBtn.textContent = 'Apply Configuration';
                        applyBtn.classList.remove('btn-success');
                    }, 2000);
                    
                    await App.refreshAll();
                    NetworkGraph.updateNodeCount(config.num_replicas);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Failed to apply config:', error);
                alert('Failed to apply configuration');
            }
        });
        
        updateQuorumInfo();
    },
    
    initSimulationControls() {
        document.getElementById('btn-start').addEventListener('click', async () => {
            document.getElementById('config-panel').style.opacity = '0.5';
            document.getElementById('config-panel').style.pointerEvents = 'none';
            
            await App.start();
            this.updateButtons();
        });
        
        document.getElementById('btn-pause').addEventListener('click', async () => {
            if (App.autoStepInterval) {
                App.stopAutoStep();
            } else {
                await App.pause();
            }
            this.updateButtons();
        });
        
        document.getElementById('btn-step').addEventListener('click', async () => {
            await App.step();
        });
        
        document.getElementById('btn-reset').addEventListener('click', async () => {
            App.stopAutoStep();
            await App.reset();
            
            document.getElementById('config-panel').style.opacity = '1';
            document.getElementById('config-panel').style.pointerEvents = 'auto';
            
            this.updateButtons();
        });
        
        document.getElementById('btn-run-steps').addEventListener('click', async () => {
            const count = parseInt(document.getElementById('step-count').value) || 10;
            await App.runSteps(count);
        });
        
        const speedSlider = document.getElementById('speed-slider');
        const autoRunBtn = document.getElementById('btn-auto-run');
        
        speedSlider.addEventListener('input', (e) => {
            document.getElementById('speed-value').textContent = e.target.value;
        });
        
        speedSlider.addEventListener('change', (e) => {
            if (App.autoStepInterval) {
                App.startAutoStep(parseInt(e.target.value));
            }
        });
        
        autoRunBtn.addEventListener('click', () => {
            if (App.autoStepInterval) {
                App.stopAutoStep();
                autoRunBtn.textContent = '▶ Auto';
                autoRunBtn.classList.remove('btn-primary');
                autoRunBtn.classList.add('btn-secondary');
            } else {
                App.startAutoStep(parseInt(speedSlider.value));
                autoRunBtn.textContent = '⏹ Stop';
                autoRunBtn.classList.remove('btn-secondary');
                autoRunBtn.classList.add('btn-primary');
            }
        });
    },
    
    updateButtons() {
        const startBtn = document.getElementById('btn-start');
        const pauseBtn = document.getElementById('btn-pause');
        const stepBtn = document.getElementById('btn-step');
        
        if (!App.isRunning) {
            startBtn.disabled = false;
            pauseBtn.disabled = true;
            stepBtn.disabled = true;
        } else {
            startBtn.disabled = true;
            pauseBtn.disabled = false;
            stepBtn.disabled = false;
        }
    },
    
    async loadConfig() {
        try {
            const response = await fetch('/api/simulation/config');
            const config = await response.json();
            
            document.getElementById('config-replicas').value = config.num_replicas;
            document.getElementById('config-faulty').value = config.num_faulty;
            document.getElementById('config-pacemaker').value = config.pacemaker_type.toLowerCase();
            document.getElementById('config-timeout').value = config.base_timeout_ms;
            
            document.getElementById('quorum-size').textContent = config.quorum_size;
            document.getElementById('max-faulty').textContent = config.max_faulty;
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    }
};
