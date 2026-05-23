import { motion } from 'framer-motion';
import AuthForm from '../components/AuthForm';
import Logo from '../components/Logo';

const floatingEmojis = ['😊', '😢', '😠', '😮', '😐', '😍', '❤️', '⭐', '👍', '☀️'];

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-mesh relative overflow-hidden px-4">
      {/* Floating emojis background */}
      {floatingEmojis.map((emoji, i) => (
        <motion.span
          key={i}
          className="absolute text-4xl sm:text-5xl floating-emoji select-none pointer-events-none opacity-10"
          style={{
            left: `${5 + (i * 9) % 90}%`,
            top: `${10 + (i * 13) % 80}%`,
          }}
          animate={{
            y: [0, -20, 10, 0],
            rotate: [0, 10, -8, 0],
          }}
          transition={{
            duration: 5 + i * 0.7,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: i * 0.3,
          }}
        >
          {emoji}
        </motion.span>
      ))}

      {/* Content */}
      <div className="relative z-10 w-full max-w-md flex flex-col items-center gap-8">
        {/* Logo */}
        <Logo size="lg" />

        {/* Tagline */}
        <motion.p
          className="text-text-secondary text-center text-sm sm:text-base max-w-xs"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          Draw emojis, and our AI will recognize them instantly ✨
        </motion.p>

        {/* Auth form */}
        <AuthForm />

        {/* Footer */}
        <motion.p
          className="text-text-muted text-xs text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          Powered by Artificial Neural Network 🧠
        </motion.p>
      </div>
    </div>
  );
}
