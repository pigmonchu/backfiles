# Instalación del servidor y login

## Crear el entorno virtual
`python -m venv <dir_entorno_virtual>`

## Instalación de dependencias
`pip install -r requirements.txt`

## Activar entorno virtual

`. .env`

Si miras el fichero verás que se crean las variables de entorno necesarias, a saber:
```
FLASK_APP=run.py
FLASK_CONFIG=development
```
## Crear fichero de configuración

Tomando como muestra el fichero `app/instance/config_template.py` crear un fichero llamado `app/config.py` e informar al menos los siguientes valores:

```
sqlitedb = os.path.abspath("data/files.db")
...
SECRET_KEY
SECURITY_PASSWORD_SALT
```
Evidentemente puedes cambiar la localización y el nombre del fichero sqlite. Lo razonable en tal caso sería añadir esa nueva localización a `.gitignore`. 

## Creación de database (en SQLite)

Crear fichero de sqlite

```
mkdir data
cd data
touch files.db
````

Ejecutar migraciones:
```
flask db upgrade
```
Eso debería generar el fichero `data/files.db` con las tablas necesarias para crear usuarios y el login y control de acceso.

## Lanzar la aplicación

Ejecutar
`flask run``

# Crear primer usuario

Para crear un usuario hay que ejecutar en el navegador el siguiente endpoint:

```
[POST] 
    http://localhost:5000/<API_ROOT_URL>/<API_VERSION>/register
```

donde API_ROOT_URL y API_VERSION son variables del fichero `instance/config.py``

Se debe informar lo siguiente en formato json
| key | value | obligatorio | 
|---|---|---|
| email | correo electrónico del usuario | Sí |
| first_name | Nombre del usuario | Sí |
| last_name | Apellidos del usuario | _No_ |
| password | contraseña | Sí |
| rpt_pass | repetir contraseña | Sí |
| is_administrator | Permisos de administrador | _No_ |


```
{
		"email": "nombre@correo.es"	,
		"first_name": "nombre",
		"last_name": "apellidos",
		"password": "supersegura",
		"rpt_pass": "supersegura"
        "is_administrator": false
}
```


Para que todo vaya bien se deben informar correctamente los siguientes valores del fichero `instance/config.py``
```
MAIL_SERVER = 'your-smtp-server-here'
MAIL_PORT = 000
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'your-mail-user-name-here'
MAIL_PASSWORD = 'your-mail-pwd-here'
DEFAULT_MAIL_SENDER ='aquí da igual lo que pongas'
```
Necesitarás obtener estos parámetros de tu proveedor de correo o de tu servidor si lo montas.

## Funcionamiento

Si el mensaje de respuesta es OK se enviará un correo a la dirección informada en el que figurará un enlace para confirmar el usuario. Tiene una validez de 24 horas o habrá que volver a pedir confirmación.

Para volver a pedir confirmación se debe usar el endpoint 
```
[POST]
    http://localhost:5000/<API_ROOT_URL>/<API_VERSION>/reconfirm
```
donde API_ROOT_URL y API_VERSION son variables del fichero `instance/config.py``

Se debe informar lo siguiente en formato json
| key | value | obligatorio | 
|---|---|---|
| email | correo electrónico del usuario | Sí |
| password | contraseña | Sí |

```
{
		"email": "nombre@correo.es"	,
		"password": "supersegura",
}
```
Si el usuario ya estuviera confirmado se informará así en la respuesta, en otro caso (siempre que exista) se generará un nuevo enlace de confirmación válido por 24h y se enviará a la dirección de correo

# Login y logout

Ambos endpoints.
## Login

```
[POST]
    http://localhost:5000/<API_ROOT_URL>/<API_VERSION>/login
```
donde API_ROOT_URL y API_VERSION son variables del fichero `instance/config.py``

Se debe informar lo siguiente en formato json
| key | value | obligatorio | 
|---|---|---|
| email | correo electrónico del usuario | Sí |
| password | contraseña | Sí |

```
{
		"email": "nombre@correo.es"	,
		"password": "supersegura"
}
```
El sistema devolverá un token que deberá informarse en todos aquellos endpoints que necesiten autenticación. O, en su caso, un mensaje de error si el login fuera incorrecto.

## Logout
```
[POST]
    http://localhost:5000/<API_ROOT_URL>/<API_VERSION>/logout
```
donde API_ROOT_URL y API_VERSION son variables del fichero `instance/config.py`. 
En este caso no hay información en formato json, se utiliza la cabecera `Authorization` con el valor `JWT <token>`. 

