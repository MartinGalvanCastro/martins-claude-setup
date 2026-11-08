---
name: grill-me
description: Interview the user one question at a time to remove ambiguity from a task, plan or design before any work starts. Use when requirements are vague, contradictory, or hide a decision the user has not made.
---

Goal: turn a vague task into a decided one. Do not plan or code until this ends.

1. Read what is already known: the task text, linked spec or ticket, and the code it touches. Answer yourself every question the code or docs can answer. Never ask the user something you can look up.
2. List the open decisions. Order them so each answer unlocks the next. Drop any that do not change the work.
3. Ask one question at a time. For each: say why it matters, give 2-3 concrete options, mark your recommendation first. Wait for the answer.
4. After each answer, re-check the remaining questions. Remove those it settled. Add new ones it exposed.
5. Stop when no open decision would change scope, design, tests or acceptance criteria. Maximum 8 questions; if more remain, say so and ask which to settle first.
6. Finish with a short decision log: question, answer, reason. The caller pastes it into the plan.

Do not ask about style, naming or anything the repo's conventions already settle. Do not ask for approval of your own questions.
