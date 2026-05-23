import { motion } from 'framer-motion';

const EMOJI_CATEGORIES = [
  { id: 0, name: 'happy',    emoji: '😊', label: 'Happy' },
  { id: 1, name: 'sad',      emoji: '😢', label: 'Sad' },
  { id: 2, name: 'angry',    emoji: '😠', label: 'Angry' },
  { id: 3, name: 'surprise', emoji: '😮', label: 'Surprise' },
  { id: 4, name: 'neutral',  emoji: '😐', label: 'Neutral' },
  { id: 5, name: 'love',     emoji: '😍', label: 'Love' },
  { id: 6, name: 'heart',    emoji: '❤️', label: 'Heart' },
  { id: 7, name: 'star',     emoji: '⭐', label: 'Star' },
  { id: 8, name: 'thumbsup', emoji: '👍', label: 'Thumbs Up' },
  { id: 9, name: 'sun',      emoji: '☀️', label: 'Sun' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.8, y: 10 },
  show: { opacity: 1, scale: 1, y: 0 },
};

export default function EmojiGrid() {
  return (
    <div className="w-full">
      <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
        Supported Emojis
      </h3>
      <motion.div
        className="grid grid-cols-5 gap-2"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {EMOJI_CATEGORIES.map((cat) => (
          <motion.div
            key={cat.id}
            variants={itemVariants}
            whileHover={{ scale: 1.15, rotate: 8 }}
            whileTap={{ scale: 0.9 }}
            className="flex flex-col items-center gap-1 p-2 rounded-xl bg-bg-card hover:bg-bg-card-hover transition-colors cursor-default"
            title={cat.label}
          >
            <span className="text-2xl sm:text-3xl">{cat.emoji}</span>
            <span className="text-[10px] text-text-muted font-medium truncate w-full text-center">
              {cat.label}
            </span>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
