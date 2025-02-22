'use client';
import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faImage, 
  faVideo, 
  faFileAudio, 
  faFilePdf, 
  faUpload,
  faMagnifyingGlass,
  faTrash,
  faCheckCircle,
  faExclamationCircle
} from '@fortawesome/free-solid-svg-icons';
import { s3Services } from '../utils/s3Services';

export default function Home() {
  const [files, setFiles] = useState({
    images: [],
    videos: [],
    audio: [],
    pdfs: []
  });
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e, type) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => ({
      ...prev,
      [type]: selectedFiles
    }));
    setError(null);
    setSuccess(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    setError(null);
    setSuccess(false);
    
    try {
      const uploadPromises = [];
      const fileTypes = ['images', 'videos', 'audio', 'pdfs'];
      
      // Create upload promises for each file type
      fileTypes.forEach(type => {
        if (files[type].length > 0) {
          const s3Type = type === 'pdfs' ? 'pdf' : type.slice(0, -1); // Convert plural to singular
          uploadPromises.push(s3Services.uploadMultipleFiles(files[type], s3Type));
        }
      });

      if (uploadPromises.length === 0) {
        throw new Error('Please select at least one file to upload');
      }

      // Wait for all uploads to complete
      const results = await Promise.all(uploadPromises);
      const uploadedUrls = results.flat();
      
      // Clear file selections
      setFiles({
        images: [],
        videos: [],
        audio: [],
        pdfs: []
      });
      
      // Update uploaded files list
      setUploadedFiles(prev => [...prev, ...uploadedUrls]);
      setSuccess(true);
      
    } catch (error) {
      console.error('Error in handleSubmit:', error);
      setError(error.message || 'An error occurred during upload');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (url) => {
    try {
      await s3Services.deleteFile(url);
      setUploadedFiles(uploadedFiles.filter(f => f !== url));
    } catch (error) {
      setError('Failed to delete file: ' + error.message);
    }
  };

  const getFileTypeFromUrl = (url) => {
    const path = url.split('/');
    return path[path.length - 2]; // Gets the type from the path structure type/filename
  };

  const renderFilePreview = (url) => {
    const type = getFileTypeFromUrl(url);
    const fileName = url.split('/').pop();

    switch (type) {
      case 'image':
        return <img src={url} alt={fileName} className="h-16 w-16 object-cover rounded" />;
      case 'video':
        return (
          <video className="h-16 w-16 object-cover rounded">
            <source src={url} type="video/mp4" />
          </video>
        );
      case 'audio':
        return (
          <audio controls className="h-8 w-48">
            <source src={url} type="audio/mpeg" />
          </audio>
        );
      case 'pdf':
        return (
          <div className="h-16 w-16 flex items-center justify-center bg-red-100 rounded">
            <FontAwesomeIcon icon={faFilePdf} className="text-red-500 text-xl" />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-blue-100">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-blue-800 mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-800">
            Fraud Detection Analysis
          </h1>
          <p className="text-blue-600 text-lg">
            Upload your files for fraud detection analysis
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
            <FontAwesomeIcon icon={faExclamationCircle} className="mr-2" />
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded relative">
            <FontAwesomeIcon icon={faCheckCircle} className="mr-2" />
            Files uploaded successfully!
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Image Input Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 transform transition-all hover:scale-105">
              <div className="text-blue-500 mb-4">
                <FontAwesomeIcon icon={faImage} size="2x" />
              </div>
              <label className="block mb-2 font-semibold text-gray-700">
                Images
              </label>
              <div className="relative">
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => handleFileChange(e, 'images')}
                  className="opacity-0 absolute inset-0 w-full h-full cursor-pointer"
                />
                <div className="border-2 border-dashed border-blue-200 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
                  <FontAwesomeIcon icon={faUpload} className="text-blue-400 mb-2" />
                  <p className="text-sm text-blue-600">Drop images or click to upload</p>
                </div>
              </div>
              <p className="text-sm text-blue-500 mt-2">
                Selected: {files.images.length} images
              </p>
            </div>

            {/* Video Input Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 transform transition-all hover:scale-105">
              <div className="text-blue-500 mb-4">
                <FontAwesomeIcon icon={faVideo} size="2x" />
              </div>
              <label className="block mb-2 font-semibold text-gray-700">
                Videos
              </label>
              <div className="relative">
                <input
                  type="file"
                  accept="video/*"
                  multiple
                  onChange={(e) => handleFileChange(e, 'videos')}
                  className="opacity-0 absolute inset-0 w-full h-full cursor-pointer"
                />
                <div className="border-2 border-dashed border-blue-200 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
                  <FontAwesomeIcon icon={faUpload} className="text-blue-400 mb-2" />
                  <p className="text-sm text-blue-600">Drop videos or click to upload</p>
                </div>
              </div>
              <p className="text-sm text-blue-500 mt-2">
                Selected: {files.videos.length} videos
              </p>
            </div>

            {/* Audio Input Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 transform transition-all hover:scale-105">
              <div className="text-blue-500 mb-4">
                <FontAwesomeIcon icon={faFileAudio} size="2x" />
              </div>
              <label className="block mb-2 font-semibold text-gray-700">
                Audio Files
              </label>
              <div className="relative">
                <input
                  type="file"
                  accept="audio/*"
                  multiple
                  onChange={(e) => handleFileChange(e, 'audio')}
                  className="opacity-0 absolute inset-0 w-full h-full cursor-pointer"
                />
                <div className="border-2 border-dashed border-blue-200 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
                  <FontAwesomeIcon icon={faUpload} className="text-blue-400 mb-2" />
                  <p className="text-sm text-blue-600">Drop audio or click to upload</p>
                </div>
              </div>
              <p className="text-sm text-blue-500 mt-2">
                Selected: {files.audio.length} audio files
              </p>
            </div>

            {/* PDF Input Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 transform transition-all hover:scale-105">
              <div className="text-blue-500 mb-4">
                <FontAwesomeIcon icon={faFilePdf} size="2x" />
              </div>
              <label className="block mb-2 font-semibold text-gray-700">
                PDF Documents
              </label>
              <div className="relative">
                <input
                  type="file"
                  accept=".pdf"
                  multiple
                  onChange={(e) => handleFileChange(e, 'pdfs')}
                  className="opacity-0 absolute inset-0 w-full h-full cursor-pointer"
                />
                <div className="border-2 border-dashed border-blue-200 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
                  <FontAwesomeIcon icon={faUpload} className="text-blue-400 mb-2" />
                  <p className="text-sm text-blue-600">Drop PDFs or click to upload</p>
                </div>
              </div>
              <p className="text-sm text-blue-500 mt-2">
                Selected: {files.pdfs.length} PDFs
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={uploading}
            className={`w-full mt-8 bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 px-6 rounded-xl 
                     shadow-lg hover:from-blue-600 hover:to-blue-700 transform transition-all hover:scale-105
                     flex items-center justify-center space-x-2 font-semibold
                     ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <FontAwesomeIcon icon={uploading ? faUpload : faMagnifyingGlass} className={uploading ? 'animate-spin' : ''} />
            <span>{uploading ? 'Uploading...' : 'Analyze Files for Fraud'}</span>
          </button>
        </form>

        {uploadedFiles.length > 0 && (
          <div className="mt-12 bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Uploaded Files</h2>
            <div className="space-y-4">
              {uploadedFiles.map((url, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center space-x-4">
                    {renderFilePreview(url)}
                    <span className="text-sm text-gray-600 truncate max-w-xs">
                      {url.split('/').pop()}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDelete(url)}
                    className="text-red-500 hover:text-red-700 transition-colors"
                  >
                    <FontAwesomeIcon icon={faTrash} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
} 