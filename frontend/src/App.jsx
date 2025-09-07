import React, { useState, useEffect } from 'react'
import { predictURL, fetchMetrics } from './api'
import FeatureHighlights from './components/FeatureHighlights'
import Dashboard from './components/Dashboard'

export default function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [error, setError] = useState('')

  async function refreshMetrics() {
    try {
      const m = await fetchMetrics()
      setMetrics(m)
    } catch (e) {
      // ignore
    }
  }

  useEffect(() => { refreshMetrics() }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const res = await predictURL(url)
      setResult(res)
      setUrl('')
      refreshMetrics()
    } catch (e) {
      console.error(e)
      setError('Failed to get prediction. Is the backend running on :8000?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',              
        display: 'flex',                 
        alignItems: 'center',            
        justifyContent: 'center',        
        background: '#0a0f1e'           
      }}
    >
      <div
        style={{
          maxWidth: 900,
          width: '100%',
          padding: '24px 16px',
          border: '2px solid #4f46e5',  
          borderRadius: '16px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          background: '#0f172a'
        }}
      >
        <header style={{display:'flex', alignItems:'center', gap:12,justifyContent:'center'}}>
          <div style={{fontSize:28,}}>Enter the URL</div>
          <div style={{opacity:.7}}></div>
        </header>

        <form 
          onSubmit={onSubmit} 
          style={{
            display:'flex', 
            flexDirection:'column', 
            gap:12, 
            marginTop:16, 
            alignItems:'center'
          }}
        >
          <input
            type="url"
            value={url}
            onChange={(e)=>setUrl(e.target.value)}
            placeholder=" e.g. http://google.com"
            required
            style={{
              flex:1,
              width:'80%',        
              maxWidth:'800px',    
              padding:'14px 16px',
              borderRadius:12,
              border:'1px solid #1e2748',
              background:'#121933',
              color:'#e7eaf6',
              fontSize:'18px'
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              padding:'14px 18px',
              borderRadius:12,
              border:'none',
              background:'#4f46e5',
              color:'white',
              cursor:'pointer',
              opacity:loading?0.7:1}}
          >
            {loading ? 'Checking…' : 'Check URL'}
          </button>
        </form>

        {error && <div style={{marginTop:12, background:'#401b1b', color:'#ffd8d8', padding:12, borderRadius:12}}>{error}</div>}

        {result && (
          <div style={{marginTop:16, background:'#121933', padding:16, borderRadius:16}}>
            <div style={{display:'flex', alignItems:'center', gap:8}}>
              <div style={{fontSize:22}}>{result.pred_label === 'phishing' ? '❌ Phishing' : '✅ Safe'}</div>
              <div style={{opacity:.8}}>Confidence: {(result.pred_proba*100).toFixed(1)}%</div>
            </div>
            <div style={{marginTop:8, fontSize:14, opacity:.85}}>
              Model thinks this because it found signals in the URL's structure and content.
            </div>
          </div>
        )}

        <Dashboard metrics={metrics} />
      </div>
    </div>
  )
}
