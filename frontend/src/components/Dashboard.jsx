import React from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Dashboard({ metrics }) {
  const data = [
    { name: 'Phishing', value: metrics?.phishing || 0 },
    { name: 'Safe', value: metrics?.legit || 0 }
  ]

  const Colors=["#ef4444","#22c55e"];
  return (
     <div style={{background:'#121933', padding:16, borderRadius:16, marginTop:16}}>
      <div style={{textAlign:'center', marginBottom:8}}>
        <h3 style={{margin:0, fontSize:16}}>Predictions so far</h3>
        <small style={{opacity:.7}}>Total: {metrics?.total || 0}</small>
      </div>
      <div style={{width:'100%', height:220}}>
        <ResponsiveContainer>
          <PieChart>
            <Pie dataKey="value" data={data} nameKey="name" outerRadius={80} label  >
             {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={Colors[index % Colors.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
      
    </div>
  )
}
