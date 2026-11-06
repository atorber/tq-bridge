<script setup lang="ts">
import { computed } from 'vue'
import { withBase } from 'vitepress'

const props = withDefaults(
  defineProps<{
    src?: string
    title?: string
  }>(),
  {
    src: '/TdxQuant接口说明文档.pdf',
    title: 'TdxQuant接口说明文档',
  },
)

const href = computed(() => withBase(props.src))
</script>

<template>
  <div class="pdf-embed">
    <p class="pdf-embed__bar">
      <a class="pdf-embed__link" :href="href" target="_blank" rel="noopener">新窗口打开</a>
      <span class="pdf-embed__sep">·</span>
      <a class="pdf-embed__link" :href="href" download>下载 PDF</a>
    </p>
    <iframe
      class="pdf-embed__frame"
      :src="href"
      :title="title"
      loading="lazy"
    />
  </div>
</template>
