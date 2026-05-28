import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface Job {
  job_id: string;
  name: string;
  interval_seconds: number;
  task_type: string;
  enabled: boolean;
  run_count: number;
  last_run: number | null;
  next_run: number | null;
}

export function AdminSchedulerPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [intervalSec, setIntervalSec] = useState('3600');
  const [taskType, setTaskType] = useState('report_generation');

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await api.get('/admin/scheduler/jobs');
      setJobs(Array.isArray(res.data) ? res.data : []);
    } catch (err: any) {
      setError(err.message || 'Failed to load scheduler jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchJobs(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/admin/scheduler/jobs', { name, interval_seconds: parseInt(intervalSec), task_type: taskType });
      setName('');
      setIntervalSec('3600');
      await fetchJobs();
    } catch (err: any) {
      setError(err.message || 'Failed to add job');
    }
  };

  const handleDelete = async (jobId: string) => {
    try {
      await api.delete(`/admin/scheduler/jobs/${jobId}`);
      await fetchJobs();
    } catch (err: any) {
      setError(err.message || 'Failed to delete job');
    }
  };

  if (loading) return <LoadingSpinner text="Loading scheduler..." />;

  return (
    <div className="page admin-page">
      <h2>Scheduled Reports</h2>
      {error && <p className="page-error">{error}</p>}

      <form className="webhook-form" onSubmit={handleAdd}>
        <h3>Add Scheduled Job</h3>
        <div className="detail-row">
          <span className="detail-label">Name</span>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
        </div>
        <div className="detail-row">
          <span className="detail-label">Interval (sec)</span>
          <input type="number" value={intervalSec} onChange={(e) => setIntervalSec(e.target.value)} required />
        </div>
        <div className="detail-row">
          <span className="detail-label">Task Type</span>
          <select value={taskType} onChange={(e) => setTaskType(e.target.value)}>
            <option value="report_generation">Report Generation</option>
            <option value="cache_warmup">Cache Warmup</option>
          </select>
        </div>
        <button type="submit" className="btn-generate">Add Job</button>
      </form>

      <table className="reports-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Interval</th>
            <th>Runs</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.job_id}>
              <td>{job.name}</td>
              <td>{job.task_type}</td>
              <td>{job.interval_seconds}s</td>
              <td>{job.run_count}</td>
              <td>
                <span className="status-badge" style={{ backgroundColor: job.enabled ? '#4caf50' : '#f44336' }}>
                  {job.enabled ? 'Active' : 'Paused'}
                </span>
              </td>
              <td>
                <button className="btn-delete" onClick={() => handleDelete(job.job_id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {jobs.length === 0 && <p className="empty-state">No scheduled jobs.</p>}
    </div>
  );
}
