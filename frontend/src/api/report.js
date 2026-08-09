import service, { requestWithRetry } from './index'

/**
 * 开始报告生成
 * @param {Object} data - { simulation_id, force_regenerate? }
 */
export const generateReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/generate', data), 3, 1000)
}

/**
 * 获取报告生成状态
 * @param {string} reportId
 */
export const getReportStatus = (reportId) => {
  return service.get(`/api/report/generate/status`, { params: { report_id: reportId } })
}

/**
 * 获取 Agent 日志（增量）
 * @param {string} reportId
 * @param {number} fromLine - 从第几行开始获取
 */
export const getAgentLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/agent-log`, { params: { from_line: fromLine } })
}

/**
 * 获取控制台日志（增量）
 * @param {string} reportId
 * @param {number} fromLine - 从第几行开始获取
 */
export const getConsoleLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/console-log`, { params: { from_line: fromLine } })
}

/**
 * 获取报告详情
 * @param {string} reportId
 */
export const getReport = (reportId) => {
  return service.get(`/api/report/${reportId}`)
}

/**
 * 与 Report Agent 对话
 * @param {Object} data - { simulation_id, message, chat_history? }
 */
export const chatWithReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/chat', data), 3, 1000)
}

/**
 * 下载报告文件
 *
 * 不能用 <a href> 直链：所有 /api/ 都要 Bearer token，浏览器导航不会带上它，
 * 直链会被 401 打回登录页。所以走 axios 拿 blob，再本地造一个下载。
 *
 * @param {string} reportId
 * @param {'pdf'|'md'} format
 */
export const downloadReportFile = async (reportId, format = 'pdf') => {
  const path = format === 'pdf'
    ? `/api/report/${reportId}/download/pdf`
    : `/api/report/${reportId}/download`

  try {
    const blob = await service.get(path, { responseType: 'blob' })
    triggerBlobDownload(blob, `${reportId}.${format}`)
  } catch (error) {
    // responseType:'blob' 让错误体也变成 Blob，拦截器取不到 data.error，
    // 用户会看到 "Request failed with status code 500" 这种没用的话。
    const payload = error?.response?.data
    if (payload instanceof Blob) {
      try {
        const parsed = JSON.parse(await payload.text())
        if (parsed?.error) error.message = parsed.error
      } catch {
        // 不是 JSON 就保持原样
      }
    }
    throw error
  }
}

function triggerBlobDownload(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  // Firefox 会在 click 之后异步读 URL，立刻 revoke 会拿到空文件
  setTimeout(() => URL.revokeObjectURL(url), 10_000)
}
