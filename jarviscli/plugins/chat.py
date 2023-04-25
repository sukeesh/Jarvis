from plugin import plugin
from plugin import complete
import gpt_2_simple as gpt2
import os

@complete("chat")
@plugin("chat")
def chat(jarvis, s):
    """
    Uses GPT-2 to give a response based on the users prompt

    Parameters:
    jarvis (obj): Jarvis assistant object
    s (str): Prompt entered by the user

    Returns:
    None

    Example Usage:
    chat What is the best programming language?
    """
    
    # Check for user input
    if not s:
        print("Please input a prompt. Usage: chat [prompt]")
        return
    
    # List of available GPT-2 models
    MODELS = ['124M', '355M', '774M', '1558M']

    # Check if the model directory already exists
    if os.path.exists('models'):
        print('GPT-2 models already installed.')
    else:
        # If the directory doesn't exist, create it
        os.makedirs('models')

        # Prompt the user to select a model to install
        print('Available models:')
        for model in MODELS:
            print(f'- {model}')
        model_choice = input('Enter the name of the model you want to install (the larger the models the better the responses): ')

        # Check that the selected model is valid
        if model_choice not in MODELS:
            print('Invalid model choice.')
        else:
            # Download the selected model
            if not os.path.isdir(os.path.join("models", model_choice)):
                print(f"Downloading {model_choice} model...")
                gpt2.download_gpt2(model_name=model_choice)

    # Check models directory for already installed models
    model_name = ""

    for model in MODELS:
        model_dir = os.path.join(os.getcwd(), 'models', model)
        if os.path.exists(model_dir):
            print(f'The {model} model is installed.')
            model_name = model
            break

    if not 'models':
        print('None of the specified models are installed. Exiting.')
        exit()

    # Start GPT-2 session with the installed model
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, model_name=model_name)

    # Generate response
    response = gpt2.generate(sess, model_name=model_name, prefix=s, length=100, temperature=0.7, nsamples=1, batch_size=1, return_as_list=True)[0]

    # Print out GPT-2's response
    print('\n')
    jarvis.say(response)
    print('\n')

    # Reset GPT-2's session
    gpt2.reset_session(sess)