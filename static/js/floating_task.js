/**
 * Floating Task Manager for Background Report Generation
 */

// Task management functions
class FloatingTaskManager {
    constructor() {
        this.tasks = [];
        this.init();
        this.notified = new Set();
        this.injectStyles();
    }
    
    injectStyles() {
        if (document.getElementById('floating-task-styles')) return;
        const style = document.createElement('style');
        style.id = 'floating-task-styles';
        style.textContent = `
            .floating-task-modal {
                position: fixed;
                bottom: 90px;
                right: 24px;
                width: 680px;
                max-width: 92vw;
                max-height: 70vh;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(0, 0, 0, 0.05);
                display: flex;
                flex-direction: column;
                z-index: 10050;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                overflow: hidden;
                transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                opacity: 0;
                transform: translateY(20px) scale(0.95);
                pointer-events: none;
            }
            .floating-task-modal.active {
                opacity: 1;
                transform: translateY(0) scale(1);
                pointer-events: auto;
            }
            .task-modal-header {
                padding: 16px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                flex-shrink: 0;
            }
            .task-modal-title {
                font-size: 16px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            .task-modal-close {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.8);
                cursor: pointer;
                font-size: 18px;
                padding: 4px;
                transition: color 0.2s;
            }
            .task-modal-close:hover {
                color: white;
            }
            .task-modal-content {
                padding: 0;
                overflow-y: auto;
                flex-grow: 1;
                background: #f8f9fa;
            }
            .task-item {
                background: white;
                margin: 12px 20px;
                padding: 16px;
                border-radius: 8px;
                border: 1px solid #eef0f2;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .task-item:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }
            .task-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            .task-name {
                font-size: 14px;
                font-weight: 600;
                color: #2d3748;
            }
            .task-meta {
                display: flex;
                gap: 12px;
                font-size: 12px;
                color: #718096;
                margin-bottom: 12px;
            }
            .task-progress-bar {
                height: 6px;
                background: #edf2f7;
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 8px;
            }
            .task-progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4fd1c5 0%, #38b2ac 100%);
                border-radius: 3px;
                transition: width 0.3s ease;
            }
            .task-actions {
                display: flex;
                gap: 8px;
                justify-content: flex-end;
            }
            .btn-action {
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                border: none;
                transition: background 0.2s;
            }
            .btn-view { background: #ebf8ff; color: #2b6cb0; }
            .btn-view:hover { background: #bee3f8; }
            .btn-pause { background: #fefcbf; color: #975a16; }
            .btn-pause:hover { background: #faf089; }
            .btn-resume { background: #c6f6d5; color: #276749; }
            .btn-resume:hover { background: #9ae6b4; }
            .btn-cancel { background: #fff5f5; color: #c53030; }
            .btn-cancel:hover { background: #fed7d7; }
            
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .floating-task-modal {
                    background: #1a202c;
                    border-color: #2d3748;
                }
                .task-modal-content {
                    background: #171923;
                }
                .task-item {
                    background: #2d3748;
                    border-color: #4a5568;
                }
                .task-name {
                    color: #e2e8f0;
                }
                .task-meta {
                    color: #a0aec0;
                }
                .task-progress-bar {
                    background: #4a5568;
                }
            }
        `;
        document.head.appendChild(style);
    }

    init() {
        this.setupTaskMonitoring();
        this.setupUIHandlers();
    }
    
    setupTaskMonitoring() {
        try {
            if (typeof Worker !== 'undefined') {
                this.worker = new Worker('/static/js/task_worker.js');
                this.worker.onmessage = (e) => {
                    const msg = e.data;
                    if (msg && msg.type === 'tasks_update' && msg.payload && msg.payload.tasks) {
                        this.updateTaskList(msg.payload.tasks);
                    }
                };
            }
        } catch(e) {}
        try {
            this.bc = new BroadcastChannel('tasks_channel');
            this.bc.onmessage = (e) => {
                const msg = e.data;
                if (msg && msg.type === 'tasks_update' && msg.payload && msg.payload.tasks) {
                    this.updateTaskList(msg.payload.tasks);
                }
            };
        } catch(e) {}
        setInterval(() => { this.fetchTaskUpdates(); }, 8000);
    }
    
