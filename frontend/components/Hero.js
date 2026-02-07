"use client";

import { motion } from "framer-motion";

const stagger = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] },
  },
};

export default function Hero() {
  return (
    <motion.div variants={stagger} initial="hidden" animate="visible">
      <motion.div className="kicker" variants={fadeUp}>
        Idea to launch plan
      </motion.div>
      <motion.h1 className="title" variants={fadeUp}>
        Turn a rough idea into a build-ready package.
      </motion.h1>
      <motion.p className="lede" variants={fadeUp}>
        Drop in a product idea and get an implementation roadmap, optimized
        stack, heavy code-generation prompts, and tailored docs — all in one
        pass.
      </motion.p>
    </motion.div>
  );
}
