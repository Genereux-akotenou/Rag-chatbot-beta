### Install ollama and run LLM
<br>

- Step 1: Download Ollama to Get Started
```sh
$ curl -fsSL https://ollama.com/install.sh | sh
```

- Step 2: Get the Model
```sh
$ ollama pull phi3
```

- Step 3: Run the Model
```sh
$ ollama run phi3
```

- Step 4: Customize Model Behavior with System Prompts
Say you want the model to always explain concepts or answer questions in plain English with minimal technical jargon as possible. Here’s how you can go about doing it:
```sh
>>> /set system For all questions asked answer in plain English avoiding technical jargon as much as possible
Set system message.
>>> /save phi3_for_sci
Created new model 'phi3_for_sci'
>>> /bye
```
Now run the model you just created:
```sh
$ ollama run phi3_for_sci
```

- Step 5: Use Ollama with Python (in UI)
```sh
$ pip install ollama
```
```python
import ollama

response = ollama.generate(model='gemma:2b',
prompt='what is a qubit?')
print(response['response'])
```