    setupUIHandlers() {
        let floatingIcon = document.getElementById('floating-icon');
        if (!floatingIcon) {
            floatingIcon = document.createElement('div');
            floatingIcon.id = 'floating-icon';
            floatingIcon.style.cssText = 'position:fixed;right:24px;bottom:24px;z-index:10060;width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#ffd54f 0%,#ff9800 100%);box-shadow:0 10px 25px rgba(0,0,0,0.2);color:#fff;display:none;align-items:center;justify-content:center;cursor:pointer;transition:transform 0.15s ease, box-shadow 0.15s ease;';
            const inner = document.createElement('div');
            inner.style.cssText = 'display:flex;align-items:center;gap:6px;';
            inner.innerHTML = '<i class="fas fa-tasks" style="font-size:18px"></i><span class="icon-text" style="font-weight:700;font-size:12px">0</span>';
            floatingIcon.appendChild(inner);
            document.body.appendChild(floatingIcon);
        }
        floatingIcon.addEventListener('click', () => { this.toggleTaskPanel(); });
        floatingIcon.addEventListener('mouseenter', () => {
            floatingIcon.style.boxShadow = '0 14px 32px rgba(0,0,0,0.25)';
        });
        floatingIcon.addEventListener('mouseleave', () => {
            floatingIcon.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
        });
        floatingIcon.addEventListener('mousedown', () => {
            floatingIcon.style.transform = 'scale(0.97)';
        });
        floatingIcon.addEventListener('mouseup', () => {
            floatingIcon.style.transform = 'scale(1)';
        });
    }
    
    fetchTaskUpdates() {
        fetch('/api/tasks')
            .then(response => response.json())
            .then(data => {
                if (data.tasks) {
                    this.updateTaskList(data.tasks);
                }
            })
            .catch(error => {
                console.error('Error fetching tasks:', error);
            });
    }
    
    updateTaskList(tasks) {
        const floatingIcon = document.getElementById('floating-icon');
        if (floatingIcon) {
            const activeTasks = tasks.filter(task => 
                task.status === 'processing' || task.status === 'pending'
            );
            
            if (activeTasks.length > 0) {
                floatingIcon.style.display = 'flex';
                floatingIcon.classList.add('processing');
                floatingIcon.classList.remove('completed');
                const pct = Math.max(...activeTasks.map(t => Number(t.progress || 0)), 0);
                floatingIcon.querySelector('.icon-text').textContent = Math.round(pct) + '%';
                const deg = Math.round((pct/100) * 360);
                floatingIcon.style.backgroundImage = `conic-gradient(#ffeb3b ${deg}deg, #ff9800 ${deg}deg)`;
            } else {
                const completedTasks = tasks.filter(task => task.status === 'completed');
                if (completedTasks.length > 0) {
                    floatingIcon.style.display = 'flex';
                    floatingIcon.classList.add('completed');
                    floatingIcon.classList.remove('processing');
                    floatingIcon.querySelector('.icon-text').textContent = '!';
                    floatingIcon.style.backgroundImage = 'linear-gradient(135deg,#66bb6a 0%,#43a047 100%)';
                    try {
                        if ('Notification' in self) {
                            Notification.requestPermission().then(p=>{
                                if (p==='granted') {
                                    completedTasks.forEach(t=>{
                                        if (!this.notified.has(t.task_id)) {
                                            const n = new Notification('报告已生成', { body: `${t.city} - ${t.industry}` });
                                            setTimeout(()=>{ try { n.close(); } catch(e){} }, 3000);
                                            this.notified.add(t.task_id);
                                        }
                                    });
                                }
                            });
                        }
                    } catch(e) {}
                } else {
                    floatingIcon.style.display = 'none';
                }
            }
        }
        // Also update panel if open
        const panel = document.getElementById('floating-task-panel');
        if (panel && panel.classList.contains('active')) {
            this.populateTaskPanel(panel);
        }
    }
    
    toggleTaskPanel() {
        let panel = document.getElementById('floating-task-panel');
        if (!panel) {
            panel = this.createTaskPanel();
            document.body.appendChild(panel);
            // Trigger reflow
            panel.offsetHeight;
        }
        
        if (panel.classList.contains('active')) {
            panel.classList.remove('active');
        } else {
            this.populateTaskPanel(panel);
            panel.classList.add('active');
        }
    }
    
    createTaskPanel() {
        const panel = document.createElement('div');
        panel.id = 'floating-task-panel';
        panel.className = 'floating-task-modal';
        
        panel.innerHTML = `
            <div class="task-modal-header">
                <div class="task-modal-title">后台任务管理</div>
                <button id="close-task-panel" class="task-modal-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div id="tasks-content" class="task-modal-content custom-scrollbar">
                <div class="text-center py-8 text-gray-500">正在加载...</div>
            </div>
        `;
        
        panel.querySelector('#close-task-panel').addEventListener('click', () => {
            panel.classList.remove('active');
        });
        
        return panel;
    }
    
