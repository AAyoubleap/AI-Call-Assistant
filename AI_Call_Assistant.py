from openai import OpenAI
import speech_recognition as sr
import pyttsx3

client = OpenAI(api_key = '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')
engine = pyttsx3.init()
# Set properties before adding anything to speak
# Changing rate
engine.setProperty('rate', 150)  # The speech rate

# Changing volume
engine.setProperty('volume', 0.9)  # The volume level (0.0 to 1.0)

# Changing voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) 

def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        print('skipping unknown error')
        
def transcribe_audio(recognizer, audio):
    # First, try recognizing in English
    try:
        return recognizer.recognize_google(audio, language="en-US")
    except sr.UnknownValueError:
        # If English recognition fails, try Spanish
        try:
            return recognizer.recognize_google(audio, language="es-ES")
        except sr.UnknownValueError:
            return None  # Return None if both recognitions fail
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

def generate_response(prompt, context, conversation_history):
    # Base prompt format with placeholders for dynamic content
    base_prompt_format = f"{context}\n{{conversation_history}}\nUser: {prompt}\nAI:"
    
    # Initial full prompt without trimming history
    conversation_history_str = "\n".join(conversation_history)
    full_prompt = base_prompt_format.format(conversation_history=conversation_history_str)
    
    # Check if the full prompt exceeds the model's maximum token limit
    max_tokens_allowed = 4096  # Adjust based on the model's limit
    estimated_tokens = len(full_prompt)  # Simplistic estimate; consider using a more accurate tokenization method if needed

    # Trim conversation history if estimated token count exceeds the limit
    while estimated_tokens > max_tokens_allowed and conversation_history:
        conversation_history.pop(0)  # Remove the oldest entry
        conversation_history_str = "\n".join(conversation_history)
        full_prompt = base_prompt_format.format(conversation_history=conversation_history_str)
        estimated_tokens = len(full_prompt)
    
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=full_prompt,
        max_tokens=100,  # Adjust if needed
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()


def speak_text(text):
    engine.say(text)
    engine.runAndWait()
    
def main():
    context = """"
    As GIV Trade's AI assistant, answer calls briefly, kindly, and accurately, with human-like emotion.
    If unsure, say 'I don't know.'
    """

    
    conversation_history = []  # This list will store the entire conversation history

    while True:
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 4000
            recognizer.pause_threshold = 0.5
            print("Listening for a question...")
            audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
        
        text = transcribe_audio(recognizer, audio)
        
        if text:
            # Check if the user said 'bye' to exit the program
            if text.lower() in ["bye", "adiós"]:
                print("Exiting the program.")
                break
            print(f"You said: {text}")
            
            # Append user's prompt to the conversation history
            conversation_history.append(f"User: {text}")
            
            # Generate response using GPT-3, considering the entire conversation history
            response = generate_response(text, context, conversation_history)
            print(f"GPT-3 says: {response}")
            
            # Read response using text-to-speech
            speak_text(response)
            
            # Append AI's response to the conversation history
            conversation_history.append(f"AI: {response}")

        else:
            print("I didn't catch that. Could you please repeat?")    

if __name__ == "__main__":
    main()

