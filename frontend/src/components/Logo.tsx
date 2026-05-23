import { motion } from 'framer-motion';

export default function Logo({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = {
    sm: { icon: 'text-2xl', text: 'text-lg' },
    md: { icon: 'text-4xl', text: 'text-2xl' },
    lg: { icon: 'text-6xl', text: 'text-4xl' },
  };

  const s = sizes[size];

  return (
    <motion.div
      className="flex items-center gap-3"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Animated emoji icon */}
      <motion.div
        className={`${s.icon} relative`}
        animate={{ rotate: [0, 5, -5, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      >
        <span role="img" aria-label="emoji">🎨</span>
      </motion.div>

      {/* App name */}
      <div className="flex flex-col leading-tight">
        <span className={`${s.text} font-bold gradient-text`}>
          Emoji
        </span>
        <span className={`${s.text} font-light text-text-secondary -mt-1`}>
          Recognizer
        </span>
      </div>
    </motion.div>
  );
}
