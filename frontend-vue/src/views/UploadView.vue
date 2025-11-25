<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航已由父组件处理 -->
    
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white shadow rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">文件上传与分析</h1>
        
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors"
             @dragover.prevent="handleDragOver"
             @drop.prevent="handleDrop"
             @dragleave="handleDragLeave">
          <div v-if="!file">
            <i class="ri-upload-2-line text-4xl text-gray-400 mb-4 block"></i>
            <p class="text-lg text-gray-600 mb-2">拖拽文件到此处或点击选择</p>
            <p class="text-sm text-gray-500 mb-4">支持格式：.txt, .md, .json, .docx, .pdf</p>
            <input 
              type="file" 
              ref="fileInput"
              @change="handleFileSelect"
              class="hidden"
              accept=".txt,.md,.json,.docx,.pdf"
            />
            <button 
              @click="selectFile"
              class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              选择文件
            </button>
          </div>
          <div v-else class="text-left">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center">
                <i class="ri-file-text-line text-xl text-indigo-600 mr-3"></i>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ file.name }}</p>
                  <p class="text-sm text-gray-500">{{ formatFileSize(file.size) }}</p>
                </div>
              </div>
              <button 
                @click="removeFile"
                class="text-gray-400 hover:text-red-500"
              >
                <i class="ri-close-line text-xl"></i>
              </button>
            </div>
            
            <div class="mt-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">分析选项</h3>
              <div class="space-y-4">
                <div class="flex items-center">
                  <input 
                    id="option1" 
                    name="options" 
                    type="checkbox" 
                    checked
                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label for="option1" class="ml-3 block text-sm text-gray-700">
                    内容分类分析
                  </label>
                </div>
                <div class="flex items-center">
                  <input 
                    id="option2" 
                    name="options" 
                    type="checkbox" 
                    checked
                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label for="option2" class="ml-3 block text-sm text-gray-700">
                    AI应用潜力分析
                  </label>
                </div>
                <div class="flex items-center">
                  <input 
                    id="option3" 
                    name="options" 
                    type="checkbox" 
                    checked
                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label for="option3" class="ml-3 block text-sm text-gray-700">
                    关键词频次分析
                  </label>
                </div>
              </div>
              
              <div class="mt-6">
                <button
                  @click="uploadFile"
                  :disabled="uploading"
                  class="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  <span v-if="!uploading">开始上传和分析</span>
                  <span v-else class="flex items-center justify-center">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    上传中...
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 上传状态显示 -->
        <div v-if="uploadStatus" class="mt-6 p-4 rounded-lg" :class="uploadStatus.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'">
          <p>{{ uploadStatus.message }}</p>
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
  name: 'UploadView',
  setup() {
    const fileInput = ref(null)
    const file = ref(null)
    const uploading = ref(false)
    const uploadStatus = ref(null)
    const router = useRouter()
    const isDragOver = ref(false)
    
    const handleFileSelect = (event) => {
      const selectedFile = event.target.files[0]
      if (selectedFile) {
        validateAndSetFile(selectedFile)
      }
    }
    
    const selectFile = () => {
      fileInput.value.click()
    }
    
    const validateAndSetFile = (selectedFile) => {
      // 验证文件类型
      const allowedTypes = ['text/plain', 'text/markdown', 'application/json', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf']
      const allowedExtensions = ['.txt', '.md', '.json', '.docx', '.pdf']
      
      const fileExtension = '.' + selectedFile.name.split('.').pop().toLowerCase()
      
      if (!allowedTypes.includes(selectedFile.type) && !allowedExtensions.includes(fileExtension)) {
        uploadStatus.value = {
          success: false,
          message: '不支持的文件格式，请选择 .txt, .md, .json, .docx, 或 .pdf 文件'
        }
        return
      }
      
      // 验证文件大小 (最大50MB)
      if (selectedFile.size > 50 * 1024 * 1024) {
        uploadStatus.value = {
          success: false,
          message: '文件大小不能超过50MB'
        }
        return
      }
      
      file.value = selectedFile
      uploadStatus.value = null
    }
    
    const removeFile = () => {
      file.value = null
      uploadStatus.value = null
    }
    
    const uploadFile = async () => {
      if (!file.value) {
        uploadStatus.value = {
          success: false,
          message: '请先选择文件'
        }
        return
      }
      
      uploading.value = true
      uploadStatus.value = null
      
      try {
        const formData = new FormData()
        formData.append('file', file.value)
        
        const response = await reportAPI.uploadFile(formData)
        
        if (response.data.success) {
          uploadStatus.value = {
            success: true,
            message: response.data.message
          }
          
          // 跳转到报告详情页或仪表板
          setTimeout(() => {
            router.push(`/report/${response.data.report_id}`)
          }, 2000)
        } else {
          uploadStatus.value = {
            success: false,
            message: response.data.message
          }
        }
      } catch (error) {
        console.error('Upload error:', error)
        uploadStatus.value = {
          success: false,
          message: error.response?.data?.message || '上传失败，请稍后重试'
        }
      } finally {
        uploading.value = false
      }
    }
    
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const handleDragOver = (event) => {
      event.preventDefault()
      isDragOver.value = true
    }
    
    const handleDragLeave = () => {
      isDragOver.value = false
    }
    
    const handleDrop = (event) => {
      event.preventDefault()
      isDragOver.value = false
      
      if (event.dataTransfer.files && event.dataTransfer.files[0]) {
        validateAndSetFile(event.dataTransfer.files[0])
      }
    }
    
    return {
      fileInput,
      file,
      uploading,
      uploadStatus,
      handleFileSelect,
      selectFile,
      removeFile,
      uploadFile,
      formatFileSize,
      handleDragOver,
      handleDragLeave,
      handleDrop
    }
  }
}
</script>