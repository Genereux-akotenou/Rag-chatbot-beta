
------- FLASK
### Create conda environment
Firstly, we will create a conda environment called *lab1_env*
```
python -m venv lab1_env
```
Secondly, we will login to the *lab1_env* environement
```
source ./lab1_env/bin/activate
```
### Install prerequisite libraries
Pip install libraries
```
pip install -r requirements.txt
```

###  Launch the app
```
python app.py
```


----- LAMMA
1. Run docker
```bash
docker compose up -d
```

2. Run the model locally (llama3):
```bash
docker exec -it ollama ollama run llama3
```

You can now chat with the model on the terminal
3. Execute python file on your host terminal
```bash
python request.ipynb
```

If you have GPU, go to the official  [ollama docker image](https://hub.docker.com/r/ollama/ollama) for configuration.

Enjoy!
