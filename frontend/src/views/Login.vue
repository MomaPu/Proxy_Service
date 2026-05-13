<template>
  <v-row align="center" justify="center" class="fill-height">
    <v-col cols="12" sm="8" md="5" lg="4">
      <div class="proxy-card">
        <div class="proxy-card-header">
          <div class="proxy-title">Авторизация</div>
          <div class="proxy-subtitle">Доступ к прокси-серверу</div>
        </div>

        <div class="proxy-form">
          <v-text-field
            v-model="email"
            label="Email"
            type="email"
            variant="outlined"
            class="proxy-input"
            color="#064e2b"
          />
          <v-text-field
            v-model="password"
            label="Пароль"
            type="password"
            variant="outlined"
            class="proxy-input"
            color="#064e2b"
          />

          <div v-if="error" class="proxy-error">
            {{ error }}
          </div>

          <button class="proxy-button" @click="handleLogin" :disabled="loading">
            {{ loading ? 'Вход...' : 'Войти' }}
          </button>
        </div>

        <div class="proxy-footer-link">
          <router-link to="/register">Создать аккаунт →</router-link>
        </div>
      </div>
    </v-col>
  </v-row>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  const result = await authStore.login(email.value, password.value)

  if (result.success) {
    router.push('/profile')
  } else {
    error.value = result.message
  }

  loading.value = false
}
</script>

<style scoped>
.proxy-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 48px 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(6, 78, 43, 0.1);
}

.proxy-card-header {
  text-align: center;
  margin-bottom: 40px;
}

.proxy-title {
  font-size: 28px;
  font-weight: 700;
  color: #0a2e1a;
  margin-bottom: 8px;
}

.proxy-subtitle {
  font-size: 14px;
  color: #6c7a6e;
}

.proxy-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.proxy-input :deep(.v-field) {
  background: #f8f9fa;
  border: 1px solid #e0e4e8;
  border-radius: 8px;
}

.proxy-input :deep(.v-field:hover) {
  border-color: #064e2b;
}

.proxy-input :deep(.v-field__input) {
  color: #1a2e1e;
}

.proxy-error {
  color: #dc3545;
  font-size: 13px;
  text-align: center;
  padding: 8px;
  background: rgba(220, 53, 69, 0.05);
  border-radius: 8px;
}

.proxy-button {
  background: linear-gradient(135deg, #0a2e1a 0%, #064e2b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 14px 28px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.proxy-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(6, 78, 43, 0.3);
}

.proxy-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.proxy-footer-link {
  text-align: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e8ecef;
}

.proxy-footer-link a {
  color: #064e2b;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.proxy-footer-link a:hover {
  color: #ffd700;
  text-decoration: underline;
}
</style>