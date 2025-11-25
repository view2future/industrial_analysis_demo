<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <header class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0 flex items-center">
              <i class="ri-pie-chart-2-line text-2xl mr-3"></i>
              <span class="text-xl font-bold">区域产业分析小工作台</span>
            </div>
          </div>
          <nav class="hidden md:flex space-x-8">
            <router-link to="/dashboard" class="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors">仪表板</router-link>
            <router-link to="/upload" class="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors">上传分析</router-link>
            <router-link to="/generate-report" class="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors">生成报告</router-link>
          </nav>
          <div class="flex items-center">
            <span class="mr-4 text-sm">欢迎, {{ user?.username }}!</span>
            <button @click="handleLogout" class="bg-white text-indigo-600 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 仪表板统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white p-6 rounded-xl shadow-md border border-gray-200">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-blue-100 text-blue-600">
              <i class="ri-file-text-line text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">总报告数</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.total_reports || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-xl shadow-md border border-gray-200">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-green-100 text-green-600">
              <i class="ri-check-double-line text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">已完成</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.completed_reports || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-xl shadow-md border border-gray-200">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-yellow-100 text-yellow-600">
              <i class="ri-loader-4-line text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">处理中</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.processing_reports || 0 }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近报告 -->
      <div class="bg-white rounded-xl shadow-md border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-800">最近报告</h2>
        </div>
        <div class="p-6">
          <div v-if="stats.recent_reports && stats.recent_reports.length > 0">
            <ul class="divide-y divide-gray-200">
              <li v-for="report in stats.recent_reports" :key="report.id" class="py-4">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-medium text-gray-900">{{ report.title }}</h3>
                    <p class="text-sm text-gray-500">{{ report.city }} - {{ report.industry }}</p>
                  </div>
                  <div class="flex items-center space-x-4">
                    <span :class="getStatusClass(report.status)" class="px-2 py-1 text-xs rounded-full">
                      {{ getStatusText(report.status) }}
                    </span>
                    <time class="text-sm text-gray-500">{{ formatDate(report.created_at) }}</time>
                    <router-link 
                      :to="`/report/${report.report_id}`" 
                      class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                    >
                      查看
                    </router-link>
                  </div>
                </div>
              </li>
            </ul>
          </div>
          <div v-else class="text-center py-8">
            <p class="text-gray-500">暂无报告数据</p>
            <div class="mt-4">
              <router-link to="/upload" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                上传文件进行分析
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, useReportStore } from '../store'
import { authAPI, dashboardAPI } from '../services/api'

export default {
  name: 'DashboardView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const reportStore = useReportStore()
    
    const stats = ref({})
    const loading = ref(false)
    
    const user = computed(() => authStore.user)
    
    const loadStats = async () => {
      loading.value = true
      try {
        const response = await dashboardAPI.getStats()
        if (response.data.success) {
          stats.value = response.data.data
        }
      } catch (error) {
        console.error('Failed to load dashboard stats:', error)
      } finally {
        loading.value = false
      }
    }
    
    const handleLogout = async () => {
      try {
        await authAPI.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        authStore.logout()
        router.push('/login')
      }
    }
    
    const getStatusClass = (status) => {
      switch (status) {
        case 'completed':
          return 'bg-green-100 text-green-800'
        case 'processing':
          return 'bg-yellow-100 text-yellow-800'
        case 'failed':
          return 'bg-red-100 text-red-800'
        default:
          return 'bg-gray-100 text-gray-800'
      }
    }
    
    const getStatusText = (status) => {
      switch (status) {
        case 'completed':
          return '已完成'
        case 'processing':
          return '处理中'
        case 'failed':
          return '失败'
        default:
          return status
      }
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    onMounted(() => {
      if (!authStore.isLoggedIn) {
        router.push('/login')
        return
      }
      loadStats()
    })
    
    return {
      stats,
      user,
      loading,
      handleLogout,
      getStatusClass,
      getStatusText,
      formatDate
    }
  }
}
</script>