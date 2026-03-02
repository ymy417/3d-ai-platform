<template>
  <div class="templates-view">
    <!-- 页面头部 -->
    <div class="header">
      <button class="home-btn" @click="goHome">
        <span class="home-icon">🏠</span> 返回主页
      </button>
      <div class="page-title">
        <h1>选择模板</h1>
        <p>从模板库中选择一个基础模型开始创作</p>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filter">
      <el-input
        v-model="searchQuery"
        placeholder="搜索模板"
        prefix-icon="Search"
        clearable
      />
      <el-select
        v-model="selectedCategory"
        placeholder="选择分类"
        clearable
      >
        <el-option label="全部" value="" />
        <el-option label="人物" value="character" />
        <el-option label="动物" value="animal" />
        <el-option label="道具" value="prop" />
        <el-option label="场景" value="scene" />
      </el-select>
    </div>

    <!-- 模板分类导航 -->
    <div class="category-nav">
      <el-button
        v-for="category in categories"
        :key="category.value"
        :type="selectedCategory === category.value ? 'primary' : 'default'"
        @click="selectedCategory = category.value"
      >
        {{ category.label }}
      </el-button>
    </div>

    <!-- 模板网格 -->
    <div class="templates-grid">
      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        class="template-card"
        @click="selectTemplate(template)"
      >
        <div class="template-preview">
          <img :src="template.preview" :alt="template.name" />
          <div class="template-overlay">
            <el-button type="primary" size="small">选择</el-button>
          </div>
        </div>
        <div class="template-info">
          <h3>{{ template.name }}</h3>
          <p>{{ template.description }}</p>
          <div class="template-meta">
            <span class="category">{{ getCategoryName(template.category) }}</span>
            <span class="difficulty">{{ getDifficultyLabel(template.difficulty) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredTemplates.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 模板详情弹窗 -->
    <el-dialog
      v-model="showTemplateDetail"
      :title="selectedTemplate?.name || '模板详情'"
      width="800px"
    >
      <div class="template-detail">
        <div class="detail-preview">
          <img :src="selectedTemplate?.preview" :alt="selectedTemplate?.name" />
        </div>
        <div class="detail-info">
          <h3>{{ selectedTemplate?.name }}</h3>
          <p>{{ selectedTemplate?.description }}</p>
          <div class="detail-meta">
            <div class="meta-item">
              <span class="label">分类：</span>
              <span class="value">{{ getCategoryName(selectedTemplate?.category) }}</span>
            </div>
            <div class="meta-item">
              <span class="label">难度：</span>
              <span class="value">{{ getDifficultyLabel(selectedTemplate?.difficulty) }}</span>
            </div>
            <div class="meta-item">
              <span class="label">文件大小：</span>
              <span class="value">{{ selectedTemplate?.fileSize }}</span>
            </div>
            <div class="meta-item">
              <span class="label">格式：</span>
              <span class="value">{{ selectedTemplate?.format }}</span>
            </div>
          </div>
          <div class="detail-tags">
            <el-tag v-for="tag in selectedTemplate?.tags" :key="tag" size="small">
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTemplateDetail = false">取消</el-button>
          <el-button type="primary" @click="confirmSelectTemplate">选择此模板</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 搜索和筛选
const searchQuery = ref('')
const selectedCategory = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(12)

// 模板数据（模拟数据）
const templates = ref([
  {
    id: 1,
    name: '基础人物模型',
    description: '一个标准的人体模型，适合作为角色创作的基础',
    category: 'character',
    difficulty: 'beginner',
    preview: 'https://via.placeholder.com/300x300?text=Character+Template',
    fileSize: '2.5 MB',
    format: 'glb',
    tags: ['人物', '基础', '通用']
  },
  {
    id: 2,
    name: '卡通角色模板',
    description: '风格化的卡通人物模型，适合动画和游戏',
    category: 'character',
    difficulty: 'intermediate',
    preview: 'https://via.placeholder.com/300x300?text=Cartoon+Character',
    fileSize: '3.2 MB',
    format: 'glb',
    tags: ['卡通', '角色', '动画']
  },
  {
    id: 3,
    name: '科幻机器人',
    description: '未来风格的机器人模型，带有机械细节',
    category: 'character',
    difficulty: 'advanced',
    preview: 'https://via.placeholder.com/300x300?text=Sci-Fi+Robot',
    fileSize: '4.8 MB',
    format: 'fbx',
    tags: ['科幻', '机器人', '未来']
  },
  {
    id: 4,
    name: '可爱小动物',
    description: 'Q版风格的小动物模型，适合儿童内容',
    category: 'animal',
    difficulty: 'beginner',
    preview: 'https://via.placeholder.com/300x300?text=Cute+Animal',
    fileSize: '1.8 MB',
    format: 'glb',
    tags: ['动物', '可爱', 'Q版']
  },
  {
    id: 5,
    name: '奇幻生物',
    description: '神话风格的奇幻生物模型，带有特殊特征',
    category: 'animal',
    difficulty: 'advanced',
    preview: 'https://via.placeholder.com/300x300?text=Mythical+Creature',
    fileSize: '5.2 MB',
    format: 'fbx',
    tags: ['奇幻', '生物', '神话']
  },
  {
    id: 6,
    name: '科幻武器',
    description: '未来风格的武器道具模型，带有细节设计',
    category: 'prop',
    difficulty: 'intermediate',
    preview: 'https://via.placeholder.com/300x300?text=Sci-Fi+Weapon',
    fileSize: '2.1 MB',
    format: 'obj',
    tags: ['武器', '科幻', '道具']
  },
  {
    id: 7,
    name: '魔法道具',
    description: '奇幻风格的魔法道具模型，适合游戏和动画',
    category: 'prop',
    difficulty: 'beginner',
    preview: 'https://via.placeholder.com/300x300?text=Magic+Prop',
    fileSize: '1.5 MB',
    format: 'glb',
    tags: ['魔法', '道具', '奇幻']
  },
  {
    id: 8,
    name: '未来城市',
    description: '科幻风格的城市场景模型，带有未来感设计',
    category: 'scene',
    difficulty: 'advanced',
    preview: 'https://via.placeholder.com/300x300?text=Future+City',
    fileSize: '8.5 MB',
    format: 'fbx',
    tags: ['城市', '科幻', '场景']
  },
  {
    id: 9,
    name: '森林场景',
    description: '自然风格的森林场景模型，适合环境创作',
    category: 'scene',
    difficulty: 'intermediate',
    preview: 'https://via.placeholder.com/300x300?text=Forest+Scene',
    fileSize: '6.2 MB',
    format: 'glb',
    tags: ['森林', '自然', '场景']
  },
  {
    id: 10,
    name: '太空站',
    description: '科幻风格的太空站模型，带有未来科技感',
    category: 'scene',
    difficulty: 'advanced',
    preview: 'https://via.placeholder.com/300x300?text=Space+Station',
    fileSize: '7.8 MB',
    format: 'fbx',
    tags: ['太空', '科幻', '场景']
  },
  {
    id: 11,
    name: '中世纪城堡',
    description: '奇幻风格的中世纪城堡模型，适合游戏场景',
    category: 'scene',
    difficulty: 'intermediate',
    preview: 'https://via.placeholder.com/300x300?text=Medieval+Castle',
    fileSize: '5.9 MB',
    format: 'glb',
    tags: ['城堡', '中世纪', '奇幻']
  },
  {
    id: 12,
    name: '未来车辆',
    description: '科幻风格的未来车辆模型，带有流线型设计',
    category: 'prop',
    difficulty: 'intermediate',
    preview: 'https://via.placeholder.com/300x300?text=Future+Vehicle',
    fileSize: '3.7 MB',
    format: 'obj',
    tags: ['车辆', '科幻', '未来']
  }
])

// 分类选项
const categories = [
  { label: '全部', value: '' },
  { label: '人物', value: 'character' },
  { label: '动物', value: 'animal' },
  { label: '道具', value: 'prop' },
  { label: '场景', value: 'scene' }
]

// 筛选后的模板
const filteredTemplates = computed(() => {
  let result = templates.value
  
  // 按分类筛选
  if (selectedCategory.value) {
    result = result.filter(template => template.category === selectedCategory.value)
  }
  
  // 按搜索词筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(template => 
      template.name.toLowerCase().includes(query) ||
      template.description.toLowerCase().includes(query) ||
      template.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  return result
})

// 分页后的模板
const paginatedTemplates = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTemplates.value.slice(start, end)
})

