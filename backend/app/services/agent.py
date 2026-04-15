import re

from app.schemas.chat import ChatResponse, Classification, IncomingMessage
from app.services.knowledge import KNOWLEDGE_BASE
from app.services.llm import get_llm_orchestrator
from app.services.research import get_research_service


class AgentService:
    def __init__(self):
        self.llm = get_llm_orchestrator()
        self.research = get_research_service()

    INTENT_KEYWORDS: dict[str, set[str]] = {
        "crisis_support": {
            "suicide",
            "kill myself",
            "end my life",
            "want to die",
            "self harm",
            "overdose",
            "hurt myself",
        },
        "anxiety_support": {"anxiety", "panic", "worried", "fear", "overthinking", "nervous"},
        "depression_support": {"depressed", "sad", "hopeless", "empty", "no motivation", "worthless"},
        "sleep_support": {"sleep", "insomnia", "cant sleep", "can't sleep", "nightmare", "rest"},
        "trauma_support": {"trauma", "ptsd", "flashback", "abuse", "violence", "assault"},
        "substance_support": {"alcohol", "drugs", "substance", "addiction", "drinking", "dependence"},
        "professional_referral": {"therapist", "psychologist", "psychiatrist", "counselor", "appointment", "referral"},
        "informational": {"what is", "explain", "difference", "causes", "symptoms", "treatment", "guide"},
        "emotional_support": {"stressed", "stress", "lonely", "overwhelmed", "burnout", "tired"},
    }

    INTENT_TAG_HINTS: dict[str, set[str]] = {
        "anxiety_support": {"anxiety", "stress", "grounding", "sleep"},
        "depression_support": {"depression", "psychosocial", "self care", "routine"},
        "sleep_support": {"sleep", "insomnia", "stress"},
        "trauma_support": {"trauma", "ptsd", "referral", "support"},
        "substance_support": {"alcohol", "substance", "motivational interviewing"},
        "professional_referral": {"referral", "policy", "care quality"},
        "informational": {"definition", "policy", "guide"},
        "emotional_support": {"support", "self care", "stress", "routine"},
    }

    def classify(self, message: str) -> Classification:
        lowered = message.lower().strip()
        severe_distress_terms = {"severe anxiety", "cannot cope", "cant cope", "losing control", "extreme panic"}

        if any(term in lowered for term in self.INTENT_KEYWORDS["crisis_support"]):
            return Classification(
                intent="crisis_support",
                risk_level="CRITICAL",
                sentiment="DISTRESSED",
                needs_research=False,
                explanation="Message contains explicit self-harm ideation.",
            )

        intent_scores: dict[str, int] = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if intent == "crisis_support":
                continue
            intent_scores[intent] = sum(1 for keyword in keywords if keyword in lowered)

        dominant_intent = max(intent_scores, key=intent_scores.get) if intent_scores else "general_support"
        dominant_score = intent_scores.get(dominant_intent, 0)
        likely_distressed = dominant_intent in {"anxiety_support", "depression_support", "emotional_support"}

        if dominant_score == 0:
            return Classification(
                intent="general_support",
                risk_level="MEDIUM",
                sentiment="NEUTRAL",
                needs_research=False,
                explanation="No strong intent cues found, using general support response.",
            )

        if likely_distressed and dominant_score >= 1:
            risk = "HIGH" if any(term in lowered for term in severe_distress_terms) else "MEDIUM"
            return Classification(
                intent="emotional_support",
                risk_level=risk,
                sentiment="DISTRESSED",
                needs_research=True,
                explanation=f"Intent signals show distress (dominant={dominant_intent}, score={dominant_score}).",
            )

        needs_research = dominant_intent in {"informational", "professional_referral", "trauma_support", "substance_support"}
        return Classification(
            intent=dominant_intent,
            risk_level="LOW",
            sentiment="NEUTRAL",
            needs_research=needs_research,
            explanation=f"Intent identified as {dominant_intent} (score={dominant_score}).",
        )

    def _tokenize(self, text: str) -> set[str]:
        return {token for token in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(token) > 2}

    def retrieve_context(self, message: str, limit: int = 4) -> tuple[list[str], list[str], list[dict], float, float]:
        query_tokens = self._tokenize(message)
        scored: list[tuple[float, dict]] = []

        for item in KNOWLEDGE_BASE:
            content_tokens = self._tokenize(item["content"])
            tag_tokens = self._tokenize(" ".join(item["tags"]))

            if not query_tokens:
                continue

            content_overlap = len(query_tokens.intersection(content_tokens)) / max(1, len(query_tokens))
            tag_overlap = len(query_tokens.intersection(tag_tokens)) / max(1, len(query_tokens))
            score = (content_overlap * 0.55) + (tag_overlap * 0.45)

            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        top = scored[:limit]

        if not top:
            return [], [], [], 0.0, 0.0

        context = [f"[{idx + 1}] {doc['content']}" for idx, (_, doc) in enumerate(top)]
        sources = [doc["source"] for _, doc in top]
        docs = [doc for _, doc in top]
        avg_score = sum(score for score, _ in top) / len(top)
        top_score = top[0][0]
        return context, sources, docs, avg_score, top_score

    def _context_matches_intent(self, intent: str, docs: list[dict], message: str) -> bool:
        if not docs:
            return False

        message_tokens = self._tokenize(message)
        expected_tags = self._tokenize(" ".join(self.INTENT_TAG_HINTS.get(intent, set())))

        for doc in docs:
            doc_tag_tokens = self._tokenize(" ".join(doc.get("tags", [])))
            doc_content_tokens = self._tokenize(doc.get("content", ""))

            if expected_tags and expected_tags.intersection(doc_tag_tokens):
                return True

            if len(message_tokens.intersection(doc_content_tokens)) >= 2:
                return True

        return False

    async def process_chat(
        self,
        messages: list[IncomingMessage],
        language: str,
        professionals: list[dict],
    ) -> ChatResponse:
        latest = messages[-1].content if messages else ""
        classification = self.classify(latest)

        if classification.risk_level in {"HIGH", "CRITICAL"}:
            response = (
                "I am concerned about your safety. Please contact emergency support now. "
                "In Rwanda, you can call 114 for immediate help. You are not alone."
                if language == "en"
                else "Ndahangayitse ku mutekano wawe. Hamagara ubufasha bwihuse nonaha. "
                "Mu Rwanda wahamagara 114. Ntabwo uri wenyine."
            )
            return ChatResponse(classification=classification, final_response=response, sources=[])

        context, sources, context_docs, avg_score, top_score = self.retrieve_context(latest)
        context_matches_intent = self._context_matches_intent(classification.intent, context_docs, latest)
        context_is_reliable = context_matches_intent and (top_score >= 0.18) and (avg_score >= 0.10)

        use_research = classification.needs_research and not context_is_reliable
        research_context: list[str] = []
        research_sources: list[str] = []

        if use_research:
            research_results = await self.research.search(f"WHO or evidence-based mental health guidance: {latest}")
            for idx, row in enumerate(research_results[:3]):
                content = row.get("content", "").strip()
                if not content:
                    continue
                research_context.append(f"[R{idx + 1}] {content}")
                source = row.get("source", "External source")
                url = row.get("url", "")
                research_sources.append(f"{source}{f' ({url})' if url else ''}")

        if not context_is_reliable:
            context = []
            sources = []

        final_context = context + research_context
        final_sources = sources + research_sources
        response_mode = "grounded" if final_context else "reasoning"
        history = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
        professionals_text = "\n".join(
            [
                f"- {p['name']} ({p['specialization']}) | Price: {p['price_per_session']} RWF | {p['availability']}"
                for p in professionals[:3]
            ]
        )

        prompt = f"""
You are Amahoro, a professional mental wellness assistant.
Language: {language}

Conversation:
{history}

Grounded context (WHO/Rwanda + research when needed):
{' '.join(final_context)}

Mode: {response_mode}

Registered professionals:
{professionals_text if professionals_text else 'No professionals currently listed.'}

Instructions:
- Be supportive, evidence-informed, and culturally respectful.
- First identify the user's real intent from their words before answering.
- Use grounded context only if it is clearly relevant to the intent and question.
- If grounded context is missing or not relevant, reason carefully from general mental health best practices.
- Never force unrelated context into the answer.
- If therapy support seems beneficial, mention 1-2 suitable professionals from the list.
- Keep harmful instructions out and include safety escalation for crisis signs.
- If mode is reasoning, do not cite the knowledge base as a source.
"""

        final_response = await self.llm.generate(prompt)

        return ChatResponse(
            classification=classification,
            final_response=final_response,
            sources=final_sources,
        )


def get_agent_service() -> AgentService:
    return AgentService()
