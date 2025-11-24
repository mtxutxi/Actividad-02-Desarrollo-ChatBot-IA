
![Badge en Desarollo](https://img.shields.io/badge/STATUS-FINALIZADO-green)
# LibrerIA

_Hemos creado un chat bot que se alimenta de una BBDD que contiene información sobre autores, libros, ventas, cachés de autores..._

## Comenzando 🚀

_Para poder ver la aplicación, tienes dos maneras de hacerlo, bien te descargas el zip y lo descomprimes o haces un CLONE del proyecto en local ._

Mira **Deployment** para conocer como desplegar el proyecto.


### Pre-requisitos 📋

_Tener Python instalado en el ordenador y como IDE recomendamos Visual Studio Code. Necesitamos tener instalado también SQL Server Management Studio_

[Instalar Python](https://kinsta.com/es/blog/instalar-python/)\
[Instalar Visual Studio Code](https://code.visualstudio.com/download)\
[SQL Server](https://learn.microsoft.com/es-es/ssms/install/install)\
[Instalar GTK3](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe)



## Despliegue 📦


Nos posicionamos en nuetsra carpeta del proyecto, abrimos cmd y ponemos los siguientes comandos para crear entorno virtual e instalars las depndencias que tenemos dentro de requirements</br>
<img width="968" height="142" alt="abrir" src="https://github.com/user-attachments/assets/1d78e1a9-c69f-4681-ba1b-0826cae9d1d7" /></br>
Una vez instalado todo abrimos el IDE con code .</br>
<img width="984" height="101" alt="abrir2" src="https://github.com/user-attachments/assets/045aec63-1855-4b17-983c-a705327e44d7" /></br>
Se va a abrir el Visual Studio Code, en la consola ponemos streamlit run ./app.py</br>
<img width="667" height="178" alt="abrir3" src="https://github.com/user-attachments/assets/a4eefe52-9065-46f5-b705-17e30ae339bc" />

## Construido con 🛠️

_Menciona las herramientas que utilizaste para crear tu proyecto_

* Python
* SQL Server Management Studio
* Librerias: streamlit, google-genai, openai, dotenv, pymssql,reportlab, openpyxl
   



## Wiki 📖

El chat lo que hace es traducir tu consulta en lenguaje natural a un bloque SQL. Le hemos dado una lista de palabras proihibidas para que solo haga conusltas SELECT
<img width="2548" height="1306" alt="Captura de pantalla 2025-11-23 222442" src="https://github.com/user-attachments/assets/f1f30c64-9a81-439f-af53-47580b1d35ed" />


## Autores ✒️

* **Txutxi Martínez** 
* **Belen Barbas** 
* **Sheila Roca** 

También puedes mirar la lista de todos los [contribuyentes](https://github.com/your/project/contributors) quíenes han participado en este proyecto. 




