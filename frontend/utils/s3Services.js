import { PutObjectCommand, DeleteObjectCommand } from "@aws-sdk/client-s3";
import s3Client from "./s3Client";

// Get bucket name hardcoded
const BUCKET_NAME = "hacklytics2025wat";

export const s3Services = {
  /**
   * Uploads a file to S3
   * @param {File} file - The file to upload
   * @param {string} type - The type of content ('image', 'video', 'audio', 'pdf')
   * @returns {Promise<string>} - The URL of the uploaded file
   */
  uploadFile: async (file, type) => {
    try {
      // Generate a unique file name
      const timestamp = Date.now();
      const fileName = `${type}/${timestamp}-${file.name}`;

      // Set the appropriate content type
      let contentType;
      switch (type) {
        case 'image':
          contentType = file.type || 'image/jpeg';
          break;
        case 'video':
          contentType = file.type || 'video/mp4';
          break;
        case 'audio':
          contentType = file.type || 'audio/mpeg';
          break;
        case 'pdf':
          contentType = 'application/pdf';
          break;
        default:
          throw new Error('Invalid file type');
      }

      // Convert file to buffer
      const fileBuffer = await file.arrayBuffer();

      // Upload to S3
      const uploadParams = {
        Bucket: BUCKET_NAME,
        Key: fileName,
        Body: Buffer.from(fileBuffer),
        ContentType: contentType,
      };

      const command = new PutObjectCommand(uploadParams);
      await s3Client.send(command);

      // Return the S3 URL
      return `https://${BUCKET_NAME}.s3.amazonaws.com/${fileName}`;
    } catch (error) {
      console.error('Error uploading file to S3:', error);
      throw error;
    }
  },

  /**
   * Uploads multiple files to S3
   * @param {File[]} files - Array of files to upload
   * @param {string} type - The type of content
   * @returns {Promise<string[]>} - Array of uploaded file URLs
   */
  uploadMultipleFiles: async (files, type) => {
    try {
      const uploadPromises = Array.from(files).map(file => 
        s3Services.uploadFile(file, type)
      );
      return await Promise.all(uploadPromises);
    } catch (error) {
      console.error('Error uploading multiple files:', error);
      throw error;
    }
  },

  /**
   * Deletes a file from S3
   * @param {string} fileUrl - The URL of the file to delete
   * @returns {Promise<void>}
   */
  deleteFile: async (fileUrl) => {
    try {
      // Extract the key from the URL
      const key = fileUrl.split('.com/')[1];

      const deleteParams = {
        Bucket: BUCKET_NAME,
        Key: key,
      };

      const command = new DeleteObjectCommand(deleteParams);
      await s3Client.send(command);
    } catch (error) {
      console.error('Error deleting file from S3:', error);
      throw error;
    }
  },

  /**
   * Batch delete files from S3
   * @param {string[]} fileUrls - Array of file URLs to delete
   * @returns {Promise<void>}
   */
  deleteMultipleFiles: async (fileUrls) => {
    try {
      const deletePromises = fileUrls.map(url => 
        s3Services.deleteFile(url)
      );
      await Promise.all(deletePromises);
    } catch (error) {
      console.error('Error deleting multiple files:', error);
      throw error;
    }
  }
}; 