<template>
  <div>
    <!-- 搜索 -->
    <el-card shadow="never" class="search-card">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="任务标题" clearable @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="query.task_type" clearable placeholder="全部">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="query.assignee_id" clearable filterable placeholder="全部">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.real_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
          <el-button type="success" @click="openForm()">新建任务</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格 -->
    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="list" stripe v-loading="loading" border size="small">
        <el-table-column prop="title" label="任务标题" min-width="180" />
        <el-table-column prop="task_type" label="类型" width="100">
          <template #default="{ row }"><el-tag size="small">{{ typeLabel(row.task_type) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="company_name" label="关联公司" width="160" />
        <el-table-column prop="assignee_name" label="负责人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }"><el-tag :type="priorityType(row.priority)" size="small">{{ priorityLabel(row.priority) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止日期" width="110">
          <template #default="{ row }">{{ row.deadline ? row.deadline.substring(0,10) : '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openForm(row)">编辑</el-button>
            <el-button link type="primary" @click="openAssign(row)">分配</el-button>
            <el-button link type="primary" @click="viewLogs(row)">日志</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button link type="danger">删除</el-button></template>
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

    <!-- 新建/编辑任务 -->
    <el-dialog v-model="formVisible" :title="formData.id ? '编辑任务' : '新建任务'" width="600px" destroy-on-close>
      <el-form :model="formData" label-width="90px">
        <el-form-item label="任务标题"><el-input v-model="formData.title" /></el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="formData.task_type">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联公司">
          <el-select v-model="formData.company_id" filterable remote :remote-method="searchCompanies" placeholder="搜索公司">
            <el-option v-for="c in companyOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="formData.assignee_id" clearable filterable placeholder="选择负责人">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.real_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="formData.priority">
            <el-option label="低" value="low" /><el-option label="中" value="medium" />
            <el-option label="高" value="high" /><el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="formData.deadline" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item v-if="formData.id" label="状态">
          <el-select v-model="formData.status">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="formData.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 分配 -->
    <el-dialog v-model="assignVisible" title="分配任务" width="400px">
      <el-form label-width="80px">
        <el-form-item label="负责人">
          <el-select v-model="assignUserId" filterable placeholder="选择负责人" style="width:100%">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.real_name" :value="u.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAssign">确定分配</el-button>
      </template>
    </el-dialog>

    <!-- 日志 -->
    <el-drawer v-model="logVisible" title="任务日志" size="450px">
      <el-timeline>
        <el-timeline-item v-for="log in logs" :key="log.id" :timestamp="log.created_at?.substring(0,19)" placement="top">
          <strong>{{ log.operator_name }}</strong> - {{ log.action }}
          <p style="color:#666">{{ log.content }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const formVisible = ref(false)
const assignVisible = ref(false)
const logVisible = ref(false)
const logs = ref([])
const assignTaskId = ref(0)
const assignUserId = ref(null)
const userOptions = ref([])
const companyOptions = ref([])
const query = ref({ page: 1, page_size: 20, keyword: '', status: '', task_type: '', assignee_id: '' })
const formData = ref({})

const statusOptions = [
  { label: '待处理', value: 'pending' }, { label: '进行中', value: 'in_progress' },
  { label: '已提交', value: 'submitted' }, { label: '已审核', value: 'approved' },
  { label: '已驳回', value: 'rejected' }, { label: '已完成', value: 'completed' },
]
const typeOptions = [
  { label: '执照注册', value: 'license_reg' }, { label: '银行开户', value: 'bank_account' },
  { label: '变更', value: 'change' }, { label: '注销', value: 'cancel' }, { label: '其他', value: 'other' },
]

const statusType = (s) => ({ pending: 'info', in_progress: '', submitted: 'warning', approved: 'success', completed: 'success', rejected: 'danger' }[s] || 'info')
const statusLabel = (s) => statusOptions.find(o => o.value === s)?.label || s
const typeLabel = (t) => typeOptions.find(o => o.value === t)?.label || t
const priorityType = (p) => ({ low: 'info', medium: '', high: 'warning', urgent: 'danger' }[p] || '')
const priorityLabel = (p) => ({ low: '低', medium: '中', high: '高', urgent: '紧急' }[p] || p)

async function fetchList() {
  loading.value = true
  try {
    const params = { ...query.value }
    if (!params.assignee_id) delete params.assignee_id
    const { data } = await api.get('/tasks', { params })
    list.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

function search() { query.value.page = 1; fetchList() }
function resetQuery() { query.value = { page: 1, page_size: 20, keyword: '', status: '', task_type: '', assignee_id: '' }; fetchList() }

function openForm(row) {
  formData.value = row ? { ...row } : { title: '', task_type: 'license_reg', description: '', company_id: null, assignee_id: null, priority: 'medium', deadline: null }
  if (row?.company_id) companyOptions.value = [{ id: row.company_id, name: row.company_name }]
  formVisible.value = true
}

async function searchCompanies(kw) {
  if (!kw) return
  const { data } = await api.get('/companies', { params: { keyword: kw, page_size: 20 } })
  companyOptions.value = data.items
}

async function handleSave() {
  if (!formData.value.title || !formData.value.company_id) return ElMessage.warning('请填写标题和关联公司')
  saving.value = true
  try {
    if (formData.value.id) {
      await api.put(`/tasks/${formData.value.id}`, formData.value)
    } else {
      await api.post('/tasks', formData.value)
    }
    ElMessage.success('保存成功')
    formVisible.value = false
    fetchList()
  } finally { saving.value = false }
}

function openAssign(row) { assignTaskId.value = row.id; assignUserId.value = row.assignee_id; assignVisible.value = true }

async function handleAssign() {
  if (!assignUserId.value) return ElMessage.warning('请选择负责人')
  await api.post(`/tasks/${assignTaskId.value}/assign?assignee_id=${assignUserId.value}`)
  ElMessage.success('分配成功')
  assignVisible.value = false
  fetchList()
}

async function viewLogs(row) {
  const { data } = await api.get(`/tasks/${row.id}/logs`)
  logs.value = data
  logVisible.value = true
}

async function handleDelete(id) {
  await api.delete(`/tasks/${id}`)
  ElMessage.success('已删除')
  fetchList()
}

onMounted(async () => {
  const { data } = await api.get('/users/options')
  userOptions.value = data
  fetchList()
})
</script>

<style scoped>
.search-card :deep(.el-card__body) { padding-bottom: 0; }
</style>
