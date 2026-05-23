import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import Canvas from '../components/Canvas';
import ResultCard from '../components/ResultCard';
import EmojiGrid from '../components/EmojiGrid';
import { predictAPI } from '../services/api';

interface Prediction {
  class_id: number;
  name: string;
  emoji: string;
  label: string;
  confidence: number;
}

export default function HomePage() {
  const [predictions, setPredictions] = useState<Prediction[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showResult, setShowResult] = useState(false);

  const handlePredict = useCallback(async (dataUrl: string) => {
    setIsLoading(true);
    setShowResult(false);

    try {
      const response = await predictAPI.predict(dataUrl);
      setPredictions(response.data.predictions);
      setShowResult(true);
    } catch (err: any) {
      console.error('Prediction failed:', err);
      setPredictions([{
        class_id: -1,
        name: 'error',
        emoji: '❓',
        label: err.response?.data?.detail || 'Prediction failed',
        confidence: 0,
      }]);
      setShowResult(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="min-h-screen pt-20 pb-10 bg-mesh">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Header */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl sm:text-4xl font-bold">
            <span className="gradient-text">Draw Your Emoji</span>
          </h1>
          <p className="text-text-secondary mt-2 text-sm sm:text-base">
            Use your mouse to draw an emoji, then let our ANN recognize it
          </p>
        </motion.div>

        {/* Main content */}
        <div className="flex flex-col lg:flex-row items-start justify-center gap-8">
          {/* Left side: Emoji guide */}
          <motion.div
            className="w-full lg:w-56 order-3 lg:order-1"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="glass rounded-2xl p-4">
              <EmojiGrid />
            </div>
          </motion.div>

          {/* Center: Canvas */}
          <motion.div
            className="w-full lg:flex-1 max-w-lg order-1 lg:order-2 flex justify-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Canvas onExport={handlePredict} isLoading={isLoading} />
          </motion.div>

          {/* Right side: Results */}
          <motion.div
            className="w-full lg:w-80 order-2 lg:order-3 flex justify-center"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            {showResult ? (
              <ResultCard predictions={predictions} isVisible={showResult} />
            ) : (
              <div className="glass rounded-2xl p-6 w-full max-w-md text-center">
                <div className="text-5xl mb-4 opacity-20">🤔</div>
                <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-2">
                  Result
                </h3>
                <p className="text-text-muted text-sm">
                  Draw an emoji and click <strong className="text-primary-light">"Recognize"</strong> to see the AI prediction
                </p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Info section */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <div className="inline-flex items-center gap-6 text-text-muted text-xs">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
              <span>ANN Model Active</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span>🧠</span>
              <span>4-Layer Neural Network</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span>📊</span>
              <span>10 Emoji Classes</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
