def build_subscription_reply(message: str) -> tuple[str, str]:
    text = (message or "").strip()
    if any(keyword in text.lower() for keyword in ("订阅", "subscribe", "关注")):
        return "subscribe", "您好，已收到您的订阅意向。请提供您的邮箱地址，我们将为您开通订阅通知。"
    return "unknown", "您好，请告诉我们您想订阅的内容，并提供邮箱地址。"
