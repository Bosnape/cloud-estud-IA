# Conceptos previos para Arquitectura en la Nube – Nivel Intermedio

**Guía rápida, práctica y con símiles de la vida real**

Este documento reúne las ideas que conviene tener claras antes (o durante) el curso. No es un tratado: cada tema tiene una definición corta, un símil cotidiano y un mini ejemplo que puedes ejecutar o leer.

**Cómo usarlo**

- No necesitas leerlo de corrido. Consulta el tema cuando aparezca en clase, en Platzi o en tu proyecto.
- Cada tema indica en qué módulo lo verás: **M1** CI/CD · **M2** Contenedores · **M3** Despliegue · **M4** Redes · **M5** Terraform · **M6** Observabilidad.
- Los comandos son para Linux o macOS (en Windows, usa WSL o Git Bash). Las salidas son ejemplos: las tuyas variarán.
- Los símiles ayudan a entender la idea, no son exactos. Cuando el símil se queda corto, lo decimos.

**Contenido**

1. Cómputo y sistema operativo: CPU, RAM, almacenamiento, kernel, proceso e hilo, variables de entorno, permisos, señales y códigos de salida
2. Ejecución de programas: compilado vs. interpretado, dependencias, binario/artefacto/build, versionado semántico, fugas de memoria y OOM kill
3. Control de versiones: Git, Gitflow, GitOps, trunk-based, pull request, tags y releases, .gitignore y secretos
4. Redes: HTTP/HTTPS, DNS, firewall y puertos, TLS y certificados
5. Conceptos de nube: IaaS/PaaS/SaaS/serverless, VM vs. contenedor, infraestructura inmutable
6. Observabilidad: logs, métricas y trazas; logs estructurados; trazas distribuidas
7. Seguridad básica: cifrado, WAF y OWASP, superficie de ataque

---

# 1. Cómputo y sistema operativo

## 1.1 CPU

**Qué es:** el componente que ejecuta las instrucciones de los programas. Tiene varios **núcleos** (cores), y cada núcleo puede atender una tarea a la vez (algunos exponen dos "hilos" por núcleo). El **uso de CPU** es qué porcentaje de su tiempo está ocupada; **saturación** es cuando hay más trabajo que capacidad y las tareas hacen fila.

**Símil:** una cocina de restaurante. Cada núcleo es un cocinero. Con 4 cocineros se preparan 4 platos a la vez. Si llegan 40 pedidos, los pedidos hacen fila: el restaurante no se cae, pero todo se vuelve lento.

**Ejemplo:**

```bash
nproc                 # cuántos núcleos ve este equipo
# 4

top                   # uso de CPU en vivo (salir con q)
# %Cpu(s): 92.0 us, 3.0 sy, 0.0 ni, 5.0 id ...
#          ^^^^ us = usuario (tus programas), id = idle (libre)

docker run --cpus=0.5 nginx   # limitar un contenedor a medio núcleo
```

**Por qué importa:** los contenedores y Kubernetes asignan y limitan CPU. Una CPU saturada es una de las causas más comunes de latencia alta. **Dónde lo verás:** M2, M6.

## 1.2 Memoria RAM

**Qué es:** la memoria rápida y temporal donde viven los programas mientras se ejecutan. Es mucho más rápida que el disco, pero **se borra al apagar** o al terminar el proceso.

**Símil:** el escritorio donde trabajas versus el archivador de la oficina. El escritorio (RAM) es pequeño pero todo está al alcance de la mano. El archivador (disco) guarda mucho más, pero ir a buscar algo toma tiempo. Si el escritorio se llena, no puedes trabajar con más documentos abiertos.

**Ejemplo:**

```bash
free -h
#                total   used   free  shared  buff/cache  available
# Mem:           7.7Gi  2.1Gi  3.9Gi   0.1Gi       1.7Gi      5.3Gi

docker run -m 256m nginx   # límite de memoria de 256 MB para el contenedor
```

**Por qué importa:** si un contenedor supera su límite de memoria, el sistema lo mata (ver 2.5). Los límites de memoria son parte de cualquier despliegue serio. **Dónde lo verás:** M2, M6.

## 1.3 Almacenamiento (bloque, archivos y objetos)

**Qué es:** donde los datos se guardan de forma **persistente**. En la nube hay tres tipos:

- **Bloque:** un disco "crudo" que se conecta a una máquina (como un disco duro virtual).
- **Archivos:** carpetas y archivos compartidos por red (varias máquinas leen el mismo directorio).
- **Objetos:** un enorme depósito donde guardas "objetos" (fotos, backups, archivos de estado) identificados por un nombre único. No hay carpetas reales ni se edita "un pedacito": se reemplaza el objeto completo.

