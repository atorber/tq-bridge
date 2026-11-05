import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'tq-bridge',
  description: '通达信 tqcenter 跨平台远程调用：Windows 网关 + 远程 SDK',
  lang: 'zh-CN',
  base: '/tq-bridge/',
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ['meta', { name: 'theme-color', content: '#0f5c4c' }],
    [
      'link',
      {
        rel: 'preconnect',
        href: 'https://fonts.googleapis.com',
      },
    ],
    [
      'link',
      {
        rel: 'preconnect',
        href: 'https://fonts.gstatic.com',
        crossorigin: '',
      },
    ],
    [
      'link',
      {
        href: 'https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap',
        rel: 'stylesheet',
      },
    ],
  ],
  themeConfig: {
    logo: undefined,
    siteTitle: 'tq-bridge',
    nav: [
      { text: '首页', link: '/' },
      { text: '文档', link: '/guide/introduction', activeMatch: '/guide/' },
      { text: 'API', link: '/api/python-sdk', activeMatch: '/api/' },
      {
        text: 'GitHub',
        link: 'https://github.com/atorber/tq-bridge',
      },
    ],
    sidebar: {
      '/guide/': [
        {
          text: '开始',
          items: [
            { text: '介绍', link: '/guide/introduction' },
            { text: '架构', link: '/guide/architecture' },
            { text: '快速开始', link: '/guide/quick-start' },
          ],
        },
        {
          text: '使用指南',
          items: [
            { text: 'Windows 网关', link: '/guide/gateway' },
            { text: '远程客户端', link: '/guide/client' },
            { text: '模式选择', link: '/guide/modes' },
            { text: '常见问题', link: '/guide/faq' },
          ],
        },
      ],
      '/api/': [
        {
          text: 'API 参考',
          items: [
            { text: 'Python SDK', link: '/api/python-sdk' },
            { text: '网关 HTTP / WS', link: '/api/gateway-http' },
            { text: '配置项', link: '/api/config' },
          ],
        },
      ],
    },
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索', buttonAriaLabel: '搜索文档' },
          modal: {
            noResultsText: '没有结果',
            resetButtonTitle: '清除',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' },
          },
        },
      },
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/atorber/tq-bridge' },
    ],
    outline: {
      label: '本页目录',
      level: [2, 3],
    },
    docFooter: {
      prev: '上一页',
      next: '下一页',
    },
    lastUpdated: {
      text: '最后更新',
    },
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '主题',
    footer: {
      message: 'MIT License · 官方 DLL / tqcenter 仍遵循通达信许可',
      copyright: 'Copyright © 2026 atorber',
    },
  },
})
