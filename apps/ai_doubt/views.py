# """
# apps/ai_doubt/views.py
# AI Doubt Solver — calls Anthropic Claude API.
# """
# import json
# import anthropic

# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.conf import settings

# from .models import DoubtSession, DoubtMessage


# @login_required
# def doubt_solver_view(request):
#     sessions = DoubtSession.objects.filter(student=request.user)[:10]
#     return render(request, "ai_doubt/chat.html", {"sessions": sessions})


# @login_required
# @require_POST
# def ask_doubt(request):
#     """Process a student question and return AI answer."""
#     data = json.loads(request.body)
#     question = data.get("question", "").strip()
#     session_id = data.get("session_id")

#     if not question:
#         return JsonResponse({"error": "Question cannot be empty."}, status=400)

#     # Get or create session
#     if session_id:
#         try:
#             session = DoubtSession.objects.get(id=session_id, student=request.user)
#         except DoubtSession.DoesNotExist:
#             session = DoubtSession.objects.create(student=request.user, title=question[:80])
#     else:
#         session = DoubtSession.objects.create(student=request.user, title=question[:80])

#     # Save student message
#     DoubtMessage.objects.create(session=session, role="user", content=question)

#     # Build message history for Claude
#     history = list(
#         session.messages.order_by("created_at").values("role", "content")
#     )

#     # Call Anthropic API
#     if not settings.ANTHROPIC_API_KEY:
#         answer = (
#             "🤖 AI Doubt Solver is not configured yet. "
#             "Please add your ANTHROPIC_API_KEY to the .env file to enable this feature."
#         )
#     else:
#         try:
#             client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
#             response = client.messages.create(
#                 model="claude-sonnet-4-6",
#                 max_tokens=1024,
#                 system=(
#                     "You are EduPeak's AI tutor — an expert in competitive exam subjects "
#                     "(Mathematics, Physics, Chemistry, Biology, and more). "
#                     "Give clear, step-by-step, helpful answers. "
#                     "Use LaTeX notation for equations when helpful. "
#                     "Be encouraging and supportive."
#                 ),
#                 messages=[{"role": m["role"], "content": m["content"]} for m in history],
#             )
#             answer = response.content[0].text
#         except Exception as exc:
#             answer = f"Sorry, I couldn't process your question right now. Please try again. (Error: {exc})"

#     # Save AI response
#     DoubtMessage.objects.create(session=session, role="assistant", content=answer)

#     return JsonResponse(
#         {"answer": answer, "session_id": str(session.id)}
#     )


# @login_required
# def doubt_session_view(request, session_id):
#     session = get_object_or_404(DoubtSession, id=session_id, student=request.user)
#     messages_qs = session.messages.order_by("created_at")
#     all_sessions = DoubtSession.objects.filter(student=request.user)[:10]
#     return render(
#         request,
#         "ai_doubt/chat.html",
#         {"session": session, "messages": messages_qs, "sessions": all_sessions},
#     )


"""
apps/ai_doubt/views.py
AI Doubt Solver — calls Google Gemini API.
"""
import json
import google.generativeai as genai

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import DoubtSession, DoubtMessage


@login_required
def doubt_solver_view(request):
    sessions = DoubtSession.objects.filter(student=request.user)[:10]
    return render(request, "ai_doubt/chat.html", {"sessions": sessions})


@login_required
@require_POST
def ask_doubt(request):
    """Process a student question and return AI answer using Gemini."""
    data = json.loads(request.body)
    question = data.get("question", "").strip()
    session_id = data.get("session_id")

    if not question:
        return JsonResponse({"error": "Question cannot be empty."}, status=400)

    # Get or create session
    if session_id:
        try:
            session = DoubtSession.objects.get(id=session_id, student=request.user)
        except DoubtSession.DoesNotExist:
            session = DoubtSession.objects.create(student=request.user, title=question[:80])
    else:
        session = DoubtSession.objects.create(student=request.user, title=question[:80])

    # Save student message
    DoubtMessage.objects.create(session=session, role="user", content=question)

    # Build message history for Gemini
    # NOTE: Anthropic uses 'user'/'assistant', Gemini expects 'user'/'model'
    raw_history = session.messages.order_by("created_at").values("role", "content")
    
    gemini_history = []
    for m in raw_history:
        gemini_role = "model" if m["role"] == "assistant" else "user"
        gemini_history.append({
            "role": gemini_role,
            "parts": [m["content"]]
        })

    # Call Gemini API
    if not getattr(settings, 'GEMINI_API_KEY', None):
        answer = (
            "🤖 AI Doubt Solver is not configured yet. "
            "Please add your GEMINI_API_KEY to the .env file to enable this feature."
        )
    else:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            system_instruction = (
                "You are EduPeak's AI tutor — an expert in competitive exam subjects "
                "(Mathematics, Physics, Chemistry, Biology, and more). "
                "Give clear, step-by-step, helpful answers. "
                "Use LaTeX notation for equations when helpful. "
                "Be encouraging and supportive."
            )

            # Initialize model (gemini-1.5-flash is super fast and best for chat/tutoring)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )

            # Pass the full formatted history (which includes the latest user question at the end)
            response = model.generate_content(gemini_history)
            answer = response.text

        except Exception as exc:
            answer = f"Sorry, I couldn't process your question right now. Please try again. (Error: {exc})"

    # Save AI response as 'assistant' in DB to keep your HTML templates working
    DoubtMessage.objects.create(session=session, role="assistant", content=answer)

    return JsonResponse(
        {"answer": answer, "session_id": str(session.id)}
    )


@login_required
def doubt_session_view(request, session_id):
    session = get_object_or_404(DoubtSession, id=session_id, student=request.user)
    messages_qs = session.messages.order_by("created_at")
    all_sessions = DoubtSession.objects.filter(student=request.user)[:10]
    return render(
        request,
        "ai_doubt/chat.html",
        {"session": session, "messages": messages_qs, "sessions": all_sessions},
    )