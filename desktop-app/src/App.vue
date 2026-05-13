<template>
  <div class="proxy-container">
    <div class="proxy-header">
      <div class="logo-section">
        <div class="logo-icon">▲</div>
        <div class="logo-text">Proxy Service</div>
      </div>
      <div class="header-status" v-if="isConnected">
        <span class="status-dot connected"></span>
        Подключен
      </div>
    </div>

    <div class="proxy-main">
      <div class="proxy-card">
        <div class="card-header">
          <div class="card-icon">🔑</div>
          <div class="card-title">Активация доступа</div>
          <div class="card-subtitle">Введите ключ для подключения к прокси-серверу</div>
        </div>

        <div class="input-group">
          <label class="proxy-label">Ключ активации</label>
          <input
            v-model="activationKey"
            type="text"
            placeholder="Вставьте ключ активации"
            :disabled="isConnected"
            class="proxy-input"
          />
        </div>

        <div class="button-group">
          <button
            v-if="!isConnected"
            @click="connect"
            :disabled="!activationKey || loading"
            class="proxy-button connect"
          >
            {{ loading ? 'Подключение...' : 'Подключиться' }}
          </button>

          <button
            v-else
            @click="disconnect"
            class="proxy-button disconnect"
          >
            Отключиться
          </button>
        </div>

        <div v-if="status" class="status-card" :class="statusClass">
          <div class="status-header">
            <span class="status-icon" v-if="status === 'connected'">✅</span>
            <span class="status-icon" v-else-if="status === 'error'">❌</span>
            <span class="status-icon" v-else>🔄</span>
            <span class="status-title">Статус: {{ statusText }}</span>
          </div>

          <div v-if="proxyInfo" class="proxy-info">
            <div class="proxy-row">
              <span class="proxy-label">Хост</span>
              <span class="proxy-value">{{ proxyInfo.host }}</span>
            </div>
            <div class="proxy-row">
              <span class="proxy-label">Порт</span>
              <span class="proxy-value">{{ proxyInfo.port }}</span>
            </div>
            <div class="proxy-row">
              <span class="proxy-label">Протокол</span>
              <span class="proxy-value">{{ proxyInfo.protocol }}</span>
            </div>
          </div>

          <div v-if="statusMessage" class="status-message">{{ statusMessage }}</div>
        </div>
      </div>
    </div>

    <div class="proxy-footer">
      <div class="footer-text">© 2026 Proxy Service</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const API_URL = 'http://localhost:8000/api/v1'

const activationKey = ref('')
const loading = ref(false)
const isConnected = ref(false)
const status = ref('')
const statusMessage = ref('')
const proxyInfo = ref(null)

const statusText = computed(() => {
  if (status.value === 'connected') return 'Подключен'
  if (status.value === 'disconnected') return 'Отключен'
  if (status.value === 'error') return 'Ошибка'
  if (status.value === 'connecting') return 'Подключение...'
  return 'Ожидание'
})

const statusClass = computed(() => {
  if (status.value === 'connected') return 'status-connected'
  if (status.value === 'disconnected') return 'status-disconnected'
  if (status.value === 'error') return 'status-error'
  return 'status-pending'
})

const connect = async () => {
  loading.value = true
  status.value = 'connecting'
  statusMessage.value = 'Активация ключа...'

  try {
    const response = await fetch(`${API_URL}/activate/key`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        activation_key: activationKey.value
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка активации')
    }

    const data = await response.json()
    proxyInfo.value = data
    isConnected.value = true
    status.value = 'connected'
    statusMessage.value = `Подключен к ${data.host}:${data.port}`

  } catch (error) {
    status.value = 'error'
    statusMessage.value = error.message
    isConnected.value = false
  } finally {
    loading.value = false
  }
}

const disconnect = async () => {
  loading.value = true

  try {
    await fetch(`${API_URL}/activate/disconnect`, {
      method: 'POST'
    })

    isConnected.value = false
    status.value = 'disconnected'
    statusMessage.value = 'Отключен от прокси'
    proxyInfo.value = null

  } catch (error) {
    console.error('Disconnect error:', error)
    status.value = 'error'
    statusMessage.value = 'Ошибка отключения'
  } finally {
    loading.value = false
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf2 100%);
  height: 100vh;
  overflow: hidden;
}

.proxy-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf2 100%);
}

.proxy-header {
  background: linear-gradient(135deg, #0a2e1a 0%, #064e2b 50%, #0a5c30 100%);
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
  font-weight: 800;
  color: #ffd700;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #ffffff;
}

.header-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.connected {
  background: #28a745;
  box-shadow: 0 0 8px #28a745;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.proxy-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.proxy-card {
  max-width: 500px;
  width: 100%;
  background: #ffffff;
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(6, 78, 43, 0.1);
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.card-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 28px;
  font-weight: 700;
  color: #0a2e1a;
  letter-spacing: 1px;
}

.card-subtitle {
  font-size: 14px;
  color: #6c7a6e;
  margin-top: 8px;
}

.input-group {
  margin-bottom: 24px;
}

.proxy-label {
  display: block;
  color: #1a2e1e;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.proxy-input {
  width: 100%;
  padding: 14px 18px;
  background: #f8f9fa;
  border: 1px solid #e0e4e8;
  border-radius: 8px;
  color: #1a2e1e;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: monospace;
}

.proxy-input:focus {
  outline: none;
  border-color: #064e2b;
  box-shadow: 0 0 0 3px rgba(6, 78, 43, 0.1);
}

.proxy-input:disabled {
  background: #e9ecef;
  cursor: not-allowed;
}

.proxy-input::placeholder {
  color: #adb5bd;
}

.button-group {
  margin-bottom: 24px;
}

.proxy-button {
  width: 100%;
  padding: 14px 28px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 16px;
}

.proxy-button.connect {
  background: linear-gradient(135deg, #0a2e1a 0%, #064e2b 100%);
  color: white;
}

.proxy-button.connect:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(6, 78, 43, 0.3);
}

.proxy-button.disconnect {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
}

.proxy-button.disconnect:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.proxy-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.status-card {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid;
}

.status-connected {
  border-left-color: #28a745;
}

.status-disconnected {
  border-left-color: #6c757d;
}

.status-error {
  border-left-color: #dc3545;
}

.status-pending {
  border-left-color: #ffc107;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-icon {
  font-size: 18px;
}

.status-title {
  font-weight: 600;
  color: #1a2e1e;
  font-size: 14px;
}

.proxy-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e0e4e8;
}

.proxy-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.proxy-label {
  color: #6c7a6e;
  font-size: 13px;
  font-weight: 500;
}

.proxy-value {
  color: #064e2b;
  font-size: 14px;
  font-weight: 600;
  font-family: monospace;
}

.status-message {
  margin-top: 12px;
  font-size: 12px;
  color: #6c7a6e;
  text-align: center;
}

.proxy-footer {
  background: linear-gradient(135deg, #0a2e1a 0%, #064e2b 100%);
  padding: 12px;
  text-align: center;
}

.footer-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
}
</style>