import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { historyAPI } from '../services/api';
import { HiOutlineTrash } from 'react-icons/hi';

interface HistoryItem {
  id: number;
  predicted_emoji: string;
  predicted_label: string;
  confidence: number;
  top_predictions: string | null;
  created_at: string;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    historyAPI.getHistory()
      .then((res) => setHistory(res.data.predictions))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  const confidenceColor = (conf: number) => {
    if (conf >= 80) return 'text-accent-green';
    if (conf >= 50) return 'text-accent-amber';
    return 'text-accent-red';
  };

  return (
    <div className="min-h-screen pt-20 pb-10 bg-mesh">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        {/* Header */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold">
            <span className="gradient-text">Recognition History</span>
          </h1>
          <p className="text-text-secondary mt-2 text-sm">
            Your past emoji predictions ({history.length} total)
          </p>
        </motion.div>

        {/* Loading state */}
        {loading && (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="skeleton h-20 rounded-xl" />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && history.length === 0 && (
          <motion.div
            className="glass rounded-2xl p-12 text-center"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="text-6xl mb-4 opacity-30">📭</div>
            <h3 className="text-lg font-semibold text-text-secondary">No predictions yet</h3>
            <p className="text-text-muted text-sm mt-2">
              Go draw some emojis and come back to see your history!
            </p>
          </motion.div>
        )}

        {/* History list */}
        <div className="space-y-3">
          {history.map((item, i) => {
            let topPreds: any[] = [];
            try {
              topPreds = item.top_predictions ? JSON.parse(item.top_predictions) : [];
            } catch {}

            return (
              <motion.div
                key={item.id}
                className="glass rounded-xl p-4 flex items-center gap-4 hover:bg-bg-card-hover transition-colors"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                {/* Emoji */}
                <div className="text-4xl">{item.predicted_emoji}</div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-text-primary">{item.predicted_label}</h3>
                    <span className={`text-sm font-semibold ${confidenceColor(item.confidence)}`}>
                      {item.confidence.toFixed(1)}%
                    </span>
                  </div>
                  {/* Other predictions */}
                  {topPreds.length > 1 && (
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-text-muted">Also:</span>
                      {topPreds.slice(1).map((p: any) => (
                        <span key={p.class_id} className="text-xs text-text-muted">
                          {p.emoji} {p.confidence.toFixed(0)}%
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Date */}
                <div className="text-xs text-text-muted whitespace-nowrap hidden sm:block">
                  {formatDate(item.created_at)}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
