<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">区域产业分析小工作台</h1>
        <p class="text-gray-600 mt-2">登录以继续</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="输入用户名"
            required
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1">密码</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="输入密码"
            required
          />
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember"
              type="checkbox"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label for="remember" class="ml-2 block text-sm text-gray-700">记住我</label>
          </div>
        </div>

        <button
          type="submit"
          class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2 px-4 rounded-lg hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-300"
          :disabled="loading"
        >
          <span v-if="!loading">登录</span>
          <span v-else class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            登录中...
          </span>
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          还没有账户？
          <router-link to="/register" class="font-medium text-indigo-600 hover:text-indigo-500">立即注册</router-link>
        </p>
      </div>

      <!-- 错误信息提示 -->
      <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store'
import { authAPI } from '../services/api'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const credentials = ref({
      username: '',
      password: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    
    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await authAPI.login(credentials.value)
        
        if (response.data.success) {
          // 登录成功，保存用户信息和token
          const { user, token } = response.data
          authStore.login(user, token)
          
          // 重定向到仪表板
          router.push('/dashboard')
        } else {
          error.value = response.data.message || '登录失败'
        }
      } catch (err) {
        console.error('Login error:', err)
        error.value = err.response?.data?.message || '登录失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }
    
    return {
      credentials,
      loading,
      error,
      handleLogin
    }
  }
}
</script>