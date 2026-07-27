import axios from 'axios'

const api = axios.create({
  // On Vercel the Python function is exposed through the /api rewrite in
  // vercel.json. Local development continues to use the FastAPI server.
  baseURL: import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://localhost:8000'),
  headers: {
    'Content-Type': 'application/json'
  }
})

export async function analyzeWebsite(url) {
  const response = await api.post('/analyze/', { url })
  return response.data
}

export default api
