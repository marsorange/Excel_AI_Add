// API 配置文件
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-production-api.com' 
  : 'https://localhost:8000';  // 改为 HTTPS

export const API_ENDPOINTS = {
  // 认证相关
  REGISTER: `${API_BASE_URL}/register`,
  LOGIN: `${API_BASE_URL}/token`,
  USER_INFO: `${API_BASE_URL}/users/me`,
  
  // 公式相关
  GENERATE_FORMULA: `${API_BASE_URL}/api/generate-formula`,
  EXPLAIN_FORMULA: `${API_BASE_URL}/api/explain-formula`,
  OPTIMIZE_FORMULA: `${API_BASE_URL}/api/optimize-formula`,
  DIAGNOSE_ERROR: `${API_BASE_URL}/api/diagnose-error`,
  
  // Agent 相关
  AGENT_CHAT: `${API_BASE_URL}/agent/chat`,
};

export default API_BASE_URL;