    populateTaskPanel(panel) {
        const contentDiv = panel.querySelector('#tasks-content');
        fetch('/api/tasks').then(r=>r.json()).then(data=>{
            if (data.tasks && data.tasks.length > 0) {
                let html = '';
                data.tasks.forEach(task => {
                        const statusClass = task.status === 'completed' ? 'text-green-600' : 
                                          task.status === 'failed' ? 'text-red-600' : 
                                          'text-yellow-600';
                        const statusText = task.status === 'completed' ? '已完成' : 
                                         task.status === 'failed' ? '失败' : 
                                         '进行中';
                        
                        // Removed llm_service parameter from URL
                        const viewHref = (task.status === 'completed' && task.report_id)
                            ? `/report/${task.report_id}`
                            : `/stream-report/${task.task_id}?city=${encodeURIComponent(task.city)}&industry=${encodeURIComponent(task.industry)}`;
                            
                        const viewText = (task.status === 'completed') ? '查看报告' : '查看生成';
                        const pct = Math.round(Number(task.progress || 0));
                        const paused = task.paused ? '(暂停)' : '';
                        
                        // Format date
                        const createdDate = task.created_at ? new Date(task.created_at * 1000).toLocaleString('zh-CN', {
                            month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
                        }) : '';

                        html += `
                        <div class="task-item">
                            <div class="task-header">
                                <div class="task-name">${task.city} - ${task.industry}</div>
                                <div class="text-xs ${statusClass} font-medium">${statusText} ${paused}</div>
                            </div>
                            <div class="task-meta">
                                <span><i class="far fa-clock mr-1"></i>${createdDate}</span>
                            </div>
                            <div class="task-progress-bar">
                                <div class="task-progress-fill" style="width:${pct}%; background: ${task.status === 'failed' ? '#fc8181' : (task.status === 'completed' ? '#68d391' : '')}"></div>
                            </div>
                            <div class="flex justify-between items-center mt-2">
                                <div class="text-xs text-gray-500">进度 ${pct}%</div>
                                <div class="task-actions">
                                    <button onclick="window.location.href='${viewHref}'" class="btn-action btn-view">${viewText}</button>
                                    ${task.status === 'processing' && !task.paused ? 
                                        `<button onclick="(function(){fetch('/api/tasks/${task.task_id}/pause',{method:'POST'}).then(()=>window.floatingTaskManager.fetchTaskUpdates());})()" class="btn-action btn-pause">暂停</button>` : ''}
                                    ${task.status === 'processing' && task.paused ? 
                                        `<button onclick="(function(){fetch('/api/tasks/${task.task_id}/resume',{method:'POST'}).then(()=>window.floatingTaskManager.fetchTaskUpdates());})()" class="btn-action btn-resume">继续</button>` : ''}
                                    ${task.status === 'processing' || task.status === 'pending' ? 
                                        `<button onclick="(function(){fetch('/api/tasks/${task.task_id}/cancel',{method:'POST'}).then(()=>window.floatingTaskManager.fetchTaskUpdates());})()" class="btn-action btn-cancel">取消</button>` : ''}
                                    <button onclick="deleteTask('${task.task_id}')" class="btn-action btn-cancel" style="background:#fff1f0;color:#e53e3e;">删除</button>
                                </div>
                            </div>
                        </div>`;
                    });
                contentDiv.innerHTML = html;
            } else {
                contentDiv.innerHTML = '<div class="text-center py-12 text-gray-400">暂无后台任务</div>';
            }
        }).catch(()=>{ contentDiv.innerHTML = '<div class="text-center py-12 text-red-500">加载失败</div>'; });
    }
}

// Global function to delete a task
function deleteTask(taskId) {
    fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            if (window.floatingTaskManager) {
                window.floatingTaskManager.fetchTaskUpdates();
            }
        }
    })
    .catch(error => {
        console.error('Error deleting task:', error);
    });
}

// Initialize the floating task manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.floatingTaskManager = new FloatingTaskManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FloatingTaskManager;
}

// Global helpers for background tasks integration
// Removed llmService parameter
window.addBackgroundTask = async function(taskId, city, industry, additionalContext = '') {
    try {
        const resp = await fetch('/api/stream/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // Removed llm_service from body
            body: JSON.stringify({ city, industry, additional_context: additionalContext })
        });
        if (window.floatingTaskManager) {
            window.floatingTaskManager.fetchTaskUpdates();
        }
    } catch (e) {
        console.error('addBackgroundTask error:', e);
    }
};

window.showFloatingIcon = function(show = true) {
    const el = document.getElementById('floating-icon');
    if (!el) return;
    el.style.display = show ? 'flex' : 'none';
};
