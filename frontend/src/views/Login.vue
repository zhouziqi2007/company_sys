<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="title">任务分发及资料管理系统</h2>
      <el-form :model="form" @keyup.enter="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width:100%" :loading="loading" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const form = ref({ username: '', password: '' })
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore()

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    return ElMessage.warning('请输入用户名和密码')
  }
  loading.value = true
  try {
    await userStore.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container { height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.login-card { width: 400px; padding: 20px; }
.title { text-align: center; margin-bottom: 30px; color: #303133; }
</style>
