import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, useLocation } from 'react-router-dom';
import Logo from './Logo';
import { HiOutlineLogout, HiOutlineClock, HiOutlineHome } from 'react-icons/hi';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <motion.nav
      className="fixed top-0 left-0 right-0 z-50 glass-strong"
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 100, damping: 20 }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <button onClick={() => navigate('/')} className="focus:outline-none cursor-pointer">
          <Logo size="sm" />
        </button>

        {/* Nav links + user */}
        {user && (
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Home */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                location.pathname === '/'
                  ? 'bg-primary/15 text-primary-light'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-card-hover'
              }`}
            >
              <HiOutlineHome className="text-lg" />
              <span className="hidden sm:inline">Draw</span>
            </motion.button>

            {/* History */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/history')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                location.pathname === '/history'
                  ? 'bg-primary/15 text-primary-light'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-card-hover'
              }`}
            >
              <HiOutlineClock className="text-lg" />
              <span className="hidden sm:inline">History</span>
            </motion.button>

            {/* Separator */}
            <div className="w-px h-6 bg-glass-border hidden sm:block" />

            {/* User info */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center text-white text-sm font-semibold">
                {user.username[0].toUpperCase()}
              </div>
              <span className="text-sm text-text-secondary hidden sm:inline font-medium">
                {user.username}
              </span>
            </div>

            {/* Logout */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={logout}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-accent-red/80 hover:text-accent-red hover:bg-accent-red/10 transition-colors cursor-pointer"
              title="Logout"
            >
              <HiOutlineLogout className="text-lg" />
              <span className="hidden sm:inline">Logout</span>
            </motion.button>
          </div>
        )}
      </div>
    </motion.nav>
  );
}
