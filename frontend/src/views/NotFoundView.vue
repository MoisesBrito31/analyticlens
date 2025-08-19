<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <!-- Ícone animado -->
      <div class="icon-container">
        <div class="robot-icon">🤖</div>
        <div class="search-icon">🔍</div>
        <div class="confused-icon">😵</div>
      </div>
      
      <!-- Título principal -->
      <h1 class="error-code">404</h1>
      <h2 class="error-title">Ops! Página não encontrada</h2>
      
      <!-- Mensagem engraçada -->
      <div class="funny-message">
        <p class="message-text">
          Parece que nossa máquina de visão computacional perdeu o foco! 
          Ela estava procurando por esta página, mas acabou encontrando um gato dormindo no servidor. 😸
        </p>
        <p class="message-text">
          Enquanto ela tenta se reorientar, que tal voltar para o caminho certo?
        </p>
      </div>
      
      <!-- Botões de ação -->
      <div class="action-buttons">
        <router-link to="/" class="btn btn-primary">
          <span class="btn-icon">🏠</span>
          Voltar para Casa
        </router-link>
        <button @click="goBack" class="btn btn-secondary">
          <span class="btn-icon">⬅️</span>
          Voltar Anterior
        </button>
      </div>
      
      <!-- Dica técnica -->
      <div class="tech-tip">
        <div class="tip-icon">💡</div>
        <p class="tip-text">
          <strong>Dica:</strong> Se você acha que deveria existir uma página aqui, 
          pode ser que ela tenha sido movida para outro lugar ou ainda esteja sendo construída 
          pelos nossos robôs desenvolvedores!
        </p>
      </div>
      
      <!-- Easter egg -->
      <div class="easter-egg" @click="showEasterEgg">
        <span class="egg-text">Clique aqui se você gosta de piadas de programador</span>
      </div>
    </div>
    
    <!-- Modal do Easter Egg -->
    <div v-if="easterEggVisible" class="easter-egg-modal" @click="hideEasterEgg">
      <div class="modal-content" @click.stop>
        <h3>🤖 Piada de Programador</h3>
        <p class="joke-text">{{ currentJoke }}</p>
        <button @click="nextJoke" class="btn btn-primary">Próxima Piada</button>
        <button @click="hideEasterEgg" class="btn btn-secondary">Fechar</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView',
  data() {
    return {
      easterEggVisible: false,
      currentJokeIndex: 0,
      jokes: [
        "Por que o programador foi ao médico? Porque ele tinha bugs! 🐛",
        "Quantos programadores são necessários para trocar uma lâmpada? Nenhum, é um problema de hardware! 💡",
        "O que o programador disse quando foi demitido? 'Foi um bug, não uma feature!' 🐛",
        "Por que o programador não consegue dormir? Porque ele está debugando! 😴",
        "Qual é a bebida favorita do programador? Java! ☕",
        "O que o programador disse para o café? 'Você é a única coisa que me mantém acordado!' ☕",
        "Por que o programador sempre confunde Halloween com Natal? Porque Oct 31 = Dec 25! 🎃",
        "O que o programador disse quando resolveu um bug difícil? 'Eureka! Agora posso dormir!' 😴",
        "Qual é o animal favorito do programador? O Python! 🐍",
        "Por que o programador foi ao parque? Para fazer um debug ao ar livre! 🌳"
      ]
    }
  },
  computed: {
    currentJoke() {
      return this.jokes[this.currentJokeIndex]
    }
  },
  methods: {
    goBack() {
      this.$router.go(-1)
    },
    showEasterEgg() {
      this.easterEggVisible = true
    },
    hideEasterEgg() {
      this.easterEggVisible = false
    },
    nextJoke() {
      this.currentJokeIndex = (this.currentJokeIndex + 1) % this.jokes.length
    }
  }
}
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.not-found-content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 600px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.icon-container {
  position: relative;
  margin-bottom: 30px;
}

.robot-icon {
  font-size: 4rem;
  animation: bounce 2s infinite;
}

.search-icon {
  position: absolute;
  top: -10px;
  right: -20px;
  font-size: 2rem;
  animation: rotate 3s linear infinite;
}

.confused-icon {
  position: absolute;
  bottom: -10px;
  left: -20px;
  font-size: 2rem;
  animation: shake 1s infinite;
}

.error-code {
  font-size: 6rem;
  font-weight: bold;
  color: #667eea;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  animation: pulse 2s infinite;
}

.error-title {
  font-size: 2rem;
  color: #333;
  margin: 20px 0;
  font-weight: 600;
}

.funny-message {
  margin: 30px 0;
}

.message-text {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin: 15px 0;
}

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin: 30px 0;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: linear-gradient(45deg, #f093fb, #f5576c);
  color: white;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(240, 147, 251, 0.4);
}

.btn-icon {
  font-size: 1.2rem;
}

.tech-tip {
  background: linear-gradient(45deg, #ffecd2, #fcb69f);
  border-radius: 15px;
  padding: 20px;
  margin: 30px 0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.tip-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.tip-text {
  color: #8b4513;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
}

.easter-egg {
  margin-top: 30px;
  padding: 15px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.easter-egg:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.02);
}

.egg-text {
  color: #667eea;
  font-size: 0.9rem;
  font-style: italic;
}

/* Modal do Easter Egg */
.easter-egg-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 30px;
  max-width: 500px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  color: #667eea;
  margin-bottom: 20px;
}

.joke-text {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin: 20px 0;
  font-style: italic;
}

.modal-content .btn {
  margin: 10px;
}

/* Animações */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

/* Responsividade */
@media (max-width: 768px) {
  .not-found-content {
    padding: 30px 20px;
    margin: 20px;
  }
  
  .error-code {
    font-size: 4rem;
  }
  
  .error-title {
    font-size: 1.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 250px;
    justify-content: center;
  }
  
  .tech-tip {
    flex-direction: column;
    text-align: center;
  }
}
</style>
