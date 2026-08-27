# Ask The User

Use the host's structured ask-user function when a missing answer changes the pack. In Codex, use `request_user_input` when it is available.

Ask only for answers not already present:

1. **Launch:** What are we launching?
2. **Page:** What one HTTPS page should people visit?
3. **Action:** What one action should people take there?
4. **Pack:** Starter, Campaign, or Everywhere?

Ask one to three short questions per function call. Give two or three clear choices only when choices help. Put the recommended choice first and explain each choice in one sentence. Let the user type a different answer.

Say what you already found before asking. Never ask for information available in the message, brand recipe, source files, or approved brief. If the function is unavailable, ask one short question in normal chat. Do not print tool JSON or pretend the function exists.
