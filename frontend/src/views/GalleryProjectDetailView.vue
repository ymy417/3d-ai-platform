<template>
  <div class="gallery-project-detail-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-buttons">
        <el-button type="primary" plain @click="goHome">
          <el-icon><House /></el-icon>返回主页
        </el-button>
        <el-button type="primary" plain @click="goBack">
          <el-icon><ArrowLeft /></el-icon>返回画廊
        </el-button>
      </div>
      <h1 class="page-title">{{ project?.name }}</h1>
    </div>

    <!-- 项目详情 -->
    <div v-loading="loading" class="project-detail">
      <!-- 项目信息 -->
      <div v-if="project" class="project-info">
        <div class="project-header">
          <div class="project-meta">
            <span class="project-author">作者: <span class="author-name" @click="handleViewAuthor">{{ project.username || project.user_id }}</span></span>
            <span class="project-date">{{ formatDate(project.created_at) }}</span>
          </div>
          <div class="project-actions">
            <el-button 
              :type="isLiked ? 'primary' : 'default'" 
              @click="handleLike"
              :loading="actionLoading"
            >
              <el-icon><Star /></el-icon>{{ isLiked ? '已点赞' : '点赞' }}
            </el-button>
            <el-button 
              :type="isFavorited ? 'primary' : 'default'" 
              @click="handleFavorite"
              :loading="actionLoading"
            >
              <el-icon><Collection /></el-icon>{{ isFavorited ? '已收藏' : '收藏' }}
            </el-button>
            <el-button 
              type="success" 
              @click="handleDownload"
              :loading="actionLoading"
              :disabled="!project.allow_download"
            >
              <el-icon><Download /></el-icon>下载
            </el-button>
          </div>
        </div>

        <div class="project-description">
          <h2>项目描述</h2>
          <p>{{ project.description || '暂无描述' }}</p>
        </div>

        <!-- 3D预览 -->
        <div class="project-preview">
          <h2>3D预览</h2>
          <div class="preview-container">
            <Scene />
          </div>
        </div>

        <!-- 评论区 -->
        <div class="project-comments">
          <h2>评论 ({{ comments.length }})</h2>
          
          <!-- 评论表单 -->
          <div v-if="isLoggedIn" class="comment-form">
            <el-input
              v-model="commentContent"
              type="textarea"
              placeholder="写下你的评论..."
              :rows="3"
              maxlength="1000"
              show-word-limit
            />
            <el-button 
              type="primary" 
              @click="handleAddComment"
              :loading="commentLoading"
              :disabled="!commentContent.trim()"
            >
              发表评论
            </el-button>
          </div>
          
          <!-- 评论列表 -->
          <div class="comments-list">
            <div v-if="comments.length === 0" class="no-comments">
              暂无评论，来发表第一条评论吧
            </div>
            <div v-else v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-header">
                <span class="comment-author">{{ comment.username || comment.user_id }}</span>
                <div class="comment-actions">
                  <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                  <el-button 
                    v-if="isLoggedIn && comment.user_id === authStore.user?.id" 
                    type="text" 
                    size="small" 
                    @click="handleDeleteComment(comment.id)"
                    class="delete-button"
                  >
                    <el-icon><Delete /></el-icon>删除
                  </el-button>
                </div>
              </div>
              <div class="comment-content">
                {{ comment.content }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载失败 -->
      <div v-else-if="!loading" class="error-container">
        <el-empty description="项目不存在或未公开" :image-size="200" />
        <el-button type="primary" @click="goBack">返回画廊</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ArrowLeft, Star, Collection, Download, House } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import Scene from '@/components/3d/Scene.vue'
import { useGalleryStore } from '@/stores/gallery'
import { useAuthStore } from '@/stores/auth'
import type { Project, Comment } from '@/types/project'

const router = useRouter()
const route = useRoute()
const galleryStore = useGalleryStore()
const authStore = useAuthStore()

// 状态
const loading = ref(true)
const actionLoading = ref(false)
const commentLoading = ref(false)
const project = ref<Project | null>(null)
const comments = ref<Comment[]>([])
const commentContent = ref('')

// 计算属性
const projectId = computed(() => route.params.id as string)
const isLoggedIn = computed(() => authStore.isAuthenticated)
const isLiked = ref(false)
const isFavorited = ref(false)

// 加载项目详情
const loadProjectDetail = async () => {
  try {
    loading.value = true
    project.value = await galleryStore.fetchPublicProject(projectId.value)
    await loadComments()
    await checkUserInteractions()
  } catch (error) {
    ElMessage.error('加载项目详情失败')
  } finally {
    loading.value = false
  }
}

