import service from './index'

/**
 * Generate a forecast from question and context
 * @param {Object} data - forecast request data
 * @returns {Promise}
 */
export function generateForecast(formData) {
  return service({
    url: '/api/forecast/generate',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * Get a forecast by ID
 * @param {String} forecastId
 * @returns {Promise}
 */
export function getForecast(forecastId) {
  return service({
    url: `/api/forecast/${forecastId}`,
    method: 'get'
  })
}
