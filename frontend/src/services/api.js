import axios from 'axios'

const api = axios.create({
  // On Vercel the Python function is exposed through the /api rewrite in
  // vercel.json. Local development continues to use the FastAPI server.
  baseURL: import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://localhost:8000'),
  timeout: 180000,
})

// FastAPI errors arrive as { detail: "..." } (or a list for validation errors).
export function getErrorMessage(err) {
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  if (err.response?.data?.message) return err.response.data.message
  if (err.code === 'ECONNABORTED') return 'The request timed out. Try a page with fewer images.'
  if (err.message === 'Network Error') return 'Cannot reach the backend. Is the API running on port 8000?'
  return err.message || 'Request failed.'
}

export async function analyzeWebsite(url) {
  const response = await api.post('/analyze/', { url })
  return response.data
}

export async function analyzeImageFile(file) {
  const form = new FormData()
  form.append('file', file)
  const response = await api.post('/analyze/upload', form)
  return response.data
}

export default api
