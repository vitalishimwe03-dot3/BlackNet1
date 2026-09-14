"""Shared request helper utilities (safe, no secrets touched)."""


def request_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def friendly_device_name(user_agent):
    ua = user_agent.lower()
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        kind = "MOBILE"
    elif "tablet" in ua or "ipad" in ua:
        kind = "TABLET"
    else:
        kind = "DESKTOP"
    if "chrome" in ua:
        browser = "CHROME"
    elif "firefox" in ua:
        browser = "FIREFOX"
    elif "safari" in ua:
        browser = "SAFARI"
    elif "edge" in ua:
        browser = "EDGE"
    else:
        browser = "UNKNOWN"
    return f"{browser} / {kind}"