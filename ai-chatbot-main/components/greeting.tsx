import { motion } from "framer-motion";

export const Greeting = () => {
  return (
    <div
      className="mx-auto mt-4 flex size-full max-w-3xl flex-col justify-center px-4 md:mt-16 md:px-8"
      key="overview"
    >
      <motion.div
        animate={{ opacity: 1, y: 0 }}
        className="font-semibold text-xl md:text-2xl"
        exit={{ opacity: 0, y: 10 }}
        initial={{ opacity: 0, y: 10 }}
        transition={{ delay: 0.5 }}
      >
        Welcome to DeepResearch Agent!
      </motion.div>
      <motion.div
        animate={{ opacity: 1, y: 0 }}
        className="text-lg text-zinc-500 md:text-xl"
        exit={{ opacity: 0, y: 10 }}
        initial={{ opacity: 0, y: 10 }}
        transition={{ delay: 0.6 }}
      >
        欢迎使用深度研究助手！今天想研究什么主题？
      </motion.div>
      <motion.div
        animate={{ opacity: 1, y: 0 }}
        className="text-base text-zinc-400 md:text-lg mt-1"
        exit={{ opacity: 0, y: 10 }}
        initial={{ opacity: 0, y: 10 }}
        transition={{ delay: 0.7 }}
      >
        What would you like to research today?
      </motion.div>
    </div>
  );
};
