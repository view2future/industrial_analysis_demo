<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">区域产业分析小工作台</h1>
        <p class="text-gray-600 mt-2">创建新账户</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input
            id="username"
            v-model="formData.username"
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
            v-model="formData.password"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="输入密码"
            required
          />
        </div>

        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
          <input
            id="confirmPassword"
            v-model="formData.confirmPassword"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="确认密码"
            required
          />
        </div>

        <button
          type="submit"
          class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2 px-4 rounded-lg hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-300"
          :disabled="loading"
        >
          <span v-if="!loading">注册</span>
          <span v-else class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            注册中...
          </span>
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          已有账户？
          <router-link to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">立即登录</router-link>
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
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const formData = ref({
      username: '',
      password: '',
      confirmPassword: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    
    const handleRegister = async () => {
      if (formData.value.password !== formData.value.confirmPassword) {
        error.value = '两次输入的密码不一致'
        return
      }
      
      loading.value = true
      error.value = ''
      
      try {
        const { confirmPassword, ...userData } = formData.value
        const response = await authAPI.register(userData)
        
        if (response.data.success) {
          // 注册成功，自动登录
          const { user, token } = response.data
          authStore.login(user, token)
          
          // 重定向到仪表板
          router.push('/dashboard')
        } else {
          error.value = response.data.message || '注册失败'
        }
      } catch (err) {
        console.error('Registration error:', err)
        error.value = err.response?.data?.message || '注册失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }
    
    return {
      formData,
      loading,
      error,
      handleRegister
    }
  }
}
</script>