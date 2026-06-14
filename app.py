    # -------- SMART SIGNAL CLASSES --------

    signal = "NO EDGE (WAIT)"
    confidence = 50
    signal_reason = "MARKET BALANCED"

    # High conviction BUY CALL
    if pcr > 1.30 and bullish > 58:
        signal = "HIGH CONVICTION BUY CALL"
        confidence = 88
        signal_reason = "STRONG CALL BUILDUP + PCR IMBALANCE"

    # Valid BUY CALL
    elif pcr > 1.10:
        signal = "VALID BUY CALL"
        confidence = 70
        signal_reason = "MODERATE CALL SIDE PRESSURE"

    # High conviction BUY PUT
    elif pcr < 0.75 and bearish > 58:
        signal = "HIGH CONVICTION BUY PUT"
        confidence = 88
        signal_reason = "STRONG PUT BUILDUP + PCR BIAS"

    # Valid BUY PUT
    elif pcr < 0.95:
        signal = "VALID BUY PUT"
        confidence = 70
        signal_reason = "MODERATE PUT SIDE PRESSURE"
