// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State Management
let tasks = [];
let currentStrategy = 'smart_balance';

// DOM Elements
const elements = {
    taskForm: document.getElementById('taskForm'),
    taskList: document.getElementById('taskList'),
    taskItems: document.getElementById('taskItems'),
    taskCount: document.getElementById('taskCount'),
    analyzeTasks: document.getElementById('analyzeTasks'),
    getSuggestions: document.getElementById('getSuggestions'),
    clearForm: document.getElementById('clearForm'),
    clearResults: document.getElementById('clearResults'),
    strategy: document.getElementById('strategy'),
    jsonInput: document.getElementById('jsonInput'),
    loadJson: document.getElementById('loadJson'),
    outputSection: document.getElementById('outputSection'),
    resultsContainer: document.getElementById('resultsContainer'),
    loadingIndicator: document.getElementById('loadingIndicator'),
    errorDisplay: document.getElementById('errorDisplay'),
    importance: document.getElementById('importance'),
    importanceRange: document.getElementById('importanceRange')
};

// Initialize App
function init() {
    setupEventListeners();
    setupTabs();
    syncImportanceInputs();
    updateTaskCount();
}

// Setup Event Listeners
function setupEventListeners() {
    elements.taskForm.addEventListener('submit', handleTaskFormSubmit);
    elements.clearForm.addEventListener('click', clearForm);
    elements.analyzeTasks.addEventListener('click', analyzeTasks);
    elements.getSuggestions.addEventListener('click', getSuggestions);
    elements.clearResults.addEventListener('click', clearResults);
    elements.loadJson.addEventListener('click', loadJsonTasks);
    elements.strategy.addEventListener('change', handleStrategyChange);
}

// Setup Tabs
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });
}

// Switch Tab
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update tab contents
    document.getElementById('formTab').classList.toggle('active', tabName === 'form');
    document.getElementById('jsonTab').classList.toggle('active', tabName === 'json');
}

// Sync Importance Inputs
function syncImportanceInputs() {
    elements.importance.addEventListener('input', (e) => {
        elements.importanceRange.value = e.target.value;
    });

    elements.importanceRange.addEventListener('input', (e) => {
        elements.importance.value = e.target.value;
    });
}

// Handle Task Form Submit
function handleTaskFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const task = {
        id: tasks.length,
        title: formData.get('title'),
        due_date: formData.get('dueDate'),
        estimated_hours: parseFloat(formData.get('estimatedHours')),
        importance: parseInt(formData.get('importance')),
        dependencies: parseDependencies(formData.get('dependencies'))
    };

    // Validate task
    if (!validateTask(task)) {
        return;
    }

    // Add task to list
    tasks.push(task);
    renderTaskList();
    updateTaskCount();
    updateAnalyzeButtons();

    // Clear form
    e.target.reset();
    elements.importance.value = 5;
    elements.importanceRange.value = 5;

    showSuccess('Task added successfully!');
}

// Parse Dependencies
function parseDependencies(depString) {
    if (!depString || depString.trim() === '') {
        return [];
    }
    return depString.split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d));
}

// Validate Task
function validateTask(task) {
    if (!task.title || task.title.trim() === '') {
        showError('Task title is required');
        return false;
    }

    if (!task.due_date) {
        showError('Due date is required');
        return false;
    }

    if (task.estimated_hours <= 0) {
        showError('Estimated hours must be greater than 0');
        return false;
    }

    if (task.importance < 1 || task.importance > 10) {
        showError('Importance must be between 1 and 10');
        return false;
    }

    return true;
}

// Clear Form
function clearForm() {
    elements.taskForm.reset();
    elements.importance.value = 5;
    elements.importanceRange.value = 5;
}

// Render Task List
function renderTaskList() {
    if (tasks.length === 0) {
        elements.taskItems.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">No tasks added yet</p>';
        return;
    }

    elements.taskItems.innerHTML = tasks.map((task, index) => `
        <div class="task-item">
            <div class="task-item-info">
                <div class="task-item-title">${escapeHtml(task.title)}</div>
                <div class="task-item-details">
                    Due: ${task.due_date} | ${task.estimated_hours}h | Importance: ${task.importance}/10
                </div>
            </div>
            <button class="task-item-remove" onclick="removeTask(${index})">
                Remove
            </button>
        </div>
    `).join('');
}

// Remove Task
function removeTask(index) {
    tasks.splice(index, 1);
    // Re-index tasks
    tasks.forEach((task, i) => {
        task.id = i;
    });
    renderTaskList();
    updateTaskCount();
    updateAnalyzeButtons();
}

// Load JSON Tasks
function loadJsonTasks() {
    const jsonText = elements.jsonInput.value.trim();

    if (!jsonText) {
        showError('Please paste JSON data');
        return;
    }

    try {
        const jsonTasks = JSON.parse(jsonText);

        if (!Array.isArray(jsonTasks)) {
            showError('JSON must be an array of tasks');
            return;
        }

        // Validate and add tasks
        const validTasks = jsonTasks.filter(task => {
            // Basic validation
            return task.title && task.due_date && task.estimated_hours && task.importance;
        });

        if (validTasks.length === 0) {
            showError('No valid tasks found in JSON');
            return;
        }

        // Add IDs
        validTasks.forEach((task, i) => {
            task.id = tasks.length + i;
            if (!task.dependencies) {
                task.dependencies = [];
            }
        });

        tasks.push(...validTasks);
        renderTaskList();
        updateTaskCount();
        updateAnalyzeButtons();

        // Switch to form tab
        switchTab('form');

        showSuccess(`Loaded ${validTasks.length} tasks from JSON`);
        elements.jsonInput.value = '';

    } catch (error) {
        showError('Invalid JSON format: ' + error.message);
    }
}

