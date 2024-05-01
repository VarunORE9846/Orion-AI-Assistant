import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from groq_ai import *
from TTS import *
import base64

# Initialize recognition object outside of main function
recognition = None

# Function to start/stop speech recognition
def autoplay_audio(file_path: str):
    # Read the audio file
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        # Embed an audio player in the Streamlit app
        st.audio(data, format='audio/mp3', start_time=0)
def main():
    st.title("ORION TALKING ASSISTANT")
    st.write("Please Click Below Button to start/stop recording ")

    # Button to start speech recognition
    speak_button = Button(label="Speak", width=100)
    st.bokeh_chart(speak_button)

    # Start recognition on speak button click
    speak_button.js_on_event(
        "button_click",
        CustomJS(
            code=""" 
            var recognition = window.recognition;
            if (!recognition) {
                recognition = window.recognition = new webkitSpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;

                recognition.onresult = function(e) {
                    var value = "";
                    for (var i = e.resultIndex; i < e.results.length; ++i) {
                        if (e.results[i].isFinal) {
                            value += e.results[i][0].transcript;
                        }
                    }
                    if (value !== "") {
                        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
                    }
                } 

                recognition.start();
            }
            """
        ),
    )

    # Button to stop speech recognition
    stop_button = Button(label="Stop", width=100)
    st.bokeh_chart(stop_button)

    # Stop recognition on stop button click
    stop_button.js_on_event(
        "button_click",
        CustomJS(
            code="""
            recognition.stop();
            window.recognition = null;
            """
        )
    )

    # Get the result of speech recognition
    result = streamlit_bokeh_events(
        speak_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0,
    )
    if result:
        if "GET_TEXT" in result:
            response = generate_response(result.get("GET_TEXT"))
            file = TTS(response)
            autoplay_audio(file)

if __name__ == "__main__":
    main()