**Símil:**

| Tipo | Símil |
|---|---|
| Bloque | Un lote vacío: tú decides cómo construirlo y organizarlo |
| Archivos | Un archivador con carpetas que varias personas consultan |
| Objetos | Una bodega con casilleros etiquetados: dejas una caja, recibes una etiqueta, la recuperas completa |

**Ejemplo:**

```bash
df -h /                      # espacio del disco donde estás
# Filesystem  Size  Used  Avail  Use%  Mounted on
# /dev/sda1    50G   32G    18G   64%  /

aws s3 cp informe.pdf s3://mi-bucket/informes/informe.pdf   # subir un objeto
```

**Por qué importa:** los contenedores borran sus datos al reemplazarse; lo que debe sobrevivir va a un volumen (bloque/archivos) o a un servicio de objetos. El **estado de Terraform** suele guardarse en almacenamiento de objetos. **Dónde lo verás:** M2, M5.

## 1.4 Kernel

**Qué es:** el núcleo del sistema operativo. Es el único programa con acceso directo al hardware (CPU, memoria, disco, red). Todos los demás programas le **piden** esos recursos.

**Símil:** el administrador de un edificio. Los inquilinos (programas) no tocan las tuberías ni el tablero eléctrico: le piden al administrador agua, luz o una cita con el ascensor, y él decide quién usa qué y cuándo.

**Ejemplo:**

```bash
uname -r
# 6.5.0-27-generic     <- versión del kernel en uso
```

**Dato clave del curso:** los contenedores **comparten el kernel del equipo anfitrión**. Por eso arrancan en segundos: no cargan un sistema operativo completo (ver 5.2). **Dónde lo verás:** M2.

## 1.5 Proceso e hilo

**Qué es:** un **proceso** es un programa en ejecución, con su propia memoria aislada. Un **hilo** (thread) es una línea de ejecución dentro de un proceso; varios hilos del mismo proceso comparten su memoria.

**Símil:** un proceso es un restaurante completo, con su cocina y su despensa. Los hilos son los cocineros dentro de esa cocina: comparten los ingredientes, lo que los hace rápidos para coordinarse pero también les permite estorbarse entre sí. Dos restaurantes distintos (procesos) no comparten despensa.

**Ejemplo:**

```bash
ps aux | grep nginx
# root   1  0.0  0.1  nginx: master process
# www    7  0.0  0.2  nginx: worker process

top -H     # muestra hilos individuales
```

**Por qué importa:** un contenedor suele ejecutar **un proceso principal**; si ese proceso termina, el contenedor termina. **Dónde lo verás:** M2, M6.

## 1.6 Variables de entorno

**Qué es:** pares `NOMBRE=valor` que se le pasan a un programa desde afuera, sin modificar su código. Sirven para cambiar su configuración según el entorno.

**Símil:** el mismo electrodoméstico funciona en distintas casas; lo único que cambia es la perilla de voltaje y el enchufe. La receta (código) no cambia, pero los ajustes (variables) sí: en desarrollo apuntas a una base de datos de prueba y en producción a la real.

**Ejemplo:**

```bash
export DB_HOST=localhost
echo $DB_HOST
# localhost

docker run -e DB_HOST=db.interna -e LOG_LEVEL=debug mi-app:1.0
```

**Por qué importa:** es la forma estándar de configurar contenedores y despliegues. **Regla de oro:** no pongas contraseñas en el código ni en la imagen; se inyectan al arrancar o vía un gestor de secretos. **Dónde lo verás:** M2, M3.

## 1.7 Permisos y usuarios (root y sudo)

**Qué es:** cada archivo tiene dueño y permisos de lectura (`r`), escritura (`w`) y ejecución (`x`). **root** es el superusuario que puede hacer todo; **sudo** permite ejecutar un comando puntual con esos poderes.

**Símil:** las llaves de un edificio. Cada persona tiene llaves de su apartamento. **root** es la llave maestra que abre todo; **sudo** es pedirle prestada la maestra al portero por un momento. Cuanto menos tiempo y menos gente la use, más seguro el edificio.

**Ejemplo:**

```bash
ls -l llave.pem
# -rw------- 1 ana ana 1675 nov 18 10:02 llave.pem
#  ^^^ dueño (rw)  ^^^ grupo (nada)  ^^^ otros (nada)

chmod 600 llave.pem    # solo el dueño lee y escribe
sudo systemctl status ssh   # comando con privilegios temporales
```

**Por qué importa:** muchas llaves y credenciales exigen permisos estrictos para ser aceptadas. Y un contenedor que corre como root es un riesgo innecesario. **Dónde lo verás:** M2, M3.

