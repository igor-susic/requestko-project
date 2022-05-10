# Project Requestko

## What is this app

Simple `async` service that tries to forward one `GET` request to another server and return response.

### Little bit about architecture

This app makes use of `asynchronous` nature of Python to handle as much load possible only using main thread.
Server used to serve this app is`uvicorn`  Framweork used to create the app is `Starlette`. Why not FastAPI, Django, Flask etc.
well I wanted to use something lightweight and native to `async`, Starlette shines there. Why not `FastAPI`? while it's great,
it has features that bring overhead that I __mostly__ don't need for this project.

Why not `gunicorn`? Well this is something that Iwould later add to scale the app, I would use combination of `gunicorn` with `uvicorn` workers
to make use of processes and `async`. But I think for now this is enough as showcase, and here we don't really have anything
that is CPU bound, so we are doing only `I/O` where `async` should be enough.

ALso there are different approaches to scaling this app but I won't discuss everything here it would be pretty long `README.md`

## How to run this service locally
* Position yourself in the directory `requestko-project` and simply run `docker compose up`
this comand will bring up:
  * Promehteus server
  * Grafana
  * Requestko service

__I won't show pictures in text below as they arn't nice, take look for yourself__

Out of the box Prometheus should be able to scrape `Requestko` service for metrics and you should see something like in the picture `prometheus.png`.

After that you should go to `Grafana` (port `3000`), log in with default username and password (which are `admin` and `admin`), add new DataSource like
in the picture `datasource.png`.
The URL for the Prometheus you can get from simple `docker inspect` where you filter for network address.
Next step is to import `Requestko-grafana.json` dashboard. To that simply use import feature, but importantly you should change:
```json
      "datasource": {
        "type": "prometheus",
        "uid": "l1Fhpl_7z"
      },
```
each snippet like this, to:
```json
      "datasource": {
        "type": "prometheus",
        "uid": "HERE_ENTER_WHATEVER_IS_YOUR_UID_OF_YOUR_SOURCE"
      },
```
Now everything should work. 

### Requestko service

`Requestko` service will be brought up inside docker container and binded to your `localhost:80` address so you don't
need to check for containers IP address. 

#### Enpoints

`Requestko` has 3 defined endpoints you can reach intentionally:

```
EDNPOINT: /api/smart
METHOD: GET
REQUESTED QUERY PARAMETERS: 
         PARAMETER_NAME: timeout
         PARAMETER_TYPE: integer [0, infinity] - represents milliseconds


EXAMPLE CALL:
curl -X GET http://localhost:80/api/smart?timeout=100
```

```
EDNPOINT: /metrics
METHOD: GET
DESCRIPTION: Prometheus metrics are exposed here
```

```
EDNPOINT: /schema
METHOD: GET
DESCRIPTION: OpenAPI schema with more details about possible responses for the route /api/smart can be checked here
```

## What should I add, and what needs to be done better
- [ ] Write tests
- [ ] Install `aiohttp` with speedups
- [ ] Handle exceptions better
- [ ] Clean the code
- [ ] Handle edge cases
    - [ ] what if someone in `timeout` sends negative number
    - [ ] better serialization/deserialization of requests and responses
    - [ ] Check if payload returned from Exponea matches specific structure
    - [ ] ...
- [ ] better error logging (mainly Exceptions)
- [ ] Add automatic test stage, linting, static code check etc.


Why haven't I added this you may ask, well answer is not enough time and this service will never run in production at least it shouldn't :D 