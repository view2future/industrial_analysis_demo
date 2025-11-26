let channel = null;
function initChannel() {
  try { channel = new BroadcastChannel('tasks_channel'); } catch(e) { channel = null; }
}
initChannel();
function broadcast(data) {
  try { if (channel) channel.postMessage(data); } catch(e) {}
  try { postMessage(data); } catch(e) {}
}
async function fetchTasks() {
  try {
    const resp = await fetch('/api/tasks');
    const data = await resp.json();
    broadcast({ type: 'tasks_update', payload: data });
  } catch (e) {
    broadcast({ type: 'tasks_error', error: String(e) });
  }
}
setInterval(fetchTasks, 2000);
fetchTasks();
