<template>
  <div class="modeling-view">
    <!-- 页面头部 -->
    <div class="header">
      <button class="home-btn" @click="goHome">
        <span class="home-icon">🏠</span> 返回主页
      </button>
      <div class="project-info">
        <h1>3D建模</h1>
        <p v-if="projectName">{{ projectName }}</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="saveProject">
          <el-icon><Download /></el-icon> 保存
        </el-button>
      </div>
    </div>

    <!-- 流程导航 -->
    <div class="process-nav">
      <div 
        v-for="(step, index) in processSteps" 
        :key="step.id"
        class="process-step"
        :class="{ 
          'active': currentStep === step.id, 
          'completed': currentStep > step.id 
        }"
        @click="goToStep(step.id)"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-title">{{ step.title }}</div>
        <div class="step-line" v-if="index < processSteps.length - 1"></div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 3D预览区域 -->
      <div class="preview-area">
        <div class="preview-container" ref="previewContainer">
          <!-- Three.js 场景将在这里渲染 -->
          <div v-if="loading" class="loading-overlay">
            <div class="spinner"></div>
            <p>加载模型中...</p>
          </div>
          <div v-else-if="!hasModel" class="no-model">
            <el-icon :size="64"><Box /></el-icon>
            <p>请选择或上传模型</p>
          </div>
        </div>
        <div class="view-controls">
          <el-button @click="resetView">
            <el-icon><Refresh /></el-icon> 重置视图
          </el-button>
          <el-button @click="toggleWireframe">
            <el-icon><View /></el-icon> {{ wireframe ? '实体' : '线框' }}
          </el-button>
        </div>
      </div>

      <!-- 参数控制面板 -->
      <div class="control-panel">
        <div class="panel-header">
          <h3>参数控制</h3>
          <el-button type="text" @click="panelCollapsed = !panelCollapsed">
            <el-icon v-if="panelCollapsed"><Expand /></el-icon>
            <el-icon v-else><Fold /></el-icon>
          </el-button>
        </div>
        
        <div v-if="!panelCollapsed" class="panel-content">
          <!-- 阶段特定的控制面板 -->
          <div v-if="currentStep === 'load'" class="step-controls">
            <h4>模型加载</h4>
            <el-button type="primary" @click="loadDefaultModel">
              <el-icon><Download /></el-icon> 加载默认模型
            </el-button>
            <el-button @click="showUploadModal = true">
              <el-icon><Upload /></el-icon> 上传模型
            </el-button>
          </div>
          
          <div v-else-if="currentStep === 'generate'" class="step-controls">
            <h4>模型生成</h4>
            <el-button type="primary" @click="showAIModal = true">
              <el-icon><ChatLineRound /></el-icon> AI生成
            </el-button>
          </div>
          
          <div v-else-if="currentStep === 'render'" class="step-controls">
            <h4>渲染设置</h4>
            <el-form :model="renderSettings">
              <el-form-item label="材质">
                <el-select v-model="renderSettings.material">
                  <el-option label="标准材质" value="standard" />
                  <el-option label="金属材质" value="metal" />
                  <el-option label="塑料材质" value="plastic" />
                </el-select>
              </el-form-item>
              <el-form-item label="颜色">
                <el-color-picker v-model="renderSettings.color" />
              </el-form-item>
            </el-form>
          </div>
          
          <div v-else-if="currentStep === 'rig'" class="step-controls">
            <h4>骨骼绑定</h4>
            <el-button type="primary" @click="autoRig">
              <el-icon><MagicStick /></el-icon> 自动绑定
            </el-button>
          </div>
          
          <div v-else-if="currentStep === 'animate'" class="step-controls">
            <h4>动画生成</h4>
            <el-button type="primary" @click="loadAnimation">
              <el-icon><VideoCamera /></el-icon> 加载动画
            </el-button>
          </div>
          
          <div v-else-if="currentStep === 'export'" class="step-controls">
            <h4>导出设置</h4>
            <el-form :model="exportSettings">
              <el-form-item label="格式">
                <el-select v-model="exportSettings.format">
                  <el-option label="OBJ" value="obj" />
                  <el-option label="FBX" value="fbx" />
                  <el-option label="GLTF" value="gltf" />
                  <el-option label="GLB" value="glb" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="exportModel">
                  <el-icon><Download /></el-icon> 导出模型
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮栏 -->
    <div class="action-bar">
      <el-button 
        @click="prevStep"
        :disabled="currentStep === processSteps[0].id"
      >
        <el-icon><ArrowLeft /></el-icon> 上一步
      </el-button>
      <el-button 
        type="primary" 
        @click="nextStep"
        :disabled="currentStep === processSteps[processSteps.length - 1].id"
      >
        下一步 <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>

    <!-- 上传模型弹窗 -->
    <el-dialog
      v-model="showUploadModal"
      title="上传模型"
      width="500px"
    >
      <el-upload
        class="upload-demo"
        action="/api/files/upload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :file-list="fileList"
        accept=".obj,.fbx,.gltf,.glb"
        :auto-upload="false"
      >
        <el-button type="primary">
          <el-icon><Upload /></el-icon> 选择文件
        </el-button>
        <template #tip>
          <div class="el-upload__tip">
            支持上传 .obj, .fbx, .gltf, .glb 格式的模型文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showUploadModal = false">取消</el-button>
          <el-button type="primary" @click="submitUpload">开始上传</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- AI生成弹窗 -->
    <el-dialog
      v-model="showAIModal"
      title="AI生成模型"
      width="600px"
    >
      <el-form :model="aiForm">
        <el-form-item label="描述">
          <el-input
            v-model="aiForm.description"
            type="textarea"
            rows="4"
            placeholder="请描述您想要的模型..."
          />
        </el-form-item>
        <el-form-item label="风格">
          <el-select v-model="aiForm.style">
            <el-option label="写实风格" value="realistic" />
            <el-option label="卡通风格" value="cartoon" />
            <el-option label="低多边形" value="lowpoly" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAIModal = false">取消</el-button>
          <el-button type="primary" @click="generateModel">生成模型</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Download,
  Box,
  Refresh,
  View,
  Expand,
  Fold,
  Upload,
  ChatLineRound,
  MagicStick,
  VideoCamera,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const router = useRouter()
