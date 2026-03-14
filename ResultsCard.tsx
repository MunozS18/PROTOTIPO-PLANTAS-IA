// frontend/src/components/ResultsCard.tsx
import React from 'react';
import { motion } from 'framer-motion';
    import { 
  FiCheckCircle, 
  FiAlertTriangle, 
  FiAlertCircle,
  FiThermometer,
  FiDroplet,
  FiSun
} from 'react-icons/fi';
import { PredictionResult } from '../types';

interface ResultsCardProps {
  prediction: PredictionResult;
  imageUrl: string;
}

export const ResultsCard: React.FC<ResultsCardProps> = ({ prediction, imageUrl }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'low': return <FiCheckCircle className="w-6 h-6" />;
      case 'medium': return <FiAlertTriangle className="w-6 h-6" />;
      case 'high': return <FiAlertCircle className="w-6 h-6" />;
      default: return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-xl overflow-hidden"
    >
      <div className="grid md:grid-cols-2 gap-6">
        {/* Image Preview */}
        <div className="relative h-96 md:h-full">
          <img 
            src={imageUrl} 
            alt="Cultivo analizado"
            className="w-full h-full object-cover"
          />
          <div className="absolute top-4 left-4">
            <span className="px-3 py-1 bg-black/50 backdrop-blur-sm text-white text-sm rounded-full">
              Imagen analizada
            </span>
          </div>
        </div>

        {/* Results */}
        <div className="p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Resultado del Análisis
          </h3>

          {/* Main Prediction */}
          <div className="mb-8">
            <div className="text-sm text-gray-500 mb-1">Diagnóstico</div>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {prediction.className}
            </div>
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border ${getSeverityColor(prediction.recommendations.severity)}`}>
              {getSeverityIcon(prediction.recommendations.severity)}
              <span className="font-medium">
                {prediction.recommendations.severity === 'low' && 'Leve'}
                {prediction.recommendations.severity === 'medium' && 'Moderado'}
                {prediction.recommendations.severity === 'high' && 'Severo'}
              </span>
            </div>
          </div>

          {/* Confidence Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">Confianza del modelo</span>
              <span className="font-semibold text-gray-900">
                {(prediction.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${prediction.confidence * 100}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className={`h-full rounded-full ${
                  prediction.confidence > 0.7 
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                    : prediction.confidence > 0.4
                    ? 'bg-gradient-to-r from-yellow-500 to-orange-500'
                    : 'bg-gradient-to-r from-red-500 to-pink-500'
                }`}
             />
            </div>
          </div>

          {/* Probabilities */}
            <div className="mb-8">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">
              Probabilidades por clase
            </h4>
            <div className="space-y-3">
              {prediction.probabilities.map((item, index) => (
                <div key={index}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{item.className}</span>
                    <span className="font-medium text-gray-900">
                      {(item.probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.probability * 100}%` }}
                      transition={{ duration: 0.8, delay: index * 0.1 }}
                      className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-gray-50 rounded-xl p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              📋 Recomendaciones
            </h4>
            <p className="text-gray-700 mb-4">
              {prediction.recommendations.description}
            </p>
            <ul className="space-y-2">
              {prediction.recommendations.actions.map((action, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  className="flex items-start gap-2"
                >
                  <span className="text-green-600 mt-1">•</span>
                  <span className="text-gray-600">{action}</span>
                </motion.li>
              ))}
            </ul>

            {/* Environmental Factors */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h5 className="text-sm font-semibold text-gray-700 mb-3">
                Factores ambientales a considerar
              </h5>
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center">
                  <FiThermometer className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <span className="text-xs text-gray-500">Temperatura</span>
                </div>
                <div className="text-center">
                  <FiDroplet className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <span className="text-xs text-gray-500">Humedad</span>
                </div>
                <div className="text-center">
                  <FiSun className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <span className="text-xs text-gray-500">Luz solar</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};