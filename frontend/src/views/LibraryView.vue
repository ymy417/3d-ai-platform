<template>
  <div class="library-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button type="primary" plain @click="goHome">
          <el-icon><House /></el-icon>返回主页
        </el-button>
        <h1 class="page-title">我的项目库</h1>
        <p class="page-subtitle">管理和查看您的所有3D项目</p>
      </div>
      <el-button type="primary" size="large" @click="handleCreate">
        <el-icon><Plus /></el-icon>新建项目
      </el-button>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索项目名称"
        clearable
        class="search-input"
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select v-model="filterStatus" placeholder="筛选状态" clearable @change="handleFilter">
        <el-option label="草稿" value="draft" />
        <el-option label="处理中" value="processing" />
        <el-option label="已完成" value="completed" />
        <el-option label="已归档" value="archived" />
      </el-select>

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

    <!-- 项目列表 -->
    <div v-loading="projectStore.loading" class="projects-container">
      <!-- 空状态 -->
      <el-empty
        v-if="!projectStore.hasProjects && !projectStore.loading"
        description="暂无项目"
        :image-size="200"
      >
        <template #description>
          <div class="empty-content">
            <p class="empty-title">还没有任何项目</p>
            <p class="empty-desc">点击上方按钮创建您的第一个3D项目</p>
          </div>
        </template>
        <el-button type="primary" @click="handleCreate">立即创建</el-button>
      </el-empty>

      <!-- 项目网格 -->
      <div v-else class="projects-grid">
        <ProjectCard
          v-for="project in projectStore.projects"
          :key="project.id"
          :project="project"
          :is-public="false"
          @edit="handleEdit"
          @delete="handleDeleteSuccess"
          @view="handleViewProject"
        />
      </div>

      <!-- 分页 -->
      <div v-if="projectStore.total > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="projectStore.total"
          :page-sizes="[12, 24, 48]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 项目表单弹窗 -->
    <ProjectForm
      v-model="formVisible"
      :project="editingProject"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, SortDown, SortUp, House } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ProjectCard from '@/components/library/ProjectCard.vue'
import ProjectForm from '@/components/library/ProjectForm.vue'
import { useProjectStore } from '@/stores/projects'
import type { Project } from '@/types/project'

const projectStore = useProjectStore()
const router = useRouter()

// 搜索和筛选状态
const searchQuery = ref('')
const filterStatus = ref('')
const sortBy = ref('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')
const currentPage = ref(1)
const pageSize = ref(12)

// 表单状态
const formVisible = ref(false)
const editingProject = ref<Project | null>(null)

// 加载项目列表
const loadProjects = async () => {
  try {
    await projectStore.fetchProjects({
      search: searchQuery.value || undefined,
      status: filterStatus.value || undefined,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      page: currentPage.value,
      page_size: pageSize.value
    })
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  }
}

// 事件处理
const handleCreate = () => {
  editingProject.value = null
  formVisible.value = true
}

const handleEdit = (project: Project) => {
  editingProject.value = project
  formVisible.value = true
}

const handleFormSuccess = () => {
  loadProjects()
}

const handleDeleteSuccess = () => {
  loadProjects()
}

const handleViewProject = (project: Project) => {
  router.push(`/library/project/${project.id}`)
}

const handleSearch = () => {
  currentPage.value = 1
  loadProjects()
}

const handleFilter = () => {
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

const goHome = () => {
  router.push('/')
}

// 监听分页变化
watch([currentPage, pageSize], () => {
  projectStore.setPage(currentPage.value)
})

// 页面加载时获取数据
onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.library-view {
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
    display: flex;
    flex-direction: column;
    gap: 12px;

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

  .search-input {
    width: 300px;
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
