import axios from 'axios'
const api = axios.create({ baseURL: '/api/v1', timeout: 60000 })

// Add auth token to requests
api.interceptors.request.use(config => {
  const token = sessionStorage.getItem('auth_token')
  if (token && token !== 'undefined' && token !== 'null') {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('auth_token')
      // Use window.location for full page redirect to ensure clean state
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const fetchSources = (params?: Record<string, unknown>) =>
  api.get('/sources/', { params }).then(r => r.data.data)
export const fetchSource = (id: number) =>
  api.get(`/sources/${id}`).then(r => r.data.data)
export const createSource = (data: Record<string, unknown>) =>
  api.post('/sources/', data).then(r => r.data)
export const updateSource = (id: number, data: Record<string, unknown>) =>
  api.patch(`/sources/${id}`, data).then(r => r.data)
export const deleteSource = (id: number) =>
  api.delete(`/sources/${id}`).then(r => r.data)
export const likeSource = (id: number) =>
  api.post(`/sources/${id}/like`).then(r => r.data.data)

// Files
export const fetchFiles = (sourceId: number) =>
  api.get(`/files/list/${sourceId}`).then(r => r.data.data)
export const uploadFile = (sourceId: number, file: File) => {
  const form = new FormData(); form.append('file', file)
  return api.post(`/files/upload/${sourceId}`, form).then(r => r.data)
}
export const getDownloadUrl = (fileId: number) =>
  `/api/v1/files/${fileId}/download`
export const getFilePreview = (fileId: number) =>
  api.get(`/files/${fileId}/preview`).then(r => r.data.data)
export const deleteFile = (fileId: number) =>
  api.delete(`/files/${fileId}`).then(r => r.data)

export const fetchLogs = (params?: Record<string, unknown>) =>
  api.get('/logs/', { params }).then(r => r.data.data)
export const login = (username: string, password: string) =>
  api.post('/auth/login', { username, password }).then(r => r.data.data)
export const getMe = () =>
  api.get('/auth/me').then(r => r.data.data)
export const fetchUsers = (params?: Record<string, unknown>) =>
  api.get('/users/', { params }).then(r => r.data.data)
export const createUser = (data: Record<string, unknown>) =>
  api.post('/users/', data).then(r => r.data)
export const updateUser = (id: number, data: Record<string, unknown>) =>
  api.patch(`/users/${id}`, data).then(r => r.data)
export const deleteUser = (id: number) =>
  api.delete(`/users/${id}`).then(r => r.data)
export const healthCheck = () =>
  api.get('/health', { baseURL: '' }).then(r => r.data)