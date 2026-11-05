<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { useData } from 'vitepress'
import mermaid from 'mermaid'

const { isDark } = useData()
const host = ref<HTMLElement | null>(null)
const ready = ref(false)
const renderId = `arch-flow-${Math.random().toString(36).slice(2, 9)}`

const diagram = `
flowchart TB
  subgraph ClientZone["业务脚本 · 任意平台"]
    direction TB
    Client["<b>客户端</b><br/><span style='font-family:ui-monospace,monospace;font-size:12px'>from tqcenter_remote import tq</span>"]
  end

  subgraph BridgeZone["Windows"]
    direction TB
    Bridge["<b>tq_bridge</b><br/>FastAPI 网关"]
  end

  subgraph LocalZone["本机通达信链路"]
    direction LR
    SDK["本机 SDK<br/><b>tqcenter.tq</b>"]
    DLL["原生库<br/><b>TPythClient.dll</b>"]
    TDX["终端<br/><b>通达信客户端</b>"]
    SDK --> DLL --> TDX
  end

  Client -->|"HTTP /rpc  +  WebSocket /ws/sub"| Bridge
  Bridge --> SDK
`.trim()

function themeVars(dark: boolean) {
  if (dark) {
    return {
      primaryColor: '#1a3d36',
      primaryTextColor: '#e8f4f0',
      primaryBorderColor: '#4db6a0',
      secondaryColor: '#1a2a38',
      secondaryTextColor: '#d7e8ef',
      secondaryBorderColor: '#6aa7d8',
      tertiaryColor: '#2a2418',
      tertiaryTextColor: '#f0e6d4',
      tertiaryBorderColor: '#c4a35a',
      lineColor: '#4db6a0',
      textColor: '#e8eef2',
      mainBkg: '#1a3d36',
      nodeBorder: '#4db6a0',
      clusterBkg: '#141c22',
      clusterBorder: '#3a5560',
      titleColor: '#9fd5c6',
      edgeLabelBackground: '#152028',
      fontFamily: 'Noto Sans SC, Segoe UI, sans-serif',
    }
  }
  return {
    primaryColor: '#e7f3ef',
    primaryTextColor: '#132029',
    primaryBorderColor: '#0f5c4c',
    secondaryColor: '#e8eef5',
    secondaryTextColor: '#132029',
    secondaryBorderColor: '#1a4f7a',
    tertiaryColor: '#f5efe4',
    tertiaryTextColor: '#132029',
    tertiaryBorderColor: '#8a6a2f',
    lineColor: '#0f5c4c',
    textColor: '#132029',
    mainBkg: '#e7f3ef',
    nodeBorder: '#0f5c4c',
    clusterBkg: '#f4f8fa',
    clusterBorder: '#9aaebb',
    titleColor: '#0f5c4c',
    edgeLabelBackground: '#ffffff',
    fontFamily: 'Noto Sans SC, Segoe UI, sans-serif',
  }
}

async function renderDiagram() {
  if (!host.value) return
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    theme: 'base',
    themeVariables: themeVars(isDark.value),
    flowchart: {
      curve: 'basis',
      padding: 18,
      nodeSpacing: 36,
      rankSpacing: 48,
      htmlLabels: true,
      useMaxWidth: true,
    },
  })
  const { svg } = await mermaid.render(renderId, diagram)
  host.value.innerHTML = svg
  const svgEl = host.value.querySelector('svg')
  if (svgEl) {
    svgEl.removeAttribute('height')
    svgEl.style.width = '100%'
    svgEl.style.maxWidth = '860px'
    svgEl.style.margin = '0 auto'
    svgEl.style.display = 'block'
  }
  ready.value = true
}

onMounted(() => {
  void nextTick(renderDiagram)
})

watch(isDark, () => {
  void nextTick(renderDiagram)
})
</script>

<template>
  <figure class="arch-mermaid" aria-label="tq-bridge 调用链路">
    <div v-show="!ready" class="arch-mermaid__placeholder">正在渲染架构图…</div>
    <div ref="host" class="arch-mermaid__canvas" />
  </figure>
</template>
