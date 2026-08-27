# Ask The User

Use the host's structured ask-user function when a missing choice changes the result. In Codex, use `request_user_input` when it is available.

- Ask one to three short questions.
- Give two or three clear choices.
- Put the recommended choice first.
- Explain each choice in one short sentence.
- Let the user type a different answer.
- Say what you found before asking.
- Never ask for information the files or the user's message already provide.

If the function is unavailable, ask one short question in normal chat. Do not print tool JSON or pretend the function exists.
