"use client";

import { motion } from "framer-motion";

export default function NeonButton({ children, disabled, onClick, type = "button" }) {
  return (
    <motion.button
      className="neon-btn"
      type={type}
      disabled={disabled}
      onClick={onClick}
      whileHover={disabled ? {} : { scale: 1.03 }}
      whileTap={disabled ? {} : { scale: 0.97 }}
    >
      {children}
    </motion.button>
  );
}
