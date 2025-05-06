# OPENAI_API_KEY

# DOMPREH
# If you don't want to use an environment variable (less secure),
# you can set the API key directly:
# openai.api_key = "YOUR_API_KEY"  # Replace with your actual API key

import openai
import api_secrets

openai.api_key = api_secrets



def generate_names_chat(theme, number_of_names=3):
    """Generates names using the Chat Completion API."""
    try:
        messages = [
            {"role": "system", "content": "You are a creative naming assistant.  You generate lists of names related to a given theme."},
            {"role": "user", "content": f"Generate {number_of_names} names that fit the theme: {theme}."},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or gpt-4
            messages=messages,
            max_tokens=100,  # Adjust as needed
            temperature=0.7,
        )

        # Extract and split the names from the response
        name_string = response.choices[0].message["content"].strip()
        names = [name.strip() for name in name_string.split("\n") if name.strip()]

        return names

    except Exception as e:
        print(f"Error generating names: {e}")
        return []



def draft_email_chat(recipient, topic, main_points, tone="professional"):
    """Drafts an email using the Chat Completion API with customizable tone."""
    try:
        messages = [
            {"role": "system", "content": f"You are an expert email writer.  Your writing style is {tone}."},
            {"role": "user", "content": f"Draft an email to {recipient} about the topic: {topic}.  Include these main points: {', '.join(main_points)}."},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or gpt-4
            messages=messages,
            max_tokens=250,  # Adjust as needed
            temperature=0.7,
        )

        email_draft = response.choices[0].message["content"].strip()
        return email_draft

    except Exception as e:
        print(f"Error drafting email: {e}")
        return ""


if __name__ == "__main__":
    # Name generation example
    theme = "cyberpunk city"
    generated_names = generate_names_chat(theme, number_of_names=4)

    if generated_names:
        print(f"Generated names for '{theme}':")
        for name in generated_names:
            print(f"- {name}")
    else:
        print("Could not generate names.")


    # Email drafting example
    recipient = "Alex Johnson"
    topic = "Project Kickoff Meeting"
    main_points = ["Agenda overview", "Team introductions", "Timeline discussion"]
    email_draft = draft_email_chat(recipient, topic, main_points, tone="friendly")

    if email_draft:
        print("\nEmail Draft (Chat Completion API):")
        print(email_draft)
    else:
        print("Could not draft email.")