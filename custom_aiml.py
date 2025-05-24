import aiml
import time

class CustomAIMLKernel(aiml.Kernel):
    def __init__(self):
        super().__init__()
        # Override the time function to use perf_counter instead of clock
        self._time = time.perf_counter

    def learn(self, file_name):
        try:
            start = time.perf_counter()
            super().learn(file_name)
            end = time.perf_counter()
            print(f"Time taken to learn {file_name}: {end - start:.2f} seconds")
        except Exception as e:
            print(f"Error in learn method: {str(e)}")
            raise

    def respond(self, input_text):
        try:
            return super().respond(input_text)
        except Exception as e:
            print(f"Error in respond method: {str(e)}")
            return "I'm having trouble processing that. Could you rephrase?"
