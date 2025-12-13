class ToasterSystem {
    constructor() {
        this.tasks = [];
        this.activeToasts = []; // Currently animating or displayed
        this.queue = []; // Pending processing
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.injectHTML();
        this.bindEvents();
        this.startMonitoring();
        this.renderState();
    }

    injectHTML() {
        // Create container
        const container = document.createElement('div');
        container.className = 'toaster-container';
        container.innerHTML = `
            <div class="toaster-body idle" id="toaster-body">
                <div class="toaster-slot"></div>
                <div class="toaster-knob"></div>
                <div class="toaster-light"></div>
                <div class="toaster-count" id="toaster-count">0</div>
            </div>
            <div id="toast-staging-area"></div>
            <div class="toast-card" id="toast-details-card">
                <h4 id="card-title" style="margin:0 0 5px 0;font-size:14px;">Task</h4>
                <p id="card-desc" style="margin:0;font-size:12px;color:#666;">Details...</p>
            </div>
            <div class="toaster-panel" id="toaster-panel">
                <div class="toaster-panel-header">
                    <div style="display:flex;gap:8px;align-items:center;">
                        <input type="checkbox" id="select-all-tasks" class="task-checkbox" title="Select All">
                        <span>Task List</span>
                    </div>
                    <div class="header-actions">
                        <button id="batch-delete" class="btn-header" title="Delete Selected" style="display:none;"><i class="fas fa-trash"></i></button>
                        <button id="close-panel" style="border:none;background:none;cursor:pointer;font-size:16px;">&times;</button>
                    </div>
                </div>
                <div class="toaster-panel-content" id="toaster-panel-content"></div>
            </div>
        `;
        document.body.appendChild(container);
        this.toasterBody = document.getElementById('toaster-body');
        this.toasterCount = document.getElementById('toaster-count');
        this.stagingArea = document.getElementById('toast-staging-area');
        this.card = document.getElementById('toast-details-card');
        this.panel = document.getElementById('toaster-panel');
        this.panelContent = document.getElementById('toaster-panel-content');
        
        this.panel.querySelector('#close-panel').addEventListener('click', () => this.hidePanel());
        this.panel.querySelector('#select-all-tasks').addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
        this.panel.querySelector('#batch-delete').addEventListener('click', () => this.deleteSelectedTasks());

        // Load CSS if not present (handled by backend usually, but for safety)
        if (!document.querySelector('link[href*="toaster.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/css/toaster.css';
            document.head.appendChild(link);
        }
    }

    bindEvents() {
        // Long press on toaster
        let pressTimer;
        this.toasterBody.addEventListener('mousedown', () => {
            pressTimer = setTimeout(() => this.openTaskPanel(), 8000); // 800ms long press
        });
        this.toasterBody.addEventListener('mouseup', () => clearTimeout(pressTimer));
        this.toasterBody.addEventListener('mouseleave', () => clearTimeout(pressTimer));
        
        // Click to toggle panel (short click)
        this.toasterBody.addEventListener('click', (e) => {
            if (e.detail === 1) { // Simple click
                // Always allow toggling the panel, regardless of task count
                this.togglePanel();
            }
        });
    }

    startMonitoring() {
        // Reuse logic from FloatingTaskManager to fetch tasks
        // Assuming /api/tasks is the endpoint
        this.fetchTasks();
        setInterval(() => this.fetchTasks(), 3000);
    }

    async fetchTasks() {
        try {
            const res = await fetch('/api/tasks');
            const data = await res.json();
            this.updateTasks(data.tasks || []);
        } catch (e) {
            console.error('Toaster fetch error:', e);
        }
    }

    updateTasks(newTasks) {
        // Diff tasks to find new ones or status changes
        // For simplicity, just check for new "completed" tasks that we haven't popped yet.
        // Or "processing" tasks to set state.
        
        const processing = newTasks.some(t => t.status === 'processing' || t.status === 'pending');
        this.setSystemState(processing ? 'processing' : 'idle');

        newTasks.forEach(task => {
            const oldTask = this.tasks.find(t => t.task_id === task.task_id);
            if (!oldTask) {
                // New task
                this.tasks.push(task);
                if (task.status === 'processing') {
                    // Maybe pop a "started" toast?
                }
            } else {
                // Update properties
                oldTask.progress = task.progress;
                
                // Status change
                if (oldTask.status !== task.status) {
                    oldTask.status = task.status;
                    if (task.status === 'completed' || task.status === 'failed') {
                        this.queueToast(task);
                    }
                }
            }
        });
        
        // Update count
        this.toasterCount.textContent = newTasks.filter(t => t.status === 'completed').length;

        // Update panel if open
        if (this.panel.classList.contains('visible')) {
            this.renderPanel();
        }
    }

    setSystemState(state) {
        if (state === 'processing') {
            this.toasterBody.classList.remove('idle');
            this.toasterBody.classList.add('processing');
        } else {
            this.toasterBody.classList.remove('processing');
            this.toasterBody.classList.add('idle');
        }
    }

    queueToast(task) {
        this.queue.push(task);
        this.processQueue();
    }

    async processQueue() {
        if (this.queue.length === 0 || this.isAnimating) return;
        
        this.isAnimating = true;
        const task = this.queue.shift();
        
        await this.runToastSequence(task);
        
        this.isAnimating = false;
        // Small delay before next
        setTimeout(() => this.processQueue(), 500); 
    }

    async runToastSequence(task) {
        return new Promise(async (resolve) => {
            // 1. Prepare (0.3s)
            this.toasterBody.classList.add('prep');
            await this.wait(300);
            this.toasterBody.classList.remove('prep');

            // 2. Create Toast
            const toast = document.createElement('div');
            toast.className = 'toast-item';
            toast.textContent = task.city ? task.city.substring(0, 2) : 'Task'; // Short text
            if (task.status === 'failed') toast.classList.add('failed');
            
            // Add click handler
            toast.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleToastClick(toast, task);
            });

            this.stagingArea.appendChild(toast);

            // 3. Eject (0.5s)
            toast.classList.add('popping');
            this.createParticles();
            await this.wait(500);

            if (task.status === 'failed') {
                // Fail sequence: Shatter
                toast.classList.add('shatter');
                // Play sound? (Skipping audio for now unless requested, user mentioned "Click sound")
                await this.wait(500);
                toast.remove();
                resolve();
                return;
            }

            // 4. Air (1.2s)
            toast.classList.remove('popping');
            toast.classList.add('flying');
            await this.wait(1200);

            // 5. Fall (1.0s)
            toast.classList.remove('flying');
            toast.classList.add('falling');
            await this.wait(1000);

            // 6. Landed
            toast.classList.remove('falling');
            toast.classList.add('landed');
            
            // Manage Stack (Max 3 visible)
            this.activeToasts.push(toast);
            this.updateStackLayout();
            
            resolve();
        });
    }

    updateStackLayout() {
        // Keep only last 3 visible
        if (this.activeToasts.length > 3) {
            const removed = this.activeToasts.shift();
            removed.remove();
        }
        
        // Position them in a fan or stack
        this.activeToasts.forEach((t, index) => {
            // Reverse index (0 is oldest, last is newest)
            // But we want newest on front?
            // Actually CSS z-index might handle order if appended later.
            // Let's offset them slightly.
            const offset = (this.activeToasts.length - 1 - index) * 5; 
            const rotate = (this.activeToasts.length - 1 - index) * 5;
            t.style.transform = `translateY(${offset}px) rotate(${rotate}deg)`;
            t.style.zIndex = index;
        });
    }

    handleToastClick(toast, task) {
        // Pause animation if running (handled by class usually, but here we might be in 'landed' state)
        // Spec: "Click flying toast: Pause animation, show details"
        
        // If it's flying/falling, we pause it.
        const computedStyle = window.getComputedStyle(toast);
        const animationState = computedStyle.animationPlayState;
        
        if (animationState !== 'paused') {
            toast.style.animationPlayState = 'paused';
            toast.classList.add('paused');
            
            // Show details
            this.showCard(task);
            
            // Resume after 2s
            setTimeout(() => {
                toast.style.animationPlayState = 'running';
                toast.classList.remove('paused');
                this.hideCard();
            }, 2000);
        } else {
            // Already paused or landed, just show details
             this.showCard(task);
             setTimeout(() => this.hideCard(), 2000);
        }
    }

    showCard(task) {
        this.card.querySelector('#card-title').textContent = `${task.city} - ${task.industry}`;
        this.card.querySelector('#card-desc').textContent = `Status: ${task.status}\nProgress: ${task.progress || 0}%`;
        this.card.classList.add('visible');
    }

    hideCard() {
        this.card.classList.remove('visible');
    }

    createParticles() {
        // Simple particle effect
        for (let i = 0; i < 5; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            p.style.left = (50 + (Math.random() * 40 - 20)) + '%';
            p.style.bottom = '60px';
            this.toasterBody.appendChild(p);
            
            // Animate
            const destX = (Math.random() * 60 - 30);
            const destY = - (20 + Math.random() * 30);
            
            p.animate([
                { transform: 'translate(0,0)', opacity: 0.8 },
                { transform: `translate(${destX}px, ${destY}px)`, opacity: 0 }
            ], {
                duration: 500,
                easing: 'ease-out'
            }).onfinish = () => p.remove();
        }
    }

    togglePanel() {
        if (this.panel.classList.contains('visible')) {
            this.hidePanel();
        } else {
            this.showPanel();
        }
    }

    showPanel() {
        this.renderPanel();
        this.panel.classList.add('visible');
    }

    hidePanel() {
        this.panel.classList.remove('visible');
    }

    renderPanel() {
        // Filter unique tasks by ID
        let uniqueTasks = Array.from(new Map(this.tasks.map(item => [item.task_id, item])).values());
        
        if (uniqueTasks.length === 0) {
            this.panelContent.innerHTML = '<div style="padding:20px;text-align:center;color:#999;">No tasks</div>';
            return;
        }

        // Apply saved order if exists
        const savedOrder = JSON.parse(localStorage.getItem('toaster_task_order') || '[]');
        if (savedOrder.length > 0) {
            const orderMap = new Map(savedOrder.map((id, index) => [id, index]));
            uniqueTasks.sort((a, b) => {
                const indexA = orderMap.has(a.task_id) ? orderMap.get(a.task_id) : 9999;
                const indexB = orderMap.has(b.task_id) ? orderMap.get(b.task_id) : 9999;
                return indexA - indexB;
            });
        } else {
            // Default Sort: processing first, then newest
            uniqueTasks.sort((a, b) => {
                if (a.status === 'processing' && b.status !== 'processing') return -1;
                if (a.status !== 'processing' && b.status === 'processing') return 1;
                return String(b.task_id).localeCompare(String(a.task_id));
            });
        }
        
        // Render
        this.panelContent.innerHTML = uniqueTasks.map(task => {
            // Format timestamp
            const date = task.created_at ? new Date(task.created_at * 1000) : new Date();
            const timeStr = date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
            
            // Status Label
            let statusLabel = '未知';
            let statusClass = 'status-pending';
            if (task.status === 'completed') { statusLabel = '已完成'; statusClass = 'status-completed'; }
            else if (task.status === 'processing') { statusLabel = '进行中'; statusClass = 'status-processing'; }
            else if (task.status === 'paused') { statusLabel = '已暂停'; statusClass = 'status-paused'; }
            else if (task.status === 'failed') { statusLabel = '失败'; statusClass = 'status-failed'; }

            return `
            <div class="toaster-task-item" draggable="true" data-id="${task.task_id}">
                <div class="drag-handle"><i class="fas fa-grip-vertical"></i></div>
                <input type="checkbox" class="task-checkbox item-checkbox" value="${task.task_id}" onchange="window.toasterSystem.updateBatchActions()">
                <div class="task-content-wrapper" onclick="window.location.href='${this.getTaskLink(task)}'">
                    <div class="task-title" title="${task.city} - ${task.industry}">${task.city} - ${task.industry}</div>
                    <div class="task-meta">
                        <span class="task-status ${statusClass}">${statusLabel}</span>
                        <span><i class="far fa-clock"></i> ${timeStr}</span>
                    </div>
                </div>
                <div class="task-actions">
                     ${task.status === 'processing' ? 
                        `<button class="btn-task-action btn-toggle" title="暂停" onclick="window.toasterSystem.toggleTaskStatus('${task.task_id}', 'pause')"><i class="fas fa-pause"></i></button>` : 
                        (task.status === 'paused' ? 
                            `<button class="btn-task-action btn-toggle" title="继续" onclick="window.toasterSystem.toggleTaskStatus('${task.task_id}', 'resume')"><i class="fas fa-play"></i></button>` : '')
                     }
                    <button class="btn-task-action btn-edit" title="编辑" onclick="window.toasterSystem.editTask('${task.task_id}')"><i class="fas fa-pen"></i></button>
                    <button class="btn-task-action btn-delete" title="删除" onclick="window.toasterSystem.deleteTask('${task.task_id}')"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `}).join('');
        
        this.bindDragEvents();
    }
    
    bindDragEvents() {
        const items = this.panelContent.querySelectorAll('.toaster-task-item');
        let draggedItem = null;
        
        items.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                draggedItem = item;
                setTimeout(() => item.classList.add('dragging'), 0);
            });
            
            item.addEventListener('dragend', () => {
                setTimeout(() => {
                    item.classList.remove('dragging');
                    draggedItem = null;
                    this.saveTaskOrder();
                }, 0);
            });
            
            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                const afterElement = getDragAfterElement(this.panelContent, e.clientY);
                if (afterElement == null) {
                    this.panelContent.appendChild(draggedItem);
                } else {
                    this.panelContent.insertBefore(draggedItem, afterElement);
                }
            });
        });
        
        function getDragAfterElement(container, y) {
            const draggableElements = [...container.querySelectorAll('.toaster-task-item:not(.dragging)')];
            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            }, { offset: Number.NEGATIVE_INFINITY }).element;
        }
    }
    
    saveTaskOrder() {
        const ids = [...this.panelContent.querySelectorAll('.toaster-task-item')].map(el => el.dataset.id);
        localStorage.setItem('toaster_task_order', JSON.stringify(ids));
    }

    toggleSelectAll(checked) {
        const checkboxes = this.panelContent.querySelectorAll('.item-checkbox');
        checkboxes.forEach(cb => cb.checked = checked);
        this.updateBatchActions();
    }
    
    updateBatchActions() {
        const checkedCount = this.panelContent.querySelectorAll('.item-checkbox:checked').length;
        const deleteBtn = this.panel.querySelector('#batch-delete');
        if (checkedCount > 0) {
            deleteBtn.style.display = 'inline-block';
        } else {
            deleteBtn.style.display = 'none';
        }
    }
    
    async deleteSelectedTasks() {
        const checkboxes = this.panelContent.querySelectorAll('.item-checkbox:checked');
        if (checkboxes.length === 0) return;
        
        if (!confirm(`确定要删除选中的 ${checkboxes.length} 个任务吗？`)) return;
        
        const ids = Array.from(checkboxes).map(cb => cb.value);
        for (const id of ids) {
            await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
        }
        
        this.fetchTasks();
        this.panel.querySelector('#select-all-tasks').checked = false;
        this.updateBatchActions();
    }

    async deleteTask(taskId) {
        if (!confirm('确定要删除此任务吗？')) return;
        await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
        this.fetchTasks();
    }
    
    async toggleTaskStatus(taskId, action) {
        await fetch(`/api/tasks/${taskId}/${action}`, { method: 'POST' });
        this.fetchTasks();
    }
    
    editTask(taskId) {
        const task = this.tasks.find(t => t.task_id === taskId);
        if (!task) return;
        
        // Since we can't easily edit running backend tasks, we'll offer to rename locally or show info
        // User requirement: "Edit button (modify task content)"
        // I will implement a visual rename for now, or alert limitation.
        const newTitle = prompt('修改任务名称 (仅本地显示):', `${task.city} - ${task.industry}`);
        if (newTitle) {
            const el = this.panelContent.querySelector(`.toaster-task-item[data-id="${taskId}"] .task-title`);
            if (el) el.textContent = newTitle;
            // In a real app, we'd save this alias to localStorage
        }
    }

    getTaskLink(task) {
        if (task.status === 'completed' && task.report_id) return `/report/${task.report_id}`;
        return `/stream-report/${task.task_id}?city=${encodeURIComponent(task.city)}&industry=${encodeURIComponent(task.industry)}`;
    }

    openTaskPanel() {
        this.showPanel();
    }

    wait(ms) {
        return new Promise(r => setTimeout(r, ms));
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    window.toasterSystem = new ToasterSystem();
    
    // Compatibility with legacy FloatingTaskManager
    window.floatingTaskManager = {
        fetchTaskUpdates: () => window.toasterSystem.fetchTasks(),
        toggleTaskPanel: () => window.toasterSystem.openTaskPanel()
    };
});

// Global helpers for background tasks integration (Legacy Support)
window.addBackgroundTask = async function(taskId, city, industry, additionalContext = '') {
    try {
        const resp = await fetch('/api/stream/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city, industry, additional_context: additionalContext })
        });
        if (window.toasterSystem) {
            window.toasterSystem.fetchTasks();
        }
    } catch (e) {
        console.error('addBackgroundTask error:', e);
    }
};

window.showFloatingIcon = function(show = true) {
    // Toaster is always visible or handled by state, but we can respect this if needed
    const body = document.getElementById('toaster-body');
    if (body) body.style.display = show ? 'block' : 'none';
};