## 1.8 Señales y códigos de salida

**Qué es:** las **señales** son avisos que el sistema le envía a un proceso (por ejemplo "termina"). El **código de salida** es un número que el proceso devuelve al terminar: **0 significa éxito**, cualquier otro valor indica error.

**Símil:** las señales son el timbre del portero: `SIGTERM` es "por favor, ya vamos a cerrar, recoge tus cosas" y `SIGKILL` es "te saco ahora mismo". El código de salida es lo que dice la persona al irse: "todo bien" (0) o "hubo un problema" (otro número).

**Ejemplo:**

```bash
ls /carpeta-que-no-existe
echo $?
# 2        <- distinto de 0: falló

docker ps -a
# STATUS
# Exited (137) 2 minutes ago     <- 137 = 128 + 9 (SIGKILL), típico de falta de memoria
# Exited (143) 5 minutes ago     <- 143 = 128 + 15 (SIGTERM), cierre ordenado
```

**Por qué importa:** los pipelines de CI marcan un paso como fallido según su código de salida. Y el código de un contenedor caído es la primera pista de diagnóstico. **Dónde lo verás:** M1, M2, M4.

---

# 2. Ejecución de programas

## 2.1 Compilado vs. interpretado

**Qué es:**

- **Compilado** (Go, C, Rust): el código se traduce de antemano a un binario que el equipo ejecuta directamente.
- **Interpretado** (Python, JavaScript/Node): un programa intermedio, el intérprete, lee y ejecuta el código línea a línea al momento de correr.
- Algunos lenguajes mezclan ambos (Java compila a un formato intermedio que luego se ejecuta en una máquina virtual).

**Símil:** un libro traducido completo antes de publicarse (compilado: lo recibes listo para leer) frente a un intérprete que traduce en vivo mientras el conferencista habla (interpretado: necesitas al intérprete presente cada vez).

**Ejemplo:**

```bash
gcc hola.c -o hola && ./hola      # compilas una vez, ejecutas el binario
python hola.py                     # necesitas Python instalado para ejecutar
```

**Por qué importa:** determina qué lleva tu imagen de contenedor: un binario compilado puede ir solo; un programa interpretado necesita además su intérprete y sus librerías. **Dónde lo verás:** M1, M2.

## 2.2 Dependencias y gestores de paquetes

**Qué es:** una **dependencia** es una librería de terceros que tu programa necesita. Un **gestor de paquetes** (npm, pip, Maven) las descarga e instala, y un archivo las lista con sus versiones.

**Símil:** una receta que requiere ingredientes comprados en el supermercado. El gestor de paquetes es el supermercado, y la lista de compras (con marcas y cantidades exactas) es el archivo de dependencias. Si cada quien compra una marca distinta, el plato no sale igual.

**Ejemplo:**

```bash
pip install -r requirements.txt     # Python
npm ci                               # Node: instala exactamente lo del lockfile
```

```text
# requirements.txt
flask==3.0.3
requests==2.32.3
```

**Por qué importa:** "en mi máquina funciona" casi siempre es una diferencia de versiones. Fijar versiones (archivos *lock*) hace los builds reproducibles. **Dónde lo verás:** M1, M2.

## 2.3 Binario, artefacto y build

**Qué es:** el **build** es el proceso de convertir el código fuente en algo ejecutable. El resultado se llama **artefacto**: el paquete listo para entregar (un `.jar`, un binario, una imagen de contenedor). Un **binario** es el archivo ejecutable ya traducido.

**Símil:** el build es hornear; el artefacto es el pan ya empacado, etiquetado y listo para enviar a las tiendas. No entregas la harina y la receta: entregas el pan.

**Ejemplo:**

```bash
mvn package
# [INFO] Building jar: target/app-1.2.0.jar     <- este jar es el artefacto

docker build -t mi-app:1.2.0 .                  # la imagen también es un artefacto
```

**Por qué importa:** un pipeline de CI construye **una vez** el artefacto y lo promueve entre entornos. Lo que se prueba debe ser exactamente lo que se despliega. **Dónde lo verás:** M1, M2.

## 2.4 Versionado semántico (SemVer)

**Qué es:** una convención de tres números, **MAYOR.MENOR.PARCHE** (por ejemplo `2.4.1`):

- **PARCHE** sube al corregir errores sin cambiar el comportamiento.
- **MENOR** sube al añadir funciones compatibles con lo anterior.
- **MAYOR** sube cuando hay cambios que pueden romper a quien lo use.

