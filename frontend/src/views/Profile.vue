<template>
  <v-row class="profile-container">
    <v-col cols="12" md="6">
      <div class="proxy-card">
        <div class="card-header">
          <div class="card-icon">👤</div>
          <div class="card-title">Профиль</div>
        </div>

        <div class="info-list">
          <div class="info-item">
            <span class="info-label">Email</span>
            <span class="info-value">{{ user?.email }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Статус</span>
            <span class="info-value">
              <span class="status-badge" :class="user?.is_active ? 'active' : 'inactive'">
                {{ user?.is_active ? 'Активен' : 'Не активирован' }}
              </span>
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">Дата регистрации</span>
            <span class="info-value">{{ formatDate(user?.created_at) }}</span>
          </div>
        </div>
      </div>
    </v-col>

    <v-col cols="12" md="6">
      <div class="proxy-card">
        <div class="card-header">
          <div class="card-icon">🔌</div>
          <div class="card-title">Прокси подключение</div>
        </div>

        <div v-if="myVM?.has_vm" class="proxy-info">
          <div class="proxy-row">
            <span class="proxy-label">Хост</span>
            <span class="proxy-value">{{ myVM.host }}</span>
          </div>
          <div class="proxy-row">
            <span class="proxy-label">Порт</span>
            <span class="proxy-value">{{ myVM.port }}</span>
          </div>
          <div class="proxy-row">
            <span class="proxy-label">Протокол</span>
            <span class="proxy-value">{{ myVM.protocol }}</span>
          </div>
          <div class="proxy-row">
            <span class="proxy-label">Статус</span>
            <span class="proxy-value">
              <span class="status-badge connected">Подключен</span>
            </span>
          </div>
          <button class="proxy-button disconnect" @click="handleDisconnect" :loading="disconnectLoading">
            Отключить
          </button>
        </div>

        <div v-else class="no-proxy">
          <div class="no-proxy-icon">⚠️</div>
          <div class="no-proxy-text">Активное подключение отсутствует</div>
          <button class="proxy-button secondary" @click="handleRefreshKey" :loading="refreshLoading">
            Обновить ключ
          </button>
        </div>
      </div>
    </v-col>

    <v-col cols="12">
      <div class="proxy-card">
        <div class="card-header">
          <div class="card-icon">🔒</div>
          <div class="card-title">Смена пароля</div>
        </div>

        <div class="password-form">
          <v-text-field
            v-model="oldPassword"
            label="Текущий пароль"
            type="password"
            variant="outlined"
            class="proxy-input"
            color="#064e2b"
          />
          <v-text-field
            v-model="newPassword"
            label="Новый пароль"
            type="password"
            variant="outlined"
            class="proxy-input"
            color="#064e2b"
          />
          <v-text-field
            v-model="confirmNewPassword"
            label="Подтверждение пароля"
            type="password"
            variant="outlined"
            class="proxy-input"
            color="#064e2b"
          />

          <div v-if="passwordError" class="proxy-error">{{ passwordError }}</div>
          <div v-if="passwordSuccess" class="proxy-success">{{ passwordSuccess }}</div>

          <button class="proxy-button" @click="handleChangePassword" :loading="passwordLoading">
            Изменить пароль
          </button>
        </div>
      </div>
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const user = ref(null)
const myVM = ref(null)

const oldPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

const refreshLoading = ref(false)
const disconnectLoading = ref(false)

onMounted(async () => {
  await authStore.fetchProfile()
  await authStore.fetchMyVM()
  user.value = authStore.getUser
  myVM.value = authStore.getVM
})

const handleChangePassword = async () => {
  if (newPassword.value !== confirmNewPassword.value) {
    passwordError.value = 'Пароли не совпадают'
    return
  }

  passwordLoading.value = true
  passwordError.value = ''
  passwordSuccess.value = ''

  const result = await authStore.changePassword(oldPassword.value, newPassword.value)

  if (result.success) {
    passwordSuccess.value = result.message
    oldPassword.value = ''
    newPassword.value = ''
    confirmNewPassword.value = ''
  } else {
    passwordError.value = result.message
  }

  passwordLoading.value = false
}

const handleRefreshKey = async () => {
  refreshLoading.value = true
  const result = await authStore.refreshKey()
  alert(result.message)
  refreshLoading.value = false
}

const handleDisconnect = async () => {
  disconnectLoading.value = true
  const result = await authStore.disconnect()
  myVM.value = authStore.getVM
  alert(result.message)
  disconnectLoading.value = false
}

const formatDate = (date) => {
  if (!date) return 'Н/Д'
  return new Date(date).toLocaleDateString('ru-RU')
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.proxy-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(6, 78, 43, 0.1);
  height: 100%;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8ecef;
}

.card-icon {
  font-size: 32px;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #0a2e1a;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e8ecef;
}

.info-label {
  color: #6c7a6e;
  font-size: 14px;
  font-weight: 500;
}

.info-value {
  color: #1a2e1e;
  font-size: 14px;
  font-weight: 600;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.inactive {
  background: #ffebee;
  color: #c62828;
}

.status-badge.connected {
  background: #e8f5e9;
  color: #2e7d32;
}

.proxy-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.proxy-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.proxy-label {
  color: #6c7a6e;
  font-size: 14px;
  font-weight: 500;
}

.proxy-value {
  color: #1a2e1e;
  font-size: 14px;
  font-weight: 600;
  font-family: monospace;
}

.no-proxy {
  text-align: center;
  padding: 32px 0;
}

.no-proxy-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.no-proxy-text {
  color: #6c7a6e;
  font-size: 14px;
  margin-bottom: 24px;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.proxy-input :deep(.v-field) {
  background: #f8f9fa;
  border: 1px solid #e0e4e8;
  border-radius: 8px;
}

.proxy-input :deep(.v-field:hover) {
  border-color: #064e2b;
}

.proxy-error {
  color: #dc3545;
  font-size: 13px;
  text-align: center;
  padding: 8px;
  background: rgba(220, 53, 69, 0.05);
  border-radius: 8px;
}

.proxy-success {
  color: #28a745;
  font-size: 13px;
  text-align: center;
  padding: 8px;
  background: rgba(40, 167, 69, 0.05);
  border-radius: 8px;
}

.proxy-button {
  background: linear-gradient(135deg, #0a2e1a 0%, #064e2b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.proxy-button.disconnect {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
}

.proxy-button.secondary {
  background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
}

.proxy-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(6, 78, 43, 0.3);
}
</style>