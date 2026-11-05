<template>
  <figure class="arch-flow" aria-label="tq-bridge 调用链路">
    <div class="arch-flow__stage">
      <p class="arch-flow__eyebrow">业务脚本 · 任意平台</p>
      <p class="arch-flow__title">客户端</p>
      <code class="arch-flow__code">from tqcenter_remote import tq</code>
    </div>

    <div class="arch-flow__edge" aria-hidden="true">
      <span class="arch-flow__line"></span>
      <span class="arch-flow__proto">HTTP <code>/rpc</code> + WebSocket <code>/ws/sub</code></span>
      <span class="arch-flow__arrow">↓</span>
    </div>

    <div class="arch-flow__stage arch-flow__stage--bridge">
      <p class="arch-flow__eyebrow">Windows</p>
      <p class="arch-flow__title">tq_bridge</p>
      <p class="arch-flow__meta">FastAPI 网关</p>
    </div>

    <div class="arch-flow__edge arch-flow__edge--short" aria-hidden="true">
      <span class="arch-flow__line"></span>
      <span class="arch-flow__arrow">↓</span>
    </div>

    <div class="arch-flow__chain" role="list">
      <div class="arch-flow__node" role="listitem">
        <span class="arch-flow__node-label">本机 SDK</span>
        <strong>tqcenter.tq</strong>
      </div>
      <span class="arch-flow__chain-arrow" aria-hidden="true">→</span>
      <div class="arch-flow__node" role="listitem">
        <span class="arch-flow__node-label">原生库</span>
        <strong>TPythClient.dll</strong>
      </div>
      <span class="arch-flow__chain-arrow" aria-hidden="true">→</span>
      <div class="arch-flow__node arch-flow__node--end" role="listitem">
        <span class="arch-flow__node-label">终端</span>
        <strong>通达信客户端</strong>
      </div>
    </div>
  </figure>
</template>
