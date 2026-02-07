"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function Accordion({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="accordion">
      <button
        className="accordion-header"
        onClick={() => setOpen((o) => !o)}
        type="button"
      >
        <span className="accordion-title">{title}</span>
        <motion.span
          className="accordion-chevron"
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
          &#9662;
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            style={{ overflow: "hidden" }}
          >
            <div className="accordion-body">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
