<script setup>
import { onMounted, ref } from 'vue';
import gsap from 'gsap';

const experiments = ref([
  {
    id: 'nn-from-scratch',
    title: '从零构建神经网络',
    desc: '使用 NumPy 手动实现前向传播和反向传播，理解梯度下降的本质',
    difficulty: '基础',
    duration: '45 min',
    tags: ['深度学习', 'NumPy']
  },
  {
    id: 'brain-signal',
    title: 'EEG 脑电信号分析',
    desc: '加载真实脑电数据，进行频域分析和事件相关电位提取',
    difficulty: '进阶',
    duration: '60 min',
    tags: ['脑科学', 'Signal Processing']
  },
  {
    id: 'transformer-attention',
    title: 'Transformer 注意力机制',
    desc: '可视化自注意力矩阵，理解 Query-Key-Value 的计算流程',
    difficulty: '进阶',
    duration: '50 min',
    tags: ['NLP', 'Transformer']
  },
  {
    id: 'bci-motor',
    title: '运动想象 BCI 分类',
    desc: '基于 CSP 特征提取和 SVM 分类器，实现脑机接口运动想象识别',
    difficulty: '高级',
    duration: '90 min',
    tags: ['BCI', '脑机接口']
  },
  {
    id: 'gan-generation',
    title: 'GAN 图像生成',
    desc: '训练生成对抗网络，观察生成器与判别器的博弈过程',
    difficulty: '进阶',
    duration: '70 min',
    tags: ['生成模型', 'PyTorch']
  },
  {
    id: 'neuron-simulation',
    title: 'Hodgkin-Huxley 神经元模型',
    desc: '模拟生物神经元的动作电位产生过程，理解离子通道动力学',
    difficulty: '高级',
    duration: '80 min',
    tags: ['计算神经科学', '仿真']
  }
]);

onMounted(() => {
  gsap.fromTo('.lab-header > *',
    { y: 30, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.8, stagger: 0.1, ease: 'expo.out' }
  );
  gsap.fromTo('.experiment-card',
    { y: 40, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.8, stagger: 0.05, ease: 'expo.out', delay: 0.2 }
  );
});
</script>

<template>
  <div class="lab-view">
    <div class="container lab-layout">
      <!-- Left sidebar: Header & Description -->
      <aside class="lab-header">
        <div class="indicator mono">
          <div class="dot"></div>
          EXPERIMENTS
        </div>
        <h1 class="display">前沿研究与<br>交互式实验</h1>
        <div class="separator"></div>
        <p class="desc">
          在基于云端的 Jupyter 环境中运行真实的计算模型。涵盖从底层的数学原理推导到顶级的神经活动信号分析，所有数据集与环境均已配置完毕。
        </p>
        <button class="btn btn-primary btn-launch-all">
          进入主工作台 <span>→</span>
        </button>
      </aside>

      <!-- Right content: Experiments Grid -->
      <main class="lab-grid">
        <article
          v-for="(exp, index) in experiments"
          :key="exp.id"
          class="experiment-card"
        >
          <div class="card-top">
            <span class="mono index">{{ String(index + 1).padStart(2, '0') }}</span>
            <div class="meta mono">
              <span class="difficulty">{{ exp.difficulty }}</span>
              <span class="duration">{{ exp.duration }}</span>
            </div>
          </div>

          <h3 class="title">{{ exp.title }}</h3>
          <p class="desc-text">{{ exp.desc }}</p>

          <div class="card-bottom">
            <div class="tags">
              <span v-for="tag in exp.tags" :key="tag" class="tag mono">{{ tag }}</span>
            </div>
            <button class="launch-btn" aria-label="Start Experiment">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M5 12h14M12 5l7 7-7 7" stroke-linecap="square"/>
              </svg>
            </button>
          </div>
        </article>
      </main>
    </div>
  </div>
</template>

<style scoped>
.lab-view {
  min-height: 100vh;
  background: var(--surface-0);
  padding-top: calc(var(--nav-height) + 60px);
  padding-bottom: 100px;
}

.lab-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 80px;
  align-items: start;
}

/* ── Header ── */
.lab-header {
  position: sticky;
  top: calc(var(--nav-height) + 60px);
}

.indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 24px;
}

.indicator .dot {
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
}

.lab-header h1 {
  font-size: 3rem;
  color: var(--text-1);
  margin-bottom: 32px;
}

.separator {
  width: 40px;
  height: 2px;
  background: var(--text-1);
  margin-bottom: 32px;
}

.desc {
  color: var(--text-3);
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 48px;
}

.btn-launch-all {
  width: 100%;
  justify-content: space-between;
}

.btn-launch-all span {
  transition: transform var(--dur-2) ease;
}

.btn-launch-all:hover span {
  transform: translateX(4px);
}

/* ── Grid ── */
.lab-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.experiment-card {
  border: 1px solid var(--border-default);
  padding: 32px;
  display: flex;
  flex-direction: column;
  background: var(--surface-0);
  transition: border-color var(--dur-2) ease;
}

.experiment-card:hover {
  border-color: var(--primary);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.index {
  color: var(--border-strong);
  font-size: 16px;
  font-weight: 700;
}

.meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--text-4);
}

.difficulty {
  color: var(--primary);
  font-weight: 600;
}

.title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-1);
  margin-bottom: 12px;
}

.desc-text {
  color: var(--text-3);
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 40px;
  flex: 1;
}

.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 1px solid var(--border-subtle);
  padding-top: 24px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  font-size: 10px;
  color: var(--text-3);
  background: var(--surface-1);
  padding: 4px 8px;
  border: 1px solid var(--border-default);
}

.launch-btn {
  color: var(--text-4);
  transition: color var(--dur-2) ease;
}

.experiment-card:hover .launch-btn {
  color: var(--primary);
}

@media (max-width: 1024px) {
  .lab-layout {
    grid-template-columns: 1fr;
    gap: 48px;
  }

  .lab-header {
    position: static;
  }

  .lab-header h1 {
    font-size: 2.5rem;
  }
}

@media (max-width: 640px) {
  .lab-grid {
    grid-template-columns: 1fr;
  }
}
</style>
