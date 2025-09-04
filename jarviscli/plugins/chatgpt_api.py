# OPENAI_API_KEY

# DOMPREH
# If you don't want to use an environment variable (less secure),
# you can set the API key directly:
# openai.api_key = "YOUR_API_KEY"  # Replace with your actual API key

from openai import OpenAI
import api_secrets



# Configure OpenAI to use OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_secrets.openai_api_key,  # Get key from api_secrets.py
)


def generate_names_chat(theme, number_of_names=3, model="openai/gpt-3.5-turbo"):
    """Generates names related to a theme using the Chat Completion API via OpenRouter."""
    try:
        messages = [
            {"role": "system", "content": "You are a creative naming assistant. Generate lists of names related to a given theme."},
            {"role": "user", "content": f"Generate {number_of_names} names that fit the theme: {theme}."},
        ]

        response = client.chat.completions.create(  # Use the 'client' object
            model=model,
            messages=messages,
            max_tokens=100,
            temperature=0.2,
            extra_headers={
                "HTTP-Referer": "https://github.com/C5Marshall/Jarvis.git",  # Required by OpenRouter
                "X-Title": "Jarvis",  # Required by OpenRouter
            },
        )

        name_string = response.choices[0].message.content.strip()
        names = [name.strip() for name in name_string.split("\n") if name.strip()]
        return names

    except Exception as e:
        print(f"Error generating names: {e}")
        return []


def draft_email_chat(recipient, topic, main_points, tone="professional", model="openai/gpt-3.5-turbo"):
    """Drafts an email using the Chat Completion API via OpenRouter with a specified tone."""
    try:
        messages = [
            {"role": "system", "content": f"You are an expert email writer. Your writing style is {tone}."},
            {"role": "user", "content": f"Draft an email to {recipient} about the topic: {topic}. Include these main points: {', '.join(main_points)}."},
        ]

        response = client.chat.completions.create(  # Use the 'client' object
            model=model,
            messages=messages,
            max_tokens=250,
            temperature=0.2,
            extra_headers={
                "HTTP-Referer": "https://github.com/C5Marshall/Jarvis.git",  # Required by OpenRouter
                "X-Title": "Jarvis",  # Required by OpenRouter
            },
        )

        email_draft = response.choices[0].message.content.strip()
        return email_draft

    except Exception as e:
        print(f"Error drafting email: {e}")
        return ""


if __name__ == "__main__":
    # Make sure to replace "openai/gpt-3.5-turbo" with a model available on OpenRouter
    # and that you have a valid OpenRouter API key in your api_secrets.py

    # Name generation example
    theme = "Magic city"
    generated_names = generate_names_chat(theme, number_of_names=4)

    if generated_names:
        print(f"Generated names for '{theme}':")
        for name in generated_names:
            print(f"- {name}")
    else:
        print("Could not generate names.")

    # Email drafting example
    recipient = "Jesse Dompreh"
    topic = "Senior Design presentation"
    main_points = ["Agenda overview", "Team introductions", "Timeline discussion"]
    email_draft = draft_email_chat(recipient, topic, main_points, tone="friendly")

    if email_draft:
        print("\nEmail Draft (Chat Completion API):")
        print(email_draft)
    else:
        print("Could not draft email.")



print(" ")


import pyttsx3

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Function to speak the text
def speak(text):
    engine.say(text)
    engine.runAndWait()  # This is required to process the speech

# Function to process the command
def process_jarvis_command(command):
    command = command.lower()

    if "name" in command:
        theme = command.split("about")[-1].strip() if "about" in command else "Random"
        names = generate_names_chat(theme)
        if names:
            print(f"\nHere are some names about '{theme}':")
            speak(f"Here are some names about {theme}.")
            for name in names:
                print(f"- {name}")
                speak(name)
        else:
            print("I couldn't come up with any names.")
            speak("I couldn't come up with any names.")

    elif "email" in command:
        recipient = "Jesse"
        topic = "Senior design update"
        main_points = ["Progress", "Timeline", "Next steps"]
        email = draft_email_chat(recipient, topic, main_points)
        print("\nDrafted Email:\n" + email)
        speak("Here is your drafted email.")
        speak(email)  # Speak the email content too
    else:
        print("Sorry, I didn't understand that.")
        speak("Sorry, I didn't understand that.")

# Start the program
if __name__ == "__main__":
    print("Jarvis is online.")
    speak("Jarvis is online.")  # To confirm that the program is running
    while True:
        user_input = input("\nYou: ")
        if "exit" in user_input.lower():
            speak("Goodbye!")
            break
        if "jarvis" in user_input.lower():
            process_jarvis_command(user_input)
import pyttsx3

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Function to speak the text
def speak(text):
    engine.say(text)
    engine.runAndWait()  # This is required to process the speech

# Function to process the command
def process_jarvis_command(command):
    command = command.lower()

    if "name" in command:
        theme = command.split("about")[-1].strip() if "about" in command else "Random"
        names = generate_names_chat(theme)
        if names:
            print(f"\nHere are some names about '{theme}':")
            speak(f"Here are some names about {theme}.")
            for name in names:
                print(f"- {name}")
                speak(name)
        else:
            print("I couldn't come up with any names.")
            speak("I couldn't come up with any names.")

    elif "email" in command:
        recipient = "Jesse"
        topic = "Senior design update"
        main_points = ["Progress", "Timeline", "Next steps"]
        email = draft_email_chat(recipient, topic, main_points)
        print("\nDrafted Email:\n" + email)
        speak("Here is your drafted email.")
        speak(email)  # Speak the email content too
    else:
        print("Sorry, I didn't understand that.")
        speak("Sorry, I didn't understand that.")


