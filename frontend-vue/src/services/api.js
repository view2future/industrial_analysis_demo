import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api', // 通过vite代理配置，/api请求将转发到http://localhost:5000/api
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response?.status === 401) {
      // 如果是认证错误，重定向到登录页面
      localStorage.removeItem('token')
      localStorage.removeItem('isLoggedIn')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关API
export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  logout: () => apiClient.post('/auth/logout'),
  getCurrentUser: () => apiClient.get('/auth/me')
}

// 仪表板相关API
export const dashboardAPI = {
  getStats: () => apiClient.get('/dashboard/stats')
}

// 报告相关API
export const reportAPI = {
  getReports: (params) => apiClient.get('/reports', params),
  getReport: (reportId) => apiClient.get(`/reports/${reportId}`),
  generateReport: (data) => apiClient.post('/generate-report', data),
  uploadFile: (formData) => apiClient.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 任务状态相关API
export const taskAPI = {
  getTaskStatus: (taskId) => apiClient.get(`/task-status/${taskId}`)
}

export default apiClient