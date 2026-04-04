<template>
  <div>
    <!-- 扫码搜索区 -->
    <el-card shadow="never" class="search-card">
      <el-form inline>
        <el-form-item label="扫码查询">
          <el-input
            ref="scanInputRef"
            v-model="scanBarcode"
            placeholder="扫描或输入任一条码即可查找产品"
            clearable
            @keyup.enter="handleScan"
            style="width: 320px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleScan">扫码查询</el-button>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="产品名称/条码" clearable @keyup.enter="search" style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button @click="search">搜索</el-button>
          <el-button type="success" @click="openAddDialog">新增产品</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 扫码结果 -->
    <el-card v-if="scanResult" shadow="never" style="margin-top: 12px">
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between">
          <span><el-icon><CircleCheck /></el-icon> 扫码结果</span>
          <el-button link type="info" @click="scanResult = null">关闭</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="产品名称">{{ scanResult.name }}</el-descriptions-item>
        <el-descriptions-item label="所属公司">{{ scanResult.company_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ scanResult.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ scanResult.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top: 12px">
        <strong>该产品的所有条码（共 {{ scanResult.barcodes.length }} 个）：</strong>
        <el-table :data="scanResult.barcodes" border size="small" style="margin-top: 8px">
          <el-table-column prop="barcode" label="条码" min-width="200" />
          <el-table-column prop="label" label="条码类型" width="120" />
        </el-table>
      </div>
    </el-card>

    <!-- 产品列表 -->
    <el-card shadow="never" style="margin-top: 12px">
      <el-table :data="list" stripe v-loading="loading" border size="small">
        <el-table-column prop="name" label="产品名称" min-width="160" />
        <el-table-column label="条码" min-width="280">
          <template #default="{ row }">
            <el-tag
              v-for="bc in row.barcodes"
              :key="bc.id"
              size="small"
              style="margin: 2px 4px 2px 0"
            >
              {{ bc.label ? `[${bc.label}] ` : '' }}{{ bc.barcode }}
            </el-tag>
            <span v-if="!row.barcodes.length" style="color: #999">无条码</span>
          </template>
        </el-table-column>
        <el-table-column prop="company_name" label="所属公司" width="160" show-overflow-tooltip />
        <el-table-column prop="remark" label="备注" width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ row.created_at?.substring(0, 19) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除此产品及其所有条码？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        style="margin-top: 12px; justify-content: flex-end"
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @change="fetchList"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="formVisible" :title="isEdit ? '编辑产品' : '新增产品'" width="640px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="产品名称" required>
          <el-input v-model="form.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="所属公司">
          <el-select
            v-model="form.company_id"
            filterable
            remote
            clearable
            :remote-method="searchCompanies"
            placeholder="搜索公司（可选）"
            style="width: 100%"
          >
            <el-option v-for="c in companyOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="产品描述" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
        <el-divider content-position="left">条码列表（可添加多个条码）</el-divider>
        <div v-for="(bc, index) in form.barcodes" :key="index" style="display: flex; gap: 8px; margin-bottom: 8px; padding-left: 90px">
          <el-input v-model="bc.barcode" placeholder="条码值" style="flex: 2" />
          <el-input v-model="bc.label" placeholder="类型(UPC/EAN/SKU等)" style="flex: 1" />
          <el-button type="danger" :icon="Delete" circle @click="removeBarcode(index)" />
        </div>
        <div style="padding-left: 90px">
          <el-button type="primary" plain @click="addBarcode">+ 添加条码</el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, CircleCheck, Delete } from '@element-plus/icons-vue'
import api from '../utils/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ keyword: '', page: 1, page_size: 20 })

// 扫码
const scanBarcode = ref('')
const scanResult = ref(null)
const scanInputRef = ref(null)

// 表单
const formVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = reactive({
  name: '',
  description: '',
  company_id: null,
  remark: '',
  barcodes: [{ barcode: '', label: '' }],
})
const companyOptions = ref([])

onMounted(() => fetchList())

async function fetchList() {
  loading.value = true
  try {
    const { data } = await api.get('/api/products', { params: query })
    list.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function search() {
  query.page = 1
  fetchList()
}

async function handleScan() {
  const code = scanBarcode.value.trim()
  if (!code) return ElMessage.warning('请输入或扫描条码')
  try {
    const { data } = await api.get('/api/products/scan', { params: { barcode: code } })
    scanResult.value = data
    ElMessage.success(`已找到产品「${data.name}」，共 ${data.barcodes.length} 个条码`)
  } catch (e) {
    scanResult.value = null
    ElMessage.error(e.response?.data?.detail || '未找到该条码对应的产品')
  }
}

function addBarcode() {
  form.barcodes.push({ barcode: '', label: '' })
}

function removeBarcode(index) {
  form.barcodes.splice(index, 1)
}

function openAddDialog() {
  isEdit.value = false
  editId.value = null
  Object.assign(form, {
    name: '',
    description: '',
    company_id: null,
    remark: '',
    barcodes: [{ barcode: '', label: '' }],
  })
  companyOptions.value = []
  formVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, {
    name: row.name,
    description: row.description,
    company_id: row.company_id,
    remark: row.remark,
    barcodes: row.barcodes.map((b) => ({ barcode: b.barcode, label: b.label })),
  })
  if (row.company_id && row.company_name) {
    companyOptions.value = [{ id: row.company_id, name: row.company_name }]
  } else {
    companyOptions.value = []
  }
  formVisible.value = true
}

async function searchCompanies(kw) {
  if (!kw) return
  try {
    const { data } = await api.get('/api/companies', { params: { keyword: kw, page_size: 20 } })
    companyOptions.value = data.items
  } catch {}
}

async function handleSave() {
  if (!form.name) return ElMessage.warning('请输入产品名称')
  // 过滤空条码
  const barcodes = form.barcodes.filter((b) => b.barcode.trim())
  const payload = {
    name: form.name,
    description: form.description,
    company_id: form.company_id,
    remark: form.remark,
    barcodes,
  }
  try {
    if (isEdit.value) {
      await api.put(`/api/products/${editId.value}`, payload)
      ElMessage.success('已更新')
    } else {
      await api.post('/api/products', payload)
      ElMessage.success('已创建')
    }
    formVisible.value = false
    fetchList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(id) {
  try {
    await api.delete(`/api/products/${id}`)
    ElMessage.success('已删除')
    fetchList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}
</script>

<style scoped>
.search-card :deep(.el-card__body) {
  padding-bottom: 2px;
}
</style>
