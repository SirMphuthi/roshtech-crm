import React, { useState, useEffect } from 'react';
import TaskModal from '../components/Tasks/TaskModal';
import '../components/Contacts/ContactModal.css';

const BACKEND_API = 'http://localhost:5000';

const TasksPage = () => {
  const [tasks, setTasks] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [taskToEdit, setTaskToEdit] = useState(null);

  const fetchTasks = () => {
    fetch(`${BACKEND_API}/api/tasks`)
      .then(res => res.json())
      .then(data => {
        if (data.items) setTasks(data.items);
        else setTasks([]);
      })
      .catch(err => console.error('Failed to fetch tasks:', err));
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleStatusChange = async (task) => {
    const updatedStatus = task.status === 'Completed' ? 'Pending' : 'Completed';
    const res = await fetch(`${BACKEND_API}/api/tasks/${task.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: updatedStatus }),
    });
    if (res.ok) {
      fetchTasks();
    } else {
      alert('Failed to update task status');
    }
  };

  return (
    <div className="tasks-page">
      <h1 className="page-title">Tasks</h1>
      <button
        className="add-task-btn"
        onClick={() => {
          setIsModalOpen(true);
          setTaskToEdit(null);
        }}
        style={{ marginBottom: '1rem' }}
      >
        Add Task
      </button>
      <table className="tasks-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Task Name</th>
            <th>Due Date</th>
            <th>Priority</th>
            <th>Related To</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {tasks.length === 0 ? (
            <tr><td colSpan={6}>No tasks found.</td></tr>
          ) : (
            tasks.map(task => (
              <tr key={task.id} style={task.status === 'Completed' ? { color: '#888', textDecoration: 'line-through' } : {}}>
                <td>
                  <input
                    type="checkbox"
                    checked={task.status === 'Completed'}
                    onChange={() => handleStatusChange(task)}
                  />
                </td>
                <td>{task.name}</td>
                <td>{task.due_date}</td>
                <td>{task.priority}</td>
                <td>{task.related_to}</td>
                <td>
                  <button onClick={() => { setTaskToEdit(task); setIsModalOpen(true); }}>Edit</button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        taskToEdit={taskToEdit}
        onSave={fetchTasks}
      />
    </div>
  );
};

export default TasksPage;