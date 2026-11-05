<script setup lang="ts">
import { VueFlow, Handle, Position, MarkerType } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import '@vue-flow/core/dist/style.css'

type HandleSpec = { type: 'source' | 'target'; position: Position; id?: string }

const card = (
  id: string,
  parent: string,
  x: number,
  y: number,
  data: { eyebrow: string; title: string; sub?: string; tone: string; handles: HandleSpec[] },
): Node => ({
  id,
  type: 'card',
  parentNode: parent,
  extent: 'parent',
  position: { x, y },
  data,
})

const nodes: Node[] = [
  {
    id: 'zone-dev',
    type: 'zone',
    position: { x: 0, y: 0 },
    data: { label: '开发机', hint: 'macOS · Linux · Windows' },
    style: { width: '258px', height: '330px' },
    zIndex: -1,
  },
  {
    id: 'zone-win',
    type: 'zone',
    position: { x: 330, y: 0 },
    data: { label: 'Windows 主机', hint: '通达信已登录' },
    style: { width: '718px', height: '330px' },
    zIndex: -1,
  },
  card('agent', 'zone-dev', 24, 52, {
    eyebrow: 'AI Agent',
    title: 'Agent Skill',
    sub: 'scripts/call.py',
    tone: 'violet',
    handles: [{ type: 'source', position: Position.Bottom }],
  }),
  card('client', 'zone-dev', 24, 205, {
    eyebrow: '业务脚本',
    title: 'tqcenter_remote',
    sub: 'from tqcenter_remote import tq',
    tone: 'teal',
    handles: [
      { type: 'target', position: Position.Top },
      { type: 'source', position: Position.Right },
    ],
  }),
  card('bridge', 'zone-win', 24, 52, {
    eyebrow: '网关',
    title: 'tq_bridge',
    sub: 'FastAPI · :18787',
    tone: 'blue',
    handles: [
      { type: 'target', position: Position.Left },
      { type: 'source', position: Position.Bottom },
    ],
  }),
  card('sdk', 'zone-win', 24, 205, {
    eyebrow: '本机 SDK',
    title: 'tqcenter.tq',
    tone: 'slate',
    handles: [
      { type: 'target', position: Position.Top },
      { type: 'source', position: Position.Right },
    ],
  }),
  card('dll', 'zone-win', 254, 205, {
    eyebrow: '原生库',
    title: 'TPythClient.dll',
    tone: 'slate',
    handles: [
      { type: 'target', position: Position.Left },
      { type: 'source', position: Position.Right },
    ],
  }),
  card('tdx', 'zone-win', 484, 205, {
    eyebrow: '终端',
    title: '通达信客户端',
    tone: 'amber',
    handles: [{ type: 'target', position: Position.Left }],
  }),
]

const flow = (id: string, source: string, target: string, label?: string, color = '#34d3b0'): Edge => ({
  id,
  source,
  target,
  type: 'smoothstep',
  animated: true,
  label,
  style: { stroke: color, strokeWidth: 2 },
  markerEnd: { type: MarkerType.ArrowClosed, color, width: 18, height: 18 },
  labelStyle: { fill: '#e6f6f1', fontSize: '12px', fontWeight: 600 },
  labelBgStyle: { fill: '#0b1a20', fillOpacity: 0.92 },
  labelBgPadding: [8, 5] as [number, number],
  labelBgBorderRadius: 6,
})

const edges: Edge[] = [
  flow('e-agent', 'agent', 'client', 'call.py', '#a78bfa'),
  flow('e-net', 'client', 'bridge', 'HTTP /rpc · WS /ws/sub', '#38bdf8'),
  flow('e-bridge', 'bridge', 'sdk'),
  flow('e-sdk', 'sdk', 'dll'),
  flow('e-dll', 'dll', 'tdx', undefined, '#fbbf24'),
]
</script>

<template>
  <figure class="arch-x" aria-label="tq-bridge 架构图">
    <VueFlow
      :nodes="nodes"
      :edges="edges"
      :fit-view-on-init="true"
      :fit-view-params="{ padding: 0.08 }"
      :nodes-draggable="false"
      :nodes-connectable="false"
      :elements-selectable="false"
      :zoom-on-scroll="false"
      :zoom-on-pinch="false"
      :zoom-on-double-click="false"
      :pan-on-drag="false"
      :prevent-scrolling="false"
      :min-zoom="0.2"
    >
      <Background pattern-color="#1f3a44" :gap="18" :size="1.2" />

      <template #node-zone="{ data }">
        <div class="arch-x__zone">
          <span class="arch-x__zone-label">{{ data.label }}</span>
          <span class="arch-x__zone-hint">{{ data.hint }}</span>
        </div>
      </template>

      <template #node-card="{ data }">
        <div class="arch-x__card" :class="`is-${data.tone}`">
          <Handle
            v-for="(h, i) in data.handles"
            :key="i"
            :type="h.type"
            :position="h.position"
            class="arch-x__handle"
          />
          <span class="arch-x__eyebrow">{{ data.eyebrow }}</span>
          <strong class="arch-x__title">{{ data.title }}</strong>
          <code v-if="data.sub" class="arch-x__sub">{{ data.sub }}</code>
        </div>
      </template>
    </VueFlow>
  </figure>
</template>
