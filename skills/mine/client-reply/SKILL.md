---
name: client-reply
description: "Draft a reply to a client, partner, or support/CS colleague from findings already in hand: answer first, short, no-blame, nobody named outside the thread. Use when the user asks to answer, reply to, write, or polish an email or message to a client, partner, or CS team."
---

Draft the reply; the user sends it. The draft goes to the reader of the thread, not to the user: write for someone who knows their own problem and none of the internals.

## Inputs

- **The thread.** Pasted, or, when a Gmail connector is available and the user names the thread (subject, sender, or link), read the whole thread from Gmail.
- **The findings.** What the conversation established: an investigation report, a case file (`tmp/cases/<slug>/case.md` in HDH), a fix that shipped. When the findings are thin, say what is missing instead of filling the gap.
- **The project tone file.** `docs/agents/client-reply.md` in the current repo, when it exists: audience, greetings, sign-off, words to prefer, and the path of the project's dated improvements list. Its rules override the defaults below.

## Rules

The defaults for every reply:

1. **Answer first.** The opening lines answer the question the thread asked. Background comes after, only as much as the answer needs.
2. **Short.** Four to eight lines per case. Several cases get one short section each, in the order the thread raised them.
3. **No-blame framing.** Describe what happened and what is now in place: "ya identificamos qué ocurría y quedó corregido el <fecha>". Keep the account factual and forward-looking, the way a calm engineer explains an incident to a customer.
4. **Only the thread's people.** Name only people who are on the thread. Everyone else is a role ("el equipo de integraciones", "el proveedor").
5. **Outside view.** Keep to what the reader can see or act on. Tokens, IPs, hosts, file paths, code, and internal ticket ids stay out.
6. **Dated improvements.** When something the reader expected didn't exist yet, cite the improvement and its date from the project's improvements list ("desde abril de 2026 …").
7. **One ask.** End with one next step or one question for the reader, with a date when there is one.
8. **Language and register.** The thread's language, friendly and professional, plain words. Run the `unslop` skill over the draft.

## Process

1. **Frame.** Write down, for yourself, the question the thread asks and the answer in one sentence each. Done when both sentences exist and the answer is backed by the findings.
2. **Draft.** Write the reply. Done when it passes every rule above, checked one by one, including the tone file's.
3. **Deliver.** With a Gmail connector and a thread, save it as a draft reply in that thread and give the user the link. Otherwise give the draft as plain text, ready to paste. Never send.

When the user corrects the tone, apply the correction, then offer to add it as a rule to the project tone file so the next draft starts there.