**Símil:** las ediciones de un libro de texto. Una fe de erratas (parche), un capítulo nuevo que no invalida los anteriores (menor), o una reedición que reorganiza todo y exige actualizar tus apuntes (mayor).

**Ejemplo:**

```text
1.4.2 -> 1.4.3   corrección de un error: actualizar es seguro
1.4.3 -> 1.5.0   función nueva: debería ser compatible
1.5.0 -> 2.0.0   cambio incompatible: revisar antes de actualizar
```

**Por qué importa:** es el lenguaje común para versiones de imágenes, módulos de Terraform y librerías. Permite decir "acepto parches pero no cambios mayores". **Dónde lo verás:** M1, M3, M5.

## 2.5 Fugas de memoria y OOM kill

**Qué es:** una **fuga de memoria** ocurre cuando un programa reserva memoria y nunca la libera, así que su consumo crece con el tiempo. Cuando se agota la memoria disponible (o el límite del contenedor), el sistema aplica el **OOM kill** (*Out Of Memory*): termina a la fuerza el proceso que consume demasiado.

**Símil:** un grifo que gotea en una bañera sin desagüe. Al principio no se nota, pero tarde o temprano se desborda. El OOM killer es el portero que, cuando el local se llena, saca al cliente que más espacio ocupa.

**Ejemplo:**

```bash
docker run -m 256m mi-app:1.0     # límite de 256 MB

docker inspect --format '{{.State.OOMKilled}}' mi-contenedor
# true       <- lo mató el sistema por exceder la memoria

dmesg | grep -i "killed process"   # evidencia en el log del kernel
```

**Síntoma típico:** el contenedor se reinicia cada cierto tiempo y el código de salida es **137**. **Dónde lo verás:** M2, M6.

---

# 3. Control de versiones

## 3.1 Git

**Qué es:** un sistema que guarda el historial completo de los cambios de tu código. Cada **commit** es un punto de guardado con autor, fecha y mensaje. Una **rama** (branch) es una línea de trabajo paralela; **merge** une una rama con otra; un **remoto** es una copia del repositorio en un servidor (GitHub, GitLab).

**Símil:** las partidas guardadas de un videojuego. Cada commit es un punto al que puedes volver. Una rama es una "partida paralela" donde pruebas algo arriesgado sin dañar la principal. El merge es decidir que lo probado en esa partida pasa a la oficial.

**Ejemplo:**

```bash
git switch -c feature/login        # crear y entrar a una rama nueva
git add app.py
git commit -m "Agrega validación de login"
git push -u origin feature/login   # subir la rama al remoto
git log --oneline
# a1b2c3d Agrega validación de login
# 9f8e7d6 Configura el proyecto
```

**Por qué importa:** casi todo en el curso (CI/CD, GitOps, Terraform) arranca de un cambio en Git. **Dónde lo verás:** M1.

## 3.2 Gitflow

**Qué es:** una estrategia de ramas con roles definidos: `main` (lo que está en producción), `develop` (integración), `feature/*` (funciones nuevas), `release/*` (preparación de una versión) y `hotfix/*` (arreglos urgentes sobre producción).

**Símil:** una editorial. Los autores escriben capítulos en borradores aparte (feature), el editor los junta en un manuscrito (develop), se prepara una edición de prueba (release), y cuando sale la edición definitiva va a la librería (main). Si se descubre un error grave ya publicado, se imprime una fe de erratas urgente (hotfix).

**Ejemplo:**

```text
main      ──●───────────────●────────●──   (versiones publicadas: v1.0, v1.1, v1.1.1)
             \             / \      /
develop       ●──●──●──●──●   ●────●
                \      /
feature/login    ●──●─●
```

**Cuándo usarlo:** equipos con versiones numeradas y ciclos de lanzamiento largos. Su costo: muchas ramas y fusiones complejas. **Dónde lo verás:** M1.

## 3.3 GitOps

**Qué es:** una práctica donde el **repositorio Git es la fuente de verdad** del estado deseado de la infraestructura y las aplicaciones. Un agente dentro del clúster (Argo CD, Flux) compara continuamente lo que dice Git con lo que realmente corre, y **corrige las diferencias solo**. Para cambiar algo, no entras al servidor: haces un cambio en Git.

**Símil:** el plano de una obra y un supervisor que recorre la construcción todos los días. Si alguien movió una pared sin autorización, el supervisor la devuelve a donde dice el plano. El plano (Git) manda; la obra (clúster) se ajusta.

**Ejemplo:**

```yaml
# deployment.yaml en el repositorio
spec:
  replicas: 3        # cambiamos 2 -> 3 en un pull request
```

