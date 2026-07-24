import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

export async function analyzeWebsite(url) {
  const response = await api.post('/analyze/', { url })
  return response.data
}

export default api
