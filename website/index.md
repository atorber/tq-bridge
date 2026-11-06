---
layout: home
title: 通达信跨平台远程调用
hero:
  name: tq-bridge
  text: 同一套 tqcenter API，跨机器调用通达信
  tagline: Windows 上开网关，macOS / Linux / Windows 客户端只改包名即可取数。
  actions:
    - theme: brand
      text: 开始使用
      link: /guide/introduction
    - theme: alt
      text: Agent Skill
      link: /guide/skill
---

<div class="home-shell">

<section class="home-block home-arch">
  <header class="home-block__head">
    <p class="home-kicker">Architecture</p>
    <h2>一条链路，两端同构</h2>
    <p>任意平台脚本经网关到达本机通达信，方法名与官方 tqcenter 对齐。</p>
  </header>

  <ClientOnly>
    <ArchFlow />
  </ClientOnly>

  <p class="home-block__more">
    <a href="./guide/architecture">架构说明</a>
  </p>
</section>

<section class="home-block home-start">
  <header class="home-block__head">
    <p class="home-kicker">Get started</p>
    <h2>三步跑通</h2>
    <p>网关常开后，开发机一行安装、一行取数。</p>
  </header>

  <ol class="home-steps">
    <li>
      <strong>Windows 启网关</strong>
      <pre class="home-code"><code>pip install tq-bridge
python -m tq_bridge</code></pre>
    </li>
    <li>
      <strong>配置网关地址</strong>
      <pre class="home-code"><code>export TQ_BRIDGE_URL=http://&lt;windows-ip&gt;:18787
export TQ_BRIDGE_TOKEN=your_secret</code></pre>
    </li>
    <li>
      <strong>改包名调用</strong>
      <pre class="home-code"><code>from tqcenter_remote import tq
tq.initialize(__file__)
print(tq.get_market_snapshot(stock_code="688318.SH"))</code></pre>
    </li>
  </ol>

  <div class="home-skill">
    <div>
      <strong>Agent Skill</strong>
      <p>一句话装到全部 Agent，用自然语言取数。</p>
    </div>
    <pre class="home-code home-code--inline"><code>npx skills add atorber/tq-bridge --skill tqcenter_remote -a '*' -g -y</code></pre>
  </div>
</section>

<section class="home-block home-cap">
  <header class="home-block__head">
    <p class="home-kicker">Capabilities</p>
    <h2>覆盖日常取数</h2>
    <p>远程 SDK 转发官方公开方法；交易接口可在网关侧关闭。</p>
  </header>

  <ul class="home-caps">
    <li>
      <strong>行情与 K 线</strong>
      <span>快照、复权 K 线、除权因子、涨跌停与量价</span>
    </li>
    <li>
      <strong>标的与板块</strong>
      <span>股票列表、板块树、成分股、代码匹配</span>
    </li>
    <li>
      <strong>财务与日历</strong>
      <span>财报、交易日历、IPO / 可转债 / 股本等</span>
    </li>
    <li>
      <strong>订阅与文件</strong>
      <span>WebSocket 行情推送、文件上传下载、print_to_tdx</span>
    </li>
  </ul>

  <div class="home-cta">
    <a class="home-cta__primary" href="./guide/quick-start">快速开始</a>
    <a class="home-cta__ghost" href="./api/python-sdk">API 参考</a>
    <a class="home-cta__ghost" href="https://github.com/atorber/tq-bridge" target="_blank" rel="noreferrer">GitHub</a>
  </div>
</section>

</div>
