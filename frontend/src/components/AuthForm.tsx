import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';
import { HiOutlineMail, HiOutlineLockClosed, HiOutlineUser, HiOutlineEye, HiOutlineEyeOff } from 'react-icons/hi';

export default function AuthForm() {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(username, password);
      } else {
        if (!email) {
          setError('Email is required');
          setLoading(false);
          return;
        }
        await register(username, email, password);
      }
    } catch (err: any) {
      let msg = 'Something went wrong';
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        msg = detail;
      } else if (Array.isArray(detail) && detail.length > 0) {
        msg = detail[0].msg;
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
  };

  return (
    <motion.div
      className="glass-strong rounded-2xl p-8 w-full max-w-md mx-auto"
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 100, damping: 15 }}
    >
      {/* Header */}
      <div className="text-center mb-8">
        <motion.h2
          className="text-2xl font-bold text-text-primary"
          key={isLogin ? 'login' : 'register'}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </motion.h2>
        <p className="text-text-secondary text-sm mt-2">
          {isLogin ? 'Sign in to start drawing' : 'Join the emoji drawing community'}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Username */}
        <div className="relative">
          <HiOutlineUser className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-lg" />
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="input-field pl-10"
            required
            id="auth-username"
          />
        </div>

        {/* Email (register only) */}
        <AnimatePresence>
          {!isLogin && (
            <motion.div
              className="relative"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <HiOutlineMail className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-lg" />
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field pl-10"
                id="auth-email"
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Password */}
        <div className="relative">
          <HiOutlineLockClosed className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-lg" />
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-field pl-10 pr-10"
            required
            id="auth-password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors cursor-pointer"
          >
            {showPassword ? <HiOutlineEyeOff className="text-lg" /> : <HiOutlineEye className="text-lg" />}
          </button>
        </div>

        {/* Error message */}
        <AnimatePresence>
          {error && (
            <motion.div
              className="text-accent-red text-sm bg-accent-red/10 border border-accent-red/20 rounded-lg px-4 py-2"
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Submit */}
        <motion.button
          type="submit"
          className="btn-primary w-full py-3 text-base cursor-pointer"
          whileTap={{ scale: 0.97 }}
          disabled={loading}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <motion.span
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full inline-block"
                animate={{ rotate: 360 }}
                transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
              />
              {isLogin ? 'Signing in...' : 'Creating account...'}
            </span>
          ) : (
            isLogin ? 'Sign In' : 'Create Account'
          )}
        </motion.button>
      </form>

      {/* Toggle */}
      <div className="mt-6 text-center">
        <span className="text-text-muted text-sm">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
        </span>
        <button
          onClick={toggleMode}
          className="text-primary-light text-sm font-semibold hover:underline cursor-pointer"
        >
          {isLogin ? 'Sign Up' : 'Sign In'}
        </button>
      </div>
    </motion.div>
  );
}
