const API_BASE_URL = 'http://localhost:8000';

export const apiService = {
  /**
   * Analyze multiple files for fraud detection
   * @param {File[]} images - Array of image files
   * @param {File[]} videos - Array of video files
   * @param {File[]} pdfs - Array of PDF files
   * @returns {Promise} Analysis results
   */
  analyzeFraud: async (images = [], videos = [], pdfs = []) => {
    try {
      const formData = new FormData();
      
      // Append all files to FormData with appropriate field names
      images.forEach(file => {
        formData.append('images', file);
      });
      
      videos.forEach(file => {
        formData.append('videos', file);
      });
      
      pdfs.forEach(file => {
        formData.append('pdfs', file);
      });

      const response = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Analysis failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error analyzing files:', error);
      throw new Error(error.message || 'Failed to analyze files');
    }
  }
}; 