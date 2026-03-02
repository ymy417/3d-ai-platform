<template>
  <el-card class="project-card" shadow="hover" @click="goToDetail">
    <div class="project-thumbnail">
      <div class="placeholder-image">
        <el-icon :size="48"><Box /></el-icon>
        <span class="placeholder-text">3D Model</span>
      </div>
      <div class="project-status">
        <el-tag :type="statusType" size="small">{{ statusLabel }}</el-tag>
        <el-tag v-if="project.is_public" type="success" size="small" effect="plain">
          <el-icon><Star /></el-icon>已发表
        </el-tag>
      </div>
    </div>
    
    <div class="project-info">
      <h3 class="project-name" :title="project.name">{{ project.name }}</h3>
      <p class="project-description" :title="project.description || ''">
        {{ project.description || '暂无描述' }}
      </p>
      <div class="project-meta">
        <span class="update-time">{{ formatDate(project.updated_at) }}</span>
        <span v-if="project.is_public" class="author-info">
          <el-icon><User /></el-icon>
          <span class="author-name" @click="handleViewAuthor">{{ project.username || project.user_id }}</span>
        </span>
        <span v-if="project.is_public" class="download-status">
          <el-icon><Download /></el-icon>{{ project.allow_download ? '可下载' : '不可下载' }}
        </span>
      </div>
    </div>
    
    <div class="project-actions" @click.stop>
      <el-dropdown trigger="click">
        <el-button type="primary" link>
          <el-icon><More /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-if="!isPublic" @click="handleEdit">
              <el-icon><Edit /></el-icon>编辑
            </el-dropdown-item>
            <el-dropdown-item v-if="!isPublic" @click="handleDuplicate">
              <el-icon><CopyDocument /></el-icon>复制
            </el-dropdown-item>
            <el-dropdown-item v-if="!isPublic" @click="handlePublish">
              <el-icon><Star /></el-icon>{{ project.is_public ? '取消发表' : '发表到画廊' }}
            </el-dropdown-item>
            <el-dropdown-item v-if="!isPublic && project.is_public" @click="handleDownloadSettings">
              <el-icon><Download /></el-icon>下载设置
            </el-dropdown-item>
            <el-dropdown-item v-if="!isPublic" divided @click="handleDelete" class="delete-item">
              <el-icon><Delete /></el-icon>删除
            </el-dropdown-item>
            <el-dropdown-item v-if="isPublic" @click="handleView">
              <el-icon><View /></el-icon>查看详情
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 发表设置对话框 -->
    <el-dialog
      v-model="publishDialogVisible"
      title="发表到画廊"
      width="400px"
    >
      <el-form :model="publishForm">
        <el-form-item label="项目状态">
          <el-switch
            v-model="publishForm.isPublic"
            active-text="公开"
            inactive-text="私密"
          />
        </el-form-item>
        <el-form-item label="下载设置">
          <el-switch
            v-model="publishForm.allowDownload"
            active-text="允许下载"
            inactive-text="禁止下载"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="publishDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmPublish">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Box, More, Edit, CopyDocument, Delete, Star, Download, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Project } from '@/types/project'
import { ProjectStatusMap } from '@/types/project'
import { useProjectStore } from '@/stores/projects'
import { useGalleryStore } from '@/stores/gallery'

const props = defineProps<{
  project: Project
  isPublic?: boolean
}>()

const emit = defineEmits<{
  edit: [project: Project]
  delete: [id: number]
  view: [project: Project]
  viewAuthor: [userId: number]
}>()

const router = useRouter()
const projectStore = useProjectStore()
const galleryStore = useGalleryStore()

// 对话框状态
const publishDialogVisible = ref(false)
const publishForm = ref({
  isPublic: false,
  allowDownload: true
})

const statusLabel = computed(() => {
  return ProjectStatusMap[props.project.status]?.label || props.project.status
})

const statusType = computed(() => {
  return ProjectStatusMap[props.project.status]?.type || 'info'
})

const isPublic = computed(() => {
  return props.isPublic || false
})

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const goToDetail = () => {
  if (isPublic.value) {
    router.push(`/gallery/project/${props.project.id}`)
  } else {
    router.push(`/library/project/${props.project.id}`)
  }
}

const handleEdit = () => {
  emit('edit', props.project)
}

const handleDuplicate = async () => {
  try {
    await projectStore.duplicateProject(props.project.id)
    ElMessage.success('项目复制成功')
  } catch (error) {
    ElMessage.error('项目复制失败')
  }
}

const handlePublish = () => {
  publishForm.value.isPublic = !props.project.is_public
  publishForm.value.allowDownload = props.project.allow_download
  publishDialogVisible.value = true
}

const handleDownloadSettings = () => {
  publishForm.value.isPublic = props.project.is_public
  publishForm.value.allowDownload = props.project.allow_download
  publishDialogVisible.value = true
}

const confirmPublish = async () => {
  try {
    await galleryStore.publishProject(
      props.project.id,
      publishForm.value.isPublic,
      publishForm.value.allowDownload
    )
    ElMessage.success(publishForm.value.isPublic ? '项目发表成功' : '项目已设为私密')
    publishDialogVisible.value = false
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${props.project.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await projectStore.deleteProject(props.project.id)
    ElMessage.success('项目删除成功')
    emit('delete', props.project.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('项目删除失败')
    }
  }
}

const handleView = () => {
  emit('view', props.project)
}

const handleViewAuthor = () => {
  emit('viewAuthor', props.project.user_id)
}
</script>

<style scoped lang="scss">
.project-card {
  position: relative;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  :deep(.el-card__body) {
    padding: 0;
  }
}

.project-item:hover .project-checkbox {
  display: block;
}

.project-thumbnail {
  position: relative;
  width: 100%;
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  
  .placeholder-image {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: rgba(255, 255, 255, 0.8);
    
    .placeholder-text {
      margin-top: 8px;
      font-size: 14px;
    }
  }
  
  .project-status {
    position: absolute;
    top: 12px;
    right: 12px;
  }
}

.project-info {
  padding: 16px;
  
  .project-name {
    margin: 0 0 8px;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .project-description {
    margin: 0 0 12px;
    font-size: 13px;
    color: #606266;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    min-height: 40px;
  }
  
  .project-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    
    .update-time {
      font-size: 12px;
      color: #909399;
    }
    
    .author-info {
      font-size: 12px;
      color: #409eff;
      display: flex;
      align-items: center;
      gap: 4px;
      
      .author-name {
        cursor: pointer;
        &:hover {
          text-decoration: underline;
        }
      }
    }
    
    .download-status {
      font-size: 12px;
      color: #67c23a;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }
}

.project-actions {
  position: absolute;
  top: 8px;
  left: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  
  .project-card:hover & {
    opacity: 1;
  }
  
  :deep(.el-button) {
    color: white;
    background: rgba(0, 0, 0, 0.3);
    border: none;
    
    &:hover {
      background: rgba(0, 0, 0, 0.5);
    }
  }
}

.delete-item {
  color: #f56c6c;
}
</style>
