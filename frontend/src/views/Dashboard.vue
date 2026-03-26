<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-row">
      <el-col :span="4" v-for="item in statCards" :key="item.key">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats[item.key] || 0 }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card>
          <template #header>我的待办任务</template>
          <el-table :data="myTasks" stripe size="small" max-height="400">
            <el-table-column prop="title" label="任务" />
            <el-table-column prop="company_name" label="公司" width="160" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="priorityType(row.priority)" size="small">{{ priorityLabel(row.priority) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>最近公司资料</template>
          <el-table :data="recentCompanies" stripe size="small" max-height="400">
            <el-table-column prop="name" label="公司名称" />
            <el-table-column prop="legal_person" label="法人" width="100" />
            <el-table-column prop="license_status" label="执照状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.license_status)" size="small">{{ licenseLabel(row.license_status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'

const stats = ref({})
const myTasks = ref([])
const recentCompanies = ref([])

const statCards = [
  { key: 'company_count', label: '公司总数' },
  { key: 'task_total', label: '任务总数' },
  { key: 'task_pending', label: '待处理' },
  { key: 'task_in_progress', label: '进行中' },
  { key: 'task_completed', label: '已完成' },
  { key: 'user_count', label: '员工数' },
]

const statusType = (s) => ({ pending: 'info', in_progress: '', processing: '', submitted: 'warning', approved: 'success', completed: 'success', rejected: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待处理', in_progress: '进行中', submitted: '已提交', approved: '已审核', completed: '已完成', rejected: '已驳回' }[s] || s)
const priorityType = (p) => ({ low: 'info', medium: '', high: 'warning', urgent: 'danger' }[p] || '')
const priorityLabel = (p) => ({ low: '低', medium: '中', high: '高', urgent: '紧急' }[p] || p)
const licenseLabel = (s) => ({ pending: '待办理', processing: '办理中', completed: '已完成', rejected: '已驳回' }[s] || s)

onMounted(async () => {
  const [s, t, c] = await Promise.all([
    api.get('/tasks/stats/overview'),
    api.get('/tasks', { params: { page_size: 10, status: 'in_progress' } }),
    api.get('/companies', { params: { page_size: 10 } }),
  ])
  stats.value = s.data
  myTasks.value = t.data.items
  recentCompanies.value = c.data.items
})
</script>

<style scoped>
.stat-row { margin-bottom: 10px; }
.stat-card { text-align: center; }
.stat-value { font-size: 28px; font-weight: bold; color: #409eff; }
.stat-label { font-size: 13px; color: #999; margin-top: 6px; }
</style>
