// Simplified API Client - No retries
import { getApiUrl } from '@config/api';

class ApiClient {
  constructor() {
    this.timeout = 30000;
  }

  // Check if URL is already absolute
  isAbsoluteURL(url) {
    return url.startsWith('http://') || url.startsWith('https://');
  }

  // Make HTTP request
  async request(url, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    const config = {
      ...options,
      headers
    };

    // Use full URL if absolute, otherwise prepend baseURL
    const fullURL = this.isAbsoluteURL(url) ? url : getApiUrl(url);

    const response = await fetch(fullURL, config);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    // Try to parse as JSON
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    } else {
      return await response.text();
    }
  }

  // GET request
  async get(url, options = {}) {
    return this.request(url, { ...options, method: 'GET' });
  }

  // POST request
  async post(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data)
    });
  }
}

const apiClient = new ApiClient();
export default apiClient;
