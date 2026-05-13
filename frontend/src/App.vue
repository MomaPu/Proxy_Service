<template>
  <v-app class="proxy-app">
    <v-app-bar flat class="proxy-header">
      <v-container class="d-flex align-center justify-space-between">
        <div class="logo-section">
          <div class="logo-icon">▲</div>
          <div class="logo-text">Proxy Service</div>
        </div>

        <div v-if="authStore.isAuthenticated" class="user-info">
          <span class="user-email">{{ authStore.getUser?.email }}</span>
          <v-btn @click="logout" variant="text" class="logout-btn">
            Выйти
          </v-btn>
        </div>
      </v-container>
    </v-app-bar>

    <v-main class="proxy-main">
      <v-container fluid class="main-container">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&display=swap');

* {
  font-family: 'Inter', sans-serif;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

.proxy-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.proxy-header {
  background: linear-gradient(135deg, #0a2e1a 0%, #064e2b 50%, #0a5c30 100%) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
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

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-email {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
}

.logout-btn {
  color: #ffd700 !important;
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 6px;
}

.proxy-main {
  flex: 1 0 auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf2 100%);
}

.main-container {
  min-height: 100%;
  padding: 24px;
}

</style>