```text
1. Abres un PR cambiando replicas de 2 a 3
2. El PR se revisa y se aprueba
3. Haces merge a main
4. El agente detecta la diferencia y el clúster pasa a 3 réplicas
```

**Ventajas:** historial de cada cambio, auditoría y reversión con `git revert`. **Cuidado:** no es "usar Git para el pipeline"; lo distintivo es el agente que reconcilia de forma continua. **Dónde lo verás:** M1, M5.

## 3.4 Trunk-based development

**Qué es:** un estilo donde todo el equipo integra en una sola rama principal (el *trunk*) con cambios **pequeños y frecuentes**, usando ramas de vida muy corta (horas o un día). Lo que aún no está listo se oculta tras un interruptor en lugar de vivir semanas en otra rama.

**Símil:** una pizarra compartida en la oficina donde todos escriben a diario, frente a que cada quien trabaje semanas en su copia del documento y luego pelee por juntar todo. Es más fácil unir pequeños cambios diarios que un cambio enorme al final.

**Ejemplo:**

```bash
git switch -c fix/timeout-api
# ...cambio pequeño...
git commit -am "Sube timeout de la API a 10s"
git push -u origin fix/timeout-api
# PR corto, revisión rápida, merge a main el mismo día
```

**Comparado con Gitflow:** menos ramas y menos fusiones difíciles, pero exige buenas pruebas automáticas, porque `main` siempre debe estar sano. Va muy bien con CI/CD. **Dónde lo verás:** M1.

## 3.5 Pull request (PR) y revisión de código

**Qué es:** una solicitud para que tus cambios se incorporen a otra rama, que primero otras personas revisan y que dispara las pruebas automáticas.

**Símil:** un editor que lee tu artículo antes de que salga en el periódico. No es desconfianza: dos pares de ojos detectan errores que uno solo no ve.

**Ejemplo:**

```bash
git push -u origin feature/login
gh pr create --title "Agrega login" --body "Valida usuario y contraseña. Cierra #12"
```

**Por qué importa:** el PR es el punto natural para ejecutar el pipeline de CI, pedir aprobaciones y dejar registro de por qué se hizo cada cambio. **Dónde lo verás:** M1.

## 3.6 Tags y releases

**Qué es:** un **tag** es una etiqueta permanente sobre un commit específico, normalmente una versión (`v1.2.0`). Un **release** es la publicación formal de esa versión, a menudo con notas y artefactos adjuntos.

**Símil:** el sello de "Primera edición" en un libro: marca exactamente qué contenido tenía esa edición, aunque después se sigan haciendo cambios.

**Ejemplo:**

```bash
git tag -a v1.2.0 -m "Versión 1.2.0: agrega login"
git push origin v1.2.0
git tag
# v1.0.0
# v1.1.0
# v1.2.0
```

**Por qué importa:** permite volver a una versión conocida (rollback) y relacionar la imagen `mi-app:1.2.0` con el código exacto que la produjo. **Dónde lo verás:** M1, M3.

## 3.7 .gitignore y secretos

**Qué es:** `.gitignore` es un archivo que lista lo que Git **no debe rastrear** (credenciales, archivos temporales, dependencias descargadas, archivos de estado).

**Símil:** no dejes las llaves de tu casa pegadas con cinta en la puerta. Aunque después las quites, quien vio la fotografía ya las vio. En Git pasa igual: **un secreto subido queda en el historial aunque lo borres después**.

**Ejemplo:**

```text
# .gitignore
.env
*.pem
*.tfstate
*.tfstate.backup
.terraform/
node_modules/
```

**Si ya subiste una credencial:** no basta con borrarla. Hay que **revocarla y generar una nueva**, porque se considera comprometida. **Dónde lo verás:** M1, M3.

---

# 4. Redes

## 4.1 HTTP/HTTPS, métodos y códigos de estado

**Qué es:** HTTP es el protocolo de la web: un cliente hace una **petición** y un servidor devuelve una **respuesta**. La petición lleva un **método** (qué quiere hacer) y la respuesta un **código de estado** (cómo salió). **HTTPS** es HTTP protegido con TLS (ver 4.4).

**Símil:** pedir en un restaurante. El método es el tipo de pedido: **GET** "muéstreme la carta", **POST** "tome este nuevo pedido", **PUT** "cambie mi pedido", **DELETE** "cancele mi pedido". El código es la respuesta del mesero.

