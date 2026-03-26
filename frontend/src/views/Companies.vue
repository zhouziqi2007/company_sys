<template>
  <div>
    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="公司名/姓名/EIN/SSN/Email" clearable @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="执照状态">
          <el-select v-model="query.license_status" clearable placeholder="全部">
            <el-option label="待办理" value="pending" />
            <el-option label="办理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="公户状态">
          <el-select v-model="query.bank_account_status" clearable placeholder="全部">
            <el-option label="待办理" value="pending" />
            <el-option label="办理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
          <el-button type="success" @click="openForm()">新增公司</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格 -->
    <el-card shadow="never" style="margin-top:12px">
      <el-table :data="list" stripe v-loading="loading" border size="small">
        <el-table-column prop="name" label="公司名称" min-width="180" />
        <el-table-column prop="unified_code" label="EIN/Tax ID" width="140" />
        <el-table-column label="法人姓名" width="150">
          <template #default="{ row }">{{ row.first_name }} {{ row.middle_name }} {{ row.last_name }}</template>
        </el-table-column>
        <el-table-column prop="ssn" label="SSN" width="120" />
        <el-table-column prop="dob" label="DOB" width="110" />
        <el-table-column prop="phone" label="Phone" width="130" />
        <el-table-column prop="state_of_formation" label="State" width="80" />
        <el-table-column label="执照状态" width="100">
          <template #default="{ row }">
            <el-tag :type="tagType(row.license_status)" size="small">{{ statusLabel(row.license_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="公户状态" width="100">
          <template #default="{ row }">
            <el-tag :type="tagType(row.bank_account_status)" size="small">{{ statusLabel(row.bank_account_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openForm(row)">编辑</el-button>
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
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

    <!-- 新增/编辑 -->
    <el-dialog v-model="formVisible" :title="formData.id ? '编辑公司' : '新增公司'" width="850px" destroy-on-close>
      <el-form :model="formData" label-width="120px">
        <el-divider content-position="left">公司信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="公司名称"><el-input v-model="formData.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="EIN/Tax ID"><el-input v-model="formData.unified_code" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="State of Formation"><el-input v-model="formData.state_of_formation" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="注册资本"><el-input v-model="formData.registered_capital" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="注册地址"><el-input v-model="formData.registered_address" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="经营范围"><el-input v-model="formData.business_scope" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>

        <el-divider content-position="left">法人个人信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="First Name"><el-input v-model="formData.first_name" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="Middle Name"><el-input v-model="formData.middle_name" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="Last Name"><el-input v-model="formData.last_name" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="SSN"><el-input v-model="formData.ssn" placeholder="XXX-XX-XXXX" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="ITIN"><el-input v-model="formData.itin" placeholder="9XX-XX-XXXX" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="DOB"><el-input v-model="formData.dob" placeholder="MM/DD/YYYY" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="Gender">
              <el-select v-model="formData.gender">
                <el-option label="Male" value="male" />
                <el-option label="Female" value="female" />
                <el-option label="Other" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8"><el-form-item label="Email"><el-input v-model="formData.email" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="Phone"><el-input v-model="formData.phone" /></el-form-item></el-col>
        </el-row>

        <el-divider content-position="left">法人地址</el-divider>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="Address Line 1"><el-input v-model="formData.address_line1" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Address Line 2"><el-input v-model="formData.address_line2" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="City"><el-input v-model="formData.city" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="State"><el-input v-model="formData.state" /></el-form-item></el-col>
          <el-col :span="4"><el-form-item label="Zip Code"><el-input v-model="formData.zip_code" /></el-form-item></el-col>
          <el-col :span="4"><el-form-item label="Country"><el-input v-model="formData.country" /></el-form-item></el-col>
        </el-row>

        <template v-if="formData.id">
          <el-divider content-position="left">办理状态</el-divider>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="执照状态">
                <el-select v-model="formData.license_status">
                  <el-option label="待办理" value="pending" />
                  <el-option label="办理中" value="processing" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已驳回" value="rejected" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="公户状态">
                <el-select v-model="formData.bank_account_status">
                  <el-option label="待办理" value="pending" />
                  <el-option label="办理中" value="processing" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已驳回" value="rejected" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <el-divider content-position="left">其他</el-divider>
        <el-row :gutter="16">
          <el-col :span="24"><el-form-item label="备注"><el-input v-model="formData.remark" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情 -->
    <el-drawer v-model="detailVisible" title="公司详情" size="750px" @open="onDetailOpen">
      <el-tabs v-model="detailTab" v-if="detailData">
        <!-- 基本信息 Tab -->
        <el-tab-pane label="基本信息" name="info">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="公司名称">{{ detailData.name }}</el-descriptions-item>
            <el-descriptions-item label="EIN/Tax ID">{{ detailData.unified_code }}</el-descriptions-item>
            <el-descriptions-item label="State of Formation">{{ detailData.state_of_formation }}</el-descriptions-item>
            <el-descriptions-item label="注册资本">{{ detailData.registered_capital }}</el-descriptions-item>
            <el-descriptions-item label="注册地址">{{ detailData.registered_address }}</el-descriptions-item>
            <el-descriptions-item label="经营范围">{{ detailData.business_scope }}</el-descriptions-item>
            <el-descriptions-item label="Full Name">{{ detailData.first_name }} {{ detailData.middle_name }} {{ detailData.last_name }}</el-descriptions-item>
            <el-descriptions-item label="SSN">{{ detailData.ssn }}</el-descriptions-item>
            <el-descriptions-item label="ITIN">{{ detailData.itin }}</el-descriptions-item>
            <el-descriptions-item label="DOB">{{ detailData.dob }}</el-descriptions-item>
            <el-descriptions-item label="Gender">{{ genderLabel(detailData.gender) }}</el-descriptions-item>
            <el-descriptions-item label="Email">{{ detailData.email }}</el-descriptions-item>
            <el-descriptions-item label="Phone">{{ detailData.phone }}</el-descriptions-item>
            <el-descriptions-item label="Address">{{ [detailData.address_line1, detailData.address_line2, detailData.city, detailData.state, detailData.zip_code, detailData.country].filter(Boolean).join(', ') }}</el-descriptions-item>
            <el-descriptions-item label="执照状态">{{ statusLabel(detailData.license_status) }}</el-descriptions-item>
            <el-descriptions-item label="公户状态">{{ statusLabel(detailData.bank_account_status) }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ detailData.remark }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <!-- 银行资料 Tab -->
        <el-tab-pane label="银行资料" name="bank">
          <div style="margin-bottom:12px">
            <el-button type="primary" size="small" @click="openBankForm()">新增银行账户</el-button>
          </div>
          <el-collapse v-model="activeBankIds" v-if="bankList.length">
            <el-collapse-item v-for="bank in bankList" :key="bank.id" :name="bank.id">
              <template #title>
                <div style="display:flex;align-items:center;gap:8px;width:100%">
                  <el-tag :type="bankStatusType(bank.status)" size="small">{{ bankStatusLabel(bank.status) }}</el-tag>
                  <el-tag v-if="bank.label" size="small" type="info">{{ bank.label }}</el-tag>
                  <strong>{{ bank.bank_name }}</strong>
                  <span style="color:#999;font-size:12px">{{ bank.account_number ? '****' + bank.account_number.slice(-4) : '' }}</span>
                </div>
              </template>
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="银行名称">{{ bank.bank_name }}</el-descriptions-item>
                <el-descriptions-item label="标签">{{ bank.label }}</el-descriptions-item>
                <el-descriptions-item label="Routing Number">{{ bank.routing_number }}</el-descriptions-item>
                <el-descriptions-item label="Account Number">{{ bank.account_number }}</el-descriptions-item>
                <el-descriptions-item label="账户类型">{{ accountTypeLabel(bank.account_type) }}</el-descriptions-item>
                <el-descriptions-item label="状态">{{ bankStatusLabel(bank.status) }}</el-descriptions-item>
                <el-descriptions-item label="网银地址" :span="2">{{ bank.login_url }}</el-descriptions-item>
                <el-descriptions-item label="网银用户名">{{ bank.login_username }}</el-descriptions-item>
                <el-descriptions-item label="网银密码">{{ bank.login_password }}</el-descriptions-item>
                <el-descriptions-item label="PIN">{{ bank.pin }}</el-descriptions-item>
                <el-descriptions-item label="密钥/Token">{{ bank.security_key }}</el-descriptions-item>
                <el-descriptions-item label="安全问题" :span="2">{{ bank.security_questions }}</el-descriptions-item>
                <el-descriptions-item label="二次验证方式">{{ bank.two_factor_method }}</el-descriptions-item>
                <el-descriptions-item label="验证手机">{{ bank.two_factor_phone }}</el-descriptions-item>
                <el-descriptions-item label="验证邮箱">{{ bank.two_factor_email }}</el-descriptions-item>
                <el-descriptions-item label="银行客服电话">{{ bank.bank_phone }}</el-descriptions-item>
                <el-descriptions-item label="银行联系人">{{ bank.bank_contact }}</el-descriptions-item>
                <el-descriptions-item label="开户行地址">{{ bank.branch_address }}</el-descriptions-item>
                <el-descriptions-item label="备注" :span="2">{{ bank.remark }}</el-descriptions-item>
              </el-descriptions>
              <!-- 银行附件 -->
              <div style="margin-top:12px">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
                  <strong style="font-size:13px">附件资料</strong>
                  <el-upload :show-file-list="false" :before-upload="(f) => uploadBankDoc(bank.id, f)" accept="*">
                    <el-button size="small" type="primary" link><el-icon><UploadFilled /></el-icon> 上传附件</el-button>
                  </el-upload>
                </div>
                <el-table :data="bankDocs[bank.id] || []" size="small" border v-if="(bankDocs[bank.id] || []).length">
                  <el-table-column prop="filename" label="文件名" min-width="160" />
                  <el-table-column label="大小" width="80">
                    <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
                  </el-table-column>
                  <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                      <el-button link size="small" type="primary" @click="previewDoc(row)">查看</el-button>
                      <el-popconfirm title="确定删除？" @confirm="deleteBankDoc(row.id, bank.id)">
                        <template #reference><el-button link size="small" type="danger">删除</el-button></template>
                      </el-popconfirm>
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-else description="暂无附件" :image-size="40" />
              </div>
              <!-- 操作按钮 -->
              <div style="margin-top:12px;text-align:right">
                <el-button size="small" type="primary" @click="openBankForm(bank)">编辑</el-button>
                <el-popconfirm title="确定删除此银行账户？" @confirm="deleteBank(bank.id)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </div>
            </el-collapse-item>
          </el-collapse>
          <el-empty v-else description="暂无银行账户" />
        </el-tab-pane>
      </el-tabs>
    </el-drawer>

    <!-- 银行账户表单 -->
    <el-dialog v-model="bankFormVisible" :title="bankForm.id ? '编辑银行账户' : '新增银行账户'" width="800px" destroy-on-close>
      <el-form :model="bankForm" label-width="120px">
        <el-divider content-position="left">账户信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="标签">
              <el-select v-model="bankForm.label" allow-create filterable placeholder="选择或输入标签">
                <el-option label="Checking" value="checking" />
                <el-option label="Savings" value="savings" />
                <el-option label="Business" value="business" />
                <el-option label="Main" value="main" />
                <el-option label="Payroll" value="payroll" />
                <el-option label="Tax" value="tax" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8"><el-form-item label="银行名称"><el-input v-model="bankForm.bank_name" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="账户类型">
              <el-select v-model="bankForm.account_type">
                <el-option label="Checking" value="checking" />
                <el-option label="Savings" value="savings" />
                <el-option label="Business Checking" value="business_checking" />
                <el-option label="Business Savings" value="business_savings" />
                <el-option label="Other" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8"><el-form-item label="Routing Number"><el-input v-model="bankForm.routing_number" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="Account Number"><el-input v-model="bankForm.account_number" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="bankForm.status">
                <el-option label="待开户" value="pending" />
                <el-option label="正常" value="active" />
                <el-option label="冻结" value="frozen" />
                <el-option label="已关闭" value="closed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">网银登录信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="24"><el-form-item label="网银地址"><el-input v-model="bankForm.login_url" placeholder="https://..." /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="登录用户名"><el-input v-model="bankForm.login_username" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="登录密码"><el-input v-model="bankForm.login_password" show-password /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="安全问题"><el-input v-model="bankForm.security_questions" type="textarea" :rows="2" placeholder="Q1: ... A1: ...\nQ2: ... A2: ..." /></el-form-item></el-col>
        </el-row>

        <el-divider content-position="left">安全与密钥</el-divider>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="PIN"><el-input v-model="bankForm.pin" show-password /></el-form-item></el-col>
          <el-col :span="16"><el-form-item label="密钥/Token"><el-input v-model="bankForm.security_key" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="二次验证方式"><el-input v-model="bankForm.two_factor_method" placeholder="SMS/Email/App" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="验证手机"><el-input v-model="bankForm.two_factor_phone" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="验证邮箱"><el-input v-model="bankForm.two_factor_email" /></el-form-item></el-col>
        </el-row>

        <el-divider content-position="left">联系信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="银行客服电话"><el-input v-model="bankForm.bank_phone" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="银行联系人"><el-input v-model="bankForm.bank_contact" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="开户行地址"><el-input v-model="bankForm.branch_address" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="备注"><el-input v-model="bankForm.remark" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="bankFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="bankSaving" @click="handleBankSave">保存</el-button>
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
const saving = ref(false)
const formVisible = ref(false)
const detailVisible = ref(false)
const detailData = ref(null)
const detailTab = ref('info')
const query = ref({ page: 1, page_size: 20, keyword: '', license_status: '', bank_account_status: '' })
const formData = ref({})

// 银行相关
const bankList = ref([])
const bankDocs = ref({})
const activeBankIds = ref([])
const bankFormVisible = ref(false)
const bankSaving = ref(false)
const bankForm = ref({})

const tagType = (s) => ({ pending: 'info', processing: '', completed: 'success', rejected: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待办理', processing: '办理中', completed: '已完成', rejected: '已驳回' }[s] || s)
const genderLabel = (g) => ({ male: 'Male', female: 'Female', other: 'Other' }[g] || g)
const bankStatusType = (s) => ({ pending: 'info', active: 'success', frozen: 'warning', closed: 'danger' }[s] || 'info')
const bankStatusLabel = (s) => ({ pending: '待开户', active: '正常', frozen: '冻结', closed: '已关闭' }[s] || s)
const accountTypeLabel = (t) => ({ checking: 'Checking', savings: 'Savings', business_checking: 'Business Checking', business_savings: 'Business Savings', other: 'Other' }[t] || t)
const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function fetchList() {
  loading.value = true
  try {
    const { data } = await api.get('/companies', { params: query.value })
    list.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

function search() { query.value.page = 1; fetchList() }
function resetQuery() { query.value = { page: 1, page_size: 20, keyword: '', license_status: '', bank_account_status: '' }; fetchList() }

function openForm(row) {
  formData.value = row ? { ...row } : {
    name: '', unified_code: '', state_of_formation: '',
    first_name: '', middle_name: '', last_name: '',
    ssn: '', itin: '', dob: '', gender: 'male', email: '', phone: '',
    address_line1: '', address_line2: '', city: '', state: '', zip_code: '', country: 'US',
    registered_address: '', business_scope: '', registered_capital: '', remark: ''
  }
  formVisible.value = true
}

function viewDetail(row) {
  detailData.value = row
  detailTab.value = 'info'
  detailVisible.value = true
}

async function onDetailOpen() {
  if (detailData.value?.id) {
    await fetchBankList()
  }
}

async function fetchBankList() {
  const { data } = await api.get('/bank-accounts', { params: { company_id: detailData.value.id, page_size: 100 } })
  bankList.value = data.items
  // 加载每个银行账户的附件
  bankDocs.value = {}
  for (const bank of data.items) {
    const res = await api.get(`/bank-accounts/${bank.id}/documents`)
    bankDocs.value[bank.id] = res.data
  }
}

function openBankForm(bank) {
  bankForm.value = bank ? { ...bank } : {
    company_id: detailData.value.id,
    label: '', bank_name: '', routing_number: '', account_number: '',
    account_type: 'checking', status: 'pending',
    login_url: '', login_username: '', login_password: '', security_questions: '',
    pin: '', security_key: '', two_factor_method: '', two_factor_phone: '', two_factor_email: '',
    bank_phone: '', bank_contact: '', branch_address: '', remark: ''
  }
  bankFormVisible.value = true
}

async function handleBankSave() {
  if (!bankForm.value.bank_name) return ElMessage.warning('请输入银行名称')
  bankSaving.value = true
  try {
    if (bankForm.value.id) {
      await api.put(`/bank-accounts/${bankForm.value.id}`, bankForm.value)
    } else {
      await api.post('/bank-accounts', bankForm.value)
    }
    ElMessage.success('保存成功')
    bankFormVisible.value = false
    await fetchBankList()
  } finally { bankSaving.value = false }
}

async function deleteBank(bankId) {
  await api.delete(`/bank-accounts/${bankId}`)
  ElMessage.success('已删除')
  await fetchBankList()
}

async function uploadBankDoc(bankId, file) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('category', 'bank_doc')
  await api.post(`/bank-accounts/${bankId}/upload`, fd)
  ElMessage.success('上传成功')
  const res = await api.get(`/bank-accounts/${bankId}/documents`)
  bankDocs.value[bankId] = res.data
  return false // prevent default upload
}

function previewDoc(row) {
  if (row.file_url) window.open(row.file_url, '_blank')
  else ElMessage.info('无法预览')
}

async function deleteBankDoc(docId, bankId) {
  await api.delete(`/documents/${docId}`)
  ElMessage.success('已删除')
  const res = await api.get(`/bank-accounts/${bankId}/documents`)
  bankDocs.value[bankId] = res.data
}

async function handleSave() {
  if (!formData.value.name) return ElMessage.warning('请输入公司名称')
  saving.value = true
  try {
    if (formData.value.id) {
      await api.put(`/companies/${formData.value.id}`, formData.value)
    } else {
      await api.post('/companies', formData.value)
    }
    ElMessage.success('保存成功')
    formVisible.value = false
    fetchList()
  } finally { saving.value = false }
}

async function handleDelete(id) {
  await api.delete(`/companies/${id}`)
  ElMessage.success('已删除')
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.search-card :deep(.el-card__body) { padding-bottom: 0; }
</style>
