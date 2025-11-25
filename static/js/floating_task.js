/**
 * Floating Task Manager
 * Manages background report generation tasks with floating icon and panel UI
 */

(function() {
    'use strict';
    
    // Global state
    window.backgroundTasks = window.backgroundTasks || [];
    let floatingPanel = null;
    let pollIntervals = {};
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        initFloatingIcon();
        restoreBackgroundTasks();
    });
    
    /**
     * Initialize floating icon if not exists
     */
    function initFloatingIcon() {
        if (document.getElementById('floating-task-icon')) {
            return; // Already exists
        }
        
        const icon = document.createElement('div');
        icon.id = 'floating-task-icon';
        icon.className = 'floating-task-icon';
        icon.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 68px;
            height: 68px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 20px rgba(255,193,7,0.4);
            cursor: pointer;
            z-index: 10000;
            display: none;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        `;
        
        icon.innerHTML = `
            <div class="icon-content" style="position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
                <div class="icon-spinner" style="
                    display: none;
                    width: 32px;
                    height: 32px;
                    border: 3px solid rgba(255,255,255,0.3);
                    border-radius: 50%;
                    border-top-color: white;
                    animation: spin 1s linear infinite;
                "></div>
                <i class="fas fa-tasks icon-symbol" style="font-size: 26px; display: none;"></i>
                <div class="task-badge" style="
                    position: absolute;
                    top: -2px;
                    right: -2px;
                    min-width: 22px;
                    height: 22px;
                    background: #dc3545;
                    border-radius: 11px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 6px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    border: 2px solid white;
                ">0</div>
            </div>
        `;
        
        icon.onclick = toggleFloatingPanel;
        document.body.appendChild(icon);
        
        // Add animation keyframes if not exists
        if (!document.getElementById('floating-task-styles')) {
            const style = document.createElement('style');
            style.id = 'floating-task-styles';
            style.textContent = `
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                .floating-task-icon:hover {
                    transform: scale(1.1) rotate(5deg);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.4), 0 0 30px rgba(255,193,7,0.6);
                }
                .floating-task-icon.completed {
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 20px rgba(40,167,69,0.4);
                }
                .floating-task-icon.completed:hover {
                    box-shadow: 0 6px 20px rgba(0,0,0,0.4), 0 0 30px rgba(40,167,69,0.6);
                }
                .floating-task-icon.processing .icon-spinner {
                    display: block !important;
                }
                .floating-task-icon.processing .icon-symbol {
                    display: none !important;
                }
                .floating-task-icon:not(.processing) .icon-spinner {
                    display: none !important;
                }
                .floating-task-icon:not(.processing) .icon-symbol {
                    display: block !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    /**
     * Show floating icon
     */
    function showFloatingIcon(isProcessing = true) {
        const icon = document.getElementById('floating-task-icon');
        if (icon) {
            icon.style.display = 'flex';
            updateFloatingIconStatus(isProcessing);
            updateTaskBadge();
        }
    }
    
    /**
     * Hide floating icon
     */
    function hideFloatingIcon() {
        const icon = document.getElementById('floating-task-icon');
        if (icon) {
            icon.style.display = 'none';
        }
    }
    
    /**
     * Update floating icon status
     * @param {boolean} isProcessing - true for yellow/processing, false for green/completed
     */
    function updateFloatingIconStatus(isProcessing) {
        const icon = document.getElementById('floating-task-icon');
        if (!icon) return;
        
        if (isProcessing) {
            icon.classList.add('processing');
            icon.classList.remove('completed');
        } else {
            icon.classList.remove('processing');
            icon.classList.add('completed');
        }
        updateTaskBadge();
    }
    
    /**
     * Update task badge count
     */
    function updateTaskBadge() {
        const badge = document.querySelector('.task-badge');
        if (!badge) return;
        
        const taskCount = window.backgroundTasks.length;
        badge.textContent = taskCount;
        badge.style.display = taskCount > 0 ? 'flex' : 'none';
    }
    
    /**
     * Toggle floating panel visibility
     */
    function toggleFloatingPanel() {
        if (floatingPanel && floatingPanel.style.display !== 'none') {
            closeFloatingPanel();
        } else {
            openFloatingPanel();
        }
    }
    
    /**
     * Open floating panel
     */
    function openFloatingPanel() {
        if (!floatingPanel) {
            createFloatingPanel();
        }
        
        floatingPanel.style.display = 'flex';
        updateFloatingPanelContent();
    }
    
    /**
     * Close floating panel
     */
    function closeFloatingPanel() {
        if (floatingPanel) {
            floatingPanel.style.display = 'none';
        }
    }
    
    /**
     * Create floating panel DOM
     */
    function createFloatingPanel() {
        floatingPanel = document.createElement('div');
        floatingPanel.id = 'floating-task-panel';
        floatingPanel.style.cssText = `
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 450px;
            height: 650px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            z-index: 9999;
            display: none;
            flex-direction: column;
            overflow: hidden;
        `;
        
        floatingPanel.innerHTML = `
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <h5 style="margin: 0; font-size: 16px;">
                    <i class="bi bi-gear-fill me-2"></i>报告生成任务
                </h5>
                <div>
                    <button id="clear-all-tasks" title="清空任务" style="
                        background: transparent;
                        border: none;
                        color: white;
                        font-size: 18px;
                        cursor: pointer;
                        padding: 0 12px 0 0;
                        line-height: 1;
                    "><i class="bi bi-trash"></i></button>
                    <button onclick="window.closeFloatingPanel()" style="
                        background: transparent;
                        border: none;
                        color: white;
                        font-size: 20px;
                        cursor: pointer;
                        padding: 0;
                        line-height: 1;
                    ">&times;</button>
                </div>
            </div>
            <div style="flex: 1; overflow-y: auto; padding: 15px;" id="floating-task-list">
                <p style="text-align: center; color: #666; margin-top: 50px;">暂无任务</p>
            </div>
        `;
        
        document.body.appendChild(floatingPanel);

        // Bind clear-all action: remove all tasks immediately without confirmation
        const clearBtn = document.getElementById('clear-all-tasks');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                window.backgroundTasks = [];
                saveBackgroundTasks();
                updateTaskBadge();
                hideFloatingIcon();
                updateFloatingPanelContent();
            });
        }
    }
    
    /**
     * Update floating panel content with task list
     */
    function updateFloatingPanelContent() {
        const taskList = document.getElementById('floating-task-list');
        if (!taskList) return;
        
        if (window.backgroundTasks.length === 0) {
            taskList.innerHTML = '<p style="text-align: center; color: #666; margin-top: 50px;">暂无任务</p>';
            return;
        }
        
        let html = '';
        window.backgroundTasks.forEach((task, index) => {
            const duration = Math.floor((Date.now() - task.startTime) / 1000);
            const statusText = task.reportId ? '已完成' : (task.status || '处理中');
            const statusClass = task.reportId ? 'success' : 'warning';
            const stageText = getStageText(task.stage || 'init');
            
            html += `
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 12px;
                    background: ${task.reportId ? '#f8f9fa' : '#fff'};
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <strong style="font-size: 14px;">任务 #${index + 1}</strong>
                        <span class="badge bg-${statusClass}" style="font-size: 11px;">${statusText}</span>
                    </div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 6px;">
                        <i class="bi bi-geo-alt"></i> ${task.city || '未知'} - ${task.industry || '未知'}
                    </div>
                    <div style="font-size: 11px; color: #999; margin-bottom: 8px;">
                        <i class="bi bi-clock"></i> 用时: ${duration}秒 | 
                        <i class="bi bi-activity"></i> ${stageText}
                    </div>
                    ${task.reportId ? `
                        <button onclick="window.location.href='/report/${task.reportId}'" 
                            class="btn btn-sm btn-primary" style="width: 100%; font-size: 12px;">
                            <i class="bi bi-eye"></i> 查看报告
                        </button>
                    ` : `
                        <div class="mb-2">
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                    role="progressbar" style="width: ${getStageProgress(task.stage)}%"></div>
                            </div>
                        </div>
                        <button onclick="window.location.href='/stream-report/${task.taskId}?city=${encodeURIComponent(task.city || '')}&industry=${encodeURIComponent(task.industry || '')}&llm_service=kimi'" 
                            class="btn btn-sm btn-success" style="width: 100%; font-size: 12px;">
                            <i class="bi bi-arrow-return-left"></i> 返回生成页面
                        </button>
                    `}
                </div>
            `;
        });
        
        taskList.innerHTML = html;
    }
    
    /**
     * Get human-readable stage text
     */
    function getStageText(stage) {
        const stageMap = {
            'init': '初始化',
            'outline': '生成大纲',
            'generation': '生成内容',
            'analysis': '分析数据',
            'finalize': '完成报告',
            'completed': '已完成'
        };
        return stageMap[stage] || '处理中';
    }
    
    /**
     * Get progress percentage by stage
     */
    function getStageProgress(stage) {
        const progressMap = {
            'init': 10,
            'outline': 30,
            'generation': 60,
            'analysis': 85,
            'finalize': 95,
            'completed': 100
        };
        return progressMap[stage] || 20;
    }
    
    /**
     * Add a new background task
     */
    function addBackgroundTask(taskId, city, industry) {
        const existing = window.backgroundTasks.find(t => t.taskId === taskId);
        if (existing) {
            existing.city = city || existing.city;
            existing.industry = industry || existing.industry;
            existing.status = existing.status || 'processing';
            saveBackgroundTasks();
            showFloatingIcon(true);
            updateTaskBadge();
            if (!pollIntervals[taskId]) startTaskPolling(taskId);
            return existing;
        }
        const task = {
            taskId: taskId,
            city: city,
            industry: industry,
            startTime: Date.now(),
            reportId: null,
            status: 'processing',
            stage: 'init'
        };
        window.backgroundTasks.push(task);
        saveBackgroundTasks();
        showFloatingIcon(true);
        updateTaskBadge();
        startTaskPolling(taskId);
        return task;
    }

    /**
     * Add a background task without backend polling (for local streaming tasks)
     */
    function addLocalBackgroundTask(taskId, city, industry) {
        const existing = window.backgroundTasks.find(t => t.taskId === taskId);
        if (existing) {
            existing.city = city || existing.city;
            existing.industry = industry || existing.industry;
            existing.status = existing.status || 'processing';
            existing.stage = existing.stage || 'generation';
            saveBackgroundTasks();
            showFloatingIcon(true);
            updateTaskBadge();
            return existing;
        }
        const task = {
            taskId: taskId,
            city: city,
            industry: industry,
            startTime: Date.now(),
            reportId: null,
            status: 'processing',
            stage: 'generation'
        };
        window.backgroundTasks.push(task);
        saveBackgroundTasks();
        showFloatingIcon(true);
        updateTaskBadge();
        return task;
    }
    
    /**
     * Start polling for task status
     */
    function startTaskPolling(taskId) {
        if (pollIntervals[taskId]) {
            clearInterval(pollIntervals[taskId]);
        }
        
        pollIntervals[taskId] = setInterval(async () => {
            try {
                const response = await fetch(`/api/task-status/${taskId}`);
                const data = await response.json();
                
                // Update task in list
                const task = window.backgroundTasks.find(t => t.taskId === taskId);
                if (!task) {
                    clearInterval(pollIntervals[taskId]);
                    return;
                }
                
                const state = (data.state || '').toUpperCase();
                const status = (data.status || '').toLowerCase();
                
                // Update stage
                if (data.info && data.info.current_step) {
                    task.stage = mapStepToStage(data.info.current_step);
                }
                
                // Handle completion
                if (state === 'SUCCESS' || status === 'completed') {
                    task.status = 'completed';
                    task.stage = 'completed';
                    task.reportId = data.result?.report_id || data.report_id;
                    
                    clearInterval(pollIntervals[taskId]);
                    saveBackgroundTasks();
                    
                    // Check if all tasks are completed
                    const hasProcessing = window.backgroundTasks.some(t => !t.reportId);
                    updateFloatingIconStatus(!hasProcessing);
                    updateTaskBadge();
                    
                    // Update panel if open
                    if (floatingPanel && floatingPanel.style.display !== 'none') {
                        updateFloatingPanelContent();
                    }
                }
                
                // Handle failure
                if (state === 'FAILURE' || state === 'REVOKED' || status === 'failed') {
                    task.status = 'failed';
                    clearInterval(pollIntervals[taskId]);
                    saveBackgroundTasks();
                    
                    if (floatingPanel && floatingPanel.style.display !== 'none') {
                        updateFloatingPanelContent();
                    }
                }
                
                // Update panel if open
                if (floatingPanel && floatingPanel.style.display !== 'none') {
                    updateFloatingPanelContent();
                }
                
            } catch (error) {
                console.error('Error polling task status:', error);
            }
        }, 2000);
    }
    
    /**
     * Map backend step to stage
     */
    function mapStepToStage(step) {
        if (step <= 1) return 'init';
        if (step === 2) return 'outline';
        if (step === 3) return 'generation';
        if (step === 4) return 'analysis';
        if (step === 5) return 'finalize';
        return 'generation';
    }
    
    /**
     * Save background tasks to localStorage
     */
    function saveBackgroundTasks() {
        try {
            localStorage.setItem('backgroundTasks', JSON.stringify(window.backgroundTasks));
        } catch (e) {
            console.error('Error saving background tasks:', e);
        }
    }
    
    /**
     * Restore background tasks from localStorage
     */
    function restoreBackgroundTasks() {
        try {
            const saved = localStorage.getItem('backgroundTasks');
            if (saved) {
                window.backgroundTasks = JSON.parse(saved);
                
                // Restart polling for incomplete tasks
                window.backgroundTasks.forEach(task => {
                    if (!task.reportId && task.taskId) {
                        startTaskPolling(task.taskId);
                    }
                });
                
                // Show icon if there are tasks
                if (window.backgroundTasks.length > 0) {
                    const hasProcessing = window.backgroundTasks.some(t => !t.reportId);
                    showFloatingIcon(hasProcessing);
                }
            }
        } catch (e) {
            console.error('Error restoring background tasks:', e);
        }
    }
    
    /**
     * Clear all completed tasks
     */
    function clearCompletedTasks() {
        window.backgroundTasks = window.backgroundTasks.filter(t => !t.reportId);
        saveBackgroundTasks();
        
        if (window.backgroundTasks.length === 0) {
            hideFloatingIcon();
            closeFloatingPanel();
        } else {
            updateFloatingPanelContent();
        }
    }
    
    // Expose functions to global scope
    window.showFloatingIcon = showFloatingIcon;
    window.hideFloatingIcon = hideFloatingIcon;
    window.updateFloatingIconStatus = updateFloatingIconStatus;
    window.addBackgroundTask = addBackgroundTask;
    window.addLocalBackgroundTask = addLocalBackgroundTask;
    window.openFloatingPanel = openFloatingPanel;
    window.closeFloatingPanel = closeFloatingPanel;
    window.clearCompletedTasks = clearCompletedTasks;
    
})();
