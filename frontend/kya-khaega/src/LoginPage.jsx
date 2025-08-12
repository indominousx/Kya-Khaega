import React from "react";
import { motion } from "framer-motion";
import pizza from "./assets/pizza.png";
import burger from "./assets/burger.png";
import ramen from "./assets/ramen.png";
import boba from "./assets/boba.png";

export default function LoginPage() {
  const floatingVariants = {
    animate: {
      y: [0, -20, 0],
      transition: {
        duration: 4,
        repeat: Infinity,
        ease: "easeInOut",
      },
    },
  };

  return (
    <div className="relative h-screen flex items-center justify-center bg-gradient-to-br from-pink-400 via-purple-500 to-indigo-500 overflow-hidden">
      {/* Floating food icons */}
      <motion.img
        src={pizza}
        alt="pizza"
        className="w-20 absolute top-10 left-10 opacity-80"
        variants={floatingVariants}
        animate="animate"
      />
      <motion.img
        src={burger}
        alt="burger"
        className="w-16 absolute top-32 right-16 opacity-80"
        variants={floatingVariants}
        animate="animate"
      />
      <motion.img
        src={ramen}
        alt="ramen"
        className="w-20 absolute bottom-20 left-16 opacity-80"
        variants={floatingVariants}
        animate="animate"
      />
      <motion.img
        src={boba}
        alt="boba"
        className="w-16 absolute bottom-10 right-10 opacity-80"
        variants={floatingVariants}
        animate="animate"
      />

      {/* Glassmorphic form */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="bg-white/10 backdrop-blur-lg p-8 rounded-3xl shadow-xl max-w-sm w-full text-white border border-white/20"
      >
        <h1 className="text-4xl font-extrabold mb-6 text-center tracking-wide">
          🍽️ Kya Khaega
        </h1>
        <form className="flex flex-col gap-4">
          <input
            type="email"
            placeholder="Email"
            className="p-3 rounded-lg bg-white/20 border border-white/30 placeholder-gray-200 focus:outline-none focus:ring-2 focus:ring-yellow-300"
          />
          <input
            type="password"
            placeholder="Password"
            className="p-3 rounded-lg bg-white/20 border border-white/30 placeholder-gray-200 focus:outline-none focus:ring-2 focus:ring-yellow-300"
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            className="bg-yellow-400 text-black p-3 rounded-lg font-bold hover:bg-yellow-500 transition"
          >
            Login
          </motion.button>
        </form>
        <p className="mt-4 text-sm text-center text-gray-200">
          Don’t have an account?{" "}
          <a href="#" className="text-yellow-300 hover:underline">
            Sign up
          </a>
        </p>
      </motion.div>
    </div>
  );
}
