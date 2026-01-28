import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Profile from "./pages/Profile";
import AuthForm from "./components/AuthForm";

import { useAuthStore } from "./stores/authStore";
import { useEffect } from "react";

const queryClient = new QueryClient();

const AppRoutes = () => {
  const { authUser, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  // 🔴 Not logged in
  if (!authUser) {
    return <AuthForm />;
  }

  // 🟡 Logged in but profile not completed
  if (authUser && authUser.profileCompleted === false) {
    return <Profile />;
  }

  // 🟢 Logged in + profile completed → MAIN APP
  return (
    <Routes>
      <Route path="/" element={<Index />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
