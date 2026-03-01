<template>
  <div class="home-view">
    <div class="hero-section">
      <h1>3D AI角色创作平台</h1>
      <p class="subtitle">使用AI技术快速创建3D角色模型</p>
      <div class="cta-buttons">
        <router-link to="/create" class="btn-primary">开始创作</router-link>
        <router-link to="/templates" class="btn-secondary">浏览模板</router-link>
      </div>
    </div>

    <div class="features-section">
      <h2>核心功能</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🤖</div>
          <h3>AI智能生成</h3>
          <p>通过文字描述自动生成3D角色</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎨</div>
          <h3>在线编辑</h3>
          <p>实时预览和调整模型细节</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📦</div>
          <h3>多格式导出</h3>
          <p>支持多种3D模型格式导出</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">☁️</div>
          <h3>云端存储</h3>
          <p>项目自动保存到云端</p>
        </div>
      </div>
    </div>

    <div class="quick-start">
      <h2>快速开始</h2>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h4>选择创作方式</h4>
            <p>AI生成、上传模型或使用模板</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>编辑和优化</h4>
            <p>使用3D编辑器调整模型</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>导出使用</h4>
            <p>下载模型应用到你的项目</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.home-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero-section {
  text-align: center;
  padding: 100px 20px;
}

.hero-section h1 {
  font-size: 3rem;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.cta-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 15px 30px;
  border-radius: 30px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s ease;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: white;
  color: #667eea;
}

.features-section {
  padding: 80px 20px;
  background: white;
  color: #333;
}

.features-section h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 60px;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  text-align: center;
  padding: 40px 30px;
  border-radius: 15px;
  background: #f8f9fa;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

.quick-start {
  padding: 80px 20px;
  background: #f8f9fa;
  color: #333;
}

.quick-start h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 60px;
}

.steps {
  display: flex;
  justify-content: center;
  gap: 60px;
  flex-wrap: wrap;
  max-width: 1000px;
  margin: 0 auto;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  max-width: 300px;
}

.step-number {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content h4 {
  font-size: 1.3rem;
  margin-bottom: 10px;
  color: #333;
}

.step-content p {
  color: #666;
  line-height: 1.6;
}
</style>