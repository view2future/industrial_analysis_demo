/**
 * Floating Task Manager for Background Report Generation
 */

// Task management functions
class FloatingTaskManager {
    constructor() {
        this.tasks = [];
        this.init();
    }
    
    init() {
        // Listen for task updates via WebSocket or polling
        this.setupTaskMonitoring();
        
        // Set up UI interactions
        this.setupUIHandlers();
    }
    
    setupTaskMonitoring() {
        // Poll for task status updates
        setInterval(() => {
            this.fetchTaskUpdates();
        }, 5000); // Check every 5 seconds
    }
    
    setupUIHandlers() {
        // Handle floating task icon interactions
        let floatingIcon = document.getElementById('floating-icon');
        if (!floatingIcon) {
            floatingIcon = document.createElement('div');
            floatingIcon.id = 'floating-icon';
            floatingIcon.style.cssText = 'position:fixed;right:24px;bottom:24px;z-index:10002;width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#ffd54f 0%,#ff9800 100%);box-shadow:0 10px 25px rgba(0,0,0,0.2);color:#fff;display:none;align-items:center;justify-content:center;cursor:pointer;';
            const inner = document.createElement('div');
            inner.style.cssText = 'display:flex;align-items:center;gap:6px;';
            inner.innerHTML = '<i class="fas fa-tasks" style="font-size:18px"></i><span class="icon-text" style="font-weight:700;font-size:12px">0</span>';
            floatingIcon.appendChild(inner);
            document.body.appendChild(floatingIcon);
        }
        floatingIcon.addEventListener('click', () => {
            this.showTaskPanel();
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
                floatingIcon.querySelector('.icon-text').textContent = activeTasks.length;
            } else {
                const completedTasks = tasks.filter(task => task.status === 'completed');
                if (completedTasks.length > 0) {
                    floatingIcon.style.display = 'flex';
                    floatingIcon.classList.add('completed');
                    floatingIcon.classList.remove('processing');
                    floatingIcon.querySelector('.icon-text').textContent = '!';
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
        panel.style.display = isHidden ? 'block' : 'none';
    }
    
    createTaskPanel() {
        const panel = document.createElement('div');
        panel.id = 'floating-task-panel';
        panel.className = 'fixed right-20 top-20 w-80 bg-white rounded-lg shadow-xl border border-gray-200';
        panel.style.display = 'none';
        panel.style.zIndex = '10050';
        panel.style.right = '24px';
        panel.style.bottom = '90px';
        
        panel.innerHTML = `
            <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-3 rounded-t-lg">
                <div class="flex justify-between items-center">
                    <h3 class="font-bold">后台任务</h3>
                    <button id="close-task-panel" class="text-white hover:text-gray-200">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div id="tasks-content" class="p-3 max-h-96 overflow-y-auto">
                <div class="text-center py-4 text-gray-500">暂无任务</div>
            </div>
        `;
        
        // Add close button handler
        panel.querySelector('#close-task-panel').addEventListener('click', () => {
            panel.style.display = 'none';
        });
        
        return panel;
    }
    
    populateTaskPanel(panel) {
        const contentDiv = panel.querySelector('#tasks-content');
        
        fetch('/api/tasks')
            .then(response => response.json())
            .then(data => {
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
                                         
                        html += `
                            <div class="task-item border-b border-gray-100 py-2">
                                <div class="font-medium">${task.city} - ${task.industry}</div>
                                <div class="text-sm text-gray-600">${task.llm_service}</div>
                                <div class="text-xs ${statusClass}">${statusText}</div>
                                <div class="flex gap-2 mt-1">
                                    <button onclick="window.location.href='${viewHref}'" 
                                            class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">${viewText}</button>
                                    <button onclick="deleteTask('${task.task_id}')" 
                                            class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">删除</button>
                                </div>
                            </div>
                        `;
                    });
                    contentDiv.innerHTML = html;
                } else {
                    contentDiv.innerHTML = '<div class="text-center py-4 text-gray-500">暂无任务</div>';
                }
            })
            .catch(error => {
                contentDiv.innerHTML = '<div class="text-center py-4 text-red-500">加载失败</div>';
                console.error('Error loading tasks:', error);
            });
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
