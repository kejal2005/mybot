import aiml
import time

# Custom Kernel to fix the time.clock() issue
class CustomKernel(aiml.Kernel):
    def learn(self, file_name):
        # Override the time.clock() call
        start = time.perf_counter()  # Use time.perf_counter() instead of time.clock()
        
        # Call the original method to maintain the usual functionality
        super().learn(file_name)
        
        end = time.perf_counter()
        print(f"Time taken to learn {file_name}: {end - start:.2f} seconds")
