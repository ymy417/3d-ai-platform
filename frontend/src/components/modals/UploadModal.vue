<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-content">
      <div class="modal-header">
        <h2>上传3D模型</h2>
        <button class="close-btn" @click="handleClose">&times;</button>
      </div>

      <div class="modal-body">
        <div
          class="drop-zone"
          :class="{ dragover: isDragover }"
          @dragover.prevent="isDragover = true"
          @dragleave.prevent="isDragover = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <div v-if="!selectedFile" class="upload-prompt">
            <div class="upload-icon">📁</div>
            <p class="prompt-text">拖拽文件到这里，或点击选择</p>
            <p class="file-types">支持 .obj, .fbx, .gltf, .glb 格式</p>
            <p class="file-limit">最大文件大小：100MB</p>
          </div>

          <div v-else class="selected-file">
            <div class="file-info">
              <span class="file-icon">📄</span>
              <div class="file-details">
                <p class="file-name">{{ selectedFile.name }}</p>
                <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
            </div>

            <div v-if="uploading" class="upload-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              </div>
              <span class="progress-text">{{ uploadProgress }}%</span>
            </div>

            <div v-else class="file-actions">
              <button class="remove-btn" @click.stop="clearFile">移除</button>
            </div>
          </div>
        </div>

        <input
          ref="fileInput"
          type="file"
          accept=".obj,.fbx,.gltf,.glb"
          @change="handleFileSelect"
          style="display: none"
        />

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div v-if="uploadResult" class="success-message">
          <span class="success-icon">✅</span>
          文件上传成功！
        </div>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" @click="handleClose" :disabled="uploading">取消</button>
        <button
          class="upload-btn"
          @click="handleUpload"
          :disabled="!selectedFile || uploading"
        >
          {{ uploading ? '上传中...' : '开始上传' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { fileApi, getFileTypeFromExtension, formatFileSize } from '@/api/file'
import type { UploadResponse } from '@/api/file'

const emit = defineEmits<{
  close: []
  uploadSuccess: [data: UploadResponse]
}>()

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const isDragover = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')
const uploadResult = ref<UploadResponse | null>(null)

const triggerFileInput = () => {
  if (!uploading.value && fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    validateAndSetFile(target.files[0])
  }
  target.value = ''
}

const handleDrop = (event: DragEvent) => {
  isDragover.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    validateAndSetFile(event.dataTransfer.files[0])
  }
}

const validateAndSetFile = (file: File) => {
  errorMessage.value = ''
  uploadResult.value = null

  const maxSize = 100 * 1024 * 1024
  if (file.size > maxSize) {
    errorMessage.value = '文件大小超过100MB限制'
    return
  }

  const ext = file.name.split('.').pop()?.toLowerCase() || ''
  const allowedExtensions = ['obj', 'fbx', 'gltf', 'glb']
  if (!allowedExtensions.includes(ext)) {
    errorMessage.value = `不支持的文件类型：.${ext}。支持：${allowedExtensions.map(e => `.${e}`).join(', ')}`
    return
  }

  selectedFile.value = file
}

const clearFile = () => {
  selectedFile.value = null
  errorMessage.value = ''
  uploadProgress.value = 0
  uploadResult.value = null
}

const handleUpload = async () => {
  if (!selectedFile.value || uploading.value) return

  uploading.value = true
  uploadProgress.value = 0
  errorMessage.value = ''

  try {
    const fileType = getFileTypeFromExtension(selectedFile.value.name)
    
    const response = await fileApi.uploadFile(selectedFile.value, {
      type: fileType,
      onProgress: (progress) => {
        uploadProgress.value = progress
      }
    })

    if (response.success) {
      uploadResult.value = response.data
      setTimeout(() => {
        emit('uploadSuccess', response.data)
      }, 500)
    }
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } } }
    errorMessage.value = err.response?.data?.detail || '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}

const handleClose = () => {
  if (!uploading.value) {
    emit('close')
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.drop-zone {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.drop-zone:hover,
.drop-zone.dragover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.upload-prompt .upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.prompt-text {
  font-size: 1rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.file-types {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.file-limit {
  color: #999;
  font-size: 0.8rem;
}

.selected-file {
  width: 100%;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.file-icon {
  font-size: 2rem;
}

.file-details {
  text-align: left;
}

.file-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 0.25rem;
  word-break: break-all;
}

.file-size {
  color: #666;
  font-size: 0.9rem;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 0.9rem;
  color: #666;
  min-width: 40px;
}

.file-actions {
  display: flex;
  justify-content: center;
}

.remove-btn {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.remove-btn:hover {
  background: #ff7875;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  color: #ff4d4f;
  font-size: 0.9rem;
}

.success-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 4px;
  color: #52c41a;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
}

.cancel-btn,
.upload-btn {
  padding: 0.6rem 1.5rem;
  border-radius: 6px;
  font-size: 0.95rem;
  cursor: pointer;
  border: none;
}

.cancel-btn {
  background: #f0f0f0;
  color: #666;
}

.cancel-btn:hover:not(:disabled) {
  background: #e0e0e0;
}

.upload-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.upload-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.upload-btn:disabled,
.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
