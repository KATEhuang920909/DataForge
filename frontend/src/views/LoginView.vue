<template>
  <div class="login-page">
    <div class="login-background" />
    <div class="login-frame">

      <main class="login-card">
        <section class="login-panel">
          <div class="login-head">
            <h1>欢迎来到 DataForge</h1>
            <p>请输入用户名和密码登录，开始管理您的数据资源。</p>
          </div>

          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <label for="username">用户名</label>
              <input
                id="username"
                v-model="username"
                type="text"
                required
                autocomplete="username"
                placeholder="请输入用户名"
              />
            </div>

            <div class="form-group">
              <label for="password">密码</label>
              <input
                id="password"
                v-model="password"
                type="password"
                required
                autocomplete="current-password"
                placeholder="请输入密码"
              />
            </div>

            <div class="form-options">
              <label class="checkbox-wrapper">
                <input type="checkbox" />
                <span>记住我</span>
              </label>
            </div>

            <button type="submit" :disabled="loading" class="login-btn">
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </form>

          <p v-if="error" class="error-message">{{ error }}</p>
        </section>

        <aside class="login-info">
          <h2>即时访问</h2>
          <p>
            DataForge 提供简洁的数据管理体验，您可以直接登录开始管理您的数据资源，并实现上传、下载、删除、更新等操作。
          </p>
          <div class="info-pill-list">
            <span class="info-pill">轻量化</span>
            <span class="info-pill">安全可靠</span>
            <span class="info-pill">高效管理</span>
          </div>
        </aside>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await login(username.value, password.value)
    localStorage.setItem('auth_token', response.access_token)
    router.replace('/')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  width: 100%;
  background: #f7f8fb;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  overflow: hidden;
}

.login-background {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top left, rgba(255, 165, 0, 0.12), transparent 22%),
    radial-gradient(circle at bottom right, rgba(59, 130, 246, 0.12), transparent 20%);
  pointer-events: none;
}

.login-frame {
  position: relative;
  width: 100%;
  max-width: 1100px;
  z-index: 1;
}

.login-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-mark {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  background: linear-gradient(135deg, #fb923c, #f97316);
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 800;
  display: grid;
  place-items: center;
}

.brand-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: #111827;
}

.brand-subtitle {
  color: #6b7280;
  font-size: 0.92rem;
}

.login-card {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 1.5rem;
  background: #ffffff;
  border-radius: 28px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 30px 70px rgba(15, 23, 42, 0.08);
}

.login-panel,
.login-info {
  padding: 3rem;
}

.login-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-head h1 {
  margin: 0;
  font-size: 2.3rem;
  font-weight: 800;
  color: #111827;
}

.login-head p {
  margin: 1rem 0 0;
  color: #4b5563;
  line-height: 1.8;
  max-width: 38rem;
}

.login-form {
  margin-top: 2rem;
  display: grid;
  gap: 1.25rem;
}

.form-group {
  display: grid;
  gap: 0.65rem;
}

.form-group label {
  font-size: 0.95rem;
  color: #374151;
  font-weight: 600;
}

input[type='text'],
input[type='password'] {
  width: 100%;
  padding: 1.1rem 1.2rem;
  border: 1px solid #d1d5db;
  border-radius: 16px;
  background: #f9fafb;
  color: #111827;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input[type='text']:focus,
input[type='password']:focus {
  border-color: #f97316;
  box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.12);
  background: #ffffff;
  outline: none;
}

.form-options {
  display: flex;
  justify-content: flex-start;
}

.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.95rem;
  color: #475569;
}

.checkbox-wrapper input {
  width: 18px;
  height: 18px;
  accent-color: #f97316;
}

.login-btn {
  width: 100%;
  border: none;
  border-radius: 16px;
  padding: 1.05rem;
  background: #ff8c2b;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  box-shadow: 0 14px 30px rgba(251, 115, 37, 0.2);
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #f97316;
}

.login-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  box-shadow: none;
}

.error-message {
  margin-top: 1rem;
  color: #b91c1c;
  font-weight: 600;
}

.login-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #f8fafc;
}

.login-info h2 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: #111827;
}

.login-info p {
  margin: 1rem 0 2rem;
  color: #475569;
  line-height: 1.9;
}

.info-pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.info-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.15rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  color: #475569;
  font-size: 0.92rem;
  font-weight: 600;
}

@media (max-width: 980px) {
  .login-card {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 1rem;
  }

  .login-frame {
    width: 100%;
  }

  .login-header,
  .login-panel,
  .login-info {
    padding: 1.5rem;
  }

  .login-head h1 {
    font-size: 1.9rem;
  }
}
</style>
