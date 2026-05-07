<template>
  <div class="login-container">
    <div class="info-panel">
      <div class="logo-section">
        <div class="logo">DF</div>
        <h1>DataForge</h1>
        <p>数据管理工具</p>
      </div>
      <div class="did-you-know">
        <h4>Did you know?</h4>
        <p>You can sync data from all popular cloud storage providers to collect new items for labeling as they are uploaded, and return the annotation results to train and continuously improve models. <a>Learn more</a></p>
      </div>
      <div class="footer">
        <span>Brought to you by</span>
        <strong>HumanSignal</strong>
      </div>
    </div>
    <div class="login-panel">
      <div class="login-card">
        <h2>Log in</h2>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username">User Name</label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              placeholder="User Name"
            />
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              placeholder="Password"
            />
          </div>
          <div class="form-options">
            <input type="checkbox" id="keep-logged-in" />
            <label for="keep-logged-in">Keep me logged in this browser</label>
          </div>
          <button type="submit" :disabled="loading" class="login-btn">
            {{ loading ? 'Logging in...' : 'Log in' }}
          </button>
        </form>
        <p class="signup-link">
          Don't have an account? <a>Sign up</a>
        </p>
        <p v-if="error" class="error">{{ error }}</p>
      </div>
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
    error.value = err.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
}

.info-panel {
  flex: 1;
  padding: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: linear-gradient(to bottom right, #fde2e2, #f0f2f5);
}

.logo-section .logo {
  width: 48px;
  height: 48px;
  background-color: #d9534f;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.logo-section h1 {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.logo-section p {
  color: #6c757d;
}

.did-you-know {
  background-color: #e9ecef;
  padding: 1.5rem;
  border-radius: 8px;
  margin: 2rem 0;
}

.did-you-know h4 {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.did-you-know p {
  color: #495057;
}

.did-you-know a {
  color: #007bff;
  text-decoration: underline;
}

.footer {
  font-size: 0.875rem;
  color: #6c757d;
}

.footer strong {
  color: #000;
}

.login-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
  border-radius: 1rem;
  background: white;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.login-card h2 {
  font-size: 1.75rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 2rem;
}

.login-form {
  display: grid;
  gap: 1.5rem;
}

.form-group {
  display: grid;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  color: #495057;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.form-options {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-options label {
  font-size: 0.875rem;
  color: #495057;
}

.login-btn {
  width: 100%;
  padding: 0.875rem;
  border: none;
  border-radius: 0.5rem;
  background: #343a40;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background: #23272b;
}

.signup-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.signup-link a {
  color: #007bff;
  text-decoration: none;
}

.error {
  margin-top: 1.25rem;
  color: #b91c1c;
  text-align: center;
  font-weight: 600;
}
</style>