import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Loader2, Brain } from "lucide-react";
import { useAuthStore } from '../stores/authStore';
import RegistrationForm from './RegistrationForm';

export default function AuthForm() {
  const { login, register, isLoading } = useAuthStore();
  const [showRegistrationForm, setShowRegistrationForm] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ name: '', email: '', password: '' });

  const handleLogin = async (e) => {
    e.preventDefault();
    const result = await login(loginForm);
    if (result.success) {
      // Auth store will handle the redirect
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const result = await register(registerForm);
    if (result.success) {
      // Auth store will handle the redirect
    }
  };

  const handleRegistrationComplete = (data) => {
    // After registration form is complete, trigger the standard registration flow
    setRegisterForm({
      name: `${data.firstName} ${data.lastName}`,
      email: data.email,
      password: data.password
    });
    // Redirect to login or auto-login
    setShowRegistrationForm(false);
  };

  // Show the detailed registration form when user clicks register
  if (showRegistrationForm) {
    return (
      <div className="relative">
        <button
          onClick={() => setShowRegistrationForm(false)}
          className="absolute top-4 left-4 text-muted-foreground hover:text-foreground z-10"
        >
          ← Back
        </button>
        <RegistrationForm onComplete={handleRegistrationComplete} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-card border-border">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Brain className="w-8 h-8 text-primary" />
            <span className="text-2xl font-bold text-foreground">Chithhi LM</span>
          </div>
          <CardTitle className="text-foreground">Welcome</CardTitle>
          <CardDescription className="text-muted-foreground">
            Sign in to your account or create a new one
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-muted">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="register">Register</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="login-email">Email</Label>
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="your@email.com"
                    value={loginForm.email}
                    onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                    required
                    className="bg-input border-border"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="login-password">Password</Label>
                  <Input
                    id="login-password"
                    type="password"
                    placeholder="••••••••"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                    required
                    className="bg-input border-border"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-primary hover:bg-primary/80"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="register">
              <form onSubmit={(e) => {
                e.preventDefault();
                setShowRegistrationForm(true);
              }} className="space-y-4">
                <div className="text-center py-4">
                  <p className="text-muted-foreground mb-4">Click the button below to start the detailed registration process</p>
                </div>
                <Button
                  type="submit"
                  className="w-full bg-primary hover:bg-primary/80"
                >
                  Start Registration
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}