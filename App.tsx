// frontend/src/App.tsx
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Header } from './components/Header';
import { UploadZone } from './components/UploadZone';
import { ResultsCard } from './components/ResultsCard';
import { LoadingSpinner } from './components/LoadingSpinner';
import { FeatureGrid } from './components/FeatureGrid';
import { PredictionResult } from './types';

function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const handleImageUpload = async (file: File) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setPrediction(data.prediction);
      setSelectedImage(URL.createObjectURL(file));
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      <Header />
      
      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <motion.section 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Identificación de Cultivos con
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-600">
              {" "}Inteligencia Artificial
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Apoyando a los pequeños agricultores colombianos con tecnología de vanguardia 
            para la detección temprana de enfermedades en sus cultivos
          </p>
        </motion.section>

        {/* Upload Section */}
        <section className="max-w-4xl mx-auto mb-16">
          <UploadZone onImageUpload={handleImageUpload} />
          
          <AnimatePresence>
            {isUploading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <LoadingSpinner />
              </motion.div>
            )}
          </AnimatePresence>

          {prediction && selectedImage && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8"
            >
              <ResultsCard 
                prediction={prediction} 
                imageUrl={selectedImage}
              />
            </motion.div>
          )}
        </section>

        {/* Features Grid */}
        <FeatureGrid />
      </main>
    </div>
  );
}

export default App;