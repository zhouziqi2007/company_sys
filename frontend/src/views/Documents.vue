<template>
  <div>
    <el-card shadow="never" class="search-card">
      <el-form inline>
        <el-form-item label="文件分类">
          <el-select v-model="query.category" clearable placeholder="全部">
            <el-option label="身份证" value="id_card" />
            <el-option label="营业执照" value="license" />
            <el-option label="银行资料" value="bank_doc" />
            <el-option label="合同" value="contract" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
          <el-button type="success" @click="uploadVisible = true">上传文件</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="list" stripe v-loading="loading" border size="small">
        <el-table-column prop="filename" label="文件名" min-width="200" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">{{ catLabel(row.category) }}</template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="120" />
        <el-table-column label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="170">
          <template #default="{ row }">{{ row.created_at?.substring(0,19) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="preview(row)">查看</el-button>
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

    <!-- 上传 -->
    <el-dialog v-model="uploadVisible" title="上传文件" width="500px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="文件分类">
          <el-select v-model="uploadForm.category">
            <el-option label="身份证" value="id_card" />
            <el-option label="营业执照" value="license" />
            <el-option label="银行资料" value="bank_doc" />
            <el-option label="合同" value="contract" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联公司">
          <el-select v-model="uploadForm.company_id" clearable filterable remote :remote-method="searchCompanies" placeholder="搜索公司(可选)">
            <el-option v-for="c in companyOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="5"
            :on-change="onFileChange"
            multiple
            drag
          >
            <el-icon size="40"><UploadFilled /></el-icon>
            <div>拖拽或点击上传文件</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const uploading = ref(false)
const uploadVisible = ref(false)
const fileList = ref([])
const companyOptions = ref([])
const query = ref({ page: 1, page_size: 20, category: '', company_id: 0, task_id: 0 })
const uploadForm = ref({ category: 'other', company_id: '' })

const catLabel = (c) => ({ id_card: '身份证', license: '营业执照', bank_doc: '银行资料', contract: '合同', other: '其他' }[c] || c)
const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function fetchList() {
  loading.value = true
  try {
    const { data } = await api.get('/documents', { params: query.value })
    list.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

function search() { query.value.page = 1; fetchList() }
function resetQuery() { query.value = { page: 1, page_size: 20, category: '', company_id: 0, task_id: 0 }; fetchList() }

function onFileChange(file) { fileList.value.push(file.raw) }

async function searchCompanies(kw) {
  if (!kw) return
  const { data } = await api.get('/companies', { params: { keyword: kw, page_size: 20 } })
  companyOptions.value = data.items
}

async function handleUpload() {
  if (fileList.value.length === 0) return ElMessage.warning('请选择文件')
  uploading.value = true
  try {
    for (const file of fileList.value) {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('category', uploadForm.value.category)
      if (uploadForm.value.company_id) fd.append('company_id', uploadForm.value.company_id)
      await api.post('/documents', fd)
    }
    ElMessage.success('上传成功')
    uploadVisible.value = false
    fileList.value = []
    fetchList()
  } finally { uploading.value = false }
}

function preview(row) {
  if (row.file_url) window.open(row.file_url, '_blank')
  else ElMessage.info('无法预览')
}

async function handleDelete(id) {
  await api.delete(`/documents/${id}`)
  ElMessage.success('已删除')
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.search-card :deep(.el-card__body) { padding-bottom: 0; }
</style>
