<template>
  <div class="create-view">
    <div class="header">
      <button class="home-btn" @click="goHome">
        <span class="home-icon">🏠</span> 返回主页
      </button>
      <h1>开始创作</h1>
      <p>选择一种方式开始创建你的3D角色</p>
    </div>

    <div class="creation-options">
      <div class="option-card" @click="selectOption('ai')">
        <div class="option-icon">🤖</div>
        <h3>AI智能生成</h3>
        <p>用文字描述生成3D角色模型</p>
        <ul class="feature-list">
          <li>支持自然语言描述</li>
          <li>多种风格选择</li>
          <li>实时预览</li>
        </ul>
        <button class="select-btn">开始创建</button>
      </div>

      <div class="option-card" @click="selectOption('upload')">
        <div class="option-icon">📤</div>
        <h3>上传现有模型</h3>
        <p>上传你的3D模型文件</p>
        <div class="file-formats">.obj .fbx .gltf .glb</div>
        <button class="select-btn">上传文件</button>
      </div>

      <div class="option-card" @click="selectOption('template')">
        <div class="option-icon">📁</div>
        <h3>选择模板</h3>
        <p>从模板库开始创作</p>
        <div class="template-preview">
          <div v-for="t in templates" :key="t.id" class="template-item">
            <img :src="t.preview" :alt="t.name" />
            <span>{{ t.name }}</span>
          </div>
        </div>
        <button class="select-btn">浏览模板</button>
      </div>
    </div>

    <UploadModal
      v-if="showUpload"
      @close="showUpload = false"
      @upload-success="handleUploadSuccess"
    />
    <AIModal
      v-if="showAI"
      @close="showAI = false"
      @generate-success="handleGenerateSuccess"
    />

    <div v-if="creating" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p>正在创建项目...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { Template } from '@/types'
import UploadModal from '@/components/modals/UploadModal.vue'
import AIModal from '@/components/modals/AIModal.vue'
import { projectApi } from '@/api/project'
import type { UploadResponse } from '@/api/file'

const router = useRouter()
const showUpload = ref(false)
const showAI = ref(false)
const creating = ref(false)

const templates = ref<Template[]>([
  { id: 1, name: '男性基础', preview: '/assets/templates/male.jpg' },
  { id: 2, name: '女性基础', preview: '/assets/templates/female.jpg' },
  { id: 3, name: '卡通角色', preview: '/assets/templates/cartoon.jpg' },
  { id: 4, name: '机器人', preview: '/assets/templates/robot.jpg' }
])

const selectOption = (option: 'ai' | 'upload' | 'template') => {
  if (option === 'ai') showAI.value = true
  else if (option === 'upload') showUpload.value = true
  else router.push('/templates')
}

const handleUploadSuccess = async (uploadData: UploadResponse) => {
  showUpload.value = false
  creating.value = true

  try {
    const project = await projectApi.createProject({
      name: uploadData.original_name.replace(/\.[^/.]+$/, ''),
      description: `从上传文件创建 - ${uploadData.original_name}`
    })

    await projectApi.updateProject(project.id, {
      name: project.name,
      description: project.description || ''
    })

    ElMessage.success('项目创建成功！')
    router.push({ 
      path: '/modeling', 
      query: { 
        projectId: project.id,
        modelUrl: uploadData.url,
        objectName: uploadData.object_name
      } 
    })
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '创建项目失败')
  } finally {
    creating.value = false
  }
}

const handleGenerateSuccess = (taskId: string) => {
  showAI.value = false
  router.push({ path: '/modeling/generating', query: { taskId } })
}

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.create-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.home-btn {
  position: absolute;
  left: 0;
  top: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.home-btn:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.home-icon {
  font-size: 1.2rem;
}

.header h1 {
  font-size: 2.5rem;
  color: #333;
}

.header p {
  color: #666;
  font-size: 1.1rem;
}

.creation-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.option-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  cursor: pointer;
  text-align: center;
}

.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.option-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.option-card h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.option-card p {
  color: #666;
  margin-bottom: 1.5rem;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
  text-align: left;
}

.feature-list li {
  padding: 0.5rem 0;
  color: #555;
  border-bottom: 1px solid #eee;
}

.file-formats {
  color: #666;
  margin: 1rem 0;
  font-size: 1.1rem;
}

.template-preview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-top: 1rem;
}

.template-item img {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 0.25rem;
}

.template-item span {
  font-size: 0.8rem;
  color: #666;
}

.select-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  margin-top: 1.5rem;
  cursor: pointer;
  transition: opacity 0.3s;
}

.select-btn:hover {
  opacity: 0.9;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.loading-content {
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-content p {
  color: #666;
  font-size: 1rem;
}
</style>
