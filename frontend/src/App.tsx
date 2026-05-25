import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Header } from './components/Header';
import { UploadZone } from './components/UploadZone';
import { ResultsCard } from './components/ResultsCard';
import { LoadingSpinner } from './components/LoadingSpinner';
import { FeatureGrid } from './components/FeatureGrid';
import { ModelStatus } from './components/ModelStatus';
import { PredictionResult, HealthStatus } from './types';

const API_BASE = import.meta.env.VITE_API_URL || '';

function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const handleImageUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setPrediction(null);

    const formData = new FormData();
    formData.append('file', file);
    setSelectedImage(URL.createObjectURL(file));

    try {
      const response = await fetch(`${API_BASE}/api/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        const msg = err.detail || 'Error al procesar la imagen';
        if (response.status === 503) {
          throw new Error(
            `${msg}. El modelo debe entrenarse con tu dataset PlantVillage (scripts/train.py).`
          );
        }
        throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
      }

      const data = await response.json();
      const pred = data.prediction;
      if (pred && !pred.analysis && pred.plantInfo) {
        pred.analysis = {
          recognized: pred.confidence >= 0.55,
          speciesName: pred.plantInfo.plantType,
          speciesConfidence: pred.confidence,
          statusLabel: pred.plantInfo.healthStatus,
          conditionShort: pred.plantInfo.condition,
          isHealthy: !pred.plantInfo.hasPest && !pred.plantInfo.hasDisease,
          hasPest: pred.plantInfo.hasPest,
          hasDisease: pred.plantInfo.hasDisease,
        };
      }
      if (pred && !pred.plantInfo && pred.recommendations) {
        pred.plantInfo = pred.recommendations;
      }
      setPrediction(pred);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error de conexión con el servidor');
      setSelectedImage(null);
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setPrediction(null);
    setSelectedImage(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      <Header />

      <main className="container mx-auto px-4 py-12">
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Identificación de Plantas Agrícolas con{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-600">
              Inteligencia Artificial
            </span>
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Plataforma para el reconocimiento de cultivos y malezas en el contexto colombiano.
            Sube una foto y obtén diagnóstico, confianza y recomendaciones agronómicas.
          </p>
        </motion.section>

        {health && <ModelStatus health={health} />}

        <section className="max-w-4xl mx-auto mb-16">
          <UploadZone onImageUpload={handleImageUpload} disabled={isUploading} />

          <AnimatePresence>
            {isUploading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <LoadingSpinner />
              </motion.div>
            )}
          </AnimatePresence>

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
              {error}
              <p className="text-sm mt-2 text-red-600">
                Verifica que el backend esté activo: <code>uvicorn backend.main:app --reload</code>
              </p>
            </div>
          )}

          {prediction && selectedImage && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mt-8">
              <ResultsCard prediction={prediction} imageUrl={selectedImage} />
              <button
                onClick={handleReset}
                className="mt-4 w-full py-3 text-green-700 font-medium hover:bg-green-50 rounded-xl transition-colors"
              >
                Analizar otra imagen
              </button>
            </motion.div>
          )}
        </section>

        <FeatureGrid />

        <section id="metodologia" className="max-w-4xl mx-auto py-12 text-gray-600">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Objetivos del proyecto</h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>Dataset estructurado de especies agrícolas y malezas (Kaggle / campo)</li>
            <li>CNN con transfer learning (MobileNetV2) para clasificación de imágenes</li>
            <li>Interfaz web intuitiva para agricultores y técnicos</li>
            <li>Evaluación de precisión y usabilidad en pruebas piloto</li>
          </ul>
        </section>
      </main>

      <footer className="bg-white border-t py-6 text-center text-gray-500 text-sm">
        AgroPlantas Colombia © {new Date().getFullYear()} — Prototipo académico
      </footer>
    </div>
  );
}

export default App;