const route = useRoute()

// 项目信息
const projectName = ref('')

// 流程步骤
const processSteps = ref([
  { id: 'load', title: '加载模型' },
  { id: 'generate', title: '模型生成' },
  { id: 'render', title: '渲染模型' },
  { id: 'rig', title: '骨骼绑定' },
  { id: 'animate', title: '动画生成' },
  { id: 'export', title: '导出模型' }
])

const currentStep = ref('load')

// 3D场景
const previewContainer = ref<HTMLElement>()
const loading = ref(false)
const hasModel = ref(false)
const wireframe = ref(false)
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let model: THREE.Object3D

// 控制面板
const panelCollapsed = ref(false)

// 渲染设置
const renderSettings = ref({
  material: 'standard',
  color: '#ffffff'
})

// 导出设置
const exportSettings = ref({
  format: 'glb'
})

// AI生成设置
const aiForm = ref({
  description: '',
  style: 'realistic'
})

// 上传设置
const showUploadModal = ref(false)
const showAIModal = ref(false)
const fileList = ref<any[]>([])

// 初始化3D场景
const initScene = () => {
  if (!previewContainer.value) return

  // 创建场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf0f0f0)

  // 创建相机
  camera = new THREE.PerspectiveCamera(
    75,
    previewContainer.value.clientWidth / previewContainer.value.clientHeight,
    0.1,
    1000
  )
  camera.position.z = 5

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(previewContainer.value.clientWidth, previewContainer.value.clientHeight)
  previewContainer.value.appendChild(renderer.domElement)

  // 添加轨道控制器
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05

  // 添加光源
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(1, 1, 1)
  scene.add(directionalLight)

  // 渲染循环
  const animate = () => {
    requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }
  animate()

  // 响应窗口大小变化
  const handleResize = () => {
    if (!previewContainer.value) return
    camera.aspect = previewContainer.value.clientWidth / previewContainer.value.clientHeight
    camera.updateProjectionMatrix()
    renderer.setSize(previewContainer.value.clientWidth, previewContainer.value.clientHeight)
  }
  window.addEventListener('resize', handleResize)
}

