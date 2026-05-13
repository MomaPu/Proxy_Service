<template>
  <v-row class="profile-container">
    <!-- Левая колонка - профиль пользователя -->
    <v-col cols="12" md="6">
      <div class="proxy-card">
        <div class="card-header">
          <div class="card-icon">👤</div>
          <div class="card-title">Профиль пользователя</div>
        </div>

        <div class="info-list">
          <div class="info-item">
            <span class="info-label">Email</span>
            <span class="info-value">{{ user?.email || '—' }}</span>
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
          <div class="info-item" v-if="user?.activation_key">
            <span class="info-label">Ключ активации</span>
            <span class="info-value">
              <code class="activation-key">{{ user.activation_key }}</code>
            </span>
          </div>
        </div>
      </div>
    </v-col>

    <!-- Правая колонка - прокси подключение -->
    <v-col cols="12" md="6">
      <div class="proxy-card">
        <div class="card-header">
          <div class="card-icon">🌐</div>
          <div class="card-title">Прокси подключение</div>
        </div>

        <div v-if="myVM?.has_vm" class="proxy-info">
          <div class="connection-status">
            <div class="status-indicator connected"></div>
            <span class="status-text connected-text">Подключено</span>
          </div>
          <div class="proxy-details">
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
          </div>
          <button class="proxy-button disconnect" @click="handleDisconnect" :loading="disconnectLoading">
            Отключиться
          </button>
        </div>

        <div v-else class="no-proxy">
          <div class="no-proxy-icon">🔌</div>
          <div class="no-proxy-text">Активное подключение отсутствует</div>
          <button class="proxy-button secondary" @click="handleRefreshKey" :loading="refreshLoading">
            Получить новый ключ
          </button>
        </div>
      </div>
    </v-col>

    <!-- Нижняя колонка - смена пароля -->
    <v-col cols="12">
      <div class="proxy-card">
        <div class="card-header">
          <div class="card-icon">🔒</div>
          <div class="card-title">Безопасность</div>
          <div class="card-subtitle">Смена пароля</div>
        </div>

        <div class="password-form">
          <v-text-field
            v-model="oldPassword"
            label="Текущий пароль"
            type="password"
            variant="outlined"
            class="proxy-input"
            color="#064e2b"
            hide-details
          />
          <v-text-field
            v-model="newPassword"
            label="Новый пароль"
            type="password"
            variant="outlined"
            class="proxy-input"
            color="#064e2b"
            hide-details
          />
          <v-text-field
            v-model="confirmNewPassword"
            label="Подтверждение пароля"
            type="password"
            variant="outlined"
            class="proxy-input"
            color="#064e2b"
            hide-details
          />

          <div v-if="passwordError" class="proxy-error">
            <span class="error-icon">⚠️</span> {{ passwordError }}
          </div>
          <div v-if="passwordSuccess" class="proxy-success">
            <span class="success-icon">✓</span> {{ passwordSuccess }}
          </div>

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

  if (newPassword.value.length < 6) {
    passwordError.value = 'Пароль должен быть не менее 6 символов'
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
  if (result.success) {
    alert('✅ ' + result.message)
  } else {
    alert('❌ ' + result.message)
  }
  refreshLoading.value = false
}

const handleDisconnect = async () => {
  disconnectLoading.value = true
  const result = await authStore.disconnect()
  if (result.success) {
    alert('✅ ' + result.message)
    myVM.value = authStore.getVM
  } else {
    alert('❌ ' + result.message)
  }
  disconnectLoading.value = false
}

const formatDate = (date) => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('ru-RU')
}
</script>

<style scoped>
.profile-container {
  padding: 24px;
}

/* Карточки */
.proxy-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8ecef;
  height: 100%;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.proxy-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

/* Заголовок карточки */
.card-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #eef2f5;
}

.card-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a2e1e;
}

.card-subtitle {
  font-size: 13px;
  color: #8a9a8e;
  margin-top: 4px;
}

/* Список информации */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f3f5;
}

.info-label {
  color: #7a8a7e;
  font-size: 14px;
  font-weight: 500;
}

.info-value {
  color: #1a2e1e;
  font-size: 14px;
  font-weight: 500;
}

/* Бейджи статуса */
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
  background: #fff3e0;
  color: #e65100;
}

/* Ключ активации */
.activation-key {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #f5f7f9;
  padding: 6px 10px;
  border-radius: 8px;
  word-break: break-all;
  display: inline-block;
  max-width: 220px;
  color: #064e2b;
}

/* Статус подключения */
.connection-status {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eef2f5;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.connected {
  background: #28a745;
  box-shadow: 0 0 8px #28a745;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 14px;
  font-weight: 600;
}

.status-text.connected-text {
  color: #28a745;
}

/* Детали прокси */
.proxy-details {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.proxy-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.proxy-row:not(:last-child) {
  border-bottom: 1px solid #e8ecef;
}

.proxy-label {
  color: #7a8a7e;
  font-size: 13px;
  font-weight: 500;
}

.proxy-value {
  color: #064e2b;
  font-size: 14px;
  font-weight: 600;
  font-family: monospace;
}

/* Нет подключения */
.no-proxy {
  text-align: center;
  padding: 32px 16px;
}

.no-proxy-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.no-proxy-text {
  color: #8a9a8e;
  font-size: 14px;
  margin-bottom: 24px;
}

/* Форма пароля */
.password-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Поля ввода */
.proxy-input :deep(.v-field) {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.proxy-input :deep(.v-field:hover) {
  border-color: #064e2b;
}

.proxy-input :deep(.v-field--focused) {
  border-color: #064e2b;
  box-shadow: 0 0 0 3px rgba(6, 78, 43, 0.1);
}

/* Сообщения об ошибках и успехе */
.proxy-error {
  color: #dc3545;
  font-size: 13px;
  text-align: center;
  padding: 10px;
  background: rgba(220, 53, 69, 0.05);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.proxy-success {
  color: #28a745;
  font-size: 13px;
  text-align: center;
  padding: 10px;
  background: rgba(40, 167, 69, 0.05);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* Кнопки */
.proxy-button {
  background: linear-gradient(135deg, #0a2e1a 0%, #064e2b 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 24px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.proxy-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(6, 78, 43, 0.3);
}

.proxy-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.proxy-button.disconnect {
  background: linear-gradient(135deg, #dc3545 0%, #b91c2c 100%);
}

.proxy-button.disconnect:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.3);
}

.proxy-button.secondary {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
}
</style>