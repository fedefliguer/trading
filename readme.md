Generar la base, entrenar el modelo, testearlo. Cuando el modelo se defina, entonces correr:

```
from google.colab import files
base.to_csv('v1.csv')
files.download('v1.csv')
```

Armar carpeta en github y subir por desktop (va a pesar demasiado para subir online). 

Guardar el script que genera la base como vX_base.ipynb.

Levantar el csv de la base con

```
url = 'https://raw.githubusercontent.com/fedefliguer/trading/master/v1/v1.csv'
base = pd.read_csv(url, index_col=0)
base['fc'] = pd.to_datetime(base['fc'], errors='coerce') # Esto reemplaza la fecha que se guarda como string
```

Guardar el script de entrenamiento y análisis como vX_train.ipynb. Guardar el modelo como vX_model.dat  con 

```
import pickle
pickle.dump(model, open("model.dat", "wb"))
```

(se guarda en el entorno de Colab, descargar desde ahí y subir por github desktop).

Para predecir, armar otro script y guardar con vX_pred.ipynb. Levantar el modelo con

```
from io import BytesIO
import pickle
import requests
mLink = 'https://github.com/fedefliguer/trading/blob/master/v1_model.dat?raw=true'
mfile = BytesIO(requests.get(mLink).content)
model = pickle.load(mfile)
```