// 选中的模板
const selectedTemplate = ref<any>(null)
const showTemplateDetail = ref(false)

// 选择模板
const selectTemplate = (template: any) => {
  selectedTemplate.value = template
  showTemplateDetail.value = true
}

// 确认选择模板
const confirmSelectTemplate = () => {
  if (selectedTemplate.value) {
    // 跳转到建模页面，传递模板信息
    router.push({
      path: '/modeling',
      query: {
        projectId: `template_${selectedTemplate.value.id}`,
        templateId: selectedTemplate.value.id
      }
    })
    ElMessage.success(`已选择模板：${selectedTemplate.value.name}`)
  }
}

// 获取分类名称
const getCategoryName = (category: string | undefined) => {
  const cat = categories.find(c => c.value === category)
  return cat ? cat.label : '未知'
}

// 获取难度标签
const getDifficultyLabel = (difficulty: string | undefined) => {
  const labels: Record<string, string> = {
    beginner: '初级',
    intermediate: '中级',
    advanced: '高级'
  }
  return labels[difficulty || ''] || '未知'
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (current: number) => {
  currentPage.value = current
}

// 返回主页
const goHome = () => {
  router.push('/')
}

// 生命周期钩子
onMounted(() => {
  // 这里可以从API获取模板数据
  // 暂时使用模拟数据
})
</script>

<style scoped>
.templates-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: #f5f7fa;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
  position: relative;
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

.page-title h1 {
  font-size: 2.5rem;
  color: #333;
  margin: 0;
}

.page-title p {
  color: #666;
  margin: 0.5rem 0 0;
  font-size: 1.1rem;
}

.search-filter {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-filter .el-input {
  flex: 1;
  min-width: 300px;
}

.category-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.template-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  cursor: pointer;
}

.template-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.template-preview {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.template-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.template-card:hover .template-preview img {
  transform: scale(1.05);
}

.template-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.template-card:hover .template-overlay {
  opacity: 1;
}

.template-info {
  padding: 1.5rem;
}

.template-info h3 {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
  color: #333;
}

.template-info p {
  margin: 0 0 1rem;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #999;
}

.category, .difficulty {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  background: #f0f0f0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 3rem;
}

.template-detail {
  display: flex;
  gap: 2rem;
}

.detail-preview {
  flex: 1;
  max-width: 300px;
}

.detail-preview img {
  width: 100%;
  border-radius: 8px;
}

.detail-info {
  flex: 1;
}

.detail-info h3 {
  margin: 0 0 1rem;
  font-size: 1.5rem;
  color: #333;
}

.detail-info p {
  margin: 0 0 1.5rem;
  color: #666;
  line-height: 1.5;
}

.detail-meta {
  margin-bottom: 1.5rem;
}

.meta-item {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
}

.meta-item .label {
  font-weight: 600;
  margin-right: 0.5rem;
  color: #333;
  min-width: 80px;
}

.meta-item .value {
  color: #666;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

@media (max-width: 768px) {
  .templates-view {
    padding: 1rem;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .search-filter {
    flex-direction: column;
  }
  
  .search-filter .el-input {
    min-width: auto;
  }
  
  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .template-detail {
    flex-direction: column;
  }
  
  .detail-preview {
    max-width: 100%;
  }
}
</style>