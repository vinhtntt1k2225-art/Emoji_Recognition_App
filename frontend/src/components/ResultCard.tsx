import { motion, AnimatePresence } from 'framer-motion';

interface Prediction {
  class_id: number;
  name: string;
  emoji: string;
  label: string;
  confidence: number;
}

interface ResultCardProps {
  predictions: Prediction[] | null;
  isVisible: boolean;
}

const confidenceColor = (conf: number) => {
  if (conf >= 80) return 'from-accent-green to-emerald-400';
  if (conf >= 50) return 'from-accent-amber to-yellow-400';
  return 'from-accent-red to-orange-400';
};

const confidenceTextColor = (conf: number) => {
  if (conf >= 80) return 'text-accent-green';
  if (conf >= 50) return 'text-accent-amber';
  return 'text-accent-red';
};

export default function ResultCard({ predictions, isVisible }: ResultCardProps) {
  if (!predictions || predictions.length === 0) return null;

  const top = predictions[0];

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="glass-strong rounded-2xl p-6 w-full max-w-md"
          initial={{ opacity: 0, y: 30, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ type: 'spring', stiffness: 120, damping: 15 }}
        >
          {/* Top prediction */}
          <div className="flex flex-col items-center mb-6">
            <motion.div
              className="text-7xl mb-3 relative"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: 'spring', stiffness: 200, damping: 10, delay: 0.1 }}
            >
              {top.confidence >= 80 && (
                <motion.div
                  className="absolute inset-0 rounded-full"
                  initial={{ scale: 0.8, opacity: 0.8 }}
                  animate={{ scale: 2, opacity: 0 }}
                  transition={{ duration: 1, repeat: 2 }}
                  style={{
                    background: 'radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%)',
                  }}
                />
              )}
              <span>{top.emoji}</span>
            </motion.div>

            <motion.h3
              className="text-xl font-bold text-text-primary"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              {top.label}
            </motion.h3>

            <motion.div
              className={`text-lg font-semibold mt-1 ${confidenceTextColor(top.confidence)}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              {top.confidence.toFixed(1)}% confident
            </motion.div>
          </div>

          {/* All predictions bar chart */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              Top Predictions
            </h4>
            {predictions.map((pred, i) => (
              <motion.div
                key={pred.class_id}
                className="flex items-center gap-3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 * (i + 1) }}
              >
                <span className="text-2xl w-10 text-center">{pred.emoji}</span>
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-text-secondary">{pred.label}</span>
                    <span className={`text-sm font-semibold ${confidenceTextColor(pred.confidence)}`}>
                      {pred.confidence.toFixed(1)}%
                    </span>
                  </div>
                  <div className="confidence-bar">
                    <motion.div
                      className={`confidence-fill bg-gradient-to-r ${confidenceColor(pred.confidence)}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.max(pred.confidence, 2)}%` }}
                      transition={{ duration: 0.8, delay: 0.2 * (i + 1), ease: [0.22, 1, 0.36, 1] }}
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
