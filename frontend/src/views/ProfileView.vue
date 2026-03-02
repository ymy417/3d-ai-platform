<template>
  <div class="profile-container">
    <div class="profile-header">
      <button class="home-btn" @click="goHome">
        <span class="home-icon">🏠</span> 返回主页
      </button>
      <h1>个人中心</h1>
    </div>

    <div class="profile-content">
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-button
              v-if="!isEditing"
              type="primary"
              size="small"
              @click="startEdit"
            >
              编辑
            </el-button>
            <div v-else>
              <el-button size="small" @click="cancelEdit">取消</el-button>
              <el-button type="primary" size="small" @click="saveEdit">保存</el-button>
            </div>
          </div>
        </template>

        <el-form
          ref="profileFormRef"
          :model="profileForm"
          :rules="profileRules"
          label-width="100px"
        >
          <el-form-item label="头像">
            <div class="avatar-section">
              <el-avatar
                :size="80"
                :src="profileForm.avatar_url || undefined"
                icon="User"
              />
              <el-input
                v-if="isEditing"
                v-model="profileForm.avatar_url"
                placeholder="头像URL"
                style="margin-top: 8px"
              />
            </div>
          </el-form-item>

          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="profileForm.username"
              :disabled="!isEditing"
              placeholder="用户名"
            />
          </el-form-item>

          <el-form-item label="邮箱">
            <el-input :model-value="authStore.user?.email || ''" disabled />
          </el-form-item>

          <el-form-item label="性别" prop="gender">
            <el-select
              v-model="profileForm.gender"
              :disabled="!isEditing"
              placeholder="请选择性别"
              style="width: 100%"
            >
              <el-option label="👨 男" value="male" />
              <el-option label="👩 女" value="female" />
              <el-option label="🤫 保密" value="secret" />
            </el-select>
          </el-form-item>

          <el-form-item label="手机号" prop="phone">
            <el-input
              v-model="profileForm.phone"
              :disabled="!isEditing"
              placeholder="手机号"
            />
          </el-form-item>

          <el-form-item label="个人签名" prop="bio">
            <el-input
              v-model="profileForm.bio"
              type="textarea"
              :rows="3"
              :disabled="!isEditing"
              placeholder="介绍一下自己吧..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="角色">
            <el-tag :type="getRoleType(authStore.user?.role)">
              {{ getRoleName(authStore.user?.role) }}
            </el-tag>
          </el-form-item>

          <el-form-item label="注册时间">
            <span>{{ formatDate(authStore.user?.created_at) }}</span>
          </el-form-item>

          <el-form-item>
            <el-button
              type="warning"
              :icon="Lock"
              @click="showPasswordDialog = true"
            >
              修改密码
            </el-button>
            <el-button
              type="info"
              :icon="Message"
              @click="showAppealDialog = true"
            >
              提交申诉
            </el-button>
            <el-button
              type="danger"
              :icon="SwitchButton"
              @click="handleLogout"
              style="margin-left: 12px"
            >
              退出登录
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 我的申诉记录 -->
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <span>我的申诉记录</span>
          </div>
        </template>
        <el-table :data="myAppeals" v-loading="appealsLoading" style="width: 100%">
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getAppealTypeType(row.type)">
                {{ getAppealTypeName(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getAppealStatusType(row.status)">
                {{ getAppealStatusName(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="提交时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" @click="showAppealDetail(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="400px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            placeholder="旧密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="新密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="确认密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="changingPassword"
          @click="changePassword"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>

    <!-- 提交申诉对话框 -->
    <el-dialog
      v-model="showAppealDialog"
      title="提交申诉"
      width="500px"
    >
      <el-form
        ref="appealFormRef"
        :model="appealForm"
        :rules="appealRules"
        label-width="100px"
      >
        <el-form-item label="申诉类型" prop="type">
          <el-select v-model="appealForm.type" style="width: 100%">
            <el-option label="账号问题" value="account" />
            <el-option label="内容问题" value="content" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input
            v-model="appealForm.title"
            placeholder="请输入申诉标题"
          />
        </el-form-item>

        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="appealForm.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述您的问题..."
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAppealDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="submittingAppeal"
          @click="submitAppeal"
        >
          提交申诉
        </el-button>
      </template>
    </el-dialog>

    <!-- 申诉详情对话框 -->
    <el-dialog
      v-model="appealDetailVisible"
      title="申诉详情"
      width="500px"
    >
      <div v-if="currentAppeal" class="appeal-detail">
        <div class="detail-item">
          <span class="label">标题：</span>
          <span>{{ currentAppeal.title }}</span>
        </div>
        <div class="detail-item">
          <span class="label">类型：</span>
          <el-tag :type="getAppealTypeType(currentAppeal.type)">
            {{ getAppealTypeName(currentAppeal.type) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <span class="label">状态：</span>
          <el-tag :type="getAppealStatusType(currentAppeal.status)">
            {{ getAppealStatusName(currentAppeal.status) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <span class="label">描述：</span>
          <p class="description">{{ currentAppeal.description }}</p>
        </div>
        <div v-if="currentAppeal.admin_response" class="detail-item">
          <span class="label">管理员回复：</span>
          <p class="admin-response">{{ currentAppeal.admin_response }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { Lock, SwitchButton, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { appealApi } from '@/api/appeal'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Appeal } from '@/types/appeal'

const authStore = useAuthStore()
const router = useRouter()

const goHome = () => {
  router.push('/')
}

const isEditing = ref(false)
const changingPassword = ref(false)
const showPasswordDialog = ref(false)
const showAppealDialog = ref(false)
const submittingAppeal = ref(false)
const appealsLoading = ref(false)
const appealDetailVisible = ref(false)
const currentAppeal = ref<any>(null)

const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const appealFormRef = ref<FormInstance>()

const profileForm = reactive({
  username: '',
  phone: '',
  avatar_url: '',
  gender: 'secret' as 'male' | 'female' | 'secret',
  bio: '',
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const appealForm = reactive({
  type: 'account',
  title: '',
  description: '',
})

const myAppeals = ref<Appeal[]>([])

const profileRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' },
  ],
  bio: [
    { max: 500, message: '个人签名不能超过500个字符', trigger: 'blur' },
  ],
}

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' },
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度为6-100个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const appealRules: FormRules = {
  type: [
    { required: true, message: '请选择申诉类型', trigger: 'change' },
  ],
  title: [
    { required: true, message: '请输入申诉标题', trigger: 'blur' },
    { max: 200, message: '标题不能超过200个字符', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入详细描述', trigger: 'blur' },
    { max: 1000, message: '描述不能超过1000个字符', trigger: 'blur' },
  ],
}

onMounted(() => {
  if (authStore.user) {
    profileForm.username = authStore.user.username
    profileForm.phone = authStore.user.phone || ''
    profileForm.avatar_url = authStore.user.avatar_url || ''
    profileForm.gender = authStore.user.gender || 'secret'
    profileForm.bio = authStore.user.bio || ''
  }
  fetchMyAppeals()
})

async function fetchMyAppeals() {
  appealsLoading.value = true
  try {
    const appeals = await appealApi.getMyAppeals()
    myAppeals.value = appeals
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '获取申诉列表失败')
  } finally {
    appealsLoading.value = false
  }
}

function startEdit() {
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  if (authStore.user) {
    profileForm.username = authStore.user.username
    profileForm.phone = authStore.user.phone || ''
    profileForm.avatar_url = authStore.user.avatar_url || ''
    profileForm.gender = authStore.user.gender || 'secret'
    profileForm.bio = authStore.user.bio || ''
  }
}

async function saveEdit() {
  if (!profileFormRef.value) return

  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await authStore.updateProfile({
        username: profileForm.username,
        phone: profileForm.phone,
        avatar_url: profileForm.avatar_url,
        gender: profileForm.gender,
        bio: profileForm.bio,
      })

      if (success) {
        ElMessage.success('更新成功')
        isEditing.value = false
      } else {
        ElMessage.error(authStore.error || '更新失败')
      }
    }
  })
}

async function changePassword() {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      changingPassword.value = true
      const success = await authStore.changePassword(
        passwordForm.oldPassword,
        passwordForm.newPassword
      )
      changingPassword.value = false

      if (success) {
        ElMessage.success('密码修改成功')
        showPasswordDialog.value = false
        passwordForm.oldPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
      } else {
        ElMessage.error(authStore.error || '密码修改失败')
      }
    }
  })
}

async function submitAppeal() {
  if (!appealFormRef.value) return

  await appealFormRef.value.validate(async (valid) => {
    if (valid) {
      submittingAppeal.value = true
      try {
        await appealApi.createAppeal({
          type: appealForm.type as 'account' | 'content' | 'other',
          title: appealForm.title,
          description: appealForm.description,
        })
        ElMessage.success('申诉提交成功，管理员会尽快处理')
        showAppealDialog.value = false
        appealForm.type = 'account'
        appealForm.title = ''
        appealForm.description = ''
        fetchMyAppeals()
      } catch (err: any) {
        ElMessage.error(err.response?.data?.detail || '申诉提交失败')
      } finally {
        submittingAppeal.value = false
      }
    }
  })
}

function showAppealDetail(appeal: any) {
  currentAppeal.value = appeal
  appealDetailVisible.value = true
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await authStore.logout()
    ElMessage.success('已退出登录')
  } catch {
    // 用户取消
  }
}

function getRoleName(role?: string) {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    creator: '创作者',
    viewer: '查看者',
  }
  return roleMap[role || 'viewer'] || '查看者'
}

function getRoleType(role?: string) {
  const typeMap: Record<string, string> = {
    admin: 'danger',
    creator: 'warning',
    viewer: 'info',
  }
  return typeMap[role || 'viewer'] || 'info'
}

function getAppealTypeName(type: string) {
  const typeMap: Record<string, string> = {
    account: '账号问题',
    content: '内容问题',
    other: '其他'
  }
  return typeMap[type] || type
}

function getAppealTypeType(type: string) {
  const typeMap: Record<string, string> = {
    account: 'danger',
    content: 'warning',
    other: 'info'
  }
  return typeMap[type] || 'info'
}

function getAppealStatusName(status: string) {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

function getAppealStatusType(status: string) {
  const typeMap: Record<string, string> = {
    pending: 'danger',
    processing: 'warning',
    resolved: 'success',
    rejected: 'info'
  }
  return typeMap[status] || 'info'
}

function formatDate(date?: string) {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 24px;
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

.profile-header h1 {
  font-size: 24px;
  color: #333;
  margin: 0;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.appeal-detail {
  .detail-item {
    margin-bottom: 16px;
    
    .label {
      font-weight: bold;
      color: #606266;
    }
    
    .description {
      margin: 8px 0 0 0;
      padding: 12px;
      background-color: #f5f7fa;
      border-radius: 4px;
      color: #606266;
      line-height: 1.6;
    }
    
    .admin-response {
      margin: 8px 0 0 0;
      padding: 12px;
      background-color: #f0f9ff;
      border-radius: 4px;
      color: #409EFF;
      line-height: 1.6;
    }
  }
}
</style>
