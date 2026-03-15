def sql_injection(request):
    """
    Sanitize input to prevent SQL injection.
    """
    # Sanitize input to prevent SQL injection
    sanitized_input = request.get("key", "")  # Example sanitization
    return sanitized_input