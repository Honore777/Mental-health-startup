"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Loader2, ShieldAlert, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/lib/contexts/AuthContext";
import { useLanguage } from "@/lib/contexts/LanguageContext";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  riskLevel?: string;
  sources?: string[];
};

export function Chat() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const [chatId, setChatId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        language === "en"
          ? "Hello, I am Amahoro. How can I support your mental well-being today?"
          : "Muraho, nitwa Amahoro. Ni gute nagufasha ku buzima bwo mu mutwe uyu munsi?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([
      {
        id: "1",
        role: "assistant",
        content:
          language === "en"
            ? "Hello, I am Amahoro. How can I support your mental well-being today?"
            : "Muraho, nitwa Amahoro. Ni gute nagufasha ku buzima bwo mu mutwe uyu munsi?",
      },
    ]);
    setChatId(crypto.randomUUID());
  }, [language]);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!user) return;
      try {
        const res = await apiFetch("/api/chats");
        const data = await res.json();
        if (data.chats && data.chats.length > 0) {
          const latestChat = data.chats[0];
          setChatId(latestChat.id);
          const msgRes = await apiFetch(`/api/chats/${latestChat.id}/messages`);
          const msgData = await msgRes.json();
          if (msgData.messages && msgData.messages.length > 0) {
            setMessages(
              msgData.messages.map((m: any) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                riskLevel: m.risk_level,
              })),
            );
          }
        }
      } catch {
        // Ignore history load errors to keep UX responsive.
      }
    };
    fetchHistory();
  }, [user]);

  const clearChat = () => {
    setChatId(crypto.randomUUID());
    setMessages([
      {
        id: Date.now().toString(),
        role: "assistant",
        content:
          language === "en"
            ? "Chat cleared. How can I help you now?"
            : "Ibiganiro byasibwe. Ni gute nagufasha ubu?",
      },
    ]);
  };

  const saveMessage = async (msg: Message) => {
    try {
      await apiFetch("/api/messages", {
        method: "POST",
        body: JSON.stringify({
          chatId,
          role: msg.role,
          content: msg.content,
          riskLevel: msg.riskLevel,
          language,
        }),
      });
    } catch {
      // Persistence is best-effort to keep response latency low.
    }
  };

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !user) return;

    const userMessage: Message = { id: Date.now().toString(), role: "user", content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setIsLoading(true);

    void saveMessage(userMessage);

    try {
      const response = await apiFetch("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          messages: updatedMessages,
          language,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || "AI processing failed");
      }

      const result = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: result.final_response,
        riskLevel: result.classification?.risk_level,
        sources: result.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
      void saveMessage(assistantMessage);
    } catch (error: any) {
      toast.error(error.message || (language === "en" ? "I encountered an error. Please try again." : "Habaye ikibazo. Ongera ugerageze."));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto h-[min(78vh,700px)] flex flex-col bg-white/80 backdrop-blur-md border-stone-200 shadow-2xl rounded-3xl overflow-hidden">
      <div className="p-4 border-b border-stone-100 flex justify-between items-center bg-stone-50/70">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
            <Bot className="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <h2 className="font-semibold text-stone-800">Amahoro Assistant</h2>
            <p className="text-xs text-stone-500">{language === "en" ? "Professional Support" : "Inkunga y'umwuga"}</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={clearChat} className="rounded-full hover:bg-red-100/50 hover:text-red-600" title={language === "en" ? "Clear Chat" : "Siba ibiganiro"}>
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>

      <div ref={listRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-white/0 to-white/40">
        <AnimatePresence initial={false}>
          {messages.map((m) => (
            <motion.div key={m.id} initial={{ opacity: 0, y: 10, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[86%] flex gap-3 ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${m.role === "user" ? "bg-stone-200" : "bg-emerald-100"}`}>
                  {m.role === "user" ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5 text-emerald-600" />}
                </div>
                <div className={`p-3 rounded-2xl text-sm leading-relaxed ${m.role === "user" ? "bg-stone-800 text-white rounded-tr-none" : "bg-white text-stone-800 border border-stone-100 rounded-tl-none shadow-sm"}`}>
                  <p className="whitespace-pre-wrap">{m.content}</p>
                  {m.riskLevel && (m.riskLevel === "HIGH" || m.riskLevel === "CRITICAL") && (
                    <div className="mt-2 flex items-center gap-1 text-red-500 font-medium text-xs">
                      <ShieldAlert className="w-3 h-3" />
                      {language === "en" ? "Safety Alert" : "Iburira ry'umutekano"}
                    </div>
                  )}
                  {m.role === "assistant" && m.sources && m.sources.length > 0 && (
                    <div className="mt-3 border-t border-stone-100 pt-2">
                      <p className="text-[11px] font-semibold text-stone-500">{language === "en" ? "Sources" : "Inkomoko"}</p>
                      <ul className="mt-1 space-y-1 text-[11px] text-stone-500 list-disc pl-4">
                        {m.sources.slice(0, 3).map((src, idx) => (
                          <li key={`${m.id}-src-${idx}`}>{src}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white p-3 rounded-2xl border border-stone-100 flex items-center gap-2 shadow-sm">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-600" />
              <span className="text-xs text-stone-500">{language === "en" ? "Amahoro is thinking..." : "Amahoro iri gutekereza..."}</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-stone-50/80 border-t border-stone-100 sticky bottom-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void handleSend();
          }}
          className="flex gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={language === "en" ? "Type your message..." : "Andika ubutumwa bwawe..."}
            className="flex-1 bg-white border-stone-200 rounded-full px-4 focus-visible:ring-emerald-500"
          />
          <Button type="submit" disabled={isLoading || !input.trim()} className="rounded-full w-10 h-10 p-0 bg-emerald-600 hover:bg-emerald-700 text-white shrink-0">
            <Send className="w-5 h-5" />
          </Button>
        </form>
        <p className="text-[10px] text-center mt-2 text-stone-400">
          {language === "en"
            ? "Amahoro is an AI assistant. If you are in crisis, please call emergency services."
            : "Amahoro ni umufasha wa AI. Niba uri mu bihe bikomeye, hamagara ubutabazi bwihuse."}
        </p>
      </div>
    </Card>
  );
}