// 加载默认模型
const loadDefaultModel = async () => {
  loading.value = true
  try {
    // 这里应该加载默认小人模型
    // 暂时创建一个简单的立方体作为占位符
    const geometry = new THREE.BoxGeometry(1, 1, 1)
    const material = new THREE.MeshStandardMaterial({ color: 0x0077ff })
    model = new THREE.Mesh(geometry, material)
    scene.add(model)
    hasModel.value = true
    ElMessage.success('默认模型加载成功')
  } catch (error) {
    ElMessage.error('模型加载失败')
  } finally {
    loading.value = false
  }
}

// 重置视图
const resetView = () => {
  if (controls) {
    controls.reset()
    camera.position.set(0, 0, 5)
    camera.lookAt(0, 0, 0)
  }
}

// 切换线框模式
const toggleWireframe = () => {
  wireframe.value = !wireframe.value
  if (model) {
    model.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        object.material.wireframe = wireframe.value
      }
    })
  }
}

// 自动绑定骨骼
const autoRig = () => {
  ElMessage.info('骨骼绑定功能开发中')
}

// 加载动画
const loadAnimation = () => {
  ElMessage.info('动画加载功能开发中')
}

// 导出模型
const exportModel = () => {
  ElMessage.info('模型导出功能开发中')
}

// 生成模型
const generateModel = () => {
  ElMessage.info('AI生成功能开发中')
  showAIModal.value = false
}

// 处理上传成功
const handleUploadSuccess = (response: any) => {
  ElMessage.success('文件上传成功')
  showUploadModal.value = false
}

// 处理上传错误
const handleUploadError = (error: any) => {
  ElMessage.error('文件上传失败')
}

// 提交上传
const submitUpload = () => {
  // 触发上传
  const uploader = document.querySelector('.el-upload__input') as HTMLInputElement
  if (uploader) {
    uploader.click()
  }
}

// 导航到指定步骤
const goToStep = (stepId: string) => {
  currentStep.value = stepId
}

// 上一步
const prevStep = () => {
  const currentIndex = processSteps.value.findIndex(step => step.id === currentStep.value)
  if (currentIndex > 0) {
    currentStep.value = processSteps.value[currentIndex - 1].id
  }
}

// 下一步
const nextStep = () => {
  const currentIndex = processSteps.value.findIndex(step => step.id === currentStep.value)
  if (currentIndex < processSteps.value.length - 1) {
    currentStep.value = processSteps.value[currentIndex + 1].id
  }
}

// 保存项目
const saveProject = () => {
  ElMessage.success('项目保存成功')
}

// 返回主页
const goHome = () => {
  router.push('/')
}

// 生命周期钩子
onMounted(() => {
  initScene()
  // 从路由参数获取项目信息
  const projectId = route.query.projectId
  if (projectId) {
    projectName.value = `项目 ${projectId}`
  }
})

onUnmounted(() => {
  // 清理3D场景
  if (renderer) {
    renderer.dispose()
  }
  if (model) {
    scene.remove(model)
  }
})
</script>

<style scoped>
.modeling-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.home-btn {
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

.project-info h1 {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}

.project-info p {
  color: #666;
  margin: 0.25rem 0 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.process-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  padding: 1.5rem 0;
  background: white;
  margin: 1rem 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  position: relative;
  z-index: 1;
  transition: all 0.3s;
}

.process-step:hover {
  transform: translateY(-2px);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 0.5rem;
  transition: all 0.3s;
}

.process-step.active .step-number {
  background: #667eea;
  color: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.process-step.completed .step-number {
  background: #67c23a;
  color: white;
}

.step-title {
  font-size: 0.9rem;
  color: #666;
  text-align: center;
  transition: all 0.3s;
}

.process-step.active .step-title {
  color: #667eea;
  font-weight: 600;
}

.step-line {
  position: absolute;
  top: 16px;
  left: 50%;
  width: 2rem;
  height: 2px;
  background: #e0e0e0;
  z-index: -1;
  transition: all 0.3s;
}

.process-step.completed .step-line {
  background: #67c23a;
}

.main-content {
  flex: 1;
  display: flex;
  gap: 1rem;
  padding: 0 2rem 1rem;
  overflow: hidden;
}

.preview-area {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-model {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.view-controls {
  padding: 1rem;
  border-top: 1px solid #eee;
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
}

.control-panel {
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.panel-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.step-controls h4 {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: #666;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: white;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>