// Update Task Count
function updateTaskCount() {
    elements.taskCount.textContent = tasks.length;
}

// Update Analyze Buttons
function updateAnalyzeButtons() {
    const hasTasks = tasks.length > 0;
    elements.analyzeTasks.disabled = !hasTasks;
    elements.getSuggestions.disabled = !hasTasks;
}

// Handle Strategy Change
function handleStrategyChange(e) {
    currentStrategy = e.target.value;
}

// Analyze Tasks
async function analyzeTasks() {
    if (tasks.length === 0) {
        showError('Please add at least one task');
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: currentStrategy
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to analyze tasks');
        }

        const data = await response.json();
        displayResults(data.tasks, 'Analysis Results', data.strategy);

    } catch (error) {
        showError('Error analyzing tasks: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Get Suggestions
async function getSuggestions() {
    if (tasks.length === 0) {
        showError('Please add at least one task');
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/suggest/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: currentStrategy,
                count: 3
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to get suggestions');
        }

        const data = await response.json();
        displayResults(data.suggestions, 'Top 3 Task Suggestions', data.strategy, true);

    } catch (error) {
        showError('Error getting suggestions: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display Results
function displayResults(resultTasks, title, strategy, isSuggestion = false) {
    elements.outputSection.style.display = 'block';
    elements.outputSection.querySelector('h2').textContent = title;

    const strategyNames = {
        'smart_balance': 'Smart Balance',
        'fastest_wins': 'Fastest Wins',
        'high_impact': 'High Impact',
        'deadline_driven': 'Deadline Driven'
    };

    const header = `
        <div style="background: #667eea; color: white; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
            <strong>Strategy Used:</strong> ${strategyNames[strategy]}<br>
            <strong>Tasks Analyzed:</strong> ${resultTasks.length}
        </div>
    `;

    const tasksHtml = resultTasks.map(task => createTaskCard(task, isSuggestion)).join('');

    elements.resultsContainer.innerHTML = header + tasksHtml;

    // Scroll to results
    elements.outputSection.scrollIntoView({ behavior: 'smooth' });
}

// Create Task Card
function createTaskCard(task, isSuggestion) {
    const priorityLevel = getPriorityLevel(task.priority_score);
    const rankBadge = isSuggestion ? `<span class="suggestion-rank">Rank #${task.rank}</span>` : '';
    const warningBadge = task.warning ? `<div class="warning-badge">⚠️ ${task.warning}</div>` : '';

    return `
        <div class="task-card priority-${priorityLevel}">
            <div class="task-card-header">
                <div style="flex: 1;">
                    ${rankBadge ? `<div style="margin-bottom: 10px;">${rankBadge}</div>` : ''}
                    <div class="task-card-title">${escapeHtml(task.title)}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="priority-badge ${priorityLevel}">${priorityLevel.toUpperCase()}</span>
                    <div class="task-card-score">${task.priority_score}</div>
                </div>
            </div>

            <div class="task-card-explanation">
                <strong>Why this score:</strong> ${escapeHtml(task.explanation)}
            </div>

            <div class="task-card-details">
                <div class="detail-item">
                    <span class="detail-label">Due Date</span>
                    <span class="detail-value">${task.due_date}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Estimated Hours</span>
                    <span class="detail-value">${task.estimated_hours}h</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Importance</span>
                    <span class="detail-value">${task.importance}/10</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Dependencies</span>
                    <span class="detail-value">${task.dependencies.length > 0 ? task.dependencies.join(', ') : 'None'}</span>
                </div>
            </div>

            <div class="task-card-components">
                <div class="component-item">
                    <div class="component-label">Urgency</div>
                    <div class="component-value">${task.score_components.urgency}</div>
                </div>
                <div class="component-item">
                    <div class="component-label">Importance</div>
                    <div class="component-value">${task.score_components.importance}</div>
                </div>
                <div class="component-item">
                    <div class="component-label">Effort</div>
                    <div class="component-value">${task.score_components.effort}</div>
                </div>
                <div class="component-item">
                    <div class="component-label">Dependencies</div>
                    <div class="component-value">${task.score_components.dependencies}</div>
                </div>
            </div>

            ${warningBadge}
        </div>
    `;
}

// Get Priority Level
function getPriorityLevel(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

// Clear Results
function clearResults() {
    elements.outputSection.style.display = 'none';
    elements.resultsContainer.innerHTML = '';
}

// Show Loading
function showLoading() {
    elements.loadingIndicator.style.display = 'block';
}

// Hide Loading
function hideLoading() {
    elements.loadingIndicator.style.display = 'none';
}

// Show Error
function showError(message) {
    elements.errorDisplay.textContent = '❌ ' + message;
    elements.errorDisplay.style.display = 'block';
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Hide Error
function hideError() {
    elements.errorDisplay.style.display = 'none';
}

// Show Success
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #26de81;
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 1000;
    `;
    successDiv.textContent = '✓ ' + message;
    document.body.appendChild(successDiv);

    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}