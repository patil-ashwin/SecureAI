// src/services/chat/messageParser.js
import { parseMarkdown } from '@utils/parsers';
import { MESSAGE_TYPES } from '@utils/constants';

export class MessageParser {
  static parseMessage(text, type = MESSAGE_TYPES.ASSISTANT) {
    if (type === MESSAGE_TYPES.USER) {
      // User messages are plain text
      return text;
    }
    
    // Assistant messages get markdown parsing
    return parseMarkdown(text);
  }

  static extractSuggestions(text) {
    // Extract suggestions from response text if embedded
    const suggestionRegex = /Suggested questions?:\s*([\s\S]*?)(?:\n\n|$)/i;
    const match = text.match(suggestionRegex);
    
    if (match) {
      const suggestionsText = match[1];
      return suggestionsText
        .split('\n')
        .map(line => line.replace(/^[-*]\s*/, '').trim())
        .filter(line => line.length > 0);
    }
    
    return [];
  }

  static stripSuggestions(text) {
    // Remove suggestions from main text
    const suggestionRegex = /Suggested questions?:\s*([\s\S]*?)(?:\n\n|$)/i;
    return text.replace(suggestionRegex, '').trim();
  }
}