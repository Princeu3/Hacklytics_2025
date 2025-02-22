// This file now contains helper functions to interact with the S3 API route

import { S3Client } from "@aws-sdk/client-s3";

// Initialize S3 client with hardcoded credentials
const s3Client = new S3Client({
  region: "us-east-1",
  credentials: {
    accessKeyId: "AKIA3QPM2DHQSZ2JKD4E",
    secretAccessKey: "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",
  },
});

export default s3Client;

// S3 operation helper functions

/**
 * Upload a file to S3
 * @param {string} fileName - Name of the file
 * @param {string} fileData - Base64 encoded file data
 * @param {string} contentType - MIME type of the file
 */
export async function uploadToS3(fileName, fileData, contentType) {
  return handleS3Operation('upload', { fileName, fileData, contentType });
}

/**
 * Get a signed URL for a file
 * @param {string} fileName - Name of the file to get URL for
 */
export async function getSignedUrl(fileName) {
  return handleS3Operation('getSignedUrl', { fileName });
}

/**
 * Delete a file from S3
 * @param {string} fileName - Name of the file to delete
 */
export async function deleteFromS3(fileName) {
  return handleS3Operation('delete', { fileName });
}

async function handleS3Operation(operation, data) {
  try {
    const response = await fetch('/api/s3', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        operation,
        data,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'S3 operation failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in S3 operation:', error);
    throw error;
  }
} 