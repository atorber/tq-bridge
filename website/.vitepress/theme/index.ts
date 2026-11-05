import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import ArchFlow from './ArchFlow.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ArchFlow', ArchFlow)
  },
} satisfies Theme