| Código | Familia | Significa | Símil |
|---|---|---|---|
| 200 | 2xx éxito | Todo bien | "Aquí tiene su plato" |
| 301 / 302 | 3xx redirección | Se movió | "Ahora estamos en otro local" |
| 400 / 404 | 4xx error del cliente | Pedido inválido / no existe | "No tenemos ese plato" |
| 401 / 403 | 4xx | No autenticado / sin permiso | "No lo conozco" / "No puede entrar a la cocina" |
| 500 / 503 | 5xx error del servidor | Falló / no disponible | "La cocina se incendió" |

**Ejemplo:**

```bash
curl -i https://miapp.ejemplo.com/health
# HTTP/1.1 200 OK
# content-type: application/json
#
# {"status":"ok"}
```

**Por qué importa:** los 4xx y 5xx son la señal básica para diagnosticar y para alertas; los balanceadores y las sondas de salud se basan en estos códigos. **Dónde lo verás:** M3, M4, M6.

## 4.2 DNS

**Qué es:** el sistema que traduce nombres legibles (`miapp.com`) a direcciones IP (`203.0.113.10`), que son las que usan las máquinas.

**Símil:** la agenda de contactos del celular. Tú buscas "Mamá"; el teléfono sabe a qué número marcar. Si el contacto cambia de número y la agenda no se actualiza, la llamada falla aunque el nombre sea correcto.

**Ejemplo:**

```bash
dig miapp.com +short
# 203.0.113.10

nslookup miapp.com
```

**Cosas a recordar:** los cambios de DNS no son instantáneos (el **TTL** indica cuánto tiempo se guardan en caché). Y un fallo de DNS ("no se puede resolver el nombre") es distinto de un fallo de conexión o de permisos. **Dónde lo verás:** M4.

## 4.3 Firewall y puertos

**Qué es:** una **IP** identifica a una máquina y un **puerto** identifica a un servicio dentro de ella (HTTP usa el 80, HTTPS el 443, SSH el 22). Un **firewall** es un conjunto de reglas que decide qué tráfico puede entrar o salir, según origen, destino y puerto. En la nube se llaman *security groups* o *network ACLs*.

**Símil:** la portería de un conjunto residencial. La IP es la dirección del conjunto; los puertos son las distintas entradas (peatonal, vehicular, domicilios). El portero tiene una lista: "a la entrada vehicular solo entran residentes; la peatonal está abierta a todos".

**Ejemplo (regla de un security group):**

```text
Permitir  TCP 443  desde 0.0.0.0/0        # el mundo accede a la web
Permitir  TCP 22   desde 190.20.30.40/32  # SSH solo desde mi IP
Denegar   todo lo demás
```

**Para diagnosticar:**

```bash
curl http://servidor:8080
# curl: (7) Connection refused    <- llegó, pero nadie escucha en ese puerto
# curl: (28) Connection timed out <- algo lo descarta en el camino (suele ser un firewall)
```

**Por qué importa:** abrir un puerto "para que funcione" es el error más común. Se abre lo mínimo necesario. **Dónde lo verás:** M4.

## 4.4 TLS y certificados

**Qué es:** TLS es el protocolo que **cifra** la comunicación y permite **verificar la identidad** del servidor. Un **certificado** es el documento digital que demuestra que un dominio le pertenece a alguien, firmado por una autoridad confiable (CA). Tiene fecha de vencimiento.

**Símil:** un sobre sellado y una cédula verificada. El sobre sellado impide que el cartero lea tu carta (cifrado). La cédula emitida por la Registraduría demuestra que quien la presenta es quien dice ser (certificado emitido por una CA).

**Ejemplo:**

```bash
echo | openssl s_client -connect miapp.com:443 -servername miapp.com 2>/dev/null \
  | openssl x509 -noout -subject -dates
# subject=CN = miapp.com
# notBefore=Sep  1 00:00:00 2026 GMT
# notAfter=Nov 30 23:59:59 2026 GMT    <- fecha de vencimiento
```

**Error clásico:** un certificado vencido o emitido para otro nombre hace que los clientes rechacen la conexión. Muchas "caídas misteriosas" son solo certificados expirados. **Dónde lo verás:** M4.

---

# 5. Conceptos de nube

## 5.1 IaaS, PaaS, SaaS y serverless

**Qué es:** distintos niveles de **cuánto administras tú y cuánto el proveedor**.

**Símil (comer):**

| Modelo | Tú administras | Símil | Ejemplo en nube |
|---|---|---|---|
| **IaaS** | Sistema operativo, programas, datos | Alquilas el local vacío y pones tú cocina y cocineros | Máquina virtual (EC2, Compute Engine) |
| **PaaS** | Tu aplicación y datos | Alquilas el local con cocina equipada: solo traes la receta | App Service, Elastic Beanstalk, Cloud Run |
| **SaaS** | Solo usas el producto | Pides domicilio: no cocinas nada | Gmail, Google Workspace |
| **Serverless** | Solo tu función | Pagas únicamente cuando hay un pedido; no hay local encendido esperando | AWS Lambda, Cloud Functions |

