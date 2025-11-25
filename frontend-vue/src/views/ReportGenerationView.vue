<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white shadow rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">LLM报告生成</h1>
        
        <form @submit.prevent="generateReport" class="space-y-6">
          <div>
            <label for="city" class="block text-sm font-medium text-gray-700 mb-1">城市</label>
            <input
              id="city"
              v-model="formData.city"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="例如：上海"
              required
            />
          </div>
          
          <div>
            <label for="industry" class="block text-sm font-medium text-gray-700 mb-1">行业</label>
            <input
              id="industry"
              v-model="formData.industry"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="例如：人工智能"
              required
            />
          </div>
          
          <div>
            <label for="additional_context" class="block text-sm font-medium text-gray-700 mb-1">补充上下文</label>
            <textarea
              id="additional_context"
              v-model="formData.additional_context"
              rows="4"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="提供额外的上下文信息以帮助生成更精确的报告"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">LLM服务</label>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <label class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  v-model="formData.llm_service"
                  value="kimi"
                  class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-3 text-sm text-gray-700">Kimi</span>
              </label>
              <label class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  v-model="formData.llm_service"
                  value="gemini"
                  class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-3 text-sm text-gray-700">Gemini</span>
              </label>
              <label class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  v-model="formData.llm_service"
                  value="ernie"
                  class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-3 text-sm text-gray-700">ERNIE Bot</span>
              </label>
            </div>
          </div>
          
          <div class="flex space-x-4">
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              <span v-if="!loading">生成报告</span>
              <span v-else class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                生成中...
              </span>
            </button>
            
            <button
              type="button"
              @click="resetForm"
              class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              重置
            </button>
          </div>
        </form>
        
        <!-- 生成状态显示 -->
        <div v-if="generationStatus" class="mt-6 p-4 rounded-lg" :class="generationStatus.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'">
          <p>{{ generationStatus.message }}</p>
          <div v-if="generationStatus.task_id" class="mt-2">
            <p>任务ID: {{ generationStatus.task_id }}</p>
            <p>报告ID: {{ generationStatus.report_id }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { reportAPI } from '@/services/api'
import { useRouter } from 'vue-router'

export default {
  name: 'ReportGenerationView',
  setup() {
    const router = useRouter()
    
    const formData = ref({
      city: '',
      industry: '',
      additional_context: '',
      llm_service: 'gemini'  // 默认选择
    })
    
    const loading = ref(false)
    const generationStatus = ref(null)
    
    const generateReport = async () => {
      loading.value = true
      generationStatus.value = null
      
      try {
        const response = await reportAPI.generateReport(formData.value)
        
        if (response.data.success) {
          generationStatus.value = {
            success: true,
            message: '报告生成任务已启动',
            task_id: response.data.task_id,
            report_id: response.data.report_id
          }
          
          // 跳转到任务状态页面
          setTimeout(() => {
            router.push(`/report/${response.data.report_id}`)
          }, 2000)
        } else {
          generationStatus.value = {
            success: false,
            message: response.data.message || '报告生成失败'
          }
        }
      } catch (error) {
        console.error('Generate report error:', error)
        generationStatus.value = {
          success: false,
          message: error.response?.data?.message || '报告生成失败，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    const resetForm = () => {
      formData.value = {
        city: '',
        industry: '',
        additional_context: '',
        llm_service: 'gemini'
      }
      generationStatus.value = null
    }
    
    return {
      formData,
      loading,
      generationStatus,
      generateReport,
      resetForm
    }
  }
}
</script>