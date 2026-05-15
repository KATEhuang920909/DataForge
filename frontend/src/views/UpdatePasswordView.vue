<template>
  <div class="login-page">
    <div class="login-background" />
    <div class="login-frame">
      <main class="login-card">
        <section class="login-panel">
          <div class="login-head">
            <h1>修改密码</h1>
            <p>请输入您的用户名、旧密码和新密码。</p>
          </div>

          <form @submit.prevent="handleUpdatePassword" class="login-form">
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
              <label for="oldPassword">旧密码</label>
              <input
                id="oldPassword"
                v-model="oldPassword"
                type="password"
                required
                autocomplete="current-password"
                placeholder="请输入旧密码"
              />
            </div>

            <div class="form-group">
              <label for="newPassword">新密码</label>
              <input
                id="newPassword"
                v-model="newPassword"
                type="password"
                required
                autocomplete="new-password"
                placeholder="请输入新密码"
              />
            </div>

            <div class="form-group">
              <label for="confirmPassword">确认新密码</label>
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                type="password"
                required
                autocomplete="new-password"
                placeholder="请再次输入新密码"
              />
            </div>

            <button type="submit" :disabled="loading" class="login-btn">
              {{ loading ? '修改中...' : '确认修改' }}
            </button>
          </form>

          <p v-if="error" class="error-message">{{ error }}</p>
          <p v-if="success" class="success-message">{{ success }}</p>
           <div class="form-options">
              <router-link to="/login" class="forgot-password">返回登录</router-link>
            </div>
        </section>

        <aside class="login-info">
          <h2>安全提示</h2>
          <p>
            为了保护您的账户安全，请定期修改密码，并使用包含字母、数字和符号的复杂密码。
          </p>
          <div class="info-pill-list">
            <span class="info-pill">定期更换</span>
            <span class="info-pill">高强度密码</span>
            <span class="info-pill">保障安全</span>
          </div>
        </aside>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { updateUserPassword } from '@/api'

const router = useRouter()
const username = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleUpdatePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次输入的新密码不一致'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await updateUserPassword(username.value, oldPassword.value, newPassword.value)
    success.value = '密码修改成功！2秒后将跳转到登录页面。'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || '密码修改失败，请重试'
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

.success-message {
  margin-top: 1rem;
  color: #16a34a;
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

.form-options {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 1rem;
}

.forgot-password {
  font-size: 0.95rem;
  color: #475569;
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
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

  .login-panel,
  .login-info {
    padding: 1.5rem;
  }

  .login-head h1 {
    font-size: 1.9rem;
  }
}
</style>
