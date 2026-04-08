// ═══════════════════════════════════════════════════════
// ClaudeFlow Integration Service — SISTEMA180
// Connects the Dashboard UI to the RuFlo V3 Swarm
// ═══════════════════════════════════════════════════════

const SWARM_STATE_PATH = '/.claude-flow/swarm/dashboard-state.json';
const POLL_INTERVAL = 5000; // 5 seconds

let _swarmState = null;
let _listeners = [];
let _pollTimer = null;

// ── Read swarm state from filesystem via fetch ──────────
async function fetchSwarmState() {
  try {
    const res = await fetch(SWARM_STATE_PATH + '?t=' + Date.now());
    if (res.ok) {
      _swarmState = await res.json();
      _listeners.forEach(fn => fn(_swarmState));
    }
  } catch (e) {
    // File not accessible via HTTP — use localStorage fallback
    const cached = localStorage.getItem('s180_swarm_state');
    if (cached) {
      try { _swarmState = JSON.parse(cached); } catch {}
    }
  }
  return _swarmState;
}

// ── Public API ──────────────────────────────────────────

export const claudeflow = {
  /**
   * Get current swarm state
   */
  getState() {
    return _swarmState || {
      swarmStatus: 'unknown',
      totalAgents: 57,
      activeAgents: 0,
      queuedTasks: 0,
      completedTasks: 0,
      agents: {},
      recentActivity: [],
    };
  },

  /**
   * Check if an agent is live in the swarm
   */
  isAgentLive(agentName) {
    if (!_swarmState || !_swarmState.agents) return false;
    const agent = _swarmState.agents[agentName.toLowerCase()];
    return agent && agent.status === 'running';
  },

  /**
   * Get agent runtime info (tasks completed, last active, etc)
   */
  getAgentInfo(agentName) {
    if (!_swarmState || !_swarmState.agents) return null;
    return _swarmState.agents[agentName.toLowerCase()] || null;
  },

  /**
   * Subscribe to state changes
   */
  onStateChange(callback) {
    _listeners.push(callback);
    return () => { _listeners = _listeners.filter(fn => fn !== callback); };
  },

  /**
   * Start polling for swarm state
   */
  startPolling() {
    if (_pollTimer) return;
    fetchSwarmState();
    _pollTimer = setInterval(fetchSwarmState, POLL_INTERVAL);
  },

  /**
   * Stop polling
   */
  stopPolling() {
    if (_pollTimer) {
      clearInterval(_pollTimer);
      _pollTimer = null;
    }
  },

  /**
   * Send a task to an agent via the swarm
   * Writes to the dashboard-state.json pendingTasks array
   */
  async sendTask(agentName, task, priority = 'normal') {
    const taskObj = {
      id: `task-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      agent: agentName,
      task: task,
      priority: priority,
      status: 'queued',
      createdAt: new Date().toISOString(),
    };

    // Store in localStorage for the daemon to pick up
    const pending = JSON.parse(localStorage.getItem('s180_pending_tasks') || '[]');
    pending.push(taskObj);
    localStorage.setItem('s180_pending_tasks', JSON.stringify(pending));

    // Also add to activity feed
    const activity = JSON.parse(localStorage.getItem('s180_agent_activity') || '[]');
    activity.unshift({
      time: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
      msg: `📤 Tarea enviada a ${agentName}: "${task.slice(0, 60)}..."`,
      type: 'task',
      agent: agentName,
    });
    localStorage.setItem('s180_agent_activity', JSON.stringify(activity.slice(0, 50)));

    return taskObj;
  },

  /**
   * Get recent activity from agents
   */
  getRecentActivity() {
    try {
      return JSON.parse(localStorage.getItem('s180_agent_activity') || '[]');
    } catch { return []; }
  },

  /**
   * Update agent status in local state (called from UI or daemon)
   */
  updateAgentStatus(agentName, status, info = {}) {
    if (!_swarmState) _swarmState = this.getState();
    if (!_swarmState.agents) _swarmState.agents = {};
    
    _swarmState.agents[agentName.toLowerCase()] = {
      name: agentName,
      status: status, // 'running', 'idle', 'error', 'building'
      lastActive: new Date().toISOString(),
      ...info,
    };
    
    _swarmState.activeAgents = Object.values(_swarmState.agents)
      .filter(a => a.status === 'running').length;
    _swarmState.lastUpdate = new Date().toISOString();

    localStorage.setItem('s180_swarm_state', JSON.stringify(_swarmState));
    _listeners.forEach(fn => fn(_swarmState));
  },

  /**
   * Execute a ClaudeFlow CLI command (for daemon/relay to pick up)
   */
  queueCommand(command) {
    const cmds = JSON.parse(localStorage.getItem('s180_queued_commands') || '[]');
    cmds.push({
      command,
      timestamp: new Date().toISOString(),
      executed: false,
    });
    localStorage.setItem('s180_queued_commands', JSON.stringify(cmds));
  },
};

// Auto-start polling when imported
claudeflow.startPolling();
