import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { FileText, Upload, Scale, Clock } from 'lucide-react';

export default function DashboardPage() {
  const [contracts, setContracts] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const fetchContracts = async () => {
    const res = await api.get('/contracts');
    setContracts(res.data);
  };

  useEffect(() => {
    fetchContracts();
    const interval = setInterval(fetchContracts, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name);

    try {
      await api.post('/contracts/upload', formData);
      fetchContracts();
    } catch (err) {
      alert("Failed to upload contract");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="dashboard-nav">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Scale color="var(--accent-gold)" />
          <h2 style={{ margin: 0 }}>LegalLens</h2>
        </div>
        <button className="btn btn-primary" onClick={() => fileRef.current?.click()} disabled={uploading}>
          <Upload size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} />
          {uploading ? 'Uploading...' : 'Upload Contract'}
        </button>
        <input type="file" accept=".pdf" ref={fileRef} hidden onChange={handleUpload} />
      </div>

      <div className="dashboard-container">
        <h1 style={{ marginBottom: '8px' }}>Contract Portfolio</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Manage and analyze your legal documents</p>

        <div className="contract-grid">
          {contracts.map(c => (
            <div key={c.id} className="contract-card" onClick={() => navigate(`/workspace/${c.id}`)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                <FileText color="var(--accent-gold)" size={24} />
                <span style={{ 
                  fontSize: '12px', padding: '4px 8px', borderRadius: '12px',
                  background: c.status === 'indexed' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                  color: c.status === 'indexed' ? 'var(--success)' : 'var(--danger)'
                }}>
                  {c.status.toUpperCase()}
                </span>
              </div>
              <h3 style={{ fontSize: '16px', marginBottom: '8px', wordBreak: 'break-word' }}>{c.title}</h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                <Clock size={12} />
                {new Date(c.upload_date).toLocaleDateString()}
              </div>
            </div>
          ))}
          {contracts.length === 0 && !uploading && (
            <div style={{ color: 'var(--text-secondary)', padding: '40px', border: '1px dashed var(--border-color)', borderRadius: '8px', textAlign: 'center', gridColumn: '1 / -1' }}>
              No contracts found. Upload a PDF to begin.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
