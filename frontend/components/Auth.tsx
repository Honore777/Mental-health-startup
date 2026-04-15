"use client";

import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { useAuth } from "@/lib/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Loader2, Mail, Lock, User, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/lib/contexts/LanguageContext";

export function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<"user" | "professional">("user");
  const [specialization, setSpecialization] = useState("");
  const [bio, setBio] = useState("");
  const [price, setPrice] = useState("");
  const [availability, setAvailability] = useState("");
  const { login } = useAuth();
  const { language } = useLanguage();
  const isRw = language === "rw";

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    const endpoint = isLogin ? "/api/auth/login" : "/api/auth/register";
    const body = isLogin
      ? { email, password }
      : {
          email,
          password,
          name,
          role,
          professionalDetails:
            role === "professional"
              ? {
                  specialization,
                  bio,
                  price: parseFloat(price),
                  availability,
                }
              : undefined,
        };

    try {
      const res = await apiFetch(endpoint, {
        method: "POST",
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (res.ok) {
        login(data.user);
        toast.success(isLogin ? (isRw ? "Murakaza neza" : "Welcome back!") : isRw ? "Konti yawe yafunguwe neza" : "Account created successfully!");
      } else {
        toast.error(data.error || (isRw ? "Kwinjira byanze" : "Authentication failed"));
      }
    } catch {
      toast.error(isRw ? "Habaye ikibazo. Ongera ugerageze." : "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <Card className="p-8 bg-white/80 backdrop-blur-xl border-stone-200 shadow-2xl rounded-3xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-stone-900 mb-2">{isLogin ? (isRw ? "Murakaza neza" : "Welcome Back") : isRw ? "Fungura Konti" : "Create Account"}</h1>
            <p className="text-stone-500">
              {isLogin
                ? isRw
                  ? "Komeza urugendo rwawe rwo kwita ku buzima bwo mu mutwe"
                  : "Continue your journey to mental wellness"
                : isRw
                  ? "Tangira kubona inkunga y'umwuga ku buzima bwo mu mutwe"
                  : "Start your professional mental health support today"}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-5 h-5 text-stone-400" />
                  <Input
                    placeholder={isRw ? "Amazina yawe" : "Full Name"}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="pl-10 rounded-xl bg-stone-50 border-stone-200"
                    required
                  />
                </div>
                <div className="flex gap-4 p-1 bg-stone-100 rounded-xl">
                  <button
                    type="button"
                    onClick={() => setRole("user")}
                    className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
                      role === "user" ? "bg-white shadow-sm text-emerald-600" : "text-stone-500"
                    }`}
                  >
                    {isRw ? "Umukoresha" : "User"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole("professional")}
                    className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
                      role === "professional" ? "bg-white shadow-sm text-emerald-600" : "text-stone-500"
                    }`}
                  >
                    {isRw ? "Inzobere" : "Professional"}
                  </button>
                </div>

                {role === "professional" && (
                  <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="space-y-4">
                    <Input
                      placeholder={isRw ? "Icyiciro cy'ubumenyi" : "Specialization (e.g. Clinical Psychologist)"}
                      value={specialization}
                      onChange={(e) => setSpecialization(e.target.value)}
                      className="rounded-xl bg-stone-50 border-stone-200"
                      required
                    />
                    <Input
                      type="number"
                      placeholder={isRw ? "Igiciro kuri buri nama (RWF)" : "Price per session (RWF)"}
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                      className="rounded-xl bg-stone-50 border-stone-200"
                      required
                    />
                    <Input
                      placeholder={isRw ? "Iminsi n'amasaha uboneka" : "Availability (e.g. Mon-Fri, 9am-5pm)"}
                      value={availability}
                      onChange={(e) => setAvailability(e.target.value)}
                      className="rounded-xl bg-stone-50 border-stone-200"
                      required
                    />
                    <textarea
                      placeholder={isRw ? "Incamake y'ibikwerekeyeho" : "Brief Bio"}
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      className="w-full p-3 rounded-xl bg-stone-50 border border-stone-200 text-sm"
                      rows={3}
                      required
                    />
                  </motion.div>
                )}
              </>
            )}
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-stone-400" />
              <Input
                type="email"
                placeholder={isRw ? "Imeli" : "Email Address"}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10 rounded-xl bg-stone-50 border-stone-200"
                required
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-stone-400" />
              <Input
                type="password"
                placeholder={isRw ? "Ijambobanga" : "Password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10 rounded-xl bg-stone-50 border-stone-200"
                required
              />
            </div>

            <Button type="submit" disabled={isLoading} className="w-full py-6 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-lg transition-all">
              {isLoading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <span className="flex items-center gap-2">
                  {isRw ? (isLogin ? "Injira" : "Iyandikishe") : isLogin ? "Sign In" : "Sign Up"}
                  <ArrowRight className="w-5 h-5" />
                </span>
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <button onClick={() => setIsLogin(!isLogin)} className="text-emerald-600 hover:underline text-sm font-medium">
              {isRw
                ? isLogin
                  ? "Nta konti ufite? Iyandikishe"
                  : "Usanzwe ufite konti? Injira"
                : isLogin
                  ? "Don't have an account? Sign up"
                  : "Already have an account? Sign in"}
            </button>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
