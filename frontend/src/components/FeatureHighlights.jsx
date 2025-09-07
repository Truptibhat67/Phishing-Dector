import React from 'react'

export default function FeatureHighlights({ contributors }) {
  if (!contributors || contributors.length === 0) return null
  return (
    <div style={{background:'#121933', padding:'12px 16px', borderRadius:16, marginTop:12}}>
      <div style={{fontSize:14, opacity:.8, marginBottom:8}}>Top contributing features</div>
      <ul style={{margin:0, paddingLeft:18}}>
        {contributors.map((c, idx) => (
          <li key={idx} style={{marginBottom:6}}>
            <code style={{background:'#0b1020', padding:'2px 6px', borderRadius:8, fontSize:12}}>{c.feature}</code>
            {" "}value: <strong>{typeof c.value === 'number' ? c.value.toFixed(3) : String(c.value)}</strong>
            {" "} | logit Δ: <strong>{c.logit_contribution.toFixed(3)}</strong>
          </li>
        ))}
      </ul>
    </div>
  )
}
