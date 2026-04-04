<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <el-icon size="24"><OfficeBuilding /></el-icon>
        <span v-show="!isCollapse">资料管理系统</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        :collapse="isCollapse"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        <el-menu-item index="/companies">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>公司资料</template>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <template #title>任务管理</template>
        </el-menu-item>
        <el-menu-item index="/documents">
          <el-icon><FolderOpened /></el-icon>
          <template #title>文件管理</template>
        </el-menu-item>
        <el-menu-item index="/phone-pool">
          <el-icon><Phone /></el-icon>
          <template #title>电话库</template>
        </el-menu-item>
        <el-menu-item index="/email-pool">
          <el-icon><Message /></el-icon>
          <template #title>邮箱库</template>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Grid /></el-icon>
          <template #title>产品条码</template>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <template #title>员工管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse" size="20">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <span class="page-title">{{ $route.meta.title }}</span>
        </div>
        <div class="header-right">
          <span class="username">{{ userStore.user?.real_name }}</span>
          <el-dropdown @command="handleCommand">
            <el-avatar :size="32">{{ userStore.user?.real_name?.[0] }}</el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <!-- 修改密码 -->
  <el-dialog v-model="pwdVisible" title="修改密码" width="400px">
    <el-form :model="pwdForm" label-width="80px">
      <el-form-item label="原密码"><el-input v-model="pwdForm.old_password" type="password" /></el-form-item>
      <el-form-item label="新密码"><el-input v-model="pwdForm.new_password" type="password" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="pwdVisible = false">取消</el-button>
      <el-button type="primary" @click="changePwd">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import api from '../utils/api'

const userStore = useUserStore()
const router = useRouter()
const isCollapse = ref(false)
const pwdVisible = ref(false)
const pwdForm = ref({ old_password: '', new_password: '' })

onMounted(async () => {
  if (userStore.token && !userStore.user) {
    try { await userStore.fetchUser() } catch { userStore.logout(); router.push('/login') }
  }
})

function handleCommand(cmd) {
  if (cmd === 'logout') { userStore.logout(); router.push('/login') }
  if (cmd === 'password') { pwdVisible.value = true; pwdForm.value = { old_password: '', new_password: '' } }
}

async function changePwd() {
  await api.post('/auth/change-password', pwdForm.value)
  ElMessage.success('密码修改成功')
  pwdVisible.value = false
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.aside { background: #304156; overflow-y: auto; transition: width 0.3s; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; gap: 8px; color: #fff; font-size: 16px; font-weight: bold; }
.header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #eee; background: #fff; }
.header-left { display: flex; align-items: center; gap: 12px; }
.collapse-btn { cursor: pointer; }
.page-title { font-size: 16px; font-weight: 500; }
.header-right { display: flex; align-items: center; gap: 12px; }
.username { font-size: 14px; color: #666; }
.main { background: #f5f7fa; }
</style>
