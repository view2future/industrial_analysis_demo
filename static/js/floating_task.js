/**
 * Floating Task Manager for Background Report Generation
 */

// Task management functions
class FloatingTaskManager {
    constructor() {
        this.tasks = [];
        this.init();
        this.notified = new Set();
    }
    
    init() {
        this.setupTaskMonitoring();
        
        // Set up UI interactions
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
        // Handle floating task icon interactions
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
        floatingIcon.addEventListener('click', () => { this.showTaskPanel(); });
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
        // Fetch active tasks from server
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
        // Update floating icon based on active tasks
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
    }
    
    showTaskPanel() {
        // Create or show task panel
        let panel = document.getElementById('floating-task-panel');
        if (!panel) {
            panel = this.createTaskPanel();
            document.body.appendChild(panel);
        }
        
        // Fetch and display current tasks
        this.populateTaskPanel(panel);
        
        // Toggle visibility using style (works without Tailwind)
        const isHidden = panel.style.display === 'none' || panel.style.display === '';
        if (isHidden) {
            if (typeof panel.updatePosition === 'function') panel.updatePosition();
            panel.style.opacity = '0';
            panel.style.transform = 'translateY(8px) scale(0.98)';
            panel.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
            panel.style.display = 'block';
            requestAnimationFrame(() => {
                panel.style.opacity = '1';
                panel.style.transform = 'translateY(0) scale(1)';
            });
        } else {
            panel.style.opacity = '1';
            panel.style.transform = 'translateY(0) scale(1)';
            panel.style.transition = 'opacity 0.15s ease, transform 0.15s ease';
            requestAnimationFrame(() => {
                panel.style.opacity = '0';
                panel.style.transform = 'translateY(8px) scale(0.98)';
                setTimeout(() => { panel.style.display = 'none'; }, 150);
            });
        }
    }
    
    createTaskPanel() {
        const panel = document.createElement('div');
        panel.id = 'floating-task-panel';
        panel.className = '';
        panel.style.position = 'fixed';
        panel.style.display = 'none';
        panel.style.zIndex = '10050';
        panel.style.right = '24px';
        panel.style.bottom = '90px';
        const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        panel.style.width = (vw < 420) ? '92vw' : '420px';
        panel.style.background = '#fff';
        panel.style.borderRadius = '12px';
        panel.style.boxShadow = '0 12px 32px rgba(0,0,0,0.2)';
        panel.style.border = '1px solid rgba(0,0,0,0.1)';
        
        panel.innerHTML = `
            <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-3 rounded-t-lg">
                <div class="flex justify-between items-center">
                    <h3 class="font-bold">后台任务</h3>
                    <button id="close-task-panel" class="text-white hover:text-gray-200">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div id="tasks-content" class="p-3" style="max-height: 380px; overflow-y: auto;">
                <div class="text-center py-4 text-gray-500">暂无任务</div>
            </div>
        `;
        
        // Add close button handler
        panel.querySelector('#close-task-panel').addEventListener('click', () => {
            panel.style.display = 'none';
        });
        // Position near icon when opening
        panel.updatePosition = () => {
            const icon = document.getElementById('floating-icon');
            if (!icon) return;
            const rect = icon.getBoundingClientRect();
            const fromBottom = window.innerHeight - rect.bottom;
            const fromRight = window.innerWidth - rect.right;
            panel.style.bottom = `${fromBottom + 72}px`;
            panel.style.right = `${fromRight + 0}px`;
        };
        
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
                        const viewHref = (task.status === 'completed' && task.report_id)
                            ? `/report/${task.report_id}`
                            : `/stream-report/${task.task_id}?city=${encodeURIComponent(task.city)}&industry=${encodeURIComponent(task.industry)}&llm_service=${task.llm_service}`;
                        const viewText = (task.status === 'completed') ? '查看报告' : '查看生成';
                        const pct = Math.round(Number(task.progress || 0));
                        const paused = task.paused ? '暂停中' : '';
                        // Read cached resume info if present
                        let resumeText = '';
                        try {
                            const cacheRaw = localStorage.getItem(`report_cache_${task.task_id}`);
                            if (cacheRaw) {
                                const cache = JSON.parse(cacheRaw);
                                if (cache && cache.content_md) {
                                    const cw = (cache.wordcount || '').toString();
                                    resumeText = `已缓存 ${cw} 字，支持断点续传`;
                                }
                            }
                        } catch(e) {}
                                          
                        html += `
                        <div class="task-item border-b border-gray-100 py-2">
                            <div class="font-medium flex items-center justify-between">
                                <span>${task.city} - ${task.industry}</span>
                                <span class="text-xs ${statusClass}">${statusText} ${paused}</span>
                            </div>
                            <div class="text-xs text-gray-600">${task.llm_service}</div>
                            <div class="mt-1">
                                <div style="height:6px;background:#eee;border-radius:4px;overflow:hidden">
                                    <div style="height:6px;width:${pct}%;background:linear-gradient(90deg,#ffd54f,#ff9800);"></div>
                                </div>
                                <div class="text-xs text-gray-500 mt-1">进度 ${pct}%${resumeText ? ' · ' + resumeText : ''}</div>
                            </div>
                            <div class="flex gap-2 mt-2">
                                <button onclick="window.location.href='${viewHref}'" class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">${viewText}</button>
                                <button onclick="(function(){fetch('/api/tasks/${task.task_id}/pause',{method:'POST'}).then(()=>window.floatingTaskManager.populateTaskPanel(document.getElementById('floating-task-panel')));})()" class="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">暂停</button>
                                <button onclick="(function(){fetch('/api/tasks/${task.task_id}/resume',{method:'POST'}).then(()=>window.floatingTaskManager.populateTaskPanel(document.getElementById('floating-task-panel')));})()" class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">继续</button>
                                <button onclick="(function(){fetch('/api/tasks/${task.task_id}/cancel',{method:'POST'}).then(()=>window.floatingTaskManager.populateTaskPanel(document.getElementById('floating-task-panel')));})()" class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">取消</button>
                                <button onclick="deleteTask('${task.task_id}')" class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">删除</button>
                            </div>
                        </div>`;
                    });
                contentDiv.innerHTML = html;
            } else {
                contentDiv.innerHTML = '<div class="text-center py-4 text-gray-500">暂无任务</div>';
            }
        }).catch(()=>{ contentDiv.innerHTML = '<div class="text-center py-4 text-red-500">加载失败</div>'; });
    }
}

// Global function to delete a task
function deleteTask(taskId) {
    fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            // Refresh the task panel
            const panel = document.getElementById('floating-task-panel');
            if (panel) {
                const floatingTaskManager = new FloatingTaskManager();
                floatingTaskManager.populateTaskPanel(panel);
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
window.addBackgroundTask = async function(taskId, city, industry, llmService = 'kimi', additionalContext = '') {
    try {
        const resp = await fetch('/api/stream/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city, industry, llm_service: llmService, additional_context: additionalContext })
        });
        // Fire-and-forget: do not consume stream; background will continue on server
        // Optionally nudge UI to show icon immediately
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
