import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import ArchFlow from './ArchFlow.vue'
import PdfEmbed from './PdfEmbed.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ArchFlow', ArchFlow)
    app.component('PdfEmbed', PdfEmbed)
  },
} satisfies Theme
