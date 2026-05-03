import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { ArrowLeft, Send, ShieldAlert, Bot } from 'lucide-react';

export default function WorkspacePage() {
  const { contractId } = useParams();
  const navigate = useNavigate();
  const [contract, setContract] = useState<any>(null);
  const [tab, setTab] = useState<'chat' | 'risks'>('risks');
  const [message, setMessage] = useState('');
  const [chats, setChats] = useState<any[]>([]);
  const [loadingChat, setLoadingChat] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchContract = async () => {
      try {
        const res = await api.get(`/contracts/${contractId}`);
        setContract(res.data);
        setChats(res.data.chats || []);
      } catch (err) {
        navigate('/dashboard');
      }
    };
    fetchContract();
  }, [contractId, navigate]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chats]);

  const handleSend = async () => {
    if (!message.trim()) return;
    const userMsg = message;
    setMessage('');
    
    // Optimistic UI update
    const tempId = Date.now();
    setChats(prev => [...prev, { id: tempId, user_message: userMsg, ai_response: '...' }]);
    setLoadingChat(true);
    
    try {
      const res = await api.post(`/contracts/${contractId}/chat`, { message: userMsg });
      setChats(prev => prev.map(c => c.id === tempId ? res.data : c));
    } catch (err) {
      setChats(prev => prev.filter(c => c.id !== tempId));
      alert("Chat failed");
    } finally {
      setLoadingChat(false);
    }
  };

  if (!contract) return <div style={{ padding: '40px', color: 'var(--text-secondary)' }}>Loading Workspace...</div>;

  const getSeverityColor = (sev: str) => {
    if (sev === 'High') return 'risk-high';
    if (sev === 'Medium') return 'risk-medium';
    return 'risk-low';
  };

  return (
    <div className="app-container">
      <div className="dashboard-nav" style={{ padding: '10px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button className="btn" style={{ padding: '4px 8px' }} onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={16} />
          </button>
          <h3 style={{ margin: 0 }}>{contract.title}</h3>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Status: {contract.status}
          </span>
        </div>
      </div>

      <div className="workspace">
        <div className="pdf-pane">
          <iframe 
            src={`http://localhost:8001/api/uploads/${contract.file_path}`} 
            style={{ width: '100%', height: '100%', border: 'none' }}
            title="Contract PDF"
          />
        </div>

        <div className="chat-pane">
          <div className="chat-tabs">
            <div className={`chat-tab ${tab === 'risks' ? 'active' : ''}`} onClick={() => setTab('risks')}>
              <ShieldAlert size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'text-bottom' }} />
              Automated Risks
            </div>
            <div className={`chat-tab ${tab === 'chat' ? 'active' : ''}`} onClick={() => setTab('chat')}>
              <Bot size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'text-bottom' }} />
              AI Assistant
            </div>
          </div>

          <div className="chat-history">
            {tab === 'risks' && (
              <div>
                {contract.status !== 'indexed' ? (
                  <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '40px' }}>
                    Contract is still being processed and indexed. Check back in a moment.
                  </p>
                ) : contract.risks?.length === 0 ? (
                  <p style={{ color: 'var(--success)', textAlign: 'center', marginTop: '40px' }}>
                    No significant risks detected in this contract.
                  </p>
                ) : (
                  contract.risks?.map((r: any) => (
                    <div key={r.id} className={`risk-card ${getSeverityColor(r.severity)}`}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <strong style={{ color: 'var(--text-primary)' }}>{r.category}</strong>
                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{r.severity} Severity</span>
                      </div>
                      <p style={{ fontSize: '14px', marginBottom: '12px', color: 'var(--text-secondary)' }}>{r.explanation}</p>
                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '4px', fontSize: '12px', fontStyle: 'italic', borderLeft: '2px solid var(--text-secondary)' }}>
                        "{r.clause_text}"
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {tab === 'chat' && (
              <div>
                {chats.length === 0 && (
                  <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '40px' }}>
                    Ask me anything about this contract (e.g., "What is the termination period?")
                  </p>
                )}
                {chats.map(c => (
                  <div key={c.id}>
                    <div className="message msg-user">{c.user_message}</div>
                    <div className="message msg-ai">
                      <div style={{ marginBottom: '8px' }} dangerouslySetInnerHTML={{ __html: c.ai_response.replace(/\n/g, '<br/>') }} />
                      {c.citations && c.citations !== '[]' && (
                        <div style={{ marginTop: '12px', borderTop: '1px solid var(--border-color)', paddingTop: '8px' }}>
                          <span style={{ fontSize: '12px', color: 'var(--accent-gold)' }}>Citations:</span>
                          {JSON.parse(c.citations).map((cit: any, idx: number) => (
                            <div key={idx} style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px', background: 'rgba(0,0,0,0.2)', padding: '4px', borderRadius: '4px' }}>
                              Pg {cit.page}: "{cit.text}"
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            )}
          </div>

          {tab === 'chat' && (
            <div className="chat-input">
              <div style={{ display: 'flex', gap: '10px' }}>
                <input 
                  value={message} 
                  onChange={e => setMessage(e.target.value)} 
                  onKeyPress={e => e.key === 'Enter' && handleSend()}
                  placeholder="Ask a question..."
                  style={{ marginBottom: 0 }}
                  disabled={loadingChat || contract.status !== 'indexed'}
                />
                <button className="btn btn-primary" onClick={handleSend} disabled={loadingChat || contract.status !== 'indexed' || !message.trim()}>
                  <Send size={18} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