**Ejemplo (una función serverless completa):**

```python
def handler(event, context):
    return {"statusCode": 200, "body": "Hola desde serverless"}
```

**Por qué importa:** entre más hacia PaaS/serverless, menos servidores gestionas, pero con menos control. El módulo 3 trata justo de desplegar "sin gestionar servidores". **Dónde lo verás:** M3.

## 5.2 Máquina virtual vs. contenedor

**Qué es:** una **máquina virtual (VM)** simula un computador completo, con su propio sistema operativo y kernel. Un **contenedor** aísla solo el programa y sus dependencias, y **comparte el kernel** del equipo anfitrión.

**Símil:** una VM es una **casa independiente**: cimientos, tuberías y electricidad propios. Un contenedor es un **apartamento en un edificio**: tiene su espacio privado, pero comparte cimientos y tuberías con los demás. Los apartamentos son más baratos y rápidos de construir; las casas aíslan más.

**Ejemplo:**

```bash
uname -r                           # kernel del anfitrión (Linux)
# 6.5.0-27-generic

docker run --rm alpine uname -r    # kernel visto desde un contenedor
# 6.5.0-27-generic                 <- el MISMO kernel: se comparte
```

| | VM | Contenedor |
|---|---|---|
| Arranque | Minutos | Segundos |
| Tamaño | Gigabytes | Megabytes |
| Aislamiento | Muy fuerte | Más ligero |

**Dónde lo verás:** M2.

## 5.3 Infraestructura inmutable vs. mutable

**Qué es:** en la infraestructura **mutable** entras al servidor y lo modificas (instalas, actualizas, ajustas a mano). En la **inmutable** nunca modificas un servidor en uso: si hay que cambiar algo, construyes uno nuevo desde una plantilla (o imagen) y reemplazas al viejo.

**Símil:** la famosa frase "mascotas vs. ganado". Una mascota tiene nombre, la cuidas y la curas cuando se enferma. El ganado se numera: si uno falla, se reemplaza por otro idéntico. O también: arreglar un carro por piezas durante años (cada carro termina siendo único e irrepetible) frente a cambiarlo por otro idéntico de fábrica.

**Ejemplo:**

```text
Mutable:    ssh servidor1 -> apt upgrade -> editar configuración a mano
            (nadie sabe después en qué estado exacto quedó)

Inmutable:  construir imagen mi-app:1.3.0 -> desplegar nuevas instancias ->
            retirar las anteriores (1.2.0)
```

**Por qué importa:** es la base de la reproducibilidad: contenedores, imágenes y Terraform asumen que el estado se describe en un archivo, no en "lo que alguien hizo un martes". **Dónde lo verás:** M2, M5.

---

# 6. Observabilidad

## 6.1 Logs, métricas y trazas

**Qué es:** los tres tipos de señales con los que un sistema "cuenta lo que le pasa".

- **Logs:** registros de eventos, uno por uno ("a las 10:02 falló el pago").
- **Métricas:** números agregados en el tiempo (peticiones por segundo, % de CPU, errores por minuto).
- **Trazas:** el recorrido completo de una petición a través de varios servicios.

**Símil (un carro):** las **métricas** son el tablero (velocidad, temperatura, combustible: te dicen *cuánto* y *si algo anda mal*). Los **logs** son la bitácora o caja negra (te dicen *qué pasó exactamente* en un momento). Las **trazas** son el GPS con la ruta recorrida (te dicen *por dónde pasó* y *dónde se demoró*).

**Ejemplo:**

```text
LOG:      2026-11-18T10:02:11Z ERROR pagos: timeout llamando a banco
MÉTRICA:  http_errores_5xx = 42 en los últimos 5 minutos
TRAZA:    petición #a91f -> api (20ms) -> pagos (30ms) -> banco (2900ms)
```

**Regla práctica:** la métrica avisa que hay un problema, la traza ubica dónde, el log explica por qué. **Dónde lo verás:** M6.

## 6.2 Logs estructurados e identificador de correlación

**Qué es:** un log **estructurado** se escribe en un formato con campos (normalmente JSON) en lugar de texto libre, para poder filtrarlo y buscarlo. El **identificador de correlación** es un código único que acompaña a una petición por todos los servicios, para encontrar todos sus logs.

**Símil:** un formulario con casillas frente a una carta escrita a mano. Es más fácil encontrar "todos los formularios con ciudad = Medellín" que leer mil cartas. Y el correlation ID es el **número de pedido** de un domicilio: lo ven la caja, la cocina y el repartidor, y con él reconstruyes toda la historia.

