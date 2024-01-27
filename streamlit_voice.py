import assemblyai as aai
import openai
import elevenlabs
from queue import Queue
import threading

# Set API keys
aai.settings.api_key = "3eae932d68a448c3ad7f9ac0ced7a66d"
openai.api_key = "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"
elevenlabs.set_api_key("9e54de1e62c112136e32d8850d57e4f7")

transcript_queue = Queue()
user_input = ""
conversation_active = False

def on_data(transcript: aai.RealtimeTranscript):
    global user_input
    if not transcript.text:
        return
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        user_input = transcript.text
        print("User:", user_input, end="\r\n")
    else:
        print(transcript.text, end="\r")

def on_error(error: aai.RealtimeError):
    print("An error occurred:", error)

# Start and stop conversation
def start_conversation():
    global conversation_active
    try:
        while conversation_active:
            transcriber = aai.RealtimeTranscriber(
                on_data=on_data,
                on_error=on_error,
                sample_rate=44_100,
            )

            # Start the connection
            transcriber.connect()

            # Open the microphone stream
            microphone_stream = aai.extras.MicrophoneStream()

            # Stream audio from the microphone
            transcriber.stream(microphone_stream)

            # Close current transcription session
            transcriber.close()

    except KeyboardInterrupt:
        print("\nConversation ended.")
        process_user_input()

def process_user_input():
    if user_input:
        # Send the transcript to OpenAI for response generation
        from openai import OpenAI
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 'You are a highly skilled AI, answer the questions given within a maximum of 1000 characters.'},
                {"role": "user", "content": user_input}
            ]
        )

        text = response.choices[0].message.content

        # Print AI response
        print("\nAI:", text, end="\r\n")

        # Generate audio from text and play it
        audio = elevenlabs.generate(
            text=text,
            # voice="Bella"  # or any voice of your choice
        )

        elevenlabs.play(audio)

if __name__ == "__main__":
    print("Welcome to the conversation! Press and hold a key (e.g., Enter) to start the conversation.")
    print("Release the key to end the conversation.")
    
    while True:
        input("Press and hold a key to start the conversation... (Press Enter to quit)")
        conversation_active = True
        conversation_thread = threading.Thread(target=start_conversation)
        conversation_thread.start()

        input("Release the key to end the conversation... (Press Enter to quit)")
        conversation_active = False
        conversation_thread.join()
