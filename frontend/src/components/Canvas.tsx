import { useRef, useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';

interface CanvasProps {
  onExport: (dataUrl: string) => void;
  isLoading?: boolean;
}

export default function Canvas({ onExport, isLoading = false }: CanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasDrawing, setHasDrawing] = useState(false);
  const lastPos = useRef<{ x: number; y: number } | null>(null);
  const strokeHistory = useRef<ImageData[]>([]);

  // Initialize canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const updateSize = () => {
      const container = canvas.parentElement;
      if (!container) return;
      const size = Math.min(container.clientWidth, 420);
      canvas.width = size;
      canvas.height = size;
      clearCanvas();
    };

    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  const getCtx = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    return ctx;
  }, []);

  const clearCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!canvas || !ctx) return;
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    setHasDrawing(false);
    strokeHistory.current = [];
  }, [getCtx]);

  const getPos = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    if ('touches' in e) {
      const touch = e.touches[0];
      return {
        x: (touch.clientX - rect.left) * scaleX,
        y: (touch.clientY - rect.top) * scaleY,
      };
    }
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  }, []);

  const startDrawing = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    const ctx = getCtx();
    if (!ctx) return;

    // Save state for undo
    const canvas = canvasRef.current;
    if (canvas) {
      strokeHistory.current.push(ctx.getImageData(0, 0, canvas.width, canvas.height));
      if (strokeHistory.current.length > 20) strokeHistory.current.shift();
    }

    const pos = getPos(e);
    lastPos.current = pos;
    setIsDrawing(true);
    setHasDrawing(true);

    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 24;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();
  }, [getCtx, getPos]);

  const draw = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (!isDrawing) return;
    const ctx = getCtx();
    if (!ctx || !lastPos.current) return;

    const pos = getPos(e);

    ctx.beginPath();
    ctx.moveTo(lastPos.current.x, lastPos.current.y);

    // Smooth line with quadratic curve
    const midX = (lastPos.current.x + pos.x) / 2;
    const midY = (lastPos.current.y + pos.y) / 2;
    ctx.quadraticCurveTo(lastPos.current.x, lastPos.current.y, midX, midY);

    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 24;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();

    lastPos.current = pos;
  }, [isDrawing, getCtx, getPos]);

  const stopDrawing = useCallback(() => {
    setIsDrawing(false);
    lastPos.current = null;
  }, []);

  const undo = useCallback(() => {
    const ctx = getCtx();
    const canvas = canvasRef.current;
    if (!ctx || !canvas || strokeHistory.current.length === 0) return;

    const prevState = strokeHistory.current.pop()!;
    ctx.putImageData(prevState, 0, 0);

    if (strokeHistory.current.length === 0) setHasDrawing(false);
  }, [getCtx]);

  const handlePredict = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dataUrl = canvas.toDataURL('image/png');
    onExport(dataUrl);
  }, [onExport]);

  return (
    <div className="flex flex-col items-center gap-4 w-full">
      {/* Canvas area */}
      <motion.div
        className={`canvas-container gradient-border w-full max-w-[420px] aspect-square ${
          isDrawing ? 'canvas-glow-active' : 'canvas-glow'
        }`}
        animate={{
          boxShadow: isDrawing
            ? '0 0 50px rgba(99, 102, 241, 0.35), 0 0 100px rgba(236, 72, 153, 0.2)'
            : '0 0 30px rgba(99, 102, 241, 0.15), 0 0 60px rgba(236, 72, 153, 0.08)',
        }}
        transition={{ duration: 0.3 }}
      >
        <canvas
          ref={canvasRef}
          className="w-full h-full rounded-2xl cursor-crosshair touch-none"
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
          id="drawing-canvas"
        />
      </motion.div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap justify-center">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={clearCanvas}
          className="btn-ghost cursor-pointer"
          id="btn-clear"
        >
          🗑️ Clear
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={undo}
          className="btn-ghost cursor-pointer"
          disabled={strokeHistory.current.length === 0}
          id="btn-undo"
        >
          ↩️ Undo
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handlePredict}
          disabled={!hasDrawing || isLoading}
          className="btn-primary px-6 py-2.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          id="btn-predict"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <motion.span
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full inline-block"
                animate={{ rotate: 360 }}
                transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
              />
              Analyzing...
            </span>
          ) : (
            '✨ Recognize'
          )}
        </motion.button>
      </div>

      {/* Drawing hint */}
      {!hasDrawing && (
        <motion.p
          className="text-text-muted text-sm text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Draw an emoji on the canvas above ✍️
        </motion.p>
      )}
    </div>
  );
}
