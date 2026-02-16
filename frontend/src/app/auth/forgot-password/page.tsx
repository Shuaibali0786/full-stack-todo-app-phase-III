'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, ArrowLeft, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/app/components/ui/Button';
import { Input } from '@/app/components/ui/Input';
import { Logo } from '@/app/components/Auth/Logo';
import { fadeInUp, staggerContainer } from '@/lib/animations';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, new_password: newPassword }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Failed to reset password. Please try again.');
        return;
      }

      setSuccess(true);
    } catch {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <motion.div
        variants={staggerContainer}
        initial="initial"
        animate="animate"
        className="w-full max-w-md"
      >
        {/* Logo */}
        <motion.div variants={fadeInUp} className="mb-8 text-center">
          <Logo size="lg" />
        </motion.div>

        {/* Card */}
        <motion.div variants={fadeInUp} className="auth-card">
          {!success ? (
            <>
              <motion.h1
                variants={fadeInUp}
                className="text-2xl font-bold text-text-primary text-center mb-2"
              >
                Reset Password
              </motion.h1>

              <motion.p
                variants={fadeInUp}
                className="text-text-secondary text-center mb-6"
              >
                Enter your email and choose a new password.
              </motion.p>

              {/* Error */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-4 p-3 rounded-lg bg-status-error/10 border border-status-error/20 text-status-error text-sm"
                >
                  {error}
                </motion.div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <motion.div variants={fadeInUp}>
                  <Input
                    id="email"
                    label="Email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={setEmail}
                    leftIcon={<Mail className="w-4 h-4" />}
                    required
                    disabled={loading}
                  />
                </motion.div>

                <motion.div variants={fadeInUp}>
                  <Input
                    id="new-password"
                    label="New Password"
                    type="password"
                    placeholder="At least 6 characters"
                    value={newPassword}
                    onChange={setNewPassword}
                    leftIcon={<Lock className="w-4 h-4" />}
                    required
                    disabled={loading}
                  />
                </motion.div>

                <motion.div variants={fadeInUp}>
                  <Input
                    id="confirm-password"
                    label="Confirm New Password"
                    type="password"
                    placeholder="Repeat your new password"
                    value={confirmPassword}
                    onChange={setConfirmPassword}
                    leftIcon={<Lock className="w-4 h-4" />}
                    required
                    disabled={loading}
                  />
                </motion.div>

                <motion.div variants={fadeInUp}>
                  <Button
                    type="submit"
                    variant="primary"
                    fullWidth
                    loading={loading}
                  >
                    Reset Password
                  </Button>
                </motion.div>
              </form>
            </>
          ) : (
            <>
              <motion.div
                variants={fadeInUp}
                className="flex flex-col items-center gap-4 mb-6"
              >
                <CheckCircle className="w-16 h-16 text-green-500" />
                <h1 className="text-2xl font-bold text-text-primary text-center">
                  Password Updated!
                </h1>
                <p className="text-text-secondary text-center">
                  Password updated successfully. You can now log in with your new password.
                </p>
              </motion.div>

              <motion.div variants={fadeInUp}>
                <Button
                  variant="primary"
                  fullWidth
                  onClick={() => router.push('/auth/login')}
                >
                  Go to Login
                </Button>
              </motion.div>
            </>
          )}
        </motion.div>

        <motion.p variants={fadeInUp} className="mt-6 text-center text-sm text-text-secondary">
          <Link
            href="/auth/login"
            className="flex items-center justify-center gap-2 text-accent-orange hover:text-accent-yellow transition-colors font-medium"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Login
          </Link>
        </motion.p>
      </motion.div>
    </div>
  );
};

export default ForgotPasswordPage;
