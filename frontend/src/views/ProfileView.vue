<template>
  <div class="profile-container">
    <div class="profile-header">
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
          <el-form-item label="用户名">
            <el-input
              v-model="profileForm.username"
              :disabled="!isEditing"
              placeholder="用户名"
            />
          </el-form-item>

          <el-form-item label="邮箱">
            <el-input :model-value="authStore.user?.email || ''" disabled />
          </el-form-item>

          <el-form-item label="手机号">
            <el-input
              v-model="profileForm.phone"
              :disabled="!isEditing"
              placeholder="手机号"
            />
          </el-form-item>

          <el-form-item label="头像">
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
          </el-form-item>

          <el-form-item label="角色">
            <el-tag :type="getRoleType(authStore.user?.role)">
              {{ getRoleName(authStore.user?.role) }}
            </el-tag>
          </el-form-item>

          <el-form-item label="注册时间">
            <span>{{ formatDate(authStore.user?.created_at) }}</span>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="password-card">
        <template #header>
          <span>修改密码</span>
        </template>

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

          <el-form-item>
            <el-button
              type="primary"
              :loading="changingPassword"
              @click="changePassword"
            >
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const authStore = useAuthStore()

const isEditing = ref(false)
const changingPassword = ref(false)

const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const profileForm = reactive({
  username: '',
  phone: '',
  avatar_url: '',
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const profileRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' },
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

onMounted(() => {
  if (authStore.user) {
    profileForm.username = authStore.user.username
    profileForm.phone = authStore.user.phone || ''
    profileForm.avatar_url = authStore.user.avatar_url || ''
  }
})

function startEdit() {
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  if (authStore.user) {
    profileForm.username = authStore.user.username
    profileForm.phone = authStore.user.phone || ''
    profileForm.avatar_url = authStore.user.avatar_url || ''
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
        passwordForm.oldPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
      } else {
        ElMessage.error(authStore.error || '密码修改失败')
      }
    }
  })
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

function formatDate(date?: string) {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  margin-bottom: 24px;
}

.profile-header h1 {
  font-size: 24px;
  color: #333;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card,
.password-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
