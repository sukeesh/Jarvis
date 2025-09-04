import wikipedia
from colorama import Fore
from plugin import plugin, require

@require(network=True)
@plugin("wiki_summary")
def wiki(jarvis, s):
    """
    Looks up a topic on Wikipedia and provides a brief summary.
    -- Example:
    wiki albert einstein
    """
    # If the user didn't provide a search term with the command, ask for one.
    if not s:
        s = jarvis.input("What would you like to look up on Wikipedia? ", Fore.CYAN)
        if not s:
            jarvis.say("No search term provided.", Fore.YELLOW)
            return

    jarvis.say(f"Searching Wikipedia for '{s}'...", Fore.BLUE)

    try:
        # Fetch a summary of the page, limited to 3 sentences for brevity.
        summary = wikipedia.summary(s, sentences=3)
        jarvis.say(summary, Fore.GREEN)

    except wikipedia.exceptions.DisambiguationError as e:
        # Handle cases where a term is ambiguous (e.g., "Java")
        jarvis.say(f"'{s}' is ambiguous. Did you mean one of these?", Fore.YELLOW)
        # List the first 5 options for the user
        for i, option in enumerate(e.options[:5]):
            jarvis.say(f"{i + 1}. {option}")

    except wikipedia.exceptions.PageError:
        # Handle cases where the page does not exist
        jarvis.say(f"Sorry, I could not find a Wikipedia page for '{s}'.", Fore.RED)

    except Exception as e:
        # Catch any other potential errors (like network issues)
        jarvis.say(f"An unexpected error occurred: {e}", Fore.RED)