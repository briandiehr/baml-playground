
// Define the LLM client (using Llama 8b as per user preference)
client<llm> LocalLlama {
  provider openai-generic
  options {
    model "llama3.1:8b" 
    api_key "dummy-key-not-needed-for-local" 
    base_url "http://localhost:11434/v1" 
  }
}
