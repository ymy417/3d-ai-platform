<template>
  <div class="user-detail-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-buttons">
        <el-button type="primary" plain @click="goBack">
          <el-icon><ArrowLeft /></el-icon>返回画廊
        </el-button>
      </div>
      <h1 class="page-title">{{ user?.username }}的个人主页</h1>
    </div>

    <!-- 用户详情 -->
    <div v-loading="userStore.loading" class="user-detail">
      <!-- 用户信息 -->
      <div v-if="user" class="user-info">
        <div class="user-profile">
          <div class="avatar-container">
            <el-avatar :size="120" :src="user.avatar_url || ''" placeholder="用户"></el-avatar>
          </div>
          <div class="user-meta">
            <h2 class="username">{{ user.username }}</h2>
            <p class="bio">{{ user.bio || '暂无个人简介' }}</p>
            <div class="user-stats">
              <span class="stat-item">
                <el-icon><Collection /></el-icon>
                {{ userProjects.length }} 个项目
              </span>
              <span class="stat-item">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(user.created_at) }} 加入
              </span>
            </div>
          </div>
        </div>

        <!-- 用户项目 -->
        <div class="user-projects">
          <h2>公开项目</h2>
          
          <!-- 空状态 -->
          <el-empty
            v-if="userProjects.length === 0 && !userStore.loading"
            description="暂无公开项目"
            :image-size="200"
          >
            <template #description>
              <div class="empty-content">
                <p class="empty-title">还没有任何公开项目</p>
                <p class="empty-desc">该用户还没有发布任何公共项目</p>
              </div>
            </template>
          </el-empty>
          
          <!-- 项目网格 -->
          <div v-else class="projects-grid">
            <ProjectCard
              v-for="project in userProjects"
              :key="project.id"
              :project="project"
              :is-public="true"
              @view="handleViewProject"
              @viewAuthor="handleViewAuthor"
            />
          </div>
        </div>
      </div>

      <!-- 加载失败 -->
      <div v-else-if="!userStore.loading" class="error-container">
        <el-empty description="用户不存在" :image-size="200" />
        <el-button type="primary" @click="goBack">返回画廊</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ArrowLeft, Collection, Calendar } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import ProjectCard from '@/components/library/ProjectCard.vue'
import { useUserStore } from '@/stores/user'
import type { Project } from '@/types/project'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 计算属性
const userId = computed(() => route.params.id as string)
const user = computed(() => userStore.currentUser)
const userProjects = computed(() => userStore.userProjects)

// 加载用户信息
const loadUserInfo = async () => {
  try {
    await userStore.fetchPublicUserInfo(Number(userId.value))
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  }
}

// 事件处理
const goBack = () => {
  router.push({ name: 'gallery' })
}

const handleViewProject = (project: Project) => {
  router.push({ name: 'gallery-project-detail', params: { id: project.id } })
}

const handleViewAuthor = (userId: number) => {
  router.push({ name: 'gallery-user-detail', params: { id: userId } })
}

// 工具函数
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 监听路由参数变化
watch(() => route.params.id, () => {
  loadUserInfo()
})

// 页面加载时获取数据
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped lang="scss">
.user-detail-view {
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

.user-detail {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  padding: 24px;
}

.user-info {
  .user-profile {
    display: flex;
    gap: 32px;
    margin-bottom: 40px;
    padding-bottom: 24px;
    border-bottom: 1px solid #ebeef5;

    .avatar-container {
      flex-shrink: 0;
    }

    .user-meta {
      flex: 1;

      .username {
        margin: 0 0 12px;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }

      .bio {
        margin: 0 0 20px;
        font-size: 14px;
        line-height: 1.6;
        color: #606266;
      }

      .user-stats {
        display: flex;
        gap: 24px;

        .stat-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .user-projects {
    h2 {
      margin: 0 0 24px;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    .projects-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 24px;
    }
  }
}

.empty-content {
  text-align: center;

  .empty-title {
    font-size: 16px;
    font-weight: 500;
    color: #303133;
    margin: 0 0 8px;
  }

  .empty-desc {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.error-container {
  text-align: center;
  padding: 64px 0;

  .el-button {
    margin-top: 24px;
  }
}

@media (max-width: 768px) {
  .user-profile {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>
