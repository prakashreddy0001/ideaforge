"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import MetaBar from "./MetaBar";
import RefinedIdeaCard from "./RefinedIdeaCard";
import ImplementationPlan from "./ImplementationPlan";
import TechStackCard from "./TechStackCard";
import MasterPromptCard from "./MasterPromptCard";
import PromptPackCard from "./PromptPackCard";
import DocsCard from "./DocsCard";

const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.05 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] },
  },
};

export default function ResultsSection({ result }) {
  const { masterPrompt, otherPrompts } = useMemo(() => {
    if (!result.prompts) return { masterPrompt: null, otherPrompts: {} };
    const { master_prompt, ...rest } = result.prompts;
    return { masterPrompt: master_prompt || null, otherPrompts: rest };
  }, [result.prompts]);

  return (
    <motion.section
      className="results-section"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item}>
        <MetaBar result={result} />
      </motion.div>

      {result.refined_idea && (
        <motion.div variants={item}>
          <RefinedIdeaCard refinedIdea={result.refined_idea} />
        </motion.div>
      )}

      <motion.div variants={item}>
        <ImplementationPlan steps={result.implementation_plan} />
      </motion.div>

      <motion.div variants={item}>
        <TechStackCard stack={result.tech_stack} />
      </motion.div>

      {masterPrompt && (
        <motion.div variants={item}>
          <MasterPromptCard prompt={masterPrompt} />
        </motion.div>
      )}

      <motion.div variants={item}>
        <PromptPackCard prompts={otherPrompts} />
      </motion.div>

      {result.docs && Object.keys(result.docs).length > 0 && (
        <motion.div variants={item}>
          <DocsCard docs={result.docs} />
        </motion.div>
      )}
    </motion.section>
  );
}
