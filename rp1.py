from transformers import pipeline

# Initialize the pipeline with distilgpt2
generator = pipeline('text-generation', model='distilgpt2')

# Example usage
response = generator("Create a recipe using chicken and rice.", max_length=100, num_return_sequences=1)
print(response[0]['generated_text'])