// 加载评论
const loadComments = async () => {
  try {
    comments.value = await galleryStore.fetchProjectComments(projectId.value)
  } catch (error) {
    ElMessage.error('加载评论失败')
  }
}

// 检查用户交互状态
const checkUserInteractions = async () => {
  if (isLoggedIn.value) {
    try {
      // 这里应该调用API检查用户是否已点赞和收藏
      // 暂时设为false
      isLiked.value = false
      isFavorited.value = false
    } catch (error) {
      console.error('检查用户交互状态失败', error)
    }
  }
}

// 事件处理
const goBack = () => {
  router.push({ name: 'gallery' })
}

const goHome = () => {
  router.push('/')
}

const handleViewAuthor = () => {
  if (project.value) {
    router.push({ name: 'gallery-user-detail', params: { id: project.value.user_id } })
  }
}

const handleLike = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }

  try {
    actionLoading.value = true
    const result = await galleryStore.toggleLike(projectId.value)
    isLiked.value = result.liked
    ElMessage.success(result.message)
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    actionLoading.value = false
  }
}

const handleFavorite = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }

  try {
    actionLoading.value = true
    const result = await galleryStore.toggleFavorite(projectId.value)
    isFavorited.value = result.favorited
    ElMessage.success(result.message)
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    actionLoading.value = false
  }
}

const handleDownload = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }

  try {
    actionLoading.value = true
    const result = await galleryStore.downloadProject(projectId.value)
    ElMessage.success(result.message)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '下载失败')
  } finally {
    actionLoading.value = false
  }
}

const handleAddComment = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }

  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  try {
    commentLoading.value = true
    await galleryStore.addComment(projectId.value, { content: commentContent.value })
    await loadComments()
    commentContent.value = ''
    ElMessage.success('评论发表成功')
  } catch (error) {
    ElMessage.error('发表评论失败')
  } finally {
    commentLoading.value = false
  }
}

const handleDeleteComment = async (commentId: number) => {
  try {
    await galleryStore.deleteComment(Number(projectId.value), commentId)
    ElMessage.success('评论删除成功')
  } catch (error) {
    ElMessage.error('删除评论失败')
  }
}

// 工具函数
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 监听路由参数变化
watch(() => route.params.id, () => {
  loadProjectDetail()
})

// 页面加载时获取数据
onMounted(() => {
  loadProjectDetail()
})
</script>

<style scoped lang="scss">
.gallery-project-detail-view {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;

  .header-buttons {
    display: flex;
    gap: 12px;
  }

  .page-title {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #303133;
  }
}

.project-detail {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  padding: 24px;
}

.project-info {
  .project-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid #ebeef5;

    .project-meta {
      display: flex;
      gap: 24px;
      font-size: 14px;
      color: #909399;

      .project-author {
        font-weight: 500;

        .author-name {
          color: #409eff;
          cursor: pointer;
          &:hover {
            text-decoration: underline;
          }
        }
      }
    }

    .project-actions {
      display: flex;
      gap: 12px;
    }
  }

  .project-description {
    margin-bottom: 32px;

    h2 {
      margin: 0 0 16px;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    p {
      margin: 0;
      font-size: 14px;
      line-height: 1.6;
      color: #606266;
    }
  }

  .project-preview {
    margin-bottom: 32px;

    h2 {
      margin: 0 0 16px;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    .preview-container {
      width: 100%;
      height: 400px;
      background: #f5f7fa;
      border-radius: 8px;
      overflow: hidden;
    }
  }

  .project-comments {
    h2 {
      margin: 0 0 24px;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    .comment-form {
      margin-bottom: 32px;
      display: flex;
      flex-direction: column;
      gap: 12px;

      .el-button {
        align-self: flex-end;
      }
    }

    .comments-list {
      .no-comments {
        text-align: center;
        padding: 48px 0;
        color: #909399;
        font-size: 14px;
      }

      .comment-item {
        padding: 16px 0;
        border-bottom: 1px solid #ebeef5;

        &:last-child {
          border-bottom: none;
        }

        .comment-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 14px;

          .comment-author {
            font-weight: 500;
            color: #303133;
          }

          .comment-actions {
            display: flex;
            align-items: center;
            gap: 12px;

            .comment-date {
              color: #909399;
            }

            .delete-button {
              color: #f56c6c;
              &:hover {
                color: #f78989;
              }
            }
          }
        }

        .comment-content {
          font-size: 14px;
          line-height: 1.6;
          color: #606266;
        }
      }
    }
  }
}

.error-container {
  text-align: center;
  padding: 64px 0;

  .el-button {
    margin-top: 24px;
  }
}
</style>