**Ejemplo:**

```json
{"ts":"2026-11-18T10:02:11Z","nivel":"ERROR","servicio":"pagos",
 "correlation_id":"a91f-77c2","msg":"timeout llamando a banco","duracion_ms":2900}
```

```bash
grep "a91f-77c2" *.log     # todos los eventos de esa petición, en todos los servicios
```

**Dónde lo verás:** M6.

## 6.3 Traza distribuida y span

**Qué es:** una **traza** es el recorrido completo de una petición; cada **span** es un tramo de ese recorrido (una llamada a un servicio, una consulta a la base de datos) con su hora de inicio y duración. Los spans se anidan como un árbol.

**Símil:** el seguimiento de un paquete en una empresa de mensajería. La traza es el envío completo; cada span es un tramo ("recogido", "en bodega", "en reparto") con su hora de llegada y salida. Mirando los tramos ves enseguida cuál se demoró.

**Ejemplo:**

```text
Traza a91f  (total 2950 ms)
└─ span: api.recibir_pedido            20 ms
   └─ span: pagos.cobrar            2900 ms   <- aquí se fue el tiempo
      └─ span: banco.autorizar      2870 ms
```

**Cuidado:** si un servicio no está instrumentado, la traza queda "cortada" y no verás qué pasó adentro. **OpenTelemetry** es el estándar abierto para generar estas señales. **Dónde lo verás:** M6.

---

# 7. Seguridad básica

## 7.1 Cifrado en tránsito vs. en reposo

**Qué es:** el cifrado **en tránsito** protege los datos mientras viajan por la red (TLS/HTTPS). El cifrado **en reposo** protege los datos mientras están guardados (en discos, bases de datos, buckets).

**Símil:** un carro blindado de transporte de valores (en tránsito: protege el dinero mientras se mueve) frente a una caja fuerte en la bodega (en reposo: lo protege mientras está quieto). Necesitas ambos: de nada sirve una caja fuerte si el dinero viaja en una bolsa abierta.

**Ejemplo:**

```bash
curl https://api.miapp.com/datos       # en tránsito: HTTPS
aws s3api get-bucket-encryption --bucket mi-bucket   # en reposo: ¿el bucket está cifrado?
```

**Dónde lo verás:** M3, M4.

## 7.2 WAF y OWASP Top 10

**Qué es:** **OWASP Top 10** es la lista publicada de las categorías de vulnerabilidad web más frecuentes (inyección SQL, control de acceso roto, configuración insegura, etc.). Un **WAF** (*Web Application Firewall*) inspecciona el **contenido** de las peticiones HTTP y bloquea las que coinciden con patrones de ataque.

**Símil:** el firewall de red es el portero que revisa **por cuál puerta** llegas. El WAF es el vigilante que además **revisa lo que traes en las manos**: ve que entras por la puerta correcta, pero abre el paquete y detecta que lleva algo sospechoso.

**Ejemplo:**

```text
Petición normal:       GET /productos?id=15            -> permitida
Petición sospechosa:   GET /productos?id=15' OR '1'='1 -> bloqueada por regla de inyección SQL
```

**Límite importante:** un WAF **no sustituye** la autenticación ni un código seguro, y no detiene "todos los ataques": solo los que sus reglas reconocen. **Dónde lo verás:** M4.

## 7.3 Superficie de ataque y exposición mínima

**Qué es:** la **superficie de ataque** es el conjunto de puntos por donde alguien podría intentar entrar (puertos abiertos, servicios publicados, credenciales, permisos). **Exposición mínima** significa abrir solo lo estrictamente necesario.

**Símil:** las puertas y ventanas de una casa. Cuantas más tenga abiertas, más lugares hay que vigilar. Una base de datos no tiene por qué ser accesible desde internet, igual que la despensa no necesita puerta a la calle.

**Ejemplo:**

```bash
ss -tlnp                           # qué puertos están escuchando en este equipo

docker run -p 5432:5432 postgres              # escucha en TODAS las interfaces (expuesta)
docker run -p 127.0.0.1:5432:5432 postgres    # solo accesible desde la propia máquina
```

**Regla práctica:** por cada puerto o permiso abierto, pregúntate "¿quién lo necesita y para qué?". Si nadie responde, se cierra. **Dónde lo verás:** M4.

---

*Documento de apoyo para el nivel intermedio de Arquitectura en la Nube. Los símiles son ayudas didácticas; ante cualquier duda, la documentación oficial de cada herramienta es la fuente de referencia.*