"""Resolve user/assistant/EOS token ids for chat-template collators."""


def resolve_collator_token_ids(tokenizer, formatter):
    """Return ``(user_token_id, assistant_token_id, eos_id)`` from tokenizer + chat formatter."""
    eos_ids = tokenizer.encode(str(formatter.im_end), add_special_tokens=False)
    if len(eos_ids) != 1:
        raise ValueError("im_end must encode to one token")

    eos_id = int(eos_ids[0])

    u = tokenizer.encode(formatter.im_user, add_special_tokens=False)
    a = tokenizer.encode(formatter.im_assistant, add_special_tokens=False)

    if int(u[0]) == int(a[0]):
        user_tid, assistant_tid = int(u[1]), int(a[1])
    else:
        user_tid, assistant_tid = int(u[0]), int(a[0])

    return user_tid, assistant_tid, eos_id