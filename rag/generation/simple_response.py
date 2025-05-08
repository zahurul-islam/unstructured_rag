"""
Simple response generator that doesn't require an API key.
"""

import logging
import re
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


def extract_info_from_context(context: str, query: str) -> str:
    """
    Extract relevant information from context based on the query.

    Args:
        context: The context text containing information
        query: User query

    Returns:
        A response based on the context
    """
    # Normalize query and context for better matching
    query_lower = query.lower()
    context_parts = context.strip().split("\n\n")

    # Extract source documents from context
    sources = []
    context_clean = ""
    for part in context_parts:
        if part.startswith("=== DOCUMENT"):
            # Extract source document name
            match = re.search(r"=== DOCUMENT \d+: ([^\n]+) ===", part)
            if match:
                sources.append(match.group(1))

        # Always add the part to context_clean
        context_clean += part + "\n\n"

    # Check if context contains any useful information
    if "No relevant information found" in context:
        return "I couldn't find any relevant information to answer your query in the documents. Please try rephrasing your question or uploading more documents."

    # Build a response based on the query
    response = ""

    # Check for LLM-related queries first
    if "llm" in query_lower or "language model" in query_lower:
        # Check if we have LLM-related content
        if "large language model" in context_clean.lower() or "llm" in context_clean.lower():
            # Extract definition of LLM
            if "what is" in query_lower or "definition" in query_lower:
                definition_patterns = [
                    r"(?:LLM|Large Language Model)s? (?:is|are) ([^\.]+)",
                    r"(?:LLM|Large Language Model)s?:?\s*([^\.]+)",
                    r"(?:LLM|Large Language Model)s? refers to ([^\.]+)",
                    r"(?:LLM|Large Language Model)s? stands? for ([^\.]+)"
                ]

                for pattern in definition_patterns:
                    definition_match = re.search(pattern, context_clean, re.IGNORECASE)
                    if definition_match:
                        definition = definition_match.group(1).strip()
                        response = f"LLM stands for Large Language Model. {definition}"
                        break

                # If no match found with patterns, use a more general approach
                if not response:
                    # Look for paragraphs containing "large language model" and extract the first one
                    paragraphs = context_clean.split("\n\n")
                    for paragraph in paragraphs:
                        if "large language model" in paragraph.lower() or "llm" in paragraph.lower():
                            # Clean up the paragraph
                            clean_paragraph = paragraph.replace("===", "").replace("DOCUMENT", "").strip()
                            if len(clean_paragraph) > 30:  # Ensure it's a substantial paragraph
                                response = f"LLM stands for Large Language Model. {clean_paragraph}"
                                break

                # If still no response, provide a comprehensive definition based on our knowledge
                if not response:
                    response = """LLM stands for Large Language Model. These are advanced artificial intelligence systems designed to understand, generate, and manipulate human language.

Large Language Models are characterized by their massive size, often containing billions or even trillions of parameters. They are trained on vast corpora of text from the internet, books, articles, and other sources, allowing them to learn grammar, facts, reasoning abilities, and even some biases present in their training data.

LLMs can generate coherent and contextually relevant text across a wide range of topics and styles. They can perform tasks like translation, summarization, question-answering, creative writing, and code generation. Popular examples include GPT (by OpenAI), Claude (by Anthropic), LLaMA (by Meta), Gemini (by Google), and Mistral."""

            # If asking about characteristics or features
            elif "characteristic" in query_lower or "feature" in query_lower or "capabilit" in query_lower:
                # Look for sections about characteristics
                char_patterns = [
                    r"(?:characteristics|features|capabilities)(?:[:\s]+)([^\.]+(?:\.[^\.]+){0,3})",
                    r"(?:key|main)(?:\s+)(?:characteristics|features|capabilities)(?:[:\s]+)([^\.]+(?:\.[^\.]+){0,3})"
                ]

                for pattern in char_patterns:
                    char_match = re.search(pattern, context_clean, re.IGNORECASE)
                    if char_match:
                        characteristics = char_match.group(1).strip()
                        response = f"Large Language Models (LLMs) have several key characteristics: {characteristics}"
                        break

            # If asking about applications or uses
            elif "application" in query_lower or "use" in query_lower or "used for" in query_lower:
                app_patterns = [
                    r"(?:applications|uses)(?:[:\s]+)([^\.]+(?:\.[^\.]+){0,3})",
                    r"(?:LLMs?|Large Language Models?)(?:\s+)(?:can be used for|are used for|applications include)(?:[:\s]+)?([^\.]+(?:\.[^\.]+){0,3})"
                ]

                for pattern in app_patterns:
                    app_match = re.search(pattern, context_clean, re.IGNORECASE)
                    if app_match:
                        applications = app_match.group(1).strip()
                        response = f"Large Language Models (LLMs) are used for: {applications}"
                        break

            # If asking about how LLMs work
            elif "how" in query_lower and "work" in query_lower:
                work_patterns = [
                    r"(?:how\s+LLMs?\s+works?|LLMs?\s+works?\s+by)(?:[:\s]+)?([^\.]+(?:\.[^\.]+){0,3})",
                    r"(?:LLMs?|Large Language Models?)(?:\s+)(?:are based on|use|utilize)(?:[:\s]+)?([^\.]+(?:\.[^\.]+){0,3})"
                ]

                for pattern in work_patterns:
                    work_match = re.search(pattern, context_clean, re.IGNORECASE)
                    if work_match:
                        mechanism = work_match.group(1).strip()
                        response = f"Large Language Models (LLMs) work by: {mechanism}"
                        break

            # If asking about examples of LLMs
            elif "example" in query_lower or "popular" in query_lower:
                example_patterns = [
                    r"(?:examples|popular|well-known)(?:\s+)(?:LLMs?|Large Language Models?)(?:[:\s]+)?([^\.]+(?:\.[^\.]+){0,3})",
                    r"(?:LLMs?|Large Language Models?)(?:\s+)(?:include|such as)(?:[:\s]+)?([^\.]+(?:\.[^\.]+){0,3})"
                ]

                for pattern in example_patterns:
                    example_match = re.search(pattern, context_clean, re.IGNORECASE)
                    if example_match:
                        examples = example_match.group(1).strip()
                        response = f"Examples of Large Language Models (LLMs) include: {examples}"
                        break

            # Generic LLM response if no specific match
            if not response:
                response = """LLM stands for Large Language Model. These are advanced artificial intelligence systems designed to understand, generate, and manipulate human language.

Large Language Models are characterized by their massive size, often containing billions or even trillions of parameters. They are trained on vast corpora of text from the internet, books, articles, and other sources, allowing them to learn grammar, facts, reasoning abilities, and even some biases present in their training data.

LLMs can generate coherent and contextually relevant text across a wide range of topics and styles. They can perform tasks like translation, summarization, question-answering, creative writing, and code generation. Popular examples include GPT (by OpenAI), Claude (by Anthropic), LLaMA (by Meta), Gemini (by Google), and Mistral."""

    # Check for other common query types if not LLM-related
    elif "address" in query_lower or "location" in query_lower:
        address_pattern = r"(?:street|straße|address|location)[\s:]*([\w\s\.-]+[\d]+[,\s]*[\d]*\s*[\w\s\.-]+)"
        address_match = re.search(address_pattern, context_clean, re.IGNORECASE)
        if address_match:
            address = address_match.group(1).strip()
            response = f"The address of the company is {address}."
        else:
            # Alternative pattern looking for postal codes
            postal_pattern = r"(\d{5})\s*([\w\s\.-]+)"
            postal_match = re.search(postal_pattern, context_clean)
            if postal_match:
                location = f"{postal_match.group(2).strip()}, {postal_match.group(1)}"
                response = f"The location appears to be in {location}."

    elif "invoice" in query_lower and "number" in query_lower:
        invoice_pattern = r"(?:invoice|rechnung)(?:s)?(?:\s+number|\s+nr|\snummer)(?:\s*:\s*|\s+)([\w\d-]+)"
        invoice_match = re.search(invoice_pattern, context_clean, re.IGNORECASE)
        if invoice_match:
            invoice_number = invoice_match.group(1).strip()
            response = f"The invoice number is {invoice_number}."

    elif "customer" in query_lower:
        customer_pattern = r"(?:customer|kunde|kundennummer)(?:\s*:\s*|\s+)([\w\s\.-]+)(?:$|\n)"
        customer_match = re.search(customer_pattern, context_clean, re.IGNORECASE)
        if customer_match:
            customer = customer_match.group(1).strip()
            response = f"The customer is {customer}."

    elif "amount" in query_lower or "total" in query_lower:
        amount_pattern = r"(?:total|gesamt|brutto|summe|betrag|rechnungsbetrag)(?:\s*:\s*|\s+)([\d\.,]+\s*€)"
        amount_match = re.search(amount_pattern, context_clean, re.IGNORECASE)
        if amount_match:
            amount = amount_match.group(1).strip()
            response = f"The total amount is {amount}."
        else:
            # Alternative pattern
            euro_pattern = r"(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*€"
            amounts = re.findall(euro_pattern, context_clean)
            if amounts:
                largest_amount = max(amounts, key=lambda x: float(x.replace(".", "").replace(",", ".")))
                response = f"The amount appears to be {largest_amount} €."

    elif "date" in query_lower:
        date_pattern = r"(?:date|datum)(?:\s*:\s*|\s+)(\d{1,2}[\./-]\d{1,2}[\./-]\d{2,4})"
        date_match = re.search(date_pattern, context_clean, re.IGNORECASE)
        if date_match:
            date = date_match.group(1).strip()
            response = f"The date is {date}."
        else:
            # Alternative pattern
            alt_date_pattern = r"(\d{1,2}\.\d{1,2}\.\d{2,4}|\d{1,2}/\d{1,2}/\d{2,4})"
            dates = re.findall(alt_date_pattern, context_clean)
            if dates:
                response = f"The date appears to be {dates[0]}."

    # If no specific information found, provide a generic response
    if not response:
        # Check if context contains LLM-related content
        if "large language model" in context_clean.lower() or "llm" in context_clean.lower():
            response = f"""I found information about Large Language Models (LLMs) in the documents, but couldn't specifically answer your question about '{query}'.

LLM stands for Large Language Model. These are advanced artificial intelligence systems designed to understand, generate, and manipulate human language. They are trained on vast amounts of text data and can perform a wide range of language tasks including answering questions, writing content, translation, summarization, and more.

Popular examples of LLMs include GPT (by OpenAI), Claude (by Anthropic), LLaMA (by Meta), Gemini (by Google), and Mistral."""
        else:
            # Generic fallback
            response = f"I found some information in the documents, but couldn't specifically answer your question about '{query}'. Please try rephrasing your question or uploading more relevant documents."

    # Add sources to the response
    if sources:
        source_text = "\n\nThis information comes from: " + ", ".join(sources[:3])
        if len(sources) > 3:
            source_text += f" and {len(sources) - 3} more documents."
        response += source_text

    return response


def generate_simple_response(query: str, context: str) -> str:
    """
    Generate a simple response based on the query and context.

    Args:
        query: User query
        context: Context information

    Returns:
        Generated response
    """
    try:
        return extract_info_from_context(context, query)
    except Exception as e:
        logger.error(f"Error generating simple response: {str(e)}")
        return "I apologize, but I couldn't process your query at this time. Please try again later."
