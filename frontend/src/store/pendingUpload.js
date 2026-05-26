/**
 * 临时存储待上传的文件、链接、行情和需求
 * 用于首页点击启动引擎后立即跳转，在Process页面再进行API调用
 */
import { reactive } from 'vue'

const state = reactive({
  files: [],
  urls: [],
  marketContext: '',
  quotes: [],
  news: [],
  simulationRequirement: '',
  isPending: false
})

export function setPendingUpload(files, requirement, metadata = {}) {
  state.files = files
  state.urls = metadata.urls || []
  state.marketContext = metadata.marketContext || ''
  state.quotes = metadata.quotes || []
  state.news = metadata.news || []
  state.simulationRequirement = requirement
  state.isPending = true
}

export function getPendingUpload() {
  return {
    files: state.files,
    urls: state.urls,
    marketContext: state.marketContext,
    quotes: state.quotes,
    news: state.news,
    simulationRequirement: state.simulationRequirement,
    isPending: state.isPending
  }
}

export function clearPendingUpload() {
  state.files = []
  state.urls = []
  state.marketContext = ''
  state.quotes = []
  state.news = []
  state.simulationRequirement = ''
  state.isPending = false
}

export default state
