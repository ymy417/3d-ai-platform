<template>
  <div class="modeling-view">
    <div class="header">
      <button class="home-btn" @click="goHome">
        <span class="home-icon">🏠</span> 返回主页
      </button>
      <h1>建模页面（开发中）</h1>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.modeling-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
  position: relative;
}

.home-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.home-btn:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.home-icon {
  font-size: 1.2rem;
}

.header h1 {
  font-size: 2.5rem;
  color: #333;
  margin: 0;
}
</style>