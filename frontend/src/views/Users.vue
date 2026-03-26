<template>
  <div>
    <el-card shadow="never" class="search-card">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="姓名/用户名" clearable @keyup.enter="search" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">搜索</el-button>
          <el-button type="success" @click="openForm()">添加员工</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="list" stripe v-loading="loading" border size="small">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'manager' ? 'warning' : 'info'" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ row.created_at?.substring(0,19) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openForm(row)">编辑</el-button>
            <el-button link type="warning" @click="resetPwd(row)">重置密码</el-button>
            <el-popconfirm title="确定禁用此账号？" @confirm="handleDisable(row.id)">
              <template #reference><el-button link type="danger" :disabled="!row.is_active">禁用</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        style="margin-top:12px;justify-content:flex-end"
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[20,50,100]"
        layout="total, sizes, prev, pager, next"
        @change="fetchList"
      />
    </el-card>

    <!-- 新增/编辑 -->
    <el-dialog v-model="formVisible" :title="formData.id ? '编辑员工' : '添加员工'" width="500px" destroy-on-close>
      <el-form :model="formData" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="formData.username" :disabled="!!formData.id" /></el-form-item>
        <el-form-item v-if="!formData.id" label="密码"><el-input v-model="formData.password" type="password" placeholder="初始密码" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="formData.real_name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="formData.phone" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="formData.role">
            <el-option label="管理员" value="admin" />
            <el-option label="主管" value="manager" />
            <el-option label="员工" value="staff" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const formVisible = ref(false)
const query = ref({ page: 1, page_size: 20, keyword: '' })
const formData = ref({})

const roleLabel = (r) => ({ admin: '管理员', manager: '主管', staff: '员工' }[r] || r)

async function fetchList() {
  loading.value = true
  try {
    const { data } = await api.get('/users', { params: query.value })
    list.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

function search() { query.value.page = 1; fetchList() }

function openForm(row) {
  formData.value = row ? { ...row } : { username: '', password: '', real_name: '', phone: '', role: 'staff' }
  formVisible.value = true
}

async function handleSave() {
  if (!formData.value.username || !formData.value.real_name) return ElMessage.warning('请填写用户名和姓名')
  if (!formData.value.id && !formData.value.password) return ElMessage.warning('请设置初始密码')
  saving.value = true
  try {
    if (formData.value.id) {
      await api.put(`/users/${formData.value.id}`, { real_name: formData.value.real_name, phone: formData.value.phone, role: formData.value.role })
    } else {
      await api.post('/users', formData.value)
    }
    ElMessage.success('保存成功')
    formVisible.value = false
    fetchList()
  } finally { saving.value = false }
}

async function handleDisable(id) {
  await api.delete(`/users/${id}`)
  ElMessage.success('已禁用')
  fetchList()
}

async function resetPwd(row) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新密码', '重置密码', { inputType: 'password' })
    if (value) {
      // 管理员直接更新密码 - 需要后端支持，此处简化
      await api.put(`/users/${row.id}`, { password: value })
      ElMessage.success('密码已重置')
    }
  } catch {}
}

onMounted(fetchList)
</script>

<style scoped>
.search-card :deep(.el-card__body) { padding-bottom: 0; }
</style>
