import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL|| 'http://localhost:8000'

export async function predictURL(url) {
  const res = await axios.post(`${BASE_URL}/predict`, { url })
  return res.data
}

export async function fetchMetrics() {
  const res = await axios.get(`${BASE_URL}/metrics`)
  return res.data
}
