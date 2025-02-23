'use client';
import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faImage, 
  faVideo, 
  faFilePdf, 
  faUpload,
  faMagnifyingGlass,
  faSpinner,
  faExclamationCircle,
  faCheckCircle,
  faTrash
} from '@fortawesome/free-solid-svg-icons';
import { apiService } from '../utils/apiService';

export default function Home() {
  const [files, setFiles] = useState({
    images: [],
    videos: [],
    pdfs: []
  });
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e, type) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => ({
      ...prev,
      [type]: [...prev[type], ...selectedFiles]
    }));
    setError(null);
    setResults(null);
  };

  const removeFile = (type, index) => {
    setFiles(prev => ({
      ...prev,
      [type]: prev[type].filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Check if at least one file is selected
    if (files.images.length === 0 && files.videos.length === 0 && files.pdfs.length === 0) {
      setError('Please select at least one file for analysis');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setResults(null);

    try {
      const result = await apiService.analyzeFraud(
        files.images,
        files.videos,
        files.pdfs
      );

      setResults(result);
      
      // Clear file selections
      setFiles({
        images: [],
        videos: [],
        pdfs: []
      });
    } catch (error) {
      console.error('Analysis error:', error);
      setError(error.message || 'An error occurred during analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  const renderFileList = (type) => {
    if (files[type].length === 0) return null;

    return (
      <div className="mt-2">
        <ul className="space-y-1">
          {files[type].map((file, index) => (
            <li key={index} className="flex items-center justify-between text-sm text-gray-600 bg-gray-50 p-2 rounded">
              <span className="truncate">{file.name}</span>
              <button
                onClick={() => removeFile(type, index)}
                className="text-red-500 hover:text-red-700 ml-2"
              >
                <FontAwesomeIcon icon={faTrash} />
              </button>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <div className="mt-12 bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Analysis Results</h2>
        <pre className="bg-gray-50 rounded-lg p-4 overflow-auto">
          {JSON.stringify(results, null, 2)}
        </pre>
      </div>
    );
  };

  const renderLoadingOverlay = () => {
    if (!analyzing) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 text-center">
          <FontAwesomeIcon 
            icon={faSpinner} 
            className="text-4xl text-blue-600 animate-spin mb-4" 
          />
          <p className="text-lg text-gray-700">Analyzing your files...</p>
        </div>
      </div>
    );
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

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-3 gap-6">
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
              {renderFileList('images')}
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
              {renderFileList('videos')}
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
              {renderFileList('pdfs')}
            </div>
          </div>

          <button
            type="submit"
            disabled={analyzing || (files.images.length === 0 && files.videos.length === 0 && files.pdfs.length === 0)}
            className={`w-full mt-8 bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 px-6 rounded-xl 
                     shadow-lg hover:from-blue-600 hover:to-blue-700 transform transition-all hover:scale-105
                     flex items-center justify-center space-x-2 font-semibold
                     ${(analyzing || (files.images.length === 0 && files.videos.length === 0 && files.pdfs.length === 0)) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <FontAwesomeIcon 
              icon={analyzing ? faSpinner : faMagnifyingGlass} 
              className={analyzing ? 'animate-spin' : ''} 
            />
            <span>{analyzing ? 'Analyzing...' : 'Analyze Files for Fraud'}</span>
          </button>
        </form>

        {renderResults()}
        {renderLoadingOverlay()}
      </div>
    </main>
  );
} 