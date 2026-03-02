<template>
  <div class="gallery-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">公共画廊</h1>
        <p class="page-subtitle">浏览和探索社区创建的3D项目</p>
      </div>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" @tab-click="handleTabChange" class="gallery-tabs">
      <el-tab-pane label="全部项目" name="all">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="search-container">
            <el-select v-model="searchType" placeholder="搜索类型" class="search-type-select">
              <el-option label="项目名称" value="project" />
              <el-option label="作者名称" value="user" />
            </el-select>
            <el-input
              v-model="searchQuery"
              :placeholder="searchType === 'project' ? '搜索项目名称' : '搜索作者名称'"
              clearable
              class="search-input"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <el-select v-model="sortBy" placeholder="排序方式" @change="handleSort">
            <el-option label="最新创建" value="created_at" />
            <el-option label="最近更新" value="updated_at" />
            <el-option label="项目名称" value="name" />
          </el-select>

          <el-radio-group v-model="sortOrder" size="small" @change="handleSort">
            <el-radio-button label="desc">
              <el-icon><SortDown /></el-icon>
            </el-radio-button>
            <el-radio-button label="asc">
              <el-icon><SortUp /></el-icon>
            </el-radio-button>
          </el-radio-group>
        </div>
      </el-tab-pane>
      <el-tab-pane label="已收藏" name="favorites">
        <!-- 工具栏 -->
        <div class="toolbar">
          <el-select v-model="sortBy" placeholder="排序方式" @change="handleSort">
            <el-option label="最新创建" value="created_at" />
            <el-option label="最近更新" value="updated_at" />
            <el-option label="项目名称" value="name" />
          </el-select>

          <el-radio-group v-model="sortOrder" size="small" @change="handleSort">
            <el-radio-button label="desc">
              <el-icon><SortDown /></el-icon>
            </el-radio-button>
            <el-radio-button label="asc">
              <el-icon><SortUp /></el-icon>
            </el-radio-button>
          </el-radio-group>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 项目列表 -->
    <div v-loading="galleryStore.loading" class="projects-container">
      <!-- 空状态 -->
      <el-empty
        v-if="!galleryStore.hasProjects && !galleryStore.loading"
        description="暂无项目"
        :image-size="200"
      >
        <template #description>
          <div class="empty-content">
            <p class="empty-title">还没有任何公共项目</p>
            <p class="empty-desc">成为第一个分享您作品的人</p>
          </div>
        </template>
      </el-empty>

      <!-- 项目网格 -->
      <div v-else class="projects-grid">
        <ProjectCard
          v-for="project in galleryStore.projects"
          :key="project.id"
          :project="project"
          :is-public="true"
          @view="handleViewProject"
          @viewAuthor="handleViewAuthor"
        />
      </div>

      <!-- 分页 -->
      <div v-if="galleryStore.total > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="galleryStore.total"
          :page-sizes="[12, 24, 48]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, SortDown, SortUp } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import ProjectCard from '@/components/library/ProjectCard.vue'
import { useGalleryStore } from '@/stores/gallery'
import type { Project } from '@/types/project'

const router = useRouter()
const galleryStore = useGalleryStore()

// 搜索和排序状态
const activeTab = ref('all')
const searchType = ref<'project' | 'user'>('project')
const searchQuery = ref('')
const sortBy = ref('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')
const currentPage = ref(1)
const pageSize = ref(12)

// 加载公共项目列表
const loadProjects = async () => {
  try {
    if (activeTab.value === 'all') {
      await galleryStore.fetchPublicProjects({
        search_type: searchQuery.value ? searchType.value : undefined,
        search_value: searchQuery.value || undefined,
        sort_by: sortBy.value,
        sort_order: sortOrder.value,
        page: currentPage.value,
        page_size: pageSize.value
      })
    } else if (activeTab.value === 'favorites') {
      await galleryStore.fetchFavoriteProjects({
        sort_by: sortBy.value,
        sort_order: sortOrder.value,
        page: currentPage.value,
        page_size: pageSize.value
      })
    }
  } catch (error: any) {
    console.error('加载项目列表失败:', error)
    if (error.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/login')
    } else if (error.response?.status === 403) {
      ElMessage.error('没有权限访问')
    } else if (error.response?.status === 404) {
      ElMessage.error('资源不存在')
    } else {
      ElMessage.error(error.response?.data?.detail || '加载项目列表失败')
    }
  }
}

// 事件处理
const handleViewProject = (project: Project) => {
  router.push({ name: 'gallery-project-detail', params: { id: project.id } })
}

const handleViewAuthor = (userId: number) => {
  router.push({ name: 'gallery-user-detail', params: { id: userId } })
}

const handleTabChange = (tab: any) => {
  activeTab.value = tab.props.name
  currentPage.value = 1
  searchQuery.value = ''
  searchType.value = 'project'
  loadProjects()
}

const handleSearch = () => {
  currentPage.value = 1
  loadProjects()
}

const handleSort = () => {
  loadProjects()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadProjects()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadProjects()
}

// 页面加载时获取数据
onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.gallery-view {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .header-left {
    .page-title {
      margin: 0 0 8px;
      font-size: 28px;
      font-weight: 600;
      color: #303133;
    }

    .page-subtitle {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }
}

.toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);

  .search-container {
    display: flex;
    align-items: center;
    gap: 8px;

    .search-type-select {
      width: 120px;
    }

    .search-input {
      width: 300px;
    }
  }
}

.projects-container {
  min-height: 400px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
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

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}
</style>