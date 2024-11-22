
RUNNING LLM UI

### Create environment
Firstly, we will create a conda environment called *rag_env*
```sh
python -m venv rag_env
```
Secondly, we will login to the *rag_env* environement
```sh
source ./rag_env/bin/activate
```
### Install prerequisite libraries

```sh
pip install -r requirements.txt
```

###  Launch the app
```
streamlit run app.py
```

###  Launch file server
```
python file_server.py
```
