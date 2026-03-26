<template>
  <div>
    <!-- 搜索区 -->
    <el-card shadow="never" class="search-card">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="电话号码/银行标签/备注" clearable @keyup.enter="search" style="width:220px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="可用" value="available" />
            <el-option label="已领用" value="claimed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">搜索</el-button>
          <el-button type="success" @click="openAddDialog">添加号码</el-button>
          <el-button type="warning" @click="openBatchDialog">批量导入</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="list" stripe v-loading="loading" border size="small">
        <el-table-column prop="phone_number" label="电话号码" width="150" />
        <el-table-column prop="sms_api" label="短信API" width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'available' ? 'success' : 'warning'" size="small">
              {{ row.status === 'available' ? '可用' : '已领用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="claimer_name" label="领用人" width="100" />
        <el-table-column prop="company_name" label="关联公司" width="180" show-overflow-tooltip />
        <el-table-column prop="bank_label" label="银行标签" width="140" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ row.created_at?.substring(0, 19) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'available'" link type="primary" @click="openClaimDialog(row)">领用</el-button>
            <el-button v-if="row.status === 'claimed'" link type="warning" @click="handleRelease(row)">释放</el-button>
            <el-button link type="info" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除此号码？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger" :disabled="row.status === 'claimed'">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        style="margin-top:12px;justify-content:flex-end"
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @change="fetchList"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="formVisible" :title="isEdit ? '编辑号码' : '添加号码'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="电话号码" required>
          <el-input v-model="form.phone_number" placeholder="请输入电话号码" />
        </el-form-item>
        <el-form-item label="短信API">
          <el-input v-model="form.sms_api" placeholder="短信API地址" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="batchVisible" title="批量导入号码" width="500px">
      <el-form label-width="90px">
        <el-form-item label="短信API">
          <el-input v-model="batchSmsApi" placeholder="统一短信API（可选）" />
        </el-form-item>
        <el-form-item label="电话号码">
          <el-input v-model="batchText" type="textarea" :rows="8" placeholder="每行一个电话号码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatch">导入</el-button>
      </template>
    </el-dialog>

    <!-- 领用对话框 -->
    <el-dialog v-model="claimVisible" title="领用号码" width="520px">
      <el-descriptions :column="1" border size="small" style="margin-bottom:16px">
        <el-descriptions-item label="电话号码">{{ claimPhone?.phone_number }}</el-descriptions-item>
      </el-descriptions>
      <el-form :model="claimForm" label-width="90px">
        <el-form-item label="关联公司" required>
          <el-select v-model="claimForm.company_id" filterable remote :remote-method="searchCompanies"
            placeholder="搜索公司" style="width:100%" @change="onCompanyChange">
            <el-option v-for="c in companyOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联银行">
          <el-select v-model="claimForm.bank_account_id" clearable placeholder="选择银行(可选)" style="width:100%">
            <el-option v-for="b in bankOptions" :key="b.id" :label="`${b.bank_name} (${b.label || b.account_type})`" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="银行标签" required>
          <el-input v-model="claimForm.bank_label" placeholder="作用于哪个银行，如 Chase / BOA" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="claimVisible = false">取消</el-button>
        <el-button type="primary" @click="handleClaim">确定领用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ keyword: '', status: '', page: 1, page_size: 20 })

// 添加/编辑
const formVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = reactive({ phone_number: '', sms_api: '', remark: '' })

// 批量
const batchVisible = ref(false)
const batchText = ref('')
const batchSmsApi = ref('')

// 领用
const claimVisible = ref(false)
const claimPhone = ref(null)
const claimForm = reactive({ company_id: null, bank_account_id: null, bank_label: '' })
const companyOptions = ref([])
const bankOptions = ref([])

onMounted(() => fetchList())

async function fetchList() {
  loading.value = true
  try {
    const { data } = await api.get('/api/phone-pool', { params: query })
    list.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function search() { query.page = 1; fetchList() }

function openAddDialog() {
  isEdit.value = false
  editId.value = null
  Object.assign(form, { phone_number: '', sms_api: '', remark: '' })
  formVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, { phone_number: row.phone_number, sms_api: row.sms_api, remark: row.remark })
  formVisible.value = true
}

async function handleSave() {
  if (!form.phone_number) return ElMessage.warning('请输入电话号码')
  try {
    if (isEdit.value) {
      await api.put(`/api/phone-pool/${editId.value}`, form)
      ElMessage.success('已更新')
    } else {
      await api.post('/api/phone-pool', form)
      ElMessage.success('已添加')
    }
    formVisible.value = false
    fetchList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

function openBatchDialog() {
  batchText.value = ''
  batchSmsApi.value = ''
  batchVisible.value = true
}

async function handleBatch() {
  const phones = batchText.value.split('\n').map(s => s.trim()).filter(Boolean)
  if (!phones.length) return ElMessage.warning('请输入电话号码')
  try {
    const { data } = await api.post('/api/phone-pool/batch', { phones, sms_api: batchSmsApi.value })
    ElMessage.success(`导入成功 ${data.created} 个，跳过 ${data.skipped} 个`)
    batchVisible.value = false
    fetchList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  }
}

function openClaimDialog(row) {
  claimPhone.value = row
  Object.assign(claimForm, { company_id: null, bank_account_id: null, bank_label: '' })
  bankOptions.value = []
  companyOptions.value = []
  claimVisible.value = true
}

async function searchCompanies(kw) {
  if (!kw) return
  try {
    const { data } = await api.get('/api/companies', { params: { keyword: kw, page_size: 20 } })
    companyOptions.value = data.items
  } catch {}
}

async function onCompanyChange(companyId) {
  claimForm.bank_account_id = null
  if (!companyId) { bankOptions.value = []; return }
  try {
    const { data } = await api.get('/api/bank-accounts', { params: { company_id: companyId, page_size: 100 } })
    bankOptions.value = data.items
  } catch {}
}

async function handleClaim() {
  if (!claimForm.company_id) return ElMessage.warning('请选择公司')
  if (!claimForm.bank_label) return ElMessage.warning('请填写银行标签')
  try {
    await api.post(`/api/phone-pool/${claimPhone.value.id}/claim`, claimForm)
    ElMessage.success('领用成功')
    claimVisible.value = false
    fetchList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '领用失败')
  }
}

async function handleRelease(row) {
  try {
    await ElMessageBox.confirm('确定释放该号码？释放后其他人可重新领用', '提示')
    await api.post(`/api/phone-pool/${row.id}/release`)
    ElMessage.success('已释放')
    fetchList()
  } catch {}
}

async function handleDelete(id) {
  try {
    await api.delete(`/api/phone-pool/${id}`)
    ElMessage.success('已删除')
    fetchList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}
</script>

<style scoped>
.search-card :deep(.el-card__body) { padding-bottom: 2px; }
</style>
