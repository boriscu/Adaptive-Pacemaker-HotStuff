const Controls = {
    init() {
        document.getElementById('btn-start').addEventListener('click', async () => {
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
            this.updateButtons();
        });
        
        document.getElementById('btn-run-steps').addEventListener('click', async () => {
            const count = parseInt(document.getElementById('step-count').value) || 10;
            await App.runSteps(count);
        });
        
        const speedSlider = document.getElementById('speed-slider');
        speedSlider.addEventListener('input', (e) => {
            document.getElementById('speed-value').textContent = e.target.value;
        });
        
        speedSlider.addEventListener('change', (e) => {
            if (App.autoStepInterval) {
                App.startAutoStep(parseInt(e.target.value));
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
    }
};
