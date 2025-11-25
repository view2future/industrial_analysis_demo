<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold text-gray-900">
            <span v-if="reportData">{{ reportData.title }}</span>
            <span v-else>报告详情</span>
          </h1>
          <button 
            @click="goBack"
            class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            返回
          </button>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="flex justify-center items-center py-12">
          <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="text-center py-12">
          <p class="text-red-600 text-lg">{{ error }}</p>
          <button 
            @click="loadReport"
            class="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
          >
            重新加载
          </button>
        </div>
        
        <!-- 报告内容 -->
        <div v-else-if="reportData" class="space-y-8">
          <!-- 报告元数据 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-blue-50 p-4 rounded-lg">
              <p class="text-sm text-gray-600">状态</p>
              <p class="font-medium">{{ getStatusText(reportData.status) }}</p>
            </div>
            <div class="bg-green-50 p-4 rounded-lg">
              <p class="text-sm text-gray-600">城市</p>
              <p class="font-medium">{{ reportData.city || 'N/A' }}</p>
            </div>
            <div class="bg-purple-50 p-4 rounded-lg">
              <p class="text-sm text-gray-600">行业</p>
              <p class="font-medium">{{ reportData.industry || 'N/A' }}</p>
            </div>
          </div>
          
          <!-- 图表区域 -->
          <div v-if="reportData.report_data && reportData.report_data.charts" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-gray-50 p-4 rounded-lg" v-for="(chart, key) in reportData.report_data.charts" :key="key">
              <h3 class="font-medium text-gray-900 mb-2">{{ getChartTitle(key) }}</h3>
              <div :id="`chart-${key}`" class="h-64"></div>
            </div>
          </div>
          
          <!-- 报告内容 -->
          <div v-if="reportData.report_data" class="prose max-w-none">
            <div v-if="reportData.report_data.summary">
              <h2 class="text-xl font-semibold text-gray-900 mb-4">摘要</h2>
              <div class="bg-gray-50 p-4 rounded-lg whitespace-pre-line">
                {{ reportData.report_data.summary }}
              </div>
            </div>
            
            <div v-if="reportData.report_data.analysis">
              <h2 class="text-xl font-semibold text-gray-900 mt-6 mb-4">详细分析</h2>
              <div v-for="(section, index) in reportData.report_data.analysis" :key="index" class="mb-4">
                <h3 class="font-medium text-gray-800">{{ section.title }}</h3>
                <div class="ml-4 mt-2 text-gray-700 whitespace-pre-line">{{ section.content }}</div>
              </div>
            </div>
            
            <div v-if="reportData.report_data.ai_opportunities">
              <h2 class="text-xl font-semibold text-gray-900 mt-6 mb-4">AI应用机会</h2>
              <ul class="space-y-2">
                <li v-for="(opportunity, index) in reportData.report_data.ai_opportunities" :key="index" class="flex items-start">
                  <span class="text-indigo-600 mr-2">•</span>
                  <span>{{ opportunity }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- 没有报告数据时的提示 -->
        <div v-else class="text-center py-12">
          <p class="text-gray-500">未找到报告数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reportAPI } from '@/services/api'
import Chart from 'chart.js/auto' // Import chart.js

export default {
  name: 'ReportView',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    const reportData = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const charts = ref({})
    
    const loadReport = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await reportAPI.getReport(props.id)
        
        if (response.data.success) {
          reportData.value = response.data.data
          
          // 在下一个tick后渲染图表
          await nextTick()
          renderCharts()
        } else {
          error.value = response.data.message || '获取报告失败'
        }
      } catch (err) {
        console.error('Error loading report:', err)
        error.value = err.response?.data?.message || '获取报告失败'
      } finally {
        loading.value = false
      }
    }
    
    const nextTick = () => {
      return new Promise(resolve => {
        setTimeout(resolve, 0)
      })
    }
    
    const renderCharts = () => {
      if (!reportData.value?.report_data?.charts) return
      
      // 销毁之前的图表
      Object.values(charts.value).forEach(chart => chart.destroy())
      charts.value = {}
      
      // 渲染新的图表
      for (const [key, chartData] of Object.entries(reportData.value.report_data.charts)) {
        const canvasId = `chart-${key}`
        const canvas = document.getElementById(canvasId)
        if (canvas) {
          // 为简单起见，这里我们只创建一个基本的图表配置
          // 实际项目中需要根据数据类型动态配置图表
          const ctx = canvas.getContext('2d')
          
          // 示例图表配置 - 在实际使用中需要根据实际数据结构配置
          charts.value[key] = new Chart(ctx, {
            type: chartData.type || 'bar',
            data: chartData.data,
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
                  text: getChartTitle(key)
                }
              }
            }
          })
        }
      }
    }
    
    const getStatusText = (status) => {
      const statusMap = {
        'pending': '等待中',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败'
      }
      return statusMap[status] || status
    }
    
    const getChartTitle = (key) => {
      const titleMap = {
        'category_distribution': '内容分类分布',
        'ai_potential': 'AI应用潜力分析',
        'keyword_frequency': '关键词频次分析',
        'document_stats': '文档统计概览'
      }
      return titleMap[key] || key
    }
    
    const goBack = () => {
      router.push('/dashboard')
    }
    
    onMounted(() => {
      loadReport()
    })
    
    onUnmounted(() => {
      // 销毁图表以释放资源
      Object.values(charts.value).forEach(chart => {
        if (chart && chart.destroy) {
          chart.destroy()
        }
      })
    })
    
    return {
      reportData,
      loading,
      error,
      loadReport,
      getStatusText,
      getChartTitle,
      goBack
    }
  }
}
</script>