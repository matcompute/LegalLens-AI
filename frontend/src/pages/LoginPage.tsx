import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { Scale } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isRegister) {
        await api.post('/auth/register', { email, password, full_name: email.split('@')[0] });
      }
      
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const res = await api.post('/auth/login', formData);
      localStorage.setItem('token', res.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      alert("Authentication failed");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <Scale size={48} color="var(--accent-gold)" />
          <h1 style={{ marginTop: '16px' }}>LegalLens AI</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Enterprise Contract Intelligence</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <input type="email" placeholder="Work Email" value={email} onChange={e => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '16px', padding: '12px' }}>
            {isRegister ? 'Create Account' : 'Sign In'}
          </button>
        </form>
        
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <span style={{ color: 'var(--text-secondary)', cursor: 'pointer' }} onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
          </span>
        </div>
      </div>
    </div>
  );
}
