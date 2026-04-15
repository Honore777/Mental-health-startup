"use client";

import { RelaxingBackground } from "@/components/RelaxingBackground";
import { Chat } from "@/components/Chat";
import { Auth } from "@/components/Auth";
import { AuthProvider, useAuth } from "@/lib/contexts/AuthContext";
import { LanguageProvider, useLanguage } from "@/lib/contexts/LanguageContext";
import { Toaster } from "@/components/ui/sonner";
import { motion } from "framer-motion";
import { Heart, ShieldCheck, Brain, Sparkles, LogOut, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";

function AppContent() {
  const { user, logout, isLoading } = useAuth();
  const { language, toggleLanguage } = useLanguage();
  const isRw = language === "rw";

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-stone-50">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="w-16 h-16 bg-emerald-200 rounded-full flex items-center justify-center">
            <Heart className="w-8 h-8 text-emerald-600" />
          </div>
          <p className="text-stone-500 font-medium">{isRw ? "Turimo gutegura urubuga rwawe..." : "Preparing your space..."}</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <>
        <RelaxingBackground />
        <Auth />
        <div className="fixed top-4 right-4 z-50">
          <Button variant="ghost" size="sm" onClick={toggleLanguage} className="gap-2 rounded-full bg-white/70 backdrop-blur border border-stone-200">
            <Globe className="w-4 h-4" />
            {isRw ? "Kinyarwanda" : "English"}
          </Button>
        </div>
        <Toaster />
      </>
    );
  }

  return (
    <div className="min-h-screen font-sans selection:bg-emerald-100 selection:text-emerald-900">
      <RelaxingBackground />
      <Toaster />

      <nav className="fixed top-0 w-full z-50 px-6 py-4 flex justify-between items-center bg-white/10 backdrop-blur-md border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
            <Heart className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-stone-900">Amahoro</span>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={toggleLanguage} className="gap-2 text-stone-700">
            <Globe className="w-4 h-4" />
            {isRw ? "Kinyarwanda" : "English"}
          </Button>
          <span className="text-sm font-medium text-stone-700">{isRw ? `Murakaza neza, ${user.name}` : `Welcome, ${user.name}`}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              void logout();
            }}
            className="gap-2 text-stone-600 hover:text-red-600"
          >
            <LogOut className="w-4 h-4" />
            {isRw ? "Gusohoka" : "Sign Out"}
          </Button>
        </div>
      </nav>

      <main className="pt-24 pb-12 px-4">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="space-y-8">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100/50 text-emerald-700 text-xs font-medium backdrop-blur-sm border border-emerald-200/50">
                <Sparkles className="w-3 h-3" />
                <span>{isRw ? "Ubuzima bwo mu mutwe ku rwego rw'umwuga" : "Professional Mental Wellness"}</span>
              </div>
              <h1 className="text-5xl lg:text-7xl font-bold text-stone-900 leading-[1.1] tracking-tight">
                {isRw ? (
                  <>
                    Bona <span className="text-emerald-600 italic">amahoro yo mu mutima</span> hamwe na Amahoro.
                  </>
                ) : (
                  <>
                    Find your <span className="text-emerald-600 italic">inner peace</span> with Amahoro.
                  </>
                )}
              </h1>
              <p className="text-xl text-stone-600 max-w-lg leading-relaxed">
                {isRw
                  ? "Umufasha wa AI wubahiriza umuco kandi wabigize umwuga, ugufasha mu rugendo rw'ubuzima bwo mu mutwe mu Cyongereza no mu Kinyarwanda."
                  : "A culturally sensitive, professional AI companion supporting your mental health journey in English and Kinyarwanda."}
              </p>
            </div>

            <div className="grid sm:grid-cols-2 gap-6">
              {[
                {
                  icon: ShieldCheck,
                  title: isRw ? "Umutekano n'Ubwirinzi" : "Safe & Private",
                  desc: isRw ? "Amakuru yawe ararinzwe kandi afunzwe" : "Your data is encrypted and secure",
                },
                {
                  icon: Brain,
                  title: isRw ? "Ubumenyi bw'Inzobere" : "Expert Knowledge",
                  desc: isRw ? "Bishingiye ku mabwiriza ya WHO na MINISANTE" : "Based on WHO & MINISANTE guidelines",
                },
                {
                  icon: Sparkles,
                  title: isRw ? "Inkunga mu Ndimi Ebyiri" : "Bilingual Support",
                  desc: isRw ? "Icyongereza n'Ikinyarwanda" : "English and Kinyarwanda support",
                },
                {
                  icon: Heart,
                  title: isRw ? "AI Ikwitaho" : "Empathetic AI",
                  desc: isRw ? "Ibisubizo by'umwuga kandi byuje impuhwe" : "Professional and caring responses",
                },
              ].map((feature, i) => (
                <div key={i} className="flex gap-4 p-4 rounded-2xl bg-white/40 backdrop-blur-sm border border-white/20">
                  <div className="w-10 h-10 shrink-0 rounded-xl bg-emerald-100 flex items-center justify-center">
                    <feature.icon className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-stone-900">{feature.title}</h3>
                    <p className="text-sm text-stone-500">{feature.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>
            <Chat />
          </motion.div>
        </div>
      </main>

      <footer className="border-t border-stone-200 bg-white/50 backdrop-blur-sm py-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2">
            <Heart className="w-5 h-5 text-emerald-600" />
            <span className="font-bold text-stone-900">Amahoro Wellness</span>
          </div>
          <p className="text-stone-500 text-sm">{isRw ? "© 2026 Amahoro Mental Wellness. Inkunga ya AI ku rwego rw'umwuga." : "© 2026 Amahoro Mental Wellness. Professional AI Support."}</p>
          <div className="flex gap-6 text-sm font-medium text-stone-600">
            <a href="#" className="hover:text-emerald-600 transition-colors">
              {isRw ? "Politiki y'Ibanga" : "Privacy Policy"}
            </a>
            <a href="#" className="hover:text-emerald-600 transition-colors">
              {isRw ? "Amategeko y'Uko Ukoresha" : "Terms of Service"}
            </a>
            <a href="#" className="hover:text-emerald-600 transition-colors">
              {isRw ? "Aho Washaka Ubutabazi Bwihuse" : "Emergency Resources"}
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export function AppShell() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </LanguageProvider>
  );
}
