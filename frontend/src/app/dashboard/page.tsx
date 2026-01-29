'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Plus, LogOut, ListOrdered } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/providers/AuthProvider';
import { Task, Priority, Tag, CreateTaskRequest, UpdateTaskRequest } from '@/types';
import { TaskFormModal } from '@/app/components/TaskForm/TaskFormModal';
import { DeleteConfirmationModal } from '@/app/components/common/DeleteConfirmationModal';
import { ViewAllTasksModal } from '@/app/components/common/ViewAllTasksModal';
import { TaskTable } from '@/app/components/TaskTable';
import { Button } from '@/app/components/ui/Button';
import { Logo } from '@/app/components/Auth/Logo';
import { taskApi, priorityApi, tagApi } from '@/utils/api';
import { fadeInUp, staggerContainer } from '@/lib/animations';
import { ChatKit } from '@/app/components/Chat/ChatKit';
import { useTaskSSE } from '@/services/sseService';

const DashboardPage: React.FC = () => {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();

  // Data state (only for modals)
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);

  // Modal state
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deletingTask, setDeletingTask] = useState<Task | null>(null);
  const [showViewAllModal, setShowViewAllModal] = useState(false);

  // Refresh trigger for TaskTable
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Real-time SSE connection for task updates
  useTaskSSE({
    onTaskCreated: (task) => {
      console.log('Task created via SSE:', task);
      setRefreshTrigger((prev) => prev + 1); // Refresh task list immediately
    },
    onTaskUpdated: (task) => {
      console.log('Task updated via SSE:', task);
      setRefreshTrigger((prev) => prev + 1); // Refresh task list
    },
    onTaskDeleted: (task) => {
      console.log('Task deleted via SSE:', task);
      setRefreshTrigger((prev) => prev + 1); // Refresh task list
    },
    onConnected: () => {
      console.log('SSE connected');
    },
    onDisconnected: () => {
      console.log('SSE disconnected');
    }
  });

  // Fetch priorities and tags for modals
  const fetchMetadata = useCallback(async () => {
    try {
      const [prioritiesRes, tagsRes] = await Promise.all([
        priorityApi.getPriorities(),
        tagApi.getTags(),
      ]);

      setPriorities(prioritiesRes.data || []);
      setTags(tagsRes.data || []);
    } catch (error) {
      console.error('Failed to load priorities and tags:', error);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetchMetadata();
    }
  }, [isAuthenticated, fetchMetadata]);

  // Task modal handlers
  const confirmDelete = async () => {
    if (!deletingTask) return;
    try {
      await taskApi.deleteTask(deletingTask.id);
      setDeletingTask(null);
      setRefreshTrigger((prev) => prev + 1); // Refresh task list
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const handleFormSubmit = async (taskData: CreateTaskRequest | UpdateTaskRequest) => {
    try {
      if (editingTask) {
        await taskApi.updateTask(editingTask.id, taskData);
      } else {
        await taskApi.createTask(taskData as CreateTaskRequest);
      }
      setEditingTask(null);
      setShowTaskModal(false);
      setRefreshTrigger((prev) => prev + 1); // Refresh task list immediately
    } catch (error) {
      console.error('Failed to save task:', error);
      throw error; // Let modal handle the error
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Auth loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <Logo size="lg" animated />
          <p className="mt-4 text-text-secondary">Loading...</p>
        </motion.div>
      </div>
    );
  }

  // Redirect if not authenticated (this is now handled by the effect above)
  // But we still need to return null if not authenticated after loading
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Background gradient */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-gradient-radial from-accent-orange/5 to-transparent" />
        <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-gradient-radial from-accent-yellow/5 to-transparent" />
      </div>

      {/* Content */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-8"
        >
          {/* Header */}
          <motion.header
            variants={fadeInUp}
            className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
          >
            <div className="flex items-center gap-4">
              <Logo size="md" />
              <div className="hidden sm:block h-8 w-px bg-border" />
              <div className="hidden sm:block">
                <p className="text-sm text-text-muted">Welcome back,</p>
                <p className="font-medium text-text-primary">
                  {user?.first_name || user?.email?.split('@')[0]}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="secondary"
                leftIcon={<ListOrdered className="w-4 h-4" />}
                onClick={() => setShowViewAllModal(true)}
                className="hidden sm:flex"
              >
                View All
              </Button>
              <Button
                variant="primary"
                leftIcon={<Plus className="w-4 h-4" />}
                onClick={() => {
                  setEditingTask(null);
                  setShowTaskModal(true);
                }}
              >
                Add Task
              </Button>
              <Button
                variant="ghost"
                leftIcon={<LogOut className="w-4 h-4" />}
                onClick={handleLogout}
              >
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          </motion.header>

          {/* Main Content Grid */}
          <motion.div variants={fadeInUp} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Tasks Section - Takes 2 columns on large screens */}
            <div className="lg:col-span-2">
              <TaskTable
                onAddTask={() => {
                  setEditingTask(null);
                  setShowTaskModal(true);
                }}
                onEditTask={(task) => {
                  setEditingTask(task);
                  setShowTaskModal(true);
                }}
                onDeleteTask={(task) => {
                  setDeletingTask(task);
                }}
                onTaskUpdated={() => {
                  // TaskTable handles its own refresh after completion toggle
                }}
                refreshTrigger={refreshTrigger}
              />
            </div>

            {/* AI Chat Section - Takes 1 column on large screens */}
            <div className="lg:col-span-1">
              <div className="sticky top-8 h-[600px]">
                <ChatKit />
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Task Form Modal */}
      <TaskFormModal
        isOpen={showTaskModal}
        onClose={() => {
          setShowTaskModal(false);
          setEditingTask(null);
        }}
        onSubmit={handleFormSubmit}
        task={editingTask}
        priorities={priorities}
        tags={tags}
      />

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={!!deletingTask}
        onClose={() => setDeletingTask(null)}
        onConfirm={confirmDelete}
        title="Delete Task"
        message="Are you sure you want to delete this task? This action cannot be undone."
        itemName={deletingTask?.title}
      />

      {/* View All Tasks Modal */}
      <ViewAllTasksModal
        isOpen={showViewAllModal}
        onClose={() => setShowViewAllModal(false)}
      />
    </div>
  );
};

export default DashboardPage;
