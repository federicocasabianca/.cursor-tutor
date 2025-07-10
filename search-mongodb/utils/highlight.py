def find_highlight_positions(text, query):
    if not query or not text:
        return 0, 0
    text_lower = text.lower()
    query_lower = query.lower()
    start_pos = text_lower.find(query_lower)
    if start_pos == -1:
        query_words = query_lower.split()
        for word in query_words:
            if len(word) >= 2:
                word_pos = text_lower.find(word)
                if word_pos != -1:
                    start_pos = word_pos
                    end_pos = word_pos + len(word)
                    return start_pos, end_pos
        return 0, 0
    end_pos = start_pos + len(query)
    return start_pos, end_pos
